"""
Streamlit Frontend - Beautiful Light Theme
Run: streamlit run ui/app.py
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.io as pio

from agents.root_agent    import run_agent
from tools.data_ingestion import data_ingestion_tool, get_active_dataframe

st.set_page_config(
    page_title="DataPilot",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #F7F4EF !important;
    color: #1A1A1A !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Hide Streamlit chrome ────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stToolbar"] { display: none; }

/* ── Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1.5px solid #E8E2D9 !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
}

/* ── Sidebar brand ────────────────────────────────────────── */
.brand-block {
    padding: 0 1.5rem 1.5rem;
    border-bottom: 1.5px solid #F0EBE3;
    margin-bottom: 1.5rem;
}
.brand-title {
    font-family: 'DM Serif Display', serif;
    font-size: 26px;
    color: #1A1A1A;
    line-height: 1.1;
    margin-bottom: 4px;
}
.brand-title span { color: #E8622A; font-style: italic; }
.brand-sub {
    font-size: 11px;
    color: #9A8F85;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 500;
}

/* ── Upload zone ──────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #FBF8F4 !important;
    border: 2px dashed #D4C9BC !important;
    border-radius: 12px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #E8622A !important;
}
[data-testid="stFileUploadDropzone"] {
    background: transparent !important;
}

/* ── Success / info banners ───────────────────────────────── */
.data-pill {
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, #FFF8F5, #FFF3EE);
    border: 1.5px solid #F5C9B5;
    border-radius: 10px;
    padding: 10px 14px;
    margin: 8px 0;
    font-size: 13px;
    color: #C44D1E;
    font-weight: 500;
}
.data-pill .icon { font-size: 16px; }

/* ── Quick prompt buttons ─────────────────────────────────── */
.stButton > button {
    width: 100% !important;
    background: #FAFAF8 !important;
    border: 1.5px solid #E5DDD4 !important;
    border-radius: 8px !important;
    color: #4A4035 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    padding: 8px 12px !important;
    text-align: left !important;
    transition: all 0.15s ease !important;
    margin-bottom: 4px !important;
}
.stButton > button:hover {
    background: #FFF3EE !important;
    border-color: #E8622A !important;
    color: #E8622A !important;
    transform: translateX(3px) !important;
}

/* ── Main chat area ───────────────────────────────────────── */
.main-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #E8E2D9;
}
.main-title {
    font-family: 'DM Serif Display', serif;
    font-size: 32px;
    color: #1A1A1A;
}
.main-title em { color: #E8622A; }
.main-subtitle {
    font-size: 13px;
    color: #9A8F85;
    font-weight: 400;
}

/* ── Chat messages ────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
}

/* User message bubble */
[data-testid="stChatMessage"][data-testid*="user"],
div[data-testid="stChatMessage"]:has(div[aria-label="user avatar"]) {
    background: transparent !important;
}

.user-bubble {
    background: linear-gradient(135deg, #1A1A1A, #2D2D2D);
    color: #FFFFFF;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    font-size: 14px;
    line-height: 1.6;
    max-width: 85%;
    margin-left: auto;
    box-shadow: 0 2px 12px rgba(0,0,0,0.12);
}

.agent-bubble {
    background: #FFFFFF;
    border: 1.5px solid #E8E2D9;
    border-radius: 4px 18px 18px 18px;
    padding: 16px 20px;
    font-size: 14px;
    line-height: 1.7;
    color: #2A2A2A;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* ── Tool call badges ─────────────────────────────────────── */
.tool-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.tool-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #F0F9F4;
    border: 1px solid #B8E0C8;
    border-radius: 20px;
    padding: 3px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #1E7A42;
    font-weight: 500;
}
.tool-badge::before { content: "⚡"; font-size: 10px; }

/* ── Chat input ───────────────────────────────────────────── */
[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border: 2px solid #E8E2D9 !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06) !important;
    transition: border-color 0.2s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #E8622A !important;
    box-shadow: 0 4px 20px rgba(232,98,42,0.12) !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    color: #1A1A1A !important;
    background: transparent !important;
}

/* ── Divider ──────────────────────────────────────────────── */
hr { border: none; border-top: 1.5px solid #E8E2D9; margin: 1rem 0; }

/* ── Metrics in trace panel ───────────────────────────────── */
[data-testid="stMetric"] {
    background: #FAFAF8;
    border: 1.5px solid #E8E2D9;
    border-radius: 10px;
    padding: 10px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'DM Serif Display', serif !important;
    font-size: 22px !important;
    color: #1A1A1A !important;
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    color: #9A8F85 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ── Expander ─────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #FAFAF8 !important;
    border: 1.5px solid #E8E2D9 !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    color: #4A4035 !important;
}

/* ── Dataframe ────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1.5px solid #E8E2D9 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* ── Sidebar section labels ───────────────────────────────── */
.section-label {
    font-size: 10px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #B5A99E;
    font-weight: 600;
    margin: 1.2rem 0 0.6rem;
    padding: 0 1.5rem;
}

/* ── Welcome state ────────────────────────────────────────── */
.welcome-card {
    background: #FFFFFF;
    border: 2px solid #E8E2D9;
    border-radius: 16px;
    padding: 2.5rem;
    text-align: center;
    margin: 2rem auto;
    max-width: 520px;
}
.welcome-icon { font-size: 48px; margin-bottom: 1rem; }
.welcome-title {
    font-family: 'DM Serif Display', serif;
    font-size: 24px;
    color: #1A1A1A;
    margin-bottom: 8px;
}
.welcome-desc { font-size: 14px; color: #9A8F85; line-height: 1.6; }
.welcome-features {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 1.5rem;
    text-align: left;
}
.feature-chip {
    background: #F7F4EF;
    border: 1.5px solid #E8E2D9;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 12px;
    color: #4A4035;
    font-weight: 500;
}
.feature-chip .feat-icon { font-size: 16px; margin-right: 6px; }

/* ── Plotly charts ────────────────────────────────────────── */
.js-plotly-plot {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1.5px solid #E8E2D9 !important;
}

/* ── Scrollbar ────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #F7F4EF; }
::-webkit-scrollbar-thumb { background: #D4C9BC; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #B5A99E; }

/* ── Caption text ─────────────────────────────────────────── */
.stCaption { color: #9A8F85 !important; font-size: 11px !important; }

/* ── Spinner ──────────────────────────────────────────────── */
.stSpinner > div { border-top-color: #E8622A !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"    not in st.session_state: st.session_state.messages    = []
if "history"     not in st.session_state: st.session_state.history     = []
if "data_loaded" not in st.session_state: st.session_state.data_loaded = False
if "data_info"   not in st.session_state: st.session_state.data_info   = {}
if "csv_path"    not in st.session_state: st.session_state.csv_path    = ""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown("""
    <div class="brand-block">
        <div class="brand-title">Data<span> Pilot</span></div>
        <div class="brand-sub">Data is new Oil</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Upload Data</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop your CSV here",
        type    = ["csv"],
        label_visibility = "collapsed",
    )

    if uploaded:
        save_dir  = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
        )
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, uploaded.name)

        with open(save_path, "wb") as f:
            f.write(uploaded.getbuffer())

        with st.spinner("Loading data…"):
            result = data_ingestion_tool("csv", save_path)

        if result["status"] == "success":
            st.session_state.data_loaded = True
            st.session_state.data_info   = result
            st.session_state.csv_path    = save_path

            greeting = (
                f"✦ **Data loaded successfully!**\n\n"
                f"Your dataset has **{result['rows']:,} rows** and **{len(result['columns'])} columns**.\n\n"
                f"**Columns detected:** {', '.join(f'`{c}`' for c in result['columns'])}\n\n"
                "Here's what I can do for you:\n"
                "- Run a full **EDA** — stats, nulls, correlations\n"
                "- Generate **charts** — histograms, heatmaps, scatter plots\n"
                "- Answer **SQL questions** — aggregations, filters\n"
                "- Train a **ML model** — classification or regression\n"
                "- Write an **executive report** — plain English insights\n\n"
                "What would you like to explore first?"
            )
            st.session_state.messages = [{"role": "assistant", "content": greeting, "charts": [], "tools": []}]
            st.session_state.history  = []
            st.rerun()
        else:
            st.error(f"Error: {result.get('message')}")

    if st.session_state.data_loaded:
        info = st.session_state.data_info
        st.markdown(f"""
        <div class="data-pill">
            <span class="icon">📊</span>
            <span>{info['rows']:,} rows · {len(info['columns'])} columns</span>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("View columns"):
            for col, dtype in info["dtypes"].items():
                st.markdown(f"`{col}` — *{dtype}*")

    st.markdown('<div class="section-label">Quick Prompts</div>', unsafe_allow_html=True)

    prompts = [
        "📊  Run a full EDA",
        "📈  Show histogram of Age",
        "🔥  Correlation heatmap",
        "🔍  Average fare by class",
        "🤖  Predict Survived column",
        "📝  Executive summary report",
    ]
    for p in prompts:
        if st.button(p, key=f"qp_{p}"):
            st.session_state["_quick_prompt"] = p.split("  ", 1)[1]
            st.rerun()

    st.markdown("---")
    if st.button("🗑  Clear conversation"):
        st.session_state.messages = []
        st.session_state.history  = []
        st.rerun()

# ── Main ──────────────────────────────────────────────────────────────────────
chat_col, trace_col = st.columns([3, 1], gap="large")

with chat_col:
    st.markdown("""
    <div class="main-header">
        <div class="main-title">Chat with your <em>Data</em></div>
    </div>
    """, unsafe_allow_html=True)

    # Welcome screen
    if not st.session_state.data_loaded:
        st.markdown("""
        <div class="welcome-card">
            <div class="welcome-icon">✦</div>
            <div class="welcome-title">Your autonomous data scientist</div>
            <div class="welcome-desc">Upload any CSV file and ask questions in plain English. The agent will analyse, visualise, model, and report — all automatically.</div>
            <div class="welcome-features">
                <div class="feature-chip"><span class="feat-icon">📊</span>Auto EDA</div>
                <div class="feature-chip"><span class="feat-icon">📈</span>Smart Charts</div>
                <div class="feature-chip"><span class="feat-icon">🔍</span>NL → SQL</div>
                <div class="feature-chip"><span class="feat-icon">🤖</span>ML Models</div>
                <div class="feature-chip"><span class="feat-icon">📝</span>AI Reports</div>
                <div class="feature-chip"><span class="feat-icon">⚡</span>Agentic AI</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="agent-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

            for chart_json in msg.get("charts", []):
                try:
                    fig = pio.from_json(chart_json)
                    fig.update_layout(
                        paper_bgcolor = "#FFFFFF",
                        plot_bgcolor  = "#FAFAF8",
                        font          = dict(family="DM Sans, sans-serif", color="#1A1A1A"),
                        title_font    = dict(family="DM Serif Display, serif", size=16, color="#1A1A1A"),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    pass

            if msg.get("tools"):
                badges = " ".join(f'<span class="tool-badge">{t["name"]}</span>' for t in msg["tools"])
                st.markdown(f'<div class="tool-row">{badges}</div>', unsafe_allow_html=True)

    # Input
    user_input = st.chat_input(
        "Ask anything about your data…" if st.session_state.data_loaded else "Upload a CSV file to get started",
        disabled = not st.session_state.data_loaded,
    )

    if "_quick_prompt" in st.session_state:
        user_input = st.session_state.pop("_quick_prompt")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input, "charts": [], "tools": []})

        with st.chat_message("user"):
            st.markdown(f'<div class="user-bubble">{user_input}</div>', unsafe_allow_html=True)

        csv_path  = st.session_state.csv_path
        data_info = st.session_state.data_info
        enriched  = (
            f"{user_input}\n\n"
            f"[CONTEXT: CSV already loaded at: {csv_path}. "
            f"Columns: {', '.join(data_info.get('columns', []))}. "
            f"Rows: {data_info.get('rows', 0)}. "
            f"If calling data_ingestion_tool use source_type='csv' source_path='{csv_path}']"
        )

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                response = run_agent(enriched, history=st.session_state.history)

            final_text      = response.get("text", "")
            charts_turn     = response.get("charts", [])
            tool_calls      = response.get("tool_calls", [])

            st.markdown(f'<div class="agent-bubble">{final_text}</div>', unsafe_allow_html=True)

            for chart_json in charts_turn:
                try:
                    fig = pio.from_json(chart_json)
                    fig.update_layout(
                        paper_bgcolor = "#FFFFFF",
                        plot_bgcolor  = "#FAFAF8",
                        font          = dict(family="DM Sans, sans-serif", color="#1A1A1A"),
                        title_font    = dict(family="DM Serif Display, serif", size=16, color="#1A1A1A"),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Chart error: {e}")

            if tool_calls:
                badges = " ".join(f'<span class="tool-badge">{t["name"]}</span>' for t in tool_calls)
                st.markdown(f'<div class="tool-row">{badges}</div>', unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant", "content": final_text,
            "charts": charts_turn, "tools": tool_calls,
        })
        st.session_state.history.append({"role": "user",  "parts": [user_input]})
        st.session_state.history.append({"role": "model", "parts": [final_text]})
        st.rerun()

