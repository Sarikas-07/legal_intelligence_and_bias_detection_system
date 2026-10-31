"""
app.py
------
AI-Powered Legal Intelligence, IPC Recommendation & Bias Detection System
Main Streamlit application entry point.

Run with:
    streamlit run app.py
"""

import os, sys, json, io
from datetime import datetime

import streamlit as st

# ── Ensure modules are importable ─────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Local imports ─────────────────────────────────────────────────────────────
from modules.database_handler   import (
    get_user, verify_password, create_user, get_all_sections,
    add_section, update_section, delete_section, get_all_users,
    delete_user, save_report, get_reports,
)
from modules.pdf_reader          import extract_text_from_pdf, extract_text_from_txt
from modules.preprocessing       import preprocess
from modules.summarizer          import summarize
from modules.keyword_extractor   import extract_keywords, extract_entities, get_legal_terms_found
from modules.sentiment_analysis  import analyze_sentiment
from modules.bias_detector       import detect_bias
from modules.ipc_recommender     import recommend_sections, classify_crime
from modules.legal_matcher       import match_legal_sections
from modules.visualization       import (
    sentiment_gauge, bias_meter, keyword_bar, crime_category_pie,
    ipc_match_bar, bias_breakdown_bar, word_count_comparison,
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "Legal AI System",
    page_icon  = "⚖️",
    layout     = "wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Main card style ── */
.legal-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #0f3460;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
/* ── Section badge ── */
.section-badge {
    background: #0f3460;
    color: #e2e8f0;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
/* ── Crime tag ── */
.crime-tag {
    background: #FF4B4B22;
    border: 1px solid #FF4B4B;
    color: #FF4B4B;
    padding: 3px 10px;
    border-radius: 14px;
    margin: 3px;
    display: inline-block;
    font-size: 0.8rem;
}
/* ── Legal keyword highlight ── */
.legal-kw {
    background: #FFD70033;
    border: 1px solid #FFD700;
    color: #FFD700;
    padding: 2px 8px;
    border-radius: 10px;
    margin: 2px;
    display: inline-block;
    font-size: 0.8rem;
}
/* ── Bias level colours ── */
.bias-low    { color: #2ECC71; font-weight:700; }
.bias-medium { color: #FFD700; font-weight:700; }
.bias-high   { color: #FF4B4B; font-weight:700; }
/* ── Disclaimer banner ── */
.disclaimer {
    background: #FFF3CD;
    border-left: 4px solid #FFC107;
    padding: 10px 14px;
    border-radius: 6px;
    color: #856404;
    font-size: 0.87rem;
    margin-bottom: 1rem;
}
/* ── Title banner ── */
.title-banner {
    background: linear-gradient(90deg, #0f3460, #533483);
    padding: 1rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
if "logged_in"  not in st.session_state:  st.session_state.logged_in  = False
if "username"   not in st.session_state:  st.session_state.username   = ""
if "role"       not in st.session_state:  st.session_state.role       = "user"
if "page"       not in st.session_state:  st.session_state.page       = "analyze"
if "analysis"   not in st.session_state:  st.session_state.analysis   = None


# ─────────────────────────────────────────────────────────────────────────────
# ── AUTH PAGES ────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
def show_login():
    st.markdown("""
    <div class='title-banner'>
        <h1 style='color:white;margin:0'>⚖️ Legal AI Intelligence System</h1>
        <p style='color:#aaa;margin:4px 0 0'>IPC Recommendation · Bias Detection · Legal Analysis</p>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Register"])

        # ── LOGIN ──────────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("#### Welcome back")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True, type="primary"):
                user = get_user(username)
                if user and verify_password(password, user["password_hash"]):
                    st.session_state.logged_in = True
                    st.session_state.username  = user["username"]
                    st.session_state.role      = user["role"]
                    st.success(f"Welcome, {user['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            st.caption("Default admin: **admin** / **admin123**")

        # ── REGISTER ──────────────────────────────────────────────────────────
        with tab_signup:
            st.markdown("#### Create an account")
            new_user = st.text_input("Choose Username", key="reg_user")
            new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
            conf_pass= st.text_input("Confirm Password",type="password", key="reg_conf")
            if st.button("Register", use_container_width=True):
                if not new_user or not new_pass:
                    st.warning("Username and password are required.")
                elif new_pass != conf_pass:
                    st.error("Passwords do not match.")
                elif len(new_pass) < 6:
                    st.warning("Password must be at least 6 characters.")
                else:
                    ok = create_user(new_user, new_pass, role="user")
                    if ok:
                        st.success("Account created! Please login.")
                    else:
                        st.error("Username already taken. Choose another.")


# ─────────────────────────────────────────────────────────────────────────────
# ── SIDEBAR NAVIGATION ────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown(f"### ⚖️ Legal AI System")
        st.markdown(f"👤 **{st.session_state.username}**  `{st.session_state.role.upper()}`")
        st.divider()

        pages_user  = {"🔍 Analyze Complaint": "analyze",
                       "📚 Legal Database":    "db_view",
                       "📋 My Reports":        "my_reports"}
        pages_admin = {"🔍 Analyze Complaint": "analyze",
                       "📚 Legal Database":    "db_view",
                       "➕ Manage Sections":   "manage_sections",
                       "👥 Manage Users":      "manage_users",
                       "📋 All Reports":       "all_reports"}

        pages = pages_admin if st.session_state.role == "admin" else pages_user

        for label, key in pages.items():
            if st.button(label, use_container_width=True,
                         type="primary" if st.session_state.page == key else "secondary"):
                st.session_state.page = key
                st.rerun()

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["logged_in", "username", "role", "page", "analysis"]:
                st.session_state.pop(k, None)
            st.rerun()

        st.markdown("""<div class='disclaimer'>
            ⚠️ <b>Disclaimer:</b> This system provides AI-generated legal suggestions
            and should <u>not</u> be considered official legal advice.
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ── HELPER: highlight legal keywords in text ─────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
def highlight_text(text: str, keywords: list[str]) -> str:
    """Return HTML string with legal keywords highlighted."""
    import re
    result = text
    for kw in sorted(set(keywords), key=len, reverse=True):
        pattern = re.compile(rf"\b({re.escape(kw)})\b", re.IGNORECASE)
        result  = pattern.sub(r"<mark style='background:#FFD70044;border-radius:4px;padding:1px 3px'>\1</mark>", result)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# ── RUN FULL ANALYSIS ────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
def run_analysis(text: str) -> dict:
    """Run all NLP modules and return a combined results dict."""
    with st.spinner("🔍 Preprocessing text…"):
        prep = preprocess(text)

    with st.spinner("📄 Summarising document…"):
        summ = summarize(text, use_transformer=False)  # set True if GPU available

    with st.spinner("🔑 Extracting keywords…"):
        kws      = extract_keywords(text)
        entities = extract_entities(text)
        legal_kw = get_legal_terms_found(text)

    with st.spinner("💬 Analysing sentiment…"):
        sent = analyze_sentiment(text)

    with st.spinner("🚨 Detecting bias…"):
        bias = detect_bias(text)

    with st.spinner("⚖️ Classifying crime & recommending IPC sections…"):
        categories = classify_crime(text)
        sections   = recommend_sections(text, top_n=6)

    return {
        "text":       text,
        "prep":       prep,
        "summary":    summ,
        "keywords":   kws,
        "entities":   entities,
        "legal_kw":   legal_kw,
        "sentiment":  sent,
        "bias":       bias,
        "categories": categories,
        "sections":   sections,
        "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# ── PAGE: ANALYZE COMPLAINT ──────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
def page_analyze():
    st.markdown("""<div class='title-banner'>
        <h2 style='color:white;margin:0'>🔍 Legal Complaint Analyzer</h2>
        <p style='color:#bbb;margin:4px 0 0'>Upload a complaint or type a crime description to get AI-powered legal insights</p>
    </div>""", unsafe_allow_html=True)

    # ── Input area ────────────────────────────────────────────────────────────
    input_col, info_col = st.columns([2, 1])

    with input_col:
        input_mode = st.radio("Input Method", ["✏️ Type / Paste Text", "📄 Upload PDF", "📝 Upload TXT"],
                              horizontal=True)

        text_input = ""

        if input_mode == "✏️ Type / Paste Text":
            sample_options = {
                "— Select a sample —": "",
                "Knife Attack + Theft": "A person was attacked by an unknown individual with a sharp knife on the road. The attacker stabbed the victim on the arm and forcefully snatched the victim's wallet containing Rs. 5000 cash and a mobile phone worth Rs. 15,000.",
                "Bank Account Hacking": "The accused hacked into the victim's bank account using phishing techniques and stole Rs. 2 lakh by making unauthorised transactions.",
                "Domestic Violence": "The husband subjected his wife to severe mental and physical cruelty for dowry demands. He beat her regularly and threatened to kill her if she complained to the police.",
                "Kidnapping": "An unknown person forcefully abducted a 10-year-old child from outside the school. The accused demanded Rs. 10 lakh ransom from the family.",
                "Drug Trafficking": "The accused was found in possession of 500 grams of heroin and was trafficking narcotic substances across state borders.",
            }
            choice = st.selectbox("Load a sample complaint", list(sample_options.keys()))
            text_input = st.text_area(
                "Enter Legal Complaint / Crime Description",
                value = sample_options[choice],
                height= 200,
                placeholder="Describe the crime or paste legal complaint text here…",
            )

        elif input_mode == "📄 Upload PDF":
            f = st.file_uploader("Upload PDF", type=["pdf"])
            if f:
                text_input = extract_text_from_pdf(f.read())
                st.text_area("Extracted Text (preview)", text_input[:800] + "…", height=180, disabled=True)

        else:  # TXT
            f = st.file_uploader("Upload TXT file", type=["txt"])
            if f:
                text_input = extract_text_from_txt(f.read())
                st.text_area("Extracted Text (preview)", text_input[:800] + "…", height=180, disabled=True)

        analyse_btn = st.button("⚡ Analyse Complaint", type="primary", use_container_width=True,
                                disabled=len(text_input.strip()) < 20)

    with info_col:
        st.markdown("""
        <div class='legal-card'>
        <b>📌 What this system analyses:</b><br><br>
        ✅ Crime classification<br>
        ✅ IPC / BNS section recommendation<br>
        ✅ Legal document summarisation<br>
        ✅ Keyword & entity extraction<br>
        ✅ Sentiment analysis<br>
        ✅ Language bias detection<br>
        ✅ Punishment details<br>
        ✅ Exportable report<br>
        </div>
        """, unsafe_allow_html=True)

    # ── Run analysis ──────────────────────────────────────────────────────────
    if analyse_btn:
        if len(text_input.strip()) < 20:
            st.error("Please enter at least 20 characters.")
        else:
            st.session_state.analysis = run_analysis(text_input)

    # ── Display results ───────────────────────────────────────────────────────
    a = st.session_state.analysis
    if a is None:
        return

    st.divider()
    st.subheader("📊 Analysis Results")

    # ── Crime categories ──────────────────────────────────────────────────────
    if a["categories"]:
        st.markdown("**🏷 Detected Crime Categories:**")
        html_tags = "".join(f"<span class='crime-tag'>{c}</span>" for c in a["categories"])
        st.markdown(html_tags, unsafe_allow_html=True)
        st.plotly_chart(crime_category_pie(a["categories"]), use_container_width=True)

    tabs = st.tabs(["📄 Summary", "⚖️ IPC Sections", "🔑 Keywords", "💬 Sentiment", "🚨 Bias", "📤 Export"])

    # ────────────────────────────────────────────────
    # TAB 1: SUMMARY
    # ────────────────────────────────────────────────
    with tabs[0]:
        s = a["summary"]
        colA, colB = st.columns(2)
        colA.metric("Original Word Count", s["original_length"])
        colB.metric("Summary Word Count",  s["summary_length"])
        st.metric("Compression Ratio", f"{s['compression_ratio']:.1%}")

        st.markdown("**📝 AI-Generated Summary:**")
        st.info(s["summary"])

        st.plotly_chart(
            word_count_comparison(s["original_length"], s["summary_length"]),
            use_container_width=True,
        )

        with st.expander("🔍 Highlighted Legal Terms in Original Text"):
            highlighted = highlight_text(a["text"], a["legal_kw"])
            st.markdown(highlighted, unsafe_allow_html=True)

    # ────────────────────────────────────────────────
    # TAB 2: IPC / BNS SECTIONS
    # ────────────────────────────────────────────────
    with tabs[1]:
        sections = a["sections"]
        if not sections:
            st.warning("No matching IPC/BNS sections found.")
        else:
            st.plotly_chart(ipc_match_bar(sections), use_container_width=True)

            for sec in sections:
                score_pct = round(sec.get("match_score", 0) * 100, 1)
                with st.expander(f"📌 {sec['section']}  —  {sec['crime_name']}  (Match: {score_pct}%)"):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.markdown(f"**Description:** {sec['description']}")
                        st.markdown(f"**Relevant Keywords:** `{sec['keywords']}`")
                    with c2:
                        st.markdown(f"**⚖️ Punishment:**")
                        st.error(sec["punishment"])

    # ────────────────────────────────────────────────
    # TAB 3: KEYWORDS
    # ────────────────────────────────────────────────
    with tabs[2]:
        kws = a["keywords"]
        if kws:
            st.plotly_chart(keyword_bar(kws), use_container_width=True)

            st.markdown("**🔴 Legal Keywords Found:**")
            legal_tags = "".join(
                f"<span class='legal-kw'>{k['word']} ({k['frequency']})</span>"
                for k in kws if k["is_legal"]
            )
            st.markdown(legal_tags or "_None detected_", unsafe_allow_html=True)

            with st.expander("Named Entities Detected"):
                ents = a["entities"]
                if ents:
                    for etype, names in ents.items():
                        st.markdown(f"**{etype}:** {', '.join(names)}")
                else:
                    st.write("No named entities detected.")

        # Preprocess stats
        with st.expander("📊 Text Preprocessing Stats"):
            p = a["prep"]
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Words",        p["word_count"])
            c2.metric("Unique Words",        p["unique_words"])
            c3.metric("Filtered Tokens",     len(p["filtered_tokens"]))

    # ────────────────────────────────────────────────
    # TAB 4: SENTIMENT
    # ────────────────────────────────────────────────
    with tabs[3]:
        sent = a["sentiment"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Polarity",     f"{sent['polarity']:+.3f}")
        c2.metric("Subjectivity", f"{sent['subjectivity']:.3f}")
        c3.metric("Label",        sent["label"])

        st.plotly_chart(sentiment_gauge(sent["polarity"]), use_container_width=True)

        if sent["negative_words"]:
            st.markdown("**Negative Legal Words Found:**")
            st.markdown(" ".join(f"`{w}`" for w in sent["negative_words"]))
        if sent["positive_words"]:
            st.markdown("**Positive Legal Words Found:**")
            st.markdown(" ".join(f"`{w}`" for w in sent["positive_words"]))

    # ────────────────────────────────────────────────
    # TAB 5: BIAS
    # ────────────────────────────────────────────────
    with tabs[4]:
        b      = a["bias"]
        level  = b["bias_level"]
        color_class = f"bias-{level.lower()}"

        c1, c2 = st.columns(2)
        c1.plotly_chart(bias_meter(b["bias_score"]), use_container_width=True)
        with c2:
            st.markdown(f"**Bias Level:** <span class='{color_class}'>{level}</span>",
                        unsafe_allow_html=True)
            st.markdown(f"**Bias Score:** `{b['bias_score']}/100`")
            st.markdown("**Recommendations:**")
            for rec in b["recommendations"]:
                st.markdown(rec)

        st.plotly_chart(
            bias_breakdown_bar(
                b["gender_bias"]["score"],
                b["aggressive_bias"]["score"],
                b["emotional_bias"]["score"],
            ),
            use_container_width=True,
        )

        with st.expander("🔍 Detailed Bias Breakdown"):
            g = b["gender_bias"]
            st.markdown(f"**Gender Bias:** Male refs = `{g['male_count']}`, Female refs = `{g['female_count']}`, Imbalance = `{g['imbalance']:.2f}`")
            if g["words_found"]:
                st.markdown(f"Words: {', '.join(set(g['words_found']))}")

            ag = b["aggressive_bias"]
            if ag["words_found"]:
                st.markdown(f"**Aggressive Words:** {', '.join(ag['words_found'])}")

            em = b["emotional_bias"]
            if em["words_found"]:
                st.markdown(f"**Emotional Words:** {', '.join(em['words_found'])}")

    # ────────────────────────────────────────────────
    # TAB 6: EXPORT
    # ────────────────────────────────────────────────
    with tabs[5]:
        st.markdown("#### 📤 Export Analysis Report")
        a_data = a

        report_text = f"""
==============================================================
 AI-POWERED LEGAL INTELLIGENCE SYSTEM - ANALYSIS REPORT
==============================================================
Generated  : {a_data['timestamp']}
Analysed by: {st.session_state.username}

DISCLAIMER: This is an AI-generated report for educational purposes only.
It does NOT constitute official legal advice.

──────────────────────────────────────────────────────────────
CRIME DESCRIPTION (EXCERPT)
──────────────────────────────────────────────────────────────
{a_data['text'][:500]}{'…' if len(a_data['text']) > 500 else ''}

──────────────────────────────────────────────────────────────
DETECTED CRIME CATEGORIES
──────────────────────────────────────────────────────────────
{chr(10).join('• ' + c for c in a_data['categories']) or 'None detected'}

──────────────────────────────────────────────────────────────
AI-GENERATED SUMMARY
──────────────────────────────────────────────────────────────
Method  : {a_data['summary']['method']}
Original: {a_data['summary']['original_length']} words
Summary : {a_data['summary']['summary_length']} words

{a_data['summary']['summary']}

──────────────────────────────────────────────────────────────
SUGGESTED IPC / BNS SECTIONS
──────────────────────────────────────────────────────────────
{chr(10).join(f"[{i+1}] {s['section']} – {s['crime_name']} (Match: {round(s.get('match_score',0)*100,1)}%)" + chr(10) + f"    Punishment: {s['punishment']}" for i, s in enumerate(a_data['sections'])) or 'No sections matched.'}

──────────────────────────────────────────────────────────────
SENTIMENT ANALYSIS
──────────────────────────────────────────────────────────────
Polarity     : {a_data['sentiment']['polarity']:+.3f}
Subjectivity : {a_data['sentiment']['subjectivity']:.3f}
Label        : {a_data['sentiment']['label']}
Intensity    : {a_data['sentiment']['intensity']}

──────────────────────────────────────────────────────────────
BIAS DETECTION
──────────────────────────────────────────────────────────────
Bias Score : {a_data['bias']['bias_score']}/100
Bias Level : {a_data['bias']['bias_level']}

{chr(10).join(a_data['bias']['recommendations'])}

──────────────────────────────────────────────────────────────
TOP KEYWORDS EXTRACTED
──────────────────────────────────────────────────────────────
{', '.join(k['word'] + f"({k['frequency']})" for k in a_data['keywords'][:10])}

==============================================================
 END OF REPORT
==============================================================
"""

        st.text_area("Report Preview", report_text, height=300)

        st.download_button(
            label    = "⬇️ Download Report (.txt)",
            data     = report_text,
            file_name= f"legal_report_{a_data['timestamp'].replace(' ','_').replace(':','-')}.txt",
            mime     = "text/plain",
            type     = "primary",
        )

        # Auto-save to DB
        if st.button("💾 Save Report to Database"):
            save_report(
                username    = st.session_state.username,
                input_text  = a_data["text"][:1000],
                summary     = a_data["summary"]["summary"],
                crime_types = ", ".join(a_data["categories"]),
                ipc_sections= "; ".join(s["section"] for s in a_data["sections"]),
                sentiment   = a_data["sentiment"]["label"],
                bias_score  = a_data["bias"]["bias_score"],
            )
            st.success("✅ Report saved to database.")


# ─────────────────────────────────────────────────────────────────────────────
# ── PAGE: LEGAL DATABASE VIEWER ──────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
def page_db_view():
    st.subheader("📚 Legal Database – IPC / BNS Sections")

    search = st.text_input("🔎 Search by keyword or crime name", placeholder="e.g. theft, murder, cyber")

    try:
        sections = get_all_sections()
    except FileNotFoundError as e:
        st.error(str(e))
        return

    if search:
        q = search.lower()
        sections = [s for s in sections
                    if q in s["keywords"].lower()
                    or q in s["crime_name"].lower()
                    or q in s["section"].lower()]

    st.caption(f"Showing {len(sections)} section(s)")

    for sec in sections:
        with st.expander(f"📌 {sec['section']}  —  {sec['crime_name']}"):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"**Description:** {sec['description']}")
                st.markdown(f"**Keywords:** `{sec['keywords']}`")
            with c2:
                st.markdown("**Punishment:**")
                st.error(sec["punishment"])


# ─────────────────────────────────────────────────────────────────────────────
# ── ADMIN PAGE: MANAGE SECTIONS ──────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
def page_manage_sections():
    st.subheader("➕ Manage Legal Sections (Admin)")

    t_add, t_edit, t_del = st.tabs(["➕ Add Section", "✏️ Edit Section", "🗑️ Delete Section"])

    with t_add:
        with st.form("add_section_form"):
            section     = st.text_input("Section Number (e.g. IPC 302 / BNS 103)")
            crime_name  = st.text_input("Crime Name")
            description = st.text_area("Description")
            punishment  = st.text_area("Punishment")
            keywords    = st.text_input("Keywords (comma-separated)")
            submitted   = st.form_submit_button("Add Section", type="primary")
            if submitted:
                if all([section, crime_name, description, punishment, keywords]):
                    add_section(section, crime_name, description, punishment, keywords)
                    st.success("✅ Section added successfully.")
                else:
                    st.warning("All fields are required.")

    with t_edit:
        sections = get_all_sections()
        opts     = {f"{s['id']} – {s['section']} ({s['crime_name']})": s for s in sections}
        choice   = st.selectbox("Select section to edit", list(opts.keys()))
        if choice:
            s = opts[choice]
            with st.form("edit_form"):
                n_sec  = st.text_input("Section", s["section"])
                n_name = st.text_input("Crime Name", s["crime_name"])
                n_desc = st.text_area("Description", s["description"])
                n_pun  = st.text_area("Punishment", s["punishment"])
                n_kw   = st.text_input("Keywords", s["keywords"])
                if st.form_submit_button("Save Changes", type="primary"):
                    update_section(s["id"], n_sec, n_name, n_desc, n_pun, n_kw)
                    st.success("✅ Section updated.")

    with t_del:
        sections = get_all_sections()
        opts     = {f"{s['id']} – {s['section']} ({s['crime_name']})": s["id"] for s in sections}
        choice   = st.selectbox("Select section to delete", list(opts.keys()), key="del_sec")
        if st.button("🗑️ Delete", type="primary"):
            delete_section(opts[choice])
            st.success("Section deleted.")
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ── ADMIN PAGE: MANAGE USERS ─────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
def page_manage_users():
    st.subheader("👥 Manage Users (Admin)")
    users = get_all_users()

    import pandas as pd
    df = pd.DataFrame(users)[["id", "username", "role", "created_at"]]
    st.dataframe(df, use_container_width=True)

    st.markdown("**Delete a User:**")
    unames = [u["username"] for u in users if u["username"] != "admin"]
    if unames:
        to_del = st.selectbox("Select user to delete", unames)
        if st.button("🗑️ Delete User"):
            delete_user(to_del)
            st.success(f"User '{to_del}' deleted.")
            st.rerun()
    else:
        st.info("No non-admin users found.")


# ─────────────────────────────────────────────────────────────────────────────
# ── PAGE: REPORTS ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
def page_reports(admin: bool = False):
    title = "📋 All Reports (Admin)" if admin else "📋 My Reports"
    st.subheader(title)

    username = None if admin else st.session_state.username
    reports  = get_reports(username)

    if not reports:
        st.info("No reports found.")
        return

    import pandas as pd
    df = pd.DataFrame(reports)[[
        "id", "username", "crime_types", "ipc_sections",
        "sentiment", "bias_score", "created_at"
    ]]
    df.columns = ["ID", "User", "Crime Types", "IPC Sections", "Sentiment", "Bias Score", "Created At"]
    st.dataframe(df, use_container_width=True)

    # Expandable detail
    for r in reports[:10]:
        with st.expander(f"📄 Report #{r['id']}  —  {r['created_at']}"):
            st.markdown(f"**User:** {r['username']}")
            st.markdown(f"**Crime Types:** {r['crime_types']}")
            st.markdown(f"**IPC Sections:** {r['ipc_sections']}")
            st.markdown(f"**Sentiment:** {r['sentiment']}")
            st.markdown(f"**Bias Score:** {r['bias_score']}")
            st.markdown(f"**Summary:**")
            st.info(r["summary"] or "N/A")


# ─────────────────────────────────────────────────────────────────────────────
# ── MAIN ROUTER ───────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        show_login()
        return

    show_sidebar()

    page = st.session_state.page

    try:
        if   page == "analyze":        page_analyze()
        elif page == "db_view":        page_db_view()
        elif page == "manage_sections" and st.session_state.role == "admin":
                                       page_manage_sections()
        elif page == "manage_users"   and st.session_state.role == "admin":
                                       page_manage_users()
        elif page == "all_reports"    and st.session_state.role == "admin":
                                       page_reports(admin=True)
        elif page == "my_reports":     page_reports(admin=False)
        else:
            st.error("Page not found or access denied.")
    except FileNotFoundError as e:
        st.error(f"Database error: {e}")
        st.info("Please run:  `python database/create_database.py`  to initialise the database.")


if __name__ == "__main__":
    main()
