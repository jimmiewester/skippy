import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # AWS Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # DynamoDB Configuration
    dynamodb_table_name: str = "skippy_webhooks"
    dynamodb_endpoint_url: Optional[str] = None  # For local development
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # Application Configuration
    app_name: str = "Skippy"
    debug: bool = False
    
    # 46elks SMS Configuration (Optional)
    elks_api_username: Optional[str] = None
    elks_api_password: Optional[str] = None
    elks_sms_from_number: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
