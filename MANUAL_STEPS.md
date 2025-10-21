# Manual Actions Checklist

## Cloudflare Pages (Frontend)

- Settings → Environment Variables:
  - `VITE_BACKEND_URL = https://<BACKEND_PUBLIC_URL>`
- Trigger a new Production deploy.
- Purge Cache if the app still calls an old URL.
- In DevTools Network, confirm requests go to `VITE_BACKEND_URL`.

## Railway (Backend Project)

- Variables:
  - `N8N_URL = https://<N8N_PUBLIC_URL>`
  - `N8N_WEBHOOK_PATH = <your_production_webhook_path>` (without `webhook/` or `webhook-test/` prefix)
  - `N8N_API_KEY = <if required>` (optional)
  - `MONGO_URI = <your_mongo_uri>` (RFC3986-encoded password)
  - `DB_NAME = <your_db_name>` (if not embedded in URI)
  - `ALLOWED_ORIGINS = https://<YOUR_CLOUDFLARE_PAGES_DOMAIN>,https://*.pages.dev`
- Redeploy service.

## Railway (n8n Project)

- Variables:
  - `WEBHOOK_URL = https://<N8N_PUBLIC_URL>`
  - `N8N_HOST = <n8n-subdomain>.up.railway.app`
  - `N8N_PORT = 8080`
  - `N8N_API_KEY = <set if using REST auth>`
  - If using basic auth for editor: `N8N_BASIC_AUTH_ACTIVE=true` plus creds
- Confirm the target workflow is Active and note its Production webhook path (e.g., `chatbot-prod-abc123`).
- Redeploy service.

## MongoDB

- If password contains special chars (@:/?#[]), URL-encode before saving to `MONGO_URI`.

## Post-Deploy Verification

- Run commands from `curl_test.md` (health, ping, webhook, chat) and confirm expected responses.
- In n8n, verify workflow runs from production webhook (not `/webhook-test/`).
- In browser, ensure chatbot network calls succeed and CORS is clean.
