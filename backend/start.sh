#!/bin/bash
# ─── TaxAI Backend Startup ────────────────────────────────────
set -e

echo "🚀 Starting TaxAI Backend..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi

# Create virtualenv if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# Copy .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  .env file created from template. Please fill in your API keys!"
    echo "   Edit backend/.env before continuing."
fi

# Start server
echo "✅ Starting FastAPI on http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
