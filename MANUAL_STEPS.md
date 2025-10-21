# Manual Configuration Steps

After merging the code changes from this PR, you must complete these manual configuration steps in Cloudflare, Railway, and n8n.

---

## 🔧 Step 1: Configure Railway Backend Service

**Navigation**: Railway Dashboard → Your Backend Project → Variables

### Required Environment Variables

Add or update these variables in your Railway backend service:

| Variable Name | Example Value | Description |
|--------------|---------------|-------------|
| `N8N_URL` | `https://your-n8n.up.railway.app` | Base URL of your n8n Railway service (no trailing slash) |
| `N8N_WEBHOOK_PATH` | `bbq-catering-chat` | Production webhook path (without `/webhook/` prefix) |
| `N8N_API_KEY` | `your-secret-key-123` | API key for n8n authentication (optional but recommended) |
| `MONGO_URI` | `mongodb+srv://user:password@cluster.mongodb.net/dbname` | MongoDB connection string (URL-encoded) |
| `DB_NAME` | `bbq_catering` | MongoDB database name |
| `ALLOWED_ORIGINS` | `https://your-site.pages.dev,https://*.pages.dev` | Comma-separated list of allowed CORS origins |

### Important Notes

1. **N8N_URL**: 
   - Get this from your n8n Railway service's public domain
   - Format: `https://n8n-production-abcd.up.railway.app`
   - **Do not** include `/webhook/` or any path

2. **N8N_WEBHOOK_PATH**:
   - This is just the path segment, e.g., `bbq-catering-chat`
   - The backend will construct the full URL: `${N8N_URL}/webhook/${N8N_WEBHOOK_PATH}`
   - **Do not** use `/webhook-test/` paths in production

