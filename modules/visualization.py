"""
modules/visualization.py
-------------------------
All Plotly chart generators for the Streamlit dashboard.
Each function returns a Plotly figure object.
"""

import plotly.graph_objects as go
import plotly.express       as px


# ── Colour palette ─────────────────────────────────────────────────────────────
COLORS = px.colors.qualitative.Safe


def sentiment_gauge(polarity: float) -> go.Figure:
    """Gauge chart showing sentiment polarity (-1 to 1)."""
    fig = go.Figure(go.Indicator(
        mode  = "gauge+number+delta",
        value = polarity,
        title = {"text": "Sentiment Polarity", "font": {"size": 18}},
        delta = {"reference": 0},
        gauge = {
            "axis":  {"range": [-1, 1], "tickwidth": 1},
            "bar":   {"color": "#4A90E2"},
            "steps": [
                {"range": [-1,  -0.2], "color": "#FF4B4B"},
                {"range": [-0.2, 0.2], "color": "#FFD700"},
                {"range": [0.2,  1.0], "color": "#2ECC71"},
            ],
            "threshold": {
                "line":  {"color": "white", "width": 4},
                "thickness": 0.75,
                "value": polarity,
            },
        },
    ))
    fig.update_layout(height=280, margin=dict(t=40, b=10, l=10, r=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def bias_meter(bias_score: float) -> go.Figure:
    """Gauge chart showing bias score (0–100)."""
    color = "#2ECC71" if bias_score < 30 else "#FFD700" if bias_score < 60 else "#FF4B4B"
    fig = go.Figure(go.Indicator(
        mode  = "gauge+number",
        value = bias_score,
        title = {"text": "Bias Score (0-100)", "font": {"size": 18}},
        gauge = {
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar":  {"color": color},
            "steps": [
                {"range": [0,  30], "color": "#d4f4dd"},
                {"range": [30, 60], "color": "#fff4cc"},
                {"range": [60, 100], "color": "#ffd6d6"},
            ],
        },
    ))
    fig.update_layout(height=280, margin=dict(t=40, b=10, l=10, r=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def keyword_bar(keywords: list[dict]) -> go.Figure:
    """Horizontal bar chart of keyword frequencies."""
    if not keywords:
        return go.Figure()

    words  = [k["word"]      for k in keywords]
    freqs  = [k["frequency"] for k in keywords]
    colors = ["#FF4B4B" if k["is_legal"] else "#4A90E2" for k in keywords]

    fig = go.Figure(go.Bar(
        x           = freqs,
        y           = words,
        orientation = "h",
        marker_color= colors,
        text        = freqs,
        textposition= "outside",
    ))
    fig.update_layout(
        title     = "Top Keywords  (🔴 Legal Terms | 🔵 General)",
        xaxis_title="Frequency",
        height    = max(300, len(keywords) * 30),
        margin    = dict(l=120, r=30, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(autorange="reversed")
    return fig


def crime_category_pie(categories: list[str]) -> go.Figure:
    """Pie chart of detected crime categories."""
    if not categories:
        return go.Figure()

    fig = go.Figure(go.Pie(
        labels   = categories,
        values   = list(range(len(categories), 0, -1)),  # rank weighting
        hole     = 0.35,
        marker   = {"colors": COLORS},
    ))
    fig.update_layout(
        title = "Detected Crime Categories",
        height= 360,
        margin= dict(t=50, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def ipc_match_bar(sections: list[dict]) -> go.Figure:
    """Horizontal bar chart of IPC section match scores."""
    if not sections:
        return go.Figure()

    labels = [f"{s['section']} – {s['crime_name']}" for s in sections]
    scores = [round(s.get("match_score", s.get("similarity_score", 0)) * 100, 1) for s in sections]

    fig = go.Figure(go.Bar(
        x            = scores,
        y            = labels,
        orientation  = "h",
        marker_color = "#4A90E2",
        text         = [f"{sc}%" for sc in scores],
        textposition = "outside",
    ))
    fig.update_layout(
        title     = "IPC/BNS Section Match Scores",
        xaxis_title="Match Score (%)",
        height    = max(300, len(sections) * 45),
        margin    = dict(l=280, r=50, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
    )
    fig.update_xaxes(range=[0, 120], showgrid=False)
    fig.update_yaxes(autorange="reversed")
    return fig


def bias_breakdown_bar(gender_score: float, aggressive_score: float, emotional_score: float) -> go.Figure:
    """Grouped bar showing breakdown of bias sub-scores."""
    labels = ["Gender Bias", "Aggressive Language", "Emotional Language"]
    values = [gender_score, aggressive_score, emotional_score]
    colors = ["#FF9F40", "#FF4B4B", "#9B59B6"]

    fig = go.Figure(go.Bar(
        x           = labels,
        y           = values,
        marker_color= colors,
        text        = [f"{v:.1f}" for v in values],
        textposition= "outside",
    ))
    fig.update_layout(
        title   = "Bias Breakdown by Category",
        yaxis   = {"range": [0, 55], "title": "Score"},
        height  = 320,
        margin  = dict(t=50, b=30, l=40, r=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
    )
    return fig


def word_count_comparison(original: int, summary: int) -> go.Figure:
    """Bar comparison of original vs summary word count."""
    fig = go.Figure(go.Bar(
        x           = ["Original Text", "Summary"],
        y           = [original, summary],
        marker_color= ["#4A90E2", "#2ECC71"],
        text        = [original, summary],
        textposition= "outside",
    ))
    fig.update_layout(
        title  = "Document Length: Original vs Summary",
        yaxis  = {"title": "Word Count"},
        height = 300,
        margin = dict(t=50, b=30, l=40, r=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
    )
    return fig
