#!/usr/bin/env python3
"""
Example script to send webhooks to the Skippy service.
"""

import requests
import json
import time
from datetime import datetime


def send_webhook(event_type: str, payload: dict, source: str = "example-script"):
    """Send a webhook to the Skippy service."""
    url = "http://localhost:8000/webhooks"
    
    webhook_data = {
        "event_type": event_type,
        "payload": payload,
        "source": source,
        "headers": {
            "content-type": "application/json",
            "user-agent": "skippy-example/1.0"
        }
    }
    
    try:
        response = requests.post(url, json=webhook_data)
        response.raise_for_status()
        
        webhook_response = response.json()
        print(f"✅ Webhook sent successfully!")
        print(f"   ID: {webhook_response['id']}")
        print(f"   Event: {webhook_response['event_type']}")
        print(f"   Created: {webhook_response['created_at']}")
        return webhook_response
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send webhook: {e}")
        return None


def main():
    """Main function to demonstrate webhook sending."""
    print("🚀 Skippy Webhook Example")
    print("=" * 40)
    
    # Example 1: User created webhook
    print("\n📝 Sending user.created webhook...")
    user_payload = {
        "user_id": "user_123",
        "email": "john.doe@example.com",
        "name": "John Doe",
        "created_at": datetime.utcnow().isoformat()
    }
    send_webhook("user.created", user_payload)
    
    time.sleep(1)
    
    # Example 2: Payment completed webhook
    print("\n💳 Sending payment.completed webhook...")
    payment_payload = {
        "payment_id": "pay_456",
        "amount": 99.99,
        "currency": "USD",
        "customer_id": "user_123",
        "status": "completed",
        "completed_at": datetime.utcnow().isoformat()
    }
    send_webhook("payment.completed", payment_payload)
    
    time.sleep(1)
    
    # Example 3: Custom event webhook
    print("\n🎯 Sending custom event webhook...")
    custom_payload = {
        "order_id": "order_789",
        "items": ["item_1", "item_2"],
        "total": 149.99,
        "shipping_address": {
            "street": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip": "10001"
        }
    }
    send_webhook("order.placed", custom_payload)
    
    print("\n🎉 All webhooks sent!")
    print("\n📖 Check the API documentation at: http://localhost:8000/docs")
    print("🔍 View webhooks at: http://localhost:8000/webhooks")


if __name__ == "__main__":
    main()
