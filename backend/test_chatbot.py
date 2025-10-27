"""
Chatbot API Testing Script
Tests all chatbot endpoints without needing MongoDB
"""
import asyncio
import httpx
from datetime import datetime
import json

BACKEND_URL = "http://localhost:8000"
WEBHOOK_URL = "http://localhost:8001"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_test(name, status, details=""):
    """Print formatted test results"""
    symbol = "✓" if status else "✗"
    color = Colors.GREEN if status else Colors.RED
    print(f"{color}{symbol} {name}{Colors.END}")
    if details:
        print(f"  {details}")


async def test_backend_health():
    """Test if backend is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/")
            print_test("Backend Server", response.status_code == 200,
                      f"Response: {response.json()}")
            return response.status_code == 200
    except Exception as e:
        print_test("Backend Server", False, f"Error: {e}")
        return False


async def test_webhook_health():
    """Test if mock webhook is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{WEBHOOK_URL}/health")
            print_test("Mock n8n Webhook", response.status_code == 200,
                      f"Response: {response.json()}")
            return response.status_code == 200
    except Exception as e:
        print_test("Mock n8n Webhook", False, f"Error: {e}")
        return False


async def test_create_session():
    """Test creating a chat session"""
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "user_name": "Test User",
                "user_email": "test@example.com"
            }
            response = await client.post(
                f"{BACKEND_URL}/api/chat/session",
                json=payload
            )
            if response.status_code == 200:
                data = response.json()
                print_test("Create Chat Session", True,
                          f"Session ID: {data.get('id')}")
                return data.get('id')
            else:
                print_test("Create Chat Session", False,
                          f"Status: {response.status_code}, Body: {response.text}")
                return None
    except Exception as e:
        print_test("Create Chat Session", False, f"Error: {e}")
        return None


async def test_send_message(session_id):
    """Test sending a message"""
    if not session_id:
        print_test("Send Message", False, "No session ID")
        return False

    try:
        async with httpx.AsyncClient(timeout=35.0) as client:
            payload = {
                "session_id": session_id,
                "message": "What are your catering prices?"
            }
            response = await client.post(
                f"{BACKEND_URL}/api/chat/message",
                json=payload
            )
            if response.status_code == 200:
                data = response.json()
                print_test("Send Message", True,
                          f"Bot Response: {data.get('message')[:100]}...")
                return True
            else:
                print_test("Send Message", False,
                          f"Status: {response.status_code}, Body: {response.text}")
                return False
    except Exception as e:
        print_test("Send Message", False, f"Error: {e}")
        return False


async def test_get_messages(session_id):
    """Test retrieving message history"""
    if not session_id:
        print_test("Get Message History", False, "No session ID")
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/chat/messages/{session_id}"
            )
            if response.status_code == 200:
                data = response.json()
                print_test("Get Message History", True,
                          f"Found {len(data)} messages")
                return True
            else:
                print_test("Get Message History", False,
                          f"Status: {response.status_code}")
                return False
    except Exception as e:
        print_test("Get Message History", False, f"Error: {e}")
        return False


async def test_get_config():
    """Test getting webhook configuration"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/chat/config")
            if response.status_code == 200:
                data = response.json()
                print_test("Get Webhook Config", True,
                          f"Webhook URL: {data.get('webhook_url')}")
                return True
            else:
                print_test("Get Webhook Config", False,
                          f"Status: {response.status_code}")
                return False
    except Exception as e:
        print_test("Get Webhook Config", False, f"Error: {e}")
        return False


async def test_update_config():
    """Test updating webhook configuration"""
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "webhook_url": "http://localhost:8001/webhook/chat"
            }
            response = await client.put(
                f"{BACKEND_URL}/api/chat/config",
                json=payload
            )
            if response.status_code == 200:
                data = response.json()
                print_test("Update Webhook Config", True,
                          f"Message: {data.get('message')}")
                return True
            else:
                print_test("Update Webhook Config", False,
                          f"Status: {response.status_code}")
                return False
    except Exception as e:
        print_test("Update Webhook Config", False, f"Error: {e}")
        return False


async def run_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("🧪 CHATBOT API TESTING SUITE")
    print(f"{'='*60}{Colors.END}\n")

    print(f"{Colors.BLUE}{Colors.BOLD}Phase 1: Health Checks{Colors.END}")
    backend_ok = await test_backend_health()
    webhook_ok = await test_webhook_health()

    if not backend_ok:
        print(f"\n{Colors.RED}❌ Backend server is not running!{Colors.END}")
        print(f"{Colors.YELLOW}Start it with: uvicorn server:app --reload{Colors.END}\n")
        return

    if not webhook_ok:
        print(f"\n{Colors.YELLOW}⚠️  Mock webhook is not running!{Colors.END}")
        print(f"{Colors.YELLOW}Start it with: python mock_n8n_webhook.py{Colors.END}")
        print(f"{Colors.YELLOW}Tests will continue but message responses will fail.{Colors.END}\n")

    print(f"\n{Colors.BLUE}{Colors.BOLD}Phase 2: Webhook Configuration{Colors.END}")
    await test_get_config()
    await test_update_config()

    print(f"\n{Colors.BLUE}{Colors.BOLD}Phase 3: Chat Session Flow{Colors.END}")
    session_id = await test_create_session()

    if session_id:
        await test_send_message(session_id)
        await test_get_messages(session_id)

    print(f"\n{Colors.BOLD}{'='*60}")
    print("✅ TESTING COMPLETE")
    print(f"{'='*60}{Colors.END}\n")


if __name__ == "__main__":
    print(f"\n{Colors.YELLOW}Prerequisites:{Colors.END}")
    print(f"1. Backend server running on port 8000")
    print(f"2. Mock webhook running on port 8001 (optional)")
    print(f"3. MongoDB connection configured\n")

    asyncio.run(run_tests())
