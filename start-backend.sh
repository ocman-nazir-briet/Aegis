#!/bin/bash
# Start only the Aegis Backend

set -e

echo "🚀 Aegis Backend — Starting..."

# Check Python
command -v python3 >/dev/null || { echo "❌ Python 3 not found"; exit 1; }

# Create virtualenv if needed
if [ ! -d backend/venv ]; then
  echo "Creating virtualenv..."
  python3 -m venv backend/venv
fi

# Activate and install
cd backend
source venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null || pip install -r requirements.txt

echo "Starting FastAPI server..."
python main.py
