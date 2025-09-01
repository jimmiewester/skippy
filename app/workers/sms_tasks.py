import logging
from datetime import datetime
from typing import Optional

from .celery_app import celery_app
from app.services.sms_service import SMSService
from app.models.sms import SMSWebhook

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_sms_task(self, sms_id: str):
    """Process an SMS asynchronously."""
    try:
        # Initialize service
        sms_service = SMSService()
        
        # Get the SMS
        sms = sms_service.get_sms(sms_id)
        if not sms:
            logger.error(f"SMS {sms_id} not found")
            return False
        
        # Process the SMS
        logger.info(f"Processing SMS {sms_id} from {sms.from_number}")
        
        # Generate automatic reply
        reply_message = sms_service.generate_reply_message(sms.message)
        
        # Mark SMS as processed
        sms_service.mark_sms_processed(sms_id)
        
        # Mark reply as sent
        sms_service.mark_reply_sent(sms_id, reply_message)
        
        logger.info(f"Successfully processed SMS {sms_id}")
        return {
            "sms_id": sms_id,
            "reply_message": reply_message,
            "processed": True
        }
        
    except Exception as exc:
        logger.error(f"Error processing SMS {sms_id}: {exc}")
        
        # Retry the task
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            logger.error(f"Max retries exceeded for SMS {sms_id}")
            return False


@celery_app.task(bind=True, max_retries=3)
def send_sms_reply_task(self, sms_id: str, reply_message: str, to_number: str):
    """Send an SMS reply asynchronously."""
    try:
        logger.info(f"Sending SMS reply to {to_number}: {reply_message}")
        
        # Here you would integrate with 46elks SMS API to send the reply
        # For now, we'll just log it
        logger.info(f"SMS Reply sent - To: {to_number}, Message: {reply_message}")
        
        # Mark reply as sent in database
        sms_service = SMSService()
        sms_service.mark_reply_sent(sms_id, reply_message)
        
        return {
            "sms_id": sms_id,
            "to_number": to_number,
            "reply_message": reply_message,
            "sent": True
        }
        
    except Exception as exc:
        logger.error(f"Error sending SMS reply {sms_id}: {exc}")
        
        # Retry the task
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            logger.error(f"Max retries exceeded for SMS reply {sms_id}")
            return False


@celery_app.task
def periodic_sms_cleanup_task():
    """Periodic task to clean up old processed SMS messages."""
    try:
        logger.info("Starting periodic SMS cleanup task")
        
        # Initialize service
        sms_service = SMSService()
        
        # Get all SMS messages
        sms_list = sms_service.list_sms(limit=1000)
        
        # Delete SMS messages older than 30 days that are processed
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        deleted_count = 0
        
        for sms in sms_list:
            if sms.processed:
                created_at = datetime.fromisoformat(sms.created.replace('Z', '+00:00'))
                if created_at < cutoff_date:
                    if sms_service.delete_sms(sms.id):
                        deleted_count += 1
        
        logger.info(f"Periodic SMS cleanup completed. Deleted {deleted_count} old SMS messages")
        return deleted_count
        
    except Exception as exc:
        logger.error(f"Error in periodic SMS cleanup task: {exc}")
        return 0
