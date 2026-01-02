"""Mapping configuration for Domestic Legal Provisions table."""

from app.schemas.mapping_schema import (
    ArrayOperation,
    MappingConfig,
    Mappings,
    NestedMapping,
    PostProcessing,
    UserMapping,
)


DOMESTIC_LEGAL_PROVISIONS_MAPPING = MappingConfig(
    table_name='Domestic Legal Provisions',
    description='Transformation rules for converting Domestic Legal Provisions table from current NocoDB format to reference format',
    version='1.0',
    mappings=Mappings(
        direct_mappings={
            'source_table': 'source_table',
            'id': 'CoLD_ID',
            'rank': 'rank',
            'ID': 'CoLD_ID',
            'Name': 'CoLD_ID',
            'Article': 'Article',
            'Full Text of the Provision (Original Language)': 'Full_Text_of_the_Provision__Original_Language_',
            'Full Text of the Provision (English Translation)': 'Full_Text_of_the_Provision__English_Translation_',
            'Record ID': 'ncRecordId',
            'Last Modified': 'updated_at',
            'Created': 'Created',
            'Ranking (Display Order)': 'Ranking__Display_Order_',
        },
        nested_mappings={
            'related_domestic_instruments': NestedMapping(
                source_array='related_domestic_instruments',
                index=0,
                mappings={
                    'Domestic Instruments Link': 'ncRecordId',
                    'Legislation Title': 'Title__in_English_',
                },
            ),
            'related_answers': NestedMapping(
                source_array='related_answers',
                array_operations={
                    'Answers': ArrayOperation(
                        operation='join',
                        field='ncRecordId',
                        separator=',',
                    ),
                },
            ),
            'related_questions': NestedMapping(
                source_array='related_questions',
                array_operations={
                    'Questions': ArrayOperation(
                        operation='join',
                        field='ncRecordId',
                        separator=',',
                    ),
                },
            ),
            'related_themes': NestedMapping(
                source_array='related_themes',
                array_operations={
                    'Themes Link': ArrayOperation(
                        operation='join',
                        field='ncRecordId',
                        separator=',',
                    ),
                },
            ),
            'related_jurisdictions': NestedMapping(
                source_array='related_jurisdictions',
                index=0,
                mappings={
                    'Jurisdictions Link': 'ncRecordId',
                    'Jurisdictions': 'Name',
                },
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