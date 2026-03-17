#!/bin/bash
# Agentic CodeForge - Quick Start Script

echo "🚀 Starting Agentic CodeForge..."

# Check if running from correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp backend/.env.example .env
    echo "📝 Please edit .env with your API keys"
fi

# Function to run with Docker
run_docker() {
    echo "🐳 Starting with Docker..."
    docker-compose up --build
}

# Function to run locally
run_local() {
    echo "💻 Starting locally..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required"
        exit 1
    fi

    # Check Node
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is required"
        exit 1
    fi

    # Start backend
    echo "🐍 Starting backend..."
    cd backend
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    uvicorn main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..

    # Start frontend
    echo "⚛️  Starting frontend..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm run dev &
    FRONTEND_PID=$!
    cd ..

    echo ""
    echo "✅ Agentic CodeForge is running!"
    echo ""
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔌 API:       http://localhost:8000"
    echo "📚 API Docs:  http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop..."

    # Wait for interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
    wait
}

# Parse arguments
case "${1:-local}" in
    docker)
        run_docker
        ;;
    local)
        run_local
        ;;
    *)
        echo "Usage: ./run.sh [docker|local]"
        exit 1
        ;;
esac
