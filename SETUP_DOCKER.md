# Docker Setup Guide - Easiest Way!

This is the **easiest way** to run the app - Docker handles everything for you!

## Prerequisites

1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
   - Make sure Docker Desktop is **running** before proceeding

## Step 1: Verify Docker

Open your terminal and check:

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Make sure Docker is running
docker ps
```

If any command fails, make sure Docker Desktop is installed and running.

## Step 2: Start Everything

```bash
# Make sure you're in the project root (Discord-chat-app folder)
cd Discord-chat-app

# Start all services (backend, frontend, Redis)
docker-compose up --build

# This will:
# - Build Docker images for backend and frontend
# - Start Redis
# - Start backend server
# - Start frontend server
# - Take a few minutes the first time
```

**First time will take longer** as it downloads images and installs dependencies.

## Step 3: Seed Database (Create Demo Data)

Open a **new terminal window**:

```bash
# Navigate to project root
cd Discord-chat-app

# Run seed script inside the backend container
docker-compose exec backend python scripts/seed.py

# You should see:
# ✅ Database seeded successfully!
# Created 5 users
# Created 5 rooms
# ...
```

## Step 4: Access the Application

1. **Frontend**: Open browser to `http://localhost:3000`
2. **Backend API Docs**: Go to `http://localhost:8000/api/docs`

## Login Credentials (After Seeding)

- **Username**: `user1` (or user2, user3, user4, user5)
- **Password**: `password123`

## Stopping the Application

Press `Ctrl+C` in the terminal where `docker-compose up` is running, then:

```bash
# Stop all containers
docker-compose down

# Or stop and remove volumes (deletes database)
docker-compose down -v
```

## Useful Docker Commands

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs
docker-compose logs backend  # Just backend logs
docker-compose logs frontend  # Just frontend logs

# Restart a service
docker-compose restart backend

# Rebuild after code changes
docker-compose up --build

# Stop everything
docker-compose down

# Clean everything (removes containers, images, volumes)
docker-compose down -v --rmi all
```

## Troubleshooting

### "docker-compose: command not found"
- Install Docker Desktop (includes docker-compose)
- Or use `docker compose` (without hyphen) on newer versions

### "Port already in use"
- Something else is using port 3000 or 8000
- Stop other services or change ports in `docker-compose.yml`

### "Cannot connect to Docker daemon"
- Make sure Docker Desktop is **running**
- Restart Docker Desktop

### Changes not reflecting
- Rebuild: `docker-compose up --build`
- Or restart: `docker-compose restart backend` or `docker-compose restart frontend`

### Database not persisting
- Check volumes in `docker-compose.yml`
- Don't use `docker-compose down -v` (that deletes volumes)

## Advantages of Docker

✅ No need to install Python, Node.js, or Redis locally  
✅ Same environment for everyone  
✅ Easy to start/stop everything  
✅ Isolated from your system  
✅ Easy to clean up  

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [SETUP_LOCAL.md](SETUP_LOCAL.md) if you prefer local setup
- Explore the API at http://localhost:8000/api/docs



