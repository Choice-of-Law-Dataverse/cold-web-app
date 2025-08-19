"""
Legacy transformer for Court Decisions using the new configurable system.
"""

from .configurable_transformer import get_configurable_transformer


class CourtDecisionsTransformer:
    """
    Transformer for converting Court Decisions table data from current NocoDB format
    to the reference format structure.
    
    This class uses the configurable transformer with external mapping rules.
    """

    @staticmethod
    def transform_to_reference_format(current_result):
        """
        Transform current court decisions format to match the reference format structure.
        
        Args:
            current_result (dict): The current format result from NocoDB
            
        Returns:
            dict: Transformed result matching the reference format
        """
        # Use the configurable transformer with external mapping rules
        transformer = get_configurable_transformer()
        return transformer.transform("Court Decisions", current_result)
