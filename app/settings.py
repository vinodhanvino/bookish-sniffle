from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path

PARENT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = PARENT_DIR / ".env"


class Settings(BaseSettings):
    HOST: str = "hello"
    PORT: int = 0
    DATABASE: str = ""
    USER: str = ""
    PASSWORD: str = ""
    POOL_SIZE: int = 0
    MAX_OVERFLOW: int = 0
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    SPIRIX_POST: int = 0
    SPIRIX_HOST: str = ""
    OUTLET_LIST_DEFAULT_LIMIT: int = 50
    OUTLET_LIST_MAX_LIMIT: int = 200
    MASTER_KSBCL_JSON_PATH: str = (
        r"D:\office\code\spirix resource\processed\processed\master-ksbcl.json"
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra='ignore'
    )


settings = Settings()
print(settings)