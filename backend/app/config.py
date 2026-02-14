from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "LLMQuant News"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    # Database
    DATABASE_URL: str = "sqlite:///../data/llmquant.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    AZURE_API_KEY: Optional[str] = None
    AZURE_API_BASE: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Feishu
    FEISHU_APP_ID: Optional[str] = None
    FEISHU_APP_SECRET: Optional[str] = None
    FEISHU_ENCRYPT_KEY: Optional[str] = None
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None
    SMTP_TLS: bool = True
    
    # Default LLM
    DEFAULT_LLM_MODEL: str = "deepseek-chat"
    
    # Crawler
    CRAWLER_INTERVAL: int = 300  # 5 minutes
    MAX_CONCURRENT_CRAWLERS: int = 5
    
    # Cost Management
    ENABLE_COST_TRACKING: bool = True
    MONTHLY_BUDGET_USD: float = 100.0
    
    # Push
    ENABLE_FEISHU_PUSH: bool = False
    ENABLE_EMAIL_PUSH: bool = False
    SCORE_THRESHOLD: float = 60.0
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
