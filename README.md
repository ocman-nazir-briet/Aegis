# Aegis Twin

Aegis Twin is an AI-native predictive digital twin platform for software architecture. It combines codebase ingestion, knowledge graph modeling, telemetry enrichment, and large language model reasoning to deliver change impact analysis, risk scoring, and developer guidance.

## Project Documents
- `srs.md` — Software Requirements Specification
- `API.md` — API and integration reference
- `architecture.md` — System architecture and component design
- `roadmap.md` — Implementation phases and timeline
- `test-plan.md` — Quality, testing, and validation plan
- `deployment.md` — Deployment strategy and environment requirements

## Key Capabilities
- Build a knowledge graph from source code and infrastructure manifests
- Predict impact of code changes with AI-powered simulations
- Show risk and blast radius in a web dashboard
- Provide inline IDE guidance via VS Code/Cursor extension
- Enforce risk-aware CI/CD guardrails
- Learn from production outcomes to improve future predictions

## Getting Started
1. Review `srs.md` for the full product requirements and scope.
2. Review `API.md` for backend contract and REST endpoints.
3. Use `architecture.md` to understand the system components.
4. Follow `roadmap.md` to plan implementation phases.
5. Use `test-plan.md` to validate functionality and non-functional requirements.
6. Use `deployment.md` when deploying to staging or production.

## Next Steps
- Build the backend service and Neo4j graph integration.
- Develop the dashboard and IDE plugin according to the SRS.
- Implement CI/CD checks for PR risk analysis.
- Set up telemetry ingestion and adaptive feedback loops.
