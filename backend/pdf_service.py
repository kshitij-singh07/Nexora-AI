import re

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


def tokenize(text):
    """
    Convert text into simple searchable words.
    """

    return set(
        re.findall(
            r"[a-zA-Z0-9]+",
            text.lower()
        )
    )


def retrieve_relevant_pages(pages, question, top_k=5):
    """
    Find the pages most relevant to the user's question.

    This is a lightweight keyword-based retrieval system.
    """

    question_words = tokenize(question)

    if not question_words:
        return []

    scored_pages = []

    for page in pages:

        page_text = page.get("text", "")

        if not page_text.strip():
            continue

        page_words = tokenize(page_text)

        matches = question_words.intersection(page_words)

        score = len(matches)

        scored_pages.append({
            "page": page["page"],
            "text": page_text,
            "score": score
        })

    scored_pages.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    relevant = [
        page
        for page in scored_pages[:top_k]
        if page["score"] > 0
    ]

    # If no keywords matched, provide the first few
    # non-empty pages so the AI still has context.
    if not relevant:

        relevant = scored_pages[:top_k]

    return relevant