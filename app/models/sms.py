from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SMSWebhook(BaseModel):
    """Model for incoming SMS webhook from 46elks."""
    id: str = Field(..., description="Unique ID of the message in 46elks systems")
    from_number: str = Field(..., alias="from", description="Sender phone number")
    to_number: str = Field(..., alias="to", description="Recipient phone number")
    message: str = Field(..., description="SMS message content")
    direction: str = Field(..., description="Message direction (incoming/outgoing)")
    created: str = Field(..., description="UTC timestamp when SMS was created")
    
    class Config:
        allow_population_by_field_name = True


class SMSResponse(BaseModel):
    """Model for SMS response data."""
    id: str = Field(..., description="Unique SMS ID")
    from_number: str = Field(..., description="Sender phone number")
    to_number: str = Field(..., description="Recipient phone number")
    message: str = Field(..., description="SMS message content")
    direction: str = Field(..., description="Message direction")
    created: datetime = Field(..., description="Creation timestamp")
    processed: bool = Field(default=False, description="Processing status")
    processed_at: Optional[datetime] = Field(default=None, description="Processing timestamp")
    reply_sent: bool = Field(default=False, description="Whether a reply was sent")
    reply_message: Optional[str] = Field(default=None, description="Reply message content")
    
    class Config:
        from_attributes = True


class SMSReply(BaseModel):
    """Model for SMS reply data."""
    message: str = Field(..., description="Reply message content")
    to_number: Optional[str] = Field(default=None, description="Recipient number (defaults to sender)")
