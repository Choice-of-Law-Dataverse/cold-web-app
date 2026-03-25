import pytest

from app.schemas.entities import EntityBase
from app.schemas.search_result import (
    TABLE_SEARCH_MODELS,
    AnswerSearchResult,
    CourtDecisionSearchResult,
    SearchResultBase,
    validate_search_result,
)


class TestValidateSearchResult:
    def test_dispatches_to_correct_model(self):
        data = {"source_table": "Answers", "answer": "Yes", "cold_id": "CHE_01"}
        result = validate_search_result(data)
        assert isinstance(result, AnswerSearchResult)
        assert result.answer == "Yes"

    def test_dispatches_court_decision(self):
        data = {"source_table": "Court Decisions", "case_title": "Test v Test"}
        result = validate_search_result(data)
        assert isinstance(result, CourtDecisionSearchResult)
        assert result.case_title == "Test v Test"

    def test_falls_back_to_base_for_unknown_table(self):
        data = {"source_table": "UnknownTable", "cold_id": "X-1"}
        result = validate_search_result(data)
        assert type(result) is SearchResultBase
        assert result.cold_id == "X-1"

    def test_falls_back_to_base_for_missing_source_table(self):
        data = {"cold_id": "X-2"}
        result = validate_search_result(data)
        assert type(result) is SearchResultBase

    def test_camel_case_alias_accepted(self):
        data = {"sourceTable": "Answers", "coldId": "CHE_01", "answer": "No"}
        result = validate_search_result(data)
        assert isinstance(result, AnswerSearchResult)
        assert result.cold_id == "CHE_01"

    def test_extra_fields_ignored(self):
        data = {"source_table": "Answers", "unexpected_field": "value"}
        result = validate_search_result(data)
        assert isinstance(result, AnswerSearchResult)

    def test_hcch_answers_mapped(self):
        assert "HCCH Answers" in TABLE_SEARCH_MODELS


class TestEntityBaseConfig:
    def test_camel_case_serialization(self):
        result = SearchResultBase(cold_id="TEST-1", source_table="Answers")
        dumped = result.model_dump(by_alias=True)
        assert "coldId" in dumped
        assert "sourceTable" in dumped

    def test_populate_by_name(self):
        result = SearchResultBase.model_validate({"coldId": "TEST-1", "sourceTable": "Answers"})
        assert result.cold_id == "TEST-1"

    def test_bool_coercion_on_str_field(self):
        class BoolModel(EntityBase):
            flag: str | None = None

        instance = BoolModel.model_validate({"flag": True})
        assert instance.flag == "True"


class TestTableSearchModelsComplete:
    @pytest.mark.parametrize(
        "table",
        [
            "Answers",
            "HCCH Answers",
            "Court Decisions",
            "Domestic Instruments",
            "Regional Instruments",
            "International Instruments",
            "Literature",
            "Arbitral Awards",
            "Arbitral Rules",
            "Arbitral Institutions",
            "Arbitral Provisions",
            "Domestic Legal Provisions",
            "International Legal Provisions",
            "Regional Legal Provisions",
            "Jurisdictions",
            "Questions",
        ],
    )
    def test_table_has_model(self, table: str):
        assert table in TABLE_SEARCH_MODELS, f"Missing TABLE_SEARCH_MODELS entry for {table}"
