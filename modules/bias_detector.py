"""
modules/bias_detector.py
-------------------------
Detect three categories of bias in legal text:
  1. Gender bias        – imbalanced gendered references
  2. Aggressive language bias – use of criminalising / derogatory terms
  3. Emotional / sentiment bias – highly charged language

Produces a bias score (0–100) and a level label: Low / Medium / High.
"""

import re
from collections import Counter


# ─── Word lists ───────────────────────────────────────────────────────────────
MALE_WORDS   = {"he", "him", "his", "man", "men", "boy", "boys", "husband",
                "father", "son", "brother", "male", "sir"}
FEMALE_WORDS = {"she", "her", "hers", "woman", "women", "girl", "girls", "wife",
                "mother", "daughter", "sister", "female", "ma'am"}

AGGRESSIVE_WORDS = {
    "dangerous", "criminal-minded", "violent", "immoral", "suspicious",
    "notorious", "evil", "wicked", "vicious", "brutal", "savage", "monster",
    "psycho", "lunatic", "maniac", "deviant", "predator", "menace",
    "terrorist", "extremist", "radical", "thug", "gangster",
}

EMOTIONAL_WORDS = {
    "horrible", "terrible", "disgusting", "outrageous", "shocking", "appalling",
    "unbelievable", "unacceptable", "heinous", "atrocious", "despicable",
    "monstrous", "horrific", "dreadful", "awful", "abominable",
}


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _tokenise(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z]+\b", text.lower())


def _gender_bias(tokens: list[str]) -> dict:
    male_count   = sum(1 for t in tokens if t in MALE_WORDS)
    female_count = sum(1 for t in tokens if t in FEMALE_WORDS)

    total = male_count + female_count
    if total == 0:
        imbalance = 0.0
    else:
        imbalance = abs(male_count - female_count) / total  # 0 = balanced, 1 = one-sided

    score = round(imbalance * 40, 2)  # max contribution: 40 pts

    return {
        "male_count":   male_count,
        "female_count": female_count,
        "imbalance":    round(imbalance, 3),
        "score":        score,
        "words_found":  [t for t in tokens if t in MALE_WORDS | FEMALE_WORDS],
    }


def _aggressive_bias(tokens: list[str]) -> dict:
    found = [t for t in tokens if t in AGGRESSIVE_WORDS]
    # Remove duplicates but keep count
    freq  = Counter(found)
    score = min(len(set(found)) * 8, 40)  # each unique word = 8 pts, cap at 40

    return {
        "words_found": list(freq.keys()),
        "frequency":   dict(freq),
        "score":       score,
    }


def _emotional_bias(tokens: list[str]) -> dict:
    found = [t for t in tokens if t in EMOTIONAL_WORDS]
    freq  = Counter(found)
    score = min(len(set(found)) * 5, 20)  # cap at 20

    return {
        "words_found": list(freq.keys()),
        "frequency":   dict(freq),
        "score":       score,
    }


def _level(score: float) -> str:
    if score >= 60:
        return "High"
    elif score >= 30:
        return "Medium"
    else:
        return "Low"


# ─── Public API ───────────────────────────────────────────────────────────────
def detect_bias(text: str) -> dict:
    """
    Analyse text for bias.

    Returns:
      {
        "bias_score":       float (0-100),
        "bias_level":       "Low" | "Medium" | "High",
        "gender_bias":      { male_count, female_count, imbalance, score, words_found },
        "aggressive_bias":  { words_found, frequency, score },
        "emotional_bias":   { words_found, frequency, score },
        "recommendations":  list[str],
      }
    """
    tokens = _tokenise(text)

    gender     = _gender_bias(tokens)
    aggressive = _aggressive_bias(tokens)
    emotional  = _emotional_bias(tokens)

    total_score = min(gender["score"] + aggressive["score"] + emotional["score"], 100)

    # Generate textual recommendations
    recs = []
    if gender["imbalance"] > 0.5:
        recs.append("⚠ Gender references are imbalanced. Use neutral language.")
    if aggressive["words_found"]:
        recs.append(f"⚠ Aggressive language detected: {', '.join(aggressive['words_found'][:5])}.")
    if emotional["words_found"]:
        recs.append(f"⚠ Highly emotional language: {', '.join(emotional['words_found'][:5])}.")
    if not recs:
        recs.append("✅ No significant bias detected in the text.")

    return {
        "bias_score":      round(total_score, 2),
        "bias_level":      _level(total_score),
        "gender_bias":     gender,
        "aggressive_bias": aggressive,
        "emotional_bias":  emotional,
        "recommendations": recs,
    }
