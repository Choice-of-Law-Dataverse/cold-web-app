from app.services.filter_builder import build_filter_clause


class TestBuildFilterClause:
    def test_empty_filters(self):
        where, params = build_filter_clause("t", [])
        assert where == ""
        assert params == {}

    def test_string_filter(self):
        filters = [{"column": "Name", "value": "Switzerland"}]
        where, params = build_filter_clause("t", filters)
        assert "ILIKE" in where
        assert params["p_0_0"] == "Switzerland"

    def test_boolean_filter(self):
        filters = [{"column": "Active", "value": True}]
        where, params = build_filter_clause("t", filters)
        assert "= :p_0_0" in where
        assert params["p_0_0"] is True

    def test_numeric_filter(self):
        filters = [{"column": "Count", "value": 42}]
        where, params = build_filter_clause("t", filters)
        assert "= :p_0_0" in where
        assert params["p_0_0"] == 42

    def test_list_value_produces_or(self):
        filters = [{"column": "Name", "value": ["A", "B"]}]
        where, params = build_filter_clause("t", filters)
        assert "OR" in where
        assert params["p_0_0"] == "A"
        assert params["p_0_1"] == "B"

    def test_none_column_skipped(self):
        filters = [{"column": None, "value": "X"}]
        where, params = build_filter_clause("t", filters)
        assert where == ""
        assert params == {}

    def test_jsonb_path_string(self):
        filters = [{"column": "themes.name", "value": "PIL"}]
        where, params = build_filter_clause("t", filters)
        assert "jsonb_array_elements" in where
        assert "ILIKE" in where
        assert params["p_0_0"] == "PIL"

    def test_jsonb_path_boolean(self):
        filters = [{"column": "themes.active", "value": True}]
        where, params = build_filter_clause("t", filters)
        assert "::boolean" in where

    def test_jsonb_path_numeric(self):
        filters = [{"column": "themes.order", "value": 5}]
        where, params = build_filter_clause("t", filters)
        assert "::numeric" in where

    def test_multiple_filters_produce_and(self):
        filters = [
            {"column": "Name", "value": "CH"},
            {"column": "Type", "value": "Civil"},
        ]
        where, params = build_filter_clause("t", filters)
        assert "AND" in where
        assert len(params) == 2

    def test_where_prefix(self):
        filters = [{"column": "Name", "value": "X"}]
        where, _ = build_filter_clause("t", filters)
        assert where.startswith(" WHERE ")

    def test_camel_case_column_converted(self):
        filters = [{"column": "legalFamily", "value": "Civil"}]
        where, _ = build_filter_clause("t", filters)
        assert "legal_family" in where

    def test_sql_injection_characters_stripped(self):
        filters = [{"column": "name; DROP TABLE", "value": "X"}]
        where, _ = build_filter_clause("t", filters)
        assert "DROP" not in where
        assert ";" not in where
