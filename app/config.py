from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "INTAKE_BOT_"}

    app_name: str = "Office Hours Intake Bot"
    model_path: Path = Path("models/qwen2.5-3b")
    max_turns: int = 10
    host: str = "0.0.0.0"
    port: int = 8000
    chroma_db_path: Path = Path("chroma_db")
    rag_corpus_path: Path = Path("rag-corpus")
    rag_top_k: int = 3


settings = Settings()
