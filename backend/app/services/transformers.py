"""
Data transformation services for converting between different data formats.
This module contains transformers that convert data structures from the current
NocoDB format to legacy/reference formats for backward compatibility.
"""

import logging

from .configurable_transformer import get_configurable_transformer
from .court_decisions_transformer import CourtDecisionsTransformer
from .domestic_instruments_transformer import DomesticInstrumentsTransformer
from .international_instruments_transformer import InternationalInstrumentsTransformer
from .regional_instruments_transformer import RegionalInstrumentsTransformer

logger = logging.getLogger(__name__)


class AnswersTransformer:
    """
    Transformer for converting Answers table data from current NocoDB format
    to the reference format structure.

    This class now uses the configurable transformer with external mapping rules.
    """

    @staticmethod
    def transform_to_reference_format(current_result):
        """
        Transform current answers format to match the reference format structure.

        Args:
            current_result (dict): The current format result from NocoDB

        Returns:
            dict: Transformed result matching the reference format
        """
        # Use the configurable transformer with external mapping rules
        transformer = get_configurable_transformer()
        return transformer.transform("Answers", current_result)


class DataTransformerFactory:
    """
    Factory class for getting the appropriate transformer based on table type.
    Now supports both legacy transformers and the new configurable transformer.
    """

    _transformers = {
        "Answers": AnswersTransformer,
        "Court Decisions": CourtDecisionsTransformer,
        "Domestic Instruments": DomesticInstrumentsTransformer,
        "Regional Instruments": RegionalInstrumentsTransformer,
        "International Instruments": InternationalInstrumentsTransformer,
        # Add other table transformers here as needed
        # "Questions": QuestionsTransformer,
        # "Jurisdictions": JurisdictionsTransformer,
    }

    @classmethod
    def get_transformer(cls, table_name):
        """
        Get the appropriate transformer for a given table.

        Args:
            table_name (str): Name of the table

        Returns:
            Transformer class or None if no transformer is available
        """
        return cls._transformers.get(table_name)

    @classmethod
    def transform_result(cls, table_name, result):
        """
        Transform a result using the appropriate transformer.
        Falls back to configurable transformer if no specific transformer exists.

        Args:
            table_name (str): Name of the source table
            result (dict): The result to transform

        Returns:
            dict: Transformed result or original result if no transformer available
        """
        # First try specific transformer
        transformer_class = cls.get_transformer(table_name)
        if transformer_class:
            return transformer_class.transform_to_reference_format(result)

        # Fall back to configurable transformer
        configurable_transformer = get_configurable_transformer()
        if table_name in configurable_transformer.mappings:
            return configurable_transformer.transform(table_name, result)

        # No transformation available
        logger.debug(f"No transformer available for table: {table_name}")
        return result
