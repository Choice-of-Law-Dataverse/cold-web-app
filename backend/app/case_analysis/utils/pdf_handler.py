"""PDF text extraction using pymupdf4llm."""

import io
import logging

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
        pdf_stream = io.BytesIO(pdf_bytes)
        markdown_text = pymupdf4llm.to_markdown(pdf_stream)

        if isinstance(markdown_text, str):
            return markdown_text
        if isinstance(markdown_text, list):
            return "\n".join(str(item) for item in markdown_text)
        return str(markdown_text)

    except Exception as e:
        error_msg = f"Failed to extract text from PDF: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e

