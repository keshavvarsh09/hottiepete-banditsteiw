from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    fish_api_key: str = ""
    fish_voice_a: str = ""
    fish_voice_b: str = ""

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    backend_base_url: str = "http://localhost:8000"

    database_url: str = "sqlite:///./data/app.db"
    assets_dir: str = "./assets"
    renders_dir: str = "./renders"


settings = Settings()
