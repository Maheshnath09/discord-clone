<div align="center">

# 💬 Discord-like Chat Application

A **production-ready**, **real-time** chat application inspired by Discord.  
Built with **FastAPI**, **React + TypeScript**, **WebSockets**, and **Redis**.

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [WebSocket Events](#-websocket-events)
- [Project Structure](#-project-structure)
- [Deployment](#-deployment)
- [Security](#-security)
- [Contributing](#-contributing)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **JWT Authentication** | Secure login with access & refresh tokens |
| 💬 **Real-time Messaging** | Instant message delivery via WebSockets |
| ⌨️ **Typing Indicators** | See when others are typing |
| 🟢 **Presence System** | Online/offline status tracking |
| 🏠 **Public & Private Rooms** | Create communities or invite-only spaces |
| 👤 **User Profiles** | Customizable profiles with avatars |
| 📱 **Responsive Design** | Works on desktop and mobile |
| 🔄 **Redis Pub/Sub** | Scalable across multiple server instances |
| 🐳 **Docker Ready** | One-command deployment |

---

## 🏗️ Architecture

### System Overview

```mermaid
flowchart TB
    subgraph Client["🖥️ Client Layer"]
        Browser["Browser / Mobile"]
        React["React + TypeScript"]
    end
    
    subgraph API["⚡ API Layer"]
        FastAPI["FastAPI Server"]
        WebSocket["WebSocket Handler"]
    end
    
    subgraph Data["💾 Data Layer"]
        SQLite["SQLite / PostgreSQL"]
        Redis["Redis Cache"]
    end
    
    Browser --> React
    React -->|HTTP REST| FastAPI
    React -->|WebSocket| WebSocket
    FastAPI --> SQLite
    FastAPI --> Redis
    WebSocket --> Redis
    
    style Client fill:#1a1a2e,stroke:#5865f2,color:#fff
    style API fill:#1a1a2e,stroke:#57F287,color:#fff
    style Data fill:#1a1a2e,stroke:#FEE75C,color:#fff
```

### Real-time Message Flow

```mermaid
sequenceDiagram
    participant User1 as 👤 User A
    participant WS1 as WebSocket
    participant API as FastAPI
    participant Redis as Redis Pub/Sub
    participant WS2 as WebSocket
    participant User2 as 👤 User B

    User1->>API: POST /messages (Send Message)
    API->>API: Save to Database
    API->>Redis: Publish to Room Channel
    Redis-->>WS1: Broadcast
    Redis-->>WS2: Broadcast
    WS1-->>User1: message.create event
    WS2-->>User2: message.create event
```

### Authentication Flow

```mermaid
flowchart LR
    subgraph Login
        A[User] -->|Credentials| B[/api/auth/login]
        B -->|Validate| C{Valid?}
        C -->|Yes| D[Generate JWT]
        C -->|No| E[401 Error]
        D --> F[Return Tokens]
    end
    
    subgraph Protected
        G[Request] -->|Bearer Token| H[Auth Middleware]
        H -->|Verify JWT| I{Valid?}
        I -->|Yes| J[Process Request]
        I -->|No| K[401 Unauthorized]
    end
    
    style A fill:#5865f2,stroke:#fff,color:#fff
    style F fill:#57F287,stroke:#fff,color:#fff
    style K fill:#ED4245,stroke:#fff,color:#fff
```

### Component Architecture

```mermaid
flowchart TB
    subgraph Frontend["React Frontend"]
        App["App.tsx"]
        Router["React Router"]
        
        subgraph Pages
            Login["LoginPage"]
            Register["RegisterPage"]
            Rooms["RoomsPage"]
            Room["RoomPage"]
            Profile["ProfilePage"]
        end
        
        subgraph Components
            Sidebar["Sidebar"]
            ChatWindow["ChatWindow"]
            MessageComposer["MessageComposer"]
            MemberList["MemberList"]
        end
        
        subgraph Services
            API["api.ts (Axios)"]
            WS["websocket.ts"]
        end
        
        subgraph Store
            AuthStore["authStore (Zustand)"]
        end
    end
    
    App --> Router
    Router --> Pages
    Pages --> Components
    Components --> Services
    Services --> Store
    
    style Frontend fill:#1a1a2e,stroke:#5865f2,color:#fff
```

```mermaid
flowchart TB
    subgraph Backend["FastAPI Backend"]
        Main["main.py"]
        
        subgraph APIRoutes["API Routes"]
            Auth["/auth"]
            Users["/users"]
            RoomsAPI["/rooms"]
            Messages["/messages"]
            WSRoute["/ws"]
        end
        
        subgraph Core
            Config["config.py"]
            Database["database.py"]
            Security["security.py"]
            RedisClient["redis_client.py"]
        end
        
        subgraph Models
            UserModel["User"]
            RoomModel["Room"]
            MessageModel["Message"]
            MemberModel["RoomMember"]
        end
        
        subgraph WebSockets
            Manager["ConnectionManager"]
            PubSub["Redis Pub/Sub"]
        end
    end
    
    Main --> APIRoutes
    APIRoutes --> Core
    APIRoutes --> Models
    WSRoute --> WebSockets
    WebSockets --> PubSub
    
    style Backend fill:#1a1a2e,stroke:#57F287,color:#fff
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async web framework |
| **SQLAlchemy** | Async ORM for database operations |
| **SQLite/PostgreSQL** | Relational database |
| **Redis** | Pub/Sub messaging & caching |
| **WebSockets** | Real-time bidirectional communication |
| **JWT (PyJWT)** | Token-based authentication |
| **Bcrypt** | Password hashing |
| **Pydantic** | Data validation |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18** | UI component library |
| **TypeScript** | Type-safe JavaScript |
| **Vite** | Fast build tool |
| **Tailwind CSS** | Utility-first styling |
| **Zustand** | Lightweight state management |
| **React Router** | Client-side routing |
| **Axios** | HTTP client |

---

## 🚀 Quick Start

### Prerequisites

- **Docker** (recommended) OR
- Python 3.11+ & Node.js 20+ & Redis

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/discord-clone.git
cd discord-clone

# Start all services
docker-compose up --build

# Access the app
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Option 2: Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Redis (new terminal)
redis-server
```

### Demo Accounts

| Username | Password |
|----------|----------|
| `testuser` | `password123` |
| `demouser` | `password123` |

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Create new account |
| `POST` | `/api/v1/auth/login` | Login & get tokens |
| `POST` | `/api/v1/auth/refresh` | Refresh access token |
| `POST` | `/api/v1/auth/logout` | Invalidate session |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/me` | Get current user |
| `PATCH` | `/api/v1/users/me` | Update profile |
| `POST` | `/api/v1/users/me/avatar` | Upload avatar |

### Rooms

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/rooms` | List all rooms |
| `POST` | `/api/v1/rooms` | Create room |
| `GET` | `/api/v1/rooms/{id}` | Get room details |
| `POST` | `/api/v1/rooms/{id}/join` | Join room |
| `POST` | `/api/v1/rooms/{id}/leave` | Leave room |
| `GET` | `/api/v1/rooms/{id}/members` | Get members |

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/rooms/{id}/messages` | Get messages |
| `POST` | `/api/v1/rooms/{id}/messages` | Send message |
| `PATCH` | `/api/v1/messages/{id}` | Edit message |
| `DELETE` | `/api/v1/messages/{id}` | Delete message |

---

## 🔌 WebSocket Events

### Connection

```
ws://localhost:8000/api/v1/ws/rooms/{room_id}?token={access_token}
```

### Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `message.create` | Server → Client | New message received |
| `message.update` | Server → Client | Message edited |
| `message.delete` | Server → Client | Message deleted |
| `typing.start` | Bidirectional | User started typing |
| `typing.stop` | Bidirectional | User stopped typing |
| `presence.update` | Server → Client | User online/offline |

### Event Payload Examples

```json
// message.create
{
  "type": "message.create",
  "data": {
    "id": 123,
    "content": "Hello!",
    "author": { "id": 1, "username": "user1" },
    "created_at": "2024-01-15T10:30:00Z"
  }
}

// typing.start
{
  "type": "typing.start",
  "data": { "user_id": 1, "username": "user1" }
}
```

---

## 📁 Project Structure

```
discord-clone/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # REST API routes
│   │   │   ├── auth.py       # Authentication endpoints
│   │   │   ├── users.py      # User management
│   │   │   ├── rooms.py      # Room operations
│   │   │   ├── messages.py   # Message CRUD
│   │   │   └── websockets.py # WebSocket handler
│   │   ├── core/             # Configuration & utilities
│   │   │   ├── config.py     # Environment settings
│   │   │   ├── database.py   # DB connection
│   │   │   ├── security.py   # JWT & password utils
│   │   │   └── redis_client.py
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── websockets/       # WebSocket manager
│   │   └── main.py           # App entry point
│   ├── scripts/              # Utility scripts
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── MessageComposer.tsx
│   │   │   └── MemberList.tsx
│   │   ├── pages/            # Route pages
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── RoomsPage.tsx
│   │   │   ├── RoomPage.tsx
│   │   │   └── ProfilePage.tsx
│   │   ├── services/         # API & WebSocket clients
│   │   ├── store/            # Zustand state
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Use **PostgreSQL** instead of SQLite
- [ ] Generate strong **SECRET_KEY**: `openssl rand -hex 32`
- [ ] Enable **HTTPS** via reverse proxy
- [ ] Configure **CORS** for your domain
- [ ] Use managed **Redis** (ElastiCache, Redis Cloud)
- [ ] Set up **file storage** (S3, Cloudflare R2)
- [ ] Enable **rate limiting**
- [ ] Configure **monitoring** (Sentry, Prometheus)

### Deploy to Render

1. Connect GitHub repository
2. Create **Backend** Web Service (Python)
3. Create **Frontend** Static Site
4. Add **PostgreSQL** and **Redis** add-ons
5. Set environment variables

### Environment Variables

```env
# Backend
SECRET_KEY=your-super-secret-key
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://redis-host:6379/0
FRONTEND_URL=https://your-frontend.com

# Frontend
VITE_API_URL=https://your-backend.com
VITE_WS_URL=your-backend.com
```

---

## 🔒 Security

| Feature | Status | Description |
|---------|--------|-------------|
| Password Hashing | ✅ | Bcrypt with salt |
| JWT Tokens | ✅ | Short-lived access tokens |
| Refresh Tokens | ✅ | HTTP-only cookies |
| Input Validation | ✅ | Pydantic schemas |
| CORS | ✅ | Configurable origins |
| Rate Limiting | ✅ | SlowAPI middleware |
| SQL Injection | ✅ | SQLAlchemy ORM |
| XSS Protection | ⚠️ | Basic (needs sanitization) |
| CSRF Protection | ⚠️ | Needed for forms |

---

## 🤝 Contributing

1. **Fork** the repository
2. Create a **feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. Open a **Pull Request**

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [Your Name]**

⭐ Star this repo if you find it useful!

</div>
