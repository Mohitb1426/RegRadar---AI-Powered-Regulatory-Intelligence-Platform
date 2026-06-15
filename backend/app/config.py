"""
Application configuration using Pydantic Settings
Loads from environment variables
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment"""

    # Application
    app_name: str = "RegRadar API"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    port: int = Field(default=8000, alias="PORT")

    # Database
    database_url: str = Field(..., alias="DATABASE_URL")

    # JWT Authentication
    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = Field(default=168, alias="JWT_EXPIRE_HOURS")  # 7 days

    # AWS Bedrock (Claude)
    aws_access_key_id: str = Field(..., alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., alias="AWS_SECRET_ACCESS_KEY")
    aws_session_token: str = Field(default="", alias="AWS_SESSION_TOKEN")
    aws_region: str = Field(default="ap-south-1", alias="AWS_REGION")
    aws_bedrock_model: str = Field(
        default="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        alias="AWS_BEDROCK_MODEL"
    )
    aws_bucket_name: str = Field(default="regradar-pdfs", alias="AWS_BUCKET_NAME")

    # Voyage AI (Embeddings)
    voyage_api_key: str = Field(..., alias="VOYAGE_API_KEY")

    # Pinecone (Vector DB)
    pinecone_api_key: str = Field(..., alias="PINECONE_API_KEY")
    pinecone_index: str = Field(default="regradar", alias="PINECONE_INDEX")

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
        "https://regradar.vercel.app"
    ]

    class Config:
        env_file = "../.env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export for easy import
settings = get_settings()
