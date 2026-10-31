"""
modules/sentiment_analysis.py
-------------------------------
Analyse the emotional tone of legal text using TextBlob.
Polarity:  -1.0 (very negative) → +1.0 (very positive)
Subjectivity: 0.0 (very objective) → 1.0 (very subjective)
"""

try:
    from textblob import TextBlob
    _TEXTBLOB_OK = True
except ImportError:
    _TEXTBLOB_OK = False


# Simple VADER-like word lists as additional signal
_NEGATIVE_WORDS = {
    "murder", "kill", "assault", "attack", "rape", "theft", "fraud",
    "threaten", "violence", "abuse", "kidnap", "robbery", "crime",
    "illegal", "criminal", "death", "terror", "torture", "corrupt",
    "dangerous", "harmful", "brutal", "aggressive", "hostile",
}
_POSITIVE_WORDS = {
    "innocent", "acquit", "justified", "legal", "lawful", "protect",
    "safe", "honest", "truthful", "compensate",
}


def _label(polarity: float) -> str:
    if polarity >= 0.2:
        return "Positive 😊"
    elif polarity <= -0.2:
        return "Negative 😡"
    else:
        return "Neutral 😐"


def _intensity(polarity: float) -> str:
    abs_p = abs(polarity)
    if abs_p >= 0.6:
        return "High"
    elif abs_p >= 0.3:
        return "Moderate"
    else:
        return "Low"


def analyze_sentiment(text: str) -> dict:
    """
    Run sentiment analysis on the provided text.

    Returns a dict:
      polarity        float   -1 … 1
      subjectivity    float    0 … 1
      label           str      Positive / Neutral / Negative
      intensity       str      High / Moderate / Low
      negative_words  list     legal-negative words found
      positive_words  list     legal-positive words found
    """
    polarity      = 0.0
    subjectivity  = 0.5

    if _TEXTBLOB_OK:
        blob         = TextBlob(text)
        polarity     = round(blob.sentiment.polarity,     4)
        subjectivity = round(blob.sentiment.subjectivity, 4)
    else:
        # Simple fallback: count negative/positive words
        words  = set(text.lower().split())
        neg_c  = len(words & _NEGATIVE_WORDS)
        pos_c  = len(words & _POSITIVE_WORDS)
        total  = neg_c + pos_c or 1
        polarity = round((pos_c - neg_c) / total, 4)

    tokens   = set(text.lower().split())
    neg_found = sorted(tokens & _NEGATIVE_WORDS)
    pos_found = sorted(tokens & _POSITIVE_WORDS)

    return {
        "polarity":       polarity,
        "subjectivity":   subjectivity,
        "label":          _label(polarity),
        "intensity":      _intensity(polarity),
        "negative_words": neg_found,
        "positive_words": pos_found,
    }
