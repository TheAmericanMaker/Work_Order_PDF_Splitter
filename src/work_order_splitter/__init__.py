"""Work Order PDF Splitter - Split PDFs by work order boundaries."""

from .core import bundle_pages, extract_page_number

__version__ = "2.0.0"
__all__ = ["bundle_pages", "extract_page_number"]
