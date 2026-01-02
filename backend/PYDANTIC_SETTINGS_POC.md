# Pydantic Settings POC

This document describes the Proof of Concept (POC) implementation of Pydantic Settings for configuration management in the CoLD backend.

## Overview

The backend configuration has been migrated from a simple dataclass to [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/), providing better type safety, automatic environment variable loading, and validation.

## Changes Made

### 1. Dependency Addition
```bash
uv add pydantic-settings
```

### 2. Configuration Migration

**Before** (`app/config.py` using dataclass):
```python
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    SQL_CONN_STRING: str | None = os.getenv("SQL_CONN_STRING")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    # ... more fields
```

**After** (`app/config.py` using Pydantic Settings):
```python
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    """Application settings using Pydantic Settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    SQL_CONN_STRING: str | None = None
    LOG_LEVEL: str = "INFO"
    # ... more fields
    
    @model_validator(mode="after")
    def set_moderation_secret_fallback(self) -> "Config":
        """Custom validator for MODERATION_SECRET fallback logic."""
        if self.MODERATION_SECRET == "secret" and self.API_KEY:
            self.MODERATION_SECRET = self.API_KEY
        return self

config = Config()
```

## Key Benefits

### 1. **Automatic Environment Variable Loading**
No need for manual `os.getenv()` calls. Pydantic Settings automatically reads from environment variables and `.env` files.

### 2. **Type Validation**
Built-in validation ensures configuration values match their type hints:
```python
# This will raise a validation error if LOG_LEVEL is not a string
config = Config(LOG_LEVEL=123)  # ValidationError!
```

### 3. **Better IDE Support**
Full type hints provide better autocomplete and type checking:
```python
config.SQL_CONN_STRING  # IDE knows this is str | None
config.LOG_LEVEL        # IDE knows this is str
```

### 4. **Custom Validators**
Complex validation logic can be implemented with `@model_validator`:
```python
@model_validator(mode="after")
def set_moderation_secret_fallback(self) -> "Config":
    """Set MODERATION_SECRET to API_KEY if not explicitly provided."""
    if self.MODERATION_SECRET == "secret" and self.API_KEY:
        self.MODERATION_SECRET = self.API_KEY
    return self
```

### 5. **No More python-dotenv**
Pydantic Settings has built-in `.env` file reading, eliminating the need for `python-dotenv`.

## Usage Examples

### Reading Configuration Values
```python
from app.config import config

# Access configuration values
db_conn = config.SQL_CONN_STRING
log_level = config.LOG_LEVEL
```

### Creating Custom Configurations (for testing)
```python
from app.config import Config

# Override specific values
test_config = Config(
    SQL_CONN_STRING="postgresql://test:test@localhost/testdb",
    LOG_LEVEL="DEBUG"
)
```

### Environment Variable Precedence
1. Environment variables (highest priority)
2. `.env` file
3. Default values in code (lowest priority)

```bash
# In shell
export LOG_LEVEL=DEBUG

# In .env file
LOG_LEVEL=INFO

# In code
LOG_LEVEL: str = "WARNING"

# Result: "DEBUG" (environment variable wins)
```

## Testing

Comprehensive tests have been added in `tests/test_config_settings.py`:

```bash
uv run pytest tests/test_config_settings.py -v
```

Tests cover:
- Configuration imports and instance creation
- Default values
- Environment variable loading
- Custom validator logic (MODERATION_SECRET fallback)
- Nullable fields
- Case sensitivity

## Demo Script

Run the demo to see all features in action:

```bash
uv run python demo_pydantic_settings.py
```

The demo shows:
- Default values
- Environment variable loading
- Fallback logic
- Type validation
- Settings configuration

## Migration Guide for Other Codebases

If you want to apply this pattern to other parts of the codebase:

1. Install pydantic-settings: `uv add pydantic-settings`
2. Replace dataclass with `BaseSettings`
3. Add `model_config = SettingsConfigDict(...)`
4. Remove manual `os.getenv()` calls - just declare fields with defaults
5. Use `@model_validator` for complex validation logic
6. Update imports from `Config` class to `config` instance

## References

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Pydantic BaseSettings API Reference](https://docs.pydantic.dev/latest/api/pydantic_settings/)

## Notes

- The POC maintains backward compatibility - all existing code continues to work
- No breaking changes to the API
- Environment variables are case-sensitive (matches the original behavior)
- The singleton `config` instance is still exported for use throughout the codebase
