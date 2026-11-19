from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url_async: str
    database_url_sync: str
    sh_client_id: str | None = None
    sh_client_secret: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
