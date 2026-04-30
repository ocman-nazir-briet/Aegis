#!/bin/bash
# Start only the Aegis Frontend

set -e

echo "🚀 Aegis Frontend — Starting..."

# Check Node.js
command -v node >/dev/null || { echo "❌ Node.js not found"; exit 1; }

cd frontend

# Install dependencies
echo "Installing dependencies..."
npm install -q 2>/dev/null || npm install

# Start dev server
echo "Starting Vite dev server..."
npm run dev
