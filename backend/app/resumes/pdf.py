import re
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PyPdfError

MAX_BYTES = 5 * 1024 * 1024
MAX_PAGES = 10
MIN_TEXT_CHARS = 100
MAX_TEXT_CHARS = 30_000

_SPACES = re.compile(r"[ \t 　]+")


class ResumeFileError(ValueError):
    pass


def extract_text(data: bytes) -> str:
    if len(data) > MAX_BYTES:
        raise ResumeFileError("File is larger than 5 MB")
    if not data.startswith(b"%PDF-"):
        raise ResumeFileError("File is not a PDF")
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise ResumeFileError("Password-protected PDFs are not supported")
        if len(reader.pages) > MAX_PAGES:
            raise ResumeFileError(f"PDF has more than {MAX_PAGES} pages")
        raw = "\n".join(page.extract_text() or "" for page in reader.pages)
    except PyPdfError:
        raise ResumeFileError("PDF could not be read") from None
    lines = (_SPACES.sub(" ", line).strip() for line in raw.splitlines())
    text = "\n".join(line for line in lines if line)
    if len(text) < MIN_TEXT_CHARS:
        raise ResumeFileError("No text found in the PDF. Scanned images are not supported")
    return text[:MAX_TEXT_CHARS]
