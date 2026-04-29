# Software Requirements Specification (SRS)

**Project:** Aegis Twin – AI-Native Predictive Digital Twin for Software Architectures
**Version:** 3.0
**Date:** April 29, 2026
**Status:** Production Planning

## 1. Introduction

### 1.1 Purpose
Aegis Twin is an AI-driven platform designed to build, maintain, and operate a live digital twin of software architecture. It delivers automated change impact analysis, risk scoring, and developer guidance through a web dashboard, IDE plugin, and CI/CD enforcement.

### 1.2 Scope
**In scope:**
- Codebase and infrastructure ingestion from source control
- Knowledge graph creation and maintenance
- Telemetry enrichment and runtime context
- AI-powered predictive simulations and explanations
- Web dashboard for architecture visualization and review
- VS Code/Cursor extension for in-editor risk feedback
- CI/CD integrations for PR checks and merge guardrails
- Production feedback loop for adaptive model improvement

**Out of scope:**
- Autonomous code generation or automated refactoring
- Native mobile applications
- On-premise air-gapped deployments in Phase 1
- Hardware and physical system digital twins

### 1.3 Audience
- Product owners and technical stakeholders
- Architects and engineering managers
- Backend, frontend, and platform engineers
- QA, DevOps, and security teams

### 1.4 Definitions
- **Aegis Twin:** The platform and product suite.
- **Knowledge Graph:** Graph representation of code, services, dependencies, and runtime data.
- **Impact Simulation:** AI-based prediction of change consequences.
- **Blast Radius:** Scope of affected components, services, and data flows.
- **Risk Score:** Numeric and categorical assessment of change risk.
- **GraphRAG:** Graph-based retrieval augmented generation.

### 1.5 References
- Internal architecture notes
- Source control provider APIs
- VS Code extension API documentation
- Neo4j and OpenTelemetry documentation

## 2. Overall Description

### 2.1 Product Perspective
Aegis Twin operates as a modular platform with five layers:
1. Ingestion and parsing
2. Knowledge graph storage
3. AI reasoning and simulation
4. Backend services and APIs
5. Developer and reviewer interfaces

The product integrates with source control, observability systems, and developer tools, enabling continuous architectural intelligence.

### 2.2 Product Functions
- Repository ingestion and dependency extraction
- Architecture graph creation and incremental updates
- Telemetry enrichment for service health and runtime context
- AI simulation and risk explanation for proposed changes
- Dashboard visualization and reporting
- IDE plugin risk annotations and commands
- CI/CD PR risk checks and merge guardrails
- Adaptive learning from production outcomes

### 2.3 User Classes
- **Software Engineers:** receive inline risk feedback, explanations, and simulation commands.
- **Software Architects:** analyze system topology, dependencies, and risk hotspots.
- **DevOps/Platform Engineers:** configure observability, integrations, and runtime thresholds.
- **Engineering Managers:** monitor risk trends, architectural debt, and delivery health.

### 2.4 Operating Environment
- Cloud-hosted backend services or container orchestration
- Modern browsers for dashboard access
- VS Code / Cursor-compatible IDE environment
- Access to GitHub/GitLab/Bitbucket and observability APIs

### 2.5 Assumptions and Dependencies
- Repository access credentials are available
- Telemetry sources emit OpenTelemetry or Prometheus-compatible metrics
- Users have VS Code or Cursor installed
- Backend has network access to external services and LLM provider

## 3. System Architecture

### 3.1 High-Level Architecture
- **Ingestion Service:** parses repos and infrastructure, extracts entities and relationships.
- **Graph Database:** Neo4j or equivalent stores nodes, relationships, and metrics.
- **Vector/Embedding Store:** stores embeddings for GraphRAG retrieval.
- **AI Reasoning Service:** orchestrates LLM prompts, retrieval, and explanation generation.
- **Backend API:** exposes REST endpoints for dashboard, plugin, CI, and ingestion.
- **Web Dashboard:** React/TypeScript UI for visualization, simulation, and administration.
- **IDE Plugin:** VS Code extension for in-editor risk feedback.

### 3.2 Component Architecture
- **Parser Modules:** Tree-Sitter adapters for Python, TypeScript, Java, Go, Rust.
- **Graph Model:** nodes for Service, Endpoint, Function, Class, Database, Queue, Deployment, Change.
- **Relationship Types:** CALLS, DEPENDS_ON, READS_FROM, WRITES_TO, OWNED_BY, IMPACTS.
- **Simulation Engine:** uses graph traversal, heuristics, and LLM reasoning.
- **Telemetry Adapter:** maps metrics to graph components.

