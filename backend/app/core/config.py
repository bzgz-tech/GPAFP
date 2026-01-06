from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv


env_candidates = [
    Path(__file__).resolve().parents[2] / ".env",
    Path(__file__).resolve().parents[3] / ".env",
]
for p in env_candidates:
    if p.exists():
        load_dotenv(p, override=False)


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str = "123210"
    jwt_algorithm: str = "HS256"
    debug: bool = True
    project_name: str = "GPAFP API"
    api_v1_str: str = ""
    backend_cors_origins: list[str] = []
    access_token_expire_minutes: int = 60
    model_config = SettingsConfigDict(env_file=None)


settings = Settings()
