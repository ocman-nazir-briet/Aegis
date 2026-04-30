# Aegis Twin — Platform Integration Summary

**Status:** ✅ ALL BACKEND APIs FULLY INTEGRATED WITH FRONTEND  
**Authentication:** ✅ JWT-based auth system implemented  
**Testing:** Ready for use  

---

## 🎯 Quick Start (2 minutes)

```bash
# Terminal 1: Start backend
cd backend
./start-backend.sh

# Terminal 2: Start frontend (new terminal)
cd frontend
./start-frontend.sh

# Terminal 3: Start Neo4j (new terminal, optional)
docker-compose up neo4j

# Then open browser
open http://localhost:3000
```

**Login with:**
- Username: `admin`
- Password: `changeme`

---

## ✅ Integration Status: ALL COMPLETE

| Component | Status | Auth Required | Endpoints |
|-----------|--------|---------------|-----------|
| **Login Screen** | ✅ | N/A | POST `/api/auth/token` |
| **Auth System** | ✅ | JWT | All requests |
| **Dashboard Tabs** | ✅ | Yes | See below |
| **Simulation** | ✅ | Analyst+ | `/api/v1/simulate/change`, `/api/v1/simulate/whatif` |
| **Architecture** | ✅ | Viewer+ | `/api/v1/architecture/map`, `/api/v1/graph/stats` |
| **Monitoring** | ✅ | Viewer+ | `/api/v1/monitoring/metrics`, `/api/v1/monitoring/accuracy`, `/api/v1/monitoring/performance` |
| **PR Review** | ✅ | Viewer+ | `/api/v1/changes/recent` |
| **Health Insights** | ✅ | Viewer+ | `/api/v1/insights/hotspots`, `/api/v1/insights/centrality` |
| **Settings** | ✅ | Admin+ | `/admin/*` endpoints |
| **PDF Export** | ✅ | Viewer+ | POST `/api/v1/export/pdf` |
| **Feedback** | ✅ | Analyst+ | POST `/api/v1/feedback/prediction` |
| **VS Code Extension** | ✅ | Token-based | `/api/v1/simulate/change`, `/api/v1/insights/hotspots` |
| **GitHub Actions** | ✅ | API key-based | `/api/v1/simulate/change`, `/api/v1/ingest/webhook` |

---

## 🔐 How Authentication Works

### 1. Login
```bash
POST /api/auth/token
{
  "username": "admin",
  "password": "changeme"
}

Response:
{
  "access_token": "eyJhbGc...",
  "role": "admin",
  "expires_in": 3600
}
```

### 2. Token Storage
- Token saved to **localStorage** (`aegis_token`)
- Username saved to **localStorage** (`aegis_user`)
- Role saved to **localStorage** (`aegis_role`)

### 3. Auto-Injection
- **Axios interceptor** auto-attaches token to all API requests
- Header: `Authorization: Bearer <token>`
- Works for all authenticated endpoints

### 4. Session Management
- Tokens expire after **60 minutes**
- On 401 response, token cleared and user redirected to login
- Logout button in header clears token

---

## 📱 Dashboard Tabs & Integrations

### 1. 🏗️ Architecture Explorer

**What it does:** Displays interactive graph of system topology

**APIs called:**
```
GET /api/v1/architecture/map?limit=500   (initial load)
GET /api/v1/graph/stats                  (sidebar stats)
```

**Authentication:** Viewer+

**User flow:**
1. Click "Architecture Explorer" tab
2. Component fetches architecture graph
3. Graph renders with React Flow
4. Click node → see details

**Data shown:**
- Node type (Service, Function, Endpoint, Database, etc.)
- Risk scores (color-coded)
- Connections/edges
- Node statistics

---

### 2. 🧪 Simulation Studio

**What it does:** Run risk analysis on proposed changes

**APIs called:**
```
POST /api/v1/simulate/change   (diff-based analysis)
POST /api/v1/simulate/whatif   (scenario analysis)
```

**Authentication:** Analyst+ (admin can also use)