### 3.3 Deployment Architecture
- Containerized deployment via Docker
- Orchestrated with Docker Compose or Kubernetes
- Backend and graph database in a secure VPC
- Frontend served from CDN or app host
- Extension communicates with backend over HTTPS

## 4. Functional Requirements

### FR1: Repository and Infrastructure Ingestion
1.1 Support GitHub, GitLab, Bitbucket sources.
1.2 Parse monorepos and multi-repo projects.
1.3 Extract services, endpoints, functions, classes, imports, and dependencies.
1.4 Ingest infrastructure definitions from Docker, Kubernetes, docker-compose, and manifest files.
1.5 Support incremental syncs for changed files and full refresh of graph data.

### FR2: Knowledge Graph Management
2.1 Represent software entities as graph nodes.
2.2 Capture dependency and runtime relationships.
2.3 Maintain historical change events and version metadata.
2.4 Provide graph queries for impact analysis and visualization.

### FR3: Telemetry Enrichment
3.1 Ingest OpenTelemetry and Prometheus metrics.
3.2 Map metrics to services, endpoints, and data flows.
3.3 Store real-time and historical metrics on graph nodes.
3.4 Surface metric anomalies and risk signals.

### FR4: AI-Powered Predictive Simulation
4.1 Accept input: Git diff, PR, code snippet, or change description.
4.2 Identify changed graph nodes and dependencies.
4.3 Compute blast radius with graph traversal and impact scoring.
4.4 Generate risk score and classification: Low, Medium, High, Critical.
4.5 Produce mitigation recommendations and explanation text.
4.6 Show confidence and uncertainty indicators.
4.7 Allow export of simulation results as PDF/JSON.

### FR5: Web Dashboard
5.1 Architecture Explorer
- Interactive topology graph with React Flow
- Search, filters, and component grouping
- Node detail panel with health, ownership, and metrics
- Risk heatmap and critical path highlighting

5.2 Simulation Studio
- Upload diff, select PR, or describe change scenario
- Run simulation with progress feedback
- Display risk gauge, affected services, and impact table
- Provide AI explanation, recommendations, and confidence

5.3 Pull Request Review
- List open PRs with risk badges
- Show per-PR impact summary and recommendation cards
- Enable review comments or approval suggestions

5.4 Health & Insights
- Risk trend charts and hotspot dashboards
- Top risky services and architectural debt indicators
- Telemetry trends for latency, errors, and throughput

5.5 Settings and Administration
- Configure integrations, risk thresholds, and alerts
- Manage access, authentication, and audit logs
- Set project-specific policies and CI/CD rules

### FR6: IDE Plugin
6.1 Provide real-time analysis in VS Code / Cursor.
6.2 Show inline decorations for risk on changed code.
6.3 Display a sidebar with current file risk and blast radius.
6.4 Offer hover actions with explanations and suggestions.
6.5 Expose command palette commands for simulation and dashboard access.
6.6 Show status bar risk indicator and plugin state.
6.7 Allow per-user configuration via settings.

### FR7: CI/CD Guardrails
7.1 Provide GitHub Action or integration for PR analysis.
7.2 Automatically run simulation on PR open/update.
7.3 Post risk summary and recommendations to PR comments.
7.4 Support status checks and merge policies for critical risk.
7.5 Allow repository-level configuration of thresholds and strictness.

### FR8: Adaptive Learning
8.1 Capture actual post-deployment outcomes and metrics.
8.2 Compare predicted impact against observed results.
8.3 Adjust scoring and recommendation models based on feedback.
8.4 Track prediction accuracy and calibration over time.

## 5. External Interface Requirements

### 5.1 User Interfaces
- Web dashboard accessible in modern browsers
- VS Code/Cursor extension UI elements
- REST API for integrations
- CLI or automation hooks for advanced workflows

### 5.2 Software Interfaces
- GitHub/GitLab/Bitbucket APIs
- Neo4j graph database
- LLM provider APIs (Claude, OpenAI, or equivalent)
- OpenTelemetry and Prometheus ingestion endpoints
- Authentication service (OAuth2/JWT)

### 5.3 Communication Interfaces
- HTTPS/TLS for all client-server communication
- WebSocket or SSE for real-time updates
- JSON/REST for backend APIs and plugin calls

## 6. Data Requirements

### 6.1 Knowledge Graph Schema
- Node types: Service, Endpoint, Function, Class, Database, Queue, Deployment, ChangeEvent, User
- Relationship types: CALLS, DEPENDS_ON, READS_FROM, WRITES_TO, OWNED_BY, IMPACTS
- Properties: riskScore, latency, errorRate, owner, lastModified, serviceLevel

