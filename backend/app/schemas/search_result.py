from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.schemas.records import coerce_bools_to_str


class SearchResultBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
        coerce_numbers_to_str=True,
    )

    _coerce_bools_to_str = coerce_bools_to_str

    source_table: str | None = None
    id: str | int | None = None
    cold_id: str | None = None
    rank: float | None = None
    result_date: str | None = None
    jurisdictions: str | None = None
    themes: str | None = None


class AnswerSearchResult(SearchResultBase):
    answer: str | None = None
    question: str | None = None
    more_information: str | None = None
    oup_book_quote: str | None = None
    court_decisions_link: str | None = None
    last_modified: str | None = None
    created: str | None = None
    jurisdictions_alpha_3_code: str | None = None
    questions_theme_code: str | None = None


class CourtDecisionSearchResult(SearchResultBase):
    case_title: str | None = None
    case_citation: str | None = None
    publication_date_iso: str | None = None
    instance: str | None = None
    choice_of_law_issue: str | None = None
    official_source_pdf: str | None = None
    source_pdf: str | None = None
    jurisdictions_alpha_3_code: str | None = None


class DomesticInstrumentSearchResult(SearchResultBase):
    title_in_english: str | None = None
    date: str | None = None
    abbreviation: str | None = None
    official_source_pdf: str | None = None
    source_pdf: str | None = None
    jurisdictions_alpha_3_code: str | None = None
    domestic_legal_provisions_themes: str | None = None


class RegionalInstrumentSearchResult(SearchResultBase):
    abbreviation: str | None = None
    date: str | None = None
    title: str | None = None
    attachment: str | None = None


class InternationalInstrumentSearchResult(SearchResultBase):
    name: str | None = None
    date: str | None = None
    official_source_pdf: str | None = None
    source_pdf: str | None = None
    attachment: str | None = None


class LiteratureSearchResult(SearchResultBase):
    title: str | None = None
    author: str | None = None
    publication_year: str | None = None
    publication_title: str | None = None
    publisher: str | None = None
    open_access: str | None = None
    oup_jd_chapter: str | None = None


class ArbitralAwardSearchResult(SearchResultBase):
    case_number: str | None = None
    arbitral_institutions: str | None = None
    arbitral_institutions_abbrev: str | None = None
    award_summary: str | None = None
    year: str | None = None
    jurisdictions_alpha_3_code: str | None = None


class ArbitralRuleSearchResult(SearchResultBase):
    set_of_rules: str | None = None
    arbitral_institutions: str | None = None
    in_force_from: str | None = None


class ArbitralInstitutionSearchResult(SearchResultBase):
    institution: str | None = None
    abbreviation: str | None = None


class ArbitralProvisionSearchResult(SearchResultBase):
    article: str | None = None
    arbitral_institutions: str | None = None
    arbitral_rules: str | None = None


class DomesticLegalProvisionSearchResult(SearchResultBase):
    article: str | None = None
    legislation_title: str | None = None
    name: str | None = None


class InternationalLegalProvisionSearchResult(SearchResultBase):
    title_of_the_provision: str | None = None
    provision: str | None = None
    instrument: str | None = None


class RegionalLegalProvisionSearchResult(SearchResultBase):
    title_of_the_provision: str | None = None
    provision: str | None = None
    instrument: str | None = None


class JurisdictionSearchResult(SearchResultBase):
    name: str | None = None
    alpha_3_code: str | None = None
    region: str | None = None
    legal_family: str | None = None
    jurisdiction_summary: str | None = None


class QuestionSearchResult(SearchResultBase):
    question: str | None = None
    question_number: str | None = None
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
