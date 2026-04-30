# Aegis Twin — Setup & Startup Guide

**Status:** Phase 5 (Enhanced Integration) implementation complete. Frontend, Backend, and VS Code Extension are fully implemented and verified connected.

## Quick Start (5 minutes)

### Prerequisites
- Python 3.13+
- Node.js 18+
- Docker & Docker Compose (optional, for Neo4j)
- VS Code 1.85+ (for extension testing)

### 1. Start Neo4j (Required for Full Functionality)

**Option A: Docker**
```bash
docker-compose up -d neo4j
# Wait 10 seconds for startup
```

**Option B: Local**
Download and run from https://neo4j.com/download/community/ — ensure it's running on `neo4j://localhost:7687` with default credentials `neo4j:password`.

### 2. Start Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
export NEO4J_URI=neo4j://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password
export ANTHROPIC_API_KEY=your-key-here  # or leave blank for now
python main.py
# Server runs on http://localhost:8000
```

### 3. Start Frontend (separate terminal)
```bash
cd frontend
npm install
npm run dev
# Dashboard available on http://localhost:3000
```

### 4. Test Backend-Frontend Connection
```bash
curl http://localhost:3000/api/v1/health
# Expected: {"success": false, "message": "..."}  (Neo4j not populated yet is OK)
```

### 5. (Optional) Load VS Code Extension

1. Open `vscode-extension/` in VS Code
2. Press `F5` to open Extension Development Host
3. Open any file and save it → status bar shows "Aegis: Analyzing..."
4. Configure API URL in VS Code settings: `aegisTwin.apiUrl: http://localhost:8000`

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    VS Code Extension                 │
│  • Decorations (inline risk highlights)              │
│  • Status bar (risk level)                           │
│  • Sidebar (detailed report)                         │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP POST /api/v1/simulate/change
                   ▼
┌─────────────────────────────────────────────────────┐
│             FastAPI Backend (8000)                   │
│  • Auth (JWT + RBAC)                                 │
│  • Simulation engine                                 │
│  • GitHub integration                                │
│  • Infrastructure parsing                            │
│  • Neo4j graph service                               │
└──────────────────┬──────────────────────────────────┘
                   │ Reads/writes graphs
                   ▼
┌─────────────────────────────────────────────────────┐
│              Neo4j (7687)                            │
│  • Infrastructure topology                           │
│  • Change history                                    │
│  • Blast radius cache                                │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│             React Frontend (3000)                    │
│  • Architecture Explorer                             │
│  • Simulation Results                                │
│  • Monitoring Dashboard                              │
│  • PR Review                                         │
│  • Health Insights                                   │
│  • Settings                                          │
└──────────────────┬──────────────────────────────────┘
                   │ Proxy: /api → localhost:8000
                   ▼
         (FastAPI Backend above)
