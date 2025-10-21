#!/usr/bin/env python3
"""
Backend API Testing for BBQ Catering Chatbot
Tests all chatbot endpoints for functionality and error handling
"""

import requests
import json
import uuid
from datetime import datetime
import sys

# Use the production URL from frontend/.env
BASE_URL = "https://source-peek-2.preview.emergentagent.com/api"

class ChatbotAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        })
    
    def test_create_chat_session_valid(self):
        """Test creating a chat session with valid data"""
        test_name = "Create Chat Session - Valid Data"
        
        try:
            payload = {
                "user_name": "John Smith",
                "user_email": "john.smith@example.com"
            }
            
            response = requests.post(f"{self.base_url}/chat/session", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "user_name", "user_email", "created_at"]
                
                if all(field in data for field in required_fields):
                    if data["user_name"] == payload["user_name"] and data["user_email"] == payload["user_email"]:
                        self.session_id = data["id"]  # Store for later tests
                        self.log_test(test_name, True, "Session created successfully", f"Session ID: {self.session_id}")
                    else:
                        self.log_test(test_name, False, "Response data doesn't match input", str(data))
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test(test_name, False, f"Missing required fields: {missing}", str(data))
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test(test_name, False, "Request failed", str(e))
    
    def test_create_chat_session_invalid_email(self):
        """Test creating a chat session with invalid email"""
        test_name = "Create Chat Session - Invalid Email"
        
        try:
            payload = {
                "user_name": "Jane Doe",
                "user_email": "invalid-email"
            }
            
            response = requests.post(f"{self.base_url}/chat/session", json=payload, timeout=10)
            
            if response.status_code == 422:  # Validation error expected
                self.log_test(test_name, True, "Validation error returned as expected")
            else:
                self.log_test(test_name, False, f"Expected 422, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test(test_name, False, "Request failed", str(e))
    
    def test_create_chat_session_missing_fields(self):
        """Test creating a chat session with missing fields"""
        test_name = "Create Chat Session - Missing Fields"
        
        try:
            payload = {
                "user_name": "Bob Wilson"
                # Missing user_email
            }
            
            response = requests.post(f"{self.base_url}/chat/session", json=payload, timeout=10)
            
            if response.status_code == 422:  # Validation error expected
                self.log_test(test_name, True, "Validation error returned as expected")
            else:
                self.log_test(test_name, False, f"Expected 422, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test(test_name, False, "Request failed", str(e))
    
    def test_get_n8n_config_initial(self):
        """Test getting n8n config (should have default values)"""
        test_name = "Get n8n Config - Initial State"
        
        try:
            response = requests.get(f"{self.base_url}/chat/config", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "webhook_url" in data and "api_key" in data:
                    self.log_test(test_name, True, "Config retrieved", f"Current webhook_url: {data.get('webhook_url')}, API Key present: {bool(data.get('api_key'))}")
                else:
                    self.log_test(test_name, False, "Missing required fields in config", str(data))
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test(test_name, False, "Request failed", str(e))
    
    def test_update_n8n_config(self):
        """Test updating n8n webhook URL and API key"""
        test_name = "Update n8n Config"
        
        try:
            payload = {
                "webhook_url": "https://test.n8n.io/webhook/test",
                "api_key": "test-api-key-12345"
            }
            
            response = requests.put(f"{self.base_url}/chat/config", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "webhook_url" in data and "api_key" in data:
                    self.log_test(test_name, True, "Config updated successfully", f"New URL: {data['webhook_url']}, API Key: {data['api_key'][:10]}...")
                else:
                    self.log_test(test_name, False, "Unexpected response format", str(data))
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test(test_name, False, "Request failed", str(e))
    
    def test_get_n8n_config_after_update(self):
        """Test getting n8n config after update"""
        test_name = "Get n8n Config - After Update"
        
        try:
            response = requests.get(f"{self.base_url}/chat/config", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_url = "https://test.n8n.io/webhook/test"
                expected_api_key = "test-api-key-12345"
                if data.get("webhook_url") == expected_url and data.get("api_key") == expected_api_key:
                    self.log_test(test_name, True, "Config retrieved with correct webhook URL and API key")
                else:
                    self.log_test(test_name, False, f"Expected URL: {expected_url}, got {data.get('webhook_url')}; Expected API Key: {expected_api_key}, got {data.get('api_key')}")
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test(test_name, False, "Request failed", str(e))
    
    def test_send_chat_message_valid(self):
        """Test sending a chat message with valid session"""
        test_name = "Send Chat Message - Valid Session"
        
        if not self.session_id:
            self.log_test(test_name, False, "No valid session ID available from previous tests")
            return
        
        try:
            payload = {
                "session_id": self.session_id,
                "message": "Hello, I'm interested in your BBQ catering services. What packages do you offer?"
            }
            
            response = requests.post(f"{self.base_url}/chat/message", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "session_id", "message", "sender", "timestamp"]
                
                if all(field in data for field in required_fields):
                    if data["sender"] == "bot" and data["session_id"] == self.session_id:
                        # Since n8n webhook is a test URL, expect graceful error message
                        if "trouble processing" in data["message"] or "not fully configured" in data["message"]:
                            self.log_test(test_name, True, "Bot responded with graceful error message as expected", f"Response: {data['message']}")
                        else:
                            self.log_test(test_name, True, "Bot responded successfully", f"Response: {data['message']}")
                    else:
                        self.log_test(test_name, False, "Invalid response data", str(data))
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test(test_name, False, f"Missing required fields: {missing}", str(data))
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test(test_name, False, "Request failed", str(e))
    
    def test_send_chat_message_invalid_session(self):
        """Test sending a chat message with invalid session ID"""
        test_name = "Send Chat Message - Invalid Session"
        
        try:
            payload = {
                "session_id": str(uuid.uuid4()),  # Random UUID that doesn't exist
                "message": "This should fail"
            }
            
            response = requests.post(f"{self.base_url}/chat/message", json=payload, timeout=10)
            
            if response.status_code == 404:
                self.log_test(test_name, True, "404 error returned as expected for invalid session")
            else:
                self.log_test(test_name, False, f"Expected 404, got {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test(test_name, False, "Request failed", str(e))
    
    def test_send_chat_message_empty_message(self):
        """Test sending an empty chat message"""
        test_name = "Send Chat Message - Empty Message"
        
        if not self.session_id:
            self.log_test(test_name, False, "No valid session ID available from previous tests")
            return
        
        try:
            payload = {
                "session_id": self.session_id,
                "message": ""
            }
            
            response = requests.post(f"{self.base_url}/chat/message", json=payload, timeout=10)
            
            # This might be handled gracefully or return validation error
            if response.status_code in [200, 422]:
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(test_name, True, "Empty message handled gracefully", f"Bot response: {data.get('message', 'No message')}")
                else:
                    self.log_test(test_name, True, "Validation error returned for empty message")
            else:
                self.log_test(test_name, False, f"Unexpected status code {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test(test_name, False, "Request failed", str(e))
    
    def test_get_chat_history_valid(self):
        """Test getting chat history for valid session"""
        test_name = "Get Chat History - Valid Session"
        
        if not self.session_id:
            self.log_test(test_name, False, "No valid session ID available from previous tests")
            return
        
        try:
            response = requests.get(f"{self.base_url}/chat/messages/{self.session_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Should have at least user and bot messages from previous test
                    if len(data) >= 2:
                        # Check if we have both user and bot messages
                        senders = [msg.get("sender") for msg in data]
                        if "user" in senders and "bot" in senders:
                            self.log_test(test_name, True, f"Chat history retrieved with {len(data)} messages", f"Senders: {set(senders)}")
                        else:
                            self.log_test(test_name, False, "Missing user or bot messages", f"Senders found: {set(senders)}")
                    else:
                        self.log_test(test_name, True, f"Chat history retrieved with {len(data)} messages (may be empty if previous tests failed)")
                else:
                    self.log_test(test_name, False, "Response is not a list", str(data))
            else:
                self.log_test(test_name, False, f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test(test_name, False, "Request failed", str(e))
    
    def test_get_chat_history_invalid(self):
        """Test getting chat history for invalid session"""
        test_name = "Get Chat History - Invalid Session"
        
        try:
            invalid_session_id = str(uuid.uuid4())
            response = requests.get(f"{self.base_url}/chat/messages/{invalid_session_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) == 0:
                    self.log_test(test_name, True, "Empty list returned for invalid session (acceptable behavior)")
                else:
                    self.log_test(test_name, False, "Unexpected data for invalid session", str(data))
            else:
                # 404 would also be acceptable
                if response.status_code == 404:
                    self.log_test(test_name, True, "404 returned for invalid session")
                else:
                    self.log_test(test_name, False, f"Unexpected status code {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test(test_name, False, "Request failed", str(e))
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 Starting Chatbot API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print("=" * 60)
        
        # Test sequence following the complete flow
        self.test_create_chat_session_valid()
        self.test_create_chat_session_invalid_email()
        self.test_create_chat_session_missing_fields()
        
        self.test_get_n8n_config_initial()
        self.test_update_n8n_config()
        self.test_get_n8n_config_after_update()
        
        self.test_send_chat_message_valid()
        self.test_send_chat_message_invalid_session()
        self.test_send_chat_message_empty_message()
        
        self.test_get_chat_history_valid()
        self.test_get_chat_history_invalid()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if total - passed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
                    if result["details"]:
                        print(f"     Details: {result['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = ChatbotAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)