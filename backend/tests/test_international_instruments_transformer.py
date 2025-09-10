"""
Tests for International Instruments data transformation functionality.
"""

from app.services.international_instruments_transformer import InternationalInstrumentsTransformer


class TestInternationalInstrumentsTransformer:
    """Test cases for the International Instruments transformer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = InternationalInstrumentsTransformer()
        
        # Sample current format data
        self.sample_current_data = {
            "CoLD_ID": "II001",
            "ID_Number": "2023-001",
            "Title": "International Climate Agreement",
            "Abbreviation": "ICA",
            "Date": "2023-01-15",
            "Status": "Active",
            "URL": "https://example.org/climate-agreement",
            "Attachment": [{"url": "https://example.org/docs/ica.pdf", "title": "ICA Full Text"}],
            "ncRecordId": "rec123456",
            "Created": "2023-01-01T10:00:00.000Z",
            "updated_at": "2023-06-15T14:30:00.000Z",
            "updated_by": {
                "id": "usr456",
                "email": "admin@example.org",
                "name": "Admin User"
            },
            "created_by": {
                "id": "usr789",
                "email": "creator@example.org", 
                "name": "Creator User"
            },
            "Entry_Into_Force": "2023-02-01",
            "Publication_Date": "2023-01-20",
            "Title__in_English_": "International Climate Agreement",
            "Official_Title": "International Climate Agreement (Fallback)",
            "Source__URL_": "https://example.org/climate-agreement",
            "Official_Source_URL": "https://fallback.org/agreement",
            "Source__PDF_": "https://example.org/docs/ica.pdf",
            "Official_Source_PDF": "https://fallback.org/docs/ica.pdf",
            "Relevant_Provisions": "Article 5, Section 2",
            "Full_Text_of_the_Provisions": "The parties agree to reduce emissions...",
            "related_specialists": [
                {
                    "Specialist": "Dr. Jane Climate",
                    "ncRecordId": "spec001"
                },
                {
                    "Specialist": "Prof. John Environment", 
                    "ncRecordId": "spec002"
                }
            ],
            "Literature_Link": [
                {
                    "id": "lit001",
                    "ncRecordId": "lit_rec001"
                },
                {
                    "id": "lit002",
                    "ncRecordId": "lit_rec002"
                }
            ],
            "International_Legal_Provisions_Link": [
                {
                    "display_value": "Climate Provision A",
                    "ncRecordId": "prov001"
                },
                {
                    "display_value": "Environmental Provision B",
                    "ncRecordId": "prov002"
                }
            ],
            "source_table": "International Instruments",
            "rank": 1.5
        }
    
    def test_basic_field_mapping(self):
        """Test that basic fields are mapped correctly."""
        result = self.transformer.transform(self.sample_current_data)
        
        # Test direct mappings
        assert result["source_table"] == "International Instruments"
        assert result["id"] == "II001"
        assert result["rank"] == 1.5
        assert result["ID"] == "II001"
        assert result["ID Number"] == "2023-001"
        assert result["Title"] == "International Climate Agreement"
        assert result["Abbreviation"] == "ICA"
        assert result["Date"] == "2023-01-15"
        assert result["Status"] == "Active"
        assert result["URL"] == "https://example.org/climate-agreement"
        assert result["Record ID"] == "rec123456"
        assert result["Created"] == "2023-01-01T10:00:00.000Z"
        assert result["Last Modified"] == "2023-06-15T14:30:00.000Z"
        assert result["Entry Into Force"] == "2023-02-01"
        assert result["Publication Date"] == "2023-01-20"
        assert result["Relevant Provisions"] == "Article 5, Section 2"
        assert result["Full Text of the Provisions"] == "The parties agree to reduce emissions..."
    
    def test_conditional_mappings(self):
        """Test conditional field mappings with primary and fallback values."""
        result = self.transformer.transform(self.sample_current_data)
        
        # Test conditional mappings - should use primary values
        assert result["sort_date"] == "2023-06-15T14:30:00.000Z"
        assert result["Title (in English)"] == "International Climate Agreement"
        assert result["Source (URL)"] == "https://example.org/climate-agreement"
        assert result["Source (PDF)"] == "https://example.org/docs/ica.pdf"
    
    def test_conditional_mappings_fallback(self):
        """Test conditional mappings when primary values are missing."""
        # Remove primary values to test fallbacks
        data_without_primary = self.sample_current_data.copy()
        data_without_primary["updated_at"] = None
        data_without_primary["result_date"] = "2023-05-01T12:00:00.000Z"
        data_without_primary["Title__in_English_"] = None
        data_without_primary["Source__URL_"] = None
        data_without_primary["Source__PDF_"] = None
        
        result = self.transformer.transform(data_without_primary)
        
        # Should fall back to secondary values
        assert result["sort_date"] == "2023-05-01T12:00:00.000Z"
        assert result["Title (in English)"] == "International Climate Agreement (Fallback)"
        assert result["Source (URL)"] == "https://fallback.org/agreement"
        assert result["Source (PDF)"] == "https://fallback.org/docs/ica.pdf"
    
    def test_specialists_transformation(self):
        """Test transformation of specialists array data."""
        result = self.transformer.transform(self.sample_current_data)
        
        # Test specialists array transformation
        assert result["Specialists"] == "Dr. Jane Climate,Prof. John Environment"
        assert result["Specialists Link"] == "spec001,spec002"
    
    def test_literature_transformation(self):
        """Test transformation of literature link arrays."""
        result = self.transformer.transform(self.sample_current_data)
        
        # Test literature transformations
        assert result["Literature"] == "lit001,lit002"
        assert result["Literature Link"] == "lit_rec001,lit_rec002"
    
    def test_legal_provisions_transformation(self):
        """Test transformation of legal provisions arrays."""
        result = self.transformer.transform(self.sample_current_data)
        
        # Test international legal provisions transformations
        assert result["International Legal Provisions"] == "Climate Provision A,Environmental Provision B"
        assert result["International Legal Provisions Link"] == "prov001,prov002"
    
    def test_user_field_mappings(self):
        """Test user field transformations."""
        result = self.transformer.transform(self.sample_current_data)
        
        # Test user mappings for last modified by
        assert result["Last Modified By.id"] == "usr456"
        assert result["Last Modified By.email"] == "admin@example.org"
        assert result["Last Modified By.name"] == "Admin User"
        
        # Test user mappings for created by
        assert result["Created By.id"] == "usr789"
        assert result["Created By.email"] == "creator@example.org"
        assert result["Created By.name"] == "Creator User"
    
    def test_attachment_handling(self):
        """Test that attachment fields are preserved correctly."""
        result = self.transformer.transform(self.sample_current_data)
        
        # Should preserve attachment structure
        assert result["Attachment"] == [{"url": "https://example.org/docs/ica.pdf", "title": "ICA Full Text"}]
    
    def test_missing_optional_fields(self):
        """Test transformation when optional fields are missing."""
        minimal_data = {
            "CoLD_ID": "II002",
            "Title": "Minimal Agreement",
            "ncRecordId": "rec789",
            "source_table": "International Instruments"
        }
        
        result = self.transformer.transform(minimal_data)
        
        # Should handle missing fields gracefully
        assert result["id"] == "II002"
        assert result["Title"] == "Minimal Agreement"
        assert result["Record ID"] == "rec789"
        assert result["source_table"] == "International Instruments"
        
        # Missing fields should not cause errors
        assert "Specialists" not in result or result["Specialists"] == ""
        assert "Literature" not in result or result["Literature"] == ""
    
    def test_empty_arrays(self):
        """Test handling of empty array fields."""
        data_with_empty_arrays = self.sample_current_data.copy()
        data_with_empty_arrays["related_specialists"] = []
        data_with_empty_arrays["Literature_Link"] = []
        data_with_empty_arrays["International_Legal_Provisions_Link"] = []
        
        result = self.transformer.transform(data_with_empty_arrays)
        
        # Empty arrays should result in empty strings or missing fields
        assert result.get("Specialists", "") == ""
        assert result.get("Specialists Link", "") == ""
        assert result.get("Literature", "") == ""
        assert result.get("Literature Link", "") == ""
        assert result.get("International Legal Provisions", "") == ""
        assert result.get("International Legal Provisions Link", "") == ""
    
    def test_post_processing(self):
        """Test post-processing rules are applied."""
        data_with_nulls = self.sample_current_data.copy()
        data_with_nulls["Status"] = None
        data_with_nulls["URL"] = ""
        
        result = self.transformer.transform(data_with_nulls)
        
        # Null values should be removed due to post-processing
        assert "Status" not in result
        # Empty strings should be preserved
        assert result["URL"] == ""
    
    def test_complete_transformation(self):
        """Test that all expected fields are present in transformed result."""
        result = self.transformer.transform(self.sample_current_data)
        
        # Verify all major field categories are represented
        expected_fields = [
            "source_table", "id", "rank", "ID", "ID Number", "Title", "Abbreviation",
            "Date", "Status", "URL", "Attachment", "Record ID", "Created", "Last Modified",
            "Entry Into Force", "Publication Date", "Relevant Provisions", 
            "Full Text of the Provisions", "Title (in English)", "Source (URL)", "Source (PDF)",
            "Specialists", "Specialists Link", "Literature", "Literature Link",
            "International Legal Provisions", "International Legal Provisions Link",
            "Last Modified By.id", "Last Modified By.email", "Last Modified By.name",
            "Created By.id", "Created By.email", "Created By.name", "sort_date"
        ]
        
        for field in expected_fields:
            assert field in result, f"Expected field '{field}' missing from result"
