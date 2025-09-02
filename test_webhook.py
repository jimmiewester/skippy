#!/usr/bin/env python3
"""
Simple test script to verify the webhook endpoint.
Run this after starting the FastAPI server.
"""

import requests
import json
from datetime import datetime

def test_webhook():
    """Test the SMS webhook endpoint."""
    
    # Test data simulating 46elks webhook
    webhook_data = {
        'id': 'test_sms_123',
        'from': '+1234567890',
        'to': '+0987654321',
        'message': 'Hello from test!',
        'direction': 'incoming',
        'created': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Send POST request to webhook endpoint
    url = 'http://localhost:8000/elks/sms'
    
    try:
        response = requests.post(url, data=webhook_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print("❌ Webhook test failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health():
    """Test the health check endpoint."""
    
    url = 'http://localhost:8000/health'
    
    try:
        response = requests.get(url)
        
        print(f"Health Check Status: {response.status_code}")
        print(f"Health Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Health check successful!")
        else:
            print("❌ Health check failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing Skippy Webhook Service...")
    print("=" * 40)
    
    test_health()
    print()
    test_webhook()
