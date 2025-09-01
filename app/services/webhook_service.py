from typing import List, Optional
from app.services.dynamodb_service import DynamoDBService
from app.models.webhook import WebhookCreate, WebhookResponse, WebhookUpdate


class WebhookService:
    """Service for webhook business logic."""
    
    def __init__(self):
        self.db_service = DynamoDBService()
    
    async def initialize(self):
        """Initialize the service (create table if needed)."""
        await self.db_service.create_table_if_not_exists()
    
    async def create_webhook(self, webhook: WebhookCreate) -> WebhookResponse:
        """Create a new webhook."""
        webhook_data = webhook.dict()
        db_webhook = await self.db_service.create_webhook(webhook_data)
        return WebhookResponse(**db_webhook)
    
    async def get_webhook(self, webhook_id: str) -> Optional[WebhookResponse]:
        """Get a webhook by ID."""
        db_webhook = await self.db_service.get_webhook(webhook_id)
        if db_webhook:
            return WebhookResponse(**db_webhook)
        return None
    
    async def list_webhooks(self, limit: int = 100) -> List[WebhookResponse]:
        """List all webhooks."""
        db_webhooks = await self.db_service.list_webhooks(limit)
        return [WebhookResponse(**webhook) for webhook in db_webhooks]
    
    async def update_webhook(self, webhook_id: str, webhook_update: WebhookUpdate) -> Optional[WebhookResponse]:
        """Update a webhook."""
        # Filter out None values
        update_data = {k: v for k, v in webhook_update.dict().items() if v is not None}
        
        if not update_data:
            return await self.get_webhook(webhook_id)
        
        db_webhook = await self.db_service.update_webhook(webhook_id, update_data)
        if db_webhook:
            return WebhookResponse(**db_webhook)
        return None
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook."""
        return await self.db_service.delete_webhook(webhook_id)
    
    async def mark_webhook_processed(self, webhook_id: str) -> Optional[WebhookResponse]:
        """Mark a webhook as processed."""
        from datetime import datetime
        
        update_data = {
            'processed': True,
            'processed_at': datetime.utcnow().isoformat()
        }
        
        db_webhook = await self.db_service.update_webhook(webhook_id, update_data)
        if db_webhook:
            return WebhookResponse(**db_webhook)
        return None
