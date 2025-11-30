"""
Configuration loader for the web scraper
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger


class Config:
    """Load and manage scraper configuration"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)

        logger.info(f"Configuration loaded from: {self.config_path}")

    def get(self, key: str, default=None):
        """Get configuration value by dot-notation key"""
        keys = key.split('.')
        value = self.data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default

        return value

    def __getitem__(self, key: str):
        """Allow dict-like access"""
        return self.data[key]

    def __contains__(self, key: str):
        """Check if key exists"""
        return key in self.data
