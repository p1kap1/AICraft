"""全局配置"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "AICraft"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production-32-chars-min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # 数据库
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/aicraft"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    DEFAULT_MODEL: str = "gpt-4o-mini"

    # 文件存储
    UPLOAD_DIR: str = "./uploads"

    class Config:
        env_file = ".env"


settings = Settings()
