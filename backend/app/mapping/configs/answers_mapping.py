"""Mapping configuration for Answers table."""

from app.mapping.enums import Separator, YesNoValue
from app.schemas.mapping_schema import (
    ArrayOperation,
    BooleanMapping,
    ConditionalMapping,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
)

ANSWERS_MAPPING = MappingConfig(
    table_name="Answers",
    description="Transformation rules for converting Answers table from current NocoDB format to reference format",
    version="1.0",
    mappings=Mappings(
        direct_mappings={
            "source_table": "source_table",
            "id": "CoLD_ID",
            "rank": "rank",
            "ID": "CoLD_ID",
            "Answer": "Answer",
            "Created": "Created",
            "Record ID": "ncRecordId",
            "Last Modified": "updated_at",
            "Last Modified By.id": "updated_by",
            "Created By.id": "created_by",
            "To Review?": "To_Review_",
            "OUP Book Quote": "OUP_Book_Quote",
            "More Information": "More_Information",
        },
        conditional_mappings={
            "sort_date": ConditionalMapping(
                primary="updated_at",
                fallback="result_date",
            ),
        },
        nested_mappings={
            "related_questions": NestedMapping(
                source_array="related_questions",
                index=0,
                mappings={
                    "Question Link": "ncRecordId",
                    "Question": "Question",
                    "Number": "Question_Number",
                },
                conditional_mappings={
                    "Questions Theme Code": ConditionalMapping(
                        primary="Theme_Code",
                        fallback="Primary_Theme",
                    ),
                },
            ),
            "related_jurisdictions": NestedMapping(
                source_array="related_jurisdictions",
                index=0,
                mappings={
                    "Jurisdictions Link": "ncRecordId",
                    "Jurisdictions Alpha-3 Code": "Alpha_3_Code",
                    "Jurisdictions Alpha-3 code": "Alpha_3_Code",  # backwards compat
                    "Jurisdictions": "Name",
                    "Jurisdictions Region": "Region",
                },
                boolean_mappings={
                    "Jurisdictions Irrelevant": BooleanMapping(
                        source_field="Irrelevant_",
                        true_value=YesNoValue.YES,
                        false_value=YesNoValue.NONE,
                    ),
                },
            ),
            "hop1_relations.related_court_decisions": NestedMapping(
                source_array="hop1_relations.related_court_decisions",
                array_operations={
                    "Court Decisions": ArrayOperation(
                        operation="join",
                        field="Case_Title",
                        separator=Separator.COMMA,
                    ),
                    "Court Decisions Link": ArrayOperation(
                        operation="join",
                        field="ncRecordId",
                        separator=Separator.COMMA,
                    ),
                    "Court Decisions ID": ArrayOperation(
                        operation="join",
                        field="CoLD_ID",
                        separator=Separator.COMMA,
                    ),
                },
            ),
            "hop1_relations.related_domestic_instruments": NestedMapping(
                source_array="hop1_relations.related_domestic_instruments",
                index=0,
                mappings={
                    "Domestic Instruments Link": "ncRecordId",
                    "Domestic Instruments": "Official_Title",
                    "Domestic Instruments ID": "CoLD_ID",
                },
            ),
            "hop1_relations.related_domestic_legal_provisions": NestedMapping(
                source_array="hop1_relations.related_domestic_legal_provisions",
                index=0,
                mappings={
                    "Domestic Legal Provisions Link": "ncRecordId",
                    "Domestic Legal Provisions": "CoLD_ID",
                },
            ),
            "related_themes": NestedMapping(
                source_array="related_themes",
                array_operations={
                    "Themes": ArrayOperation(
                        operation="join",
                        field="Theme",
                        separator=Separator.COMMA_SPACE,
                    ),
                },
            ),
        },
    ),
    post_processing=PostProcessing(
        remove_null_values=True,
    ),
)
