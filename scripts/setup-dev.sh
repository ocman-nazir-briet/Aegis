#!/bin/bash
set -e

echo "🚀 Aegis Twin - Phase 1 Development Setup"
echo "==========================================="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Setup environment
echo "📝 Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from .env.example"
else
    echo "✅ .env already exists"
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check Neo4j
echo "🔍 Checking Neo4j..."
if docker-compose exec -T neo4j curl -s http://localhost:7474/browser > /dev/null 2>&1; then
    echo "✅ Neo4j is running"
else
    echo "❌ Neo4j failed to start"
    docker-compose logs neo4j
    exit 1
fi

# Check Backend
echo "🔍 Checking Backend..."
if docker-compose exec -T backend curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✅ Backend API is running"
else
    echo "⚠️  Backend might still be initializing..."
fi

# Setup Frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install > /dev/null 2>&1
cd ..
echo "✅ Frontend dependencies installed"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Load Neo4j schema:"
echo "   docker-compose exec neo4j cypher-shell -u neo4j -p password < neo4j/schema.cypher"
echo ""
echo "2. Start frontend (in a new terminal):"
echo "   cd frontend && npm run dev"
echo ""
echo "3. Access services:"
echo "   - Dashboard: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - Neo4j Browser: http://localhost:7474"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "📖 For more info, see PHASE1_QUICKSTART.md"
