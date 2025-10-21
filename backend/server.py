from fastapi import FastAPI, APIRouter, HTTPException, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
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
from contextlib import asynccontextmanager



# n8n configuration (read from environment)
# Legacy full URL support for existing /api/chat/message route
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")

# Strict env usage for new /chat and /chat/ping routes
N8N_URL = os.environ.get("N8N_URL")
N8N_WEBHOOK_PATH = os.environ.get("N8N_WEBHOOK_PATH")
N8N_API_KEY = os.environ.get("N8N_API_KEY")

# Optional: customize how the API key is sent (legacy behavior remains supported for /api/chat/message)
# - Header name to use (default: X-N8N-API-KEY)
N8N_API_KEY_HEADER_NAME = os.environ.get("N8N_API_KEY_HEADER_NAME", "X-N8N-API-KEY")
# - If set, send API key as a query parameter with this name (takes precedence over header)
N8N_API_KEY_QUERY_PARAM = os.environ.get("N8N_API_KEY_QUERY_PARAM")


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (prefer MONGO_URI, fallback to legacy MONGO_URL/DB_NAME)
MONGO_URI = os.environ.get("MONGO_URI") or os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")
client = None
db = None
try:
    if MONGO_URI:
        # Fast fail server selection to avoid long startup hangs
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=1000)
        if DB_NAME:
            db = client[DB_NAME]
        else:
            # If DB name is encoded in the URI, get_default_database returns it; else remains None
            try:
                db = client.get_default_database()
            except Exception:
                db = None
    else:
        logging.getLogger(__name__).warning("MONGO_URI is not set; continuing without database")
except Exception as e:
    logging.getLogger(__name__).warning(f"Failed to initialize Mongo client: {e}")
    client = None
    db = None

# Allow configuring allowed origins for Cloudflare Pages
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
ALLOWED_ORIGIN_REGEX = os.environ.get("ALLOWED_ORIGIN_REGEX", r"https://.*\\.pages\\.dev$")

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


@asynccontextmanager
async def lifespan_context(app: FastAPI):
    # Startup: ping Mongo quickly and log outcome, continue regardless
    if client is not None:
        try:
            await client.admin.command("ping")
            logger.info("MongoDB ping successful on startup")
        except Exception as e:
            logger.warning(f"MongoDB ping failed on startup: {e}")
    yield
    # Shutdown: close Mongo client
    if client is not None:
        client.close()


# Replace app lifespan to include startup/shutdown logic
app.router.lifespan_context = lifespan_context

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=ALLOWED_ORIGIN_REGEX,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        origin = request.headers.get("origin") or "-"
        session_id_header = request.headers.get("x-session-id")
        session_id_query = request.query_params.get("sessionId")
        session_id = session_id_header or session_id_query or "-"
        logger.info(
            f"req {request_id} {request.method} {request.url.path} origin={origin} sid={session_id}"
        )
        response = await call_next(request)
        logger.info(
            f"res {request_id} {request.method} {request.url.path} status={response.status_code} sid={session_id}"
        )
        # Echo request id in response for traceability
        response.headers["X-Request-ID"] = request_id
        return response


app.add_middleware(RequestLoggingMiddleware)


def _n8n_headers() -> dict:
    headers: dict = {}
    if N8N_API_KEY:
        headers[N8N_API_KEY_HEADER_NAME] = N8N_API_KEY
    return headers


def _normalize_webhook_path(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    p = path.strip().lstrip("/")
    # Disallow webhook-test; strip any accidental prefixes
    if p.startswith("webhook-test/"):
        logger.warning("N8N_WEBHOOK_PATH appears to use test webhook. Use production path without 'webhook-test/'.")
        p = p[len("webhook-test/"):]
    if p.startswith("webhook/"):
        p = p[len("webhook/"):]
    return p


@app.get("/health")
async def health():
    version = os.getenv("RAILWAY_GIT_COMMIT_SHA") or os.getenv("GIT_SHA") or "dev"
    return {"ok": True, "version": version}


@app.get("/chat/ping")
async def chat_ping():
    if not N8N_URL:
        # Missing configuration
        detail = {"code": "ERR_N8N_CONFIG", "error": "N8N_URL not configured"}
        raise HTTPException(status_code=500, detail=detail)

    url = f"{N8N_URL.rstrip('/')}/rest/ping"
    try:
        async with httpx.AsyncClient(timeout=10.0) as hc:
            r = await hc.get(url, headers=_n8n_headers())
            content_type = r.headers.get("content-type", "")
            body = r.json() if "application/json" in content_type else (r.text or "")
            logger.info(f"n8n ping status={r.status_code} body={(str(body)[:200])}")
            return {"n8n": body, "status": r.status_code}
    except httpx.TimeoutException:
        logger.error("ERR_N8N_TIMEOUT during /chat/ping")
        detail = {"code": "ERR_N8N_TIMEOUT", "error": "Timeout contacting n8n"}
        raise HTTPException(status_code=504, detail=detail)
    except Exception as e:
        logger.error(f"ERR_N8N_PING: {e}")
        detail = {"code": "ERR_N8N_PING", "error": str(e)}
        raise HTTPException(status_code=502, detail=detail)


@app.post("/chat")
async def chat(request: Request):
    # Validate input
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail={"code": "ERR_BAD_REQUEST", "error": "Invalid JSON"})

    message = (payload.get("message") or "").strip() if isinstance(payload, dict) else ""
    if not message:
        raise HTTPException(status_code=400, detail={"code": "ERR_BAD_REQUEST", "error": "'message' is required"})

    # Build n8n production webhook URL
    normalized_path = _normalize_webhook_path(N8N_WEBHOOK_PATH)
    if not N8N_URL or not normalized_path:
        raise HTTPException(status_code=500, detail={"code": "ERR_N8N_CONFIG", "error": "N8N_URL or N8N_WEBHOOK_PATH not configured"})

    n8n_url = f"{N8N_URL.rstrip('/')}/webhook/{normalized_path}"

    # Prepare body and headers
    out_body = dict(payload)
    out_body["receivedAt"] = datetime.utcnow().isoformat()
    headers = {"Content-Type": "application/json"}
    headers.update(_n8n_headers())

    try:
        async with httpx.AsyncClient(timeout=20.0) as hc:
            r = await hc.post(n8n_url, json=out_body, headers=headers)
            content_type = r.headers.get("content-type", "")
            if r.status_code >= 400:
                body_text = r.text[:500] if isinstance(r.text, str) else str(r.text)[:500]
                code = f"ERR_N8N_{r.status_code}"
                logger.error(f"{code} upstream_status={r.status_code} body={body_text}")
                raise HTTPException(
                    status_code=502,
                    detail={"error": "UPSTREAM_N8N", "code": code, "status": r.status_code, "body": body_text},
                )

            # Success: passthrough JSON or text
            if "application/json" in content_type:
                return r.json()
            return {"text": r.text}
    except httpx.TimeoutException:
        logger.error("ERR_N8N_TIMEOUT during /chat")
        raise HTTPException(status_code=504, detail={"error": "N8N_TIMEOUT", "code": "ERR_N8N_TIMEOUT", "message": "n8n request timed out"})
    except HTTPException:
        # Already logged above
        raise
    except Exception as e:
        logger.error(f"ERR_N8N_UNEXPECTED during /chat: {e}")
        raise HTTPException(status_code=502, detail={"error": "ERR_N8N_UNEXPECTED", "message": str(e)})

# Retain shutdown hook for compatibility; connection is also closed via lifespan
@app.on_event("shutdown")
async def shutdown_db_client():
    if client is not None:
        client.close()
