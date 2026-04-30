# Aegis Twin — Complete User Guide

**Last Updated:** April 30, 2026  
**Version:** 1.0.0  
**Status:** ✅ Ready to Use

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Login & Authentication](#login--authentication)
3. [Using the Dashboard](#using-the-dashboard)
4. [Simulation Studio](#simulation-studio)
5. [Architecture Explorer](#architecture-explorer)
6. [Monitoring Dashboard](#monitoring-dashboard)
7. [PR Review](#pr-review)
8. [Health Insights](#health-insights)
9. [VS Code Extension](#vs-code-extension)
10. [GitHub Integration](#github-integration)
11. [Advanced Features](#advanced-features)
12. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Step 1: Start the Backend

```bash
cd backend
./start-backend.sh
# Or manually:
python main.py
```

**Expected output:**
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start the Frontend

In a **new terminal**:

```bash
cd frontend
./start-frontend.sh
# Or manually:
npm run dev
```

**Expected output:**
```
VITE v5.0.0  ready in 1234 ms

➜  Local:   http://localhost:3000/
```

### Step 3: Start Neo4j (Optional but Required for Full Features)

In a **third terminal**:

```bash
docker-compose up neo4j
# Or manually:
./start-neo4j.sh
```

**Expected output:**
```
neo4j_1  | 2024-04-30 12:34:56.789 INFO Server started at http://0.0.0.0:7474
```

### Step 4: Open in Browser

```bash
open http://localhost:3000
```

You should see the Aegis Twin login screen.

---

## Login & Authentication

### Default Credentials

**Admin User** (full access):
- Username: `admin`
- Password: `changeme`

**Viewer User** (read-only access):
- Username: `viewer`
- Password: `viewonly`

### Login Flow

1. **Open the app:** http://localhost:3000
2. **Enter username:** `admin` or `viewer`
3. **Enter password:** (see credentials above)
4. **Click "Sign In"**
5. **Dashboard appears**

### Token Storage

- JWT tokens are stored in browser localStorage (`aegis_token`)
- Tokens auto-attach to all API requests
- Tokens expire after 60 minutes (auto-refreshable)
- Logout clears token from localStorage

### Changing Your Password

⚠️ **Not yet implemented.** Credentials are currently set in environment:
- Backend: `backend/.env`
- Modify `ADMIN_PASSWORD` and `VIEWER_PASSWORD` to change credentials

---

## Using the Dashboard

### Navigation

The dashboard has **6 main tabs** at the top:

| Tab | Icon | Purpose | Requires Auth |
|-----|------|---------|---------------|
| Architecture Explorer | 🏗️ | View system topology graph | Viewer+ |
| Simulation Studio | 🧪 | Analyze proposed changes | Analyst+ |
| Monitoring | 📊 | View system health & trends | Viewer+ |
| PR Review | 🔀 | See recent changes & risks | Viewer+ |
| Health | 📈 | KPIs and hotspots | Viewer+ |
| Settings | ⚙️ | Configure system | Admin+ |

### Header

- **Left:** Aegis Twin logo and tagline
- **Right:** 
  - Current username
  - "Sign Out" button

### Sidebar (Architecture Tab Only)

Shows graph statistics:
- Total nodes
- Services count
- Functions count
- Endpoints count
- Databases count
- Total relationships

**Refresh button:** Re-fetches stats

---

## Simulation Studio

### Purpose

Analyze the risk and impact of proposed code changes before deployment.

### Two Modes

#### Mode 1: Diff-Based Analysis

Analyze an actual git diff:

1. **Click "Diff-based" tab** (default)
2. **Fill in:**
   - **Repository URL\*** — GitHub repo URL (required)
     - Example: `https://github.com/myorg/my-service`
   - **Git Diff\*** — Paste `git diff` output (required)
     - Example: Copy output of `git diff origin/main...HEAD`
   - **PR URL** — Link to GitHub PR (optional)
   - **Context** — Describe the change (optional)
3. **Click "Run Simulation"**
4. **See results on right panel:**
   - Risk score (Low/Medium/High/Critical)
   - Confidence percentage
   - Blast radius (affected services/endpoints/databases)
   - Mitigations list

**Time:** 2-15 seconds depending on LLM inference

#### Mode 2: What-If Scenario

Analyze hypothetical changes:

1. **Click "What-if Scenario" tab**
2. **Fill in:**
   - **Repository URL\*** — GitHub repo URL (required)
   - **Scenario Description\*** — Describe the "what if" (required)
     - Example: "What if we increase database timeout from 5s to 30s?"
   - **Target Service\*** — Primary service to analyze (required)
3. **Click "Run Simulation"**
4. **See risk assessment results**

### Interpreting Results

**Risk Score:**
- 🟢 **Low** — Safe to deploy, minimal blast radius
- 🟡 **Medium** — Review mitigations, manageable risk
- 🟠 **High** — Risky, needs careful monitoring
- 🔴 **Critical** — Very risky, recommend rollback plan

**Confidence:**
- Higher = more reliable prediction
- Based on graph size and training data

**Blast Radius:**
- Number of services affected
- Number of endpoints affected
- Number of databases affected

**Mitigations:**
- Recommended actions to reduce risk
- Ordered by importance

---

## Architecture Explorer

### Purpose

Visualize your system's architecture as an interactive graph.

### Graph Layout

**Nodes represent:**
- 🔵 **Services** — Microservices, servers, applications
- 🟢 **Functions** — Code functions, methods
- 🟠 **Endpoints** — API endpoints, HTTP routes
- 🔴 **Databases** — Databases, data stores
- 🟣 **Deployments** — Container/Pod definitions
- 🩷 **Queues** — Message brokers (Kafka, RabbitMQ, etc.)
- 🔵 **Classes** — Code classes, models

**Edges represent:**
- → Calls/dependencies between nodes
- Color/width indicates frequency

### Controls

**Mouse:**
- **Pan:** Click + drag empty space
- **Zoom:** Scroll wheel
- **Select node:** Click node
- **View node details:** Click node (panel appears on right)

**Buttons (top-left corner):**
- **+** — Zoom in
- **−** — Zoom out
- **⬜** — Fit to view
- **🗺️** — Toggle mini map (bottom-right)

### Sidebar (Right)

When a node is selected, shows:
- Node name
- Type
- Risk score (if available)
- Connected nodes
- Metrics (latency, throughput, etc.)

**Refresh button:** Re-fetches entire graph

### Risk Coloring

- 🟢 **Green** — Low risk (< 50%)
- 🟡 **Yellow** — Medium risk (50-75%)
- 🔴 **Red** — High/Critical risk (> 75%)

---

## Monitoring Dashboard

### Purpose

Track system health, latency, accuracy, and performance over time.

### Charts

**1. Latency Trends (Last 24h)**
- X-axis: Time
- Y-axis: Response time (ms)
- Shows: p50, p95, p99 percentiles
- Trend: Green (improving) vs Red (degrading)

**2. Error Rate**
- X-axis: Time
- Y-axis: Error percentage (%)
- Red = high error rate
- Green = low error rate

**3. Prediction Accuracy**
- X-axis: Time
- Y-axis: Accuracy percentage (%)
- Shows how well risk predictions match actual outcomes
- Green = improving, Red = degrading

**4. False Positives & Negatives**
- False Positives: Predicted high risk, actual was low
- False Negatives: Predicted low risk, actual was high
- Both are problematic

**5. Performance by Endpoint**
- Lists all API endpoints
- Shows latency, throughput, error rate per endpoint
- Sortable by metric

---

## PR Review

### Purpose

See recent changes analyzed by Aegis Twin.

### Layout

**Left Panel:**
- List of recent PRs/changes
- Sorted by newest first
- Shows:
  - PR title/description
  - Repository
  - Risk score (colored badge)
  - Confidence percentage
  - Blast radius count

**Right Panel:**
- Detailed view of selected change
- Full analysis:
  - Risk assessment
  - Affected services
  - Mitigations
  - Timeline

### Actions

- **Click PR:** View full details
- **Export PDF:** Download risk report as PDF
- **View on GitHub:** Open PR in GitHub
- **Copy link:** Share PR analysis link

---

## Health Insights

### Purpose

High-level system health summary with key metrics.

### Key Metrics

**KPI Cards (Top):**
- **System Health %** — Overall status
- **Avg Latency (ms)** — Average response time
- **Error Rate %** — Percentage of failed requests
- **Prediction Accuracy %** — Model confidence

**Hotspots (High-Risk Components):**
- List of services with highest risk
- Reason for risk
- Recommended actions

**Service Centrality (Most Connected):**
- Services with most connections
- Most impactful to overall system
- If these fail, many others are affected

**Latency Distribution:**
- Histogram of latency ranges
- Shows which latency buckets have most requests

---

## VS Code Extension

### Installation

1. **Open VS Code**
2. **Open `/vscode-extension` folder**
   ```bash
   code vscode-extension
   ```
3. **Press `F5`** to start Extension Development Host
4. **A new VS Code window opens with extension loaded**

### Configuration (Optional)

In VS Code settings (`Ctrl+,` or `Cmd+,`):

```json
{
  "aegisTwin.apiUrl": "http://localhost:8000",
  "aegisTwin.token": "",  // Leave blank if using login
  "aegisTwin.autoAnalyzeOnSave": true
}
```

### Usage

#### Auto-Analyze on Save

1. **Open any file in a git repository**
2. **Make changes**
3. **Save file** (`Ctrl+S` or `Cmd+S`)
4. **Status bar shows:** `Aegis: Analyzing...` with spinner
5. **Result appears:**
   - 🟢 **Green:** Low risk
   - 🟡 **Yellow:** Medium risk
   - 🟠 **Orange:** High risk
   - 🔴 **Red:** Critical risk

#### Manual Analysis

1. **Command Palette:** `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. **Type:** "Aegis Twin: Run Simulation"
3. **Press Enter**
4. **Same analysis as auto-analyze**

#### View Details

1. **Click status bar risk indicator**
2. **Sidebar panel opens** with:
   - Risk score
   - Confidence percentage
   - Blast radius
   - Mitigations list

#### Clear Decorations

1. **Command Palette:** `Ctrl+Shift+P`
2. **Type:** "Aegis Twin: Clear Risk Decorations"
3. **Press Enter**
4. **Highlights removed**

#### Open Dashboard

1. **Command Palette:** `Ctrl+Shift+P`
2. **Type:** "Aegis Twin: Open Aegis Dashboard"
3. **Press Enter**
4. **Browser opens** to http://localhost:3000

### What You See in the Editor

**Line Decorations:**
- 🟡 **Yellow left border** — Medium/High risk changes
- 🔴 **Red background** — Critical risk changes
- Hover to see mitigation hints

**Status Bar (bottom-right):**
- Shows current risk level
- Click to open sidebar details

**Problems Panel (bottom):**
- For critical changes only
- Lists mitigations
- Click to go to line

---

## GitHub Integration

### Automatic PR Checks

GitHub Actions workflow runs automatically on every PR.

### Setup

1. **Ensure workflow file exists:**
   ```
   .github/workflows/aegis-pr-check.yml
   ```

2. **Set repository variable** (GitHub Settings → Secrets and variables → Variables):
   ```
   AEGIS_API_URL = http://your-server:8000
   ```
   Or use default `http://localhost:8000` for local testing

3. **Create/update a PR**

### What Happens

1. **PR opened/updated**
2. **GitHub Actions triggered**
3. **Gets diff:** `git diff origin/main...HEAD`
4. **Calls Aegis API:** `/api/v1/simulate/change`
5. **Posts comment** on PR with results
6. **Blocks merge** if risk is Critical

### PR Comment

Shows:

```
## 🛡️ Aegis Twin — Risk Analysis

**Risk: 🟠 High** · Confidence: 92%

### Blast Radius
| Services | Endpoints | Databases |
|----------|-----------|-----------|
| 5 | 12 | 2 |

### Analysis
Changes to authentication service detected. 
Risk of breaking dependent services.

### Mitigations
1. Add comprehensive error handling for token validation
2. Implement gradual rollout via feature flag
3. Monitor auth latency spike (expected +50ms)
```

### Merge Blocking

If risk is **Critical**:
- PR cannot be merged
- Must dismiss/retry
- Or add to exception list

---

## Advanced Features

### Recording Actual Outcomes

After deploying a simulation, record actual impact:

1. **Go to Settings tab**
2. **Click "Integrations"**
3. **Submit Prediction Feedback:**
   - Simulation ID
   - Actual latency change (ms)
   - Actual error count
4. **Click "Submit"**
5. **Model learns from feedback**

### False Positive/Negative Analysis

View predictions that didn't match reality:

1. **Go to Monitoring tab**
2. **Scroll to "False Positives/Negatives"**
3. **Review misclassified predictions**
4. **View improvement recommendations**

### Custom Graph Seed

Populate the system with your architecture:

1. **Parse Kubernetes manifests:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/ingest/repo \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "repo_url": "https://github.com/yourorg/yourrepo",
       "include_patterns": ["k8s/**/*.yaml", "helm/**/*.yaml"]
     }'
   ```

2. **Or manually import via Settings:**
   - Go to Settings → Integrations
   - Paste infrastructure definitions
   - Click "Import"

---

## Troubleshooting

### Login Issues

**Problem:** "Incorrect username or password"

**Solution:**
1. Verify credentials in `backend/.env`
2. Check default:
   - Admin: `admin` / `changeme`
   - Viewer: `viewer` / `viewonly`
3. Restart backend if password changed

---

**Problem:** "Bearer token required" error

**Solution:**
1. Log out and log back in
2. Check browser localStorage (`F12` → Application → LocalStorage → aegis_token)
3. Clear cache and try again
4. Check token expiration (tokens last 60 minutes)

---

### Simulation Issues

**Problem:** "Neo4j connection failed"

**Solution:**
1. Verify Neo4j is running: `docker-compose ps`
2. Start if needed: `docker-compose up -d neo4j`
3. Check port: `neo4j://localhost:7687`
4. Verify credentials: `neo4j/password`

---

**Problem:** "Diff exceeds maximum size"

**Solution:**
- Diff larger than 500KB not allowed
- Break into smaller commits
- Or increase limit in `backend/app/config.py`: `max_diff_size`

---

**Problem:** "ANTHROPIC_API_KEY not set"

**Solution:**
1. LLM features disabled without API key
2. Set environment variable:
   ```bash
   export ANTHROPIC_API_KEY=sk-...
   ```
3. Restart backend
4. Or disable LLM: Set in code to return dummy response

---

### Extension Issues

**Problem:** "No git diff available" in VS Code

**Solution:**
1. Make sure file is in a git repository
2. Make unsaved edits (changes must exist)
3. Save file to trigger analysis
4. Check output panel for errors

---

**Problem:** Extension doesn't load in VS Code

**Solution:**
1. Make sure you're in `/vscode-extension` folder
2. Press `F5` to start Development Host
3. Check Debug Console for errors
4. Reinstall dependencies: `npm install`
5. Recompile: `npm run compile`

---

**Problem:** "API unreachable" from extension

**Solution:**
1. Verify backend running: `curl http://localhost:8000/api/v1/health`
2. Check extension config: `aegisTwin.apiUrl`
3. Ensure Cors headers allow extension origin
4. Try changing `autoAnalyzeOnSave` to false, then use command palette

---

### Performance Issues

**Problem:** Dashboard is slow to load

**Solution:**
1. Large graphs (1000+ nodes) are slow to render
2. Use Chrome DevTools (F12) to check Network tab
3. Check if Neo4j is the bottleneck: `docker stats neo4j`
4. Increase Neo4j memory: `docker-compose` environment variables

---

**Problem:** Simulation takes 15+ seconds

**Solution:**
1. First time is slow while LLM initializes
2. Subsequent runs are faster
3. Large diffs slow down analysis
4. Check Backend logs: `docker logs aegis-backend` or terminal

---

### GitHub Integration Issues

**Problem:** No comment appearing on PR

**Solution:**
1. Verify workflow file: `.github/workflows/aegis-pr-check.yml` exists
2. Check GitHub Actions tab for errors
3. Verify `AEGIS_API_URL` variable is set
4. Check backend is reachable from GitHub Actions runner
5. Look at action logs for detailed error

---

**Problem:** Merge blocked but should be allowed

**Solution:**
1. Risk score is Critical (red 🔴)
2. Two options:
   - Dismiss critical risk review (if you trust the change)
   - Or address mitigations and retry

---

## Getting Help

### Resources

- **API Docs:** [API.md](./API.md)
- **Setup Guide:** [SETUP.md](./SETUP.md)
- **Architecture:** [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)
- **Roadmap:** [WHATS_NEXT.md](./WHATS_NEXT.md)

### Common Commands

```bash
# Check if everything is running
curl http://localhost:8000/api/v1/health
curl http://localhost:3000

# Get auth token
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}'

# Run test simulation
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}' | jq -r '.access_token')

curl -X POST http://localhost:8000/api/v1/simulate/change \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "diff": "--- a/test.py\n+++ b/test.py\n@@ -1 @@\n-print(1)\n+print(2)",
    "repo_url": "https://github.com/example/repo"
  }'
```

---

## Feature Status

| Feature | Status | Notes |
|---------|--------|-------|
| Authentication | ✅ Working | JWT + RBAC |
| Simulation | ✅ Working | Requires ANTHROPIC_API_KEY for LLM |
| Architecture Graph | ✅ Working | Requires populated Neo4j |
| Monitoring | ✅ Working | Real-time once data populated |
| VS Code Extension | ✅ Working | Full feature set |
| GitHub Actions | ✅ Working | Auto-runs on PR |
| PDF Export | ✅ Working | Downloads as file |
| Metrics/Prometheus | ✅ Working | Available at `/metrics` |
| WebSocket (real-time) | ⏳ TODO | Planned for Phase 5E |
| Mobile UI | ⏳ TODO | Desktop-optimized only |
| Custom auth | ⏳ TODO | Current: hardcoded in .env |

---

**Need more help?** Check the logs or open an issue.
