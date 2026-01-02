"""
Pydantic models for mapping configuration validation.

This module defines strict schemas for the transformation mapping JSON files,
providing type safety, validation, and better IDE support.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


class ConditionalMapping(BaseModel):
    """Configuration for conditional field mapping with fallback."""

    primary: str = Field(..., description="Primary field to use")
    fallback: str = Field(..., description="Fallback field if primary is not available")


class BooleanMapping(BaseModel):
    """Configuration for boolean field transformation."""

    source_field: str = Field(..., description="Source field name")
    true_value: str | bool = Field(..., description="Value representing true")
    false_value: str | bool = Field(..., description="Value representing false")


class ArrayOperation(BaseModel):
    """Configuration for array field operations."""

    operation: Literal["join"] = Field(..., description="Operation type (currently only 'join')")
    field: str = Field(..., description="Field name to extract from array items")
    separator: str = Field(..., description="Separator for join operation")


class NestedMapping(BaseModel):
    """Configuration for nested/related data mapping."""

    model_config = {"extra": "forbid"}

    source_array: str = Field(..., description="Source array field path")
    index: int | None = Field(default=None, description="Optional index to extract single item from array")
    mappings: dict[str, str] | None = Field(default=None, description="Direct field mappings for nested data")
    array_operations: dict[str, ArrayOperation] | None = Field(default=None, description="Operations to perform on arrays")
    conditional_mappings: dict[str, ConditionalMapping] | None = Field(default=None, description="Conditional mappings for nested data")
    boolean_mappings: dict[str, BooleanMapping] | None = Field(default=None, description="Boolean mappings for nested data")


class ComplexMapping(BaseModel):
    """Configuration for complex field transformations."""

    source_field: str = Field(..., description="Source field name")
    type: str = Field(..., description="Type of complex transformation")
    operation: str = Field(..., description="Specific operation to perform")


class UserFieldMapping(BaseModel):
    """Configuration for user field mapping."""

    model_config = {"populate_by_name": True}

    id: str = Field(..., alias="Last Modified By.id", description="User ID field mapping")
    email: str = Field(..., alias="Last Modified By.email", description="User email field mapping")
    name: str = Field(..., alias="Last Modified By.name", description="User name field mapping")


class UserMapping(BaseModel):
    """Configuration for user data transformation."""

    source_field: str = Field(..., description="Source field containing user data")
    user_fields: dict[str, str] = Field(..., description="Mapping of user fields")


class Mappings(BaseModel):
    """Container for all mapping configurations."""

    direct_mappings: dict[str, str] = Field(default_factory=dict, description="Direct field-to-field mappings")
    conditional_mappings: dict[str, ConditionalMapping] = Field(
        default_factory=dict, description="Conditional field mappings with fallbacks"
    )
    nested_mappings: dict[str, NestedMapping] = Field(default_factory=dict, description="Nested/related data mappings")
    complex_mappings: dict[str, ComplexMapping] = Field(default_factory=dict, description="Complex field transformations")
    user_mappings: dict[str, UserMapping] = Field(default_factory=dict, description="User data transformations")
    boolean_mappings: dict[str, BooleanMapping] = Field(default_factory=dict, description="Boolean field transformations")


class PostProcessing(BaseModel):
    """Configuration for post-processing operations."""

    remove_null_values: bool = Field(default=False, description="Whether to remove null values from output")
    field_transformations: dict[str, Any] = Field(default_factory=dict, description="Additional field transformations")


class MappingConfig(BaseModel):
    """
    Complete mapping configuration schema.

    This model validates the entire structure of a mapping JSON file,
    ensuring all required fields are present and correctly typed.
    """

    model_config = {
        "json_schema_extra": {
            "example": {
                "table_name": "Answers",
                "description": "Transformation rules for Answers table",
                "version": "1.0",
                "mappings": {
                    "direct_mappings": {"id": "CoLD_ID", "rank": "rank"},
                    "conditional_mappings": {"sort_date": {"primary": "updated_at", "fallback": "result_date"}},
                },
            }
        }
    }

    table_name: str = Field(..., description="Name of the table this mapping applies to")
    description: str = Field(..., description="Human-readable description of the mapping")
    version: str = Field(..., description="Version of the mapping configuration")
    mappings: Mappings = Field(..., description="All mapping configurations")
    post_processing: PostProcessing = Field(
        default_factory=PostProcessing, description="Optional post-processing configuration"
    )
