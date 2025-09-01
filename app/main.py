import logging
from typing import List
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.config import settings
from app.models.sms import SMSWebhook
from app.services.sms_service import SMSService
from app.workers.sms_tasks import process_sms_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A webhook service with DynamoDB storage and worker tasks",
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

# Dependency to get SMS service
def get_sms_service():
    return SMSService()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Skippy webhook service...")
    
    sms_service = SMSService()
    await sms_service.initialize()
    
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
async def receive_sms_webhook(
    request: Request,
    sms_service: SMSService = Depends(get_sms_service)
):
    """Receive SMS webhook from 46elks."""
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
        
        # Store SMS in DynamoDB
        sms_response = await sms_service.store_sms(sms_webhook)
        
        return Response(
            status_code=200
        )
        
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
