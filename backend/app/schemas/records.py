from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class RecordBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )

    source_table: str | None = None
    id: str | int | None = None
    rank: float | None = None


class AnswerRecord(RecordBase):
    answer: str | None = None
    created: str | None = None
    record_id: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    to_review: str | None = None
    oup_book_quote: str | None = None
    more_information: str | None = None
    sort_date: str | None = None
    question_link: str | None = None
    question: str | None = None
    number: str | None = None
    questions_theme_code: str | None = None
    jurisdictions_link: str | None = None
    jurisdictions_alpha_3_code: str | None = None
    jurisdictions: str | None = None
    jurisdictions_region: str | None = None
    jurisdictions_irrelevant: bool | None = None
    themes: str | None = None
    court_decisions_id: str | None = None
    court_decisions: str | None = None
    court_decisions_link: str | None = None
    domestic_instruments: str | None = None
    domestic_instruments_id: str | None = None
    domestic_instruments_link: str | None = None
    domestic_legal_provisions: str | None = None
    domestic_legal_provisions_link: str | None = None


class CourtDecisionRecord(RecordBase):
    case_citation: str | None = None
    case_title: str | None = None
    instance: str | None = None
    date: str | None = None
    abstract: str | None = None
    created: str | None = None
    record_id: str | None = None
    id_number: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    added_by_id: str | None = None
    created_time: str | None = None
    answers_link: str | None = None
    answers_question: str | None = None
    text_of_the_relevant_legal_provisions: str | None = None
    quote: str | None = None
    case_rank: str | None = None
    english_translation: str | None = None
    choice_of_law_issue: str | None = None
    court_s_position: str | None = None
    translated_excerpt: str | None = None
    relevant_facts: str | None = None
    date_of_judgment: str | None = None
    pil_provisions: str | None = None
    original_text: str | None = None
    sort_date: str | None = None
    publication_date_iso: str | None = None
    official_source_url: str | None = None
    questions: str | None = None
    jurisdictions_link: str | None = None
    jurisdictions_alpha_3_code: str | None = None
    jurisdictions: str | None = None
    region_from_jurisdictions: str | None = None
    themes: str | None = None
    official_source_pdf: str | None = None
    last_modified_by_email: str | None = None
    last_modified_by_name: str | None = None
    added_by_email: str | None = None
    added_by_name: str | None = None
    created_by_email: str | None = None
    created_by_name: str | None = None


class DomesticInstrumentRecord(RecordBase):
    id_number: str | None = None
    date: str | None = None
    status: str | None = None
    abbreviation: str | None = None
    relevant_provisions: str | None = None
    record_id: str | None = None
    created: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    entry_into_force: str | None = None
    publication_date: str | None = None
    full_text_of_the_provisions: str | None = None
    official_title: str | None = None
    sort_date: str | None = None
    title_in_english: str | None = None
    source_url: str | None = None
    source_pdf: str | None = None
    compatible_with_the_hcch_principles: bool | None = None
    compatible_with_the_uncitral_model_law: bool | None = None
    jurisdictions_link: str | None = None
    jurisdictions_alpha_3_code: str | None = None
    jurisdictions: str | None = None
    type_from_jurisdictions: str | None = None
    question_id: str | None = None
    answers_link: str | None = None
    domestic_legal_provisions_link: str | None = None
    domestic_legal_provisions_full_text_of_the_provision_english_t: str | None = None
    domestic_legal_provisions_full_text_of_the_provision_original: str | None = None
    domestic_legal_provisions: str | None = None
    last_modified_by_email: str | None = None
    last_modified_by_name: str | None = None
    created_by_email: str | None = None
    created_by_name: str | None = None


class InternationalInstrumentRecord(RecordBase):
    id_number: str | None = None
    title: str | None = None
    abbreviation: str | None = None
    date: str | None = None
    status: str | None = None
    url: str | None = None
    attachment: str | None = None
    record_id: str | None = None
    created: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    entry_into_force: str | None = None
    publication_date: str | None = None
    relevant_provisions: str | None = None
    full_text_of_the_provisions: str | None = None
    name: str | None = None
    sort_date: str | None = None
    title_in_english: str | None = None
    source_url: str | None = None
    source_pdf: str | None = None
    specialists: str | None = None
    specialists_link: str | None = None
    international_legal_provisions: str | None = None
    international_legal_provisions_link: str | None = None
    literature: str | None = None
    literature_link: str | None = None
    hcch_answers: str | None = None
    hcch_answers_link: str | None = None
    last_modified_by_email: str | None = None
    last_modified_by_name: str | None = None
    created_by_email: str | None = None
    created_by_name: str | None = None


