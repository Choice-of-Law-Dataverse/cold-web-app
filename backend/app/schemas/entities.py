from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.schemas.records import coerce_bools_to_str


class EntityBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        coerce_numbers_to_str=True,
    )

    _coerce_bools_to_str = coerce_bools_to_str

    cold_id: str | None = None


class AnswerBase(BaseModel):
    answer: str | None = None
    more_information: str | None = None
    oup_book_quote: str | None = None
    jurisdictions_alpha_3_code: str | None = None


class QuestionBase(BaseModel):
    question: str | None = None
    question_number: str | None = None


class JurisdictionBase(BaseModel):
    name: str | None = None
    region: str | None = None
    legal_family: str | None = None
    jurisdiction_summary: str | None = None


class CourtDecisionBase(BaseModel):
    case_title: str | None = None
    case_citation: str | None = None
    publication_date_iso: str | None = None
    instance: str | None = None
    choice_of_law_issue: str | None = None
    official_source_pdf: str | None = None
    jurisdictions_alpha_3_code: str | None = None


class DomesticInstrumentBase(BaseModel):
    title_in_english: str | None = None
    date: str | None = None
    abbreviation: str | None = None
    source_pdf: str | None = None
    jurisdictions_alpha_3_code: str | None = None


class DomesticLegalProvisionBase(BaseModel):
    article: str | None = None


class RegionalInstrumentBase(BaseModel):
    title: str | None = None
    abbreviation: str | None = None
    date: str | None = None
    attachment: str | None = None


class RegionalLegalProvisionBase(BaseModel):
    title_of_the_provision: str | None = None
    provision: str | None = None


class InternationalInstrumentBase(BaseModel):
    name: str | None = None
    date: str | None = None
    attachment: str | None = None


class InternationalLegalProvisionBase(BaseModel):
    title_of_the_provision: str | None = None
    provision: str | None = None


class LiteratureBase(BaseModel):
    title: str | None = None
    author: str | None = None
    publication_year: str | None = None
    publication_title: str | None = None
    publisher: str | None = None
    open_access: str | None = None
    oup_jd_chapter: str | None = None


class ArbitralAwardBase(BaseModel):
    case_number: str | None = None
    award_summary: str | None = None
    year: str | None = None


class ArbitralRuleBase(BaseModel):
    set_of_rules: str | None = None
    in_force_from: str | None = None


class ArbitralInstitutionBase(BaseModel):
    institution: str | None = None
    abbreviation: str | None = None


class ArbitralProvisionBase(BaseModel):
    article: str | None = None
