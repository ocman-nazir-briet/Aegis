# Aegis Twin - Platform Usage Guide

Aegis Twin is an AI-Native Predictive Digital Twin for Software Architectures. It combines graph analysis, LLM simulation, and continuous monitoring to provide risk insights for code changes and infrastructure modifications.

## Quick Start

### Prerequisites
- Python 3.13+ with pip
- Node.js 16+ with npm
- Neo4j database running locally (port 7687)
- Backend running on port 8000
- Frontend running on port 3000

### Starting the System

**Terminal 1 - Backend:**
```bash
cd /Users/blackghost/Desktop/Aegis/backend
source venv/bin/activate
python main.py
```
Backend will be available at `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd /Users/blackghost/Desktop/Aegis/frontend
npm run dev
```
Frontend will be available at `http://localhost:3000`

**Terminal 3 - Neo4j (if not running):**
```bash
# Via Docker
docker run --name neo4j -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

## Authentication

### Logging In

1. Navigate to `http://localhost:3000`
2. Enter credentials:
   - **Admin**: username=`admin`, password=`changeme`
   - **Viewer**: username=`viewer`, password=`viewonly`
3. Click "Sign In"

The system uses JWT tokens stored in browser localStorage. Tokens expire after 60 minutes.

### User Roles

- **Admin**: Full access - can simulate, ingest, provide feedback, monitor, and access admin features
- **Analyst**: Can simulate, provide feedback, monitor, and read data (no admin/ingest)
- **Viewer**: Read-only access to dashboards

## Main Dashboard Features

### 1. Architecture Explorer (🏗️)
**What it does:** Visualizes your entire system architecture as an interactive graph

**How to use:**
- View all services, functions, endpoints, and their relationships
- Click on nodes to select and view details in the right sidebar
- Drag nodes to reorganize the visualization
- Use the zoom controls to focus on specific areas
- The sidebar shows:
  - Total nodes count
  - Service count
  - Function count
  - Endpoint count
  - Database connections

**Data sources:** Comes from repository ingestion and Neo4j knowledge graph

---

### 2. Simulation Studio (🧪)
**What it does:** Analyze impact of proposed code changes using AI-powered risk assessment

**How to use:**
1. Paste your git diff (from `git diff` command)
2. Enter the repository URL
3. (Optional) Add context about the change
4. Click "Simulate Change"
5. View results:
   - **Risk Score**: Low, Medium, High, Critical
   - **Confidence**: How confident the model is (0-100%)
   - **Blast Radius**: Which services/endpoints/databases are affected
   - **Explanation**: Why this risk was identified
   - **Mitigations**: Suggested actions to reduce risk
   - **Predicted Impact**: Expected changes to system metrics

**Example diff to simulate:**
```bash
# Make a change in your repo
git diff > /tmp/change.diff

# Copy the contents into the Simulation Studio
```

---

### 3. Monitoring Dashboard (📊)
**What it does:** Real-time system health and performance metrics

**Displays:**
- API latency (P50, P99 percentiles)
- Error rate percentage
- Neo4j query performance
- LLM inference time
- Active simulations count
- Total/accurate predictions
- Model accuracy percentage
- Cache hit rate

**Usage:** Monitor system performance after deployments, identify bottlenecks, track model accuracy over time

---

### 4. PR Review (🔀)
**What it does:** Analyze pull request changes for risk before merge

**How to use:**
1. Push a branch to GitHub
2. Open a Pull Request
3. The GitHub Actions workflow automatically:
   - Extracts the diff
   - Calls Aegis Twin simulation API
   - Posts a risk analysis comment
   - Blocks merge if risk is Critical
4. View the risk summary directly in the PR comment

**GitHub integration requirements:**
- Set `AEGIS_API_URL` repository variable (e.g., `http://internal-api:8000`)
- Enable GitHub Actions in the repository

---

### 5. Health Insights (📈)
**What it does:** Service health metrics and architectural hotspots

**What you'll see:**
- **KPI Cards**: Key performance indicators at a glance
- **Latency Chart**: API response times over time
- **Hotspots**: Services with most dependencies (highest risk)
- **Centrality**: Most-connected services in your architecture

**Usage:**
- Identify services that are bottlenecks or single points of failure
- Understand service interdependencies
- Plan refactoring efforts to reduce coupling

---

### 6. Settings (⚙️)
**What it does:** Configure integrations and platform settings

**Sections:**

**General:**
- View API URL and documentation
- Check Neo4j connection status

**Integrations:**
- GitHub token (for PR integration and repo access)
- GitLab token (for GitLab repositories)
- Bitbucket token (for Bitbucket repositories)
- Anthropic API key (for LLM simulation)

**Users:**
- Add/remove user accounts (admin only)
- Manage roles and permissions

**Danger Zone:**
- Clear all cached data
- Reset database schema
- Purge simulation history

## API Reference

All APIs require authentication with JWT bearer token (except `/auth/token` and `/health`)

### Authentication Endpoints

