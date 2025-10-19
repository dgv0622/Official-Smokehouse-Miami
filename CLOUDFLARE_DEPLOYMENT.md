# 🚀 Cloudflare Pages Deployment - Quick Reference

This project is **fully configured** for Cloudflare Pages deployment using npm and wrangler.

## ✅ What's Already Configured

- ✅ Root `package.json` with deployment scripts
- ✅ `wrangler.toml` configured for Cloudflare Pages
- ✅ `.node-version` file for Node.js version
- ✅ Vite build configured to output to `frontend/build`
- ✅ All dependencies properly organized

## 🚀 Deploy in 3 Commands

```bash
# 1. Install dependencies (includes wrangler)
npm install

# 2. Login to Cloudflare
npx wrangler login

# 3. Build and deploy
npm run deploy
```

That's it! Your site will be deployed to Cloudflare Pages.

## 📝 Available npm Scripts

| Command | Description |
|---------|-------------|
| `npm install` | Install all dependencies (frontend + wrangler) |
| `npm run dev` | Start local development server |
| `npm run build` | Build frontend for production |
| `npm run preview` | Preview production build with wrangler |
| `npm run deploy` | Build and deploy to Cloudflare Pages |

## 🔧 First Time Deployment

```bash
# From project root
npm install
npx wrangler login
npm run deploy
```

Wrangler will guide you through creating a new project or selecting an existing one.

## 📦 Project Structure

```
/
├── package.json              # Root config with deployment scripts
├── wrangler.toml            # Cloudflare Pages configuration
├── .node-version            # Node.js version (18.20.0)
├── frontend/
│   ├── package.json         # Frontend dependencies
│   ├── vite.config.ts       # Vite configuration
│   ├── build/               # Build output (deployed to CF Pages)
│   └── src/                 # React source code
└── backend/                 # Python backend (deploy separately)
```

## 🌐 Environment Variables

After deploying, configure in Cloudflare Pages dashboard:

**Settings → Environment Variables → Add Variable:**

| Variable | Value | Example |
|----------|-------|---------|
| `VITE_BACKEND_URL` | Your backend API URL | `https://your-api.railway.app` |

**Important:** 
- No trailing slash on URLs
- Apply to both Production and Preview environments
- Redeploy after adding variables

## 🔄 Continuous Deployment

### Option 1: Manual Deployment
```bash
npm run deploy
```

### Option 2: Git Integration (Recommended)
1. Push code to GitHub
2. In Cloudflare Pages dashboard:
   - Connect to Git repository
   - Build configuration:
     - **Build command:** `npm run build`
     - **Build output directory:** `frontend/build`
     - **Root directory:** `/` (project root)
     - **Node version:** 18.20.0 (from .node-version)
3. Automatic deployments on every push!

## 🛠️ Troubleshooting

### Build fails with "command not found"
Make sure you're running from the project root, not the frontend directory.

### Environment variables not working
- Check they're set in Cloudflare Pages dashboard
- Ensure they start with `VITE_` prefix
- Redeploy after adding variables

### "Project not found" error
Use the full command with project name:
```bash
npx wrangler pages deploy frontend/build --project-name=smokehouse-miami-bbq
```

## 📊 Build Information

- **Build Command:** `cd frontend && npm run build`
- **Output Directory:** `frontend/build`
- **Node Version:** 18.20.0
- **Package Manager:** npm
- **Build Tool:** Vite
- **Framework:** React + TypeScript

## 🔐 Backend Deployment

The Python FastAPI backend **cannot** run on Cloudflare Workers/Pages.

Deploy backend separately to:
- **Railway** (recommended) - See DEPLOY.md
- **Heroku** - Traditional platform
- **Render** - Free tier available

Then set `VITE_BACKEND_URL` in Cloudflare Pages to point to your backend.

## 📚 Additional Resources

- Full deployment guide: [DEPLOY.md](./DEPLOY.md)
- Project overview: [README.md](./README.md)
- Wrangler docs: https://developers.cloudflare.com/pages/
- Cloudflare Pages: https://pages.cloudflare.com/

## ✨ Features of This Setup

✅ **Simple** - One command deployment: `npm run deploy`  
✅ **Fast** - Vite builds in seconds  
✅ **Reliable** - Wrangler handles all Cloudflare communication  
✅ **Flexible** - Works with manual or Git-based deployments  
✅ **Clean** - Organized structure with root and frontend configs  
✅ **Modern** - Uses latest Node.js and Cloudflare Pages features  

---

**Ready to deploy?** Just run: `npm install && npm run deploy` 🚀
