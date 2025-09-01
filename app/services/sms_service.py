import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.services.dynamodb_service import DynamoDBService
from app.models.sms import SMSWebhook, SMSResponse, SMSReply


class SMSService:
    """Service for SMS business logic."""
    
    def __init__(self):
        self.db_service = DynamoDBService()
        self.sms_table_name = "skippy_sms"
    
    async def initialize(self):
        """Initialize the service (create table if needed)."""
        await self._create_sms_table_if_not_exists()
    
    async def _create_sms_table_if_not_exists(self):
        """Create the SMS DynamoDB table if it doesn't exist."""
        try:
            # Create a temporary table reference to check if it exists
            temp_table = self.db_service.dynamodb.Table(self.sms_table_name)
            temp_table.load()
        except Exception as e:
            if "ResourceNotFoundException" in str(e):
                # Table doesn't exist, create it
                self.db_service.dynamodb.create_table(
                    TableName=self.sms_table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'id',
                            'KeyType': 'HASH'  # Partition key
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'id',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                # Wait for table to be created
                self.db_service.dynamodb.meta.client.get_waiter('table_exists').wait(
                    TableName=self.sms_table_name
                )
    
    async def store_sms(self, sms_webhook: SMSWebhook) -> SMSResponse:
        """Store an incoming SMS in DynamoDB."""
        # Parse the created timestamp
        created_dt = datetime.fromisoformat(sms_webhook.created.replace('Z', '+00:00'))
        
        sms_data = {
            'id': sms_webhook.id,
            'from_number': sms_webhook.from_number,
            'to_number': sms_webhook.to_number,
            'message': sms_webhook.message,
            'direction': sms_webhook.direction,
            'created': created_dt.isoformat(),
            'processed': False,
            'processed_at': None,
            'reply_sent': False,
            'reply_message': None
        }
        
        # Store in DynamoDB
        table = self.db_service.dynamodb.Table(self.sms_table_name)
        table.put_item(Item=sms_data)
        
        return SMSResponse(**sms_data)
    
    async def get_sms(self, sms_id: str) -> Optional[SMSResponse]:
        """Get an SMS by ID."""
        try:
            table = self.db_service.dynamodb.Table(self.sms_table_name)
            response = table.get_item(Key={'id': sms_id})
            item = response.get('Item')
            if item:
                return SMSResponse(**item)
            return None
        except Exception:
            return None
    
    async def list_sms(self, limit: int = 100) -> List[SMSResponse]:
        """List all SMS messages."""
        try:
            table = self.db_service.dynamodb.Table(self.sms_table_name)
            response = table.scan(Limit=limit)
            items = response.get('Items', [])
            return [SMSResponse(**item) for item in items]
        except Exception:
            return []
    
    async def mark_sms_processed(self, sms_id: str) -> Optional[SMSResponse]:
        """Mark an SMS as processed."""
        try:
            table = self.db_service.dynamodb.Table(self.sms_table_name)
            response = table.update_item(
                Key={'id': sms_id},
                UpdateExpression="SET processed = :processed, processed_at = :processed_at",
                ExpressionAttributeValues={
                    ':processed': True,
                    ':processed_at': datetime.utcnow().isoformat()
                },
                ReturnValues="ALL_NEW"
            )
            return SMSResponse(**response.get('Attributes'))
        except Exception:
            return None
    
    async def mark_reply_sent(self, sms_id: str, reply_message: str) -> Optional[SMSResponse]:
        """Mark that a reply was sent for an SMS."""
        try:
            table = self.db_service.dynamodb.Table(self.sms_table_name)
            response = table.update_item(
                Key={'id': sms_id},
                UpdateExpression="SET reply_sent = :reply_sent, reply_message = :reply_message",
                ExpressionAttributeValues={
                    ':reply_sent': True,
                    ':reply_message': reply_message
                },
                ReturnValues="ALL_NEW"
            )
            return SMSResponse(**response.get('Attributes'))
        except Exception:
            return None
    
    async def delete_sms(self, sms_id: str) -> bool:
        """Delete an SMS."""
        try:
            table = self.db_service.dynamodb.Table(self.sms_table_name)
            table.delete_item(Key={'id': sms_id})
            return True
        except Exception:
            return False
    
    def generate_reply_message(self, original_message: str) -> str:
        """Generate an automatic reply message based on the original SMS."""
        # Simple auto-reply logic - you can customize this
        message_lower = original_message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! Thanks for your message. We'll get back to you soon."
        elif "help" in message_lower:
            return "Need help? Contact our support team at support@example.com"
        elif "status" in message_lower:
            return "Your request is being processed. We'll update you shortly."
        else:
            return "Thank you for your message. We've received it and will respond shortly."
