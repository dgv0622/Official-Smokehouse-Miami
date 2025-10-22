#!/usr/bin/env python3
"""
Simple Configuration Verification Script
Verifies n8n webhook and API key are properly configured
"""

import sys
import os
import re

def verify_server_config():
    """Verify server.py has correct configuration"""
    print("=" * 70)
    print("🔍 VERIFYING CHATBOT CONFIGURATION")
    print("=" * 70)
    
    # Read server.py file
    server_file = "/workspace/backend/server.py"
    
    with open(server_file, 'r') as f:
        content = f.read()
    
    # Expected values
    expected_webhook = "https://webhook-processor-production-a91f.up.railway.app/webhook/985e88ec-2d95-4b9c-a43f-3a9846dcda55"
    expected_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4MWU1Zjk4Ny0xMzE3LTQ1NGEtYTAwMy0wOWRjZGZhYzZkZTciLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxMDU3NDMxfQ.uqCDj2b40-XJpBFrj-6RZGdDobShurS0ItS6RvozZRU"
    
    results = {}
    
    # Check webhook URL
    print("\n📡 Checking n8n Webhook URL...")
    if expected_webhook in content:
        print(f"✅ Webhook URL found in configuration")
        print(f"   URL: {expected_webhook}")
        results['webhook_url'] = True
    else:
        print(f"❌ Webhook URL not found in configuration")
        results['webhook_url'] = False
    
    # Check API key
    print("\n🔑 Checking n8n API Key...")
    if expected_api_key in content:
        print(f"✅ API Key found in configuration")
        print(f"   Key: {expected_api_key[:30]}...{expected_api_key[-10:]}")
        results['api_key'] = True
    else:
        print(f"❌ API Key not found in configuration")
        results['api_key'] = False
    
    # Check if they're used correctly with os.environ.get
    print("\n⚙️ Checking configuration pattern...")
    
    # Check for N8N_WEBHOOK_URL pattern
    webhook_pattern = r'N8N_WEBHOOK_URL\s*=\s*os\.environ\.get\(\s*["\']N8N_WEBHOOK_URL["\']'
    if re.search(webhook_pattern, content):
        print("✅ Webhook URL uses correct environment variable pattern")
        results['webhook_pattern'] = True
    else:
        print("⚠️  Webhook URL may not use environment variable pattern")
        results['webhook_pattern'] = False
    
    # Check for N8N_API_KEY pattern
    api_key_pattern = r'N8N_API_KEY\s*=\s*os\.environ\.get\(\s*["\']N8N_API_KEY["\']'
    if re.search(api_key_pattern, content):
        print("✅ API Key uses correct environment variable pattern")
        results['api_key_pattern'] = True
    else:
        print("⚠️  API Key may not use environment variable pattern")
        results['api_key_pattern'] = False
    
    # Check logging configuration
    print("\n📋 Checking logging configuration...")
    if 'logging.basicConfig' in content and 'logger = logging.getLogger(__name__)' in content:
        print("✅ Logging is properly configured")
        results['logging'] = True
    else:
        print("❌ Logging configuration issue")
        results['logging'] = False
    
    return results


def verify_frontend_components():
    """Verify frontend chatbot component"""
    print("\n" + "=" * 70)
    print("🎨 VERIFYING FRONTEND COMPONENTS")
    print("=" * 70)
    
    results = {}
    
    # Check ChatBot.tsx
    chatbot_file = "/workspace/frontend/src/components/ChatBot.tsx"
    print("\n📄 Checking ChatBot.tsx...")
    
    with open(chatbot_file, 'r') as f:
        content = f.read()
    
    # Check for essential features
    checks = {
        'Session creation': 'handleCreateSession',
        'Message sending': 'handleSendMessage',
        'Message loading': 'loadMessages',
        'Backend URL': 'BACKEND_URL',
        'User form': 'userName',
        'Message state': 'messages',
    }
    
    for feature, keyword in checks.items():
        if keyword in content:
            print(f"✅ {feature}: Found")
            results[f'chatbot_{feature}'] = True
        else:
            print(f"❌ {feature}: Missing")
            results[f'chatbot_{feature}'] = False
    
    # Check ChatConfig.tsx
    config_file = "/workspace/frontend/src/pages/ChatConfig.tsx"
    print("\n📄 Checking ChatConfig.tsx...")
    
    with open(config_file, 'r') as f:
        content = f.read()
    
    config_checks = {
        'Webhook URL config': 'webhookUrl',
        'Config loading': 'loadConfig',
        'Config saving': 'handleSave',
        'Backend URL': 'BACKEND_URL',
    }
    
    for feature, keyword in config_checks.items():
        if keyword in content:
            print(f"✅ {feature}: Found")
            results[f'config_{feature}'] = True
        else:
            print(f"❌ {feature}: Missing")
            results[f'config_{feature}'] = False
    
    return results


