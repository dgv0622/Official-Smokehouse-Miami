# PR: Fix Chatbot Integration with n8n on Railway

## 🎯 Objective

Diagnose and fix the chatbot integration after moving n8n to a separate Railway project. This PR implements robust error handling, proper environment variable usage, comprehensive logging, and provides clear manual configuration steps.

---

## 📊 Summary of Changes

### Backend Changes (`backend/server.py`)

#### 1. **New Health & Connectivity Routes**

✅ **`GET /health`**
- Returns server status, version (git SHA), and timestamp
- Used for health checks and deployment verification

✅ **`GET /chat/ping`**
- Tests n8n connectivity via REST API
- Returns n8n ping response with status code
- Helps diagnose connection issues between backend and n8n

✅ **`POST /chat`**
- New production endpoint for direct chatbot integration
- Validates message payload (returns 400 if message missing/empty)
- Forwards requests to n8n webhook with proper error handling
- 20-second timeout (as specified)
- Returns structured error codes:
  - `INVALID_JSON` - Malformed request body
  - `MISSING_MESSAGE` - Empty or missing message field
  - `N8N_NOT_CONFIGURED` - Missing n8n environment variables
  - `UPSTREAM_N8N` - n8n returned error (includes status and body)
  - `N8N_TIMEOUT` - Request timed out after 20 seconds
  - `N8N_ERROR` - Unexpected error calling n8n

#### 2. **Environment Variable Updates**

| Old | New | Notes |
|-----|-----|-------|
| `N8N_WEBHOOK_URL` | `N8N_URL` + `N8N_WEBHOOK_PATH` | Separates base URL from webhook path |
| `MONGO_URL` | `MONGO_URI` | Standardized name (supports both for backward compatibility) |
| `CORS_ORIGINS` | `ALLOWED_ORIGINS` | Clearer naming |

**New structure**:
```python
N8N_URL = "https://n8n.up.railway.app"
N8N_WEBHOOK_PATH = "bbq-catering-chat"
# Constructs: https://n8n.up.railway.app/webhook/bbq-catering-chat
```

**Backward compatibility**: If `N8N_WEBHOOK_URL` is still set and new vars aren't, it will be used with a deprecation warning.

#### 3. **Robust CORS Configuration**

- Uses `ALLOWED_ORIGINS` env var with specific domains
- Default: `https://*.pages.dev,http://localhost:3000`
- Restricts methods to `GET, POST, OPTIONS` (more secure than `*`)
- Allows credentials for session-based auth

#### 4. **Structured Logging**

**Request logging middleware**:
- Generates unique request IDs for tracking
- Logs: method, path, origin, response status
- Format: `[req_id] METHOD /path origin=https://...`

**Error logging**:
- Logs upstream n8n errors with status code and response body (first 500 chars)
- Includes contextual information (session ID, message length)
- Uses consistent format for easy log parsing

**Logger placement fix**:
- Moved logger initialization to **before** routes (was previously after routes that used it)

#### 5. **MongoDB Connection Validation**

**Startup validation**:
- Attempts `ping` command with 1-second timeout
- Logs success (✅) or failure (⚠️) with clear emoji indicators
- **Does not crash** the server if MongoDB is unavailable
- Server continues to run (logs warning if DB operations fail)

**Environment variable handling**:
- Supports both `MONGO_URI` (new) and `MONGO_URL` (legacy)
- Documents need for URL encoding special characters in passwords
- Defaults `DB_NAME` to `bbq_catering` if not set

#### 6. **n8n Integration Improvements**

**URL construction**:
- Cleaner separation: `${N8N_URL}/webhook/${N8N_WEBHOOK_PATH}`
- Prevents accidental use of `/webhook-test/` paths
- Simplified API key handling (header-based)

**Error handling**:
- Returns upstream status codes and body snippets on errors
- Timeout reduced from 30s to 20s (as specified)
- Structured error responses for client-side handling

---

## 📁 New Files Created

### 1. `analysis/inventory.md`
- Complete codebase analysis
- Framework detection (FastAPI)
- Current issues identified
- Environment variable mismatches
- Required changes summary

### 2. `curl_test.md`
- 7 copy-pasteable curl test commands
- Expected responses for each test
- Troubleshooting matrix for common errors
- Production readiness checklist
- Logging and debugging tips

### 3. `MANUAL_STEPS.md`
- Step-by-step configuration guide
- Exact Railway environment variable setup (backend and n8n)
- Cloudflare Pages environment variable setup
- n8n workflow activation steps
- Verification steps with expected outputs
- Troubleshooting guide for 5+ common issues
- Final checklist

---

## 🔍 Key Fixes

### Issue 1: Missing Health Routes ✅
**Before**: No `/health` or `/chat/ping` endpoints  
**After**: Both endpoints implemented with proper error handling

### Issue 2: Inconsistent Environment Variables ✅
**Before**: Used `MONGO_URL`, `CORS_ORIGINS`, monolithic `N8N_WEBHOOK_URL`  
**After**: Standardized to `MONGO_URI`, `ALLOWED_ORIGINS`, split `N8N_URL` + `N8N_WEBHOOK_PATH`

### Issue 3: Logger Defined After Use ✅
**Before**: Logger defined at line 219, used in routes at lines 102, 172-176  
**After**: Logger defined at line 24, before all routes