# ── Trace panel ───────────────────────────────────────────────────────────────
with trace_col:
    st.markdown("""
    <div style="font-family:'DM Serif Display',serif;font-size:20px;color:#1A1A1A;margin-bottom:1rem;padding-bottom:0.75rem;border-bottom:2px solid #E8E2D9;">
        Agent Trace
    </div>
    """, unsafe_allow_html=True)

    last_tools = []
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant" and msg.get("tools"):
            last_tools = msg["tools"]
            break

    if not last_tools:
        st.caption("Tool calls will appear here after the agent runs.")
    else:
        for i, tool in enumerate(last_tools, 1):
            with st.expander(f"⚡ {tool['name']}", expanded=(i == 1)):
                st.json(tool.get("args", {}))

    st.markdown("---")

    st.markdown("""
    <div style="font-family:'DM Serif Display',serif;font-size:20px;color:#1A1A1A;margin-bottom:0.75rem;">
        Data Preview
    </div>
    """, unsafe_allow_html=True)

    df = get_active_dataframe()
    if df is not None:
        st.dataframe(df.head(8), use_container_width=True, height=220)
        c1, c2 = st.columns(2)
        c1.metric("Rows",    f"{len(df):,}")
        c2.metric("Cols",    len(df.columns))
        c1.metric("Nulls",   f"{round(df.isnull().mean().mean()*100,1)}%")
        c2.metric("Dupes",   int(df.duplicated().sum()))
    else:
        st.caption("Upload a CSV to see a preview here.")