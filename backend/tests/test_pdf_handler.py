"""Tests for PDF text extraction."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pymupdf
import pytest

from app.case_analyzer.utils import pdf_handler
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


def test_concurrent_extractions_never_overlap(monkeypatch: pytest.MonkeyPatch) -> None:
    active = 0
    most_active = 0
    counter = threading.Lock()

    def slow_to_markdown(path: str, pages: list[int] | None = None) -> str:
        nonlocal active, most_active
        with counter:
            active += 1
            most_active = max(most_active, active)
        time.sleep(0.05)
        with counter:
            active -= 1
        return "text"

    monkeypatch.setattr(pdf_handler.pymupdf4llm, "to_markdown", slow_to_markdown)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: pdf_handler.extract_text_from_pdf(b"%PDF-1.7"), range(4)))

    assert results == ["text"] * 4
    assert most_active == 1
