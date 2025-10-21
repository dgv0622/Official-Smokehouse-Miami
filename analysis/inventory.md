# Inventory and Assumptions

- Backend framework: FastAPI detected
  - App init: `app = FastAPI()` (see `backend/server.py`)
  - Imports: `from fastapi import FastAPI, APIRouter, HTTPException`
- Existing chat-related endpoints (prefixed with `/api` via `APIRouter(prefix="/api")`):
  - `POST /api/chat/session`
  - `POST /api/chat/message` (sends to n8n via env-stored URL)
  - `GET /api/chat/messages/{session_id}`
  - `GET /api/chat/config` and `PUT /api/chat/config` (webhook URL managed in Mongo)
- Current n8n integration (existing):
  - Uses `N8N_WEBHOOK_URL` (single full URL), not the split `N8N_URL` + `N8N_WEBHOOK_PATH`
  - Optional API key handling via header or query param
- CORS (existing):
  - Uses `CORS_ORIGINS` env (default `*`) with `allow_methods=["*"]`, `allow_headers=["*"]`
- MongoDB (existing):
  - Uses `MONGO_URL` and `DB_NAME`
  - Client: `motor.motor_asyncio.AsyncIOMotorClient`
- Frontend:
  - Vite present (`frontend/vite.config.ts`)
  - Uses `import.meta.env.VITE_BACKEND_URL` in:
    - `frontend/src/components/ChatBot.tsx`
    - `frontend/src/pages/ChatConfig.tsx`
  - No absolute hardcoded production URLs found; defaults to `http://localhost:8000` if env var missing

Assumptions to apply in changes:
- Add top-level routes (no `/api` prefix): `GET /health`, `GET /chat/ping`, `POST /chat`
- Enforce envs: `N8N_URL`, `N8N_WEBHOOK_PATH`, `N8N_API_KEY`, `MONGO_URI`
- Keep existing `/api` endpoints for backward compatibility
- Implement robust CORS tuned for Cloudflare Pages
- Add request + error logging, upstream logging, and Mongo ping at startup
