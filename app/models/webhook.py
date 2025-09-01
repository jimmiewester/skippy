from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class WebhookBase(BaseModel):
    """Base webhook model with common fields."""
    event_type: str = Field(..., description="Type of webhook event")
    payload: Dict[str, Any] = Field(..., description="Webhook payload data")
    source: str = Field(..., description="Source of the webhook")
    headers: Optional[Dict[str, str]] = Field(default=None, description="HTTP headers")


class WebhookCreate(WebhookBase):
    """Model for creating a new webhook."""
    pass


class WebhookUpdate(BaseModel):
    """Model for updating a webhook."""
    event_type: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    processed: Optional[bool] = None


class WebhookResponse(WebhookBase):
    """Model for webhook response."""
    id: str = Field(..., description="Unique webhook ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    processed: bool = Field(default=False, description="Processing status")
    processed_at: Optional[datetime] = Field(default=None, description="Processing timestamp")
    
    class Config:
        from_attributes = True