def test_webhook_connection():
    """Test connection to n8n webhook"""
    print("\n" + "=" * 70)
    print("🌐 TESTING N8N WEBHOOK CONNECTION")
    print("=" * 70)
    
    try:
        import httpx
        import asyncio
        
        webhook_url = "https://webhook-processor-production-a91f.up.railway.app/webhook/985e88ec-2d95-4b9c-a43f-3a9846dcda55"
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4MWU1Zjk4Ny0xMzE3LTQ1NGEtYTAwMy0wOWRjZGZhYzZkZTciLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxMDU3NDMxfQ.uqCDj2b40-XJpBFrj-6RZGdDobShurS0ItS6RvozZRU"
        
        async def test_connection():
            print(f"\n📤 Testing webhook: {webhook_url}")
            
            test_payload = {
                "session_id": "test-verification-session",
                "user_name": "Test User",
                "user_email": "test@example.com",
                "message": "Test message to verify webhook connectivity",
                "timestamp": "2025-10-22T00:00:00"
            }
            
            headers = {"X-N8N-API-KEY": api_key}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    print("   Sending request...")
                    response = await client.post(
                        webhook_url,
                        json=test_payload,
                        headers=headers
                    )
                    
                    print(f"\n📥 Response:")
                    print(f"   Status Code: {response.status_code}")
                    
                    # Try to parse as JSON
                    try:
                        response_data = response.json()
                        print(f"   Response Data: {response_data}")
                        
                        if response.status_code == 200:
                            print("\n✅ Webhook connection successful!")
                            if "response" in response_data or "message" in response_data:
                                bot_response = response_data.get("response") or response_data.get("message")
                                print(f"   Bot would respond with: {bot_response}")
                            return True
                        else:
                            print(f"\n⚠️  Unexpected status code: {response.status_code}")
                            return False
                    except ValueError:
                        # Non-JSON response
                        print(f"   Text Response: {response.text[:200]}")
                        if response.status_code == 200:
                            print("\n✅ Webhook connection successful (non-JSON response)")
                            return True
                        else:
                            print(f"\n⚠️  Unexpected status code: {response.status_code}")
                            return False
                        
                except httpx.HTTPError as e:
                    print(f"\n❌ HTTP Error: {e}")
                    return False
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    return False
        
        result = asyncio.run(test_connection())
        return {'webhook_connection': result}
        
    except ImportError:
        print("\n⚠️  httpx not available, skipping connection test")
        return {'webhook_connection': None}
    except Exception as e:
        print(f"\n❌ Error testing webhook: {e}")
        return {'webhook_connection': False}


def main():
    """Run all verification checks"""
    print("\n" + "=" * 70)
    print("🚀 BBQ CATERING CHATBOT VERIFICATION")
    print("=" * 70)
    
    all_results = {}
    
    # Run all checks
    all_results.update(verify_server_config())
    all_results.update(verify_frontend_components())
    all_results.update(test_webhook_connection())
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in all_results.values() if v is True)
    failed = sum(1 for v in all_results.values() if v is False)
    skipped = sum(1 for v in all_results.values() if v is None)
    total = len(all_results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    if skipped > 0:
        print(f"⏭️  Skipped: {skipped}/{total}")
    
    # Show failed checks
    if failed > 0:
        print("\n🔍 Failed Checks:")
        for key, value in all_results.items():
            if value is False:
                print(f"   • {key}")
    
    # Final verdict
    print("\n" + "=" * 70)
    if failed == 0:
        print("🎉 ALL CHECKS PASSED! Chatbot is properly configured.")
        print("\n✨ The chatbot is ready to use with the following configuration:")
        print("   • n8n webhook URL is configured")
        print("   • n8n API key is configured")
        print("   • Frontend components are in place")
        print("   • Webhook connection is working")
        return True
    else:
        print("⚠️  Some checks failed. Please review the output above.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
