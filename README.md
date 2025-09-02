# Skippy - FastAPI Webhook Service for 46elks SMS

A simple Python webhook service that receives SMS messages from 46elks and stores them in DynamoDB.

## Features

- **FastAPI** for webhook endpoints
- **DynamoDB** for data storage
- **46elks SMS Integration** for receiving SMS webhooks
- **Simple and lightweight** - no complex processing or worker tasks

## Project Structure

```
Skippy/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models/
│   │   └── sms.py          # SMS webhook model
│   └── services/
│       └── dynamodb_service.py  # DynamoDB operations
├── docker-compose.yml       # Docker setup (DynamoDB local)
├── requirements.txt         # Python dependencies
├── test_webhook.py         # Simple test script
└── README.md               # This file
```

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file with:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=skippy_webhooks
```

### 3. Start DynamoDB Local (Optional)
For local development:
```bash
docker-compose up -d
```

## Running the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /health` - Health check
- `POST /elks/sms` - Receive SMS webhook from 46elks

## Testing

Run the test script to verify the webhook endpoint:
```bash
python test_webhook.py
```

## 46elks Integration

The service expects SMS webhooks from 46elks with the following fields:
- `id` - Unique message ID
- `from` - Sender phone number
- `to` - Recipient phone number  
- `message` - SMS content
- `direction` - Message direction (incoming/outgoing)
- `created` - UTC timestamp

## DynamoDB Schema

Webhooks are stored with the following structure:
- `id` - Unique webhook ID (partition key)
- `event_type` - Type of event (e.g., "sms_received")
- `payload` - Full SMS data from 46elks
- `source` - Source system ("46elks")
- `headers` - HTTP headers from the webhook
- `processed` - Processing status
- `created_at` - Webhook creation timestamp
- `updated_at` - Last update timestamp
