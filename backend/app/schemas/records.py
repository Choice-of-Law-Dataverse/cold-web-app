import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, create_model

from app.mapping.configs import ALL_MAPPINGS
from app.schemas.mapping_schema import MappingConfig

_SKIP_FIELDS = {"source_table", "id", "rank", "ID"}


class RecordBase(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    source_table: str | None = None
    id: str | int | None = None
    rank: float | None = None


def _extract_output_fields(config: MappingConfig) -> dict[str, type]:
    fields: dict[str, type] = {}
    m = config.mappings

    for name in m.direct_mappings:
        if name not in _SKIP_FIELDS:
            fields[name] = str

    for name in m.conditional_mappings:
        if name not in _SKIP_FIELDS:
            fields[name] = str

    for name in m.boolean_mappings:
        fields[name] = bool

    for name in m.complex_mappings:
        fields[name] = str

    for key, nested in m.nested_mappings.items():
        if key.startswith("hop1_relations."):
            continue
        if nested.mappings:
            for name in nested.mappings:
                if name not in _SKIP_FIELDS:
                    fields[name] = str
        if nested.array_operations:
            for name in nested.array_operations:
                fields[name] = str
        if nested.conditional_mappings:
            for name in nested.conditional_mappings:
                fields[name] = str
        if nested.boolean_mappings:
            for name in nested.boolean_mappings:
                fields[name] = bool

    for user_mapping in m.user_mappings.values():
        for name in user_mapping.user_fields:
            fields[name] = str

    return fields


def _to_python_name(name: str) -> str:
    result = re.sub(r"[^a-zA-Z0-9]", "_", name)
    result = re.sub(r"_+", "_", result)
    result = result.strip("_").lower()
    if not result or result[0].isdigit():
        result = f"f_{result}"
    return result


def _build_record_model(model_name: str, config: MappingConfig) -> type[RecordBase]:
    output_fields = _extract_output_fields(config)

    field_defs: dict[str, Any] = {}
    seen: set[str] = {"source_table", "id", "rank"}

    for field_name, field_type in sorted(output_fields.items()):
        py_name = _to_python_name(field_name)
        if py_name in seen:
            continue
        seen.add(py_name)

        optional_type = field_type | None
        if py_name == field_name:
            field_defs[py_name] = (optional_type, None)
        else:
            field_defs[py_name] = (optional_type, Field(None, alias=field_name))

    return create_model(model_name, __base__=RecordBase, **field_defs)  # type: ignore[return-value]


AnswerRecord = _build_record_model("AnswerRecord", ALL_MAPPINGS["Answers"])
CourtDecisionRecord = _build_record_model("CourtDecisionRecord", ALL_MAPPINGS["Court Decisions"])
DomesticInstrumentRecord = _build_record_model("DomesticInstrumentRecord", ALL_MAPPINGS["Domestic Instruments"])
InternationalInstrumentRecord = _build_record_model("InternationalInstrumentRecord", ALL_MAPPINGS["International Instruments"])
RegionalInstrumentRecord = _build_record_model("RegionalInstrumentRecord", ALL_MAPPINGS["Regional Instruments"])
LiteratureRecord = _build_record_model("LiteratureRecord", ALL_MAPPINGS["Literature"])
ArbitralAwardRecord = _build_record_model("ArbitralAwardRecord", ALL_MAPPINGS["Arbitral Awards"])
ArbitralInstitutionRecord = _build_record_model("ArbitralInstitutionRecord", ALL_MAPPINGS["Arbitral Institutions"])
ArbitralProvisionRecord = _build_record_model("ArbitralProvisionRecord", ALL_MAPPINGS["Arbitral Provisions"])
ArbitralRuleRecord = _build_record_model("ArbitralRuleRecord", ALL_MAPPINGS["Arbitral Rules"])
DomesticLegalProvisionRecord = _build_record_model("DomesticLegalProvisionRecord", ALL_MAPPINGS["Domestic Legal Provisions"])
InternationalLegalProvisionRecord = _build_record_model(
    "InternationalLegalProvisionRecord", ALL_MAPPINGS["International Legal Provisions"]
)
RegionalLegalProvisionRecord = _build_record_model("RegionalLegalProvisionRecord", ALL_MAPPINGS["Regional Legal Provisions"])
JurisdictionRecord = _build_record_model("JurisdictionRecord", ALL_MAPPINGS["Jurisdictions"])
QuestionRecord = _build_record_model("QuestionRecord", ALL_MAPPINGS["Questions"])

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
