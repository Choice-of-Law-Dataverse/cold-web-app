"""Mapping configuration for International Instruments table."""

from app.mapping.enums import Separator
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

INTERNATIONAL_INSTRUMENTS_MAPPING = MappingConfig(
    table_name="International Instruments",
    description=(
        "Transformation rules for converting International Instruments table from current NocoDB format to reference format"
    ),
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "source_table": "source_table",
            "id": "CoLD_ID",
            "rank": "rank",
            "ID": "CoLD_ID",
            "ID Number": "ID_Number",
            "Title": "Title",
            "Abbreviation": "Abbreviation",
            "Date": "Date",
            "Status": "Status",
            "URL": "URL",
            "Attachment": "Attachment",
            "Record ID": "ncRecordId",
            "Created": "Created",
            "Last Modified": "updated_at",
            "Last Modified By.id": "updated_by",
            "Created By.id": "created_by",
            "Entry Into Force": "Entry_Into_Force",
            "Publication Date": "Publication_Date",
            "Relevant Provisions": "Relevant_Provisions",
            "Full Text of the Provisions": "Full_Text_of_the_Provisions",
            "Name": "Name",
        },
        conditional_mappings={
            "sort_date": ConditionalMapping(
                primary="updated_at",
                fallback="result_date",
            ),
            "Title (in English)": ConditionalMapping(
                primary="Title__in_English_",
                fallback="Official_Title",
            ),
            "Source (URL)": ConditionalMapping(
                primary="Source__URL_",
                fallback="Official_Source_URL",
            ),
            "Source (PDF)": ConditionalMapping(
                primary="Source__PDF_",
                fallback="Official_Source_PDF",
            ),
        },
        nested_mappings={
            "related_specialists": NestedMapping(
                source_array="related_specialists",
                array_operations={
                    "Specialists": ArrayOperation(
                        operation="join",
                        field="Specialist",
                        separator=Separator.COMMA,
                    ),
                    "Specialists Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=Separator.COMMA,
                    ),
                },
            ),
            "related_legal_provisions": NestedMapping(
                source_array="related_legal_provisions",
                array_operations={
                    "International Legal Provisions": ArrayOperation(
                        operation="join",
                        field="CoLD_ID",
                        separator=Separator.COMMA,
                    ),
                    "International Legal Provisions Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=Separator.COMMA,
                    ),
                },
            ),
            "related_literature": NestedMapping(
                source_array="related_literature",
                array_operations={
                    "Literature": ArrayOperation(
                        operation="join",
                        field="CoLD_ID",
                        separator=Separator.COMMA,
                    ),
                    "Literature Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=Separator.COMMA,
                    ),
                },
            ),
            "related_hcch_answers": NestedMapping(
                source_array="related_hcch_answers",
                array_operations={
                    "HCCH Answers": ArrayOperation(
                        operation="join",
                        field="Adapted_Question",
                        separator=Separator.COMMA,
                    ),
                    "HCCH Answers Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=Separator.COMMA,
                    ),
                },
            ),
        },
        complex_mappings={
            "Literature": ComplexMapping(
                source_field="Literature_Link",
                type="array_extract",
                operation="join_ids",
            ),
            "Literature Link": ComplexMapping(
                source_field="Literature_Link",
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