```

---

## Component Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Backend** | ✅ Complete | FastAPI server, Auth, Simulation, GitHub API, Prometheus metrics |
| **Frontend** | ✅ Complete | React dashboard, 6 tabs (Explorer, Simulation, Monitoring, PRReview, Health, Settings) |
| **VS Code Extension** | ✅ Complete | Decorations, status bar, sidebar, auto-analyze on save |
| **GitHub Actions** | ✅ Complete | Automatic PR risk comment + Critical merge blocking |
| **Neo4j** | ⚠️ Required | Must be running for full functionality; seed scripts optional |
| **Tests** | ❌ Pending | Unit tests, integration tests, E2E tests (Phase 5E) |
| **Production Deployment** | ❌ Pending | Kubernetes manifests, Helm chart, TLS, monitoring (Phase 5F) |

---

## Configuration

### Backend (backend/.env)
```ini
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme
VIEWER_USERNAME=viewer
VIEWER_PASSWORD=viewonly
ANTHROPIC_API_KEY=sk-...  # Optional; LLM features disabled without it
GITHUB_TOKEN=ghp_...       # Optional; GitHub integration requires it
JWT_SECRET=your-secret-here
JWT_ALGORITHM=HS256
```

### Frontend (frontend/.env)
```ini
VITE_API_URL=http://localhost:8000
```

### VS Code Extension (VS Code settings.json)
```json
{
  "aegisTwin.apiUrl": "http://localhost:8000",
  "aegisTwin.token": "",
  "aegisTwin.autoAnalyzeOnSave": true
}
```

---

## API Endpoints

### Core
- `GET /` → 200 OK (health check)
- `GET /api/v1/health` → Backend status + Neo4j connectivity

### Simulation
- `POST /api/v1/simulate/change` → Analyze diff + repo URL
- `GET /api/v1/pr/{pr_id}/analysis` → Historical PR analysis

### Architecture
- `GET /api/v1/architecture/map` → Full infrastructure graph
- `GET /api/v1/graph/stats` → Graph node/edge counts

### Monitoring
- `GET /api/v1/monitoring/metrics` → Time-series latency/accuracy
- `GET /metrics` → Prometheus-format metrics

### Insights
- `GET /api/v1/insights/hotspots` → High-risk components
- `GET /api/v1/insights/centrality` → Most-impactful services

### Auth
- `POST /api/v1/auth/token` → Exchange credentials for JWT
- `POST /api/v1/auth/register` → Register new user (if enabled)

### Admin
- `POST /api/v1/admin/ingest/webhook` → GitHub webhook receiver
- `POST /api/v1/admin/ingest/batch` → Batch ingest repositories

---

## Troubleshooting

**Backend fails to start: "Neo4j connection failed"**
→ Ensure Neo4j is running on `neo4j://localhost:7687` with correct credentials

**Frontend shows "502 Bad Gateway" on API calls**
→ Backend is not running on port 8000; check `npm run dev` terminal

**VS Code extension shows "No git diff available"**
→ Open a git repository and make edits; unsaved changes don't trigger diffs

**"Bearer token required" error**
→ Some endpoints require auth. Set `Authorization: Bearer <jwt_token>` header

---

## Next Steps

1. **Populate data:** Run a simulation with a real repo URL to seed the graph
2. **Connect GitHub:** Set `GITHUB_TOKEN` and run `/admin/ingest/batch` to import repositories
3. **Monitor:** Check `/metrics` endpoint with Prometheus scraper (optional)
4. **Deploy:** Use Phase 5F (Production Deployment) manifests for cloud deployment

---

## Testing the System End-to-End

```bash
# 1. Ensure all services are running
curl http://localhost:8000/api/v1/health        # Backend
curl http://localhost:3000                       # Frontend
# Neo4j: check http://localhost:7474

# 2. Get auth token
ADMIN_TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}' \
  | jq -r '.data.access_token')

# 3. Run a simulation
curl -X POST http://localhost:8000/api/v1/simulate/change \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "diff": "--- a/src/api.py\n+++ b/src/api.py\n@@ -10,7 +10,9 @@ def handler():\n   return response",
    "repo_url": "https://github.com/user/repo"
  }'

# 4. View results in frontend
open http://localhost:3000
# Click "Simulation" tab to see results

# 5. Check architecture graph
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/architecture/map

# 6. Check monitoring metrics
curl http://localhost:8000/api/v1/monitoring/metrics | head -20
```

---

## Known Limitations & TODOs

- **Testing:** No automated test suite (Phase 5E)
- **Deployment:** No Kubernetes/Helm manifests (Phase 5F)
- **Real-time:** Graph updates require page refresh (WebSocket upgrade pending)
- **Scaling:** Single-instance deployment; load-balancing not configured

---

For detailed implementation notes, see:
- [PHASE3_VERIFICATION.md](./PHASE3_VERIFICATION.md) — VS Code extension details
- [PHASE4_IMPLEMENTATION.md](./PHASE4_IMPLEMENTATION.md) — Backend routes & services
- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) — Overall architecture
