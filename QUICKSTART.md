# Quick Start Guide

Get the Discord-like Chat App running in 5 minutes!

**📖 For detailed setup instructions:**
- **Docker Setup**: See [SETUP_DOCKER.md](SETUP_DOCKER.md)
- **Local Setup**: See [SETUP_LOCAL.md](SETUP_LOCAL.md)

## Option 1: Docker (Recommended - Easiest!)

```bash
# Clone the repository
git clone <repository-url>
cd Discord-chat-app

# Start all services
docker-compose up --build

# Seed the database (in another terminal)
docker-compose exec backend python scripts/seed.py

# Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/docs
```

**Login credentials (after seeding):**
- Username: `user1` (or user2, user3, etc.)
- Password: `password123`

## Option 2: Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and edit .env
cp .env.example .env

# Start Redis (if not using Docker)
redis-server

# Run the server
python -m uvicorn app.main:app --reload

# Seed database (in another terminal)
python scripts/seed.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## First Steps

1. **Register a new account** or use seeded accounts (user1/password123)
2. **Browse rooms** on the home page
3. **Join a room** by clicking on it
4. **Start chatting!** Type a message and press Enter

## Troubleshooting

### Backend won't start
- Check if Redis is running: `redis-cli ping`
- Check if port 8000 is available
- Verify DATABASE_URL in .env

### Frontend won't connect
- Check if backend is running on port 8000
- Check browser console for errors
- Verify CORS_ORIGINS in backend .env includes frontend URL

### WebSocket connection fails
- Ensure Redis is running
- Check WebSocket URL in browser console
- Verify token is being sent correctly

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) if you want to contribute
- Explore the API docs at http://localhost:8000/api/docs

