"""Convert PDFs to markdown using pymupdf4llm for all S3 framework papers.
These are born-digital PDFs (arXiv/journal) so direct text extraction works perfectly.
"""
from multiprocessing import freeze_support
from pathlib import Path


BASE = Path(__file__).resolve().parent

PAPERS = [
    (BASE / "beverland_2022" / "2211.07629v1.pdf", BASE / "beverland_2022", "paper.md"),
    (BASE / "stilck_franca_2021" / "2009.05532v1.pdf", BASE / "stilck_franca_2021", "paper.md"),
    (BASE / "ronnow" / "1401.2910v1.pdf", BASE / "ronnow", "paper.md"),
    (BASE / "hoefler_assessment" / "3571725.pdf", BASE / "hoefler_assessment", "paper.md"),
    (BASE / "babbush_2021" / "paper.pdf", BASE / "babbush_2021", "paper_marker.md"),
]


def convert_with_pymupdf4llm(pdf_path: Path) -> str:
    """Use pymupdf4llm for fast, high-quality extraction from born-digital PDFs."""
    try:
        import pymupdf4llm
        return pymupdf4llm.to_markdown(str(pdf_path))
    except ImportError:
        pass

    # Fallback: use pymupdf directly with manual markdown formatting
    import fitz
    doc = fitz.open(str(pdf_path))
    pages = []
    for page in doc:
        text = page.get_text("text")
        pages.append(text)
    doc.close()
    return "\n\n".join(pages)


def main():
    for pdf_path, out_dir, final_name in PAPERS:
        if not pdf_path.exists():
            print(f"SKIP (no PDF): {pdf_path}")
            continue
        dest = out_dir / final_name
        if dest.exists():
            print(f"SKIP (already exists): {dest}")
            continue
        print(f"Converting: {pdf_path.name} -> {final_name}")
        try:
            md_text = convert_with_pymupdf4llm(pdf_path)
            dest.write_text(md_text, encoding="utf-8")
            print(f"  SUCCESS: {len(md_text)} chars")
        except Exception as e:
            print(f"  ERROR: {e}")

    print("\nDone!")


if __name__ == "__main__":
    freeze_support()
    main()
