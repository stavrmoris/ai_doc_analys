from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Document Analyst API"
    database_url: str = "sqlite:///./app.db"
    qdrant_url: str = "http://qdrant:6333"
    storage_root: str = "/app/storage"
    embedding_model_name: str = "hashing-384"
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    chunk_size: int = 800
    chunk_overlap: int = 120
    retrieval_top_k: int = 20
    answer_top_k: int = 5
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
