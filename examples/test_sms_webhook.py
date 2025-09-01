#!/usr/bin/env python3
"""
Example script to test SMS webhook functionality by simulating 46elks webhook requests.
"""

import requests
import json
import time
from datetime import datetime


def test_sms_webhook(sms_data: dict):
    """Test SMS webhook endpoint by simulating 46elks webhook."""
    url = "http://localhost:8000/elks/sms"
    
    try:
        # Send form data as 46elks would
        response = requests.post(url, data=sms_data)
        
        print(f"📱 SMS Webhook Test")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ SMS webhook processed successfully!")
        else:
            print("   ❌ SMS webhook failed!")
            
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send SMS webhook: {e}")
        return None


def test_sms_api():
    """Test SMS API endpoints."""
    base_url = "http://localhost:8000"
    
    print("\n📋 Testing SMS API endpoints...")
    
    # Test listing SMS
    try:
        response = requests.get(f"{base_url}/sms")
        if response.status_code == 200:
            sms_list = response.json()
            print(f"   📝 Found {len(sms_list)} SMS messages")
            for sms in sms_list[:3]:  # Show first 3
                print(f"      - {sms['from_number']}: {sms['message'][:50]}...")
        else:
            print(f"   ❌ Failed to list SMS: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error listing SMS: {e}")


def main():
    """Main function to test SMS functionality."""
    print("📱 Skippy SMS Webhook Test")
    print("=" * 40)
    
    # Test 1: Simple greeting SMS
    print("\n📝 Testing simple greeting SMS...")
    sms_data_1 = {
        "id": "test_sms_001",
        "from": "+46706861004",
        "to": "+46706860000",
        "message": "Hello! How are you?",
        "direction": "incoming",
        "created": datetime.utcnow().isoformat()
    }
    test_sms_webhook(sms_data_1)
    
    time.sleep(1)
    
    # Test 2: Help request SMS
    print("\n🆘 Testing help request SMS...")
    sms_data_2 = {
        "id": "test_sms_002",
        "from": "+46706861005",
        "to": "+46706860000",
        "message": "I need help with my account",
        "direction": "incoming",
        "created": datetime.utcnow().isoformat()
    }
    test_sms_webhook(sms_data_2)
    
    time.sleep(1)
    
    # Test 3: Status inquiry SMS
    print("\n📊 Testing status inquiry SMS...")
    sms_data_3 = {
        "id": "test_sms_003",
        "from": "+46706861006",
        "to": "+46706860000",
        "message": "What's the status of my order?",
        "direction": "incoming",
        "created": datetime.utcnow().isoformat()
    }
    test_sms_webhook(sms_data_3)
    
    time.sleep(2)
    
    # Test SMS API endpoints
    test_sms_api()
    
    print("\n🎉 SMS testing complete!")
    print("\n📖 Check the API documentation at: http://localhost:8000/docs")
    print("📱 View SMS messages at: http://localhost:8000/sms")


if __name__ == "__main__":
    main()
