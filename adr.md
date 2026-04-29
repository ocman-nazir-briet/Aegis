# Architecture Decision Records (ADR)

## ADR 1: Knowledge Graph Database
**Decision:** Use Neo4j as the core knowledge graph database.
**Status:** Approved
**Context:** Neo4j provides mature graph querying, relationship modeling, and native graph analytics.
**Consequences:** Simplifies impact analysis and topology queries, but requires optimized data modeling for scale.

## ADR 2: Parser Strategy
**Decision:** Use Tree-Sitter for multi-language parsing.
**Status:** Approved
**Context:** Tree-Sitter supports reliable syntax trees for Python, TypeScript, Java, Go, and Rust.
**Consequences:** Enables extensible parser support and accurate dependency extraction.

## ADR 3: AI Reasoning Architecture
**Decision:** Implement GraphRAG for simulation prompts.
**Status:** Approved
**Context:** Combining graph context with retrieval-augmented LLM prompts reduces hallucination and improves risk assessment accuracy.
**Consequences:** Requires semantic embeddings and retrieval infrastructure.

## ADR 4: IDE Integration
**Decision:** Build a VS Code/Cursor extension using TypeScript.
**Status:** Approved
**Context:** VS Code is the primary developer environment and supports rich editor integration.
**Consequences:** Plugin can deliver inline feedback and command palette workflows.

## ADR 5: CI/CD Enforcement
**Decision:** Use GitHub Actions for initial PR risk guardrails.
**Status:** Approved
**Context:** GitHub is the most common VCS and supports status checks and automated comments.
**Consequences:** Future support can expand to GitLab and Bitbucket.

## ADR 6: Authentication
**Decision:** Use OAuth2/JWT for API and dashboard authentication.
**Status:** Approved
**Context:** Standard secure approach for modern web applications.
**Consequences:** Supports SSO and token-based authorization.
