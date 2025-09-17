import logging
from typing import Optional

_APP_LOGGER_NAME = "app"

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return an application logger under the `app` namespace.

    Example:
        logger = get_logger("api.routes")  # -> app.api.routes
    """
    full_name = _APP_LOGGER_NAME if not name else f"{_APP_LOGGER_NAME}.{name}"
    return logging.getLogger(full_name)


