import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from .celery_app import celery_app
from app.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_webhook_task(self, webhook_id: str):
    """Process a webhook asynchronously."""
    try:
        # Initialize service
        webhook_service = WebhookService()
        
        # Get the webhook
        webhook = webhook_service.get_webhook(webhook_id)
        if not webhook:
            logger.error(f"Webhook {webhook_id} not found")
            return False
        
        # Process the webhook based on event type
        logger.info(f"Processing webhook {webhook_id} of type {webhook.event_type}")
        
        # Example processing logic - you can customize this
        if webhook.event_type == "user.created":
            process_user_created_webhook(webhook)
        elif webhook.event_type == "payment.completed":
            process_payment_webhook(webhook)
        else:
            process_generic_webhook(webhook)
        
        # Mark as processed
        webhook_service.mark_webhook_processed(webhook_id)
        
        logger.info(f"Successfully processed webhook {webhook_id}")
        return True
        
    except Exception as exc:
        logger.error(f"Error processing webhook {webhook_id}: {exc}")
        
        # Retry the task
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            logger.error(f"Max retries exceeded for webhook {webhook_id}")
            return False


@celery_app.task
def periodic_cleanup_task():
    """Periodic task to clean up old processed webhooks."""
    try:
        logger.info("Starting periodic cleanup task")
        
        # Initialize service
        webhook_service = WebhookService()
        
        # Get all webhooks
        webhooks = webhook_service.list_webhooks(limit=1000)
        
        # Delete webhooks older than 30 days that are processed
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        deleted_count = 0
        
        for webhook in webhooks:
            if webhook.processed:
                created_at = datetime.fromisoformat(webhook.created_at.replace('Z', '+00:00'))
                if created_at < cutoff_date:
                    if webhook_service.delete_webhook(webhook.id):
                        deleted_count += 1
        
        logger.info(f"Periodic cleanup completed. Deleted {deleted_count} old webhooks")
        return deleted_count
        
    except Exception as exc:
        logger.error(f"Error in periodic cleanup task: {exc}")
        return 0


def process_user_created_webhook(webhook):
    """Process user.created webhook events."""
    logger.info(f"Processing user.created webhook: {webhook.payload}")
    # Add your user creation logic here
    # Example: send welcome email, create user profile, etc.


def process_payment_webhook(webhook):
    """Process payment.completed webhook events."""
    logger.info(f"Processing payment.completed webhook: {webhook.payload}")
    # Add your payment processing logic here
    # Example: update subscription status, send receipt, etc.


def process_generic_webhook(webhook):
    """Process generic webhook events."""
    logger.info(f"Processing generic webhook: {webhook.event_type} - {webhook.payload}")
    # Add your generic webhook processing logic here
