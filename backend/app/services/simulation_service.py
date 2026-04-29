import json
import logging
import time
from typing import Dict, Any, Optional, List
from anthropic import Anthropic
from app.models import SimulationResult, BlastRadius, RiskLevel, ChangeRequest
from app.services.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)


class SimulationService:
    def __init__(self, neo4j_service: Neo4jService, anthropic_api_key: Optional[str] = None, model: str = "claude-haiku-4-5-20251001"):
        self.neo4j = neo4j_service
        self.api_key = anthropic_api_key
        self.model = model
        self.client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds

    def simulate_change(self, request: ChangeRequest) -> SimulationResult:
        """Simulate the impact of a code change using GraphRAG + LLM."""
        try:
            # Extract changed files from diff
            changed_files = self._parse_diff_files(request.diff)
            logger.info(f"Detected changed files: {changed_files}")

            # Get subgraph for impact analysis (GraphRAG retrieval)
            subgraph = self.neo4j.get_subgraph_for_impact(changed_files)
            logger.info(f"Retrieved subgraph with {len(subgraph['nodes'])} nodes")

            # If we have LLM access, use it for better analysis
            if self.client:
                result = self._simulate_with_llm(request, subgraph, changed_files)
            else:
                # Fall back to rule-based analysis
                logger.warning("No LLM API key available, using rule-based fallback")
                result = self._simulate_fallback(subgraph, changed_files)

            # Persist the simulation as a ChangeEvent
            self._persist_simulation(result, request)

            return result

        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            return self._simulate_fallback({}, [])

    def simulate_whatif(self, description: str, target_service: str) -> SimulationResult:
        """Simulate a what-if scenario for a specific service."""
        try:
            # For what-if, we start from the target service
            with self.neo4j.driver.session() as session:
                result = session.run("""
                    MATCH (s:Service {name: $target_service})
                    RETURN properties(s) as service_props
                """, target_service=target_service)
                record = result.single()
                if not record:
                    return self._simulate_fallback({}, [])

            # Get the subgraph rooted at target service
            subgraph = self.neo4j.get_subgraph_for_impact([target_service])

            if self.client:
                result = self._simulate_whatif_with_llm(description, target_service, subgraph)
            else:
                result = self._simulate_fallback(subgraph, [target_service])

            return result

        except Exception as e:
            logger.error(f"What-if simulation failed: {e}")
            return self._simulate_fallback({}, [])

    def _simulate_with_llm(self, request: ChangeRequest, subgraph: Dict[str, Any], changed_files: List[str]) -> SimulationResult:
        """Run simulation using Claude with GraphRAG context."""
        try:
            # Build prompt context
            subgraph_context = self._format_subgraph_for_prompt(subgraph)
            telemetry_context = self._extract_telemetry_context(subgraph)

            prompt = f"""Context (Code Graph and Relationships):
{subgraph_context}

Production Telemetry (Current Metrics):
{telemetry_context}

Proposed Change:
{request.diff}

{f"Additional Context: {request.context}" if request.context else ""}

Analyze this change and provide impact assessment. Focus on:
1. Which services/endpoints are affected
2. Predicted impact on latency and error rates
3. Overall risk level (Low, Medium, High, Critical)
4. Confidence in the assessment (0.0-1.0)
5. Recommended mitigations

Return response ONLY as valid JSON with no other text:
{{
  "risk_score": "Low|Medium|High|Critical",
  "confidence": 0.0-1.0,
  "blast_radius": {{"services": N, "endpoints": N, "databases": N}},
  "predicted_impact": {{"latency_delta_ms": N, "error_rate_increase": N}},
  "explanation": "Clear explanation of analysis",
  "mitigations": ["mitigation1", "mitigation2"]
}}"""

            # Call LLM with retry logic
            response_text = self._call_llm_with_retry(prompt)

            if not response_text:
                return self._simulate_fallback(subgraph, changed_files)

            # Parse JSON response
            simulation_result = self._parse_llm_response(response_text, subgraph, changed_files)
            return simulation_result

        except Exception as e:
            logger.error(f"LLM simulation failed: {e}, falling back to rule-based")
            return self._simulate_fallback(subgraph, changed_files)

    def _simulate_whatif_with_llm(self, description: str, target_service: str, subgraph: Dict[str, Any]) -> SimulationResult:
        """Simulate a what-if scenario for a specific service."""
        try:
            subgraph_context = self._format_subgraph_for_prompt(subgraph)
            telemetry_context = self._extract_telemetry_context(subgraph)

            prompt = f"""Scenario Analysis for Service: {target_service}

Context (Service Graph):
{subgraph_context}

Current Telemetry:
{telemetry_context}

Proposed Scenario:
{description}

Analyze the impact of this scenario. Provide assessment in JSON format:
{{
  "risk_score": "Low|Medium|High|Critical",
  "confidence": 0.0-1.0,
  "blast_radius": {{"services": N, "endpoints": N, "databases": N}},
  "predicted_impact": {{"latency_delta_ms": N, "error_rate_increase": N}},
  "explanation": "Analysis of scenario impact",
  "mitigations": ["action1", "action2"]
}}"""

            response_text = self._call_llm_with_retry(prompt)
            if not response_text:
                return self._simulate_fallback(subgraph, [target_service])

            simulation_result = self._parse_llm_response(response_text, subgraph, [target_service])
            return simulation_result

        except Exception as e:
            logger.error(f"What-if LLM simulation failed: {e}")
            return self._simulate_fallback(subgraph, [target_service])

    def _call_llm_with_retry(self, prompt: str) -> Optional[str]:
        """Call Claude API with exponential backoff retry logic."""
        if not self.client:
            return None

        for attempt in range(self.max_retries):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    system="You are an expert software architect analyzing code changes for impact. Respond with valid JSON only."
                )
                return message.content[0].text

            except Exception as e:
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning(f"LLM call attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                else:
                    logger.error(f"LLM call failed after {self.max_retries} attempts")
                    return None

    def _parse_llm_response(self, response_text: str, subgraph: Dict[str, Any], changed_files: List[str]) -> SimulationResult:
        """Parse JSON response from LLM into SimulationResult."""
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_str = response_text
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            data = json.loads(json_str)

            # Validate required fields
            affected_entities = [node["properties"].get("name", f"node_{node['id']}") for node in subgraph.get("nodes", [])[:20]]

            return SimulationResult(
                risk_score=RiskLevel(data.get("risk_score", "Medium")),
                confidence=float(data.get("confidence", 0.5)),
                blast_radius=BlastRadius(
                    services=data.get("blast_radius", {}).get("services", 1),
                    endpoints=data.get("blast_radius", {}).get("endpoints", 2),
                    databases=data.get("blast_radius", {}).get("databases", 0),
                    affected_entities=affected_entities
                ),
                predicted_impact=data.get("predicted_impact", {"latency_delta_ms": 0, "error_rate_increase": 0.0}),
                explanation=data.get("explanation", "LLM analysis complete"),
                mitigations=data.get("mitigations", [])
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return self._simulate_fallback(subgraph, changed_files)

    def _simulate_fallback(self, subgraph: Dict[str, Any], changed_files: List[str]) -> SimulationResult:
        """Rule-based fallback when LLM is unavailable."""
        affected_count = len(subgraph.get("nodes", []))
        affected_entities = [node["properties"].get("name", f"node_{node['id']}") for node in subgraph.get("nodes", [])[:20]]

        # Simple heuristic: more files/nodes = higher risk
        if affected_count > 5:
            risk = RiskLevel.HIGH
            confidence = 0.7
            latency_delta = 50
        elif affected_count > 2:
            risk = RiskLevel.MEDIUM
            confidence = 0.75
            latency_delta = 20
        else:
            risk = RiskLevel.LOW
            confidence = 0.8
            latency_delta = 5

        return SimulationResult(
            risk_score=risk,
            confidence=confidence,
            blast_radius=BlastRadius(
                services=max(1, affected_count // 3),
                endpoints=max(2, affected_count // 2),
                databases=0,
                affected_entities=affected_entities
            ),
            predicted_impact={
                "latency_delta_ms": latency_delta,
                "error_rate_increase": 0.001 if risk == RiskLevel.HIGH else 0.0005
            },
            explanation="Rule-based impact assessment (LLM unavailable). Analyzed code graph structure and dependency graph to estimate risk.",
            mitigations=[
                "Conduct thorough code review before merging",
                "Run integration tests with all affected services",
                "Monitor metrics closely after deployment",
                "Have rollback plan ready"
            ]
        )

    def _parse_diff_files(self, diff: str) -> List[str]:
        """Extract changed file paths from a git diff."""
        files = []
        for line in diff.split("\n"):
            if line.startswith("+++ b/"):
                file_path = line[6:].strip()
                if file_path and file_path != "/dev/null":
                    files.append(file_path)
            elif line.startswith("--- a/"):
                file_path = line[6:].strip()
                if file_path and file_path != "/dev/null":
                    files.append(file_path)

        return list(set(files))  # Remove duplicates

    def _format_subgraph_for_prompt(self, subgraph: Dict[str, Any]) -> str:
        """Format subgraph as readable text for LLM context."""
        lines = ["=== Code Graph ==="]
        for node in subgraph.get("nodes", [])[:20]:
            labels = node.get("labels", [])
            props = node.get("properties", {})
            name = props.get("name", "unknown")
            lines.append(f"- {labels[0] if labels else 'Node'}: {name}")

        for rel in subgraph.get("relationships", [])[:20]:
            rel_type = rel.get("type", "UNKNOWN")
            lines.append(f"  {rel['start_node_id']} --{rel_type}--> {rel['end_node_id']}")

        return "\n".join(lines) if lines else "No graph context available"

    def _extract_telemetry_context(self, subgraph: Dict[str, Any]) -> str:
        """Extract telemetry metrics from subgraph nodes."""
        lines = ["=== Telemetry Metrics ==="]
        for node in subgraph.get("nodes", [])[:10]:
            props = node.get("properties", {})
            name = props.get("name", "unknown")

            metrics = []
            if "avg_p99_latency" in props:
                metrics.append(f"p99_latency: {props['avg_p99_latency']}ms")
            if "error_rate" in props:
                metrics.append(f"error_rate: {props['error_rate'] * 100:.2f}%")
            if "health_score" in props:
                metrics.append(f"health: {props['health_score'] * 100:.0f}%")
            if "throughput" in props:
                metrics.append(f"throughput: {props['throughput']} req/s")

            if metrics:
                lines.append(f"- {name}: {', '.join(metrics)}")

        return "\n".join(lines) if len(lines) > 1 else "No telemetry data"

    def _persist_simulation(self, result: SimulationResult, request: ChangeRequest) -> None:
        """Persist simulation result as a ChangeEvent node in Neo4j."""
        try:
            with self.neo4j.driver.session() as session:
                session.run("""
                    CREATE (ce:ChangeEvent {
                        change_id: apoc.util.uuid(),
                        repo_url: $repo_url,
                        diff_snippet: $diff_snippet,
                        risk_score: $risk_score,
                        confidence: $confidence,
                        simulated_at: datetime(),
                        blast_radius: $blast_radius,
                        predicted_impact: $predicted_impact
                    })
                """,
                repo_url=request.repo_url,
                diff_snippet=request.diff[:500],
                risk_score=result.risk_score.value,
                confidence=result.confidence,
                blast_radius={
                    "services": result.blast_radius.services,
                    "endpoints": result.blast_radius.endpoints,
                    "databases": result.blast_radius.databases
                },
                predicted_impact=result.predicted_impact
            )
        except Exception as e:
            logger.warning(f"Failed to persist simulation: {e}")
