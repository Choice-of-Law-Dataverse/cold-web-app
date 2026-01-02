"""
Python-based mapping configurations.

This module contains Python class-based mapping configurations
that replace the legacy JSON files, providing better type safety
and maintainability.
"""

from app.mapping.configs.answers_mapping import ANSWERS_MAPPING
from app.mapping.configs.arbitral_awards_mapping import ARBITRAL_AWARDS_MAPPING
from app.mapping.configs.arbitral_institutions_mapping import ARBITRAL_INSTITUTIONS_MAPPING
from app.mapping.configs.arbitral_provisions_mapping import ARBITRAL_PROVISIONS_MAPPING
from app.mapping.configs.arbitral_rules_mapping import ARBITRAL_RULES_MAPPING
from app.mapping.configs.court_decisions_mapping import COURT_DECISIONS_MAPPING
from app.mapping.configs.domestic_instruments_mapping import DOMESTIC_INSTRUMENTS_MAPPING
from app.mapping.configs.domestic_legal_provisions_mapping import DOMESTIC_LEGAL_PROVISIONS_MAPPING
from app.mapping.configs.international_instruments_mapping import INTERNATIONAL_INSTRUMENTS_MAPPING
from app.mapping.configs.international_legal_provisions_mapping import INTERNATIONAL_LEGAL_PROVISIONS_MAPPING
from app.mapping.configs.jurisdictions_mapping import JURISDICTIONS_MAPPING
from app.mapping.configs.literature_mapping import LITERATURE_MAPPING
from app.mapping.configs.questions_mapping import QUESTIONS_MAPPING
from app.mapping.configs.regional_instruments_mapping import REGIONAL_INSTRUMENTS_MAPPING
from app.mapping.configs.regional_legal_provisions_mapping import REGIONAL_LEGAL_PROVISIONS_MAPPING
from app.schemas.mapping_schema import MappingConfig


# Registry of all mapping configurations
ALL_MAPPINGS: dict[str, MappingConfig] = {
    "Answers": ANSWERS_MAPPING,
    "Jurisdictions": JURISDICTIONS_MAPPING,
    "Questions": QUESTIONS_MAPPING,
    "Court Decisions": COURT_DECISIONS_MAPPING,
    "Domestic Instruments": DOMESTIC_INSTRUMENTS_MAPPING,
    "International Instruments": INTERNATIONAL_INSTRUMENTS_MAPPING,
    "Regional Instruments": REGIONAL_INSTRUMENTS_MAPPING,
    "Literature": LITERATURE_MAPPING,
    "Arbitral Awards": ARBITRAL_AWARDS_MAPPING,
    "Arbitral Institutions": ARBITRAL_INSTITUTIONS_MAPPING,
    "Arbitral Provisions": ARBITRAL_PROVISIONS_MAPPING,
    "Arbitral Rules": ARBITRAL_RULES_MAPPING,
    "Domestic Legal Provisions": DOMESTIC_LEGAL_PROVISIONS_MAPPING,
    "International Legal Provisions": INTERNATIONAL_LEGAL_PROVISIONS_MAPPING,
    "Regional Legal Provisions": REGIONAL_LEGAL_PROVISIONS_MAPPING,
}


__all__ = [
    "ALL_MAPPINGS",
    "ANSWERS_MAPPING",
    "JURISDICTIONS_MAPPING",
    "QUESTIONS_MAPPING",
    "COURT_DECISIONS_MAPPING",
    "DOMESTIC_INSTRUMENTS_MAPPING",
    "INTERNATIONAL_INSTRUMENTS_MAPPING",
    "REGIONAL_INSTRUMENTS_MAPPING",
    "LITERATURE_MAPPING",
    "ARBITRAL_AWARDS_MAPPING",
    "ARBITRAL_INSTITUTIONS_MAPPING",
    "ARBITRAL_PROVISIONS_MAPPING",
    "ARBITRAL_RULES_MAPPING",
    "DOMESTIC_LEGAL_PROVISIONS_MAPPING",
    "INTERNATIONAL_LEGAL_PROVISIONS_MAPPING",
    "REGIONAL_LEGAL_PROVISIONS_MAPPING",
]
