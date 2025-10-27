"""
Mock n8n Webhook Server for Testing Chatbot
This simulates an n8n workflow that responds to chatbot messages
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import random

app = FastAPI(title="Mock n8n Webhook")

# Allow CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample responses for BBQ catering chatbot
SAMPLE_RESPONSES = [
    "Thanks for your interest! Our BBQ catering packages start at $15 per person. We specialize in slow-smoked brisket, pulled pork, and ribs. What type of event are you planning?",
    "We'd love to cater your event! Our most popular package includes brisket, pulled pork, coleslaw, baked beans, and cornbread. How many guests are you expecting?",
    "Great question! We use authentic Texas-style smoking techniques with hickory and mesquite wood. Our meats are smoked low and slow for 12-16 hours for that perfect tenderness.",
    "For holiday catering, we recommend booking at least 2-3 weeks in advance. We offer special holiday packages with all the fixings. What date are you looking at?",
    "Our minimum order is for 25 people, but we can accommodate events from intimate gatherings to large corporate functions of 500+. Tell me more about your event!",
    "Absolutely! We offer vegetarian sides including grilled vegetables, mac and cheese, green beans, and more. We can also accommodate dietary restrictions with advance notice.",
]

BBQ_KEYWORDS = {
    "price": "Our catering starts at $15 per person for basic packages and goes up to $30 per person for premium options with multiple meats and sides.",
    "menu": "Our signature menu includes slow-smoked brisket, pulled pork, ribs, chicken, with sides like coleslaw, baked beans, mac and cheese, and cornbread. We also have vegetarian options!",
    "booking": "To book your event, we just need the date, number of guests, and your preferred menu. We require a 50% deposit to secure the date. Would you like me to send you our booking form?",
    "delivery": "We offer full-service catering with setup and cleanup, or drop-off service. Delivery fees vary based on location. Where is your event located?",
    "holiday": "We're already taking holiday bookings! Thanksgiving and Christmas are filling up fast. We offer special holiday packages with turkey, ham, and all traditional sides.",
}


@app.post("/webhook/chat")
async def handle_chat_webhook(request: Request):
    """
    Handle incoming chat messages from the chatbot
    Expected payload:
    {
        "session_id": "uuid",
        "user_name": "John Doe",
        "user_email": "john@example.com",
        "message": "User's message",
        "timestamp": "ISO timestamp"
    }
    """
    data = await request.json()

    user_message = data.get("message", "").lower()
    user_name = data.get("user_name", "there")

    # Check for keywords and provide relevant responses
    response_text = None
    for keyword, response in BBQ_KEYWORDS.items():
        if keyword in user_message:
            response_text = response
            break

    # If no keyword match, use a random generic response
    if not response_text:
        response_text = random.choice(SAMPLE_RESPONSES)

    # Personalize if user asked a question
    if "?" in data.get("message", ""):
        response_text = f"Great question! {response_text}"

    # Log the interaction
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Received message from {user_name}")
    print(f"User: {data.get('message')}")
    print(f"Bot: {response_text}\n")

    # Return response in the format expected by the backend
    return {
        "response": response_text,
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": data.get("session_id")
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Mock n8n Webhook",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint with instructions"""
    return {
        "message": "Mock n8n Webhook Server for Chatbot Testing",
        "webhook_url": "http://localhost:8001/webhook/chat",
        "instructions": "Configure your chatbot to use the webhook_url above",
        "health_check": "GET /health"
    }


if __name__ == "__main__":
    print("=" * 60)
    print("🔥 Mock n8n Webhook Server Starting...")
    print("=" * 60)
    print("\n📍 Webhook URL: http://localhost:8001/webhook/chat")
    print("🏥 Health Check: http://localhost:8001/health")
    print("\n💡 Use this URL in your chatbot configuration")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