class RegionalInstrumentRecord(RecordBase):
    id_number: str | None = None
    title: str | None = None
    abbreviation: str | None = None
    date: str | None = None
    url: str | None = None
    attachment: str | None = None
    record_id: str | None = None
    created: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    sort_date: str | None = None
    specialists: str | None = None
    specialists_link: str | None = None
    regional_legal_provisions: str | None = None
    regional_legal_provisions_link: str | None = None
    last_modified_by_email: str | None = None
    last_modified_by_name: str | None = None
    created_by_email: str | None = None
    created_by_name: str | None = None


class LiteratureRecord(RecordBase):
    record_id: str | None = None
    cold_id: str | None = None
    key: str | None = None
    item_type: str | None = None
    publication_year: str | None = None
    author: str | None = None
    title: str | None = None
    isbn: str | None = None
    issn: str | None = None
    url: str | None = None
    date: str | None = None
    date_added: str | None = None
    date_modified: str | None = None
    publisher: str | None = None
    language: str | None = None
    extra: str | None = None
    manual_tags: str | None = None
    editor: str | None = None
    last_modified: str | None = None
    created: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    publication_title: str | None = None
    issue: str | None = None
    volume: str | None = None
    pages: str | None = None
    abstract_note: str | None = None
    library_catalog: str | None = None
    doi: str | None = None
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
    answers: str | None = None
    sort_date: str | None = None
    jurisdiction_link: str | None = None
    jurisdiction: str | None = None
    themes: str | None = None
    themes_link: str | None = None
    international_instruments: str | None = None
    international_instruments_link: str | None = None
    international_legal_provisions: str | None = None
    international_legal_provisions_link: str | None = None
    last_modified_by_email: str | None = None
    last_modified_by_name: str | None = None
    created_by_email: str | None = None
    created_by_name: str | None = None


class ArbitralAwardRecord(RecordBase):
    record_id: str | None = None
    case_number: str | None = None
    context: str | None = None
    award_summary: str | None = None
    year: str | None = None
    nature_of_the_award: str | None = None
    seat_town: str | None = None
    source: str | None = None
    created: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    sort_date: str | None = None
    arbitral_institutions: str | None = None
    arbitral_institutions_abbrev: str | None = None
    arbitral_institutions_link: str | None = None
    arbitral_provisions_articles: str | None = None
    arbitral_provisions_link: str | None = None
    court_decisions: str | None = None
    court_decisions_link: str | None = None
    jurisdictions: str | None = None
    jurisdictions_alpha_3_code: str | None = None
    jurisdictions_link: str | None = None
    themes: str | None = None
    related_arbitral_institutions: list[dict[str, str | None]] | None = None
    related_jurisdictions: list[dict[str, str | None]] | None = None
    related_themes: list[dict[str, str | None]] | None = None


class ArbitralInstitutionRecord(RecordBase):
    record_id: str | None = None
    institution: str | None = None
    abbreviation: str | None = None
    created: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    arbitral_awards: str | None = None
    arbitral_awards_link: str | None = None
    arbitral_rules: str | None = None
    arbitral_rules_in_force_from: str | None = None
    arbitral_rules_link: str | None = None
    arbitral_provisions_articles: str | None = None
    arbitral_provisions_link: str | None = None
    jurisdictions: str | None = None
    jurisdictions_alpha_3_code: str | None = None
    jurisdictions_link: str | None = None


class ArbitralProvisionRecord(RecordBase):
    record_id: str | None = None
    arbitral_rules_id: str | None = None
    article: str | None = None
    full_text_original_language: str | None = None
    full_text_english_translation: str | None = None
    arbitration_method_type: str | None = None
    non_state_law_allowed_in_aoc: str | None = None
    created: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    arbitral_awards: str | None = None
    arbitral_awards_link: str | None = None
    arbitral_institutions: str | None = None
    arbitral_institutions_abbrev: str | None = None
    arbitral_institutions_link: str | None = None
    arbitral_rules: str | None = None
    arbitral_rules_in_force_from: str | None = None
    arbitral_rules_link: str | None = None


class ArbitralRuleRecord(RecordBase):
    record_id: str | None = None
    set_of_rules: str | None = None
    in_force_from: str | None = None
    official_source_url: str | None = None
    created: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    arbitral_institutions: str | None = None
    arbitral_institutions_abbrev: str | None = None
    arbitral_institutions_link: str | None = None
    arbitral_provisions_articles: str | None = None
    arbitral_provisions_link: str | None = None
    jurisdictions: str | None = None
    jurisdictions_alpha_3_code: str | None = None
    jurisdictions_link: str | None = None
    related_arbitral_institutions: list[dict[str, str | None]] | None = None


