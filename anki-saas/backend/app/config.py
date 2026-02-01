from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://anki:anki_secret@localhost:5432/anki_saas"
    anthropic_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
