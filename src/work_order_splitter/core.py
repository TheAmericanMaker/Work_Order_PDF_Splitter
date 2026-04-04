"""Core PDF splitting logic."""

import logging
import re
from os import PathLike
from pathlib import Path
from typing import Any, Optional, Union

from pypdf import PdfReader, PdfWriter

logger = logging.getLogger(__name__)

PAGE_NUMBER_PATTERN = re.compile(r"page\s+(\d+)", re.IGNORECASE)
PathValue = Union[str, PathLike[str]]


class PDFSplitError(Exception):
    """Raised when PDF splitting fails."""


def extract_page_number(page: Any) -> Optional[int]:
    """Extract the page number from a PDF page's text content."""
    try:
        text = page.extract_text()
        if text is None:
            return None
        match = PAGE_NUMBER_PATTERN.search(text)
        if match:
            return int(match.group(1))
    except Exception as exc:
        logger.debug("Failed to extract page number: %s", exc)
    return None


def _write_bundle(writer: PdfWriter, output_path: Path) -> None:
    with output_path.open("wb") as output_file:
        writer.write(output_file)


def bundle_pages(input_pdf_path: PathValue, output_directory: PathValue) -> list[str]:
    """Split a PDF into multiple PDFs based on work order boundaries.

    The splitter starts a new output file whenever it encounters text matching
    ``page 1`` on a page after the first buffered page. Pages without a page
    marker are preserved in the current bundle rather than being discarded.
    """
    input_path = Path(input_pdf_path)
    output_dir = Path(output_directory)

    if not input_path.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    if not input_path.is_file():
        raise PDFSplitError(f"Input path is not a file: {input_path}")

    if output_dir.exists() and not output_dir.is_dir():
        raise PDFSplitError(f"Output path is not a directory: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        reader = PdfReader(str(input_path))
    except Exception as exc:
        raise PDFSplitError(f"Failed to read PDF: {exc}") from exc

    if not reader.pages:
        raise PDFSplitError("Input PDF has no pages")

    logger.info("Processing PDF %s with %d pages", input_path.name, len(reader.pages))

    writer = PdfWriter()
    output_files: list[str] = []
    output_file_count = 1

    for page in reader.pages:
        extracted_page_number = extract_page_number(page)

        if extracted_page_number == 1 and len(writer.pages) > 0:
            output_path = output_dir / f"output_{output_file_count}.pdf"
            _write_bundle(writer, output_path)
            output_files.append(str(output_path))
            logger.info("Wrote %s", output_path.name)
            writer = PdfWriter()
            output_file_count += 1

        writer.add_page(page)

    if len(writer.pages) > 0:
        output_path = output_dir / f"output_{output_file_count}.pdf"
        _write_bundle(writer, output_path)
        output_files.append(str(output_path))
        logger.info("Wrote %s", output_path.name)

    if not output_files:
        raise PDFSplitError("No output files were generated")

    logger.info("Split complete: %d output files generated", len(output_files))
    return output_files
