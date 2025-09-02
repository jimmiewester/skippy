from pydantic import BaseModel, Field


class SMSWebhook(BaseModel):
    """Model for incoming SMS webhook from 46elks."""
    id: str = Field(..., description="Unique ID of the message in 46elks systems")
    from_number: str = Field(..., description="Sender phone number")
    to_number: str = Field(..., description="Recipient phone number")
    message: str = Field(..., description="SMS message content")
    direction: str = Field(..., description="Message direction (incoming/outgoing)")
    created: str = Field(..., description="UTC timestamp when SMS was created")
    
    class Config:
        allow_population_by_field_name = True
