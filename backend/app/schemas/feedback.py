from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel


class EntityType(StrEnum):
    COURT_DECISION = "court_decision"
    DOMESTIC_INSTRUMENT = "domestic_instrument"
    REGIONAL_INSTRUMENT = "regional_instrument"
    INTERNATIONAL_INSTRUMENT = "international_instrument"
    LITERATURE = "literature"
    ARBITRAL_AWARD = "arbitral_award"
    ARBITRAL_RULE = "arbitral_rule"
    QUESTION = "question"
    JURISDICTION = "jurisdiction"


class FeedbackType(StrEnum):
    IMPROVE = "improve"
    MISSING_DATA = "missing_data"
    WRONG_INFO = "wrong_info"
    OUTDATED = "outdated"
    OTHER = "other"


class FeedbackModerationStatus(StrEnum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"


class FeedbackSubmit(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    entity_type: EntityType
    entity_id: str = Field(..., max_length=256)
    entity_title: str | None = Field(None, max_length=512)
    feedback_type: FeedbackType
    message: str = Field(..., min_length=1)
    submitter_email: EmailStr


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int


class FeedbackDetail(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    created_at: datetime
    entity_type: str
    entity_id: str
    entity_title: str | None
    feedback_type: str
    message: str
    submitter_email: str
    token_sub: str | None
    moderation_status: str


class FeedbackPendingItem(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    created_at: datetime
    entity_type: str
    entity_id: str
    entity_title: str | None
    feedback_type: str
    message: str
    submitter_email: str
    moderation_status: str


class FeedbackUpdate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    moderation_status: FeedbackModerationStatus
