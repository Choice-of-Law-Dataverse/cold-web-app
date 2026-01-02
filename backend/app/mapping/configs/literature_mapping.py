"""Mapping configuration for Literature table."""

from app.schemas.mapping_schema import (
    ArrayOperation,
    ComplexMapping,
    ConditionalMapping,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
    UserMapping,
)

LITERATURE_MAPPING = MappingConfig(
    table_name="Literature",
    description="Transformation rules for converting Literature table from current NocoDB format to reference format",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "id": "CoLD_ID",
            "source_table": "source_table",
            "Record ID": "ncRecordId",
            "CoLD_ID": "CoLD_ID",
            "ID": "ID_Number",
            "Key": "Key",
            "Item Type": "Item_Type",
            "Publication Year": "Publication_Year",
            "Author": "Author",
            "Title": "Title",
            "ISBN": "ISBN",
            "ISSN": "ISSN",
            "Url": "Url",
            "Date": "Date",
            "Date Added": "Date_Added",
            "Date Modified": "Date_Modified",
            "Publisher": "Publisher",
            "Language": "Language",
            "Extra": "Extra",
            "Manual Tags": "Manual_Tags",
            "Editor": "Editor",
            "Last Modified": "updated_at",
            "Created": "Created",
            "Last Modified By.id": "updated_by",
            "Created By.id": "created_by",
            "Publication Title": "Publication_Title",
            "Issue": "Issue",
            "Volume": "Volume",
            "Pages": "Pages",
            "Abstract Note": "Abstract_Note",
            "Library Catalog": "Library_Catalog",
            "DOI": "DOI",
            "Access Date": "Access_Date",
            "Open Access": "Open_Access",
            "Open Access URL": "Open_Access_URL",
            "Journal Abbreviation": "Journal_Abbreviation",
            "Short Title": "Short_Title",
            "Place": "Place",
            "Num Pages": "Num_Pages",
            "Type": "Type",
            "OUP JD Chapter": "OUP_JD_Chapter",
            "Contributor": "Contributor",
            "Automatic Tags": "Automatic_Tags",
            "Number": "Number",
            "Series": "Series",
            "Series Number": "Series_Number",
            "Series Editor": "Series_Editor",
            "Edition": "Edition",
            "Call Number": "Call_Number",
            "Jurisdiction Summary": "Jurisdiction_Summary",
            "Answers": "Answers",
        },
        conditional_mappings={
            "sort_date": ConditionalMapping(
                primary="Date",
                fallback="Publication_Year",
            ),
        },
        nested_mappings={
            "related_jurisdictions": NestedMapping(
                source_array="related_jurisdictions",
                index=0,
                mappings={
                    "Jurisdiction Link": "ncRecordId",
                    "Jurisdiction": "Name",
                },
            ),
            "related_themes": NestedMapping(
                source_array="related_themes",
                array_operations={
                    "Themes": ArrayOperation(
                        operation="join",
                        field="Theme",
                        separator=",",
                    ),
                    "Themes Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=",",
                    ),
                },
            ),
            "related_international_instruments": NestedMapping(
                source_array="related_international_instruments",
                array_operations={
                    "International Instruments": ArrayOperation(
                        operation="join",
                        field="Name",
                        separator=",",
                    ),
                    "International Instruments Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=",",
                    ),
                },
            ),
            "hop1_relations.related_international_instruments": NestedMapping(
                source_array="hop1_relations.related_international_instruments",
                array_operations={
                    "International Instruments": ArrayOperation(
                        operation="join",
                        field="Name",
                        separator=",",
                    ),
                    "International Instruments Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=",",
                    ),
                },
            ),
            "related_international_legal_provisions": NestedMapping(
                source_array="related_international_legal_provisions",
                array_operations={
                    "International Legal Provisions": ArrayOperation(
                        operation="join",
                        field="Title_of_the_Provision",
                        separator=",",
                    ),
                    "International Legal Provisions Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=",",
                    ),
                },
            ),
            "hop1_relations.related_international_legal_provisions": NestedMapping(
                source_array="hop1_relations.related_international_legal_provisions",
                array_operations={
                    "International Legal Provisions": ArrayOperation(
                        operation="join",
                        field="Title_of_the_Provision",
                        separator=",",
                    ),
                    "International Legal Provisions Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=",",
                    ),
                },
            ),
            "hop1_relations.related_regional_instruments": NestedMapping(
                source_array="hop1_relations.related_regional_instruments",
                array_operations={
                    "Regional Instruments": ArrayOperation(
                        operation="join",
                        field="Name",
                        separator=",",
                    ),
                    "Regional Instruments Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=",",
                    ),
                },
            ),
        },
        complex_mappings={
            "International Instruments": ComplexMapping(
                source_field="International_Instruments_Link",
                type="array_extract",
                operation="join_display_values",
            ),
            "International Instruments Link": ComplexMapping(
                source_field="International_Instruments_Link",
                type="array_extract",
                operation="join_record_ids",
            ),
            "International Legal Provisions": ComplexMapping(
                source_field="International_Legal_Provisions_Link",
                type="array_extract",
                operation="join_display_values",
            ),
            "International Legal Provisions Link": ComplexMapping(
                source_field="International_Legal_Provisions_Link",
                type="array_extract",
                operation="join_record_ids",
            ),
            "Regional Instruments": ComplexMapping(
                source_field="Regional_Instruments_Link",
                type="array_extract",
                operation="join_display_values",
            ),
            "Regional Instruments Link": ComplexMapping(
                source_field="Regional_Instruments_Link",
                type="array_extract",
                operation="join_record_ids",
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
