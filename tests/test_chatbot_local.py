import os
import sys
import asyncio
import uuid
import httpx

# Ensure the backend uses the in-memory DB for tests and has CORS wide open
os.environ.setdefault("USE_IN_MEMORY_DB", "true")
os.environ.setdefault("CORS_ORIGINS", "*")

# Optionally set provided n8n credentials (read by server on import)
os.environ.setdefault(
    "N8N_WEBHOOK_URL",
    "https://webhook-processor-production-a91f.up.railway.app/webhook/985e88ec-2d95-4b9c-a43f-3a9846dcda55",
)
os.environ.setdefault(
    "N8N_API_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4MWU1Zjk4Ny0xMzE3LTQ1NGEtYTAwMy0wOWRjZGZhYzZkZTciLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxMDU3NDMxfQ.uqCDj2b40-XJpBFrj-6RZGdDobShurS0ItS6RvozZRU",
)

# Ensure the repository root is importable
repo_root = "/workspace"
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.server import app  # noqa: E402


async def run_tests() -> bool:
    transport = httpx.ASGITransport(app=app)
    passed = 0
    total = 0

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        def check(name: str, cond: bool, details: str | None = None):
            nonlocal passed, total
            total += 1
            if cond:
                print(f"✅ PASS {name}")
                passed += 1
            else:
                print(f"❌ FAIL {name}{': ' + details if details else ''}")

        # Root
        r = await client.get("/api/")
        check("Root endpoint", r.status_code == 200 and r.json().get("message") == "Hello World")

        # Create session (valid)
        r = await client.post(
            "/api/chat/session",
            json={"user_name": "John Smith", "user_email": "john.smith@example.com"},
        )
        ok = r.status_code == 200 and all(k in r.json() for k in ["id", "user_name", "user_email", "created_at"])  # type: ignore
        check("Create chat session (valid)", ok, details=str(r.text))
        session_id = r.json().get("id") if ok else None

        # Create session (invalid email)
        r2 = await client.post(
            "/api/chat/session",
            json={"user_name": "Jane", "user_email": "not-an-email"},
        )
        check("Create chat session (invalid email)", r2.status_code == 422)

        # Create session (missing field)
        r3 = await client.post(
            "/api/chat/session",
            json={"user_name": "Bob"},
        )
        check("Create chat session (missing field)", r3.status_code == 422)

        # Update config to a fast-failing URL to avoid slow external calls
        fast_fail_url = "http://127.0.0.1:9/webhook/test"
        r4 = await client.put("/api/chat/config", json={"webhook_url": fast_fail_url})
        check("Update n8n config", r4.status_code == 200)

        r5 = await client.get("/api/chat/config")
        check(
            "Get n8n config",
            r5.status_code == 200 and r5.json().get("webhook_url") == fast_fail_url,  # type: ignore
            details=str(r5.text),
        )

        # Send chat message (valid session)
        if session_id:
            r6 = await client.post(
                "/api/chat/message",
                json={"session_id": session_id, "message": "Hi! What packages do you offer?"},
                timeout=10.0,
            )
            ok6 = r6.status_code == 200 and r6.json().get("sender") == "bot"  # type: ignore
            check("Send chat message (valid session)", ok6, details=str(r6.text))

            # Get chat history
            r7 = await client.get(f"/api/chat/messages/{session_id}")
            ok7 = r7.status_code == 200 and isinstance(r7.json(), list) and len(r7.json()) >= 2  # type: ignore
            check("Get chat history (valid session)", ok7, details=str(r7.text))

        # Invalid session message
        r8 = await client.post(
            "/api/chat/message",
            json={"session_id": str(uuid.uuid4()), "message": "Hello"},
        )
        check("Send chat message (invalid session)", r8.status_code == 404)

        # Invalid session history
        r9 = await client.get(f"/api/chat/messages/{uuid.uuid4()}")
        ok9 = r9.status_code == 200 and isinstance(r9.json(), list) and len(r9.json()) == 0  # type: ignore
        check("Get chat history (invalid session)", ok9, details=str(r9.text))

    print("\nSummary:")
    print(f"Passed: {passed}/{total}")
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    raise SystemExit(0 if success else 1)
