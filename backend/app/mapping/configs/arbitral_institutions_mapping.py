"""Mapping configuration for Arbitral Institutions table."""

from app.mapping.enums import Separator
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
                        separator=Separator.COMMA_SPACE,
                    ),
                    "Arbitral Awards Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=Separator.COMMA,
                    ),
                },
            ),
            "related_arbitral_rules": NestedMapping(
                source_array="related_arbitral_rules",
                array_operations={
                    "Arbitral Rules": ArrayOperation(
                        operation="join",
                        field="Set_of_Rules",
                        separator=Separator.COMMA_SPACE,
                    ),
                    "Arbitral Rules In Force From": ArrayOperation(
                        operation="join",
                        field="In_Force_From",
                        separator=Separator.COMMA_SPACE,
                    ),
                    "Arbitral Rules Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=Separator.COMMA,
                    ),
                },
            ),
            "related_arbitral_provisions": NestedMapping(
                source_array="related_arbitral_provisions",
                array_operations={
                    "Arbitral Provisions (Articles)": ArrayOperation(
                        operation="join",
                        field="Article",
                        separator=Separator.COMMA_SPACE,
                    ),
                    "Arbitral Provisions Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=Separator.COMMA,
                    ),
                },
            ),
            "related_jurisdictions": NestedMapping(
                source_array="related_jurisdictions",
                array_operations={
                    "Jurisdictions": ArrayOperation(
                        operation="join",
                        field="Name",
                        separator=Separator.COMMA_SPACE,
                    ),
                    "Jurisdictions Alpha-3 Code": ArrayOperation(
                        operation="join",
                        field="Alpha_3_Code",
                        separator=Separator.COMMA,
                    ),
                    "Jurisdictions Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=Separator.COMMA,
                    ),
                },
            ),
        },
    ),
    post_processing=PostProcessing(
        remove_null_values=True,
    ),
)
