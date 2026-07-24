"""
Travel Buddy — AI-Powered Multi-Agent Travel Planner
Modularized Streamlit application router and execution engine.
"""

import os
import sys

# Ensure root workspace directory is in sys.path for Streamlit Cloud execution
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st

from core.logger import get_logger, get_session_logs, clear_session_logs
from core.db import init_db
from core.profile import load_user_profile
from ui.styles import inject_custom_css
from ui.sidebar import render_sidebar
from ui.landing import render_landing_view
from ui.plan_view import render_plan_results

logger = get_logger("app")

# ── Page Configuration & CSS Styling ─────────────────────────────────────────
st.set_page_config(
    page_title="Travel Buddy — AI Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_custom_css()

# ── Helper for Streamlit Secrets ──────────────────────────────────────────────
def get_secret(key_name: str, default: str = "") -> str:
    """Safely retrieve key from st.secrets or os.environ."""
    if hasattr(st, "secrets") and key_name in st.secrets:
        return str(st.secrets[key_name])
    return os.environ.get(key_name, default)


# ── Header Section ────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🌍 Travel Buddy — Multi-Agent Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Collaborative AI Travel Planning • Custom Persona • Guided Chatbot • Live Maps</div>', unsafe_allow_html=True)

secret_gemini = get_secret("GEMINI_API_KEY") or get_secret("GOOGLE_API_KEY")
secret_tavily = get_secret("TAVILY_API_KEY")
secret_gmaps = get_secret("GOOGLE_MAPS_API_KEY") or get_secret("GMAPS_API_KEY")

# Initialize DB & User Profile
init_db(get_secret("SUPABASE_URL"), get_secret("SUPABASE_KEY"))

if "user_profile" not in st.session_state:
    st.session_state.user_profile = load_user_profile()

# Render Sidebar UI & Retrieve Inputs
inputs = render_sidebar(secret_gemini, secret_tavily, secret_gmaps)

# Node Display Labels for Execution Progress
NODE_LABELS = {
    "itinerary_agent": ("🗺️", "Itinerary Agent", "Planning day-by-day sightseeing & activities..."),
    "food_retail_agent": ("🍽️", "Food & Retail Agent", "Curating dining & shopping..."),
    "hospitality_agent": ("🏨", "Hospitality Agent", "Sourcing accommodation..."),
    "purchasing_agent": ("🛒", "Purchasing & Booking Agent", "Sourcing flights, hotels, car rental & booking links..."),
    "budget_guardrail": ("💰", "Budget Guardrail", "Evaluating total budget constraints..."),
    "agent_as_judge": ("⚖️", "Agent-as-Judge", "Evaluating persona compliance..."),
    "final_output": ("✨", "Final Output", "Compiling approved plan..."),
    "terminal_fallback": ("🚨", "Planning Failed", "Budget or quality constraints could not be met."),
}

# ── Main Execution Flow ───────────────────────────────────────────────────────
if inputs["plan_button"]:
    clear_session_logs()
    logger.info(f"Session started for destination='{inputs['destination']}', persona='{inputs['persona']}'")

    if not inputs["gemini_key"] or not inputs["tavily_key"]:
        st.error("⚠️ Please provide Gemini and Tavily API keys in sidebar or Streamlit secrets.")
        st.stop()
    if not inputs["destination"].strip():
        st.error("⚠️ Please enter a destination.")
        st.stop()

    os.environ["GOOGLE_API_KEY"] = inputs["gemini_key"]
    os.environ["TAVILY_API_KEY"] = inputs["tavily_key"]
    if inputs["gmaps_key"]:
        os.environ["GOOGLE_MAPS_API_KEY"] = inputs["gmaps_key"]

    with st.spinner("Initializing AI agents & LangGraph pipeline..."):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            try:
                from langchain_tavily import TavilySearch as TavilySearchResults
            except ImportError:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    from langchain_community.tools.tavily_search import TavilySearchResults
            from core.graph import build_graph

            llm = ChatGoogleGenerativeAI(
                model="gemini-3.1-flash-lite",
                temperature=0.7,
                max_output_tokens=8192,
            )
            search_tool = TavilySearchResults(max_results=3)
            app = build_graph(llm, search_tool)
        except Exception as e:
            logger.exception(f"Failed to initialize graph: {e}")
            st.error(f"❌ Failed to initialize graph: {e}")
            st.stop()

    st.success(f"✅ 4 Agents initialized for {inputs['travelers_summary']}. Starting planning for {inputs['dates']}...")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    if "force_no_budget" in st.session_state:
        inputs["no_budget"] = st.session_state.pop("force_no_budget")
    if "force_persona" in st.session_state:
        inputs["persona"] = st.session_state.pop("force_persona")
    if "force_dates" in st.session_state:
        inputs["dates"] = st.session_state.pop("force_dates")

    initial_state = {
        "origin": inputs["origin"],
        "destination": inputs["destination"],
        "budget": inputs["budget"],
        "num_adults": inputs["num_adults"],
        "num_children": inputs["num_children"],
        "num_infants": inputs["num_infants"],
        "travelers_summary": inputs["travelers_summary"],
        "self_drive": inputs["self_drive"],
        "no_budget": inputs["no_budget"],
        "currency": "SGD",
        "dates": inputs["dates"],
        "num_days": inputs["num_days"],
        "persona": inputs["persona"],
        "custom_persona_profile": inputs["custom_profile"],
        "user_preferences": st.session_state.user_profile.get("preferences", {}),
        "status": "start",
        "budget_attempts": 0,
        "critique_history": [],
    }

    result_container = st.container()
    progress_bar = st.progress(0.0)
    status_text = st.empty()

    node_count = 0
    total_expected_nodes = 7
    completed_nodes = []

    try:
        for event in app.stream(initial_state):
            for node_name, node_output in event.items():
                node_count += 1
                progress = min(1.0, node_count / total_expected_nodes)
                progress_bar.progress(progress)

                icon, label, desc = NODE_LABELS.get(node_name, ("⚙️", node_name, "Processing..."))
                status_text.markdown(f"**{icon} {label}** — _{desc}_")
                completed_nodes.append((node_name, node_output))

        progress_bar.progress(1.0)
        status_text.markdown("**✅ Pipeline complete!**")
    except Exception as e:
        logger.exception(f"Pipeline execution error: {e}")
        st.error(f"❌ Execution error: {e}")
        logs_content = get_session_logs()
        with st.expander("🚨 View Diagnostic Execution Logs & Stack Trace", expanded=True):
            st.markdown(f'<div class="log-box">{logs_content}</div>', unsafe_allow_html=True)
            st.download_button(
                label="📥 Download Diagnostic Debug Log (.log)",
                data=logs_content.encode("utf-8"),
                file_name="pipeline_failure_debug.log",
                mime="text/plain",
                use_container_width=True,
            )
        st.stop()

    result = dict(initial_state)
    for _, output in completed_nodes:
        if isinstance(output, dict):
            result.update(output)

    result["session_logs"] = get_session_logs()
    st.session_state.current_result = result

    with result_container:
        render_plan_results(result, inputs, search_tool=search_tool, llm=llm)

elif "current_result" in st.session_state and st.session_state.current_result:
    result = st.session_state.current_result
    render_plan_results(result, inputs)

else:
    render_landing_view(inputs["gemini_key"])
