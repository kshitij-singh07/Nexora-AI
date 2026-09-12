from pypdf import PdfReader


def extract_pdf(file_path):
    """
    Extract text from a PDF while preserving page boundaries.
    """

    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""

        text = text.strip()

        pages.append({
            "page": page_number,
            "text": text
        })

    full_text = "\n\n".join(
        f"[Page {page['page']}]\n{page['text']}"
        for page in pages
        if page["text"]
    )

    return {
        "page_count": len(reader.pages),
        "pages": pages,
        "text": full_text
    }