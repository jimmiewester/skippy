import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.config import settings
from app.models.sms import SMSWebhook
from app.services.dynamodb_service import DynamoDBService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A webhook service for receiving elk46 SMS and storing in DynamoDB",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global DynamoDB service instance
db_service = DynamoDBService()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Skippy webhook service...")
    
    # Initialize DynamoDB table
    await db_service.create_table_if_not_exists()
    
    logger.info("Skippy webhook service started successfully!")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0"
    }


@app.post("/elks/sms")
async def receive_sms_webhook(request: Request):
    """Receive SMS webhook from 46elks and store in DynamoDB."""
    try:
        # Parse form data from 46elks webhook
        form_data = await request.form()
        
        # Debug: Log the received form data
        logger.info(f"Received form data: {dict(form_data)}")
        
        # Convert form data to dict and handle URL encoding
        sms_data = {}
        for key, value in form_data.items():
            if key == "from":
                sms_data["from_number"] = value
            elif key == "to":
                sms_data["to_number"] = value
            else:
                sms_data[key] = value
        
        # Debug: Log the processed SMS data
        logger.info(f"Processed SMS data: {sms_data}")
        
        # Create SMS webhook object
        sms_webhook = SMSWebhook(**sms_data)
        
        # Store in DynamoDB
        webhook_data = {
            'event_type': 'sms_received',
            'payload': sms_webhook.dict(),
            'source': '46elks',
            'headers': dict(request.headers)
        }
        
        stored_webhook = await db_service.create_webhook(webhook_data)
        logger.info(f"Stored webhook with ID: {stored_webhook['id']}")
        
        return Response(status_code=200)
        
    except Exception as e:
        logger.error(f"Error processing SMS webhook: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        if hasattr(e, 'errors'):
            logger.error(f"Validation errors: {e.errors}")
        return Response(
            content="Error processing SMS",
            media_type="text/plain",
            status_code=500
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
