"""Mapping configuration for Jurisdictions table."""

from app.schemas.mapping_schema import (
    BooleanMapping,
    MappingConfig,
    Mappings,
    PostProcessing,
)

JURISDICTIONS_MAPPING = MappingConfig(
    table_name="Jurisdictions",
    description="Transformation rules for converting Jurisdictions table from current NocoDB format to reference format",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "source_table": "source_table",
            "id": "id",
            "cold_id": "cold_id",
            "Name": "Name",
            "Alpha-3 Code": "Alpha_3_Code",
            "Type": "Type",
            "Region": "Region",
            "North-South Divide": "North_South_Divide",
            "Jurisdictional Differentiator": "Jurisdictional_Differentiator",
            "Record ID": "ncRecordId",
            "Created": "Created",
            "Last Modified": "Last_Modified",
            "Last Modified By.id": "updated_by",
            "Created By.id": "created_by",
            "Jurisdiction Summary": "Jurisdiction_Summary",
            "Legal Family": "Legal_Family",
            "Answer Coverage": "Answer_Coverage",
        },
        boolean_mappings={
            "Irrelevant?": BooleanMapping(
                source_field="Irrelevant_",
                true_value=True,
                false_value=False,
            ),
            "Done": BooleanMapping(
                source_field="Done",
                true_value=True,
                false_value=False,
            ),
        },
    ),
    post_processing=PostProcessing(
        remove_null_values=True,
    ),
)
