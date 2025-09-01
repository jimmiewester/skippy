import boto3
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError

from app.config import settings


class DynamoDBService:
    """Service for DynamoDB operations."""
    
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            endpoint_url=settings.dynamodb_endpoint_url
        )
        self.table = self.dynamodb.Table(settings.dynamodb_table_name)
    
    async def create_table_if_not_exists(self):
        """Create the DynamoDB table if it doesn't exist."""
        try:
            self.table.load()
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Table doesn't exist, create it
                self.dynamodb.create_table(
                    TableName=settings.dynamodb_table_name,
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
                self.table.meta.client.get_waiter('table_exists').wait(
                    TableName=settings.dynamodb_table_name
                )
    
    async def create_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new webhook record."""
        webhook_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        item = {
            'id': webhook_id,
            'event_type': webhook_data['event_type'],
            'payload': webhook_data['payload'],
            'source': webhook_data['source'],
            'headers': webhook_data.get('headers'),
            'processed': False,
            'created_at': now,
            'updated_at': now
        }
        
        self.table.put_item(Item=item)
        return item
    
    async def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """Get a webhook by ID."""
        try:
            response = self.table.get_item(Key={'id': webhook_id})
            return response.get('Item')
        except ClientError:
            return None
    
    async def list_webhooks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all webhooks."""
        try:
            response = self.table.scan(Limit=limit)
            return response.get('Items', [])
        except ClientError:
            return []
    
    async def update_webhook(self, webhook_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a webhook."""
        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}
        
        for key, value in update_data.items():
            if value is not None:
                attr_name = f"#{key}"
                attr_value = f":{key}"
                update_expression += f"{attr_name} = {attr_value}, "
                expression_attribute_names[attr_name] = key
                expression_attribute_values[attr_value] = value
        
        # Always update the updated_at timestamp
        update_expression += "#updated_at = :updated_at"
        expression_attribute_names["#updated_at"] = "updated_at"
        expression_attribute_values[":updated_at"] = datetime.utcnow().isoformat()
        
        try:
            response = self.table.update_item(
                Key={'id': webhook_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )
            return response.get('Attributes')
        except ClientError:
            return None
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook."""
        try:
            self.table.delete_item(Key={'id': webhook_id})
            return True
        except ClientError:
            return False
