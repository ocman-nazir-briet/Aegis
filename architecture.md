# Architecture Overview

## Purpose
This document describes the architecture of Aegis Twin, including the main components, data flow, and deployment topology.

## System Components

### Ingestion Service
- Parses source repositories from GitHub/GitLab/Bitbucket.
- Uses Tree-Sitter adapters for supported languages: Python, TypeScript, Java, Go, Rust.
- Extracts services, functions, endpoints, and dependencies.
- Parses infrastructure definitions from Docker, Kubernetes, and manifest files.

### Knowledge Graph
- Stores software entities and relationships in Neo4j.
- Node types: Service, Endpoint, Function, Class, Database, Queue, Deployment, ChangeEvent, User.
- Relationship types: CALLS, DEPENDS_ON, READS_FROM, WRITES_TO, OWNED_BY, IMPACTS.
- Supports graph queries for impact analysis and visualization.

### Vector/Embedding Store
- Stores semantic embeddings for code and graph context.
- Enables GraphRAG retrieval during simulation.
- Can use Neo4j vector indexes or a dedicated vector store.

### AI Reasoning Service
- Orchestrates retrieval, prompt assembly, and LLM calls.
- Uses the knowledge graph and telemetry context to generate predictions.
- Produces risk scores, blast radius estimates, explanations, and mitigations.

### Backend API
- Exposes REST endpoints for ingestion, simulation, dashboard data, plugin integration, and CI/CD workflows.
- Implements authentication with OAuth2/JWT.
- Provides health, audit, and admin endpoints.

### Web Dashboard
- Built with React + TypeScript and React Flow.
- Visualizes architecture topology and risk heatmaps.
- Supports simulation studio, PR review, and insights dashboards.
- Manages configuration, thresholds, and access controls.

### IDE Plugin
- VS Code / Cursor extension written in TypeScript.
- Provides inline risk decorations and hover explanations.
- Offers commands to simulate changes and open dashboard reports.
- Uses backend APIs for analysis and metadata.

### CI/CD Integration
- GitHub Actions or app integration runs simulation on PR events.
- Posts risk summaries, status checks, and merge guardrail feedback.

## Data Flow
1. Source repository ingestion builds the knowledge graph.
2. Telemetry ingestion enriches graph nodes with runtime metrics.
3. Code changes are analyzed and mapped to graph entities.
4. AI simulation uses graph retrieval + telemetry context to compute risk.
5. Results flow to dashboard, IDE plugin, and CI/CD systems.

## Deployment Topology
- Containerized services deployed with Docker Compose or Kubernetes.
- Backend and Neo4j in a secure network.
- Frontend served from a web host or CDN.
- Plugin communicates over HTTPS to backend.
- Optional WebSocket/SSE for realtime updates.

## Security and Operations
- TLS for all communication.
- Role-based access control for users and projects.
- Audit logs for ingestion, simulation, and feedback events.
- Monitoring of backend, graph, and LLM usage.
