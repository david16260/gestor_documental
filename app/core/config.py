from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # Aplicación
    app_name: str = Field("Gestor Documental", env="APP_NAME")
    app_env: str = Field("development", env="APP_ENV")
    debug: bool = Field(True, env="APP_DEBUG")

    # Seguridad
    secret_key: str = Field("change-me", env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Base de datos
    database_url: str = Field(
        "postgresql://postgres:12345@localhost:5432/gestor_documental",
        env="DATABASE_URL",
    )

    # Archivos / uploads
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    upload_dir: Path = base_dir / "uploads"
    max_upload_size: int = Field(10 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 10 MB
    allowed_extensions: Tuple[str, ...] = Field(
        (".pdf", ".docx", ".xlsx", ".png", ".jpg", ".trd", ".ccd"),
        env="ALLOWED_EXT",
    )

    # CORS
    allowed_origins: List[str] = Field(default_factory=list, env="ALLOWED_ORIGINS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(exist_ok=True, parents=True)
    return settings
