# Aegis Twin — Full Gap Analysis
**Date:** April 29, 2026  
**Baseline:** SRS v3.0 + API.md + architecture.md + data-model.md + security-plan.md + test-plan.md  
**Current state:** Phases 1–4 implemented

---

## Audit Summary

| Area | Implemented | Missing | Coverage |
|------|-------------|---------|----------|
| Ingestion & Parsing | Basic regex parser | Tree-Sitter, infra parsing, Git APIs, incremental sync | ~25% |
| Knowledge Graph Schema | Service, Function, Endpoint, Database, ChangeEvent | Class, Queue, User nodes; missing relationships | ~60% |
| AI Simulation | GraphRAG + LLM, blast radius, mitigations | PDF export, anomaly detection | ~85% |
| Web Dashboard | Topology SVG, Simulation Studio, Monitoring | React Flow, PR Review, Settings/Admin, Heatmap | ~45% |
| IDE Plugin | Decorations, sidebar, commands, status bar | Hover explanations | ~90% |
| CI/CD | GitHub Actions workflow | GitLab/Bitbucket, repository config UI | ~60% |
| Adaptive Learning | Feedback recording, accuracy tracking | Auto-calibration, model retraining loop | ~50% |
| Authentication | jwt_secret in config | JWT middleware, OAuth2, RBAC — none enforced | ~5% |
| Security | Parameterized queries, CORS | Rate limiting, input scanning, SSO | ~30% |
| Testing | No tests written | Full pytest suite, Playwright E2E, coverage | ~0% |
| Observability | Request logging, Neo4j metrics | Prometheus export, alerting, Grafana | ~20% |
| Deployment | Docker Compose (dev) | Kubernetes, staging, production configs | ~20% |
| Real-time | None | WebSocket/SSE for live updates | ~0% |

---

## Detailed Gaps by SRS Section

### FR1 — Repository & Infrastructure Ingestion

| Requirement | Status | Notes |
|-------------|--------|-------|
| GitHub/GitLab/Bitbucket API integration | ❌ Missing | Tokens in config but no API calls |
| Monorepo + multi-repo support | ❌ Missing | Single repo assumption only |
| Extract classes (FR1.3) | ❌ Partial | Only functions and endpoints via regex |
| Infrastructure: Docker, K8s, manifests | ❌ Missing | Not parsed at all |
| Incremental sync (changed files only) | ❌ Missing | Full re-parse only |
| Tree-Sitter multi-language parsing | ⚠️ Installed | Library installed but not wired up |

### FR2 — Knowledge Graph

| Requirement | Status | Notes |
|-------------|--------|-------|
| Class nodes | ❌ Missing | Not in schema or services |
| Queue nodes | ❌ Missing | Not in schema or services |
| User nodes | ❌ Missing | Not in schema or services |
| READS_FROM relationship | ❌ Missing | Only CALLS, DEPENDS_ON, RELIANT_ON exist |
| WRITES_TO relationship | ❌ Missing | — |
| OWNED_BY relationship | ❌ Missing | — |
| IMPACTS relationship | ❌ Missing | — |
| Historical change tracking | ⚠️ Partial | ChangeEvent exists, no versioning |

### FR3 — Telemetry

| Requirement | Status | Notes |
|-------------|--------|-------|
| Prometheus metric ingestion | ✅ Done | telemetry_service.py handles it |
| Map metrics to graph nodes | ✅ Done | — |
| Anomaly detection / risk signals | ❌ Missing | No statistical analysis of metrics |

### FR4 — AI Simulation

| Requirement | Status | Notes |
|-------------|--------|-------|
| Risk score + blast radius + mitigations | ✅ Done | — |
| Confidence + uncertainty indicators | ✅ Done | — |
| Export simulation as PDF | ❌ Missing | Only JSON export |
| Stale graph warning (> 24h) | ❌ Missing | Not implemented |

### FR5 — Web Dashboard

