# Curl Tests

Replace placeholders with your actual values before running.

```bash
# 1) Backend health
curl -i https://<BACKEND_PUBLIC_URL>/health

# 2) Backend → n8n ping
curl -i https://<BACKEND_PUBLIC_URL>/chat/ping

# 3) Direct n8n REST ping (if public)
curl -i https://<N8N_PUBLIC_URL>/rest/ping -H "X-N8N-API-KEY: <N8N_API_KEY>"

# 4) Direct n8n webhook (payload)
curl -i -X POST https://<N8N_PUBLIC_URL>/webhook/<N8N_WEBHOOK_PATH> \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: <N8N_API_KEY>" \
  -d '{"message":"hi from curl"}'

# 5) Frontend → Backend functional test
curl -i -X POST https://<BACKEND_PUBLIC_URL>/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hello","sessionId":"test-123"}'
```

## Expected Results

- Backend health
  - Expected: 200 OK
  - Sample: `{ "ok": true, "version": "<git-sha-or-dev>" }`

- Backend → n8n ping
  - Expected: 200 OK with `{ "n8n": <object|string>, "status": 200 }`
  - If 401: Missing/invalid `X-N8N-API-KEY`
  - If 5xx/timeout: n8n offline or wrong `N8N_URL`

- Direct n8n REST ping
  - Expected: 200 OK with `{ "status": "ok" }` (varies by n8n version)
  - If 401/403: API key missing/invalid or auth enabled

- Direct n8n webhook
  - Expected: 2xx OK with your workflow response (JSON or text)
  - 404: Using `/webhook-test/...` instead of production `/webhook/...`, or path mismatch

- Frontend → Backend functional test
  - Expected: 2xx OK; JSON passthrough of n8n workflow response
  - 502: Upstream n8n error included in body

## Quick Troubleshooting Matrix

- 404 on webhook: Ensure production path `/webhook/<path>`, not `/webhook-test/...`
- 401/403 from n8n: Set and pass `X-N8N-API-KEY` correctly; confirm key in n8n env
- 504 timeout: n8n slow/unreachable; verify `N8N_URL` and network access
- CORS error in browser: Ensure `ALLOWED_ORIGINS` includes your Pages domain and `https://*.pages.dev`
- Mixed content blocked: Use HTTPS for `VITE_BACKEND_URL` in Cloudflare Pages
- Mongo connection warnings: Ensure `MONGO_URI` is RFC3986-encoded; server will continue without DB
