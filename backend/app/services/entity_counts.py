from __future__ import annotations

COUNT_TABLES: tuple[tuple[str, str, bool], ...] = (
    ("courtDecisions", "data_views.base_court_decisions", True),
    ("literature", "data_views.base_literature", True),
    ("domesticInstruments", "data_views.base_domestic_instruments", True),
    ("regionalInstruments", "data_views.base_regional_instruments", False),
    ("internationalInstruments", "data_views.base_international_instruments", False),
    ("arbitralAwards", "data_views.base_arbitral_awards", True),
    ("arbitralInstitutions", "data_views.base_arbitral_institutions", True),
    ("arbitralRules", "data_views.base_arbitral_rules", True),
    ("arbitralProvisions", "data_views.base_arbitral_provisions", False),
    ("specialists", "data_views.base_specialists", True),
    ("jurisdictions", "data_views.base_jurisdictions", False),
    ("questions", "data_views.base_questions", False),
    ("answers", "data_views.base_answers", True),
    ("hcchAnswers", "data_views.base_hcch_answers", False),
    ("domesticLegalProvisions", "data_views.base_domestic_legal_provisions", True),
    ("regionalLegalProvisions", "data_views.base_regional_legal_provisions", False),
    ("internationalLegalProvisions", "data_views.base_international_legal_provisions", False),
)
