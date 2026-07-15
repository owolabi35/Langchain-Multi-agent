"""
Streamlit frontend for the LangChain Multi-Agent Research Pipeline.

Expects a `run_research_pipeline(topic: str) -> dict` function in
src/pipelines/pipeline.py that returns a state dict, e.g.:
    {
        "search_results": "...",
        "reader_results": "...",
        "writer_results": "...",
        "critic_results": "...",
    }

Only "search_results" is guaranteed based on the current pipeline.py —
the app gracefully displays whatever keys are present in the returned state.
"""

import time
import streamlit as st

# ----------------------------------------------------------------------
# Import the pipeline. Adjust the import path if your project layout
# differs from src/pipelines/pipeline.py
# ----------------------------------------------------------------------
try:
    from src.pipelines.pipeline import run_research_pipeline
except ImportError as e:
    run_research_pipeline = None
    IMPORT_ERROR = str(e)
else:
    IMPORT_ERROR = None


# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Research Agent Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# Custom CSS — dark, glassy, gradient-accented aesthetic
# ----------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 15% 10%, #1a1c3a 0%, #0d0e21 45%, #08091a 100%);
        color: #e6e6f0;
    }

    /* Hide default streamlit chrome */
    #MainMenu, footer, header {visibility: hidden;}

    /* Hero header */
    .hero {
        padding: 2.2rem 2rem;
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(124,92,255,0.18), rgba(56,189,248,0.10));
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1.6rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    }
    .hero h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(90deg, #a78bfa, #38bdf8 60%, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero p {
        color: #a3a6c2;
        font-size: 1.02rem;
        margin-top: 0.4rem;
    }

    /* Agent pipeline chips */
    .pipeline-track {
        display: flex;
        gap: 0.6rem;
        margin-top: 1.1rem;
        flex-wrap: wrap;
    }
    .chip {
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.04);
        color: #b9bcd6;
    }
    .chip.active {
        background: linear-gradient(90deg, #7c5cff, #38bdf8);
        color: white;
        border: none;
        box-shadow: 0 0 16px rgba(124,92,255,0.5);
    }
    .chip.done {
        background: rgba(74, 222, 128, 0.14);
        border: 1px solid rgba(74, 222, 128, 0.4);
        color: #86efac;
    }

    /* Card container */
    .glass-card {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 1.5rem 1.7rem;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(10px);
    }
    .glass-card h3 {
        font-family: 'Space Grotesk', sans-serif;
        margin-top: 0;
        font-size: 1.15rem;
        color: #f1f1fb;
    }

    /* Input styling */
    div[data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 12px;
        color: #f1f1fb;
        padding: 0.7rem 1rem;
        font-size: 1rem;
    }
    div[data-testid="stTextInput"] input:focus {
        border: 1px solid #7c5cff;
        box-shadow: 0 0 0 3px rgba(124,92,255,0.25);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #7c5cff, #38bdf8);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.65rem 1.6rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-shadow: 0 4px 18px rgba(124,92,255,0.35);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(124,92,255,0.5);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12132b, #0a0b1c);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] * {
        color: #cfd1e8;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        color: #a3a6c2;
        font-weight: 500;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #f1f1fb;
        border-bottom: 2px solid #7c5cff;
    }

    /* Metric cards */
    .metric-box {
        text-align: center;
        padding: 1rem;
        border-radius: 14px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
    }
    .metric-box .value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #a78bfa;
    }
    .metric-box .label {
        font-size: 0.78rem;
        color: #9295b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    code, pre {
        background: rgba(0,0,0,0.35) !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None
if "topic" not in st.session_state:
    st.session_state.topic = "Latest advances in mRNA vaccine technology"


# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧠 Research Agent Studio")
    st.caption("Multi-agent LangChain research pipeline")
    st.divider()

    st.markdown("**Pipeline stages**")
    st.markdown("1. 🔎 Search Agent — gathers sources\n"
                "2. 📖 Reader Agent — extracts & digests\n"
                "3. ✍️ Writer Chain — drafts the report\n"
                "4. 🧐 Critic — reviews & refines")

    st.divider()
    st.markdown("**Session history**")
    if st.session_state.history:
        for i, h in enumerate(reversed(st.session_state.history[-10:])):
            st.markdown(f"- {h}")
    else:
        st.caption("No searches yet")

    st.divider()
    if st.button("🗑️ Clear history", use_container_width=True):
        st.session_state.history = []
        st.session_state.result = None
        st.rerun()


# ----------------------------------------------------------------------
# Hero header
# ----------------------------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>Research Agent Studio</h1>
    <p>Ask a question. Watch a team of AI agents search, read, write, and critique the answer for you.</p>
    <div class="pipeline-track">
        <span class="chip">🔎 Search</span>
        <span class="chip">📖 Read</span>
        <span class="chip">✍️ Write</span>
        <span class="chip">🧐 Critique</span>
    </div>
</div>
""", unsafe_allow_html=True)

if IMPORT_ERROR:
    st.warning(
        f"⚠️ Could not import `run_research_pipeline` "
        f"(`{IMPORT_ERROR}`). The UI will still render — fix the import "
        f"path at the top of app.py to match your project structure.",
        icon="⚠️",
    )

# ----------------------------------------------------------------------
# Input row
# ----------------------------------------------------------------------
col1, col2 = st.columns([5, 1])
with col1:
    topic = st.text_input(
        "Research topic",
        key="topic",
        placeholder="e.g. Latest advances in mRNA vaccine technology",
        label_visibility="collapsed",
    )
with col2:
    run_clicked = st.button("🚀 Run", use_container_width=True)

# ----------------------------------------------------------------------
# Run pipeline
# ----------------------------------------------------------------------
if run_clicked and topic.strip():
    st.session_state.topic = topic.strip()
    st.session_state.history.append(topic.strip())

    stage_placeholder = st.empty()
    progress = st.progress(0)

    stages = [
        ("🔎", "Search agent is gathering sources...", 25),
        ("📖", "Reader agent is digesting content...", 55),
        ("✍️", "Writer chain is drafting the report...", 80),
        ("🧐", "Critic is reviewing the draft...", 95),
    ]

    if run_research_pipeline is not None:
        try:
            for icon, msg, pct in stages:
                stage_placeholder.markdown(
                    f"<div class='glass-card'>{icon} &nbsp; {msg}</div>",
                    unsafe_allow_html=True,
                )
                progress.progress(pct)
                time.sleep(0.35)  # purely cosmetic pacing

            result = run_research_pipeline(st.session_state.topic)
            progress.progress(100)
            stage_placeholder.markdown(
                "<div class='glass-card'>✅ &nbsp; Pipeline complete!</div>",
                unsafe_allow_html=True,
            )
            st.session_state.result = result
        except Exception as e:
            stage_placeholder.empty()
            progress.empty()
            st.error(f"❌ Pipeline failed: {e}")
            st.session_state.result = None
    else:
        stage_placeholder.empty()
        progress.empty()
        st.error("`run_research_pipeline` isn't available — check the import path.")

elif run_clicked and not topic.strip():
    st.info("👆 Enter a topic above before running the pipeline.")


# ----------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------
result = st.session_state.result

if result:
    st.markdown("### 📊 Results")

    # Quick metrics row
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f"<div class='metric-box'><div class='value'>{len(result)}</div>"
            f"<div class='label'>Stages returned</div></div>",
            unsafe_allow_html=True,
        )
    with m2:
        total_chars = sum(len(str(v)) for v in result.values())
        st.markdown(
            f"<div class='metric-box'><div class='value'>{total_chars:,}</div>"
            f"<div class='label'>Characters generated</div></div>",
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"<div class='metric-box'><div class='value'>{len(st.session_state.history)}</div>"
            f"<div class='label'>Queries this session</div></div>",
            unsafe_allow_html=True,
        )

    st.write("")

    # Known stage labels, mapped to keys likely returned by the pipeline
    stage_labels = {
        "search_results": ("🔎 Search Results", "Raw findings gathered from the web"),
        "reader_results": ("📖 Reader Notes", "Extracted & summarized source content"),
        "writer_results": ("✍️ Draft Report", "Synthesized written answer"),
        "critic_results": ("🧐 Critic Review", "Feedback and refinements"),
    }

    keys_present = list(result.keys())
    tab_titles = [stage_labels.get(k, (k.replace("_", " ").title(), ""))[0] for k in keys_present]

    if tab_titles:
        tabs = st.tabs(tab_titles)
        for tab, key in zip(tabs, keys_present):
            label, subtitle = stage_labels.get(key, (key.replace("_", " ").title(), ""))
            with tab:
                if subtitle:
                    st.caption(subtitle)
                st.markdown(
                    f"<div class='glass-card'>{result[key]}</div>",
                    unsafe_allow_html=True,
                )
    else:
        st.json(result)

    with st.expander("🔧 Raw state (debug)"):
        st.json(result)

else:
    st.markdown("""
    <div class="glass-card" style="text-align:center; padding: 3rem;">
        <div style="font-size: 2.5rem;">🛰️</div>
        <p style="color:#9295b8; margin-top: 0.6rem;">
            Enter a topic above and hit <b>Run</b> to start the agent pipeline.
        </p>
    </div>
    """, unsafe_allow_html=True)
