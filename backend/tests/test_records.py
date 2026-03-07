import pytest

from app.mapping.configs import ALL_MAPPINGS
from app.schemas.records import (
    TABLE_RECORD_MODELS,
    AnswerRecord,
    ArbitralAwardRecord,
    CourtDecisionRecord,
    DomesticInstrumentRecord,
    InternationalInstrumentRecord,
    JurisdictionRecord,
    LiteratureRecord,
    QuestionRecord,
    RecordBase,
    RegionalInstrumentRecord,
    _extract_output_fields,
    _to_python_name,
)


class TestToPythonName:
    def test_simple(self):
        assert _to_python_name("Answer") == "answer"

    def test_spaces(self):
        assert _to_python_name("Case Citation") == "case_citation"

    def test_special_chars(self):
        assert _to_python_name("Official Source (URL)") == "official_source_url"

    def test_dot_notation(self):
        assert _to_python_name("Last Modified By.id") == "last_modified_by_id"

    def test_question_mark(self):
        assert _to_python_name("To Review?") == "to_review"

    def test_apostrophe(self):
        assert _to_python_name("Court's Position") == "court_s_position"

    def test_hyphen(self):
        assert _to_python_name("ID-number") == "id_number"

    def test_alpha_3_code(self):
        assert _to_python_name("Jurisdictions Alpha-3 Code") == "jurisdictions_alpha_3_code"

    def test_leading_digit(self):
        assert _to_python_name("3rd Party") == "f_3rd_party"


class TestExtractOutputFields:
    def test_answers_has_expected_fields(self):
        fields = _extract_output_fields(ALL_MAPPINGS["Answers"])
        assert "Answer" in fields
        assert "Themes" in fields
        assert "Jurisdictions" in fields
        assert "Question" in fields

    def test_court_decisions_has_expected_fields(self):
        fields = _extract_output_fields(ALL_MAPPINGS["Court Decisions"])
        assert "Case Citation" in fields
        assert "Case Title" in fields
        assert "Abstract" in fields
        assert "Themes" in fields

    def test_boolean_fields_typed_as_bool(self):
        fields = _extract_output_fields(ALL_MAPPINGS["Domestic Instruments"])
        assert fields["Compatible With the HCCH Principles"] is bool
        assert fields["Compatible With the UNCITRAL Model Law"] is bool

    def test_hop1_relations_excluded(self):
        fields = _extract_output_fields(ALL_MAPPINGS["Answers"])
        for name in fields:
            assert not name.startswith("hop1_relations")

    def test_skip_fields_excluded(self):
        fields = _extract_output_fields(ALL_MAPPINGS["Answers"])
        assert "source_table" not in fields
        assert "ID" not in fields

    def test_user_mapping_fields_included(self):
        fields = _extract_output_fields(ALL_MAPPINGS["Court Decisions"])
        assert "Last Modified By.email" in fields
        assert "Created By.name" in fields


class TestTableRecordModels:
    def test_all_tables_have_models(self):
        assert set(TABLE_RECORD_MODELS.keys()) == set(ALL_MAPPINGS.keys())

    def test_all_models_subclass_record_base(self):
        for table, model in TABLE_RECORD_MODELS.items():
            assert issubclass(model, RecordBase), f"{table} model must subclass RecordBase"

    def test_common_fields_on_all_models(self):
        for table, model in TABLE_RECORD_MODELS.items():
            fields = model.model_fields
            assert "source_table" in fields, f"{table} missing source_table"
            assert "id" in fields, f"{table} missing id"
            assert "rank" in fields, f"{table} missing rank"


class TestRecordBaseConstruction:
    def test_from_dict_with_extra_fields(self):
        record = RecordBase.model_validate({"source_table": "Answers", "id": "CHE_15-TC", "Answer": "Yes"})
        assert record.source_table == "Answers"
        assert record.id == "CHE_15-TC"

    def test_extra_fields_preserved(self):
        data = {"source_table": "Answers", "id": "X", "Answer": "Yes", "Custom": "value"}
        record = RecordBase.model_validate(data)
        assert record.model_dump()["Custom"] == "value"


class TestPerTableModels:
    def test_answer_record_accepts_aliased_fields(self):
        record = AnswerRecord.model_validate({"source_table": "Answers", "id": "CHE_15-TC", "Answer": "Yes", "Themes": "PIL"})
        assert record.source_table == "Answers"

    def test_court_decision_record_fields(self):
        record = CourtDecisionRecord.model_validate(
            {
                "source_table": "Court Decisions",
                "id": "CD-GBR-1",
                "Case Citation": "[2020] UKSC 1",
                "Case Title": "Test v Test",
            }
        )
        dumped = record.model_dump(by_alias=True)
        assert dumped["Case Citation"] == "[2020] UKSC 1"
        assert dumped["Case Title"] == "Test v Test"

    def test_literature_record_many_fields(self):
        record = LiteratureRecord.model_validate(
            {
                "source_table": "Literature",
                "id": "LIT-001",
                "Author": "Smith, J.",
                "Title": "PIL Overview",
                "Publication Year": "2020",
                "ISBN": "978-0-123456-78-9",
            }
        )
        dumped = record.model_dump(by_alias=True)
        assert dumped["Author"] == "Smith, J."
        assert dumped["Publication Year"] == "2020"

    def test_jurisdiction_record(self):
        record = JurisdictionRecord.model_validate({"id": 1, "Name": "Switzerland", "Alpha-3 Code": "CHE", "Region": "Europe"})
        dumped = record.model_dump(by_alias=True)
        assert dumped["Alpha-3 Code"] == "CHE"

    def test_boolean_field_on_domestic_instrument(self):
        record = DomesticInstrumentRecord.model_validate(
            {
                "source_table": "Domestic Instruments",
                "id": "DI-1",
                "Compatible With the HCCH Principles": True,
            }
        )
        dumped = record.model_dump(by_alias=True)
        assert dumped["Compatible With the HCCH Principles"] is True

    @pytest.mark.parametrize(
        "table,model",
        [
            ("Answers", AnswerRecord),
            ("Court Decisions", CourtDecisionRecord),
            ("Domestic Instruments", DomesticInstrumentRecord),
            ("International Instruments", InternationalInstrumentRecord),
            ("Regional Instruments", RegionalInstrumentRecord),
            ("Literature", LiteratureRecord),
            ("Arbitral Awards", ArbitralAwardRecord),
            ("Questions", QuestionRecord),
        ],
    )
    def test_model_roundtrip(self, table: str, model: type[RecordBase]) -> None:
        data = {"source_table": table, "id": "TEST-1", "rank": 1.5}
        record = model.model_validate(data)
        dumped = record.model_dump(exclude_none=True)
        assert dumped["source_table"] == table
        assert dumped["id"] == "TEST-1"
        assert dumped["rank"] == 1.5


class TestJsonSchema:
    def test_answer_schema_has_aliased_properties(self):
        schema = AnswerRecord.model_json_schema()
        props = schema["properties"]
        assert "Answer" in props
        assert "Themes" in props
        assert "Jurisdictions Alpha-3 Code" in props

    def test_court_decision_schema_has_expected_fields(self):
        schema = CourtDecisionRecord.model_json_schema()
        props = schema["properties"]
        assert "Case Citation" in props
        assert "Official Source (PDF)" in props

    def test_field_count_matches_config(self):
        for table, model in TABLE_RECORD_MODELS.items():
            model_specific = {k for k in model.model_fields if k not in ("source_table", "id", "rank")}
            assert len(model_specific) > 0, f"{table} has no specific fields"
            assert len(model_specific) <= len(_extract_output_fields(ALL_MAPPINGS[table]))
