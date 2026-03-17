@echo off
REM Agentic CodeForge - Quick Start Script (Windows)

echo 🚀 Starting Agentic CodeForge...

REM Check if running from correct directory
if not exist "docker-compose.yml" (
    echo ❌ Please run this script from the project root directory
    exit /b 1
)

REM Check for .env file
if not exist ".env" (
    echo ⚠️  No .env file found. Creating from template...
    copy backend\.env.example .env
    echo 📝 Please edit .env with your API keys
)

if "%1"=="docker" goto docker
goto local

:docker
echo 🐳 Starting with Docker...
docker-compose up --build
goto end

:local
echo 💻 Starting locally...

REM Start backend
echo 🐍 Starting backend...
start "Backend" cmd /c "cd backend && python -m venv venv 2>nul && venv\Scripts\activate && pip install -r requirements.txt && uvicorn main:app --reload --port 8000"

REM Wait for backend to start
timeout /t 5 /nobreak

REM Start frontend
echo ⚛️  Starting frontend...
start "Frontend" cmd /c "cd frontend && npm install && npm run dev"

echo.
echo ✅ Agentic CodeForge is running!
echo.
echo 📊 Dashboard: http://localhost:3000
echo 🔌 API:       http://localhost:8000
echo 📚 API Docs:  http://localhost:8000/docs
echo.
echo Close the terminal windows to stop...

:end
