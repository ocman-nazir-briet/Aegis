#!/bin/bash

echo "🔍 Aegis Twin - Service Status Check"
echo "===================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    exit 1
fi

# Get container status
echo "📦 Docker Containers:"
docker-compose ps

echo ""
echo "🔗 Service Connectivity:"

# Check Neo4j
if docker-compose exec -T neo4j curl -s http://localhost:7474/browser > /dev/null 2>&1; then
    echo "✅ Neo4j (http://localhost:7474)"
else
    echo "❌ Neo4j (http://localhost:7474)"
fi

# Check Backend
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/api/v1/health | grep -o '"success":[^,}]*')
    echo "✅ Backend API (http://localhost:8000) - $HEALTH"
else
    echo "❌ Backend API (http://localhost:8000)"
fi

# Check Dashboard
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Dashboard (http://localhost:3000)"
else
    echo "⏳ Dashboard (http://localhost:3000) - not yet started"
fi

echo ""
echo "📊 Graph Statistics:"
if curl -s http://localhost:8000/api/v1/graph/stats 2>/dev/null | grep -q "total_nodes"; then
    STATS=$(curl -s http://localhost:8000/api/v1/graph/stats | python3 -m json.tool 2>/dev/null | grep -E '"total_nodes"|"services"|"functions"' || echo "unable to parse")
    echo "$STATS"
else
    echo "⏳ No data yet - load neo4j/schema.cypher"
fi