**User flow:**
1. Click "Simulation Studio" tab
2. Choose mode: "Diff-based" or "What-if Scenario"
3. Fill in required fields
4. Click "Run Simulation"
5. Results appear on right panel

**Diff-based inputs:**
- Repository URL (required)
- Git diff (required) — paste `git diff origin/main...HEAD`
- PR URL (optional)
- Context (optional)

**What-if inputs:**
- Repository URL (required)
- Scenario description (required) — "increase timeout to 30s"
- Target service (required)

**Results:**
- Risk score (Low/Medium/High/Critical)
- Confidence percentage
- Blast radius breakdown
- Mitigations list

---

### 3. 📊 Monitoring

**What it does:** Track system health, latency, accuracy

**APIs called:**
```
GET /api/v1/monitoring/metrics             (latency, error trends)
GET /api/v1/monitoring/accuracy?days=7    (prediction accuracy)
GET /api/v1/monitoring/performance        (latency by endpoint)
GET /api/v1/insights/improvement-recommendations  (AI recommendations)
GET /api/v1/insights/false-positives?days=30
GET /api/v1/insights/false-negatives?days=30
```

**Authentication:** Viewer+

**Charts shown:**
- Latency over time (p50, p95, p99)
- Error rate trend
- Prediction accuracy
- False positive/negative rates
- Performance by endpoint

---

### 4. 🔀 PR Review

**What it does:** See recent changes with risk scores

**APIs called:**
```
GET /api/v1/changes/recent?limit=50      (list of recent changes)
GET /api/v1/graph/stats                  (stats sidebar)
GET /api/v1/insights/hotspots            (hotspots)
POST /api/v1/export/pdf                  (download report)
```

**Authentication:** Viewer+

**User flow:**
1. Click "PR Review" tab
2. Left panel shows list of recent changes
3. Click a change to see full analysis
4. Right panel shows details
5. Click "Export PDF" to download report

**Information shown:**
- PR title and description
- Repository
- Risk score
- Confidence
- Blast radius
- Mitigations
- Changes timeline

---

### 5. 📈 Health Insights

**What it does:** High-level system KPIs and hotspots

**APIs called:**
```
GET /api/v1/insights/hotspots          (high-risk services)
GET /api/v1/insights/centrality        (most connected services)
GET /api/v1/monitoring/metrics         (KPI data)
```

**Authentication:** Viewer+

**Cards shown:**
- System Health %
- Average Latency (ms)
- Error Rate %
- Prediction Accuracy %

**Lists shown:**
- Hotspots (high-risk services)
- Service Centrality (most connected)
- Latency distribution

---

### 6. ⚙️ Settings

**What it does:** Configure system, manage users, admin operations

**APIs called:**
```
GET /admin/users                    (list users)
POST /admin/rebuild-indexes         (rebuild Neo4j indexes)
POST /admin/clear-graph             (reset database)
GET /api/v1/ingest/webhook          (GitHub events)
```

**Authentication:** Admin only

**Tabs:**

**General:**
- API URL configuration
- Repository URL
- Risk threshold settings
- Local storage

**Integrations:**
- GitHub token (future)
- Slack integration (future)
- Custom webhook setup

**Users:**
- List of users
- Roles and permissions
- Create/edit users (future)

**Danger Zone:**
- Rebuild Neo4j indexes
- Clear entire graph
- Reset to defaults

---

