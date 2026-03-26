from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    DANBOORU_LOGIN: str
    DANBOORU_API_KEY: SecretStr
    SAUCENAO_API_KEY: SecretStr
    DANBOORU_DOMAIN: str
    USELESS_HOSTS: list[str]
    USER_AGENT: str
    DAILY_LIMIT: int = 10
    OWNER_ID: int
    
    @property
    def database_url(self) -> str:
        return "sqlite+aiosqlite:///./database.db"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()