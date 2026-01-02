"""Mapping configuration for International Legal Provisions table."""

from app.schemas.mapping_schema import (
    ConditionalMapping,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
    UserMapping,
)

INTERNATIONAL_LEGAL_PROVISIONS_MAPPING = MappingConfig(
    table_name="International Legal Provisions",
    description="Transformation rules for converting International Legal Provisions to the desired reference format",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "source_table": "source_table",
            "id": "CoLD_ID",
            "rank": "rank",
            "ID": "CoLD_ID",
            "cold_id": "CoLD_ID",
            "CoLD_ID": "CoLD_ID",
            "Title of the Provision": "Title_of_the_Provision",
            "Full Text": "Full_Text",
            "Provision": "Provision",
            "Record ID": "ncRecordId",
            "Created": "Created",
            "Last Modified": "updated_at",
            "Last Modified By.id": "updated_by",
            "Created By.id": "created_by",
            "Ranking__Display_Order_": "Ranking__Display_Order_",
            "nc_order": "nc_order",
            "ncRecordHash": "ncRecordHash",
            "Arbitral_Awards": "Arbitral_Awards",
            "Instrument_CoLD_ID": "Instrument_CoLD_ID",
            "International_Instruments_copy": "International_Instruments_copy",
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
            "hop1_relations.related_international_instruments": NestedMapping(
                source_array="hop1_relations.related_international_instruments",
                index=0,
                mappings={
                    "Instrument Link": "ncRecordId",
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
