"""
Travel Buddy — AI-Powered Multi-Agent Travel Planner
Streamlit web application entry point.
"""

import streamlit as st
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
    /* Global font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Header gradient */
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
        margin-bottom: 30px;
    }

    /* Card styling */
    .result-card {
        background: #1A1F2E;
        border-radius: 12px;
        padding: 24px;
        margin: 12px 0;
        border: 1px solid #2A3040;
    }
    .result-card h3 {
        color: #FF8E53;
        margin-top: 0;
    }

    /* Status badges */
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

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #141821;
    }

    /* Progress node labels */
    .node-label {
        font-weight: 600;
        font-size: 0.95rem;
    }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Divider */
    .gradient-divider {
        height: 3px;
        background: linear-gradient(90deg, #FF6B6B, #FF8E53, #FFC857);
        border: none;
        border-radius: 2px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-header">🌍 Travel Buddy</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">AI-Powered Multi-Agent Travel Planner • '
    'Powered by LangGraph & Gemini</p>',
    unsafe_allow_html=True,
)
st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)


# ── Sidebar: Inputs ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔐 API Keys")
    gemini_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIzaSy...",
        help="Get your key at https://aistudio.google.com/apikey",
    )
    tavily_key = st.text_input(
        "Tavily API Key",
        type="password",
        placeholder="tvly-...",
        help="Get your key at https://tavily.com",
    )

    st.markdown("---")
    st.markdown("## ✈️ Trip Details")

    destination = st.text_input(
        "Destination",
        value="Tokyo, Japan",
        placeholder="e.g., Paris, France",
    )
    budget = st.number_input(
        "Budget (USD)",
        min_value=100.0,
        max_value=100000.0,
        value=3000.0,
        step=100.0,
        format="%.2f",
    )
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
    "itinerary_agent": ("🗺️", "Itinerary Agent", "Planning sightseeing & activities..."),
    "food_retail_agent": ("🍽️", "Food & Retail Agent", "Curating dining & shopping..."),
    "hospitality_agent": ("🏨", "Hospitality Agent", "Sourcing accommodation..."),
    "budget_guardrail": ("💰", "Budget Guardrail", "Validating costs..."),
    "agent_as_judge": ("⚖️", "Agent-as-Judge", "Evaluating persona compliance..."),
    "final_output": ("✨", "Final Output", "Compiling approved plan..."),
    "budget_busted_fallback": ("🚨", "Budget Busted", "Budget could not be reconciled."),
}


