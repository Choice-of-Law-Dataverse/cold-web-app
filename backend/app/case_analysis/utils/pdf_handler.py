"""PDF text extraction using pymupdf4llm."""

import logging
import tempfile
from pathlib import Path

import pymupdf4llm

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes using pymupdf4llm.

    Args:
        pdf_bytes: PDF file content as bytes

    Returns:
        Extracted text as markdown string

    Raises:
        ValueError: If PDF extraction fails
    """
    try:
        # pymupdf4llm.to_markdown() requires a file path, so write to temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_path = Path(tmp_file.name)

        try:
            markdown_text = pymupdf4llm.to_markdown(str(tmp_path))

            if isinstance(markdown_text, str):
                return markdown_text
            if isinstance(markdown_text, list):
                return "\n".join(str(item) for item in markdown_text)
            return str(markdown_text)
        finally:
            # Clean up temp file
            tmp_path.unlink(missing_ok=True)

    except Exception as e:
        error_msg = f"Failed to extract text from PDF: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
