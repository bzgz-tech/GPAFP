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
    
    # LLM Settings
    # 推荐使用 DeepSeek (深度求索) 或 Moonshot (Kimi)，兼容 OpenAI 格式且国内可用
    llm_api_key: str = "" 
    llm_base_url: str = "" # 示例: DeepSeek API 地址
    llm_model: str = "" # 示例: deepseek-chat, gpt-3.5-turbo
    llm_chat_path: str = "chat/completions" # 对话接口路径
    
    
    model_config = SettingsConfigDict(env_file=None, extra="ignore")


settings = Settings()
