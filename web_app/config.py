"""
Centralized configuration management for NVIDIA Course Advisor
Loads settings from environment variables with sensible defaults
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


def get_env(key: str, default: str = None, required: bool = False) -> str:
    """Get environment variable with optional default and validation."""
    value = os.environ.get(key, default)
    if required and not value:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable."""
    value = os.environ.get(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int = 0) -> int:
    """Get integer environment variable."""
    try:
        return int(os.environ.get(key, default))
    except (TypeError, ValueError):
        return default


def get_env_float(key: str, default: float = 0.0) -> float:
    """Get float environment variable."""
    try:
        return float(os.environ.get(key, default))
    except (TypeError, ValueError):
        return default


class Config:
    """Application configuration loaded from environment variables."""

    # ==========================================================================
    # Flask Settings
    # ==========================================================================
    SECRET_KEY = get_env('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = get_env_bool('FLASK_DEBUG', False)
    HOST = get_env('FLASK_HOST', '0.0.0.0')
    PORT = get_env_int('FLASK_PORT', 5000)

    # Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = get_env_bool('SESSION_COOKIE_SECURE', False)  # Set True in production with HTTPS
    SESSION_LIFETIME_DAYS = get_env_int('SESSION_LIFETIME_DAYS', 7)

    # ==========================================================================
    # Database Settings
    # ==========================================================================
    # Default path relative to web_app directory
    _default_db_path = str(Path(__file__).parent.parent / 'pdf_ingestion_system' / 'nvidia_courses.db')
    DATABASE_PATH = get_env('DATABASE_PATH', _default_db_path)

    # ==========================================================================
    # NVIDIA NIM / LLM Settings
    # ==========================================================================
    # Switch to NVIDIA's hosted API
    OLLAMA_API_URL = get_env('OLLAMA_API_URL', 'https://integrate.api.nvidia.com/v1')
    OLLAMA_MODEL = get_env('OLLAMA_MODEL', 'meta/llama3-8b-instruct')
    
    # NVIDIA API Key
    NVIDIA_API_KEY = get_env('NVIDIA_API_KEY', )
    
    LLM_TEMPERATURE = get_env_float('LLM_TEMPERATURE', 0.2)
    LLM_TIMEOUT = get_env_int('LLM_TIMEOUT', 120)

    # ==========================================================================
    # Embedding Settings
    # ==========================================================================
    EMBEDDING_MODEL = get_env('EMBEDDING_MODEL', 'sentence-transformers/all-mpnet-base-v2')

    # ==========================================================================
    # RAG Retrieval Settings
    # ==========================================================================
    TOP_K_CHUNKS = get_env_int('TOP_K_CHUNKS', 6)
    CHUNK_OVERLAP = get_env_int('CHUNK_OVERLAP', 2)

    # ==========================================================================
    # Security Settings
    # ==========================================================================
    MIN_PASSWORD_LENGTH = get_env_int('MIN_PASSWORD_LENGTH', 8)
    MAX_LOGIN_ATTEMPTS = get_env_int('MAX_LOGIN_ATTEMPTS', 5)
    LOGIN_LOCKOUT_MINUTES = get_env_int('LOGIN_LOCKOUT_MINUTES', 15)

    # ==========================================================================
    # Rate Limiting Settings
    # ==========================================================================
    RATELIMIT_ENABLED = get_env_bool('RATELIMIT_ENABLED', True)
    RATELIMIT_STORAGE_URI = get_env('RATELIMIT_STORAGE_URI', 'memory://')
    RATELIMIT_DEFAULT = get_env('RATELIMIT_DEFAULT', '100 per minute')
    RATELIMIT_LOGIN = get_env('RATELIMIT_LOGIN', '5 per minute')
    RATELIMIT_REGISTER = get_env('RATELIMIT_REGISTER', '3 per minute')
    RATELIMIT_CHAT = get_env('RATELIMIT_CHAT', '20 per minute')

    # ==========================================================================
    # Gunicorn Production Server Settings
    # ==========================================================================
    GUNICORN_WORKERS = get_env_int('GUNICORN_WORKERS', 4)
    GUNICORN_WORKER_CLASS = get_env('GUNICORN_WORKER_CLASS', 'gevent')
    GUNICORN_TIMEOUT = get_env_int('GUNICORN_TIMEOUT', 180)
    GUNICORN_BIND = get_env('GUNICORN_BIND', '0.0.0.0:5000')
    GUNICORN_ACCESS_LOG = get_env('GUNICORN_ACCESS_LOG', '-')  # stdout
    GUNICORN_ERROR_LOG = get_env('GUNICORN_ERROR_LOG', '-')    # stderr
    GUNICORN_LOGLEVEL = get_env('GUNICORN_LOGLEVEL', 'info')

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return not cls.DEBUG

    @classmethod
    def validate(cls) -> list:
        """Validate configuration and return list of warnings."""
        warnings = []

        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            warnings.append("WARNING: Using default SECRET_KEY. Set a secure key in production!")

        if cls.is_production() and not cls.SESSION_COOKIE_SECURE:
            warnings.append("WARNING: SESSION_COOKIE_SECURE should be True in production with HTTPS")

        if not Path(cls.DATABASE_PATH).exists():
            warnings.append(f"WARNING: Database not found at {cls.DATABASE_PATH}")

        return warnings


# Create singleton instance
config = Config()
