# Chatbot Integration Test Commands

This document contains curl commands to test the entire chatbot integration stack.

## Environment Variables Needed

Before running these tests, set these variables in your terminal:

```bash
# Backend (your Railway backend service)
export BACKEND_PUBLIC_URL="https://your-backend.up.railway.app"

# n8n (your Railway n8n service)
export N8N_PUBLIC_URL="https://your-n8n.up.railway.app"
export N8N_WEBHOOK_PATH="your-production-webhook-path"
export N8N_API_KEY="your-n8n-api-key-if-configured"

# Frontend (your Cloudflare Pages domain)
export FRONTEND_URL="https://your-site.pages.dev"
```

---

## Test 1: Backend Health Check

**Purpose**: Verify backend is running and accessible

```bash
curl -i https://${BACKEND_PUBLIC_URL}/health
```

**Expected Response**:
```
HTTP/2 200 
content-type: application/json

{
  "ok": true,
  "version": "abc123def456",
  "timestamp": "2025-10-21T12:34:56.789Z"
}
```

**Troubleshooting**:
- `Connection refused` → Backend not deployed or domain incorrect
- `404 Not Found` → Route not implemented (check server.py)
- `502 Bad Gateway` → Backend crashed on startup (check Railway logs)

---

## Test 2: Backend → n8n Connectivity (Ping)

**Purpose**: Verify backend can reach n8n REST API

```bash
curl -i https://${BACKEND_PUBLIC_URL}/chat/ping
```

**Expected Response**:
```
HTTP/2 200
content-type: application/json

{
  "status": 200,
  "n8n": {
    "status": "ok"
  }
}
```

**Troubleshooting**:
- `"error": "N8N_URL not configured"` → Missing `N8N_URL` env var in Railway backend
- `"error": "N8N_TIMEOUT"` → n8n not reachable or wrong URL
- `"status": 401` → Missing or incorrect `N8N_API_KEY` (if required)
- `"status": 404` → n8n REST endpoint not available (check n8n deployment)

---

## Test 3: Direct n8n REST Ping (Optional)

**Purpose**: Test n8n directly to isolate backend issues

```bash
curl -i https://${N8N_PUBLIC_URL}/rest/ping \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}"
```

**Expected Response**:
```
HTTP/2 200
content-type: application/json

{
  "status": "ok"
}
```

**Troubleshooting**:
- `Connection refused` → n8n not running
- `401 Unauthorized` → API key required but not provided or incorrect
- `404 Not Found` → Wrong n8n URL or REST API disabled

---

## Test 4: Direct n8n Webhook Test

**Purpose**: Test the production webhook directly

```bash
curl -i -X POST https://${N8N_PUBLIC_URL}/webhook/${N8N_WEBHOOK_PATH} \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -d '{
    "message": "Test message from curl",
    "sessionId": "test-123",
    "receivedAt": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'"
  }'
```

**Expected Response**:
```
HTTP/2 200
content-type: application/json

{
  "response": "Hello! How can I help you with BBQ catering today?",
  "sessionId": "test-123"
}
```

**Troubleshooting**:
- `404 Not Found` → Wrong webhook path or workflow not active
  - ❌ Using `/webhook-test/` instead of `/webhook/`
  - ❌ Workflow is not activated in n8n
  - ❌ Typo in `N8N_WEBHOOK_PATH`
- `401 Unauthorized` → API key mismatch
- `500 Internal Error` → Workflow has errors (check n8n logs)

---

## Test 5: Backend → n8n Full Integration

**Purpose**: Test the `/chat` endpoint (end-to-end backend flow)

```bash
curl -i -X POST https://${BACKEND_PUBLIC_URL}/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your BBQ packages?",
    "sessionId": "test-session-456"
  }'
```

**Expected Response**:
```
HTTP/2 200
content-type: application/json

{
  "response": "We offer several BBQ packages...",
  "sessionId": "test-session-456"
}
```

**Troubleshooting**:
- `400 Bad Request` with `"code": "MISSING_MESSAGE"` → Empty message field
- `500 Internal Error` with `"code": "N8N_NOT_CONFIGURED"` → Missing `N8N_URL` or `N8N_WEBHOOK_PATH` env vars
- `502 Bad Gateway` with `"code": "UPSTREAM_N8N"` → n8n returned error
  - Check `"status"` and `"body"` fields for n8n error details
- `504 Gateway Timeout` with `"code": "N8N_TIMEOUT"` → n8n took >20 seconds to respond

---

## Test 6: Frontend → Backend (CORS Preflight)

**Purpose**: Verify CORS is configured correctly

