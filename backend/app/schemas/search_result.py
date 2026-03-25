import logging
from typing import Any

from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

from app.schemas.entities import (
    AnswerBase,
    ArbitralAwardBase,
    ArbitralInstitutionBase,
    ArbitralProvisionBase,
    ArbitralRuleBase,
    CourtDecisionBase,
    DomesticInstrumentBase,
    DomesticLegalProvisionBase,
    EntityBase,
    InternationalInstrumentBase,
    InternationalLegalProvisionBase,
    JurisdictionBase,
    LiteratureBase,
    QuestionBase,
    RegionalInstrumentBase,
    RegionalLegalProvisionBase,
)

logger = logging.getLogger(__name__)


class SearchResultBase(EntityBase):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        coerce_numbers_to_str=True,
        extra="ignore",
    )

    id: str | int | None = None
    source_table: str | None = None
    rank: float | None = None
    result_date: str | None = None
    jurisdictions: str | None = None
    themes: str | None = None


class AnswerSearchResult(SearchResultBase, AnswerBase):
    question: str | None = None
    court_decisions_link: str | None = None
    last_modified: str | None = None
    created: str | None = None
    questions_theme_code: str | None = None


class CourtDecisionSearchResult(SearchResultBase, CourtDecisionBase):
    source_pdf: str | None = None


class DomesticInstrumentSearchResult(SearchResultBase, DomesticInstrumentBase):
    official_source_pdf: str | None = None
    domestic_legal_provisions_themes: str | None = None


class RegionalInstrumentSearchResult(SearchResultBase, RegionalInstrumentBase):
    pass


class InternationalInstrumentSearchResult(SearchResultBase, InternationalInstrumentBase):
    official_source_pdf: str | None = None
    source_pdf: str | None = None


class LiteratureSearchResult(SearchResultBase, LiteratureBase):
    pass


class ArbitralAwardSearchResult(SearchResultBase, ArbitralAwardBase):
    arbitral_institutions: str | None = None
    arbitral_institutions_abbrev: str | None = None
    jurisdictions_alpha_3_code: str | None = None


class ArbitralRuleSearchResult(SearchResultBase, ArbitralRuleBase):
    arbitral_institutions: str | None = None


class ArbitralInstitutionSearchResult(SearchResultBase, ArbitralInstitutionBase):
    pass


class ArbitralProvisionSearchResult(SearchResultBase, ArbitralProvisionBase):
    arbitral_institutions: str | None = None
    arbitral_rules: str | None = None


class DomesticLegalProvisionSearchResult(SearchResultBase, DomesticLegalProvisionBase):
    legislation_title: str | None = None
    name: str | None = None


class InternationalLegalProvisionSearchResult(SearchResultBase, InternationalLegalProvisionBase):
    instrument: str | None = None


class RegionalLegalProvisionSearchResult(SearchResultBase, RegionalLegalProvisionBase):
    instrument: str | None = None


class JurisdictionSearchResult(SearchResultBase, JurisdictionBase):
    alpha_3_code: str | None = None


class QuestionSearchResult(SearchResultBase, QuestionBase):
    theme_code: str | None = None


class HcchAnswerSearchResult(SearchResultBase):
    adapted_question: str | None = None
    position: str | None = None
    question_cold_id: str | None = None


TABLE_SEARCH_MODELS: dict[str, type[SearchResultBase]] = {
    "Answers": AnswerSearchResult,
    "HCCH Answers": HcchAnswerSearchResult,
    "Court Decisions": CourtDecisionSearchResult,
    "Domestic Instruments": DomesticInstrumentSearchResult,
    "Regional Instruments": RegionalInstrumentSearchResult,
    "International Instruments": InternationalInstrumentSearchResult,
    "Literature": LiteratureSearchResult,
    "Arbitral Awards": ArbitralAwardSearchResult,
    "Arbitral Rules": ArbitralRuleSearchResult,
    "Arbitral Institutions": ArbitralInstitutionSearchResult,
    "Arbitral Provisions": ArbitralProvisionSearchResult,
    "Domestic Legal Provisions": DomesticLegalProvisionSearchResult,
    "International Legal Provisions": InternationalLegalProvisionSearchResult,
    "Regional Legal Provisions": RegionalLegalProvisionSearchResult,
    "Jurisdictions": JurisdictionSearchResult,
    "Questions": QuestionSearchResult,
}

AnySearchResult = (
    AnswerSearchResult
    | HcchAnswerSearchResult
    | CourtDecisionSearchResult
    | DomesticInstrumentSearchResult
    | RegionalInstrumentSearchResult
    | InternationalInstrumentSearchResult
    | LiteratureSearchResult
    | ArbitralAwardSearchResult
    | ArbitralRuleSearchResult
    | ArbitralInstitutionSearchResult
    | ArbitralProvisionSearchResult
    | DomesticLegalProvisionSearchResult
    | InternationalLegalProvisionSearchResult
    | RegionalLegalProvisionSearchResult
    | JurisdictionSearchResult
    | QuestionSearchResult
    | SearchResultBase
)


def validate_search_result(data: dict[str, Any]) -> SearchResultBase:
    source_table = data.get("sourceTable") or data.get("source_table") or ""
    model = TABLE_SEARCH_MODELS.get(source_table)
    if model is None:
        logger.warning("Unknown source_table %r — falling back to SearchResultBase", source_table)
        model = SearchResultBase
    return model(**data)
