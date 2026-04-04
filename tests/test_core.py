from pathlib import Path

import pytest
from pypdf import PdfReader

from work_order_splitter.core import PDFSplitError, bundle_pages, extract_page_number


class StubPage:
    def __init__(self, text: str) -> None:
        self._text = text

    def extract_text(self) -> str:
        return self._text


def test_extract_page_number_returns_match() -> None:
    assert extract_page_number(StubPage("This is page 12 of the work order")) == 12


def test_extract_page_number_returns_none_when_missing() -> None:
    assert extract_page_number(StubPage("No page marker here")) is None


def test_bundle_pages_splits_work_orders(sample_work_order_pdf: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"

    output_files = bundle_pages(sample_work_order_pdf, output_dir)

    assert [Path(path).name for path in output_files] == ["output_1.pdf", "output_2.pdf"]
    assert len(PdfReader(output_files[0]).pages) == 2
    assert len(PdfReader(output_files[1]).pages) == 3


def test_bundle_pages_preserves_pages_without_markers(mixed_marker_pdf: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "output"

    output_files = bundle_pages(mixed_marker_pdf, output_dir)

    assert len(output_files) == 2
    assert len(PdfReader(output_files[0]).pages) == 2
    assert len(PdfReader(output_files[1]).pages) == 1


def test_bundle_pages_raises_for_missing_input(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        bundle_pages(tmp_path / "missing.pdf", tmp_path / "output")


def test_bundle_pages_raises_for_invalid_pdf(tmp_path: Path) -> None:
    invalid_pdf = tmp_path / "invalid.pdf"
    invalid_pdf.write_text("not a real pdf", encoding="utf-8")

    with pytest.raises(PDFSplitError):
        bundle_pages(invalid_pdf, tmp_path / "output")
