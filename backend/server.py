from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime
import httpx
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


# n8n configuration (read from environment)
# If no DB-stored webhook is found, the server will fall back to this env var.
N8N_WEBHOOK_URL = os.environ.get("https://webhook-processor-production-a91f.up.railway.app/webhook/985e88ec-2d95-4b9c-a43f-3a9846dcda55")
N8N_API_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4MWU1Zjk4Ny0xMzE3LTQ1NGEtYTAwMy0wOWRjZGZhYzZkZTciLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxMDU3NDMxfQ.uqCDj2b40-XJpBFrj-6RZGdDobShurS0ItS6RvozZRU")
# Optional: customize how the API key is sent
# - Header name to use (default: X-N8N-API-KEY)
N8N_API_KEY_HEADER_NAME = os.environ.get("N8N_API_KEY_HEADER_NAME", "X-N8N-API-KEY")
# - If set, send API key as a query parameter with this name (takes precedence over header)
N8N_API_KEY_QUERY_PARAM = os.environ.get("N8N_API_KEY_QUERY_PARAM")


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Chatbot Models
class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_name: str
    user_email: EmailStr
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatSessionCreate(BaseModel):
    user_name: str
    user_email: EmailStr

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    message: str
    sender: str  # "user" or "bot"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatMessageSend(BaseModel):
    session_id: str
    message: str

class N8nConfig(BaseModel):
    webhook_url: Optional[str] = None

class N8nConfigUpdate(BaseModel):
    webhook_url: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Chatbot Routes
@api_router.post("/chat/session", response_model=ChatSession)
async def create_chat_session(session_data: ChatSessionCreate):
    """Create a new chat session with user information"""
    session = ChatSession(**session_data.dict())
    await db.chat_sessions.insert_one(session.dict())
    logger.info(f"Created chat session: {session.id} for {session.user_email}")
    return session

@api_router.post("/chat/message", response_model=ChatMessage)
async def send_chat_message(message_data: ChatMessageSend):
    """Send a message to n8n workflow and return the response"""
    # Verify session exists
    session = await db.chat_sessions.find_one({"id": message_data.session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Save user message
    user_message = ChatMessage(
        session_id=message_data.session_id,
        message=message_data.message,
        sender="user"
    )
    await db.chat_messages.insert_one(user_message.dict())
    
    # Get n8n webhook URL
    config = await db.n8n_config.find_one({})
    webhook_url = (config.get("webhook_url") if (config and config.get("webhook_url")) else N8N_WEBHOOK_URL)
    
    bot_response_text = ""
    
    if webhook_url:
        try:
            # Send to n8n workflow
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Build URL and headers depending on how the API key should be passed
                request_headers = {}
                url_to_post = webhook_url

                if N8N_API_KEY and N8N_API_KEY_QUERY_PARAM:
                    # Append API key as query param
                    parts = urlsplit(url_to_post)
                    query_params = dict(parse_qsl(parts.query))
                    query_params[N8N_API_KEY_QUERY_PARAM] = N8N_API_KEY
                    new_query = urlencode(query_params, doseq=True)
                    url_to_post = urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
                elif N8N_API_KEY:
                    # Send API key in header (default)
                    request_headers[N8N_API_KEY_HEADER_NAME] = N8N_API_KEY

                response = await client.post(
                    url_to_post,
                    json={
                        "session_id": message_data.session_id,
                        "user_name": session.get("user_name"),
                        "user_email": session.get("user_email"),
                        "message": message_data.message,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    headers=request_headers or None
                )
                response.raise_for_status()

                # Parse n8n response (support JSON or plain text)
                try:
                    n8n_response = response.json()
                    bot_response_text = (
                        n8n_response.get("response")
                        or n8n_response.get("message")
                        or str(n8n_response)
                    )
                except ValueError:
                    # Not JSON; use raw text
                    bot_response_text = response.text.strip() or "(no response)"
                
        except httpx.HTTPError as e:
            logger.error(f"Error calling n8n webhook: {e}")
            bot_response_text = "I apologize, but I'm having trouble processing your request right now. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error with n8n: {e}")
            bot_response_text = "I apologize, but I'm having trouble processing your request right now. Please try again later."
    else:
        # No webhook configured - return default message
        bot_response_text = "The chatbot is not fully configured yet. Please contact the administrator to set up the n8n webhook URL."
    
    # Save bot response
    bot_message = ChatMessage(
        session_id=message_data.session_id,
        message=bot_response_text,
        sender="bot"
    )
    await db.chat_messages.insert_one(bot_message.dict())
    
    return bot_message

@api_router.get("/chat/messages/{session_id}", response_model=List[ChatMessage])
async def get_chat_messages(session_id: str):
    """Get all messages for a chat session"""
    messages = await db.chat_messages.find({"session_id": session_id}).sort("timestamp", 1).to_list(1000)
    return [ChatMessage(**msg) for msg in messages]

@api_router.get("/chat/config", response_model=N8nConfig)
async def get_n8n_config():
    """Get the current n8n webhook configuration"""
    config = await db.n8n_config.find_one({})
    if config and config.get("webhook_url"):
        return N8nConfig(webhook_url=config.get("webhook_url"))
    return N8nConfig(webhook_url=N8N_WEBHOOK_URL)

@api_router.put("/chat/config")
async def update_n8n_config(config_data: N8nConfigUpdate):
    """Update the n8n webhook URL"""
    # Delete existing config and insert new one
    await db.n8n_config.delete_many({})
    await db.n8n_config.insert_one({"webhook_url": config_data.webhook_url})
    logger.info("Updated n8n webhook URL")
    return {"message": "Configuration updated successfully", "webhook_url": config_data.webhook_url}

# Configure logging (before routes that use logger)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
