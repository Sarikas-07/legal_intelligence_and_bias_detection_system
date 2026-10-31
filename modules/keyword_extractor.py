"""
modules/keyword_extractor.py
-----------------------------
Extract legally-relevant keywords from crime descriptions.
Uses:
  - NLTK frequency distribution
  - A curated legal vocabulary to boost relevant terms
  - Optional spaCy NER for named entity detection
"""

from collections import Counter
import re

import nltk
for _pkg in ("punkt", "stopwords", "averaged_perceptron_tagger", "maxent_ne_chunker", "words", "punkt_tab"):
    try:
        nltk.download(_pkg, quiet=True)
    except Exception:
        pass

from nltk.tokenize import word_tokenize
from nltk.corpus   import stopwords

# ─── Legal vocabulary (boosted weight if found) ───────────────────────────────
LEGAL_VOCAB = {
    "murder", "kill", "killed", "death", "assault", "attack", "beat", "theft",
    "steal", "stole", "stolen", "rob", "robbery", "kidnap", "abduct", "rape",
    "fraud", "cheat", "deceive", "hack", "cybercrime", "threat", "threaten",
    "extort", "blackmail", "drug", "narcotic", "bribe", "corruption",
    "trespass", "forged", "forgery", "defame", "defamation", "harass",
    "domestic", "violence", "weapon", "gun", "knife", "bomb", "acid",
    "victim", "accused", "suspect", "criminal", "offence", "offense",
    "arrest", "police", "court", "complaint", "fir", "evidence", "witness",
    "dowry", "molest", "sexual", "stalking", "intimidate", "coerce",
    "money", "property", "wallet", "phone", "bag", "car", "vehicle",
    "bank", "account", "password", "data", "identity", "impersonate",
    "fire", "burn", "poison", "injury", "wound", "fracture", "hospital",
}

_STOP = set(stopwords.words("english"))


def extract_keywords(text: str, top_n: int = 15) -> list[dict]:
    """
    Extract top-n keywords with frequencies.

    Returns:
        [ {"word": str, "frequency": int, "is_legal": bool}, ... ]
    """
    tokens = word_tokenize(text.lower())
    tokens = [
        t for t in tokens
        if t.isalpha() and t not in _STOP and len(t) > 2
    ]

    freq   = Counter(tokens)

    # Boost legal terms
    boosted = {}
    for word, count in freq.items():
        boosted[word] = count * (3 if word in LEGAL_VOCAB else 1)

    top = sorted(boosted.items(), key=lambda x: x[1], reverse=True)[:top_n]

    return [
        {
            "word":      word,
            "frequency": freq[word],   # original count (not boosted)
            "is_legal":  word in LEGAL_VOCAB,
        }
        for word, _ in top
    ]


def extract_entities(text: str) -> dict:
    """
    Extract named entities using NLTK chunker.
    Returns { entity_type: [entity_string, ...] }
    """
    entities: dict[str, list[str]] = {}
    try:
        tokens   = word_tokenize(text)
        tagged   = nltk.pos_tag(tokens)
        chunked  = nltk.ne_chunk(tagged)
        for subtree in chunked:
            if hasattr(subtree, "label"):
                label = subtree.label()
                name  = " ".join(token for token, _ in subtree.leaves())
                entities.setdefault(label, []).append(name)
    except Exception:
        pass
    return entities


def get_legal_terms_found(text: str) -> list[str]:
    """Return list of legal vocabulary words found in the text."""
    tokens = set(word_tokenize(text.lower()))
    return sorted(tokens & LEGAL_VOCAB)
