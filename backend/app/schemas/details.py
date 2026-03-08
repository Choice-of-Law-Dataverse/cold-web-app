from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.schemas.records import coerce_bools_to_str
from app.schemas.relations import EntityRelations


class _DetailBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        coerce_numbers_to_str=True,
    )

    _coerce_bools_to_str = coerce_bools_to_str

    id: int
    cold_id: str | None = None
    source_table: str
    relations: EntityRelations = EntityRelations()
    created_at: str | None = None
    updated_at: str | None = None
    created_by: str | None = None
    updated_by: str | None = None


class AnswerDetail(_DetailBase):
    answer: str | None = None
    more_information: str | None = None
    to_review: str | None = None
    oup_book_quote: str | None = None
    jurisdictions_alpha_3_code: str | None = None
    question_cold_id: str | None = None


class HcchAnswerDetail(_DetailBase):
    adapted_question: str | None = None
    position: str | None = None
    question_cold_id: str | None = None


class QuestionDetail(_DetailBase):
    question: str | None = None
    question_number: str | None = None
    primary_theme: str | None = None
    answering_options: str | None = None


class JurisdictionDetail(_DetailBase):
    name: str | None = None
    type: str | None = None
    region: str | None = None
    north_south_divide: str | None = None
    jurisdictional_differentiator: str | None = None
    legal_family: str | None = None
    jurisdiction_summary: str | None = None
    irrelevant: bool | None = None
    done: bool | None = None


class CourtDecisionDetail(_DetailBase):
    id_number: str | None = None
    case_citation: str | None = None
    case_title: str | None = None
    instance: str | None = None
    date: str | None = None
    abstract: str | None = None
    case_rank: str | None = None
    english_translation: str | None = None
    choice_of_law_issue: str | None = None
    court_s_position: str | None = None
    translated_excerpt: str | None = None
    relevant_facts: str | None = None
    date_of_judgment: str | None = None
    pil_provisions: str | None = None
    original_text: str | None = None
    quote: str | None = None
    text_of_the_relevant_legal_provisions: str | None = None
    official_source_url: str | None = None
    official_source_pdf: str | None = None
    publication_date_iso: str | None = None
    jurisdictions_alpha_3_code: str | None = None


class DomesticInstrumentDetail(_DetailBase):
    id_number: str | None = None
    title_in_english: str | None = None
    official_title: str | None = None
    date: str | None = None
    status: str | None = None
    abbreviation: str | None = None
    relevant_provisions: str | None = None
    full_text_of_the_provisions: str | None = None
    publication_date: str | None = None
    entry_into_force: str | None = None
    source_url: str | None = None
    source_pdf: str | None = None
    compatible_with_the_hcch_principles: bool | None = None
    compatible_with_the_uncitral_model_law: bool | None = None
    jurisdictions_alpha_3_code: str | None = None


class DomesticLegalProvisionDetail(_DetailBase):
    article: str | None = None
    full_text_of_the_provision_original_language: str | None = None
    full_text_of_the_provision_english_translation: str | None = None
    ranking_display_order: str | None = None
    domestic_instrument_cold_id: str | None = None


class RegionalInstrumentDetail(_DetailBase):
    id_number: str | None = None
    title: str | None = None
    abbreviation: str | None = None
    date: str | None = None
    url: str | None = None
    attachment: str | None = None


class RegionalLegalProvisionDetail(_DetailBase):
    provision: str | None = None
    title_of_the_provision: str | None = None
    full_text: str | None = None
    instrument_cold_id: str | None = None


class InternationalInstrumentDetail(_DetailBase):
    id_number: str | None = None
    name: str | None = None
    date: str | None = None
    url: str | None = None
    attachment: str | None = None


class InternationalLegalProvisionDetail(_DetailBase):
    provision: str | None = None
    title_of_the_provision: str | None = None
    full_text: str | None = None
    ranking_display_order: str | None = None
    instrument_cold_id: str | None = None