```bash
curl -i -X OPTIONS https://${BACKEND_PUBLIC_URL}/chat \
  -H "Origin: ${FRONTEND_URL}" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type"
```

**Expected Response**:
```
HTTP/2 200
access-control-allow-origin: https://your-site.pages.dev
access-control-allow-methods: GET, POST, OPTIONS
access-control-allow-headers: *
access-control-allow-credentials: true
```

**Troubleshooting**:
- Missing `access-control-allow-origin` → CORS not configured
- `access-control-allow-origin: null` → Frontend origin not in `ALLOWED_ORIGINS`
- Browser shows "CORS error" → Check that:
  - `ALLOWED_ORIGINS` includes your Cloudflare Pages domain
  - You're using HTTPS (not HTTP)
  - Frontend is calling the correct `VITE_BACKEND_URL`

---

## Test 7: Frontend → Backend Functional Test

**Purpose**: Simulate actual frontend chat request

```bash
curl -i -X POST https://${BACKEND_PUBLIC_URL}/chat \
  -H "Content-Type: application/json" \
  -H "Origin: ${FRONTEND_URL}" \
  -d '{
    "message": "hello",
    "sessionId": "frontend-test-789"
  }'
```

**Expected Response**:
```
HTTP/2 200
content-type: application/json
access-control-allow-origin: https://your-site.pages.dev

{
  "response": "Hello! How can I assist you today?",
  ...
}
```

**Troubleshooting**:
- Same as Test 5, plus:
- Missing CORS headers → Origin not allowed (check `ALLOWED_ORIGINS`)

---

## Quick Diagnostic Matrix

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Test 1 fails | Backend not deployed | Deploy backend to Railway |
| Test 2 fails with "N8N_URL not configured" | Missing env var | Set `N8N_URL` in Railway backend |
| Test 2 fails with timeout | n8n unreachable | Check n8n deployment, verify URL |
| Test 3 fails with 401 | API key required | Set `N8N_API_KEY` in both services |
| Test 4 fails with 404 | Wrong webhook path or inactive workflow | Verify workflow is Active, check path |
| Test 4 gets `/webhook-test/` | Using test URL | Use `/webhook/` for production |
| Test 5 fails with 502 | n8n workflow error | Check n8n workflow logs |
| Test 6 fails | CORS not configured | Set `ALLOWED_ORIGINS` in Railway |
| Test 7 mixed content error | Frontend using HTTP | Ensure `VITE_BACKEND_URL` uses HTTPS |

---

## Production Readiness Checklist

Before going live, verify:

- ✅ Test 1 passes (backend healthy)
- ✅ Test 2 passes (backend → n8n connectivity)
- ✅ Test 4 passes (n8n webhook works)
- ✅ Test 5 passes (full integration)
- ✅ Test 6 passes (CORS configured)
- ✅ Test 7 passes (end-to-end with CORS)
- ✅ Using `/webhook/` not `/webhook-test/`
- ✅ n8n workflow is **Active** (not paused)
- ✅ Frontend deployed with correct `VITE_BACKEND_URL`
- ✅ All env vars set in Railway (both backend and n8n projects)

---

## Logging & Debugging

### View Backend Logs
```bash
# Railway CLI
railway logs --service backend

# Or in Railway dashboard: Service → Deployments → View Logs
```

### View n8n Logs
```bash
# Railway CLI
railway logs --service n8n

# Or check n8n UI: Workflow → Executions tab
```

### Check Frontend Console
```javascript
// In browser DevTools console:
console.log('Backend URL:', import.meta.env.VITE_BACKEND_URL)

// Test backend connectivity:
fetch(import.meta.env.VITE_BACKEND_URL + '/health')
  .then(r => r.json())
  .then(console.log)
```

---

## Notes

1. **Production vs Test Webhooks**: Always use `/webhook/` paths in production. The `/webhook-test/` endpoints are for testing workflows without triggering full execution.

2. **API Keys**: If n8n is public, you may not need `N8N_API_KEY`. However, for security, it's recommended to:
   - Set `N8N_API_KEY` in both Railway projects
   - Configure n8n to require the API key for webhooks

3. **HTTPS Required**: Cloudflare Pages requires HTTPS. Ensure:
   - `VITE_BACKEND_URL` uses `https://`
   - Railway services use their `https://` domains

4. **CORS Wildcard**: The `https://*.pages.dev` pattern in `ALLOWED_ORIGINS` allows all Cloudflare Pages preview deployments. For production, you may want to restrict this to your specific domain.

5. **Timeout Tuning**: The `/chat` endpoint has a 20s timeout. If n8n workflows take longer, you may need to:
   - Optimize the workflow
   - Implement async processing with callbacks
   - Return immediate acknowledgment and send response later
