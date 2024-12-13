import sys

from loguru import logger
from datetime import datetime


class Logger:
    def __init__(self) -> None:
        current_date = datetime.now().strftime("%d.%m.%Y")
        self.path = f"logs/{current_date}.log"
        self.rotation = "1 day"
        self.retention = "1 month"
        self.level = "INFO"

    def init_logger(self):
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