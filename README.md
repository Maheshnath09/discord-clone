# Discord-like Chat Application

A production-ready, real-time chat application inspired by Discord. Built with FastAPI backend, React + TypeScript frontend, SQLite/PostgreSQL database, and Redis for real-time features.

## Features

- 🔐 **Authentication**: JWT-based auth with refresh tokens, secure password hashing
- 💬 **Real-time Messaging**: WebSocket-based real-time chat with typing indicators and presence
- 🏠 **Rooms**: Public and private rooms (channels) with member management
- 👤 **User Profiles**: Customizable profiles with avatar uploads
- 📱 **Responsive UI**: Modern, Discord-like interface with Tailwind CSS
- 🔄 **Redis Pub/Sub**: Scalable real-time messaging across multiple instances
- 🐳 **Dockerized**: Easy deployment with Docker and docker-compose
- ✅ **Tests**: Unit tests, integration tests, and E2E tests

## Tech Stack

### Backend
- FastAPI (Python 3.11+)
- SQLAlchemy (async) with SQLite/PostgreSQL
- Redis for pub/sub and presence
- WebSockets for real-time communication
- JWT authentication with refresh tokens

### Frontend
- React 18 + TypeScript
- Vite
- Tailwind CSS
- Zustand for state management
- React Router for navigation

## Quick Start

**Choose your setup method:**

1. **🐳 Docker (Easiest)** - See [SETUP_DOCKER.md](SETUP_DOCKER.md)
2. **💻 Local Setup** - See [SETUP_LOCAL.md](SETUP_LOCAL.md)

### Prerequisites

**For Docker (Recommended):**
- Docker Desktop installed and running

**For Local Development:**
- Python 3.11+
- Node.js 20+
- Redis installed and running

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Discord-chat-app
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Copy environment file
   cp .env.example .env
   # Edit .env with your settings
   
   # Run migrations (creates database)
   python -m uvicorn app.main:app --reload
   ```

3. **Seed Database** (optional)
   ```bash
   python scripts/seed.py
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Start Redis** (if not using Docker)
   ```bash
   redis-server
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs
   - Demo data: created automatically the first time you start the backend (configurable via `AUTO_SEED_DEMO_DATA`)

### Docker Development

1. **Start all services**
   ```bash
   docker-compose up --build
   ```

2. **Seed database** (in backend container)
   ```bash
   docker-compose exec backend python scripts/seed.py
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Environment Variables

See `backend/.env.example` for all available environment variables.

Key variables:
- `SECRET_KEY`: Secret key for JWT tokens (use a strong random string in production)
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `FRONTEND_URL`: Frontend URL for CORS

## Database Migration (SQLite to PostgreSQL)

1. **Update DATABASE_URL in .env**
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/chat_app
   ```

2. **Install PostgreSQL driver** (if not already installed)
   ```bash
   pip install psycopg[binary]
   ```

3. **Update database.py** to use asyncpg for PostgreSQL

4. **Run migrations** (Alembic setup needed - see future improvements)

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update profile
- `POST /api/v1/users/me/avatar` - Upload avatar
- `GET /api/v1/users/{id}` - Get public user profile

### Rooms
- `GET /api/v1/rooms` - List/discover rooms
- `POST /api/v1/rooms` - Create room
- `GET /api/v1/rooms/{id}` - Get room details
- `POST /api/v1/rooms/{id}/join` - Join room
- `POST /api/v1/rooms/{id}/leave` - Leave room
- `GET /api/v1/rooms/{id}/members` - Get room members

### Messages
- `GET /api/v1/rooms/{id}/messages` - Get messages (cursor-based pagination)
- `POST /api/v1/rooms/{id}/messages` - Send message
- `PATCH /api/v1/messages/{id}` - Edit message
- `DELETE /api/v1/messages/{id}` - Delete message
- `POST /api/v1/messages/{id}/reactions` - Add reaction
- `DELETE /api/v1/messages/{id}/reactions/{reaction_id}` - Remove reaction

### WebSocket
- `WS /api/v1/ws/rooms/{room_id}?token={access_token}` - Real-time messaging

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### E2E Tests
```bash
cd frontend
npx playwright test
```

## Deployment

### Production Considerations

1. **Use PostgreSQL** instead of SQLite
2. **Set strong SECRET_KEY** (generate with `openssl rand -hex 32`)
3. **Enable HTTPS** (use reverse proxy like Nginx)
4. **Configure CORS** properly for your domain
5. **Use managed Redis** (AWS ElastiCache, Redis Cloud, etc.)
6. **Set up file storage** (AWS S3, Cloudflare R2, etc.)
7. **Enable rate limiting** (already configured)
8. **Set up monitoring** (Sentry, Prometheus, etc.)

### Deployment Options

#### Render
1. Connect your GitHub repository
2. Set environment variables
3. Deploy backend and frontend as separate services
4. Use Render's PostgreSQL and Redis add-ons

#### DigitalOcean App Platform
1. Connect repository
2. Configure build commands
3. Set environment variables
4. Use managed databases

#### AWS (ECS/Fargate)
1. Build Docker images
2. Push to ECR
3. Deploy with ECS/Fargate
4. Use RDS for PostgreSQL and ElastiCache for Redis

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core config, database, security
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── websockets/   # WebSocket manager
│   │   └── main.py       # FastAPI app
│   ├── scripts/          # Utility scripts (seed, etc.)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API and WebSocket clients
│   │   ├── store/        # State management
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Future Improvements

- [ ] Full-text search for messages
- [ ] File attachments (images, documents)
- [ ] Message reactions with emoji picker
- [ ] Direct messages (1:1 chats)
- [ ] Voice/video calls (WebRTC)
- [ ] Advanced permissions and roles
- [ ] Message search and filters
- [ ] Notification system (in-app + push)
- [ ] OAuth integration (Google, GitHub)
- [ ] Message history retention policies
- [ ] Admin dashboard
- [ ] Audit logs UI
- [ ] Alembic migrations setup
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Performance optimizations (message virtualization)
- [ ] End-to-end encryption option

## Security Checklist

- ✅ Password hashing with bcrypt
- ✅ JWT tokens with expiration
- ✅ HTTP-only cookies for refresh tokens
- ✅ Input validation with Pydantic
- ✅ CORS configuration
- ✅ Rate limiting (configured)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ⚠️ File upload validation (basic - needs enhancement)
- ⚠️ XSS protection (needs sanitization for markdown)
- ⚠️ CSRF protection (needed for forms)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

