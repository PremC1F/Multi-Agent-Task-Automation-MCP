from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "mcp_db"
    postgres_user: str = "mcp_user"
    postgres_password: str = "mcp_password"
    
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    
    api_port: int = 8000
    log_level: str = "INFO"
    environment: Literal["development", "test", "production"] = "development"
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
