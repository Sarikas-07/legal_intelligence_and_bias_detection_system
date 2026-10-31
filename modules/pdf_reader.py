"""
modules/pdf_reader.py
---------------------
Extract plain text from uploaded PDF files using PyPDF2.
"""

import io

try:
    import PyPDF2
    _PYPDF2_AVAILABLE = True
except ImportError:
    _PYPDF2_AVAILABLE = False


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Given raw PDF bytes (e.g. from st.file_uploader), return all extracted text.
    Falls back to an informative message if PyPDF2 is unavailable.
    """
    if not _PYPDF2_AVAILABLE:
        return "[ERROR] PyPDF2 is not installed. Run: pip install PyPDF2"

    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages  = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        full_text = "\n\n".join(pages)
        return full_text if full_text.strip() else "[WARNING] No extractable text found in PDF."
    except Exception as e:
        return f"[ERROR] Could not read PDF: {e}"


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Decode a plain-text upload to a Python string."""
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return file_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    return "[ERROR] Could not decode the text file."
