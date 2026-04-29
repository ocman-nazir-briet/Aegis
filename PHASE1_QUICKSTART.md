# Phase 1: Foundation - Quickstart Guide

## Overview

Phase 1 establishes the core infrastructure for Aegis Twin:
- **Neo4j Knowledge Graph**: Stores code entities, services, functions, endpoints, and relationships
- **FastAPI Backend**: Provides REST APIs for graph operations and analysis
- **React Dashboard**: Visualizes architecture topology and node relationships

## Project Structure

```
.
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── services/     # Business logic (Neo4j, ingestion)
│   │   ├── models.py     # Pydantic request/response models
│   │   ├── config.py     # Configuration management
│   │   └── ingestion/    # Repository parsing (future: Tree-Sitter)
│   ├── main.py           # FastAPI entry point
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile        # Container image
├── frontend/              # React + TypeScript dashboard
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── types/        # TypeScript types
│   │   ├── App.tsx       # Main app
│   │   └── main.tsx      # Entry point
│   ├── package.json
│   ├── vite.config.ts    # Vite build config
│   └── tailwind.config.js # Styling
├── neo4j/                 # Neo4j schema and initialization
│   └── schema.cypher     # Graph schema with sample data
└── docker-compose.yml    # Local development setup
```

## Prerequisites

- **Docker & Docker Compose** (recommended)
- OR **Python 3.11+**, **Node 18+**, **Neo4j 5.14** (manual setup)

## Quick Start with Docker

### 1. Set up environment
```bash
cp .env.example .env
# Edit .env with your configuration if needed
```

### 2. Start services
```bash
docker-compose up -d
```

This starts:
- **Neo4j** at `http://localhost:7474` (browser) and `bolt://localhost:7687`
- **FastAPI** at `http://localhost:8000` with docs at `/docs`

### 3. Load initial graph schema
```bash
# Option A: Via Neo4j Browser
# Open http://localhost:7474
# Log in: neo4j / password
# Paste contents of neo4j/schema.cypher
# Run each statement

# Option B: Via cypher-shell
docker-compose exec neo4j cypher-shell -u neo4j -p password < neo4j/schema.cypher
```

### 4. Start frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```

Dashboard available at `http://localhost:3000`

## Manual Setup (Without Docker)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start Neo4j separately first, then:
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints (Phase 1)

### Core Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | System health check |
| GET | `/api/v1/graph/stats` | Graph statistics (node counts, relationships) |
| GET | `/api/v1/architecture/map` | Full architecture graph as JSON |
| GET | `/api/v1/nodes/{node_id}` | Detailed information about a node |
| POST | `/api/v1/ingest/repo` | Queue repository for ingestion |
| POST | `/api/v1/simulate/change` | Analyze change impact (basic phase 1 version) |

### Example API Usage

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get graph stats
curl http://localhost:8000/api/v1/graph/stats

# Get architecture map
curl http://localhost:8000/api/v1/architecture/map?limit=500

# Get specific node
curl http://localhost:8000/api/v1/nodes/{node_id}

# Queue repository ingestion
curl -X POST http://localhost:8000/api/v1/ingest/repo \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/example/project", "branch": "main"}'
```

## Database Schema

### Node Types
- **Service**: Application/microservice
- **Function**: Code function/method
- **Endpoint**: API endpoint
- **Database**: Data source
- **Deployment**: Deployment metadata
- **ChangeEvent**: Analyzed code changes

### Relationships
- `Service-[:CONTAINS]->Function`
- `Service-[:EXPOSES]->Endpoint`
- `Function-[:CALLS]->Function`
- `Service-[:RELIANT_ON]->Service`
- `Service-[:DEPENDS_ON]->Database`

## Dashboard Features

### Architecture Explorer
- Browse all nodes in the graph
- View node details (properties, relationships)
- Filter by node type
- Graph statistics sidebar

### Node Details Panel
- Shows all properties of selected node
- Related nodes and relationships
- Health metrics (for services/endpoints)

## Testing

### Health Check
```bash
curl http://localhost:8000/api/v1/health
# Expected response:
# {"success": true, "data": {"status": "healthy", "neo4j": "connected", "timestamp": "..."}}
```

### Dashboard
1. Open http://localhost:3000
2. Should display architecture topology
3. Click any node to see details in right panel
4. Click "Refresh" to reload graph data

## Known Limitations (Phase 1)

- ⚠️ Repository ingestion queued but not fully implemented
- ⚠️ Change simulation returns placeholder data (LLM integration in Phase 2)
- ⚠️ No production security (auth/authorization in Phase 2)
- ⚠️ No telemetry ingestion (Phase 2 feature)
- ⚠️ Tree-Sitter parsing not yet integrated (basic regex parsing)
- ⚠️ IDE plugin not included (Phase 3)

## Next Steps (Phase 2)

1. **Telemetry Ingestion**: OpenTelemetry/Prometheus metrics mapping
2. **AI Simulation**: LLM-powered change impact analysis with GraphRAG
3. **Advanced Features**: Risk scoring, confidence estimation, mitigations
4. **PR Integration**: GitHub Actions integration for CI/CD

## Troubleshooting

### Neo4j connection fails
- Ensure Neo4j is running: `docker-compose ps`
- Check credentials in `.env`: `NEO4J_USER`, `NEO4J_PASSWORD`
- If using Docker, wait for health check: `docker-compose logs neo4j`

### Backend won't start
- Check port 8000 is free: `lsof -i :8000` (kill if needed)
- Verify Neo4j connection: `curl neo4j:7687` (should timeout, not refuse)
- Check Python version: `python --version` (needs 3.11+)

### Frontend build fails
- Clear cache: `npm cache clean --force`
- Reinstall: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (needs 18+)

## For Developers

### Code Standards
- Python: Follow PEP 8, use type hints
- TypeScript: Strict mode enabled, no `any` types
- API: RESTful with consistent error responses

### Making Changes
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes
3. Commit with descriptive messages
4. Test locally before committing
5. Push and create pull request

### Running Tests
```bash
cd backend
pytest  # Unit tests

cd ../frontend
npm run lint  # Type checking and linting
```

## Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Aegis Twin SRS](./srs.md)
- [Architecture Overview](./architecture.md)
