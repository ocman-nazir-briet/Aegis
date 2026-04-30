#!/bin/bash
# Start all Aegis Twin services (Backend, Frontend, Neo4j)

set -e

echo "🚀 Aegis Twin — Starting all services..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check prerequisites
command -v python3 >/dev/null || { echo "❌ Python 3 not found"; exit 1; }
command -v node >/dev/null || { echo "❌ Node.js not found"; exit 1; }

# Start Neo4j (if docker-compose available)
if command -v docker-compose >/dev/null; then
  echo -e "${YELLOW}→ Starting Neo4j...${NC}"
  docker-compose up -d neo4j 2>/dev/null || true
  sleep 5
fi

# Create backend virtualenv if needed
if [ ! -d backend/venv ]; then
  echo -e "${YELLOW}→ Creating Python virtualenv...${NC}"
  python3 -m venv backend/venv
fi

# Start Backend
echo -e "${YELLOW}→ Starting Backend...${NC}"
(
  cd backend
  source venv/bin/activate
  pip install -q -r requirements.txt 2>/dev/null || pip install -r requirements.txt
  python main.py &
  BACKEND_PID=$!
  echo $BACKEND_PID > /tmp/aegis-backend.pid
)
sleep 3

# Start Frontend
echo -e "${YELLOW}→ Starting Frontend...${NC}"
(
  cd frontend
  npm install -q 2>/dev/null || npm install
  npm run dev &
  FRONTEND_PID=$!
  echo $FRONTEND_PID > /tmp/aegis-frontend.pid
)

echo ""
echo -e "${GREEN}✓ All services started!${NC}"
echo ""
echo "📍 Access points:"
echo "   Backend API:     http://localhost:8000"
echo "   Frontend UI:     http://localhost:3000"
echo "   Neo4j Browser:   http://localhost:7474 (neo4j/password)"
echo ""
echo "📝 API Health Check:"
echo "   curl http://localhost:8000/api/v1/health"
echo ""
echo "💡 To stop all services: press Ctrl+C"
echo ""

# Keep script running
wait
