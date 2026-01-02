"""Mapping configuration for Court Decisions table."""

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

COURT_DECISIONS_MAPPING = MappingConfig(
    table_name="Court Decisions",
    description="Transformation rules for converting Court Decisions table from current NocoDB format to reference format",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "source_table": "source_table",
            "id": "CoLD_ID",
            "rank": "rank",
            "ID": "CoLD_ID",
            "Case Citation": "Case_Citation",
            "Case Title": "Case_Title",
            "Instance": "Instance",
            "Date": "Date",
            "Abstract": "Abstract",
            "Created": "Created",
            "Record ID": "ncRecordId",
            "ID-number": "ID_number",
            "Last Modified": "updated_at",
            "Last Modified By.id": "updated_by",
            "Created By.id": "created_by",
            "Added By.id": "created_by",
            "Created time": "Created",
            "Answers Link": "Answers_Link",
            "Answers Question": "Answers_Question",
            "Text_of_the_Relevant_Legal_Provisions": "Text_of_the_Relevant_Legal_Provisions",
            "Quote": "Quote",
            "Case Rank": "Case_Rank",
            "English Translation": "English_Translation",
            "Choice of Law Issue": "Choice_of_Law_Issue",
            "Court's Position": "Court's_Position",
            "Translated Excerpt": "Translated_Excerpt",
            "Relevant Facts": "Relevant_Facts",
            "Date of Judgment": "Date_of_Judgment",
            "PIL Provisions": "PIL_Provisions",
            "Original Text": "Original_Text",
        },
        conditional_mappings={
            "sort_date": ConditionalMapping(
                primary="Publication_Date_ISO",
                fallback="updated_at",
            ),
            "Publication Date ISO": ConditionalMapping(
                primary="Publication_Date_ISO",
                fallback="Date",
            ),
            "Official Source (URL)": ConditionalMapping(
                primary="Official_Source__URL_",
                fallback="Official_Source_URL",
            ),
        },
        nested_mappings={
            "related_questions": NestedMapping(
                source_array="related_questions",
                array_operations={
                    "Questions": ArrayOperation(
                        operation="join",
                        field="CoLD_ID",
                        separator=",",
                    ),
                },
            ),
            "related_jurisdictions": NestedMapping(
                source_array="related_jurisdictions",
                index=0,
                mappings={
                    "Jurisdictions Link": "ncRecordId",
                    "Jurisdictions Alpha-3 Code": "Alpha_3_Code",
                    "Jurisdictions": "Name",
                    "Region (from Jurisdictions)": "Region",
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
                },
            ),
        },
        complex_mappings={
            "Official Source (PDF)": ComplexMapping(
                source_field="Official_Source__PDF_",
                type="json_extract",
                operation="first_item_as_airtable_format",
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
            "Added By": UserMapping(
                source_field="created_by",
                user_fields={
                    "Added By.id": "id",
                    "Added By.email": "email",
                    "Added By.name": "name",
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
