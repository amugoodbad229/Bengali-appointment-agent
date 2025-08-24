import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings for production deployment"""
    # Twilio Configuration
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None

    # Gemini Configuration
    gemini_api_key: str | None = None

    # n8n Configuration
    n8n_webhook_url: str | None = None

    # Server Configuration
    port: int = int(os.environ.get("PORT", 8000))
    environment: str = os.environ.get("RAILWAY_ENVIRONMENT", "production")

    # Railway Configuration
    railway_project_id: Optional[str] = os.environ.get("RAILWAY_PROJECT_ID")
    railway_service_id: Optional[str] = os.environ.get("RAILWAY_SERVICE_ID")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings for production deployment"""
    
    # Twilio Configuration
    twilio_account_sid: str
    twilio_auth_token: str
    
    # Gemini Configuration
    gemini_api_key: str
    
    # n8n Configuration
    n8n_webhook_url: str
    
    # Server Configuration
    port: int = int(os.environ.get("PORT", 8000))
    environment: str = os.environ.get("RAILWAY_ENVIRONMENT", "production")
    
    # Railway Configuration
    railway_project_id: Optional[str] = os.environ.get("RAILWAY_PROJECT_ID")
    railway_service_id: Optional[str] = os.environ.get("RAILWAY_SERVICE_ID")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()