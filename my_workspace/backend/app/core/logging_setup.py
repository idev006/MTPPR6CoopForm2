import sys
from loguru import logger

from app.core.config import get_logging_config


def setup_logging() -> None:
    cfg = get_logging_config().get("logging", {})
    level = cfg.get("level", "INFO")
    fmt = cfg.get("format", "{time} | {level} | {name}:{line} — {message}")
    colorize = cfg.get("colorize", False)

    logger.remove()

    # stdout (container logs)
    logger.add(sys.stdout, level=level, format=fmt, colorize=colorize)

    # file logs
    file_cfg = cfg.get("file", {})
    if app_log := file_cfg.get("app_log"):
        logger.add(
            app_log,
            level=level,
            format=fmt,
            rotation=file_cfg.get("rotation", "00:00"),
            retention=file_cfg.get("retention", "30 days"),
            enqueue=True,
        )
    if error_log := file_cfg.get("error_log"):
        logger.add(
            error_log,
            level="ERROR",
            format=fmt,
            rotation=file_cfg.get("rotation", "00:00"),
            retention=file_cfg.get("retention", "30 days"),
            enqueue=True,
        )
