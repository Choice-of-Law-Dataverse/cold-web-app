"""Mapping configuration for Arbitral Rules table."""

from app.mapping.enums import Separator
from app.schemas.mapping_schema import (
    ArrayOperation,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
)

ARBITRAL_RULES_MAPPING = MappingConfig(
    table_name="Arbitral Rules",
    description="Pretty mapping for Arbitral Rules with related institutions and provisions",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "source_table": "source_table",
            "id": "CoLD_ID",
            "rank": "rank",
            "ID": "CoLD_ID",
            "Record ID": "ncRecordId",
            "Set of Rules": "Set_of_Rules",
            "In Force From": "In_Force_From",
            "Official Source (URL)": "Official_Source__URL_",
            "Created": "Created",
            "Last Modified": "updated_at",
            "Last Modified By.id": "updated_by",
            "Created By.id": "created_by",
        },
        nested_mappings={
            "related_arbitral_institutions": NestedMapping(
                source_array="related_arbitral_institutions",
                array_operations={
                    "Arbitral Institutions": ArrayOperation(
                        operation="join",
                        field="Institution",
                        separator=Separator.COMMA_SPACE,
                    ),
                    "Arbitral Institutions Abbrev": ArrayOperation(
                        operation="join",
                        field="Abbreviation",
                        separator=Separator.COMMA_SPACE,
                    ),
                    "Arbitral Institutions Link": ArrayOperation(
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
