"""
modules/ipc_recommender.py
---------------------------
Match a crime description to IPC / BNS sections using:
  1. Direct keyword overlap with database keywords
  2. TF-IDF cosine similarity for fuzzy matching

Ranks results and returns the top-N most relevant sections.
"""

import re
from collections import defaultdict

# local imports
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.database_handler import get_all_sections

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    _SKLEARN_OK = True
except ImportError:
    _SKLEARN_OK = False


# ─── Crime Category Map ───────────────────────────────────────────────────────
# Maps high-level crime categories to sets of trigger keywords
CRIME_CATEGORY_KEYWORDS = {
    "Murder / Homicide":    {"murder", "kill", "killed", "death", "shoot", "stab", "homicide", "poison", "dead"},
    "Assault / Hurt":       {"assault", "attack", "beat", "punch", "hit", "slap", "hurt", "injury", "wound", "kick"},
    "Theft / Robbery":      {"steal", "stole", "stolen", "theft", "rob", "robbery", "snatch", "pickpocket", "loot"},
    "Fraud / Cheating":     {"fraud", "cheat", "deceive", "scam", "fake", "false", "con", "mislead", "swindle"},
    "Cybercrime":           {"hack", "hacking", "cyber", "phishing", "malware", "password", "account", "data breach", "ransomware"},
    "Kidnapping":           {"kidnap", "abduct", "missing", "hostage", "forcefully taken"},
    "Sexual Offence":       {"rape", "sexual assault", "molest", "harass", "grope", "outrage modesty"},
    "Domestic Violence":    {"domestic violence", "dowry", "wife", "husband abuse", "marital", "cruelty"},
    "Drug Offence":         {"drug", "narcotic", "cocaine", "heroin", "ganja", "marijuana", "trafficking"},
    "Defamation":           {"defame", "slander", "libel", "false accusation", "reputation"},
    "Trespass / Burglary":  {"trespass", "break in", "burglary", "illegal entry", "unauthorized"},
    "Forgery":              {"forge", "forged", "fake document", "counterfeit", "tamper", "fabricate"},
    "Intimidation":         {"threat", "threaten", "blackmail", "extort", "intimidate", "coerce"},
}


def classify_crime(text: str) -> list[str]:
    """Return a list of detected crime categories (ordered by match strength)."""
    lower = text.lower()
    scores: dict[str, int] = defaultdict(int)
    for category, keywords in CRIME_CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", lower):
                scores[category] += 1
    sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [cat for cat, sc in sorted_cats if sc > 0]


def _keyword_score(query_tokens: set[str], section_keywords: str) -> float:
    """Count how many query tokens appear in the section's keyword list."""
    sec_kws = set(re.split(r"[,\s]+", section_keywords.lower()))
    overlap = query_tokens & sec_kws
    return len(overlap) / max(len(sec_kws), 1)


def recommend_sections(text: str, top_n: int = 5) -> list[dict]:
    """
    Recommend the most applicable IPC/BNS sections for the given text.

    Returns a list of section dicts (from DB) enriched with:
      - match_score  (float, 0-1)
      - match_method ("keyword" | "tfidf" | "combined")
    """
    sections = get_all_sections()
    if not sections:
        return []

    query_tokens = set(re.findall(r"\b[a-z]+\b", text.lower()))
    query_tokens -= {"the", "a", "an", "is", "are", "was", "were", "and", "or", "in", "on", "at", "to"}

    # ── Method 1: keyword overlap ─────────────────────────────────────────────
    kw_scores = {}
    for sec in sections:
        score = _keyword_score(query_tokens, sec["keywords"])
        kw_scores[sec["id"]] = score

    # ── Method 2: TF-IDF cosine similarity ────────────────────────────────────
    tfidf_scores = {sec["id"]: 0.0 for sec in sections}

    if _SKLEARN_OK:
        try:
            corpus = [f"{s['crime_name']} {s['description']} {s['keywords']}" for s in sections]
            vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform(corpus + [text])
            sims = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
            for idx, sec in enumerate(sections):
                tfidf_scores[sec["id"]] = float(sims[idx])
        except Exception:
            pass

    # ── Combine scores (60% TF-IDF + 40% keyword) ────────────────────────────
    combined = []
    for sec in sections:
        sid   = sec["id"]
        score = 0.6 * tfidf_scores[sid] + 0.4 * kw_scores[sid]
        if score > 0:
            combined.append({**sec, "match_score": round(score, 4), "match_method": "combined"})

    combined.sort(key=lambda x: x["match_score"], reverse=True)
    return combined[:top_n]
