"""
modules/summarizer.py
---------------------
Two-tier summarisation:
  1. HuggingFace facebook/bart-large-cnn  (abstractive – best quality)
  2. Extractive fallback using sentence scoring (no internet / GPU required)

The app calls summarize() and gets a result regardless of GPU/model availability.
"""

import re


# ─────────────────────────────────────────────────────────────────────────────
# TIER 1 – Transformer-based (optional, loads lazily)
# ─────────────────────────────────────────────────────────────────────────────
_pipeline = None
_TRANSFORMERS_OK = False

def _load_pipeline():
    global _pipeline, _TRANSFORMERS_OK
    if _pipeline is not None:
        return
    try:
        from transformers import pipeline
        _pipeline = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6",  # lighter than bart-large-cnn
            max_length=150,
            min_length=40,
            do_sample=False,
        )
        _TRANSFORMERS_OK = True
        print("[Summarizer] Loaded DistilBART model.")
    except Exception as e:
        print(f"[Summarizer] Transformer unavailable ({e}). Using extractive fallback.")
        _TRANSFORMERS_OK = False


# ─────────────────────────────────────────────────────────────────────────────
# TIER 2 – Extractive fallback
# ─────────────────────────────────────────────────────────────────────────────
LEGAL_KEYWORDS = {
    "murder", "theft", "assault", "fraud", "rape", "kidnap", "hack",
    "accused", "victim", "arrested", "crime", "complaint", "police",
    "court", "section", "ipc", "law", "punish", "drug", "violence",
    "threat", "bribe", "dowry", "domestic", "negligence", "stolen",
}


def _sentence_score(sentence: str) -> float:
    words = set(sentence.lower().split())
    hits  = words & LEGAL_KEYWORDS
    length_bonus = min(len(words) / 20.0, 1.0)  # prefer medium-length sentences
    return len(hits) + length_bonus


def extractive_summary(text: str, num_sentences: int = 4) -> str:
    """Pick the top-scoring sentences and return them in original order."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if len(s.split()) > 5]

    if not sentences:
        return text[:500]

    scored = sorted(enumerate(sentences), key=lambda x: _sentence_score(x[1]), reverse=True)
    top_n  = sorted(scored[:num_sentences], key=lambda x: x[0])  # restore order
    return " ".join(s for _, s in top_n)


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────
def summarize(text: str, use_transformer: bool = True) -> dict:
    """
    Summarise a legal document.

    Returns:
        {
          "summary":          str,
          "method":           "transformer" | "extractive",
          "original_length":  int,
          "summary_length":   int,
          "compression_ratio": float,
        }
    """
    original_len = len(text.split())

    summary_text = ""
    method       = "extractive"

    if use_transformer:
        _load_pipeline()

    if use_transformer and _TRANSFORMERS_OK and _pipeline is not None:
        try:
            # BART has a 1024 token limit; truncate long inputs
            truncated = " ".join(text.split()[:900])
            result    = _pipeline(truncated, truncation=True)
            summary_text = result[0]["summary_text"]
            method       = "transformer"
        except Exception as e:
            print(f"[Summarizer] Transformer inference failed: {e}. Falling back.")
            summary_text = extractive_summary(text)
    else:
        summary_text = extractive_summary(text)

    summary_len = len(summary_text.split())

    return {
        "summary":           summary_text,
        "method":            method,
        "original_length":   original_len,
        "summary_length":    summary_len,
        "compression_ratio": round(summary_len / max(original_len, 1), 3),
    }
