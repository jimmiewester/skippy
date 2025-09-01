import uuid
from datetime import datetime
from typing import Optional


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO format."""
    return dt.isoformat()


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse datetime from ISO format string."""
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        return None


def validate_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Validate webhook signature (placeholder implementation)."""
    # This is a placeholder - implement actual signature validation
    # based on your webhook provider's requirements
    return True
