import logging
from typing import List
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.config import settings
from app.models.webhook import WebhookCreate, WebhookResponse, WebhookUpdate
from app.models.sms import SMSWebhook, SMSResponse, SMSReply
from app.services.webhook_service import WebhookService
from app.services.sms_service import SMSService
from app.workers.tasks import process_webhook_task
from app.workers.sms_tasks import process_sms_task, send_sms_reply_task

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

# Dependency to get webhook service
def get_webhook_service():
    return WebhookService()

# Dependency to get SMS service
def get_sms_service():
    return SMSService()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Skippy webhook service...")
    webhook_service = WebhookService()
    await webhook_service.initialize()
    
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


@app.post("/webhooks", response_model=WebhookResponse)
async def create_webhook(
    webhook: WebhookCreate,
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """Create a new webhook."""
    try:
        webhook_response = await webhook_service.create_webhook(webhook)
        
        # Queue the webhook for processing
        process_webhook_task.delay(webhook_response.id)
        
        return webhook_response
    except Exception as e:
        logger.error(f"Error creating webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to create webhook")


@app.get("/webhooks", response_model=List[WebhookResponse])
async def list_webhooks(
    limit: int = 100,
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """List all webhooks."""
    try:
        return await webhook_service.list_webhooks(limit=limit)
    except Exception as e:
        logger.error(f"Error listing webhooks: {e}")
        raise HTTPException(status_code=500, detail="Failed to list webhooks")


@app.get("/webhooks/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """Get a specific webhook by ID."""
    try:
        webhook = await webhook_service.get_webhook(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        return webhook
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook {webhook_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook")


@app.put("/webhooks/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    webhook_update: WebhookUpdate,
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """Update a webhook."""
    try:
        webhook = await webhook_service.update_webhook(webhook_id, webhook_update)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        return webhook
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating webhook {webhook_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update webhook")


@app.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """Delete a webhook."""
    try:
        success = await webhook_service.delete_webhook(webhook_id)
        if not success:
            raise HTTPException(status_code=404, detail="Webhook not found")
        return {"message": "Webhook deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting webhook {webhook_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete webhook")


@app.post("/webhooks/{webhook_id}/process")
async def process_webhook(
    webhook_id: str,
    webhook_service: WebhookService = Depends(get_webhook_service)
):
    """Manually trigger webhook processing."""
    try:
        webhook = await webhook_service.get_webhook(webhook_id)
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Queue the webhook for processing
        process_webhook_task.delay(webhook_id)
        
        return {"message": "Webhook queued for processing"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook {webhook_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")


# ============================================================================
# SMS Endpoints
# ============================================================================

@app.post("/elks/sms")
async def receive_sms_webhook(
    request: Request,
    sms_service: SMSService = Depends(get_sms_service)
):
    """Receive SMS webhook from 46elks."""
    try:
        # Parse form data from 46elks webhook
        form_data = await request.form()
        
        # Convert form data to dict and handle URL encoding
        sms_data = {}
        for key, value in form_data.items():
            if key == "from":
                sms_data["from_number"] = value
            elif key == "to":
                sms_data["to_number"] = value
            else:
                sms_data[key] = value
        
        # Create SMS webhook object
        sms_webhook = SMSWebhook(**sms_data)
        
        # Store SMS in DynamoDB
        sms_response = await sms_service.store_sms(sms_webhook)
        
        # Queue SMS for processing
        process_sms_task.delay(sms_response.id)
        
        # Generate automatic reply
        reply_message = sms_service.generate_reply_message(sms_webhook.message)
        
        logger.info(f"Received SMS from {sms_webhook.from_number}: {sms_webhook.message}")
        
        # Return the reply message in the response body (46elks will send this as SMS)
        return Response(
            content=reply_message,
            media_type="text/plain",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error processing SMS webhook: {e}")
        return Response(
            content="Error processing SMS",
            media_type="text/plain",
            status_code=500
        )


@app.get("/sms", response_model=List[SMSResponse])
async def list_sms(
    limit: int = 100,
    sms_service: SMSService = Depends(get_sms_service)
):
    """List all SMS messages."""
    try:
        return await sms_service.list_sms(limit=limit)
    except Exception as e:
        logger.error(f"Error listing SMS: {e}")
        raise HTTPException(status_code=500, detail="Failed to list SMS messages")


@app.get("/sms/{sms_id}", response_model=SMSResponse)
async def get_sms(
    sms_id: str,
    sms_service: SMSService = Depends(get_sms_service)
):
    """Get a specific SMS by ID."""
    try:
        sms = await sms_service.get_sms(sms_id)
        if not sms:
            raise HTTPException(status_code=404, detail="SMS not found")
        return sms
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting SMS {sms_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SMS")


@app.post("/sms/{sms_id}/reply")
async def send_sms_reply(
    sms_id: str,
    reply: SMSReply,
    sms_service: SMSService = Depends(get_sms_service)
):
    """Send a reply to an SMS."""
    try:
        # Get the original SMS
        sms = await sms_service.get_sms(sms_id)
        if not sms:
            raise HTTPException(status_code=404, detail="SMS not found")
        
        # Determine recipient number
        to_number = reply.to_number or sms.from_number
        
        # Queue the reply for sending
        send_sms_reply_task.delay(sms_id, reply.message, to_number)
        
        # Mark reply as sent in database
        await sms_service.mark_reply_sent(sms_id, reply.message)
        
        return {"message": "SMS reply queued for sending"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending SMS reply {sms_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send SMS reply")


@app.delete("/sms/{sms_id}")
async def delete_sms(
    sms_id: str,
    sms_service: SMSService = Depends(get_sms_service)
):
    """Delete an SMS."""
    try:
        success = await sms_service.delete_sms(sms_id)
        if not success:
            raise HTTPException(status_code=404, detail="SMS not found")
        return {"message": "SMS deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting SMS {sms_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete SMS")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
