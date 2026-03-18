# pyright: reportIncompatibleVariableOverride=false
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.schemas.details import (
    AnswerDetail,
    ArbitralAwardDetail,
    ArbitralInstitutionDetail,
    ArbitralProvisionDetail,
    ArbitralRuleDetail,
    CourtDecisionDetail,
    DomesticInstrumentDetail,
    DomesticLegalProvisionDetail,
    InternationalInstrumentDetail,
    InternationalLegalProvisionDetail,
    JurisdictionDetail,
    LiteratureDetail,
    QuestionDetail,
    RegionalInstrumentDetail,
    RegionalLegalProvisionDetail,
)
from app.schemas.records import coerce_bools_to_str
from app.schemas.relations import EntityRelations


class SearchResultBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
        coerce_numbers_to_str=True,
    )

    _coerce_bools_to_str = coerce_bools_to_str

    id: str | int | None = None
    source_table: str | None = None
    relations: EntityRelations | None = Field(default=None, exclude=True)
    rank: float | None = None
    result_date: str | None = None
    jurisdictions: str | None = None
    themes: str | None = None


class AnswerSearchResult(SearchResultBase, AnswerDetail):
    question: str | None = None
    court_decisions_link: str | None = None
    last_modified: str | None = None
    created: str | None = None
    questions_theme_code: str | None = None


class CourtDecisionSearchResult(SearchResultBase, CourtDecisionDetail):
    source_pdf: str | None = None


class DomesticInstrumentSearchResult(SearchResultBase, DomesticInstrumentDetail):
    official_source_pdf: str | None = None
    domestic_legal_provisions_themes: str | None = None


class RegionalInstrumentSearchResult(SearchResultBase, RegionalInstrumentDetail):
    pass


class InternationalInstrumentSearchResult(SearchResultBase, InternationalInstrumentDetail):
    official_source_pdf: str | None = None
    source_pdf: str | None = None


class LiteratureSearchResult(SearchResultBase, LiteratureDetail):
    pass


class ArbitralAwardSearchResult(SearchResultBase, ArbitralAwardDetail):
    arbitral_institutions: str | None = None
    arbitral_institutions_abbrev: str | None = None
    jurisdictions_alpha_3_code: str | None = None


class ArbitralRuleSearchResult(SearchResultBase, ArbitralRuleDetail):
    arbitral_institutions: str | None = None


class ArbitralInstitutionSearchResult(SearchResultBase, ArbitralInstitutionDetail):
    pass


class ArbitralProvisionSearchResult(SearchResultBase, ArbitralProvisionDetail):
    arbitral_institutions: str | None = None
    arbitral_rules: str | None = None


class DomesticLegalProvisionSearchResult(SearchResultBase, DomesticLegalProvisionDetail):
    legislation_title: str | None = None
    name: str | None = None


class InternationalLegalProvisionSearchResult(SearchResultBase, InternationalLegalProvisionDetail):
    instrument: str | None = None


class RegionalLegalProvisionSearchResult(SearchResultBase, RegionalLegalProvisionDetail):
    instrument: str | None = None


class JurisdictionSearchResult(SearchResultBase, JurisdictionDetail):
    alpha_3_code: str | None = None


class QuestionSearchResult(SearchResultBase, QuestionDetail):
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