| Requirement | Status | Notes |
|-------------|--------|-------|
| Interactive topology (React Flow) | ❌ Missing | Using plain SVG with grid layout |
| Search + filter + component grouping | ❌ Missing | No search in explorer |
| Risk heatmap on graph | ❌ Missing | No color coding by risk in explorer |
| Critical path highlighting | ❌ Missing | — |
| Simulation Studio | ✅ Done | — |
| PR Review page (FR5.3) | ❌ Missing | Entire section not built |
| Health & Insights charts | ⚠️ Partial | Hotspots list only, no charts |
| Telemetry trend charts | ❌ Missing | No time-series charts |
| Settings & Administration page (FR5.5) | ❌ Missing | No UI for config, integrations, RBAC |

### FR6 — IDE Plugin

| Requirement | Status | Notes |
|-------------|--------|-------|
| Inline risk decorations | ✅ Done | — |
| Sidebar with blast radius | ✅ Done | — |
| Hover actions with explanations (FR6.4) | ❌ Missing | No hover providers |
| Command palette commands | ✅ Done | — |
| Status bar indicator | ✅ Done | — |
| Per-user configuration | ✅ Done | — |

### FR7 — CI/CD Guardrails

| Requirement | Status | Notes |
|-------------|--------|-------|
| GitHub Actions workflow | ✅ Done | — |
| PR risk comment + status check | ✅ Done | — |
| Merge blocking on Critical | ✅ Done | — |
| Repository-level threshold config | ❌ Missing | Hardcoded only |
| GitLab / Bitbucket support | ❌ Missing | GitHub only |

### FR8 — Adaptive Learning

| Requirement | Status | Notes |
|-------------|--------|-------|
| Record post-deployment outcomes | ✅ Done | FeedbackService |
| Compare prediction vs actual | ✅ Done | accuracy_score field |
| Adjust scoring based on feedback | ❌ Missing | Data collected but not used to retune |
| Track prediction accuracy over time | ✅ Done | MonitoringService |

### Non-Functional Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| JWT / OAuth2 authentication | ❌ Critical | jwt_secret in config but zero enforcement |
| RBAC (admin/analyst/viewer roles) | ❌ Missing | — |
| Rate limiting (60 req/min simulation) | ❌ Missing | No rate limiter |
| Input scanning (secrets in diffs) | ❌ Missing | No pattern scanning |
| WCAG 2.1 AA accessibility | ❌ Missing | No aria labels, no keyboard nav audit |
| Automated test suite | ❌ Missing | Zero tests written |
| Prometheus metrics export | ❌ Missing | Internal metrics only |
| WebSocket / SSE real-time updates | ❌ Missing | Polling only |
| Kubernetes deployment manifests | ❌ Missing | Docker Compose only |
| Admin API endpoints | ❌ Missing | /admin/rebuild-indexes, /admin/clear-graph, /admin/audit-log |
| Circuit breaker for Neo4j + LLM | ⚠️ Partial | Retry exists, no circuit breaker |
| Stale graph detection | ❌ Missing | No warning if graph > 24h old |
| Frontend served from CDN | ❌ Missing | Dev only |
| Correlation IDs in logs | ❌ Missing | Basic structured logs, no request IDs |

---

## Prioritized Missing Features

### P0 — Blocking for any real use
1. **JWT authentication middleware** — all endpoints currently open
2. **Rate limiting** — simulation endpoints can be abused
3. **Automated test suite** — zero tests is unacceptable for production

### P1 — Core product gaps (SRS explicitly required)
4. **React Flow topology** — SVG grid is unacceptable for production UX
5. **PR Review dashboard page** — entire FR5.3 unbuilt
6. **Tree-Sitter integration** — critical for accurate code parsing
7. **Hover explanations in IDE** — explicitly in FR6.4
8. **PDF export** — explicitly in FR4.7
9. **Admin endpoints** — /admin/rebuild-indexes, /admin/audit-log

### P2 — Architecture completeness
10. **Class + Queue + User graph nodes** — data model incomplete
11. **Missing relationships** (READS_FROM, WRITES_TO, OWNED_BY, IMPACTS)
12. **GitHub API integration** — currently uses local git only
13. **Infrastructure parsing** (Docker, K8s, manifests)
14. **Incremental sync** — full refresh only

### P3 — Observability & operations
15. **Prometheus metrics export**
16. **WebSocket/SSE real-time updates**
17. **Correlation IDs in logs**
18. **Stale graph warning**
19. **Kubernetes manifests**
20. **Settings/Admin UI page**

