from typing import Any

from pydantic import ConfigDict

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


class SearchResultBase(EntityBase):
    model_config = ConfigDict(extra="ignore")

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


TABLE_SEARCH_MODELS: dict[str, type[SearchResultBase]] = {
    "Answers": AnswerSearchResult,
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


def validate_search_result(data: dict[str, Any]) -> AnySearchResult:
    source_table = data.get("source_table") or data.get("sourceTable") or ""
    model = TABLE_SEARCH_MODELS.get(source_table, SearchResultBase)
    return model(**data)  # type: ignore[return-value]
