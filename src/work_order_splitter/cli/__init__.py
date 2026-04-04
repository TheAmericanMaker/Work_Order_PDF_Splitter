"""CLI entry point for Work Order PDF Splitter."""

import argparse
import logging
import sys
from pathlib import Path

from ..core import PDFSplitError, bundle_pages

logger = logging.getLogger(__name__)


def main() -> None:
    """Run the CLI interface for PDF splitting."""
    parser = argparse.ArgumentParser(
        description="Split a PDF containing multiple work orders into individual PDF files."
    )
    parser.add_argument("input_pdf", help="Path to the input PDF file")
    parser.add_argument("output_dir", help="Directory to write output PDF files to")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    input_path = Path(args.input_pdf)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        output_files = bundle_pages(input_path, args.output_dir)
        print(f"Split complete: {len(output_files)} file(s) written to {args.output_dir}")
    except PDFSplitError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