### P4 — Nice to have
21. **Telemetry trend charts** (time-series)
22. **Risk heatmap on graph**
23. **GitLab / Bitbucket CI/CD support**
24. **Anomaly detection on metrics**
25. **Accessibility (WCAG 2.1 AA)**
26. **SSO / enterprise auth**
27. **Auto-calibration of LLM scoring from feedback**

---

## Revised Phase Plan

### Phase 5A: Security & Authentication ← DO FIRST
*Unblocks all other work; nothing should ship without auth*

- JWT middleware enforcing Bearer tokens on all routes
- `/auth/token` endpoint (password or API-key grant)
- Role-based decorators: `admin`, `analyst`, `viewer`
- Rate limiting on `/simulate/change` (60 req/min)
- Admin endpoints: `/admin/rebuild-indexes`, `/admin/clear-graph`, `/admin/audit-log`
- Correlation IDs injected into all structured logs
- Stale graph warning (last_synced > 24h)

### Phase 5B: Dashboard UX Overhaul
*Current SVG explorer is not production-quality per SRS FR5*

- Replace SVG grid with **React Flow** interactive topology
  - Drag-and-drop nodes
  - Zoom/pan
  - Risk heatmap color coding
  - Critical path highlighting
- Search and filter bar across nodes
- **PR Review page** — list open PRs with risk badges + detail cards
- **Health & Insights page** — time-series charts (latency, errors, throughput)
- **Settings/Admin page** — integrations, thresholds, user management

### Phase 5C: Enhanced Ingestion
*FR1 currently at ~25% — this is the core data quality layer*

- Wire up **Tree-Sitter** for Python, TypeScript (replace regex)
- Add **Class** and **Queue** node extraction
- Add **GitHub API** integration (list repos, fetch diffs, webhooks)
- **Infrastructure parsing** — Docker Compose, Kubernetes manifests
- **Incremental sync** — changed files only
- Add missing relationships (READS_FROM, WRITES_TO, OWNED_BY)

### Phase 5D: IDE & CI Completeness
*Finish the remaining IDE/CI gaps*

- **Hover provider** in VS Code extension — show risk explanation on hover
- **PDF export** for simulation results (browser print-to-PDF or server-side)
- **Repository-level threshold config** — YAML/JSON file for risk thresholds
- **Prometheus metrics endpoint** (`/metrics` for Grafana)
- **WebSocket** for real-time graph updates in dashboard

### Phase 5E: Testing & Accessibility
*Required by test-plan.md; 0% complete currently*

- **pytest suite**: unit tests for all services (simulation, telemetry, feedback, ingestion)
- **Integration tests**: Neo4j write/read, LLM call mocking, API contract
- **Playwright E2E**: dashboard flows (explore → simulate → feedback)
- **VS Code extension test harness**
- **WCAG 2.1 AA audit** — aria labels, keyboard nav, contrast ratios
- **Load test**: 100 concurrent users against simulation endpoint

### Phase 5F: Production Deployment
*Kubernetes + observability for real production*

- **Kubernetes manifests** — Deployment, Service, Ingress for all components
- **Helm chart** — parameterized K8s deployment
- **Prometheus + Grafana** — metrics dashboards
- **AlertManager** — rules for 5xx rate, slow queries, low accuracy
- **Neo4j backups** — scheduled snapshots
- **TLS** — cert-manager or existing certificate provisioning
- **CI pipeline** — automated build, test, push, deploy

---

## Recommended Execution Order

```
Phase 5A: Security & Auth     (1 week)  — unblocks everything
Phase 5B: Dashboard UX        (2 weeks) — biggest user-visible gap  
Phase 5C: Enhanced Ingestion  (1.5 wks) — data quality foundation
Phase 5D: IDE & CI Completeness (1 week) — close remaining SRS gaps
Phase 5E: Testing & A11y      (1 week)  — quality gate before launch
Phase 5F: Production Deploy   (1 week)  — go live
```

**Total estimated: ~8 weeks to full SRS compliance**

The system is functional end-to-end but is not yet production-safe (no auth), not fully SRS-compliant (missing React Flow, PR Review, Tree-Sitter, tests), and not deployment-ready (no K8s, no TLS, no monitoring pipeline).
