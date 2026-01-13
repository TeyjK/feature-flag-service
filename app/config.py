from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    environment: str
    log_level: str
    rate_limit_per_minute: int

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()