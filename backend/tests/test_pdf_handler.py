"""Tests for PDF text extraction."""

import pymupdf

from app.case_analyzer.utils.pdf_handler import extract_text_from_pdf


def _make_pdf(pages_text: list[str]) -> bytes:
    doc = pymupdf.open()
    for text in pages_text:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    return doc.tobytes()


def test_extracts_all_pages_by_default() -> None:
    pdf = _make_pdf(["first page marker", "second page marker"])
    text = extract_text_from_pdf(pdf)
    assert "first page marker" in text
    assert "second page marker" in text


def test_extracts_only_requested_pages() -> None:
    pdf = _make_pdf(["first page marker", "second page marker"])
    text = extract_text_from_pdf(pdf, pages=[0])
    assert "first page marker" in text
    assert "second page marker" not in text
