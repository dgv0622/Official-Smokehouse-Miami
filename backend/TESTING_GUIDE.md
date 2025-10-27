# Chatbot Testing Guide

## 🚀 Quick Start

### Option 1: Test with Real MongoDB (Recommended if you have credentials)

1. **Create `.env` file** in the `backend` directory:
```bash
# Copy the example
cp .env.example .env

# Edit .env with your real credentials
nano .env  # or use your preferred editor
```

Your `.env` should look like:
```env
MONGO_URL=mongodb+srv://your-username:your-password@cluster.mongodb.net/smokehouse
DB_NAME=smokehouse
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

2. **Install dependencies** (if not already installed):
```bash
pip install -r requirements.txt
```

3. **Start the mock n8n webhook** (in one terminal):
```bash
python mock_n8n_webhook.py
```
You should see:
```
🔥 Mock n8n Webhook Server Starting...
📍 Webhook URL: http://localhost:8001/webhook/chat
```

4. **Start the backend server** (in another terminal):
```bash
uvicorn server:app --reload --port 8000
```

5. **Configure the webhook** (in a third terminal):
```bash
python test_chatbot.py
```
Or manually via curl:
```bash
curl -X PUT http://localhost:8000/api/chat/config \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "http://localhost:8001/webhook/chat"}'
```

6. **Test the chatbot**:
```bash
python test_chatbot.py
```

---

### Option 2: Test with MongoDB Atlas (Free - If you don't have MongoDB)

1. **Set up MongoDB Atlas** (5 minutes):
   - Go to https://www.mongodb.com/cloud/atlas/register
   - Create a free account
   - Create a free cluster (M0)
   - Click "Connect" → "Connect your application"
   - Copy the connection string

2. **Create `.env` file**:
```env
MONGO_URL=<your-connection-string-from-atlas>
DB_NAME=smokehouse
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

3. **Follow steps 2-6 from Option 1**

---

### Option 3: Quick Test with Mock Everything (No MongoDB needed)

If you want to test WITHOUT MongoDB, I can create a mock database version.

---

## 📁 Files Created for Testing

1. **`mock_n8n_webhook.py`** - Simulates n8n AI responses
   - Runs on port 8001
   - Provides BBQ-related responses
   - Includes keyword detection for prices, menu, booking, etc.

2. **`test_chatbot.py`** - Automated test suite
   - Tests all API endpoints
   - Creates test sessions
   - Sends test messages
   - Validates responses

3. **`TESTING_GUIDE.md`** - This file

---

## 🧪 Testing Checklist

- [ ] MongoDB is accessible (or mock DB created)
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Mock webhook running on port 8001
- [ ] Backend server running on port 8000
- [ ] Webhook configured via API or test script
- [ ] Test script passes all tests

---

## 🔍 Manual Testing Steps

### 1. Create a Chat Session
```bash
curl -X POST http://localhost:8000/api/chat/session \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "John Doe",
    "user_email": "john@example.com"
  }'
```

Expected response:
```json
{
  "id": "some-uuid",
  "user_name": "John Doe",
  "user_email": "john@example.com",
  "created_at": "2025-10-24T..."
}
```

### 2. Send a Message
```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "<session-id-from-step-1>",
    "message": "What are your catering prices?"
  }'
```

Expected response:
```json
{
  "id": "some-uuid",
  "session_id": "<session-id>",
  "message": "Our catering starts at $15 per person...",
  "sender": "bot",
  "timestamp": "2025-10-24T..."
}
```

### 3. Get Message History
```bash
curl http://localhost:8000/api/chat/messages/<session-id>
```

---

## 🎨 Frontend Testing

### 1. Create frontend `.env` file:
```bash
cd ../frontend
cp .env.example .env
```

Edit `.env`:
```env
VITE_BACKEND_URL=http://localhost:8000
```

### 2. Install frontend dependencies:
```bash
npm install
```

### 3. Start frontend dev server:
```bash
npm run dev
```

### 4. Open browser and test:
- Navigate to `http://localhost:5173`
- Click the chatbot button (bottom right)
- Fill in name and email
- Send test messages

---

## ✅ Expected Test Results

When running `python test_chatbot.py`, you should see:

```
🧪 CHATBOT API TESTING SUITE
============================================================

Phase 1: Health Checks
✓ Backend Server
  Response: {'message': 'Hello World'}
✓ Mock n8n Webhook
  Response: {'status': 'healthy', ...}

Phase 2: Webhook Configuration
✓ Get Webhook Config
  Webhook URL: http://localhost:8001/webhook/chat
✓ Update Webhook Config
  Message: Configuration updated successfully

Phase 3: Chat Session Flow
✓ Create Chat Session
  Session ID: abc-123-def
✓ Send Message
  Bot Response: Our catering starts at $15 per person...
✓ Get Message History
  Found 2 messages

============================================================
✅ TESTING COMPLETE
============================================================
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Try a different port
uvicorn server:app --reload --port 8080
```

### MongoDB connection error
- Verify connection string in `.env`
- Check MongoDB Atlas network access (allow your IP)
- Ensure database user has read/write permissions

### Webhook not responding
```bash
# Check if webhook is running
curl http://localhost:8001/health

# Restart webhook
python mock_n8n_webhook.py
```

### CORS errors in frontend
- Verify `CORS_ORIGINS` in backend `.env` includes your frontend URL
- Restart backend after changing `.env`

---

## 🎯 Next Steps After Testing

1. ✅ Fix deprecated Pydantic `.dict()` calls → `.model_dump()`
2. ✅ Add authentication to `/api/chat/config` endpoint
3. ✅ Add rate limiting
4. ✅ Add message length validation
5. ✅ Deploy to production with real n8n workflow

---

## 📞 Need Help?

If you encounter issues:
1. Check logs in terminal where backend is running
2. Check browser console for frontend errors
3. Verify all services are running (backend, webhook, MongoDB)
4. Test each endpoint manually with curl
