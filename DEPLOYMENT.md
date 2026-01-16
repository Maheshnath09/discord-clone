# Deployment Guide: Vercel + Render + Neon + Upstash

This guide walks you through deploying the Discord-like Chat App using **free tiers** of multiple platforms.

## Overview

| Component | Platform | URL |
|-----------|----------|-----|
| Frontend | Vercel | https://vercel.com |
| Backend | Render | https://render.com |
| PostgreSQL | Neon | https://neon.tech |
| Redis | Upstash | https://upstash.com |

---

## Step 1: Set Up Neon PostgreSQL (Free)

1. Go to [neon.tech](https://neon.tech) and sign up
2. Create a new project (e.g., `discord-clone`)
3. Copy your connection string:
   ```
   postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. **Important**: For SQLAlchemy async, change the URL format to:
   ```
   postgresql+asyncpg://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?ssl=require
   ```

---

## Step 2: Set Up Upstash Redis (Free)

1. Go to [upstash.com](https://upstash.com) and sign up
2. Create a new Redis database
3. Choose a region close to your Render backend
4. Copy the connection string:
   ```
   rediss://default:xxx@xxx.upstash.io:6379
   ```

---

## Step 3: Deploy Backend to Render

1. Go to [render.com](https://render.com) and sign up
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `discord-clone-api`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. Add Environment Variables:
   ```
   SECRET_KEY=<generate a random 32-char string>
   DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/neondb?ssl=require
   REDIS_URL=rediss://default:xxx@xxx.upstash.io:6379
   FRONTEND_URL=https://your-app.vercel.app
   ALLOWED_ORIGINS=https://your-app.vercel.app
   AUTO_SEED_DEMO_DATA=true
   ```

6. Click **Create Web Service**

7. Note your backend URL (e.g., `https://discord-clone-api.onrender.com`)

---

## Step 4: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and sign up
2. Click **Add New** → **Project**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. Add Environment Variables:
   ```
   VITE_API_URL=https://discord-clone-api.onrender.com
   VITE_WS_URL=discord-clone-api.onrender.com
   ```

6. Click **Deploy**

---

## Step 5: Update Render with Vercel URL

1. Go back to Render Dashboard
2. Navigate to your Web Service → Environment
3. Update:
   ```
   FRONTEND_URL=https://your-app.vercel.app
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```
4. Save and redeploy

---

## Verification

1. Visit your Vercel URL
2. Try registering a new account
3. Create a room and send messages
4. Open in two browsers to test real-time messaging

---

## Troubleshooting

### Backend Cold Starts
Render free tier sleeps after 15 minutes of inactivity. First request after sleep takes ~30-60 seconds.

### WebSocket Connection Issues
Ensure `VITE_WS_URL` doesn't include `https://` - just the domain: `discord-clone-api.onrender.com`

### CORS Errors
Make sure `ALLOWED_ORIGINS` in Render matches your exact Vercel URL (with `https://`)

### Database Connection Errors
Ensure you're using `postgresql+asyncpg://` prefix and `?ssl=require` suffix for Neon

---

## Cost Summary

| Service | Free Tier Limits |
|---------|------------------|
| Vercel | Unlimited static hosting |
| Render | 750 hours/month, sleeps after 15 min |
| Neon | 3GB storage, unlimited compute hours |
| Upstash | 10,000 commands/day |

**Total Monthly Cost: $0** 🎉
