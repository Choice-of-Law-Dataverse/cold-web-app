from typing import Any

from pydantic import BaseModel, ConfigDict, create_model
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


_OPT_STR = (str | None, None)


def _pick(
    model_name: str,
    detail: type[BaseModel],
    *fields: str,
    **extras: tuple[Any, Any],
) -> type[SearchResultBase]:
    picked: dict[str, Any] = {}
    for field_name in fields:
        info = detail.model_fields[field_name]
        picked[field_name] = (info.annotation, info.default)
    picked.update(extras)
    return create_model(model_name, __base__=SearchResultBase, **picked)  # type: ignore[return-value]


AnswerSearchResult = _pick(
    "AnswerSearchResult",
    AnswerDetail,
    "answer",
    "more_information",
    "oup_book_quote",
    "jurisdictions_alpha_3_code",
    question=_OPT_STR,
    court_decisions_link=_OPT_STR,
    last_modified=_OPT_STR,
    created=_OPT_STR,
    questions_theme_code=_OPT_STR,
)

CourtDecisionSearchResult = _pick(
    "CourtDecisionSearchResult",
    CourtDecisionDetail,
    "case_title",
    "case_citation",
    "publication_date_iso",
    "instance",
    "choice_of_law_issue",
    "official_source_pdf",
    "jurisdictions_alpha_3_code",
    source_pdf=_OPT_STR,
)

DomesticInstrumentSearchResult = _pick(
    "DomesticInstrumentSearchResult",
    DomesticInstrumentDetail,
    "title_in_english",
    "date",
    "abbreviation",
    "source_pdf",
    "jurisdictions_alpha_3_code",
    official_source_pdf=_OPT_STR,
    domestic_legal_provisions_themes=_OPT_STR,
)

RegionalInstrumentSearchResult = _pick(
    "RegionalInstrumentSearchResult",
    RegionalInstrumentDetail,
    "abbreviation",
    "date",
    "title",
    "attachment",
)

InternationalInstrumentSearchResult = _pick(
    "InternationalInstrumentSearchResult",
    InternationalInstrumentDetail,
    "name",
    "date",
    "attachment",
    official_source_pdf=_OPT_STR,
    source_pdf=_OPT_STR,
)

LiteratureSearchResult = _pick(
    "LiteratureSearchResult",
    LiteratureDetail,
    "title",
    "author",
    "publication_year",
    "publication_title",
    "publisher",
    "open_access",
    "oup_jd_chapter",
)

ArbitralAwardSearchResult = _pick(
    "ArbitralAwardSearchResult",
    ArbitralAwardDetail,
    "case_number",
    "award_summary",
    "year",
    arbitral_institutions=_OPT_STR,
    arbitral_institutions_abbrev=_OPT_STR,
    jurisdictions_alpha_3_code=_OPT_STR,
)

ArbitralRuleSearchResult = _pick(
    "ArbitralRuleSearchResult",
    ArbitralRuleDetail,
    "set_of_rules",
    "in_force_from",
    arbitral_institutions=_OPT_STR,
)

ArbitralInstitutionSearchResult = _pick(
    "ArbitralInstitutionSearchResult",
    ArbitralInstitutionDetail,
    "institution",
    "abbreviation",
)

ArbitralProvisionSearchResult = _pick(
    "ArbitralProvisionSearchResult",
    ArbitralProvisionDetail,
    "article",
    arbitral_institutions=_OPT_STR,
    arbitral_rules=_OPT_STR,
)

DomesticLegalProvisionSearchResult = _pick(
    "DomesticLegalProvisionSearchResult",
    DomesticLegalProvisionDetail,
    "article",
    legislation_title=_OPT_STR,
    name=_OPT_STR,
)

InternationalLegalProvisionSearchResult = _pick(
    "InternationalLegalProvisionSearchResult",
    InternationalLegalProvisionDetail,
    "title_of_the_provision",
    "provision",
    instrument=_OPT_STR,
)

RegionalLegalProvisionSearchResult = _pick(
    "RegionalLegalProvisionSearchResult",
    RegionalLegalProvisionDetail,
    "title_of_the_provision",
    "provision",
    instrument=_OPT_STR,
)

JurisdictionSearchResult = _pick(
    "JurisdictionSearchResult",
    JurisdictionDetail,
    "name",
    "region",
    "legal_family",
    "jurisdiction_summary",
    alpha_3_code=_OPT_STR,
)

QuestionSearchResult = _pick(
    "QuestionSearchResult",
    QuestionDetail,
    "question",
    "question_number",
    theme_code=_OPT_STR,
)


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
