from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.schemas.records import coerce_bools_to_str


class EntityBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        coerce_numbers_to_str=True,
    )

    _coerce_bools_to_str = coerce_bools_to_str

    cold_id: str | None = Field(default=None, description="CoLD unique identifier (e.g. 'CD-CHE-42', 'DI-FRA-3').")


class AnswerBase(EntityBase):
    answer: str | None = Field(default=None, description="The substantive answer text, or 'No data'.")
    more_information: str | None = Field(default=None, description="Additional context or commentary on the answer.")
    oup_book_quote: str | None = Field(default=None, description="Relevant quote from the OUP companion publication.")
    jurisdictions_alpha_3_code: str | None = Field(
        default=None, description="ISO 3166-1 Alpha-3 code of the answering jurisdiction."
    )


class QuestionBase(EntityBase):
    question: str | None = Field(default=None, description="The standardised questionnaire item text.")
    question_number: str | None = Field(default=None, description="Question number within the questionnaire (e.g. '15-TC').")


class JurisdictionBase(EntityBase):
    name: str | None = Field(default=None, description="Full jurisdiction name (e.g. 'Switzerland').")
    region: str | None = Field(default=None, description="Geographic region (e.g. 'Europe', 'Asia').")
    legal_family: str | None = Field(default=None, description="Legal tradition (e.g. 'Civil Law', 'Common Law', 'Mixed').")
    jurisdiction_summary: str | None = Field(default=None, description="Brief overview of the jurisdiction's PIL framework.")


class CourtDecisionBase(EntityBase):
    case_title: str | None = Field(default=None, description="Title or short name of the court decision.")
    case_citation: str | None = Field(default=None, description="Formal case citation reference.")
    publication_date_iso: str | None = Field(default=None, description="Publication date in ISO 8601 format.")
    instance: str | None = Field(default=None, description="Court instance (e.g. 'Supreme Court', 'Court of Appeal').")
    choice_of_law_issue: str | None = Field(default=None, description="The choice-of-law issue addressed by the court.")
    official_source_pdf: str | None = Field(default=None, description="URL to the official source PDF.")
    jurisdictions_alpha_3_code: str | None = Field(default=None, description="Alpha-3 code of the jurisdiction.")


class DomesticInstrumentBase(EntityBase):
    title_in_english: str | None = Field(default=None, description="English title of the domestic legislation.")
    date: str | None = Field(default=None, description="Date of enactment or last amendment.")
    abbreviation: str | None = Field(default=None, description="Common abbreviation (e.g. 'IPRG', 'Rome I').")
    source_pdf: str | None = Field(default=None, description="URL to the source PDF.")
    jurisdictions_alpha_3_code: str | None = Field(default=None, description="Alpha-3 code of the jurisdiction.")


class DomesticLegalProvisionBase(EntityBase):
    article: str | None = Field(default=None, description="Article number or section reference.")


class RegionalInstrumentBase(EntityBase):
    title: str | None = Field(default=None, description="Title of the regional instrument.")
    abbreviation: str | None = Field(default=None, description="Common abbreviation (e.g. 'Rome I').")
    date: str | None = Field(default=None, description="Date of adoption or entry into force.")
    attachment: str | None = Field(default=None, description="URL to an attached document.")


class RegionalLegalProvisionBase(EntityBase):
    title_of_the_provision: str | None = Field(default=None, description="Title or heading of the provision.")
    provision: str | None = Field(default=None, description="Article or section reference.")


class InternationalInstrumentBase(EntityBase):
    name: str | None = Field(default=None, description="Name of the international instrument.")
    date: str | None = Field(default=None, description="Date of adoption or entry into force.")
    attachment: str | None = Field(default=None, description="URL to an attached document.")


class InternationalLegalProvisionBase(EntityBase):
    title_of_the_provision: str | None = Field(default=None, description="Title or heading of the provision.")
    provision: str | None = Field(default=None, description="Article or section reference.")


class LiteratureBase(EntityBase):
    title: str | None = Field(default=None, description="Title of the publication.")
    author: str | None = Field(default=None, description="Author name(s).")
    publication_year: str | None = Field(default=None, description="Year of publication.")
    publication_title: str | None = Field(default=None, description="Journal or book title.")
    publisher: str | None = Field(default=None, description="Publisher name.")
    open_access: str | None = Field(default=None, description="Whether the work is open access.")
    oup_jd_chapter: str | None = Field(default=None, description="OUP Juris Diversitas chapter reference.")


class ArbitralAwardBase(EntityBase):
    case_number: str | None = Field(default=None, description="Arbitral case number.")
    award_summary: str | None = Field(default=None, description="Summary of the award's choice-of-law analysis.")
    year: str | None = Field(default=None, description="Year the award was rendered.")


class ArbitralRuleBase(EntityBase):
    set_of_rules: str | None = Field(default=None, description="Name of the arbitration rules set.")
    in_force_from: str | None = Field(default=None, description="Date from which these rules are in force.")


class ArbitralInstitutionBase(EntityBase):
    institution: str | None = Field(default=None, description="Full name of the arbitration institution.")
    abbreviation: str | None = Field(default=None, description="Common abbreviation (e.g. 'ICC', 'LCIA').")


class ArbitralProvisionBase(EntityBase):
    article: str | None = Field(default=None, description="Article number or section reference within the rules.")
