"""
Configuration Manager
Startup Growth Analytics System

Loads YAML configuration and CSV metadata files.
"""

from pathlib import Path
import yaml
import pandas as pd


class ConfigManager:
    """Loads and provides access to project configuration."""

    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)

        self.config = self._load_yaml("config.yaml")
        self.indicators = self._load_csv("indicators.csv")
        self.sources = self._load_csv("sources.csv")

    def _load_yaml(self, filename):
        filepath = self.config_dir / filename

        with open(filepath, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def _load_csv(self, filename):
        filepath = self.config_dir / filename
        return pd.read_csv(filepath)

    def get_config(self):
        return self.config

    def get_indicators(self):
        return self.indicators

    def get_sources(self):
        return self.sources


if __name__ == "__main__":

    config = ConfigManager()

    print(config.get_config())

    print(config.get_indicators().head())

    print(config.get_sources().head())