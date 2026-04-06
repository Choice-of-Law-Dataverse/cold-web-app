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
from app.schemas.relations import EntityRelations


class DetailBase(EntityBase):
    id: int
    source_table: str
    relations: EntityRelations = EntityRelations()
    created_at: str | None = None
    updated_at: str | None = None


class AnswerDetail(DetailBase, AnswerBase):
    to_review: str | None = None
    question_cold_id: str | None = None


class HcchAnswerDetail(DetailBase):
    adapted_question: str | None = None
    position: str | None = None
    question_cold_id: str | None = None


class QuestionDetail(DetailBase, QuestionBase):
    primary_theme: str | None = None
    answering_options: str | None = None


class JurisdictionDetail(DetailBase, JurisdictionBase):
    type: str | None = None
    north_south_divide: str | None = None
    jurisdictional_differentiator: str | None = None
    irrelevant: bool | None = None
    done: bool | None = None


class CourtDecisionDetail(DetailBase, CourtDecisionBase):
    id_number: str | None = None
    date: str | None = None
    abstract: str | None = None
    case_rank: str | None = None
    english_translation: str | None = None
    court_s_position: str | None = None
    translated_excerpt: str | None = None
    relevant_facts: str | None = None
    date_of_judgment: str | None = None
    pil_provisions: str | None = None
    original_text: str | None = None
    quote: str | None = None
    text_of_the_relevant_legal_provisions: str | None = None
    official_source_url: str | None = None


class DomesticInstrumentDetail(DetailBase, DomesticInstrumentBase):
    id_number: str | None = None
    official_title: str | None = None
    status: str | None = None
    relevant_provisions: str | None = None
    full_text_of_the_provisions: str | None = None
    publication_date: str | None = None
    entry_into_force: str | None = None
    source_url: str | None = None
    compatible_with_the_hcch_principles: bool | None = None
    compatible_with_the_uncitral_model_law: bool | None = None


class DomesticLegalProvisionDetail(DetailBase, DomesticLegalProvisionBase):
    full_text_of_the_provision_original_language: str | None = None
    full_text_of_the_provision_english_translation: str | None = None
    ranking_display_order: str | None = None
    domestic_instrument_cold_id: str | None = None


class RegionalInstrumentDetail(DetailBase, RegionalInstrumentBase):
    id_number: str | None = None
    url: str | None = None


class RegionalLegalProvisionDetail(DetailBase, RegionalLegalProvisionBase):
    full_text: str | None = None
    instrument_cold_id: str | None = None


class InternationalInstrumentDetail(DetailBase, InternationalInstrumentBase):
    id_number: str | None = None
    url: str | None = None


class InternationalLegalProvisionDetail(DetailBase, InternationalLegalProvisionBase):
    full_text: str | None = None
    ranking_display_order: str | None = None
    instrument_cold_id: str | None = None


class LiteratureDetail(DetailBase, LiteratureBase):
    id_number: str | None = None
    item_type: str | None = None
    abstract_note: str | None = None
    isbn: str | None = None
    issn: str | None = None
    doi: str | None = None
    url: str | None = None
    date: str | None = None
    date_added: str | None = None
    date_modified: str | None = None
    language: str | None = None
    extra: str | None = None
    manual_tags: str | None = None
    editor: str | None = None
    issue: str | None = None
    volume: str | None = None
    pages: str | None = None
    library_catalog: str | None = None
    access_date: str | None = None
    open_access_url: str | None = None
    journal_abbreviation: str | None = None
    short_title: str | None = None
    place: str | None = None
    num_pages: str | None = None
    type: str | None = None
    contributor: str | None = None
    automatic_tags: str | None = None
    number: str | None = None
    series: str | None = None
    series_number: str | None = None
    series_editor: str | None = None
    edition: str | None = None
    call_number: str | None = None
    jurisdiction_summary: str | None = None


class ArbitralAwardDetail(DetailBase, ArbitralAwardBase):
    id_number: str | None = None
    context: str | None = None
    nature_of_the_award: str | None = None
    seat_town: str | None = None
    source: str | None = None


class ArbitralInstitutionDetail(DetailBase, ArbitralInstitutionBase):
    pass


class ArbitralRuleDetail(DetailBase, ArbitralRuleBase):
    id_number: str | None = None
    official_source_url: str | None = None


class ArbitralProvisionDetail(DetailBase, ArbitralProvisionBase):
    full_text_original_language: str | None = None
    full_text_english_translation: str | None = None
    arbitration_method_type: str | None = None
    non_state_law_allowed_in_aoc: str | None = None
    arbitral_rules_cold_id: str | None = None


class SpecialistDetail(DetailBase):
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
    | DetailBase
)

TABLE_DETAIL_MODELS: dict[str, type[DetailBase]] = {
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
