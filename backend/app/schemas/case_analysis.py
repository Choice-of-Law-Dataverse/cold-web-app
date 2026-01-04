from typing import Literal

from pydantic import BaseModel, Field


class UploadDocumentRequest(BaseModel):
    """Request to upload and process a court decision document."""

    file_name: str = Field(..., description="Original filename of the uploaded document")
    blob_url: str = Field(..., description="Azure Blob Storage URL of the uploaded PDF")


class JurisdictionInfo(BaseModel):
    """Detected jurisdiction information."""

    legal_system_type: str = Field(..., description="Type of legal system (Civil-law, Common-law, or No court decision)")
    precise_jurisdiction: str = Field(..., description="Specific jurisdiction (e.g., 'Switzerland')")
    jurisdiction_code: str = Field(..., description="ISO country code (e.g., 'CH')")
    confidence: Literal["low", "medium", "high"] = Field(..., description="Confidence level of detection")
    reasoning: str = Field(..., description="Explanation of jurisdiction detection")


class UploadDocumentResponse(BaseModel):
    """Response from document upload containing initial analysis."""

    correlation_id: str = Field(..., description="Unique identifier for tracking this analysis")
    extracted_text: str = Field(..., description="Extracted text from the document")
    jurisdiction: JurisdictionInfo = Field(..., description="Detected jurisdiction information")


class ConfirmAnalysisRequest(BaseModel):
    """Request to confirm jurisdiction and continue analysis."""

    correlation_id: str = Field(..., description="Correlation ID from upload response")
    jurisdiction: JurisdictionInfo = Field(..., description="Confirmed or corrected jurisdiction information")


class AnalysisStep(BaseModel):
    """Intermediate step in the analysis workflow."""

    step_name: str = Field(..., description="Name of the analysis step")
    status: Literal["in_progress", "completed", "error"] = Field(..., description="Status of this step")
    data: dict | None = Field(None, description="Step result data")
    error: str | None = Field(None, description="Error message if status is 'error'")


class AnalysisResult(BaseModel):
    """Complete analysis result for court decision."""

    correlation_id: str
    case_citation: str | None = None
    abstract: str | None = None
    relevant_facts: str | None = None
    pil_provisions: list[str] | None = None
    choice_of_law_issue: str | None = None
    courts_position: str | None = None
    themes: list[str] | None = None
    confidence_scores: dict[str, str] | None = None
