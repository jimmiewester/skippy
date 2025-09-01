# Skippy - FastAPI Webhook Service with DynamoDB and Worker Tasks

A Python project featuring:
- **FastAPI** for webhook endpoints
- **DynamoDB** for data storage
- **Celery** for continuous worker tasks
- **Redis** as message broker
- **46elks SMS Integration** for receiving and processing SMS messages

## Project Structure

```
Skippy/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models/              # Pydantic models (webhooks & SMS)
│   ├── services/            # Business logic (webhooks & SMS)
│   ├── workers/             # Celery tasks (webhooks & SMS)
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── examples/                # Example scripts
├── docker-compose.yml       # Docker setup
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Setup

### Option 1: Quick Development Setup
1. **Run the startup script:**
   ```bash
   ./start.sh
   ```

### Option 2: Manual Setup
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment variables:**
   Create a `.env` file with:
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   DYNAMODB_TABLE_NAME=skippy_webhooks
   REDIS_URL=redis://localhost:6379
   ```

3. **Start services with Docker:**
   ```bash
   docker-compose up -d
   ```

### Option 3: Production Setup with systemd
1. **Install as systemd service (with auto-reload):**
   ```bash
   ./install-systemd.sh
   ```

2. **Manage services:**
   ```bash
   # Start all services
   sudo systemctl start skippy*
   
   # Check status
   sudo systemctl status skippy
   
   # View logs
   sudo journalctl -u skippy -f
   
   # Stop all services
   sudo systemctl stop skippy*
   ```

3. **Uninstall systemd services:**
   ```bash
   ./uninstall-systemd.sh
   ```

## Running the Application

1. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the Celery worker:**
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info
   ```

3. **Start the Celery beat scheduler (optional):**
   ```bash
   celery -A app.workers.celery_app beat --loglevel=info
   ```

## API Endpoints

### Webhooks
- `GET /health` - Health check
- `POST /webhooks` - Receive webhook data
- `GET /webhooks` - List webhooks
- `GET /webhooks/{webhook_id}` - Get specific webhook
- `PUT /webhooks/{webhook_id}` - Update webhook
- `DELETE /webhooks/{webhook_id}` - Delete webhook
- `POST /webhooks/{webhook_id}/process` - Manually trigger processing

### SMS (46elks Integration)
- `POST /elks/sms` - Receive SMS webhook from 46elks
- `GET /sms` - List all SMS messages
- `GET /sms/{sms_id}` - Get specific SMS
- `POST /sms/{sms_id}/reply` - Send SMS reply
- `DELETE /sms/{sms_id}` - Delete SMS

## Development

- **Format code:** `black app/ tests/`
- **Lint code:** `flake8 app/ tests/`
- **Type checking:** `mypy app/`
- **Run tests:** `pytest`
- **Test SMS:** `python examples/test_sms_webhook.py`
- **Install systemd:** `./install-systemd.sh`
- **Uninstall systemd:** `./uninstall-systemd.sh`
