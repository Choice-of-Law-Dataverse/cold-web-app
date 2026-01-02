"""Mapping configuration for Arbitral Awards table."""

from app.schemas.mapping_schema import (
    ArrayOperation,
    ConditionalMapping,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
)

ARBITRAL_AWARDS_MAPPING = MappingConfig(
    table_name="Arbitral Awards",
    description=(
        "Pretty mapping for Arbitral Awards with relations to institutions, provisions, "
        "court decisions, jurisdictions, and themes"
    ),
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "source_table": "source_table",
            "id": "CoLD_ID",
            "rank": "rank",
            "ID": "CoLD_ID",
            "Record ID": "ncRecordId",
            "Case Number": "Case_Number",
            "Context": "Context",
            "Award Summary": "Award_Summary",
            "Year": "Year",
            "Nature of the Award": "Nature_of_the_Award",
            "Seat (Town)": "Seat__Town_",
            "Source": "Source",
            "Created": "Created",
            "Last Modified": "updated_at",
            "Last Modified By.id": "updated_by",
            "Created By.id": "created_by",
        },
        conditional_mappings={
            "sort_date": ConditionalMapping(
                primary="Year",
                fallback="updated_at",
            ),
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
            "related_court_decisions": NestedMapping(
                source_array="related_court_decisions",
                array_operations={
                    "Court Decisions": ArrayOperation(
                        operation="join",
                        field="Case_Title",
                        separator=", ",
                    ),
                    "Court Decisions Link": ArrayOperation(
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
            "related_themes": NestedMapping(
                source_array="related_themes",
                array_operations={
                    "Themes": ArrayOperation(
                        operation="join",
                        field="Theme",
                        separator=", ",
                    ),
                },
            ),
        },
    ),
    post_processing=PostProcessing(
        remove_null_values=True,
    ),
)
