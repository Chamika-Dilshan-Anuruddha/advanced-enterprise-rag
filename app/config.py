from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Use SecretStr to prevent sensitive data from leaking into logs
    GROQ_API_KEY: SecretStr
    QDRANT_API_KEY: SecretStr
    QDRANT_CLUSTER_ENDPOINT: SecretStr
    QDRANT_COLLECITON: str = "enterpirse_rag"
    RAW_BUCKET: str = "dmtepress-rag-raw"
    PROCESSED_BUCKET: str = "dmtepress-rag-processed"

    LOGFIRE_TONEN: SecretStr

    LANGSMITH_TRACING: SecretStr
    LANGSMITH_ENDPOINT: SecretStr
    LANGSMITH_API_KEY: SecretStr
    LANGSMITH_PROJECT: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

