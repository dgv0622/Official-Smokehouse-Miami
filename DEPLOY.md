# Cloudflare Deployment Guide

## Overview
This application uses a **hybrid deployment** strategy:
- **Frontend**: Cloudflare Pages (React/Vite static site)
- **Backend**: Railway, Heroku, or Render (FastAPI Python server)
- **Database**: MongoDB Atlas (free tier)

> **Note**: The Python FastAPI backend cannot run on Cloudflare Workers. It must be hosted on a traditional platform.

## Quick Start

### 1. Deploy Backend (Choose One Platform)

#### Option A: Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
cd backend
railway init
railway up
```

Set environment variables in Railway dashboard:
```
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/smokehouse
DB_NAME=smokehouse
CORS_ORIGINS=*
```

#### Option B: Heroku
```bash
heroku login
cd backend
heroku create smokehouse-miami-api
heroku config:set MONGO_URL="your-mongodb-url"
heroku config:set DB_NAME="smokehouse"
heroku config:set CORS_ORIGINS="*"
git init
git add .
git commit -m "Deploy backend"
heroku git:remote -a smokehouse-miami-api
git push heroku main
```

#### Option C: Render
1. Go to https://render.com
2. Create New → Web Service
3. Connect repository or upload `backend` folder
4. Configure:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in dashboard

**Save your backend URL** (e.g., `https://your-app.railway.app`)

### 2. Setup MongoDB Atlas (Free)

1. Create account at https://mongodb.com/cloud/atlas
2. Create FREE M0 cluster
3. Database Access → Add new user with password
4. Network Access → Add IP: `0.0.0.0/0` (allow all)
5. Get connection string from "Connect" button
6. Update your backend's `MONGO_URL` environment variable

### 3. Deploy Frontend to Cloudflare Pages

```bash
# From the root directory

# Install dependencies (includes wrangler)
npm install

# Login to Cloudflare
npx wrangler login

# Build and deploy in one command
npm run deploy

# Or deploy to a specific project name
npx wrangler pages deploy frontend/build --project-name=smokehouse-miami-bbq
```

**Save your frontend URL** (e.g., `https://smokehouse-miami-bbq.pages.dev`)

> **Note**: The root `package.json` now handles all build and deployment commands.

### 4. Connect Frontend to Backend

In Cloudflare Pages dashboard:
1. Go to your project → Settings → Environment Variables
2. Add variable:
   - **Name**: `VITE_BACKEND_URL`
   - **Value**: Your backend URL (e.g., `https://your-app.railway.app`)
   - **Note**: No trailing slash!
3. Apply to both Production and Preview environments
4. Redeploy your site

### 5. Update Backend CORS

Update your backend's `CORS_ORIGINS` environment variable:
```
CORS_ORIGINS=https://smokehouse-miami.pages.dev
```

If using a custom domain, add it (comma-separated):
```
CORS_ORIGINS=https://smokehouse-miami.pages.dev,https://yourdomain.com
```

## Testing Your Deployment

1. Visit your Cloudflare Pages URL
2. Test navigation and all pages
3. Test the quote calculator form
4. Test the chatbot (may show fallback message if n8n not configured)
5. Check browser console (F12) for any errors

## Troubleshooting

### CORS Errors
- Ensure `CORS_ORIGINS` in backend includes your frontend URL
- No trailing slashes in URLs

### API Calls Failing
- Verify `VITE_BACKEND_URL` is set correctly in Cloudflare Pages
- Check backend is running and accessible
- Inspect Network tab in browser DevTools

### Database Connection Issues
- Verify MongoDB Atlas IP whitelist allows all IPs (0.0.0.0/0)
- Check connection string has correct password
- Ensure database user has read/write permissions

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
# Create .env file with MONGO_URL and DB_NAME
uvicorn server:app --reload --port 8000
```

### Frontend
```bash
# From root directory
npm install  # Installs frontend dependencies automatically
npm run dev  # Starts Vite dev server on port 3000

# Or manually from frontend directory
cd frontend
npm run dev
```

> **Tip**: The root `package.json` includes convenience scripts:
> - `npm install` - Installs all frontend dependencies
> - `npm run dev` - Starts development server
> - `npm run build` - Builds for production
> - `npm run preview` - Preview production build locally
> - `npm run deploy` - Build and deploy to Cloudflare Pages

## Production Checklist

- [ ] Backend deployed and running
- [ ] MongoDB Atlas configured with proper access
- [ ] Frontend built and deployed to Cloudflare Pages
- [ ] `VITE_BACKEND_URL` set in Cloudflare Pages
- [ ] `CORS_ORIGINS` updated in backend with frontend URL
- [ ] All features tested in production
- [ ] SSL certificate active (automatic with Cloudflare)

## Custom Domain (Optional)

To add a custom domain:
1. In Cloudflare Pages → Custom domains
2. Add your domain
3. Update DNS records as instructed
4. Wait for SSL certificate (~15 minutes)
5. Update backend `CORS_ORIGINS` to include custom domain

## Deployment Files

- `package.json` - Root configuration with build and deployment scripts
- `wrangler.toml` - Cloudflare Pages configuration
- `.node-version` - Node.js version specification for Cloudflare Pages
- `backend/requirements.txt` - Python dependencies
- `backend/Procfile` - Heroku configuration
- `backend/railway.toml` - Railway configuration
- `frontend/package.json` - Frontend dependencies and scripts
- `frontend/.env.example` - Frontend environment variables template

## Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review backend logs in your hosting dashboard
3. Check browser console for frontend errors
4. Verify all environment variables are set correctly

## Architecture

```
┌─────────────────────┐
│  Cloudflare Pages   │  Frontend (React/Vite)
│  Static Hosting     │  
└──────────┬──────────┘
           │
           │ HTTPS API Calls
           │
┌──────────▼──────────┐
│   Railway/Heroku    │  Backend (FastAPI)
│   Python Server     │
└──────────┬──────────┘
           │
           │ MongoDB Protocol
           │
┌──────────▼──────────┐
│   MongoDB Atlas     │  Database
│   Cloud Database    │
└─────────────────────┘
```

## Estimated Deployment Time

- MongoDB Setup: 10 minutes
- Backend Deployment: 15 minutes
- Frontend Deployment: 10 minutes
- Configuration & Testing: 15 minutes

**Total: ~50 minutes**
