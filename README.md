# Smokehouse Miami BBQ

A modern, full-stack web application for a Miami-based BBQ catering business featuring an interactive quote calculator, AI chatbot, and beautiful UI.

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and optimized builds
- **Tailwind CSS** + **shadcn/ui** for modern, responsive design
- **React Router** for navigation
- **TanStack Query** for data fetching

### Backend
- **FastAPI** (Python) for RESTful API
- **Motor** for async MongoDB operations
- **Pydantic** for data validation
- **CORS** middleware for cross-origin requests

### Database
- **MongoDB** for flexible document storage

## Features

- 🏠 **Modern Landing Page** with hero section, gallery, and testimonials
- 📝 **Interactive Quote Calculator** for catering estimates
- 💬 **AI Chatbot** with n8n webhook integration
- 📦 **Package Showcase** for catering offerings
- 📱 **Fully Responsive** design for mobile and desktop
- 🎨 **Beautiful UI** with smooth animations and transitions

## Project Structure

```
.
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── pages/      # Page components
│   │   ├── hooks/      # Custom React hooks
│   │   └── lib/        # Utility functions
│   ├── public/         # Static assets
│   └── build/          # Production build output
│
├── backend/            # FastAPI backend server
│   ├── server.py       # Main application file
│   ├── requirements.txt # Python dependencies
│   ├── Procfile        # Heroku configuration
│   └── railway.toml    # Railway configuration
│
├── wrangler.toml       # Cloudflare Pages configuration
└── DEPLOY.md           # Deployment guide
```

## Local Development

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- MongoDB instance (local or Atlas)

### Quick Start

**Frontend Setup (from root directory)**
```bash
# Install all dependencies
npm install

# Build frontend for production
npm run build
```

**Backend Setup**
```bash
cd backend
pip install -r requirements.txt

# Create .env file with:
# MONGO_URL=your-mongodb-connection-string
# DB_NAME=smokehouse
# CORS_ORIGINS=https://your-frontend-url.pages.dev

# Start backend server
uvicorn server:app --reload --port 8000
```

### API Documentation
Once the backend is deployed, visit:
- Swagger UI: https://your-backend-url.com/docs
- ReDoc: https://your-backend-url.com/redoc

## Deployment

See [DEPLOY.md](./DEPLOY.md) for complete deployment instructions.

**Quick Summary:**
1. Deploy backend to Railway, Heroku, or Render
2. Setup MongoDB Atlas (free tier)
3. Deploy frontend to Cloudflare Pages:
   ```bash
   npm install
   npm run deploy
   ```
4. Configure environment variables in Cloudflare dashboard

**Key Features of This Setup:**
- ✅ Root `package.json` manages build and deployment
- ✅ Simple `npm run deploy` command for Cloudflare Pages
- ✅ Wrangler included as dev dependency
- ✅ Node version pinned with `.node-version` file
- ✅ Clean separation between frontend and deployment configs

## Environment Variables

### Frontend (`frontend/.env`)
```bash
VITE_BACKEND_URL=https://your-backend-url.com
```

### Backend (`backend/.env`)
```bash
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/smokehouse
DB_NAME=smokehouse
CORS_ORIGINS=https://your-frontend-url.pages.dev
```

## API Endpoints

### Status
- `GET /api/` - Health check
- `GET /api/status` - Get status checks
- `POST /api/status` - Create status check

### Chat
- `POST /api/chat/session` - Create chat session
- `POST /api/chat/message` - Send chat message
- `GET /api/chat/messages/{session_id}` - Get chat history
- `GET /api/chat/config` - Get n8n webhook config
- `PUT /api/chat/config` - Update n8n webhook config

## Scripts

### Root Level (npm)
- `npm install` - Install all dependencies (frontend + wrangler)
- `npm run dev` - Start Vite development server
- `npm run build` - Build frontend for production
- `npm run preview` - Preview production build locally with wrangler
- `npm run deploy` - Build and deploy to Cloudflare Pages
- `npm run cf-typegen` - Generate Cloudflare types

### Frontend Only
```bash
cd frontend
npm run dev     # Start Vite dev server
npm run build   # Build for production
npm run lint    # Run ESLint
```

### Backend
```bash
cd backend
uvicorn server:app --reload  # Start development server
pytest                        # Run tests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

This project is proprietary and confidential.

## Support

For deployment issues or questions, see [DEPLOY.md](./DEPLOY.md) or contact the development team.
