import os
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class Settings:
    """Application settings loaded from environment variables"""
    
    def __init__(self):
        # API Keys
        self.openai_api_key: Optional[str] = self._get_required_env("OPENAI_API_KEY")
        self.openai_model: str = self._get_env("OPENAI_MODEL", "gpt-4o-mini")
        
        self.weather_api_key: Optional[str] = self._get_required_env("WEATHER_API_KEY")
        self.weather_base_url: str = self._get_env("WEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5")
        
        self.google_gemini_api_key: Optional[str] = self._get_required_env("GOOGLE_GEMINI_API_KEY")
        self.google_gemini_model: str = self._get_env("GOOGLE_GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        # Application Configuration
        self.environment: str = self._get_env("ENVIRONMENT", "development")
        self.log_level: str = self._get_env("LOG_LEVEL", "INFO")
        self.debug: bool = self._get_env("DEBUG", "true").lower() == "true"
        
        # Database Configuration
        self.database_url: str = self._get_env("DATABASE_URL", "sqlite:///./command_logs.db")
        
        # ChromaDB Configuration
        self.chroma_persist_directory: str = self._get_env("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
        
        # Validate configuration
        self._validate_config()
    
    def _get_env(self, key: str, default: str = None) -> str:
        """Get environment variable with optional default"""
        return os.getenv(key, default)
    
    def _get_required_env(self, key: str) -> Optional[str]:
        """Get required environment variable"""
        value = os.getenv(key)
        if not value:
            logger.warning(f"Required environment variable {key} not set")
        return value
    
    def _validate_config(self):
        """Validate that required configuration is present"""
        missing_keys = []
        
        if not self.openai_api_key:
            missing_keys.append("OPENAI_API_KEY")
        if not self.weather_api_key:
            missing_keys.append("WEATHER_API_KEY")
        if not self.google_gemini_api_key:
            missing_keys.append("GOOGLE_GEMINI_API_KEY")
        
        if missing_keys:
            logger.warning(f"Missing API keys: {', '.join(missing_keys)}")
            logger.warning("Some features may not work without proper API configuration")
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    def get_api_keys_status(self) -> dict:
        """Get status of API key configuration"""
        return {
            "openai": bool(self.openai_api_key),
            "weather": bool(self.weather_api_key),
            "google_gemini": bool(self.google_gemini_api_key)
        }

# Global settings instance
settings = Settings()
