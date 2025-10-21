# Code Inventory and Analysis

## Detection Summary

**Date**: 2025-10-21  
**Repository**: /workspace  
**Branch**: cursor/troubleshoot-and-configure-chatbot-integration-3f4c

## Backend Analysis

### Framework Detection
- **Framework**: FastAPI
- **Location**: `/workspace/backend/server.py`
- **App Initialization**: `app = FastAPI()` (line 36)
- **Router**: Uses APIRouter with `/api` prefix (line 39)

### Current Architecture Issues

#### 1. Environment Variable Mismatches
The current code uses different environment variable names than required:

| Required | Current | Status |
|----------|---------|--------|
| `N8N_URL` | N/A | ❌ Missing |
| `N8N_WEBHOOK_PATH` | N/A | ❌ Missing |
| `N8N_WEBHOOK_URL` | ✓ Present | ⚠️ Should be split |
| `MONGO_URI` | `MONGO_URL` | ❌ Wrong name |
| `ALLOWED_ORIGINS` | `CORS_ORIGINS` | ⚠️ Different name |
| `N8N_API_KEY` | ✓ Present | ✅ Correct |

#### 2. Missing Routes
- ❌ `/health` - Health check endpoint not present
- ❌ `/chat/ping` - n8n connectivity test endpoint not present
- ⚠️ `/chat` - Currently at `/api/chat/message` (wrong path)

#### 3. Current Chat Endpoint Issues (`/api/chat/message`)
Located at lines 105-189:
- Uses database-stored webhook config (adds unnecessary complexity)
- Timeout is 30s instead of required 20s (line 130)
- Error responses don't include unique error codes (e.g., `ERR_N8N_502`)
- No request ID logging
- Generic error messages without status code passthrough
- URL construction is complex due to query param/header logic

#### 4. CORS Configuration
Located at lines 224-230:
- Uses `CORS_ORIGINS` env var (should be `ALLOWED_ORIGINS`)
- Defaults to `*` (should default to specific domains)
- Properly allows credentials ✅

#### 5. Logging Issues
- Logger defined at line 219 AFTER routes that use it (lines 102, 172-176)
- No structured request logging (method, path, request ID, session ID)
- Error logging is basic, doesn't include upstream status/body details
- No unique error fingerprints

#### 6. MongoDB Configuration
Located at lines 31-33:
- Uses `MONGO_URL` instead of `MONGO_URI`
- No startup connection validation
- No handling of special characters in password
- Server will crash on MongoDB connection failure

#### 7. n8n Integration Issues
- Current logic uses database-stored webhook URL (lines 122-123)
- Falls back to `N8N_WEBHOOK_URL` env var
- Complex URL construction for API key (lines 135-144)
- No clear separation between base URL and webhook path
- ⚠️ Risk of using `/webhook-test/` instead of production `/webhook/`

## Frontend Analysis

### Framework Detection
- **Framework**: Vite + React + TypeScript
- **Location**: `/workspace/frontend`
- **Config**: `vite.config.ts` confirms Vite setup

### Environment Variable Usage
✅ **Correctly uses** `import.meta.env.VITE_BACKEND_URL`:
- `ChatBot.tsx` line 21
- `ChatConfig.tsx` line 10

### API Endpoint Calls
Current endpoints being called:
- `POST /api/chat/session` - Create session (line 68)
- `POST /api/chat/message` - Send message (line 115)
- `GET /api/chat/messages/{session_id}` - Load messages (line 52)

**Issue**: These use `/api` prefix, but requirements specify `/chat` for the main endpoint.

## Required Changes Summary

### Backend Changes Needed

1. **Add Health & Ping Routes**
   - `GET /health` → Return git SHA, OK status
   - `GET /chat/ping` → Test n8n REST endpoint

2. **Refactor Chat Endpoint**
   - Move from `/api/chat/message` to `/chat`
   - Remove database webhook config dependency
   - Use `N8N_URL` + `N8N_WEBHOOK_PATH` pattern
   - Reduce timeout to 20s
   - Add unique error codes
   - Return upstream status/body on errors

3. **Fix Environment Variables**
   - Rename `MONGO_URL` → `MONGO_URI`
   - Use `ALLOWED_ORIGINS` instead of `CORS_ORIGINS`
   - Add `N8N_URL` and `N8N_WEBHOOK_PATH` (split from `N8N_WEBHOOK_URL`)

4. **Add Structured Logging**
   - Move logger definition before routes
   - Add request ID generation
   - Log: method, path, request ID, session ID, origin
   - Log upstream errors with status/body

5. **Add MongoDB Validation**
   - Startup ping test with 1s timeout
   - Log success/failure
   - Don't crash server if DB unavailable

6. **Update CORS**
   - Use specific allowed origins
   - Support `https://*.pages.dev` pattern

### Frontend Changes Needed

✅ **Frontend is already correct!**
- Uses `VITE_BACKEND_URL` properly
- No hardcoded URLs found

**Note**: Frontend calls `/api/chat/message` but this will continue to work as we'll keep the `/api` router and add a separate `/chat` endpoint for direct n8n integration.

## Dependencies

Current dependencies (`requirements.txt`):
- ✅ `fastapi==0.110.1` - Good
- ✅ `uvicorn==0.25.0` - Good
- ✅ `httpx>=0.27.0` - Good (async HTTP client)
- ✅ `motor==3.3.1` - Good (async MongoDB)
- ✅ `python-dotenv>=1.0.1` - Good

No additional dependencies needed.

## Deployment Configuration Files

- `backend/railway.toml` - Railway configuration
- `backend/Procfile` - Process definition
- `wrangler.toml` - Cloudflare Pages configuration

## Next Steps

1. Create new `/health` and `/chat/ping` routes
2. Create new `/chat` POST endpoint (separate from `/api/chat/message`)
3. Fix logger placement
4. Add MongoDB startup validation
5. Add structured logging middleware
6. Update CORS configuration
7. Create curl test file
8. Create manual steps file
