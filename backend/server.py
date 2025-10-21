from fastapi import FastAPI, APIRouter, HTTPException, Request
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


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging (MUST be before routes that use logger)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# n8n configuration (read from environment)
# New structure: separate base URL and webhook path
N8N_URL = os.environ.get("N8N_URL", "")  # e.g., https://n8n.railway.app
N8N_WEBHOOK_PATH = os.environ.get("N8N_WEBHOOK_PATH", "")  # e.g., my-webhook-path
N8N_API_KEY = os.environ.get("N8N_API_KEY")
# Backward compatibility: support old N8N_WEBHOOK_URL if new vars not set
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")

if not N8N_URL and N8N_WEBHOOK_URL:
    logger.warning("Using deprecated N8N_WEBHOOK_URL. Please set N8N_URL and N8N_WEBHOOK_PATH instead.")

# MongoDB connection with error handling
try:
    # Support both MONGO_URI (preferred) and MONGO_URL (legacy)
    mongo_uri = os.environ.get('MONGO_URI') or os.environ.get('MONGO_URL')
    if not mongo_uri:
        raise ValueError("MONGO_URI or MONGO_URL environment variable is required")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[os.environ.get('DB_NAME', 'bbq_catering')]
    logger.info("MongoDB client initialized")
except Exception as e:
    logger.error(f"Failed to initialize MongoDB: {e}")
    # Don't crash the server, but log the error
    client = None
    db = None

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ============================================================================
# HEALTH & CONNECTIVITY ROUTES (no /api prefix)
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint - returns server status and version"""
    return {
        "ok": True,
        "version": os.environ.get("RAILWAY_GIT_COMMIT_SHA", "dev"),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/chat/ping")
async def chat_ping():
    """Test n8n connectivity via REST API ping"""
    if not N8N_URL:
        return {
            "error": "N8N_URL not configured",
            "status": 500
        }
    
    headers = {}
    if N8N_API_KEY:
        headers["X-N8N-API-KEY"] = N8N_API_KEY
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            response = await http_client.get(
                f"{N8N_URL}/rest/ping",
                headers=headers
            )
            
            # Parse response
            try:
                body = response.json()
            except Exception:
                body = response.text
            
            logger.info(f"n8n ping response: status={response.status_code}")
            
            return {
                "status": response.status_code,
                "n8n": body
            }
    except httpx.TimeoutException:
        logger.error("n8n ping timeout")
        return {"error": "N8N_TIMEOUT", "status": 504}
    except Exception as e:
        logger.error(f"n8n ping error: {e}")
        return {"error": str(e), "status": 500}


@app.post("/chat")
async def chat(request: Request):
    """
    Direct chat endpoint that forwards messages to n8n webhook.
    This is the production endpoint for the chatbot.
    
    Expected payload: {
        \"message\": \"user message\",
        \"sessionId\": \"optional-session-id\",
        ...any other fields to forward
    }
    """
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON payload: {e}")
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_JSON", "message": "Request body must be valid JSON"}
        )
    
    # Validate required fields
    message = payload.get("message", "").strip()
    if not message:
        raise HTTPException(
            status_code=400,
            detail={"code": "MISSING_MESSAGE", "message": "message field is required and cannot be empty"}
        )
    
    # Build n8n webhook URL
    if N8N_URL and N8N_WEBHOOK_PATH:
        webhook_url = f"{N8N_URL}/webhook/{N8N_WEBHOOK_PATH}"
    elif N8N_WEBHOOK_URL:
        # Backward compatibility
        webhook_url = N8N_WEBHOOK_URL
    else:
        logger.error("n8n webhook not configured: N8N_URL and N8N_WEBHOOK_PATH required")
        raise HTTPException(
            status_code=500,
            detail={"code": "N8N_NOT_CONFIGURED", "message": "n8n webhook is not configured"}
        )
    
    # Add server metadata
    payload["receivedAt"] = datetime.utcnow().isoformat()
    
    # Prepare headers
    headers = {"Content-Type": "application/json"}
    if N8N_API_KEY:
        headers["X-N8N-API-KEY"] = N8N_API_KEY
    
    # Log the request
    session_id = payload.get("sessionId", "unknown")
    logger.info(f"Forwarding chat message to n8n: session={session_id}, message_len={len(message)}")
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as http_client:
            response = await http_client.post(
                webhook_url,
                json=payload,
                headers=headers
            )
            
            # Log response
            logger.info(f"n8n response: status={response.status_code}")
            
            # Handle non-2xx responses
            if response.status_code >= 400:
                error_body = response.text[:500]
                logger.error(
                    f"n8n upstream error: status={response.status_code}, "
                    f"body={error_body}"
                )
                raise HTTPException(
                    status_code=502,
                    detail={
                        "code": "UPSTREAM_N8N",
                        "message": "n8n webhook returned an error",
                        "status": response.status_code,
                        "body": error_body
                    }
                )
            
            # Parse successful response
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                return response.json()
            else:
                return {"text": response.text}
                
    except httpx.TimeoutException:
        logger.exception("n8n request timeout")
        raise HTTPException(
            status_code=504,
            detail={"code": "N8N_TIMEOUT", "message": "Request to n8n timed out after 20 seconds"}
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"Unexpected error calling n8n: {e}")
        raise HTTPException(
            status_code=502,
            detail={"code": "N8N_ERROR", "message": f"Error communicating with n8n: {str(e)}"}
        )


# ============================================================================
# API ROUTES (with /api prefix)
# ============================================================================


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

# Include the router in the main app
app.include_router(api_router)

# CORS Configuration
ALLOWED_ORIGINS = os.environ.get(
    'ALLOWED_ORIGINS',
    'https://*.pages.dev,http://localhost:3000'
).split(',')

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} "
        f"origin={request.headers.get('origin', 'unknown')}"
    )
    response = await call_next(request)
    logger.info(f"[{request_id}] Response status={response.status_code}")
    return response

@app.on_event("startup")
async def startup_db_client():
    """Validate MongoDB connection on startup"""
    if client:
        try:
            # Quick ping test with 1s timeout
            await client.admin.command('ping', serverSelectionTimeoutMS=1000)
            logger.info("✅ MongoDB connection validated successfully")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB connection validation failed: {e}")
            logger.warning("Server will continue but database operations may fail")
    else:
        logger.warning("⚠️ MongoDB client not initialized")

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()
        logger.info("MongoDB client closed")
