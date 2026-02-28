from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Required
    OPENAI_API_KEY: str

    # Redis Connection
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Qdrant Connection
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # Collection Names
    COLLECTION_WISDOM: str = "wisdom"
    COLLECTION_WIRE: str = "wire"

    # Load from .env for local development (Docker uses environment vars)
    # extra="ignore": skip env vars meant for other services (e.g., GATEWAY_URL)
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