**POST /auth/token**
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}'
```
Returns: `{access_token, token_type, role, expires_in}`

**GET /auth/me**
```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```
Returns: Current user identity and role

### Architecture Endpoints

**GET /api/v1/health**
System health check

**GET /api/v1/graph/stats**
Graph statistics: node counts, service/function/endpoint counts

**GET /api/v1/architecture/map?limit=500**
Complete architecture topology as React Flow JSON (nodes and edges)

**GET /api/v1/nodes/{node_id}**
Detailed information about a specific node

### Simulation Endpoints

**POST /api/v1/simulate/change**
```bash
curl -X POST http://localhost:8000/api/v1/simulate/change \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "diff": "...",
    "repo_url": "github.com/org/repo",
    "context": "Added new payment service"
  }'
```

**POST /api/v1/simulate/whatif**
Simulate hypothetical changes to a specific service

### Insights Endpoints

**GET /api/v1/insights/hotspots**
Services with highest risk (most dependencies, lowest health)

**GET /api/v1/insights/centrality**
Services ranked by network centrality (most connected)

### Monitoring Endpoints

**GET /api/v1/monitoring/metrics**
Current system metrics (latency, errors, accuracy)

**GET /api/v1/monitoring/accuracy?days=7**
Model accuracy report over time period

**GET /api/v1/monitoring/performance?hours=24**
Performance metrics by endpoint

## VS Code Extension (Phase 3)

The VS Code extension (coming soon) will bring Aegis analysis directly into your IDE:

**Features:**
- **Inline Decorations**: Risk indicators on changed lines
- **Sidebar Panel**: Risk report with mitigations
- **Status Bar**: Current analysis status
- **Commands**:
  - `Aegis: Run Simulation` - Analyze current file
  - `Aegis: Open Dashboard` - Open browser dashboard
  - `Aegis: Clear Risk Decorations` - Clear visual markers

**Configuration** (in VS Code settings):
```json
{
  "aegisTwin.apiUrl": "http://localhost:8000",
  "aegisTwin.repoUrl": "github.com/org/repo",
  "aegisTwin.autoAnalyzeOnSave": true
}
```

**Auto-Analysis**: Every time you save a file, Aegis automatically analyzes your changes and shows risk indicators.

## Common Workflows

### Workflow 1: Test Impact of a Code Change
1. Make code changes locally
2. Run: `git diff > change.diff`
3. Go to Simulation Studio
4. Paste the diff
5. Enter your repo URL
6. Click "Simulate"
7. Review risk score and mitigations

### Workflow 2: Set Up Automated PR Checks
1. Go to Settings → Integrations
2. Add GitHub token
3. Set repository variable `AEGIS_API_URL`
4. Push a branch and open PR
5. GitHub Actions automatically runs Aegis
6. Risk analysis appears as PR comment
7. Critical risks block merge

### Workflow 3: Monitor Architecture Health
1. Go to Health Insights tab
2. Review hotspots (risky services)
3. Check centrality (bottleneck services)
4. Plan refactoring to reduce dependencies
5. Track improvements over time in Monitoring

### Workflow 4: Respond to Production Issues
1. Go to Monitoring Dashboard
2. Check error rate and latency
3. Identify affected services
4. Go to Health Insights
5. Check centrality - is this service a bottleneck?
6. Review recent simulations
7. Plan remediation with lower risk

## Troubleshooting

### "Cannot reach backend"
- Check backend is running: `lsof -i :8000`
- Check .env file has correct `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- Verify Neo4j is running: `curl http://localhost:7687`

### "Incorrect username or password"
- Verify credentials in backend `.env` file
- Restart backend after changing credentials
- Ensure passwords don't exceed 72 characters (bcrypt limit)

### "Neo4j connection failed"
- Check Neo4j is running: `docker ps | grep neo4j`
- Check default password is correct (default: `neo4j/password`)
- Check ports: Neo4j uses 7687 (bolt), 7474 (http)

### "Blank architecture graph"
- Ingest a repository first (via API or Settings)
- Check that Services/Functions/Endpoints exist in Neo4j
- Try: `curl http://localhost:8000/api/v1/graph/stats`

### "Simulation always shows 0 confidence"
- Set `ANTHROPIC_API_KEY` in `.env` file
- Verify key is valid (try via Anthropic API directly)
- Check `ANTHROPIC_MODEL` setting (default: claude-haiku-4-5-20251001)

## Performance & Limits

- **Max diff size**: 500 KB (configurable)
- **Simulation timeout**: 30 seconds
- **Ingestion timeout**: 300 seconds
- **Rate limit**: 60 simulations per minute per IP
- **Cache TTL**: Varies by data type (see Monitoring Dashboard)

## Next Steps

1. **Ingest your first repository**: Use Settings → Integrations to add GitHub/GitLab/Bitbucket tokens
2. **Simulate a change**: Go to Simulation Studio and test a code diff
3. **Set up PR checks**: Configure GitHub Actions workflow for automated risk analysis
4. **Install VS Code extension**: Get inline risk indicators while coding
5. **Monitor your services**: Track health, latency, and accuracy over time

## Support

- **Issues/Bugs**: Report via GitHub issues
- **API Docs**: Visit `http://localhost:8000/docs` for interactive API documentation
- **Logs**: Check backend logs in terminal running `python main.py`

---

**Current Status**: All core features working ✓
- Authentication & authorization ✓
- Architecture exploration ✓
- Change simulation ✓
- System monitoring ✓
- PR analysis ready ✓
- Health insights ✓
- Settings & integrations ✓
