"""Mapping configuration for Regional Instruments table."""

from app.schemas.mapping_schema import (
    ArrayOperation,
    ConditionalMapping,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
    UserMapping,
)

REGIONAL_INSTRUMENTS_MAPPING = MappingConfig(
    table_name="Regional Instruments",
    description="Transformation rules for converting Regional Instruments table from current NocoDB format to reference format",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "source_table": "source_table",
            "id": "CoLD_ID",
            "rank": "rank",
            "ID": "CoLD_ID",
            "ID Number": "ID_Number",
            "Title": "Title",
            "Abbreviation": "Abbreviation",
            "Date": "Date",
            "URL": "URL",
            "Attachment": "Attachment",
            "Record ID": "ncRecordId",
            "Created": "Created",
            "Last Modified": "updated_at",
            "Last Modified By.id": "updated_by",
            "Created By.id": "created_by",
        },
        conditional_mappings={
            "sort_date": ConditionalMapping(
                primary="Date",
                fallback="updated_at",
            ),
        },
        nested_mappings={
            "related_specialists": NestedMapping(
                source_array="related_specialists",
                array_operations={
                    "Specialists": ArrayOperation(
                        operation="join",
                        field="Specialist",
                        separator=",",
                    ),
                    "Specialists Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=",",
                    ),
                },
            ),
            "related_legal_provisions": NestedMapping(
                source_array="related_legal_provisions",
                array_operations={
                    "Regional Legal Provisions": ArrayOperation(
                        operation="join",
                        field="CoLD_ID",
                        separator=",",
                    ),
                    "Regional Legal Provisions Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=",",
                    ),
                },
            ),
        },
        user_mappings={
            "Last Modified By": UserMapping(
                source_field="updated_by",
                user_fields={
                    "Last Modified By.id": "id",
                    "Last Modified By.email": "email",
                    "Last Modified By.name": "name",
                },
            ),
            "Created By": UserMapping(
                source_field="created_by",
                user_fields={
                    "Created By.id": "id",
                    "Created By.email": "email",
                    "Created By.name": "name",
                },
            ),
        },
    ),
    post_processing=PostProcessing(
        remove_null_values=True,
    ),
)
