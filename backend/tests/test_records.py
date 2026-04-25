import pytest

from app.schemas.records import (
    TABLE_RECORD_MODELS,
    AnswerRecord,
    ArbitralAwardRecord,
    ArbitralInstitutionRecord,
    ArbitralProvisionRecord,
    ArbitralRuleRecord,
    CourtDecisionRecord,
    DomesticInstrumentRecord,
    DomesticLegalProvisionRecord,
    InternationalInstrumentRecord,
    InternationalLegalProvisionRecord,
    JurisdictionRecord,
    LiteratureRecord,
    QuestionRecord,
    RecordBase,
    RegionalInstrumentRecord,
    RegionalLegalProvisionRecord,
)


class TestRecordBase:
    def test_instantiate_with_snake_case(self):
        record = RecordBase(source_table="Answers", id="CHE_15-TC", rank=1.5)
        assert record.source_table == "Answers"
        assert record.id == "CHE_15-TC"
        assert record.rank == 1.5

    def test_serialize_to_camel_case(self):
        record = RecordBase(source_table="Answers", id="X", rank=2.0)
        dumped = record.model_dump(by_alias=True)
        assert "sourceTable" in dumped
        assert dumped["sourceTable"] == "Answers"

    def test_accept_camel_case_input(self):
        record = RecordBase.model_validate({"sourceTable": "Answers", "id": "X"})
        assert record.source_table == "Answers"

    def test_extra_fields_ignored(self):
        data = {"source_table": "Answers", "id": "X", "Custom": "value"}
        record = RecordBase.model_validate(data)
        assert "Custom" not in record.model_dump()


class TestTableRecordModels:
    def test_all_16_entries(self):
        assert len(TABLE_RECORD_MODELS) == 16

    def test_expected_table_names(self):
        expected = {
            "Answers",
            "Court Decisions",
            "Domestic Instruments",
            "International Instruments",
            "Regional Instruments",
            "Literature",
            "Arbitral Awards",
            "Arbitral Institutions",
            "Arbitral Provisions",
            "Arbitral Rules",
            "Domestic Legal Provisions",
            "International Legal Provisions",
            "Regional Legal Provisions",
            "Jurisdictions",
            "Questions",
            "Specialists",
        }
        assert set(TABLE_RECORD_MODELS.keys()) == expected

    def test_all_models_subclass_record_base(self):
        for table, model in TABLE_RECORD_MODELS.items():
            assert issubclass(model, RecordBase), f"{table} model must subclass RecordBase"

    def test_common_fields_on_all_models(self):
        for table, model in TABLE_RECORD_MODELS.items():
            fields = model.model_fields
            assert "source_table" in fields, f"{table} missing source_table"
            assert "id" in fields, f"{table} missing id"
            assert "rank" in fields, f"{table} missing rank"


class TestSnakeCaseInstantiation:
    def test_answer_record_snake_case(self):
        record = AnswerRecord(source_table="Answers", id="CHE_15-TC", answer="Yes", themes="PIL")
        assert record.answer == "Yes"
        assert record.themes == "PIL"

    def test_court_decision_record_snake_case(self):
        record = CourtDecisionRecord(
            source_table="Court Decisions",
            id="CD-GBR-1",
            case_citation="[2020] UKSC 1",
            case_title="Test v Test",
        )
        assert record.case_citation == "[2020] UKSC 1"
        assert record.case_title == "Test v Test"

    def test_domestic_instrument_boolean_fields(self):
        record = DomesticInstrumentRecord(
            source_table="Domestic Instruments",
            id="DI-1",
            compatible_with_the_hcch_principles=True,
            compatible_with_the_uncitral_model_law=False,
        )
        assert record.compatible_with_the_hcch_principles is True
        assert record.compatible_with_the_uncitral_model_law is False

    def test_jurisdiction_record_snake_case(self):
        record = JurisdictionRecord(id=1, name="Switzerland", alpha_3_code="CHE", region="Europe")
        assert record.name == "Switzerland"
        assert record.alpha_3_code == "CHE"

    def test_jurisdiction_boolean_fields(self):
        record = JurisdictionRecord(id=1, irrelevant=True, done=False)
        assert record.irrelevant is True
        assert record.done is False


