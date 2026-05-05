from functools import lru_cache
from pathlib import Path
import tomli
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # อ่านจาก .env / environment variables
    DATABASE_URL: str
    SECRET_KEY: str
    REFRESH_TOKEN_SECRET: str
    ENVIRONMENT: str = "development"

    # TOML config path - Default to dynamic discovery for robustness
    CONFIG_DIR: str = str(Path(__file__).parent.parent.parent.parent / "config")
    
    # Root data directory
    DATA_DIR: str = "data"

    # Static assets directory (fonts, icons, PDF templates)
    ASSETS_DIR: str = "app/assets"

    # Loan interest rates
    INTEREST_RATE_ORDINARY: float = 5.75

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Global settings instance
settings = get_settings()


def _load_toml(filename: str) -> dict:
    from loguru import logger
    path = Path(get_settings().CONFIG_DIR) / filename
    try:
        with open(path, "rb") as f:
            return tomli.load(f)
    except Exception as e:
        logger.error(f"Failed to load config {filename} at {path.absolute()}: {e}")
        raise e


@lru_cache
def get_app_config() -> dict:
    return _load_toml("app.toml")


@lru_cache
def get_security_config() -> dict:
    return _load_toml("security.toml")


@lru_cache
def get_logging_config() -> dict:
    return _load_toml("logging.toml")


@lru_cache
def get_storage_config() -> dict:
    return get_app_config().get("storage", {
        "max_size_mb": 10,
        "allowed_mimes": ["application/pdf"]
    })


@lru_cache
def get_validation_config() -> dict:
    return get_app_config().get("validation", {
        "enabled": True,
        "check_file_size": True,
        "check_file_type": True,
        "check_app_status": True
    })
