# Local Setup Guide - Step by Step

This guide will walk you through installing and running the app **locally on your machine** (without Docker).

## Prerequisites

You need these installed on your computer:

1. **Python 3.11+** - [Download here](https://www.python.org/downloads/)
2. **Node.js 20+** - [Download here](https://nodejs.org/)
3. **Redis** - Choose one:
   - **Windows**: Download from [Redis for Windows](https://github.com/microsoftarchive/redis/releases) or use WSL
   - **Mac**: `brew install redis`
   - **Linux**: `sudo apt-get install redis-server` (Ubuntu/Debian)

## Step 1: Verify Prerequisites

Open your terminal and check:

```bash
# Check Python version (should be 3.11+)
python --version
# or
python3 --version

# Check Node.js version (should be 20+)
node --version

# Check npm (comes with Node.js)
npm --version

# Check Redis (should show "PONG")
redis-cli ping
```

## Step 2: Backend Setup

```bash
# Navigate to backend folder
cd backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file (copy from example)
# On Windows:
copy .env.example .env
# On Mac/Linux:
cp .env.example .env

# Edit .env file - at minimum, set:
# SECRET_KEY=your-secret-key-here (use a random string)
# DATABASE_URL=sqlite:///./chat_app.db
# REDIS_URL=redis://localhost:6379/0
```

## Step 3: Start Redis

Open a **new terminal window** and start Redis:

```bash
# Start Redis server
redis-server

# Keep this terminal open! Redis needs to keep running.
```

## Step 4: Start Backend Server

In your **original terminal** (with venv activated):

```bash
# Make sure you're in the backend folder
cd backend

# Start the FastAPI server
python -m uvicorn app.main:app --reload

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete.
```

**Keep this terminal open!** The server needs to keep running.

## Step 5: Seed Database (Optional but Recommended)

Open a **new terminal window**:

```bash
# Navigate to backend
cd backend

# Activate virtual environment again
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Run seed script to create demo data
python scripts/seed.py

# You should see:
# ✅ Database seeded successfully!
# Created 5 users
# Created 5 rooms
# ...
```

## Step 6: Frontend Setup

Open a **new terminal window**:

```bash
# Navigate to frontend folder
cd frontend

# Install Node.js dependencies (this may take a few minutes)
npm install

# Start the development server
npm run dev

# You should see:
# VITE v5.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
```

## Step 7: Access the Application

1. **Frontend**: Open your browser and go to `http://localhost:5173` (or the port shown)
2. **Backend API Docs**: Go to `http://localhost:8000/api/docs`

## Login Credentials (After Seeding)

- **Username**: `user1` (or user2, user3, user4, user5)
- **Password**: `password123`

## Troubleshooting

### "python: command not found"
- Use `python3` instead of `python` on Mac/Linux
- Make sure Python is installed and in your PATH

### "pip: command not found"
- Use `python -m pip` instead
- Or install pip: `python -m ensurepip --upgrade`

### "redis-server: command not found"
- Redis is not installed or not in PATH
- Install Redis (see Prerequisites)
- Or use Docker: `docker run -d -p 6379:6379 redis:7-alpine`

### "Port 8000 already in use"
- Another process is using port 8000
- Kill it: `lsof -ti:8000 | xargs kill` (Mac/Linux)
- Or change port in uvicorn command: `--port 8001`

### "Port 5173 already in use"
- Vite will automatically use the next available port
- Or change it in `vite.config.ts`

### Backend can't connect to Redis
- Make sure Redis is running: `redis-cli ping` should return `PONG`
- Check REDIS_URL in `.env` file

### Frontend can't connect to backend
- Make sure backend is running on port 8000
- Check browser console for errors
- Verify CORS settings in backend `.env`

## Quick Commands Reference

```bash
# Backend
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
npm install  # First time only
npm run dev

# Redis
redis-server  # Keep running in separate terminal

# Seed database
cd backend
python scripts/seed.py
```

## Stopping the Application

1. **Frontend**: Press `Ctrl+C` in the frontend terminal
2. **Backend**: Press `Ctrl+C` in the backend terminal
3. **Redis**: Press `Ctrl+C` in the Redis terminal (or `redis-cli shutdown`)

## Next Steps

- Read [README.md](README.md) for more details
- Check [QUICKSTART.md](QUICKSTART.md) for Docker setup (easier!)
- Explore the API at http://localhost:8000/api/docs