## 🧩 API Endpoint Summary

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| **POST** | `/api/auth/token` | ❌ | Get JWT token |
| **GET** | `/api/auth/me` | ✅ | Get current user |
| **POST** | `/api/v1/simulate/change` | Analyst+ | Analyze diff |
| **POST** | `/api/v1/simulate/whatif` | Analyst+ | Scenario analysis |
| **GET** | `/api/v1/architecture/map` | Viewer+ | Get graph topology |
| **GET** | `/api/v1/graph/stats` | Viewer+ | Get node counts |
| **GET** | `/api/v1/monitoring/metrics` | Viewer+ | Get system metrics |
| **GET** | `/api/v1/monitoring/accuracy` | Viewer+ | Prediction accuracy |
| **GET** | `/api/v1/monitoring/performance` | Viewer+ | Latency by endpoint |
| **GET** | `/api/v1/insights/hotspots` | Viewer+ | High-risk services |
| **GET** | `/api/v1/insights/centrality` | Viewer+ | Most connected services |
| **GET** | `/api/v1/insights/false-positives` | Viewer+ | Mispredictions (high→low) |
| **GET** | `/api/v1/insights/false-negatives` | Viewer+ | Mispredictions (low→high) |
| **GET** | `/api/v1/insights/improvement-recommendations` | Analyst+ | AI suggestions |
| **GET** | `/api/v1/changes/recent` | Viewer+ | Recent changes |
| **POST** | `/api/v1/export/pdf` | Viewer+ | Export report |
| **POST** | `/api/v1/feedback/prediction` | Analyst+ | Submit feedback |
| **POST** | `/api/v1/ingest/webhook` | ❌ | GitHub webhook |
| **GET** | `/health` | ❌ | Backend health check |
| **GET** | `/metrics` | ❌ | Prometheus metrics |

---

## 🔐 Role Hierarchy

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Viewer** | Read all data | Business analysts, PMs |
| **Analyst** | Read + simulate + feedback | Engineers, SREs |
| **Admin** | All actions | System admins |

**Default Users:**
- Admin: `admin` / `changeme`
- Viewer: `viewer` / `viewonly`

---

## 🚀 VS Code Extension

**Status:** ✅ Fully integrated

### Features

1. **Auto-analyze on save**
   - Make changes, save → instant risk analysis
   - Status bar shows risk level
   - Decorations highlight affected lines

2. **Manual analysis**
   - Command Palette: "Aegis Twin: Run Simulation"
   - Same as auto-analyze

3. **View details**
   - Click status bar → sidebar panel opens
   - See risk score, confidence, mitigations

4. **Commands**
   - `aegis.runSimulation` — Run analysis
   - `aegis.openDashboard` — Open browser
   - `aegis.clearDecorations` — Clear highlights

### Setup

```bash
cd vscode-extension
# Press F5 in VS Code
# New window opens with extension loaded
# Edit a file and save to test
```

### Configuration

```json
{
  "aegisTwin.apiUrl": "http://localhost:8000",
  "aegisTwin.token": "",  // auto-filled from browser login
  "aegisTwin.autoAnalyzeOnSave": true
}
```

---

## 🔗 GitHub Integration

**Status:** ✅ Automatic PR checks working

### How It Works

1. **Push to repo with workflow file** (`.github/workflows/aegis-pr-check.yml`)
2. **Create/update PR**
3. **GitHub Actions triggered automatically**
4. **Gets PR diff**
5. **Calls Aegis API:** `POST /api/v1/simulate/change`
6. **Posts comment** on PR with risk analysis
7. **Blocks merge** if risk is Critical

### Workflow File

Located at `.github/workflows/aegis-pr-check.yml`

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  risk-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Aegis simulation
        env:
          AEGIS_API_URL: ${{ vars.AEGIS_API_URL }}
        run: |
          # Get diff, call API, post comment
```

### Configuration

Set repository variable (GitHub Settings → Secrets and variables → Variables):
```
AEGIS_API_URL = http://your-server:8000
```

---

## 📊 Data Flow Diagram

```
┌──────────────────────────────────────┐
│       Browser (React Frontend)       │
│  • Login Component                   │
│  • Dashboard (6 tabs)                │
│  • Charts, Forms, Navigation         │
└──────────────┬───────────────────────┘
               │
         Axios Interceptor
      (auto-inject JWT token)
               │
               ▼
