"""
modules/legal_matcher.py
-------------------------
Fine-grained NLP-based matching between user complaint and legal section descriptions.
Uses TF-IDF + cosine similarity on section descriptions (not just keywords).
Also provides a ranked comparison table.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.database_handler import get_all_sections

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _SKLEARN_OK = True
except ImportError:
    _SKLEARN_OK = False


def match_legal_sections(complaint: str, top_n: int = 8) -> list[dict]:
    """
    Return the top-N sections ranked by semantic similarity to the complaint.

    Each result dict contains:
      section, crime_name, description, punishment, keywords,
      similarity_score (0-1), confidence_label
    """
    sections = get_all_sections()
    if not sections or not _SKLEARN_OK:
        return []

    # Build corpus: description + crime_name + keywords for each section
    corpus = [
        f"{s['crime_name']} {s['description']} {s['keywords']}"
        for s in sections
    ]

    try:
        vec  = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=5000)
        mat  = vec.fit_transform(corpus + [complaint])
        sims = cosine_similarity(mat[-1], mat[:-1]).flatten()
    except Exception:
        return []

    results = []
    for idx, sec in enumerate(sections):
        score = float(sims[idx])
        if score > 0.01:
            label = (
                "Very High" if score >= 0.5 else
                "High"      if score >= 0.3 else
                "Medium"    if score >= 0.15 else
                "Low"
            )
            results.append({
                **sec,
                "similarity_score":  round(score, 4),
                "confidence_label":  label,
            })

    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:top_n]
