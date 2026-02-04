#!/bin/bash

# RAG System Startup Script

echo "🚀 Starting RAG System..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start PostgreSQL
echo "📦 Starting PostgreSQL with pgvector..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
    exit 1
fi

# Verify database setup
echo "🔍 Verifying database setup..."
python test_setup.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application locally, run:"
echo "  source venv/bin/activate"
echo "  python -m app.main"
echo ""
echo "OR start the entire stack (API + DB) using Docker Compose:"
echo "  docker-compose up -d --build"
echo ""
echo "Then visit: http://localhost:8000/docs"