class LiteratureDetail(_DetailBase):
    id_number: str | None = None
    item_type: str | None = None
    publication_year: str | None = None
    author: str | None = None
    title: str | None = None
    publication_title: str | None = None
    abstract_note: str | None = None
    isbn: str | None = None
    issn: str | None = None
    doi: str | None = None
    url: str | None = None
    date: str | None = None
    date_added: str | None = None
    date_modified: str | None = None
    publisher: str | None = None
    language: str | None = None
    extra: str | None = None
    manual_tags: str | None = None
    editor: str | None = None
    issue: str | None = None
    volume: str | None = None
    pages: str | None = None
    library_catalog: str | None = None
    access_date: str | None = None
    open_access: str | None = None
    open_access_url: str | None = None
    journal_abbreviation: str | None = None
    short_title: str | None = None
    place: str | None = None
    num_pages: str | None = None
    type: str | None = None
    oup_jd_chapter: str | None = None
    contributor: str | None = None
    automatic_tags: str | None = None
    number: str | None = None
    series: str | None = None
    series_number: str | None = None
    series_editor: str | None = None
    edition: str | None = None
    call_number: str | None = None
    jurisdiction_summary: str | None = None


class ArbitralAwardDetail(_DetailBase):
    id_number: str | None = None
    case_number: str | None = None
    context: str | None = None
    award_summary: str | None = None
    year: str | None = None
    nature_of_the_award: str | None = None
    seat_town: str | None = None
    source: str | None = None


class ArbitralInstitutionDetail(_DetailBase):
    institution: str | None = None
    abbreviation: str | None = None


class ArbitralRuleDetail(_DetailBase):
    id_number: str | None = None
    set_of_rules: str | None = None
    in_force_from: str | None = None
    official_source_url: str | None = None


class ArbitralProvisionDetail(_DetailBase):
    article: str | None = None
    full_text_original_language: str | None = None
    full_text_english_translation: str | None = None
    arbitration_method_type: str | None = None
    non_state_law_allowed_in_aoc: str | None = None
    arbitral_rules_cold_id: str | None = None


class SpecialistDetail(_DetailBase):
    specialist: str | None = None
    affiliation: str | None = None
    contact: str | None = None
    bio: str | None = None
    website: str | None = None


AnyDetail = (
    AnswerDetail
    | HcchAnswerDetail
    | QuestionDetail
    | JurisdictionDetail
    | CourtDecisionDetail
    | DomesticInstrumentDetail
    | DomesticLegalProvisionDetail
    | RegionalInstrumentDetail
    | RegionalLegalProvisionDetail
    | InternationalInstrumentDetail
    | InternationalLegalProvisionDetail
    | LiteratureDetail
    | ArbitralAwardDetail
    | ArbitralInstitutionDetail
    | ArbitralRuleDetail
    | ArbitralProvisionDetail
    | SpecialistDetail
    | _DetailBase
)

TABLE_DETAIL_MODELS: dict[str, type[_DetailBase]] = {
    "Answers": AnswerDetail,
    "HCCH Answers": HcchAnswerDetail,
    "Questions": QuestionDetail,
    "Jurisdictions": JurisdictionDetail,
    "Court Decisions": CourtDecisionDetail,
    "Domestic Instruments": DomesticInstrumentDetail,
    "Domestic Legal Provisions": DomesticLegalProvisionDetail,
    "Regional Instruments": RegionalInstrumentDetail,
    "Regional Legal Provisions": RegionalLegalProvisionDetail,
    "International Instruments": InternationalInstrumentDetail,
    "International Legal Provisions": InternationalLegalProvisionDetail,
    "Literature": LiteratureDetail,
    "Arbitral Awards": ArbitralAwardDetail,
    "Arbitral Institutions": ArbitralInstitutionDetail,
    "Arbitral Rules": ArbitralRuleDetail,
    "Arbitral Provisions": ArbitralProvisionDetail,
    "Specialists": SpecialistDetail,
}
