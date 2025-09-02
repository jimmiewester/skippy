import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # AWS Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # DynamoDB Configuration
    dynamodb_table_name: str = "skippy_webhooks"
    dynamodb_endpoint_url: Optional[str] = None  # For local development
    
    # Application Configuration
    app_name: str = "Skippy"
    debug: bool = False
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from environment
    )


# Global settings instance
settings = Settings()
