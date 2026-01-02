"""Mapping configuration for Arbitral Provisions table."""

from app.mapping.enums import Separator
from app.schemas.mapping_schema import (
    ArrayOperation,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
)

ARBITRAL_PROVISIONS_MAPPING = MappingConfig(
    table_name="Arbitral Provisions",
    description="Pretty mapping for Arbitral Provisions with related awards, institutions, and rules",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "source_table": "source_table",
            "id": "CoLD_ID",
            "rank": "rank",
            "ID": "CoLD_ID",
            "Record ID": "ncRecordId",
            "Arbitral Rules ID": "Arbitral_Rules_CoLD_ID",
            "Article": "Article",
            "Full Text (Original Language)": "Full_Text_of_the_Provision__Original_Language_",
            "Full Text (English Translation)": "Full_Text_of_the_Provision__English_Translation_",
            "Arbitration method type": "Arbitration_method_type",
            "Non-State law allowed in AoC?": "Non_State_law_allowed_in_AoC_",
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
        },
    ),
    post_processing=PostProcessing(
        remove_null_values=True,
    ),
)