### Issue 4: No Request Logging ✅
**Before**: Basic logging, no request IDs or context  
**After**: Middleware logs all requests with unique IDs, method, path, origin

### Issue 5: Generic Error Messages ✅
**Before**: Generic "error occurred" messages  
**After**: Structured error codes (`ERR_N8N_502`, etc.) with status and body passthrough

### Issue 6: MongoDB Crashes on Failure ✅
**Before**: Server would crash if MongoDB connection failed  
**After**: Server continues, logs warning, handles DB operations gracefully

### Issue 7: No Production Webhook Discipline ✅
**Before**: Could accidentally use `/webhook-test/` paths  
**After**: Clear separation of `N8N_WEBHOOK_PATH`, documented production URL format

### Issue 8: 30s Timeout ✅
**Before**: 30-second timeout on n8n requests  
**After**: 20-second timeout as specified

---

## 🧪 Testing

### Syntax Validation
```bash
✅ Syntax check passed
```

### Linter Check
```
✅ No linter errors found
```

### Manual Testing Steps

Follow `curl_test.md` for comprehensive testing:

1. **Backend health**: `curl https://<backend>/health`
2. **n8n ping**: `curl https://<backend>/chat/ping`
3. **Direct n8n webhook**: `curl -X POST https://<n8n>/webhook/<path> -d '{"message":"test"}'`
4. **Full integration**: `curl -X POST https://<backend>/chat -d '{"message":"test"}'`
5. **CORS preflight**: `curl -X OPTIONS https://<backend>/chat`

---

## 📋 Deployment Checklist

After merging this PR, follow `MANUAL_STEPS.md`:

### Railway Backend
- [ ] Set `N8N_URL`
- [ ] Set `N8N_WEBHOOK_PATH`
- [ ] Set `N8N_API_KEY` (optional)
- [ ] Set `MONGO_URI`
- [ ] Set `ALLOWED_ORIGINS`
- [ ] Redeploy service

### Railway n8n
- [ ] Set `N8N_HOST`
- [ ] Set `WEBHOOK_URL`
- [ ] Set `N8N_API_KEY` (if used)
- [ ] Activate workflow
- [ ] Verify production webhook path
- [ ] Redeploy service

### Cloudflare Pages
- [ ] Set `VITE_BACKEND_URL`
- [ ] Redeploy production
- [ ] Purge cache if needed

### Verification
- [ ] `/health` returns 200
- [ ] `/chat/ping` returns 200
- [ ] Chatbot works end-to-end
- [ ] Check logs for errors

---

## 🔒 Security Improvements

1. **CORS restricted** to specific origins (no more `*`)
2. **API key authentication** for n8n (optional but recommended)
3. **Basic auth** documentation for n8n editor UI
4. **Error messages** don't leak sensitive information
5. **MongoDB password** encoding documented

---

## 📚 Documentation

All documentation is complete and actionable:

- ✅ `analysis/inventory.md` - Full codebase analysis
- ✅ `curl_test.md` - 7 test commands with expected outputs
- ✅ `MANUAL_STEPS.md` - Complete deployment guide

---

## 🚀 Next Steps

1. Review and merge this PR
2. Follow `MANUAL_STEPS.md` exactly
3. Run tests from `curl_test.md`
4. Monitor Railway logs for errors
5. Verify chatbot works on production site

---

## ⚠️ Breaking Changes

### Environment Variables
Some environment variables have been renamed. Update your Railway configuration:

| Old Variable | New Variable | Required |
|--------------|--------------|----------|
| `MONGO_URL` | `MONGO_URI` | Yes (or keep `MONGO_URL`) |
| `CORS_ORIGINS` | `ALLOWED_ORIGINS` | No (defaults provided) |
| `N8N_WEBHOOK_URL` | `N8N_URL` + `N8N_WEBHOOK_PATH` | Yes |

**Note**: Backward compatibility is maintained for `MONGO_URL` and `N8N_WEBHOOK_URL`, but they will log deprecation warnings.

### New Required Variables
- `N8N_URL` - Base URL of n8n service
- `N8N_WEBHOOK_PATH` - Production webhook path (without `/webhook/` prefix)

---

## 📊 Files Changed

- `backend/server.py` - Major refactor with new routes and error handling
- `analysis/inventory.md` - New file
- `curl_test.md` - New file
- `MANUAL_STEPS.md` - New file
- `PR_SUMMARY.md` - This file

**Frontend**: No changes needed (already using `VITE_BACKEND_URL` correctly)

---

## 🎉 Expected Outcomes

After completing all steps:

1. ✅ Chatbot connects to n8n successfully
2. ✅ Clear error messages when issues occur
3. ✅ Easy debugging with structured logs
4. ✅ Health checks for monitoring
5. ✅ Production-ready error handling
6. ✅ Comprehensive documentation for maintenance

---

## 💡 Additional Notes

- The existing `/api/chat/message` endpoint remains unchanged and continues to work
- The new `/chat` endpoint is designed for direct integration without database dependencies
- MongoDB is now optional for the chat flow (though still used for `/api/chat/message`)
- All changes follow FastAPI best practices
- Logging follows Railway/production standards

---

**Questions?** Review the documentation files:
- Technical issues → `curl_test.md`
- Configuration → `MANUAL_STEPS.md`
- Architecture → `analysis/inventory.md`
