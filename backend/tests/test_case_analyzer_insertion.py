#!/usr/bin/env python3
"""
Test case analyzer suggestion insertion into Court_Decisions table.
"""

from unittest.mock import patch

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from app.services.moderation_writer import MainDBWriter
from app.services.suggestion_approval import prepare_nocodb_data


class TestCaseAnalyzerInsertion:
    """Tests for case analyzer insertion into Court_Decisions table."""

    def test_prepare_case_analyzer_for_court_decisions_basic(self):
        """Test basic transformation of normalized case analyzer data."""
        # Create a mock writer (we don't need real DB connection for this test)
        with patch.object(MainDBWriter, "__init__", return_value=None):
            writer = MainDBWriter()
            # Mock the CASE_ANALYZER_METADATA_LABELS constant
            writer.CASE_ANALYZER_METADATA_LABELS = {
                "jurisdiction_type": "Jurisdiction Type",
                "choice_of_law_sections": "Choice of Law Section(s)",
                "theme": "Theme",
                "model": "AI Model",
            }

            # Mock normalized case analyzer data
            normalized = {
                "case_citation": "Smith v. Jones [2024] EWCA Civ 123",
                "date": "2024-03-15",
                "abstract": "This case deals with choice of law in contract disputes.",
                "relevant_facts": "The parties entered into a contract in 2020.",
                "pil_provisions": "Rome I Regulation, Article 3",
                "choice_of_law_issue": "Which law governs the contract?",
                "courts_position": "The court held that English law applies.",
                "jurisdiction": "United Kingdom",
                "jurisdiction_type": "Common Law",
                "choice_of_law_sections": "Section 3",
                "theme": "Contract Law",
                "model": "gpt-4",
            }

            result = writer.prepare_case_analyzer_for_court_decisions(normalized)

            # Check direct mappings
            assert result["case_citation"] == "Smith v. Jones [2024] EWCA Civ 123"
            assert result["date"] == "2024-03-15"
            assert result["abstract"] == "This case deals with choice of law in contract disputes."
            assert result["relevant_facts"] == "The parties entered into a contract in 2020."
            assert result["pil_provisions"] == "Rome I Regulation, Article 3"
            assert result["choice_of_law_issue"] == "Which law governs the contract?"
            assert result["courts_position"] == "The court held that English law applies."
            assert result["jurisdiction"] == "United Kingdom"

            # Check that metadata is combined in internal_notes
            assert "internal_notes" in result
            assert "Jurisdiction Type: Common Law" in result["internal_notes"]
            assert "Choice of Law Section(s): Section 3" in result["internal_notes"]
            assert "Theme: Contract Law" in result["internal_notes"]
            assert "AI Model: gpt-4" in result["internal_notes"]

    def test_prepare_case_analyzer_for_court_decisions_minimal(self):
        """Test transformation with minimal data."""
        with patch.object(MainDBWriter, "__init__", return_value=None):
            writer = MainDBWriter()
            writer.CASE_ANALYZER_METADATA_LABELS = {
                "jurisdiction_type": "Jurisdiction Type",
                "choice_of_law_sections": "Choice of Law Section(s)",
                "theme": "Theme",
                "model": "AI Model",
            }

            normalized = {
                "case_citation": "Test Case [2024]",
                "jurisdiction": "Germany",
            }

            result = writer.prepare_case_analyzer_for_court_decisions(normalized)

            assert result["case_citation"] == "Test Case [2024]"
            assert result["jurisdiction"] == "Germany"
            # Should not have internal_notes if no metadata present
            assert "internal_notes" not in result

    def test_prepare_case_analyzer_for_court_decisions_empty_values(self):
        """Test transformation with None/empty values."""
        with patch.object(MainDBWriter, "__init__", return_value=None):
            writer = MainDBWriter()
            writer.CASE_ANALYZER_METADATA_LABELS = {
                "jurisdiction_type": "Jurisdiction Type",
                "choice_of_law_sections": "Choice of Law Section(s)",
                "theme": "Theme",
                "model": "AI Model",
            }

            normalized = {
                "case_citation": None,
                "date": None,
                "abstract": "",
                "jurisdiction": "France",
                "jurisdiction_type": "",
                "theme": None,
            }

            result = writer.prepare_case_analyzer_for_court_decisions(normalized)

            # Should only include non-empty values
            assert "case_citation" not in result
            assert "date" not in result
            assert "abstract" not in result
            assert result["jurisdiction"] == "France"
            # Empty/None metadata should not appear in internal_notes
            assert "internal_notes" not in result

    def test_prepare_case_analyzer_for_court_decisions_all_fields(self):
        """Test transformation with all possible fields."""
        with patch.object(MainDBWriter, "__init__", return_value=None):
            writer = MainDBWriter()
            writer.CASE_ANALYZER_METADATA_LABELS = {
                "jurisdiction_type": "Jurisdiction Type",
                "choice_of_law_sections": "Choice of Law Section(s)",
                "theme": "Theme",
                "model": "AI Model",
            }

            normalized = {
                "case_citation": "Complete Case [2024]",
                "date": "2024-01-01",
                "abstract": "Full abstract",
                "relevant_facts": "Full facts",
                "pil_provisions": "Full provisions",
                "choice_of_law_issue": "Full issue",
                "courts_position": "Full position",
                "jurisdiction": "United States",
                "jurisdiction_type": "Federal Common Law",
                "choice_of_law_sections": "Sections 1-5",
                "theme": "International Commerce",
                "model": "gpt-4-turbo",
                "username": "test_user",
                "user_email": "test@example.com",
            }

            result = writer.prepare_case_analyzer_for_court_decisions(normalized)

            # Check all expected fields are present
            # 7 direct fields: case_citation, date, abstract, relevant_facts, pil_provisions,
            #                  choice_of_law_issue, courts_position
            # 1 linking field: jurisdiction
            # 1 combined field: internal_notes (from metadata)
            expected_field_count = 10
            assert len(result) == expected_field_count
            assert result["case_citation"] == "Complete Case [2024]"
            assert result["jurisdiction"] == "United States"

            # Check internal notes contains all metadata
            notes = result["internal_notes"]
            assert "Jurisdiction Type: Federal Common Law" in notes
            assert "Choice of Law Section(s): Sections 1-5" in notes
            assert "Theme: International Commerce" in notes
            assert "AI Model: gpt-4-turbo" in notes

            # username and user_email should not be in the result
            assert "username" not in result
            assert "user_email" not in result

    def test_insert_record_maps_id_number_and_ignores_legacy_audit_fields(self):
        engine = sa.create_engine("sqlite://")
        metadata = sa.MetaData()
        court_decisions = sa.Table(
            "Court_Decisions",
            metadata,
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("ID_Number", sa.String),
            sa.Column("created_by", sa.String),
        )
        metadata.create_all(engine)

        writer = MainDBWriter.__new__(MainDBWriter)
        writer.engine = engine
        writer.schema = None
        writer.metadata = sa.MetaData()
        writer.Session = sessionmaker(bind=engine, expire_on_commit=False)

        record_id = writer.insert_record(
            "Court_Decisions",
            {
                "id_number": "case-123",
                "created_by": "must-not-be-written",
            },
        )

        with engine.connect() as connection:
            row = connection.execute(
                sa.select(court_decisions.c.ID_Number, court_decisions.c.created_by).where(court_decisions.c.id == record_id)
            ).one()

        assert row.ID_Number == "case-123"
        assert row.created_by is None

    def test_prepare_nocodb_data_uses_api_field_titles(self):
        writer = MainDBWriter.__new__(MainDBWriter)

        result = prepare_nocodb_data(
            writer,
            {
                "case_citation": "Example",
                "courts_position": "Position",
                "jurisdiction": "GTM",
            },
        )

        assert result == {
            "Case Citation": "Example",
            "Court's Position": "Position",
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
