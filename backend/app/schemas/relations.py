from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _RelationBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    cold_id: str | None = None


class AnswerRelation(_RelationBase):
    answer: str | None = None
    more_information: str | None = None


class HcchAnswerRelation(_RelationBase):
    adapted_question: str | None = None
    position: str | None = None


class QuestionRelation(_RelationBase):
    question: str | None = None
    question_number: str | int | None = None
    primary_theme: str | None = None


class JurisdictionRelation(_RelationBase):
    name: str | None = None
    region: str | None = None
    legal_family: str | None = None


class ThemeRelation(_RelationBase):
    theme: str | None = None


class CourtDecisionRelation(_RelationBase):
    case_citation: str | None = None
    case_title: str | None = None
    date: str | None = None


class DomesticInstrumentRelation(_RelationBase):
    title_in_english: str | None = None
    official_title: str | None = None
    abbreviation: str | None = None


class DomesticLegalProvisionRelation(_RelationBase):
    article: str | None = None
    ranking_display_order: str | int | None = None


class RegionalInstrumentRelation(_RelationBase):
    title: str | None = None
    abbreviation: str | None = None


class RegionalLegalProvisionRelation(_RelationBase):
    provision: str | None = None
    title_of_the_provision: str | None = None


class InternationalInstrumentRelation(_RelationBase):
    name: str | None = None


class InternationalLegalProvisionRelation(_RelationBase):
    provision: str | None = None
    title_of_the_provision: str | None = None
    full_text: str | None = None
    ranking_display_order: str | int | None = None


class LiteratureRelation(_RelationBase):
    author: str | None = None
    title: str | None = None
    publication_year: str | int | None = None
    oup_jd_chapter: str | bool | None = None


class ArbitralAwardRelation(_RelationBase):
    case_number: str | None = None
    year: str | int | None = None


class ArbitralInstitutionRelation(_RelationBase):
    institution: str | None = None
    abbreviation: str | None = None


class ArbitralRuleRelation(_RelationBase):
    set_of_rules: str | None = None
    in_force_from: str | None = None


class ArbitralProvisionRelation(_RelationBase):
    article: str | None = None


class SpecialistRelation(_RelationBase):
    specialist: str | None = None
    affiliation: str | None = None


class EntityRelations(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    hcch_answers: list[HcchAnswerRelation] = []
    questions: list[QuestionRelation] = []
    jurisdictions: list[JurisdictionRelation] = []
    themes: list[ThemeRelation] = []
    court_decisions: list[CourtDecisionRelation] = []
    domestic_instruments: list[DomesticInstrumentRelation] = []
    domestic_legal_provisions: list[DomesticLegalProvisionRelation] = []
    regional_instruments: list[RegionalInstrumentRelation] = []
    regional_legal_provisions: list[RegionalLegalProvisionRelation] = []
    international_instruments: list[InternationalInstrumentRelation] = []
    international_legal_provisions: list[InternationalLegalProvisionRelation] = []
    literature: list[LiteratureRelation] = []
    arbitral_awards: list[ArbitralAwardRelation] = []
    arbitral_institutions: list[ArbitralInstitutionRelation] = []
    arbitral_rules: list[ArbitralRuleRelation] = []
    arbitral_provisions: list[ArbitralProvisionRelation] = []
    specialists: list[SpecialistRelation] = []