class DomesticLegalProvisionRecord(RecordBase):
    name: str | None = None
    article: str | None = None
    full_text_of_the_provision_original_language: str | None = None
    full_text_of_the_provision_english_translation: str | None = None
    record_id: str | None = None
    last_modified: str | None = None
    created: str | None = None
    ranking_display_order: str | None = None
    domestic_instruments_link: str | None = None
    legislation_title: str | None = None
    answers: str | None = None
    questions: str | None = None
    themes_link: str | None = None
    jurisdictions_link: str | None = None
    jurisdictions: str | None = None
    last_modified_by_id: str | None = None
    last_modified_by_email: str | None = None
    last_modified_by_name: str | None = None
    created_by_id: str | None = None
    created_by_email: str | None = None
    created_by_name: str | None = None


class InternationalLegalProvisionRecord(RecordBase):
    cold_id: str | None = None
    title_of_the_provision: str | None = None
    full_text: str | None = None
    provision: str | None = None
    record_id: str | None = None
    created: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    ranking_display_order: str | None = None
    nc_order: str | None = None
    nc_record_hash: str | None = None
    arbitral_awards: str | None = None
    instrument_cold_id: str | None = None
    international_instruments_copy: str | None = None
    sort_date: str | None = None
    instrument: str | None = None
    last_modified_by_email: str | None = None
    last_modified_by_name: str | None = None
    created_by_email: str | None = None
    created_by_name: str | None = None


class RegionalLegalProvisionRecord(RecordBase):
    title_of_the_provision: str | None = None
    full_text: str | None = None
    provision: str | None = None
    record_id: str | None = None
    created: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    sort_date: str | None = None
    instrument: str | None = None
    instrument_link: str | None = None
    questions: str | None = None
    last_modified_by_email: str | None = None
    last_modified_by_name: str | None = None
    created_by_email: str | None = None
    created_by_name: str | None = None


class JurisdictionRecord(RecordBase):
    cold_id: str | None = None
    name: str | None = None
    alpha_3_code: str | None = None
    type: str | None = None
    region: str | None = None
    north_south_divide: str | None = None
    jurisdictional_differentiator: str | None = None
    record_id: str | None = None
    created: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    jurisdiction_summary: str | None = None
    legal_family: str | None = None
    answer_coverage: str | None = None
    irrelevant: bool | None = None
    done: bool | None = None


class QuestionRecord(RecordBase):
    question: str | None = None
    question_number: str | None = None
    created: str | None = None
    record_id: str | None = None
    theme_code: str | None = None
    answering_options: str | None = None
    last_modified: str | None = None
    last_modified_by_id: str | None = None
    created_by_id: str | None = None
    sort_date: str | None = None
    themes: str | None = None


TABLE_RECORD_MODELS: dict[str, type[RecordBase]] = {
    "Answers": AnswerRecord,
    "Court Decisions": CourtDecisionRecord,
    "Domestic Instruments": DomesticInstrumentRecord,
    "International Instruments": InternationalInstrumentRecord,
    "Regional Instruments": RegionalInstrumentRecord,
    "Literature": LiteratureRecord,
    "Arbitral Awards": ArbitralAwardRecord,
    "Arbitral Institutions": ArbitralInstitutionRecord,
    "Arbitral Provisions": ArbitralProvisionRecord,
    "Arbitral Rules": ArbitralRuleRecord,
    "Domestic Legal Provisions": DomesticLegalProvisionRecord,
    "International Legal Provisions": InternationalLegalProvisionRecord,
    "Regional Legal Provisions": RegionalLegalProvisionRecord,
    "Jurisdictions": JurisdictionRecord,
    "Questions": QuestionRecord,
}

AnyRecord = (
    AnswerRecord
    | CourtDecisionRecord
    | DomesticInstrumentRecord
    | InternationalInstrumentRecord
    | RegionalInstrumentRecord
    | LiteratureRecord
    | ArbitralAwardRecord
    | ArbitralInstitutionRecord
    | ArbitralProvisionRecord
    | ArbitralRuleRecord
    | DomesticLegalProvisionRecord
    | InternationalLegalProvisionRecord
    | RegionalLegalProvisionRecord
    | JurisdictionRecord
    | QuestionRecord
    | RecordBase
)


def validate_record(data: dict) -> AnyRecord:
    source_table = data.get("source_table", "")
    model = TABLE_RECORD_MODELS.get(source_table, RecordBase)
    return model(**data)  # type: ignore[return-value]
