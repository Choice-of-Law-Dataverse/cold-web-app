"""
Legacy transformer for International Instruments table.
This transformer maintains backward compatibility while using the new configuration-driven system.
"""

from app.services.configurable_transformer import ConfigurableTransformer


class InternationalInstrumentsTransformer:
    """Legacy transformer for International Instruments that uses the configuration-driven system."""

    def __init__(self):
        self.configurable_transformer = ConfigurableTransformer()

    @staticmethod
    def transform_to_reference_format(current_result):
        """
        Transform current International Instruments format to match the reference format structure.

        Args:
            current_result (dict): The current format result from NocoDB

        Returns:
            dict: Transformed result matching the reference format
        """
        # Use the configurable transformer with external mapping rules
        transformer = ConfigurableTransformer()
        return transformer.transform("International Instruments", current_result)

    def transform(self, data):
        """
        Transform International Instruments data using configuration-driven approach.

        Args:
            data: The input data to transform

        Returns:
            Transformed data in the reference format
        """
        return self.configurable_transformer.transform("International Instruments", data)