class TestCamelCaseSerialization:
    def test_answer_record_camel_output(self):
        record = AnswerRecord(answer="Yes", themes="PIL", jurisdictions_alpha_3_code="CHE")
        dumped = record.model_dump(by_alias=True, exclude_none=True)
        assert "answer" in dumped
        assert "themes" in dumped
        assert "jurisdictionsAlpha3Code" in dumped

    def test_court_decision_camel_output(self):
        record = CourtDecisionRecord(case_citation="[2020] UKSC 1", case_title="Test v Test")
        dumped = record.model_dump(by_alias=True, exclude_none=True)
        assert "caseCitation" in dumped
        assert "caseTitle" in dumped

    def test_literature_record_camel_output(self):
        record = LiteratureRecord(
            author="Smith, J.",
            title="PIL Overview",
            publication_year="2020",
            isbn="978-0-123456-78-9",
        )
        dumped = record.model_dump(by_alias=True, exclude_none=True)
        assert dumped["author"] == "Smith, J."
        assert dumped["publicationYear"] == "2020"
        assert dumped["isbn"] == "978-0-123456-78-9"


class TestCamelCaseInput:
    def test_accept_camel_case_fields(self):
        record = AnswerRecord.model_validate({"sourceTable": "Answers", "id": "X", "answer": "Yes", "themes": "PIL"})
        assert record.source_table == "Answers"
        assert record.answer == "Yes"

    def test_court_decision_camel_input(self):
        record = CourtDecisionRecord.model_validate({"caseCitation": "[2020] UKSC 1", "caseTitle": "Test v Test"})
        assert record.case_citation == "[2020] UKSC 1"
        assert record.case_title == "Test v Test"


class TestModelExpectedFields:
    def test_answer_record_has_expected_fields(self):
        fields = AnswerRecord.model_fields
        assert "answer" in fields
        assert "themes" in fields
        assert "jurisdictions" in fields
        assert "question" in fields

    def test_court_decision_has_expected_fields(self):
        fields = CourtDecisionRecord.model_fields
        assert "case_citation" in fields
        assert "case_title" in fields
        assert "abstract" in fields
        assert "themes" in fields
        assert "official_source_pdf" in fields

    def test_literature_has_expected_fields(self):
        fields = LiteratureRecord.model_fields
        assert "author" in fields
        assert "title" in fields
        assert "publication_year" in fields
        assert "isbn" in fields

    def test_arbitral_award_has_expected_fields(self):
        fields = ArbitralAwardRecord.model_fields
        assert "case_number" in fields
        assert "award_summary" in fields
        assert "arbitral_institutions" in fields

    def test_question_has_expected_fields(self):
        fields = QuestionRecord.model_fields
        assert "question" in fields
        assert "question_number" in fields
        assert "themes" in fields

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
            ("Arbitral Institutions", ArbitralInstitutionRecord),
            ("Arbitral Provisions", ArbitralProvisionRecord),
            ("Arbitral Rules", ArbitralRuleRecord),
            ("Domestic Legal Provisions", DomesticLegalProvisionRecord),
            ("International Legal Provisions", InternationalLegalProvisionRecord),
            ("Regional Legal Provisions", RegionalLegalProvisionRecord),
            ("Jurisdictions", JurisdictionRecord),
            ("Questions", QuestionRecord),
        ],
    )
    def test_each_model_has_specific_fields(self, table: str, model: type[RecordBase]) -> None:
        model_specific = {k for k in model.model_fields if k not in ("source_table", "id", "rank")}
        assert len(model_specific) > 0, f"{table} has no specific fields"


class TestModelRoundtrip:
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
            ("Arbitral Institutions", ArbitralInstitutionRecord),
            ("Arbitral Provisions", ArbitralProvisionRecord),
            ("Arbitral Rules", ArbitralRuleRecord),
            ("Domestic Legal Provisions", DomesticLegalProvisionRecord),
            ("International Legal Provisions", InternationalLegalProvisionRecord),
            ("Regional Legal Provisions", RegionalLegalProvisionRecord),
            ("Jurisdictions", JurisdictionRecord),
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
    def test_answer_schema_has_camel_properties(self):
        schema = AnswerRecord.model_json_schema()
        props = schema["properties"]
        assert "answer" in props
        assert "themes" in props
        assert "jurisdictionsAlpha3Code" in props

    def test_court_decision_schema_has_camel_properties(self):
        schema = CourtDecisionRecord.model_json_schema()
        props = schema["properties"]
        assert "caseCitation" in props
        assert "officialSourcePdf" in props
