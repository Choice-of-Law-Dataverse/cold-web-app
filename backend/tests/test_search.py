import pytest

from app.schemas.details import TABLE_DETAIL_MODELS
from app.schemas.entities import EntityBase
from app.schemas.records import TABLE_RECORD_MODELS
from app.schemas.responses import FullTextSearchResponse
from app.schemas.search_result import (
    TABLE_SEARCH_MODELS,
    AnswerSearchResult,
    CourtDecisionSearchResult,
    HcchAnswerSearchResult,
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

    def test_hcch_answers_dispatched(self):
        data = {"source_table": "HCCH Answers", "adapted_question": "Q1", "position": "Yes"}
        result = validate_search_result(data)
        assert isinstance(result, HcchAnswerSearchResult)
        assert result.adapted_question == "Q1"


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


class TestTableModelCrossCoverage:
    SEARCH_ONLY_TABLES = {"HCCH Answers"}
    DETAIL_ONLY_TABLES = {"Specialists"}

    def test_search_keys_covered_by_detail(self):
        missing = TABLE_SEARCH_MODELS.keys() - TABLE_DETAIL_MODELS.keys() - self.SEARCH_ONLY_TABLES
        assert not missing, f"TABLE_SEARCH_MODELS has tables missing from TABLE_DETAIL_MODELS: {missing}"

    def test_detail_keys_covered_by_search(self):
        missing = TABLE_DETAIL_MODELS.keys() - TABLE_SEARCH_MODELS.keys() - self.DETAIL_ONLY_TABLES
        assert not missing, f"TABLE_DETAIL_MODELS has tables missing from TABLE_SEARCH_MODELS: {missing}"

    def test_record_keys_covered_by_search(self):
        missing = TABLE_SEARCH_MODELS.keys() - TABLE_RECORD_MODELS.keys() - self.SEARCH_ONLY_TABLES
        assert not missing, f"TABLE_SEARCH_MODELS has tables missing from TABLE_RECORD_MODELS: {missing}"


class TestFullTextSearchResponseSerialization:
    def test_response_serializes_mixed_results(self):
        results = [
            validate_search_result({"source_table": "Answers", "answer": "Yes", "cold_id": "CHE_01"}),
            validate_search_result({"source_table": "Court Decisions", "case_title": "A v B"}),
            validate_search_result({"source_table": "HCCH Answers", "adapted_question": "Q1"}),
        ]
        response = FullTextSearchResponse(
            query="test",
            total_matches=3,
            page=1,
            page_size=50,
            results=results,
        )
        dumped = response.model_dump(by_alias=True)
        assert len(dumped["results"]) == 3
        assert dumped["results"][0]["answer"] == "Yes"
        assert dumped["results"][1]["caseTitle"] == "A v B"
        assert dumped["results"][2]["adaptedQuestion"] == "Q1"

    def test_response_handles_empty_results(self):
        response = FullTextSearchResponse(
            query="nothing",
            total_matches=0,
            page=1,
            page_size=50,
            results=[],
        )
        dumped = response.model_dump(by_alias=True)
        assert dumped["results"] == []
        assert dumped["totalMatches"] == 0
