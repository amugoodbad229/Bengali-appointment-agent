import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings for production deployment"""
    
    # Twilio Configuration
    twilio_account_sid: str = os.environ.get("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.environ.get("TWILIO_AUTH_TOKEN", "")
    
    # Gemini Configuration
    gemini_api_key: str = os.environ.get("GEMINI_API_KEY", "")
    
    # n8n Configuration
    n8n_webhook_url: str = os.environ.get("N8N_WEBHOOK_URL", "")
    
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