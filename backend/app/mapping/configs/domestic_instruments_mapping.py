"""Mapping configuration for Domestic Instruments table."""

from app.schemas.mapping_schema import (
    ArrayOperation,
    BooleanMapping,
    ComplexMapping,
    ConditionalMapping,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
    UserMapping,
)


DOMESTIC_INSTRUMENTS_MAPPING = MappingConfig(
    table_name='Domestic Instruments',
    description='Transformation rules for converting Domestic Instruments table from current NocoDB format to reference format',
    version='1.0',
    mappings=Mappings(
        direct_mappings={
            'source_table': 'source_table',
            'id': 'CoLD_ID',
            'rank': 'rank',
            'ID': 'CoLD_ID',
            'ID-number': 'ID_Number',
            'Date': 'Date',
            'Status': 'Status',
            'Abbreviation': 'Abbreviation',
            'Relevant Provisions': 'Relevant_Provisions',
            'Record ID': 'ncRecordId',
            'Created': 'Created',
            'Last Modified': 'updated_at',
            'Last Modified By.id': 'updated_by',
            'Created By.id': 'created_by',
            'Entry Into Force': 'Entry_Into_Force',
            'Publication Date': 'Publication_Date',
            'Full Text of the Provisions': 'Full_Text_of_the_Provisions',
            'Official Title': 'Official_Title',
        },
        conditional_mappings={
            'sort_date': ConditionalMapping(
                primary='Date',
                fallback='updated_at',
            ),
            'Title (in English)': ConditionalMapping(
                primary='Title__in_English_',
                fallback='Official_Title',
            ),
            'Source (URL)': ConditionalMapping(
                primary='Source__URL_',
                fallback='Official_Source_URL',
            ),
            'Source (PDF)': ConditionalMapping(
                primary='Source__PDF_',
                fallback='Official_Source_PDF',
            ),
        },
        boolean_mappings={
            'Compatible With the HCCH Principles': BooleanMapping(
                source_field='Compatible_With_the_HCCH_Principles_',
                true_value=True,
                false_value=False,
            ),
            'Compatible With the UNCITRAL Model Law': BooleanMapping(
                source_field='Compatible_With_the_UNCITRAL_Model_Law_',
                true_value=True,
                false_value=False,
            ),
        },
        nested_mappings={
            'related_jurisdictions': NestedMapping(
                source_array='related_jurisdictions',
                index=0,
                mappings={
                    'Jurisdictions Link': 'ncRecordId',
                    'Jurisdictions Alpha-3 Code': 'Alpha_3_Code',
                    'Jurisdictions': 'Name',
                    'Type (from Jurisdictions)': 'Type',
                },
            ),
            'related_questions': NestedMapping(
                source_array='related_questions',
                array_operations={
                    'Question ID': ArrayOperation(
                        operation='join',
                        field='ncRecordId',
                        separator=',',
                    ),
                },
            ),
            'related_answers': NestedMapping(
                source_array='related_answers',
                array_operations={
                    'Answers Link': ArrayOperation(
                        operation='join',
                        field='ncRecordId',
                        separator=',',
                    ),
                },
            ),
            'related_legal_provisions': NestedMapping(
                source_array='related_legal_provisions',
                array_operations={
                    'Domestic Legal Provisions Link': ArrayOperation(
                        operation='join',
                        field='ncRecordId',
                        separator=',',
                    ),
                    'Domestic Legal Provisions Full Text of the Provision (English T': ArrayOperation(
                        operation='join',
                        field='Full_Text_of_the_Provision__English_Translation_',
                        separator=',',
                    ),
                    'Domestic Legal Provisions Full Text of the Provision (Original ': ArrayOperation(
                        operation='join',
                        field='Full_Text_of_the_Provision__Original_Language_',
                        separator=',',
                    ),
                    'Domestic Legal Provisions': ArrayOperation(
                        operation='join',
                        field='CoLD_ID',
                        separator=',',
                    ),
                },
            ),
        },
        complex_mappings={
            'Source (PDF)': ComplexMapping(
                source_field='Source__PDF_',
                type='json_extract',
                operation='first_item_as_airtable_format',
            ),
        },
        user_mappings={
            'Last Modified By': UserMapping(
                source_field='updated_by',
                user_fields={
                    'Last Modified By.id': 'id',
                    'Last Modified By.email': 'email',
                    'Last Modified By.name': 'name',
                },
            ),
            'Created By': UserMapping(
                source_field='created_by',
                user_fields={
                    'Created By.id': 'id',
                    'Created By.email': 'email',
                    'Created By.name': 'name',
                },
            ),
        },
    ),
    post_processing=PostProcessing(
        remove_null_values=True,
    ),
)