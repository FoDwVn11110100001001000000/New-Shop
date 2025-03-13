"""
This module contains functions for logging.
"""

import sys

from datetime import datetime
from loguru import logger


class Logger:
    """
    Class for logging.
    """
    def __init__(self) -> None:
        current_date = datetime.now().strftime("%d.%m.%Y")
        self.path = f"logs/{current_date}.log"
        self.rotation = "1 day"
        self.retention = "1 month"
        self.level = "INFO"

    def init_logger(self):
        """
        Initializes logger with the specified path, rotation, retention, and level.

        Returns logger object.
        """

        logger.remove()
        logger.add(
            self.path,
            rotation=self.rotation,
            retention=self.retention,
            level=self.level
            )

        logger.add(
            sys.stdout,
            level=self.level
        )
        return logger


log_instance = Logger()
log = log_instance.init_logger()
