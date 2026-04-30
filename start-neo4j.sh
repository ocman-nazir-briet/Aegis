#!/bin/bash
# Start Neo4j using Docker Compose

set -e

echo "🚀 Neo4j — Starting..."

# Check docker-compose
command -v docker-compose >/dev/null || { echo "❌ Docker Compose not found"; exit 1; }

docker-compose up neo4j

echo ""
echo "✓ Neo4j started!"
echo "  Browser: http://localhost:7474"
echo "  Credentials: neo4j/password"
echo ""
echo "To stop: press Ctrl+C"
