#!/usr/bin/env python3
"""
Test case analyzer suggestion insertion into Court_Decisions table.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date

from app.services.moderation_writer import MainDBWriter


class TestCaseAnalyzerInsertion:
    """Tests for case analyzer insertion into Court_Decisions table."""

    def test_prepare_case_analyzer_for_court_decisions_basic(self):
        """Test basic transformation of normalized case analyzer data."""
        # Create a mock writer (we don't need real DB connection for this test)
        with patch.object(MainDBWriter, '__init__', return_value=None):
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
        with patch.object(MainDBWriter, '__init__', return_value=None):
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
        with patch.object(MainDBWriter, '__init__', return_value=None):
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
        with patch.object(MainDBWriter, '__init__', return_value=None):
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
            assert len(result) == 9  # 7 direct fields + jurisdiction + internal_notes
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
