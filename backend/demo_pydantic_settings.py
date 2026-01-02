"""
Demonstration of Pydantic Settings POC

This script demonstrates the key features of the Pydantic Settings implementation:
1. Automatic environment variable loading
2. Type validation
3. Default values
4. Custom validators
5. Case sensitivity
"""


from app.config import Config, config


def main():
    print("=" * 80)
    print("Pydantic Settings POC Demonstration")
    print("=" * 80)

    # Show the default config instance
    print("\n1. Default Config Instance:")
    print(f"   APP_NAME: {config.APP_NAME}")
    print(f"   API_VERSION: {config.API_VERSION}")
    print(f"   LOG_LEVEL: {config.LOG_LEVEL}")
    print(f"   MODERATION_SECRET: {config.MODERATION_SECRET}")

    # Show environment variable loading
    print("\n2. Environment Variable Loading:")
    print(f"   SQL_CONN_STRING: {config.SQL_CONN_STRING or '(not set)'}")
    print(f"   MONGODB_CONN_STRING: {config.MONGODB_CONN_STRING or '(not set)'}")
    print(f"   API_KEY: {config.API_KEY or '(not set)'}")

    # Demonstrate creating a custom config with environment variables
    print("\n3. Custom Config with Environment Variables:")
    # Create a custom config with explicit values (overriding any env vars)
    custom_config = Config(
        SQL_CONN_STRING="postgresql://custom:custom@localhost/customdb",
        LOG_LEVEL="DEBUG",
    )
    print(f"   SQL_CONN_STRING: {custom_config.SQL_CONN_STRING}")
    print(f"   LOG_LEVEL: {custom_config.LOG_LEVEL}")

    # Demonstrate the fallback logic for MODERATION_SECRET
    print("\n4. MODERATION_SECRET Fallback Logic:")
    print("   Scenario A: No API_KEY, no MODERATION_SECRET")
    config_a = Config()
    print(f"      MODERATION_SECRET: {config_a.MODERATION_SECRET}")

    print("\n   Scenario B: API_KEY set, no MODERATION_SECRET")
    config_b = Config(API_KEY="my_api_key_123")
    print(f"      API_KEY: {config_b.API_KEY}")
    print(f"      MODERATION_SECRET: {config_b.MODERATION_SECRET}")

    print("\n   Scenario C: Both API_KEY and MODERATION_SECRET set")
    config_c = Config(API_KEY="my_api_key_123", MODERATION_SECRET="my_custom_secret")
    print(f"      API_KEY: {config_c.API_KEY}")
    print(f"      MODERATION_SECRET: {config_c.MODERATION_SECRET}")

    # Show validation features
    print("\n5. Type Validation:")
    print("   Pydantic Settings provides automatic type validation.")
    print("   All fields have proper type hints and are validated on instantiation.")

    # Show the settings configuration
    print("\n6. Settings Configuration:")
    print("   - Reads from .env file (if exists)")
    print("   - Case-sensitive environment variables")
    print("   - Ignores extra environment variables")
    print("   - UTF-8 encoding for .env file")

    print("\n" + "=" * 80)
    print("POC Demonstration Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
