"""Tests for Pydantic Settings configuration."""

import os
from unittest.mock import patch

import pytest


def test_config_imports():
    """Test that Config can be imported and is a Pydantic BaseSettings."""
    from pydantic_settings import BaseSettings

    from app.config import Config, config

    # Verify Config is a Pydantic BaseSettings subclass
    assert issubclass(Config, BaseSettings)

    # Verify config instance is created
    assert isinstance(config, Config)


def test_config_default_values():
    """Test that default values are set correctly."""
    from app.config import Config

    config = Config()

    assert config.LOG_LEVEL == "INFO"
    assert config.MODERATION_SECRET == "secret"


def test_config_env_variable_loading():
    """Test that environment variables are loaded correctly."""
    from app.config import Config

    with patch.dict(
        os.environ,
        {
            "SQL_CONN_STRING": "test_sql_connection",
            "LOG_LEVEL": "DEBUG",
            "API_KEY": "test_api_key",
        },
        clear=False,
    ):
        config = Config()

        assert config.SQL_CONN_STRING == "test_sql_connection"
        assert config.LOG_LEVEL == "DEBUG"
        assert config.API_KEY == "test_api_key"


def test_config_moderation_secret_fallback():
    """Test that MODERATION_SECRET falls back to API_KEY when not set."""
    from app.config import Config

    # Test 1: MODERATION_SECRET not set, API_KEY is set -> use API_KEY
    with patch.dict(
        os.environ,
        {
            "API_KEY": "my_api_key",
        },
        clear=False,
    ):
        config = Config()
        assert config.MODERATION_SECRET == "my_api_key"

    # Test 2: MODERATION_SECRET is set explicitly -> use explicit value
    with patch.dict(
        os.environ,
        {
            "API_KEY": "my_api_key",
            "MODERATION_SECRET": "my_moderation_secret",
        },
        clear=False,
    ):
        config = Config()
        assert config.MODERATION_SECRET == "my_moderation_secret"

    # Test 3: Neither set -> use default "secret"
    env_without_keys = {k: v for k, v in os.environ.items() if k not in ["API_KEY", "MODERATION_SECRET"]}
    with patch.dict(os.environ, env_without_keys, clear=True):
        config = Config()
        assert config.MODERATION_SECRET == "secret"

    # Test 4: MODERATION_SECRET explicitly set to "secret" with API_KEY -> use "secret"
    # This test ensures the validator doesn't override an explicit "secret" value
    with patch.dict(
        os.environ,
        {
            "API_KEY": "my_api_key",
            "MODERATION_SECRET": "secret",
        },
        clear=False,
    ):
        config = Config()
        assert config.MODERATION_SECRET == "secret"  # Should not be overridden by API_KEY


def test_config_nullable_fields():
    """Test that nullable fields work correctly."""
    from app.config import Config

    config = Config()

    # These should all be None by default
    assert config.SQL_CONN_STRING is None
    assert config.MONGODB_CONN_STRING is None
    assert config.OPENAI_API_KEY is None
    assert config.NOCODB_BASE_URL is None
    assert config.AUTH0_DOMAIN is None


def test_config_case_sensitivity():
    """Test that environment variables are case-sensitive."""
    from app.config import Config

    with patch.dict(
        os.environ,
        {
            "api_key": "lowercase_key",  # lowercase should not work
            "API_KEY": "uppercase_key",  # uppercase should work
        },
        clear=False,
    ):
        config = Config()
        # Should use the uppercase version
        assert config.API_KEY == "uppercase_key"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
