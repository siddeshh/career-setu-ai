import re
from pathlib import Path

from pypdf import PdfReader


def clean_resume_text(text: str) -> str:
    """
    Clean extracted PDF text for downstream AI processing.
    """

    # Normalize Windows and PDF line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces at the beginning/end of lines
    lines = [line.strip() for line in text.split("\n")]

    # Remove empty lines
    lines = [line for line in lines if line]

    # Remove excessive consecutive duplicate blank-like separators
    text = "\n".join(lines)

    return text.strip()


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract and clean text from a PDF resume.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    reader = PdfReader(str(path))

    text = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text.append(page_text)

    raw_text = "\n".join(text)

    return clean_resume_text(raw_text)