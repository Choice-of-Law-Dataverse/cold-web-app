"""PDF text extraction using pymupdf4llm."""

import logging
import tempfile
import threading
from pathlib import Path

import pymupdf4llm

logger = logging.getLogger(__name__)

_PYMUPDF_LOCK = threading.Lock()


def extract_text_from_pdf(pdf_bytes: bytes, pages: list[int] | None = None) -> str:
    """
    Extract text from PDF bytes using pymupdf4llm.

    pymupdf4llm.to_markdown() reads from a file path, so the bytes go through a temporary file.

    PyMuPDF and the Leptonica library it uses for OCR are not thread-safe ("Attempt to use Leptonica from 2 threads
    at once!"), yet callers run this through asyncio.to_thread: the upload route, Azure storage and the corpus
    extraction script, which downloads several PDFs at once. A module-wide lock serialises the extraction itself
    here, so every caller is covered and downloads stay concurrent.

    Args:
        pdf_bytes: PDF file content as bytes
        pages: Optional list of 0-based page indices to extract; None extracts all pages

    Returns:
        Extracted text as markdown string

    Raises:
        ValueError: If PDF extraction fails
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_path = Path(tmp_file.name)

        try:
            with _PYMUPDF_LOCK:
                markdown_text = pymupdf4llm.to_markdown(str(tmp_path), pages=pages)

            if isinstance(markdown_text, str):
                return markdown_text
            if isinstance(markdown_text, list):
                return "\n".join(str(item) for item in markdown_text)
            return str(markdown_text)
        finally:
            tmp_path.unlink(missing_ok=True)

    except Exception as e:
        error_msg = f"Failed to extract text from PDF: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e
