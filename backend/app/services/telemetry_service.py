import logging
from typing import Dict, Any, List, Optional
from app.services.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)


class TelemetryService:
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service

    def ingest_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ingest telemetry metrics and map them to graph nodes."""
        results = {
            "total": len(metrics),
            "updated": 0,
            "failed": 0,
            "errors": []
        }

        for metric in metrics:
            try:
                service_name = metric.get("service_name")
                if not service_name:
                    results["failed"] += 1
                    results["errors"].append("Missing service_name in metric")
                    continue

                telemetry_data = {
                    "avg_p99_latency": metric.get("avg_p99_latency", 0.0),
                    "error_rate": metric.get("error_rate", 0.0),
                    "throughput": metric.get("throughput", 0.0),
                    "health_score": metric.get("health_score", 1.0),
                    "last_telemetry_update": None  # Neo4j datetime() will be added by database
                }

                # Update the service node with telemetry
                success = self.neo4j.update_telemetry(service_name, telemetry_data)
                if success:
                    results["updated"] += 1
                    logger.info(f"Updated telemetry for service: {service_name}")
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Service not found: {service_name}")

            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error processing metric: {str(e)}")
                logger.error(f"Failed to ingest metric: {e}")

        return results

    def get_service_telemetry(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve telemetry metrics for a specific service."""
        try:
            with self.neo4j.driver.session() as session:
                result = session.run("""
                    MATCH (s:Service {name: $service_name})
                    RETURN
                        s.name as name,
                        s.avg_p99_latency as latency,
                        s.error_rate as error_rate,
                        s.throughput as throughput,
                        s.health_score as health_score,
                        s.last_telemetry_update as last_update
                """, service_name=service_name)

                record = result.single()
                if record:
                    return {
                        "service_name": record["name"],
                        "avg_p99_latency": record["latency"],
                        "error_rate": record["error_rate"],
                        "throughput": record["throughput"],
                        "health_score": record["health_score"],
                        "last_update": record["last_update"]
                    }
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve telemetry for {service_name}: {e}")
            return None

    def ingest_prometheus_metrics(self, metrics_text: str) -> Dict[str, Any]:
        """Ingest Prometheus-format metrics and extract relevant ones."""
        parsed_metrics = []

        for line in metrics_text.split("\n"):
            if line.startswith("#") or not line.strip():
                continue

            try:
                # Parse Prometheus format: metric_name{labels} value timestamp
                # Example: http_request_duration_seconds_sum{instance="service_a",quantile="0.99"} 250.5
                if "{" in line:
                    metric_name = line.split("{")[0]
                    labels_part = line.split("{")[1].split("}")[0]
                    value_part = line.split("}")[1].strip().split()[0]

                    # Extract service name from labels
                    service_name = None
                    for label in labels_part.split(","):
                        if "service" in label.lower():
                            service_name = label.split("=")[1].strip('"')
                            break

                    if not service_name:
                        continue

                    # Map common Prometheus metrics
                    value = float(value_part)

                    if "latency" in metric_name.lower() or "duration" in metric_name.lower():
                        parsed_metrics.append({
                            "service_name": service_name,
                            "avg_p99_latency": value
                        })
                    elif "error_rate" in metric_name.lower() or "errors_total" in metric_name.lower():
                        parsed_metrics.append({
                            "service_name": service_name,
                            "error_rate": value
                        })
                    elif "throughput" in metric_name.lower() or "requests_total" in metric_name.lower():
                        parsed_metrics.append({
                            "service_name": service_name,
                            "throughput": value
                        })

            except (IndexError, ValueError) as e:
                logger.debug(f"Failed to parse Prometheus line: {line}, error: {e}")
                continue

        return self.ingest_metrics(parsed_metrics)

    def health_check(self) -> Dict[str, Any]:
        """Check health of telemetry ingestion system."""
        return {
            "status": "healthy",
            "neo4j_connection": self.neo4j.health_check(),
            "timestamp": None
        }
