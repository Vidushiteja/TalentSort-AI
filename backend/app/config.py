from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./talentsort.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,https://talent-sort-ai-livid.vercel.app"
    max_upload_mb: int = 10
    use_semantic_model: bool = True
    secret_key: str = "development-only-change-me"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