3. **MONGO_URI**:
   - If your password contains special characters (`@`, `:`, `/`, `?`, `#`, `[`, `]`), you **must** URL-encode them
   - Use [urlencoder.org](https://www.urlencoder.org/) or similar
   - Example: `p@ssw0rd!` becomes `p%40ssw0rd%21`

4. **ALLOWED_ORIGINS**:
   - Include your production Cloudflare Pages domain
   - Use `https://*.pages.dev` to allow all preview deployments
   - Example: `https://bbq-catering.pages.dev,https://*.pages.dev`

### Steps to Add Variables

1. Open Railway Dashboard
2. Select your **Backend** project
3. Click on your service (e.g., "backend")
4. Go to **Variables** tab
5. Click **+ New Variable**
6. Add each variable from the table above
7. Click **Deploy** (Railway will auto-redeploy with new variables)

---

## 🔧 Step 2: Configure Railway n8n Service

**Navigation**: Railway Dashboard → Your n8n Project → Variables

### Required Environment Variables

| Variable Name | Example Value | Description |
|--------------|---------------|-------------|
| `N8N_HOST` | `your-n8n.up.railway.app` | Your n8n Railway service domain (no https://) |
| `N8N_PORT` | `5678` | Port n8n listens on (default: 5678) |
| `WEBHOOK_URL` | `https://your-n8n.up.railway.app` | Public URL for webhooks |
| `N8N_API_KEY` | `your-secret-key-123` | Same API key as backend (if using authentication) |
| `N8N_BASIC_AUTH_ACTIVE` | `true` | Enable basic auth for editor UI (optional) |
| `N8N_BASIC_AUTH_USER` | `admin` | Username for n8n UI (if using basic auth) |
| `N8N_BASIC_AUTH_PASSWORD` | `secure-password` | Password for n8n UI (if using basic auth) |

### Important Notes

1. **WEBHOOK_URL**:
   - This should match the `N8N_URL` you set in the backend
   - Include `https://` but no trailing slash

2. **N8N_API_KEY**:
   - If set, n8n will require this key for webhook and REST API calls
   - Must match the `N8N_API_KEY` in your backend service
   - Leave blank if you don't want API key authentication

3. **Basic Auth** (Optional):
   - Protects the n8n editor UI with username/password
   - Recommended for production to prevent unauthorized access to workflows

### Steps to Add Variables

1. Open Railway Dashboard
2. Select your **n8n** project (separate from backend)
3. Click on your n8n service
4. Go to **Variables** tab
5. Add each required variable
6. Click **Deploy**

---

## 🔧 Step 3: Configure n8n Workflow

**Navigation**: n8n UI → Workflows

### 1. Activate the Workflow

1. Open your n8n instance (`https://your-n8n.up.railway.app`)
2. Navigate to your BBQ catering chatbot workflow
3. Click the **Activate** toggle in the top-right (it should turn green)
4. **Critical**: Verify the workflow is using a **production** webhook, not a test webhook

### 2. Get the Production Webhook Path

1. In your workflow, find the **Webhook** trigger node
2. Click on the Webhook node
3. Look for the webhook URL or path
4. It should look like: `/webhook/bbq-catering-chat`
5. **Copy the path after `/webhook/`** (e.g., `bbq-catering-chat`)

### 3. Verify Webhook URL Format

❌ **WRONG** (Test webhook):
```
https://your-n8n.up.railway.app/webhook-test/bbq-catering-chat
```

✅ **CORRECT** (Production webhook):
```
https://your-n8n.up.railway.app/webhook/bbq-catering-chat
```

### 4. Update Railway Backend with Webhook Path

If you copied the path in step 2, ensure it's set as `N8N_WEBHOOK_PATH` in your Railway backend variables (see Step 1).

---

## 🔧 Step 4: Configure Cloudflare Pages

**Navigation**: Cloudflare Dashboard → Pages → Your Site → Settings

### 1. Set Environment Variables

1. Go to **Settings** → **Environment variables**
2. Select **Production** tab
3. Add this variable:

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `VITE_BACKEND_URL` | `https://your-backend.up.railway.app` | Your Railway backend public URL |

**Important**:
- Use the **exact** Railway backend URL (no trailing slash)
- Must start with `https://` (not `http://`)
- Get this from Railway → Backend Service → Settings → Domain

### 2. Deploy Production Build

After adding the environment variable:

1. Go to **Deployments** tab
2. Find the latest deployment
3. Click the **⋮** (three dots) menu
4. Select **Retry deployment** or **Redeploy**

OR

1. Push a new commit to your repository
2. Cloudflare will automatically redeploy

### 3. Purge Cache (If Needed)

If the chatbot still uses an old URL after redeploying:

1. Go to Cloudflare Dashboard → **Caching** → **Configuration**
2. Click **Purge Everything**
3. Confirm the purge
4. Wait 1-2 minutes for cache to clear

---

## 🔧 Step 5: Verify Configuration

After completing the above steps, verify the integration is working.

### 1. Test Backend Health

Open in browser or use curl:
```bash
https://your-backend.up.railway.app/health
```

Expected response:
```json
{
  "ok": true,
  "version": "abc123",
  "timestamp": "2025-10-21T12:34:56.789Z"
}
```

### 2. Test n8n Connectivity

```bash
https://your-backend.up.railway.app/chat/ping
```

Expected response:
```json
{
  "status": 200,
  "n8n": {
    "status": "ok"
  }
}
```

### 3. Test Frontend

1. Open your Cloudflare Pages site
2. Open browser DevTools (F12) → Console
3. Type: `import.meta.env.VITE_BACKEND_URL`
4. Verify it shows your Railway backend URL

### 4. Test Chatbot End-to-End

1. On your website, click the chatbot button
2. Enter your name and email
3. Send a test message
4. Verify you receive a response from n8n

---

## 🔧 Step 6: Monitor Logs

After deployment, monitor logs to catch any issues.

### Backend Logs (Railway)

1. Railway Dashboard → Backend Service
2. Click **Deployments** → Select latest deployment
3. Click **View Logs**

Look for:
- ✅ `MongoDB connection validated successfully`
- ✅ `[request_id] POST /chat origin=https://your-site.pages.dev`
- ✅ `n8n response: status=200`
- ❌ Any errors with `ERR_` or `UPSTREAM_N8N`

### n8n Logs (Railway)

1. Railway Dashboard → n8n Service
2. Click **Deployments** → Select latest deployment
3. Click **View Logs**

### n8n Execution Logs (n8n UI)

1. Open n8n UI
2. Click **Executions** in the left sidebar
3. Click on recent executions to see details
4. Verify webhook executions are successful

---

## 🚨 Troubleshooting Common Issues

### Issue 1: "CORS Error" in Browser Console

**Symptoms**:
```
Access to fetch at 'https://backend.railway.app/chat' from origin 'https://site.pages.dev' has been blocked by CORS policy
```

**Fix**:
1. Verify `ALLOWED_ORIGINS` in Railway backend includes your Cloudflare Pages domain
2. Ensure it's formatted correctly: `https://your-site.pages.dev,https://*.pages.dev`
3. Redeploy backend service in Railway

---

### Issue 2: "N8N_NOT_CONFIGURED" Error

**Symptoms**:
```json
{
  "detail": {
    "code": "N8N_NOT_CONFIGURED",
    "message": "n8n webhook is not configured"
  }
}
```

**Fix**:
1. Check Railway backend variables have `N8N_URL` and `N8N_WEBHOOK_PATH` set
2. Verify no typos in variable names
3. Redeploy backend service

---

### Issue 3: "UPSTREAM_N8N" Error (502)

**Symptoms**:
```json
{
  "detail": {
    "code": "UPSTREAM_N8N",
    "status": 404,
    "body": "Workflow not found"
  }
}
```

**Fix**:
1. Verify n8n workflow is **Active** (toggle in top-right of workflow editor)
2. Check `N8N_WEBHOOK_PATH` matches the actual webhook path in n8n
3. Ensure using `/webhook/` not `/webhook-test/`
4. Check n8n execution logs for errors

---

### Issue 4: MongoDB Connection Failed

**Symptoms** (in Railway logs):
```
⚠️ MongoDB connection validation failed: Authentication failed
```

**Fix**:
1. Check `MONGO_URI` is correct
2. If password has special characters, ensure it's URL-encoded
3. Verify MongoDB Atlas IP allowlist includes Railway IPs (or use `0.0.0.0/0` for testing)
4. Test connection with MongoDB Compass

---

### Issue 5: Frontend Shows "localhost:8000"

**Symptoms**:
- Chatbot tries to connect to `http://localhost:8000`
- CORS errors or connection refused

**Fix**:
1. Verify `VITE_BACKEND_URL` is set in Cloudflare Pages **Production** environment variables
2. Redeploy Cloudflare Pages site
3. Hard-refresh browser (Ctrl+Shift+R) to clear cache
4. Check DevTools console: `import.meta.env.VITE_BACKEND_URL` should show Railway URL

---

## 📋 Final Checklist

Before marking this as complete, verify:

- [ ] Railway Backend has all 6 required variables set
- [ ] Railway n8n has all required variables set
- [ ] n8n workflow is **Active** (not paused)
- [ ] n8n workflow uses **production** webhook path (`/webhook/`, not `/webhook-test/`)
- [ ] Cloudflare Pages has `VITE_BACKEND_URL` set
- [ ] Cloudflare Pages deployed with new environment variable
- [ ] `/health` endpoint returns 200 OK
- [ ] `/chat/ping` endpoint returns 200 OK with n8n status
- [ ] Chatbot works end-to-end on live site
- [ ] Railway logs show successful requests
- [ ] n8n executions show successful webhook triggers

---

## 📞 Support

If you encounter issues not covered here:

1. Check `curl_test.md` for detailed test commands
2. Review Railway logs (backend and n8n)
3. Check n8n execution logs in the UI
4. Verify all environment variables match exactly
5. Ensure all services are using HTTPS (not HTTP)

**Common gotchas**:
- Trailing slashes in URLs (should not be present)
- Using test webhooks instead of production webhooks
- Special characters in MongoDB password not URL-encoded
- Wrong origin in CORS config (must match exactly)
- Environment variables not redeployed (Railway needs manual redeploy)
