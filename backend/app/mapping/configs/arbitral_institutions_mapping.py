"""Mapping configuration for Arbitral Institutions table."""

from app.schemas.mapping_schema import (
    ArrayOperation,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
)

ARBITRAL_INSTITUTIONS_MAPPING = MappingConfig(
    table_name="Arbitral Institutions",
    description="Pretty mapping for Arbitral Institutions with related awards, rules, provisions, and jurisdictions",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "source_table": "source_table",
            "id": "id",
            "rank": "rank",
            "ID": "id",
            "Record ID": "ncRecordId",
            "Institution": "Institution",
            "Abbreviation": "Abbreviation",
            "Created": "Created",
            "Last Modified": "updated_at",
            "Last Modified By.id": "updated_by",
            "Created By.id": "created_by",
        },
        nested_mappings={
            "related_arbitral_awards": NestedMapping(
                source_array="related_arbitral_awards",
                array_operations={
                    "Arbitral Awards": ArrayOperation(
                        operation="join",
                        field="Case_Number",
                        separator=", ",
                    ),
                    "Arbitral Awards Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=",",
                    ),
                },
            ),
            "related_arbitral_rules": NestedMapping(
                source_array="related_arbitral_rules",
                array_operations={
                    "Arbitral Rules": ArrayOperation(
                        operation="join",
                        field="Set_of_Rules",
                        separator=", ",
                    ),
                    "Arbitral Rules In Force From": ArrayOperation(
                        operation="join",
                        field="In_Force_From",
                        separator=", ",
                    ),
                    "Arbitral Rules Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=",",
                    ),
                },
            ),
            "related_arbitral_provisions": NestedMapping(
                source_array="related_arbitral_provisions",
                array_operations={
                    "Arbitral Provisions (Articles)": ArrayOperation(
                        operation="join",
                        field="Article",
                        separator=", ",
                    ),
                    "Arbitral Provisions Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=",",
                    ),
                },
            ),
            "related_jurisdictions": NestedMapping(
                source_array="related_jurisdictions",
                array_operations={
                    "Jurisdictions": ArrayOperation(
                        operation="join",
                        field="Name",
                        separator=", ",
                    ),
                    "Jurisdictions Alpha-3 Code": ArrayOperation(
                        operation="join",
                        field="Alpha_3_Code",
                        separator=",",
                    ),
                    "Jurisdictions Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=",",
                    ),
                },
            ),
        },
    ),
    post_processing=PostProcessing(
        remove_null_values=True,
    ),
)
