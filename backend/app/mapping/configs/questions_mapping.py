"""Mapping configuration for Questions table."""

from app.mapping.enums import Separator
from app.schemas.mapping_schema import (
    ArrayOperation,
    ConditionalMapping,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
)

QUESTIONS_MAPPING = MappingConfig(
    table_name="Questions",
    description="Transformation rules for converting Questions table from current NocoDB format to reference format",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "source_table": "source_table",
            "id": "CoLD_ID",
            "rank": "rank",
            "ID": "CoLD_ID",
            "Question": "Question",
            "Question_Number": "Question_Number",
            "Created": "Created",
            "Record ID": "ncRecordId",
            "Theme_Code": "Primary_Theme",
            "Answering_Options": "Answering_Options",
            "Last Modified": "updated_at",
            "Last Modified By.id": "updated_by",
            "Created By.id": "created_by",
        },
        conditional_mappings={
            "sort_date": ConditionalMapping(
                primary="updated_at",
                fallback="result_date",
            ),
            "Theme_Code": ConditionalMapping(
                primary="Primary_Theme",
                fallback="Theme_Code",
            ),
        },
        nested_mappings={
            "related_themes": NestedMapping(
                source_array="related_themes",
                array_operations={
                    "Themes": ArrayOperation(
                        operation="join",
                        field="Theme",
                        separator=Separator.COMMA_SPACE,
                    ),
                },
            ),
        },
    ),
    post_processing=PostProcessing(
        remove_null_values=True,
    ),
)