# ── Main Execution ────────────────────────────────────────────────────────────
if plan_button:
    # Validate inputs
    if not gemini_key or not tavily_key:
        st.error("⚠️ Please provide both API keys in the sidebar.")
        st.stop()
    if not destination.strip():
        st.error("⚠️ Please enter a destination.")
        st.stop()
    if not dates.strip():
        st.error("⚠️ Please enter your travel dates.")
        st.stop()

    # Set API keys as environment variables
    import os
    os.environ["GOOGLE_API_KEY"] = gemini_key
    os.environ["TAVILY_API_KEY"] = tavily_key

    # Lazy imports (only when running)
    with st.spinner("Initializing AI agents..."):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_community.tools.tavily_search import TavilySearchResults
            from core.graph import build_graph
            from core.personas import PERSONA_PROFILES
            from core.utils import build_recommendations_text, sanitize_filename

            llm = ChatGoogleGenerativeAI(
                model="gemini-3.1-flash-lite",
                temperature=0.7,
                max_output_tokens=8192,
            )
            search_tool = TavilySearchResults(max_results=3)
            app = build_graph(llm, search_tool)
        except Exception as e:
            st.error(f"❌ Failed to initialize: {e}")
            st.stop()

    st.success("✅ Agents initialized. Starting planning...")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # ── Initialize state ──────────────────────────────────────────────────
    initial_state = {
        "destination": destination,
        "budget": budget,
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

    # ── Stream execution ──────────────────────────────────────────────────
    progress_container = st.container()
    result_container = st.container()

    with progress_container:
        st.markdown("### 🔄 Agent Pipeline Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()

        completed_nodes = []
        node_count = 0
        total_expected = 5  # Minimum nodes in a successful run

        try:
            for step_output in app.stream(initial_state):
                for node_name, node_output in step_output.items():
                    node_count += 1
                    icon, label, desc = NODE_LABELS.get(
                        node_name, ("⚙️", node_name, "Processing...")
                    )

                    # Update progress
                    progress = min(node_count / total_expected, 1.0)
                    progress_bar.progress(progress)
                    status_text.markdown(
                        f"**{icon} {label}** — {desc}"
                    )
                    completed_nodes.append((node_name, node_output))

                    # Show budget attempt info inline
                    if node_name == "budget_guardrail" and isinstance(node_output, dict):
                        attempt = node_output.get("budget_attempts", 0)
                        status = node_output.get("status", "")
                        if status == "budget_passed":
                            st.success(f"✅ Budget check passed on attempt {attempt}/3")
                        elif status == "budget_busted":
                            st.error(f"🚨 Budget busted after {attempt} attempts")
                        else:
                            st.warning(
                                f"🔄 Budget attempt {attempt}/3 failed — retrying..."
                            )
                            total_expected += 4  # Account for retry loop

            progress_bar.progress(1.0)
            status_text.markdown("**✅ Pipeline complete!**")

        except Exception as e:
            st.error(f"❌ Pipeline error: {e}")
            st.exception(e)
            st.stop()

    # ── Get final state via invoke ────────────────────────────────────────
    try:
        result = app.invoke(initial_state)
    except Exception:
        # Fallback: reconstruct from streamed outputs
        result = dict(initial_state)
        for _, output in completed_nodes:
            if isinstance(output, dict):
                result.update(output)

    status = result.get("status", "unknown")

    # ── Display Results ───────────────────────────────────────────────────
    with result_container:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # Status badge
        if status == "approved":
            st.markdown(
                '<span class="badge-approved">✅ TRIP PLAN APPROVED</span>',
                unsafe_allow_html=True,
            )

            # Result tabs
            tab_itin, tab_food, tab_hotel, tab_budget, tab_judge = st.tabs([
                "🗺️ Itinerary",
                "🍽️ Food & Retail",
                "🏨 Accommodation",
                "💰 Budget",
                "⚖️ Quality Verdict",
            ])

            with tab_itin:
                st.markdown(result.get("itinerary", "N/A"))

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

        # ── Download Button ───────────────────────────────────────────────
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📥 Download Recommendations")

        persona_label = PERSONA_PROFILES.get(
            persona, PERSONA_PROFILES["couple"]
        )["label"]

        file_content = build_recommendations_text(
            result, destination, budget, dates, persona_label
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_dest = sanitize_filename(destination).replace(" ", "_").lower()
        filename = f"travel_buddy_{safe_dest}_{timestamp}.txt"

        st.download_button(
            label=f"💾 Download {filename}",
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
            <p>Three specialized AI agents collaborate to plan your perfect trip:
            Itinerary, Food & Retail, and Hospitality.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="result-card">
            <h3>⚖️ Dual Evaluation</h3>
            <p>Deterministic budget guardrail + cognitive Agent-as-Judge
            ensure quality and cost compliance.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="result-card">
            <h3>🎭 Persona-Aware</h3>
            <p>Plans adapt to your travel style — Solo Traveler,
            Couple's Getaway, or Family Adventure.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Architecture diagram
    st.markdown("### 🏗️ System Architecture")
    st.markdown("""
    ```mermaid
    graph LR
        A[START] --> B[🗺️ Itinerary Agent]
        B --> C[🍽️ Food & Retail Agent]
        C --> D[🏨 Hospitality Agent]
        D --> E{💰 Budget Guardrail}
        E -->|Pass| F[⚖️ Agent-as-Judge]
        E -->|Retry ≤3| B
        E -->|Busted| G[🚨 Budget Busted]
        F --> H[✨ Final Output]
        H --> I[END]
        G --> I
    ```
    """)

    st.info(
        "👈 **Enter your API keys and trip details in the sidebar, "
        "then click 'Plan My Trip' to start!**"
    )
