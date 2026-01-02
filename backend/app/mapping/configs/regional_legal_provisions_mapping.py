"""Mapping configuration for Regional Legal Provisions table."""

from app.schemas.mapping_schema import (
    ArrayOperation,
    ConditionalMapping,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
    UserMapping,
)

REGIONAL_LEGAL_PROVISIONS_MAPPING = MappingConfig(
    table_name="Regional Legal Provisions",
    description="Transformation rules for converting Regional Legal Provisions to the desired reference format",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "source_table": "source_table",
            "id": "CoLD_ID",
            "rank": "rank",
            "ID": "CoLD_ID",
            "Title of the Provision": "Title_of_the_Provision",
            "Full Text": "Full_Text",
            "Provision": "Provision",
            "Record ID": "ncRecordId",
            "Created": "Created",
            "Last Modified": "updated_at",
            "Last Modified By.id": "updated_by",
            "Created By.id": "created_by",
        },
        conditional_mappings={
            "sort_date": ConditionalMapping(
                primary="updated_at",
                fallback="result_date",
            ),
            "Instrument": ConditionalMapping(
                primary="Instrument_CoLD_ID",
                fallback="hop1_relations.Instrument_CoLD_ID",
            ),
        },
        nested_mappings={
            "related_regional_instruments": NestedMapping(
                source_array="related_regional_instruments",
                index=0,
                mappings={
                    "Instrument Link": "ncRecordId",
                },
            ),
            "hop1_relations.related_regional_instruments": NestedMapping(
                source_array="hop1_relations.related_regional_instruments",
                index=0,
                mappings={
                    "Instrument Link": "ncRecordId",
                },
            ),
            "related_questions": NestedMapping(
                source_array="related_questions",
                array_operations={
                    "Questions": ArrayOperation(
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
