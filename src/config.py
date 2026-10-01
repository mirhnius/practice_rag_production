"""
Week 1 — application settings.

Centralizes every environment variable behind one typed object instead of
scattering `os.environ.get()` calls through the codebase. Pydantic reads
from `.env` (see `.env.example` for the full list of variables that will
eventually exist) and validates types for you.

As you move through later weeks, add one field per environment variable
you introduce — field names map to env vars case-insensitively (e.g.
`chunk_size: int` reads `CHUNK_SIZE`), so keep field names matching the
`.env.example` names below with underscores instead of shouting-case.
`get_settings()` is cached so the whole app shares one instance instead
of re-parsing `.env` on every call.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    debug: bool = False
    environment: str = "development"
    app_port: int = 8100

    arxiv_base_url: str
    postgres_database_url: str
    arxiv_search_category: str
    arxiv_max_results: int
    arxiv_rate_limit_delay: float
    arxiv_pdf_cache_dir: str

    # TODO (Week 3): opensearch_host: str, opensearch_index_name: str

    # TODO (Week 4): chunk_size: int, chunk_overlap_size: int,
    #   chunk_min_size: int, jina_api_key: str

    # TODO (Week 5): ollama_host: str, ollama_model: str

    # TODO (Week 6): redis_host: str, redis_port: int, redis_ttl_hours: int,
    #   langfuse_enabled: bool = False, langfuse_public_key: str = "",
    #   langfuse_secret_key: str = "", langfuse_host: str = ""

    # TODO (Week 7): telegram_bot_token: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
