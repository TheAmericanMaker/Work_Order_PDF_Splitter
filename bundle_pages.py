import sys
from importlib import import_module
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

cli = import_module("work_order_splitter.cli")
core = import_module("work_order_splitter.core")

main = cli.main
PDFSplitError = core.PDFSplitError
bundle_pages = core.bundle_pages
extract_page_number = core.extract_page_number


__all__ = ["PDFSplitError", "bundle_pages", "extract_page_number", "main"]


if __name__ == "__main__":
    main()
