# Test Plan

## Purpose
This plan describes the quality and validation approach for Aegis Twin, covering unit, integration, system, and acceptance testing.

## Test Objectives
- Verify functional requirements across ingestion, simulation, dashboard, plugin, and CI/CD.
- Validate non-functional behavior for performance, reliability, and security.
- Ensure the platform meets user workflows and acceptance criteria.

## Test Levels

### Unit Testing
- Parser modules for code and manifest extraction.
- Graph schema and relationship mapping.
- Backend API validation and request handling.
- AI prompt generation and result parsing.
- Plugin commands and UI state updates.

### Integration Testing
- Ingestion service writing to Neo4j.
- Simulation endpoint using graph data and telemetry.
- Dashboard fetching and rendering graph data.
- IDE plugin calling backend APIs and showing results.
- CI/CD workflow triggering PR analysis.

### End-to-End Testing
- Full flow from repository ingestion to dashboard visualization.
- Code change simulation from diff input to risk output.
- PR submission, CI check execution, and comment posting.
- IDE plugin change detection and risk decoration.

### Acceptance Testing
- Validate acceptance criteria listed in `srs.md`.
- Confirm dashboard and plugin UX flows with sample users.
- Verify that critical risk blocks PR merges when configured.

## Key Test Cases
- Build knowledge graph from sample repo and verify node counts.
- Simulate a code change and verify risk score, blast radius, explanation.
- Load dashboard architecture explorer and navigate node details.
- Use IDE plugin to highlight risky lines and open simulation.
- Run CI/CD action on PR update and confirm comment/status.
- Submit production feedback and validate learning records.

## Non-Functional Tests
- Performance: dashboard render time, simulation latency, plugin refresh time.
- Scalability: ingestion and simulation with large repository sample.
- Reliability: recover from Neo4j outages and LLM failures.
- Security: auth enforcement, input sanitization, audit logging.
- Accessibility: keyboard navigation and WCAG checks.

## Automation Strategy
- Use pytest for backend and ingestion tests.
- Use Playwright or Cypress for dashboard UI flows.
- Use VS Code extension test harness for plugin behavior.
- Use GitHub Actions for continuous test execution.

## Metrics
- Code coverage target: >80% for backend and core modules.
- Simulation accuracy tracking in production feedback.
- Test pass rates per build and deployment pipeline.
