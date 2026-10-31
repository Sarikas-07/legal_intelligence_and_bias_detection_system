"""
modules/preprocessing.py
-------------------------
Clean and normalise legal text before passing it to NLP modules.
Downloads required NLTK data on first use.
"""

import re
import string

import nltk

# Download quietly on first use
for _pkg in ("punkt", "stopwords", "punkt_tab"):
    try:
        nltk.download(_pkg, quiet=True)
    except Exception:
        pass

from nltk.corpus   import stopwords
from nltk.tokenize import word_tokenize


STOP_WORDS = set(stopwords.words("english"))

# Legal words that must NOT be stripped even though they look like stop-words
LEGAL_KEEP = {
    "not", "no", "without", "against", "under", "above", "before", "after",
    "between", "with", "by", "on", "at", "to", "from",
}
EFFECTIVE_STOPS = STOP_WORDS - LEGAL_KEEP


def clean_text(text: str) -> str:
    """
    Basic cleaning:
    - lowercase
    - strip URLs, emails, special chars
    - collapse whitespace
    """
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+",     " ", text)  # remove URLs
    text = re.sub(r"\S+@\S+",              " ", text)  # remove emails
    text = re.sub(r"\d+",                  " ", text)  # remove standalone numbers
    text = re.sub(r"[^a-z\s]",             " ", text)  # keep only letters
    text = re.sub(r"\s+",                  " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    """Word-tokenise text using NLTK."""
    return word_tokenize(text)


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Remove stop-words while preserving legal connectives."""
    return [t for t in tokens if t not in EFFECTIVE_STOPS and len(t) > 2]


def preprocess(text: str) -> dict:
    """
    Full pipeline.
    Returns a dict with:
      - original_text
      - cleaned_text
      - tokens
      - filtered_tokens
      - word_count
      - unique_words
    """
    cleaned  = clean_text(text)
    tokens   = tokenize(cleaned)
    filtered = remove_stopwords(tokens)

    return {
        "original_text":  text,
        "cleaned_text":   cleaned,
        "tokens":         tokens,
        "filtered_tokens": filtered,
        "word_count":     len(tokens),
        "unique_words":   len(set(tokens)),
    }
