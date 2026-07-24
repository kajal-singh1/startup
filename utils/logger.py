"""
Logging Utility
Startup Growth Analytics System

Provides centralized logging for all project modules.
"""

import logging
from pathlib import Path


class ProjectLogger:
    """Creates and manages project loggers."""

    def __init__(self, log_file="logs/project.log"):

        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("StartupGrowthAnalytics")

        # Avoid duplicate handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        # File Handler
        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


if __name__ == "__main__":

    logger = ProjectLogger().get_logger()

    logger.info("Logger initialized successfully.")

    logger.warning("This is a warning.")

    logger.error("This is a sample error.")