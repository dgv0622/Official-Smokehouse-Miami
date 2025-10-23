# 🚀 Quick Start - Cloudflare Pages Deployment

## Deploy Your Site in 3 Commands

```bash
# 1. Install dependencies (includes wrangler)
npm install

# 2. Login to Cloudflare
npx wrangler login

# 3. Build and deploy
npm run deploy
```

That's it! Your site is now live on Cloudflare Pages. 🎉

## 📝 What This Does

1. **npm install** - Installs:
   - Frontend dependencies (React, Vite, UI components)
   - Wrangler CLI (Cloudflare deployment tool)

2. **npx wrangler login** - Opens browser to authenticate with Cloudflare

3. **npm run deploy** - Automatically:
   - Builds React app with Vite
   - Deploys to Cloudflare Pages
   - Provides deployment URL

## 🔧 Configuration Needed After Deploy

### In Cloudflare Pages Dashboard

1. Go to: **Settings → Environment Variables**
2. Add this variable:
   - **Name:** `VITE_BACKEND_URL`
   - **Value:** Your backend API URL (e.g., `https://your-api.railway.app`)
3. Click **Save**
4. **Redeploy** your site

### Backend Deployment

Your Python backend needs to be deployed separately:
- **Railway** (recommended): Fast and easy
- **Heroku**: Reliable platform
- **Render**: Free tier available

See `DEPLOY.md` for backend deployment instructions.

## 📋 All Available Commands

```bash
npm install    # Install all dependencies
npm run dev    # Start development server
npm run build  # Build for production
npm run deploy # Build + Deploy to Cloudflare Pages
npm run preview # Preview build with wrangler
```

## 🎯 Project Structure

```
/
├── package.json        # Root config (deployment scripts)
├── wrangler.toml      # Cloudflare Pages config
├── .node-version      # Node.js version (18.20.0)
│
├── frontend/          # React application
│   ├── src/          # Source code
│   └── build/        # Production build (auto-generated)
│
└── backend/          # Python API (deploy separately)
```

## ✅ What's Already Done

- ✅ Root package.json configured
- ✅ Wrangler setup complete
- ✅ Build process optimized
- ✅ Vite configuration ready
- ✅ All dependencies specified
- ✅ Node version pinned

## 🌐 After Deployment

Your site will be available at:
```
https://smokehouse-miami-bbq.pages.dev
```

Or your custom domain if configured.

## 💡 Tips

### Custom Project Name
```bash
npm run build
npx wrangler pages deploy frontend/build --project-name=your-name-here
```

### View Deployments
```bash
npx wrangler pages deployment list
```

### Preview Build
```bash
npm run preview
```

## 🆘 Need Help?

- **Quick Reference:** `CLOUDFLARE_DEPLOYMENT.md`
- **Full Guide:** `DEPLOY.md`
- **Project Info:** `README.md`
- **Changes:** `DEPLOYMENT_SUMMARY.md`

## 🎉 You're All Set!

Your website is configured and ready to deploy. Just run:

```bash
npm install && npm run deploy
```

Happy deploying! 🚀