┌──────────────────────────────────────┐
│     FastAPI Backend (8000)           │
│  • Auth endpoints                    │
│  • Simulation engine                 │
│  • Graph queries                     │
│  • Monitoring/metrics                │
└──────────────┬───────────────────────┘
               │
               ├─→ GET /api/v1/architecture/map
               ├─→ POST /api/v1/simulate/change
               ├─→ GET /api/v1/monitoring/metrics
               ├─→ GET /api/v1/insights/hotspots
               └─→ POST /api/v1/export/pdf
               │
               ▼
┌──────────────────────────────────────┐
│    Neo4j Database (7687)             │
│  • Infrastructure topology           │
│  • Change history                    │
│  • Risk assessments                  │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│   VS Code Extension                  │
│  • Editor decorations                │
│  • Status bar                        │
│  • Sidebar                           │
└──────────────┬───────────────────────┘
               │
         Axios Instance
         (Bearer token)
               │
               ▼
          FastAPI Backend
      /api/v1/simulate/change

┌──────────────────────────────────────┐
│   GitHub Actions                     │
│  • PR check workflow                 │
│  • Auto-comment                      │
│  • Merge blocking                    │
└──────────────┬───────────────────────┘
               │
         HTTP Request
       (no auth required)
               │
               ▼
          FastAPI Backend
      /api/v1/simulate/change
```

---

## 🧪 Testing the Integration

### 1. Test Login

```bash
# Get token
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}'

# Response should be:
{
  "access_token": "eyJhbGc...",
  "role": "admin",
  "expires_in": 3600
}
```

### 2. Test Protected Endpoint

```bash
# Without token (should fail)
curl http://localhost:8000/api/v1/graph/stats
# Response: 401 Unauthorized

# With token (should work)
TOKEN="<token-from-step-1>"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/graph/stats
# Response: {"success": true, "data": {...}}
```

### 3. Test Simulation

```bash
curl -X POST http://localhost:8000/api/v1/simulate/change \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "diff": "--- a/handler.py\n+++ b/handler.py\n@@ -1 @@\n-return None\n+db.query(SELECT * FROM users)\n+return response",
    "repo_url": "https://github.com/example/repo"
  }'
```

### 4. Test Frontend

```bash
# Open browser
open http://localhost:3000

# Login with: admin / changeme
# Click through tabs and verify they load data
```

### 5. Test VS Code Extension

```bash
cd vscode-extension
# Press F5
# Edit a file in a git repo
# Save file
# Status bar should show "Aegis: Analyzing..."
```

---

## 🐛 Common Issues & Solutions

### Login doesn't work
- Check credentials in `backend/.env`
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Clear browser cache and localStorage

### "Neo4j connection failed"
- Start Neo4j: `docker-compose up neo4j`
- Check port: 7687 (bolt) and 7474 (HTTP)
- Default credentials: neo4j / password

### API returns 401
- Token expired (60 min max)
- Log out and log back in
- Check localStorage for `aegis_token`

### Extension shows "API unreachable"
- Verify backend running on port 8000
- Check VS Code settings: `aegisTwin.apiUrl`
- Try disabling `autoAnalyzeOnSave` and use Command Palette instead

### Simulation takes 15+ seconds
- First time is slow (LLM initialization)
- Large diffs take longer
- Check backend logs for ANTHROPIC_API_KEY errors

---

## 📚 Documentation

- **HOW_TO_USE.md** — Complete user guide (this file has quick reference)
- **SETUP.md** — Setup and startup guide
- **API.md** — API endpoint documentation
- **PRODUCTION_READINESS.md** — Production hardening checklist
- **WHATS_NEXT.md** — Future phases and roadmap

---

## ✨ Summary

**All backend APIs are fully integrated with the frontend through:**

1. **Authentication:** JWT tokens managed in localStorage
2. **Axios Interceptor:** Auto-attaches tokens to all requests
3. **Login Screen:** Secure authentication before accessing dashboard
4. **Component Integration:** All tabs call their respective APIs
5. **Error Handling:** 401 errors redirect to login
6. **VS Code Extension:** Uses same authentication system
7. **GitHub Actions:** Webhook-based without client auth

**Ready for production testing!** 🚀