### 6.2 Telemetry Data
- Required metrics: latency (p50/p95/p99), error rate, throughput
- Optional metrics: resource utilization, traffic volume, custom business events
- Mapping between telemetry streams and graph entities

### 6.3 AI Model Data
- Embeddings for code, graph context, and change events
- Prompt templates and retrieval context
- Simulation history for audit and improvement

## 7. Non-Functional Requirements

### 7.1 Performance
- Dashboard graph rendering under 2 seconds for 500 nodes
- Simulation response within 15 seconds for typical PRs
- IDE analysis refresh within 2-3 seconds after edit or save

### 7.2 Scalability
- Support repositories with 15,000+ functions and 1,000+ services
- Support multiple projects and tenants in a shared deployment
- Scale ingestion and AI reasoning independently

### 7.3 Reliability
- 99.5% uptime for backend services
- Graceful degradation for dashboard and plugin features when external services are unavailable
- Retry and circuit breaker behavior for external integrations

### 7.4 Security
- Strong authentication and authorization
- Data encryption in transit and at rest
- Role-based access control for dashboard and API
- Audit logging for key actions and simulations
- Secure handling of secrets and credentials

### 7.5 Usability
- Clean, developer-friendly interfaces
- Minimal onboarding and intuitive workflows
- Consistent in-editor guidance and dashboard navigation

### 7.6 Accessibility
- WCAG 2.1 AA compliance for dashboard
- Keyboard navigation, contrast, and screen reader support

### 7.7 Maintainability
- Modular architecture and clear separation of concerns
- Well-documented APIs and data schemas
- Automated tests covering unit, integration, and end-to-end flows

### 7.8 Compliance
- GDPR and data privacy alignment for telemetry and code metadata
- Secure logging and data retention policies

## 8. Use Cases

### UC1: Developer reviews a risky code change
- Developer edits code and saves.
- Aegis Twin analyzes the diff and highlights high-risk lines.
- Developer opens the sidebar, views blast radius, and reads mitigation guidance.

### UC2: Architect evaluates architecture drift
- Architect opens the dashboard explorer.
- They identify dependency hot spots and services with elevated risk.
- They run simulation on a proposed change and export a risk report.

### UC3: CI/CD gates merge on risk
- Developer opens a PR.
- CI integration runs Aegis simulation and posts a risk summary.
- Merge is blocked if critical risk is detected.

### UC4: Production feedback improves predictions
- After deployment, the platform ingests production metrics.
- Aegis Twin compares predictions to actual outcomes.
- The system adjusts risk calibration and recommendation quality.

## 9. Acceptance Criteria
- Ingestion service builds a knowledge graph from a sample repository.
- Dashboard visualizes architecture topology, dependencies, and risk data.
- Simulation outputs risk score, blast radius, and mitigation recommendations.
- IDE plugin highlights risky code and offers explanatory feedback.
- CI/CD integration posts PR risk reports and enforces merge rules.
- Adaptive learning pipeline records production outcomes and updates predictions.

## 10. Implementation Roadmap

### Phase 1: Foundation
- Establish repo ingestion and graph schema
- Implement backend API and Neo4j integration
- Build basic dashboard topology explorer

### Phase 2: Simulation and AI
- Add telemetry ingestion and mapping
- Implement change impact analysis and GraphRAG flow
- Build simulation studio and risk report output

### Phase 3: Developer Tooling
- Develop VS Code extension with inline feedback
- Add command palette and sidebar workflows
- Build CI/CD integration for PR checks

### Phase 4: Production Readiness
- Add adaptive learning and feedback loop
- Harden security, logging, and observability
- Complete accessibility and performance testing

### Phase 5: Launch and Scale
- Deploy production environment
- Monitor performance, reliability, and model accuracy
- Iterate on feedback and expand language/support coverage

## 11. Risks and Mitigation
- **LLM reliability:** Use GraphRAG and structured prompts to reduce hallucination.
- **Data privacy:** Limit storage of sensitive source content and secure telemetry.
- **Performance bottlenecks:** Cache graph queries and batch AI calls.
- **Adoption friction:** Provide intuitive UX and fast feedback loops.

## 12. Glossary
- **GraphRAG:** Graph-based retrieval-augmented generation.
- **Telemetry:** Runtime metrics from operating systems and services.
- **LLM:** Large language model used for reasoning and explanation.
- **PR:** Pull request.
- **CI:** Continuous integration.
- **CD:** Continuous delivery/deployment.
