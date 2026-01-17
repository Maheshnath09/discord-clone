"""
Application configuration using Pydantic settings.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    PROJECT_NAME: str = "Discord-like Chat App"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///./chat_app.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PRESENCE_PREFIX: str = "presence:"
    REDIS_PUBSUB_PREFIX: str = "pubsub:"
    
    # AWS S3 (optional, for production)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    S3_REGION: str = "us-east-1"
    USE_S3: bool = False
    
    # Supabase Storage (for avatars)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None  # Use service_role key for server-side uploads
    SUPABASE_BUCKET: str = "avatars"
    USE_SUPABASE: bool = False
    
    # File uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf", "text/plain", "application/zip"
    ]
    
    # OAuth (optional)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # CORS - Additional origins from environment (comma-separated)
    ALLOWED_ORIGINS: str = ""  # Comma-separated list of allowed origins
    
    # CORS
    # Include common dev origins and the docker-compose service hostnames so
    # requests from the frontend container (origin `http://frontend`) are allowed
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:31000",
        "http://frontend",
        "http://frontend:80",
    ]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    def get_cors_origins(self) -> List[str]:
        """Get all CORS origins including those from environment."""
        origins = list(self.CORS_ORIGINS)
        # Add FRONTEND_URL if not already included
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        # Add ALLOWED_ORIGINS (comma-separated from env)
        if self.ALLOWED_ORIGINS:
            for origin in self.ALLOWED_ORIGINS.split(","):
                origin = origin.strip()
                if origin and origin not in origins:
                    origins.append(origin)
        return origins
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Demo data
    AUTO_SEED_DEMO_DATA: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()



