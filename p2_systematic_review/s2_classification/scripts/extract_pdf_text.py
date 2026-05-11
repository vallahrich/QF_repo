"""Extract plain text from PDF files using pypdf."""

import argparse
import os
import re
import sys
from pathlib import Path

# Ensure project root is on sys.path
_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from pypdf import PdfReader  # noqa: E402

from shared.tools.logger import get_logger  # noqa: E402

logger = get_logger("extract_pdf_text")

MIN_TEXT_LENGTH = 100


def extract_text(pdf_path: str) -> tuple[str, bool]:
    """Extract plain text from a PDF file using pypdf.

    Returns:
        tuple: (extracted_text, is_valid)
        - extracted_text: the full text content
        - is_valid: False if text < 100 chars (likely image-only PDF)
    """
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages.append(page_text)

    text = "\n\n".join(pages)
    # Collapse 3+ consecutive newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    page_count = len(pages)
    char_count = len(text)
    is_valid = char_count >= MIN_TEXT_LENGTH

    logger.info(
        "PDF processed",
        extra={"pdf_path": pdf_path, "pages": page_count, "chars": char_count},
    )

    if not is_valid:
        logger.warning(
            "Extracted text is very short — likely an image-only/scanned PDF",
            extra={"pdf_path": pdf_path, "chars": char_count},
        )

    return text, is_valid


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract plain text from a PDF file."
    )
    parser.add_argument("--file", required=True, help="Path to the PDF file")
    parser.add_argument(
        "--output",
        default=None,
        help="Path to write extracted text. If omitted, print to stdout.",
    )
    args = parser.parse_args()

    try:
        text, is_valid = extract_text(args.file)
    except FileNotFoundError:
        logger.error("File not found", extra={"pdf_path": args.file})
        sys.exit(1)
    except Exception as exc:
        logger.error(
            "Unexpected error reading PDF",
            extra={"pdf_path": args.file, "error": str(exc)},
        )
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info("Text written", extra={"output_path": args.output})
    else:
        print(text)

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
