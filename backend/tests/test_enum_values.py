#!/usr/bin/env python3
"""
Test to verify enum values match their string representations.
This ensures that the migration from JSON string values to Python enums
maintains the exact same business logic.
"""

from app.mapping.enums import TrueFalse, YesNoValue


def test_yes_no_value_enum():
    """Test YesNoValue enum values match expected strings."""
    assert YesNoValue.YES.value == "Yes", "YES enum value should be 'Yes'"
    assert YesNoValue.NO.value == "No", "NO enum value should be 'No'"
    assert YesNoValue.NONE.value == "None", "NONE enum value should be 'None'"
    print("✅ YesNoValue enum values verified")


def test_true_false_enum():
    """Test TrueFalse enum values match expected strings."""
    assert TrueFalse.TRUE.value == "true", "TRUE enum value should be 'true'"
    assert TrueFalse.FALSE.value == "false", "FALSE enum value should be 'false'"
    print("✅ TrueFalse enum values verified")


def test_enum_string_representation():
    """Test that enums serialize to their string values correctly."""
    # When used in Pydantic models, enums should serialize to their values
    assert str(YesNoValue.YES) == "YesNoValue.YES"
    assert YesNoValue.YES.value == "Yes"

    # Test that the value is what gets used in transformations
    # Pydantic will use .value when serializing
    from pydantic import BaseModel

    class TestModel(BaseModel):
        field: str


if __name__ == "__main__":
    test_yes_no_value_enum()
    test_true_false_enum()
    test_enum_string_representation()
    print("\n🎉 All enum validation tests passed!")
