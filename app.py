"""
Travel Buddy — AI-Powered Multi-Agent Travel Planner
Streamlit web application entry point.
"""

import os
import urllib.parse
import streamlit as st
import pandas as pd
from datetime import datetime

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Travel Buddy — AI Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 50%, #FFC857 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        text-align: center;
        color: #8892A0;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 25px;
    }

    .result-card {
        background: #1A1F2E;
        border-radius: 12px;
        padding: 24px;
        margin: 12px 0;
        border: 1px solid #2A3040;
    }
    .result-card h3 { color: #FF8E53; margin-top: 0; }

    .badge-approved {
        background: linear-gradient(135deg, #00C853, #69F0AE);
        color: #0E1117;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-busted {
        background: linear-gradient(135deg, #FF5252, #FF8A80);
        color: #0E1117;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    section[data-testid="stSidebar"] { background: #141821; }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    .gradient-divider {
        height: 3px;
        background: linear-gradient(90deg, #FF6B6B, #FF8E53, #FFC857);
        border: none;
        border-radius: 2px;
        margin: 20px 0;
    }

    .map-frame {
        border-radius: 12px;
        border: 1px solid #2A3040;
        overflow: hidden;
        width: 100%;
        height: 450px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-header">🌍 Travel Buddy</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">AI-Powered Multi-Agent Travel Planner • '
    'Default SGD (S$) • Google Maps Grounding</p>',
    unsafe_allow_html=True,
)
st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)


# ── Read Secrets / Sidebar Inputs ────────────────────────────────────────────
def get_secret(key_name, default=""):
    """Check Streamlit secrets first, then environment variables."""
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return os.environ.get(key_name, default)


secret_gemini = get_secret("GOOGLE_API_KEY") or get_secret("GEMINI_API_KEY")
secret_tavily = get_secret("TAVILY_API_KEY")
secret_gmaps = get_secret("GOOGLE_MAPS_API_KEY") or get_secret("GMAPS_API_KEY")

with st.sidebar:
    st.markdown("## 🔐 API Credentials")

    if secret_gemini and secret_tavily:
        st.success("🔑 API keys loaded from Streamlit Secrets!")
        gemini_key = secret_gemini
        tavily_key = secret_tavily
        gmaps_key = secret_gmaps
    else:
        st.info("💡 Enter your API keys below (or set in `.streamlit/secrets.toml`).")
        gemini_key = st.text_input(
            "Gemini API Key",
            value=secret_gemini,
            type="password",
            placeholder="AIzaSy...",
        )
        tavily_key = st.text_input(
            "Tavily API Key",
            value=secret_tavily,
            type="password",
            placeholder="tvly-...",
        )
        gmaps_key = st.text_input(
            "Google Maps API Key (Optional)",
            value=secret_gmaps,
            type="password",
            placeholder="AIzaSy... (for Maps Embed API)",
        )

    st.markdown("---")
    st.markdown("## ✈️ Trip Details")

    destination = st.text_input(
        "Destination",
        value="Tokyo, Japan",
        placeholder="e.g., Tokyo, Japan or Paris, France",
    )

    no_budget = st.checkbox("Infinite / Flexible Budget (No Limit)", value=False)

    if not no_budget:
        budget = st.number_input(
            "Budget in Singapore Dollars (SGD / S$)",
            min_value=100.0,
            max_value=500000.0,
            value=3000.0,
            step=100.0,
            format="%.2f",
        )
    else:
        budget = 0.0
        st.caption("ℹ️ Budget guardrail will be bypassed. Agents will focus on best experiences.")

    dates = st.text_input(
        "Travel Dates",
        value="March 10-15, 2025",
        placeholder="e.g., March 10-15, 2025",
    )

    persona_options = {
        "🧑 Solo Traveler": "single",
        "💑 Couple's Getaway": "couple",
        "👨‍👩‍👧‍👦 Family Adventure": "family",
    }
    persona_display = st.radio(
        "Traveler Persona",
        options=list(persona_options.keys()),
        index=1,
    )
    persona = persona_options[persona_display]

    st.markdown("---")
    plan_button = st.button(
        "🚀 Plan My Trip",
        use_container_width=True,
        type="primary",
    )


# ── Node display labels ──────────────────────────────────────────────────────
NODE_LABELS = {
    "itinerary_agent": ("🗺️", "Itinerary Agent", "Planning sightseeing & activities in SGD..."),
    "food_retail_agent": ("🍽️", "Food & Retail Agent", "Curating dining & shopping in SGD..."),
    "hospitality_agent": ("🏨", "Hospitality Agent", "Sourcing accommodation in SGD..."),
    "budget_guardrail": ("💰", "Budget Guardrail", "Validating SGD costs & safety buffer..."),
    "agent_as_judge": ("⚖️", "Agent-as-Judge", "Evaluating persona compliance..."),
    "final_output": ("✨", "Final Output", "Compiling approved plan..."),
    "budget_busted_fallback": ("🚨", "Budget Busted", "Budget could not be reconciled."),
}


# ── Main Execution ────────────────────────────────────────────────────────────
if plan_button:
    if not gemini_key or not tavily_key:
        st.error("⚠️ Please provide Gemini and Tavily API keys in sidebar or Streamlit secrets.")
        st.stop()
    if not destination.strip():
        st.error("⚠️ Please enter a destination.")
        st.stop()

    os.environ["GOOGLE_API_KEY"] = gemini_key
    os.environ["TAVILY_API_KEY"] = tavily_key
    if gmaps_key:
        os.environ["GOOGLE_MAPS_API_KEY"] = gmaps_key

    with st.spinner("Initializing AI agents & LangGraph pipeline..."):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_community.tools.tavily_search import TavilySearchResults
            from core.graph import build_graph
            from core.personas import PERSONA_PROFILES
            from core.utils import (
                build_recommendations_text,
                sanitize_filename,
                parse_itinerary_to_dataframe,
            )

            llm = ChatGoogleGenerativeAI(
                model="gemini-3.1-flash-lite",
                temperature=0.7,
                max_output_tokens=8192,
            )
            search_tool = TavilySearchResults(max_results=3)
            app = build_graph(llm, search_tool)
        except Exception as e:
            st.error(f"❌ Failed to initialize graph: {e}")
            st.stop()

    st.success("✅ Agents initialized. Starting execution...")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    initial_state = {
        "destination": destination,
        "budget": budget,
        "no_budget": no_budget,
        "currency": "SGD",
        "dates": dates,
        "persona": persona,
        "itinerary": "",
        "food_and_retail": "",
        "hotel_recommendations": "",
        "budget_breakdown": "",
        "budget_attempts": 0,
        "critique_history": [],
        "status": "planning",
        "judge_verdict": "",
    }

    progress_container = st.container()
    result_container = st.container()

    with progress_container:
        st.markdown("### 🔄 Agent Pipeline Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()

        completed_nodes = []
        node_count = 0
        total_expected = 5

        try:
            for step_output in app.stream(initial_state):
                for node_name, node_output in step_output.items():
                    node_count += 1
                    icon, label, desc = NODE_LABELS.get(
                        node_name, ("⚙️", node_name, "Processing...")
                    )
                    progress = min(node_count / total_expected, 1.0)
                    progress_bar.progress(progress)
                    status_text.markdown(f"**{icon} {label}** — {desc}")
                    completed_nodes.append((node_name, node_output))

                    if node_name == "budget_guardrail" and isinstance(node_output, dict):
                        attempt = node_output.get("budget_attempts", 0)
                        status_val = node_output.get("status", "")
                        if status_val == "budget_passed":
                            st.success(f"✅ Budget validation passed on attempt {attempt}/3!")
                        elif status_val == "budget_busted":
                            st.error(f"🚨 Budget busted after {attempt} attempts")
                        else:
                            st.warning(f"🔄 Budget attempt {attempt}/3 failed — retrying...")
                            total_expected += 4

            progress_bar.progress(1.0)
            status_text.markdown("**✅ Pipeline complete!**")
        except Exception as e:
            st.error(f"❌ Execution error: {e}")
            st.exception(e)
            st.stop()

    try:
        result = app.invoke(initial_state)
    except Exception:
        result = dict(initial_state)
        for _, output in completed_nodes:
            if isinstance(output, dict):
                result.update(output)

    status = result.get("status", "unknown")

    # ── Display Results ───────────────────────────────────────────────────
    with result_container:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        if status == "approved":
            st.markdown(
                '<span class="badge-approved">✅ TRIP PLAN APPROVED</span>',
                unsafe_allow_html=True,
            )

            # Tabs
            tab_itin, tab_map, tab_table, tab_food, tab_hotel, tab_budget, tab_judge = st.tabs([
                "🗺️ Itinerary",
                "📍 Location Map",
                "📊 Tabular Itinerary",
                "🍽️ Food & Retail",
                "🏨 Accommodation",
                "💰 Budget Breakdown",
                "⚖️ Quality Verdict",
            ])

            with tab_itin:
                st.markdown(result.get("itinerary", "N/A"))

            with tab_map:
                st.markdown(f"### 📍 Google Maps Location Visualizer — {destination}")
                encoded_dest = urllib.parse.quote(destination)

                if gmaps_key:
                    map_url = f"https://www.google.com/maps/embed/v1/search?key={gmaps_key}&q={encoded_dest}+attractions"
                else:
                    map_url = f"https://www.google.com/maps?q={encoded_dest}&output=embed"

                st.components.v1.iframe(map_url, height=500, scrolling=True)

                st.markdown("#### 🔗 Quick Directions & Google Maps Links")
                gmaps_direct_url = f"https://www.google.com/maps/search/?api=1&query={encoded_dest}"
                st.markdown(f"[👉 Open {destination} on Google Maps]({gmaps_direct_url})")

            with tab_table:
                st.markdown("### 📊 Day-by-Day Tabular Itinerary")
                itinerary_text = result.get("itinerary", "")
                df_itin = parse_itinerary_to_dataframe(itinerary_text)
                st.dataframe(df_itin, use_container_width=True)

                # CSV Download Button
                csv_data = df_itin.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download Itinerary as CSV",
                    data=csv_data,
                    file_name=f"travel_itinerary_{sanitize_filename(destination).lower()}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with tab_food:
                st.markdown(result.get("food_and_retail", "N/A"))

            with tab_hotel:
                st.markdown(result.get("hotel_recommendations", "N/A"))

            with tab_budget:
                st.code(result.get("budget_breakdown", "N/A"), language=None)

            with tab_judge:
                st.markdown(result.get("judge_verdict", "N/A"))

        elif status == "budget_busted":
            st.markdown(
                '<span class="badge-busted">🚨 BUDGET COULD NOT BE RECONCILED</span>',
                unsafe_allow_html=True,
            )
            st.markdown("---")
            st.code(result.get("budget_breakdown", "N/A"), language=None)

            if result.get("itinerary"):
                with st.expander("📋 Last Attempted Itinerary (not approved)"):
                    st.markdown(result.get("itinerary", ""))
        else:
            st.warning(f"⚠️ Unexpected status: {status}")

        # ── Full Text File Download ──────────────────────────────────────────
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📥 Download Complete Recommendations Report")

        persona_label = PERSONA_PROFILES.get(persona, PERSONA_PROFILES["couple"])["label"]
        file_content = build_recommendations_text(
            result, destination, budget, dates, persona_label, no_budget=no_budget, currency="SGD"
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_dest = sanitize_filename(destination).replace(" ", "_").lower()
        filename = f"travel_buddy_{safe_dest}_{timestamp}.txt"

        st.download_button(
            label=f"💾 Download Full Text Report ({filename})",
            data=file_content,
            file_name=filename,
            mime="text/plain",
            use_container_width=True,
        )

else:
    # ── Landing state ─────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="result-card">
            <h3>🤖 Multi-Agent System</h3>
            <p>Three specialized AI agents collaborate: Sightseeing, Food & Retail, and Hospitality.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="result-card">
            <h3>💰 Default SGD & Flexible Budget</h3>
            <p>Calculates costs in Singapore Dollars (SGD / S$) with optional unlimited budget mode.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="result-card">
            <h3>📍 Google Maps & Tabular Export</h3>
            <p>Visualizes locations on Google Maps and exports itineraries directly to CSV & Text.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏗️ System Architecture")
    st.markdown("""
    ```mermaid
    graph LR
        A[START] --> B[🗺️ Itinerary Agent (SGD)]
        B --> C[🍽️ Food & Retail Agent (SGD)]
        C --> D[🏨 Hospitality Agent (SGD)]
        D --> E{💰 Budget Guardrail}
        E -->|Pass / No Budget| F[⚖️ Agent-as-Judge]
        E -->|Retry ≤3| B
        E -->|Busted| G[🚨 Budget Busted]
        F --> H[✨ Final Output & Map/CSV Export]
        H --> I[END]
        G --> I
    ```
    """)
    st.info("👈 **Configure trip details in the sidebar and click 'Plan My Trip' to start!**")
