# Aegis Twin — Quick Start Guide

**⏱️ Time to working system: 5 minutes**

---

## Step 1: Start the Services

### Terminal 1 — Backend
```bash
cd backend
./start-backend.sh
# Wait for "INFO: Uvicorn running on http://0.0.0.0:8000"
```

### Terminal 2 — Frontend
```bash
cd frontend
./start-frontend.sh
# Wait for "VITE... ready in Xms"
```

### Terminal 3 — Neo4j (optional but recommended)
```bash
docker-compose up neo4j
# Or: ./start-neo4j.sh
```

---

## Step 2: Open Browser
```bash
open http://localhost:3000
```

You'll see the Aegis Twin login screen.

---

## Step 3: Login
```
Username: admin
Password: changeme
```

Click "Sign In"

---

## Step 4: Use the Dashboard

You now have access to 6 main features:

### 🏗️ Architecture Explorer
- View your system as an interactive graph
- See nodes (services, functions, endpoints, databases)
- Click nodes to see details
- Color-coded by risk (green/yellow/red)

### 🧪 Simulation Studio
- Analyze proposed code changes for risk
- Two modes:
  - **Diff-based:** Paste `git diff` output
  - **What-if:** Describe a hypothetical change
- Get: risk score, confidence, blast radius, mitigations

### 📊 Monitoring
- Latency trends (p50, p95, p99)
- Error rates
- Prediction accuracy
- Performance by endpoint
- AI recommendations

### 🔀 PR Review
- See recent changes with risk scores
- Click to view full analysis
- Export reports as PDF

### 📈 Health Insights
- Key system metrics (health %, latency, errors, accuracy)
- High-risk services (hotspots)
- Most-connected services (centrality)
- Latency distribution

### ⚙️ Settings
- Configure system (Admin only)
- Manage integrations
- List users and roles
- Database operations

---

## Step 5: Test Features

### Try Simulation
1. Click "Simulation Studio" tab
2. Fill in:
   - **Repository URL:** `https://github.com/yourorg/yourrepo`
   - **Git Diff:** Paste output of `git diff origin/main...HEAD`
3. Click "Run Simulation"
4. See risk assessment results

### Try VS Code Extension
```bash
cd vscode-extension
# Press F5 in VS Code to start Extension Development Host
# Edit a file and save it → status bar shows risk level
```

### Try GitHub Integration
1. Push repo with `.github/workflows/aegis-pr-check.yml`
2. Create a PR
3. GitHub Actions runs automatically
4. Comment appears on PR with risk analysis

---

## Default Credentials

| User | Username | Password | Access |
|------|----------|----------|--------|
| Admin | `admin` | `changeme` | All features |
| Viewer | `viewer` | `viewonly` | Read-only |

---

## Troubleshooting

### "Connection refused" when opening http://localhost:3000
- Frontend not running. Check Terminal 2.

### "Backend API error" in dashboard
- Backend not running. Check Terminal 1.

### "Neo4j connection failed"
- Start Neo4j: `docker-compose up neo4j` in Terminal 3

### Login shows "Incorrect password"
- Check default credentials above
- Or verify `backend/.env` for custom creds

---

## Complete Documentation

- **[HOW_TO_USE.md](HOW_TO_USE.md)** — Full user guide for every feature
- **[PLATFORM_INTEGRATION_SUMMARY.md](PLATFORM_INTEGRATION_SUMMARY.md)** — Technical integration details
- **[SETUP.md](SETUP.md)** — Installation & configuration
- **[STATUS_REPORT.md](STATUS_REPORT.md)** — Project status overview
- **[WHATS_NEXT.md](WHATS_NEXT.md)** — Future roadmap

---

## Key Info

| Component | URL | Credentials |
|-----------|-----|-------------|
| **Frontend** | http://localhost:3000 | admin / changeme |
| **Backend API** | http://localhost:8000 | JWT token (auto-obtained at login) |
| **Neo4j** | http://localhost:7474 | neo4j / password |

---

## Next: Deep Dive

After testing the basics, read **[HOW_TO_USE.md](HOW_TO_USE.md)** for:
- Detailed feature documentation
- VS Code extension guide
- GitHub integration setup
- Troubleshooting guide
- Advanced features

---

**Ready? Start with Terminal 1!** 🚀
