"""Mapping configuration for Arbitral Rules table."""

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
                        separator=", ",
                    ),
                    "Arbitral Institutions Abbrev": ArrayOperation(
                        operation="join",
                        field="Abbreviation",
                        separator=", ",
                    ),
                    "Arbitral Institutions Link": ArrayOperation(
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
