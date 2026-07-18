"""
Travel Buddy — AI-Powered Multi-Agent Travel Planner
Streamlit web application entry point in clean light mode with complete itinerary location mapping, group composition, self-drive options, interactive currency conversion, and booking links.
"""

import os
import urllib.parse
import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime

from core.logger import get_logger, get_session_logs, clear_session_logs
from core.db import init_db, is_db_ready, save_trip_plan, get_saved_trips, get_trip_plan

logger = get_logger("app")

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Travel Buddy — AI Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom Light Mode CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #FFFFFF;
        color: #0F172A;
    }

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
        color: #475569;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 25px;
    }

    .result-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 24px;
        margin: 12px 0;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    .result-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .result-card h3 { color: #FF6B6B; margin-top: 0; }

    .badge-approved {
        background: linear-gradient(135deg, #10B981, #34D399);
        color: #FFFFFF;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
    }
    .badge-busted {
        background: linear-gradient(135deg, #EF4444, #F87171);
        color: #FFFFFF;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    section[data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    .gradient-divider {
        height: 3px;
        background: linear-gradient(90deg, #FF6B6B, #FF8E53, #FFC857);
        border: none;
        border-radius: 2px;
        margin: 20px 0;
    }

    .log-box {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        background-color: #0F172A;
        color: #4ADE80;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #334155;
        max-height: 400px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-header">🌍 Travel Buddy</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">AI-Powered Multi-Agent Travel Planner • '
    'Group Composition Controls • Full Itinerary Location Mapping • Light Mode UI</p>',
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


# Initialize DB
init_db(get_secret("SUPABASE_URL"), get_secret("SUPABASE_KEY"))

with st.sidebar:
    gemini_key = secret_gemini
    tavily_key = secret_tavily
    gmaps_key = secret_gmaps

    st.markdown("## 👥 Travelers & Group Composition")
    col_a, col_c, col_i = st.columns(3)
    with col_a:
        num_adults = st.number_input("Adults", min_value=1, max_value=20, value=2, step=1)
    with col_c:
        num_children = st.number_input("Children (>2y)", min_value=0, max_value=20, value=1, step=1)
    with col_i:
        num_infants = st.number_input("Infants (<2y)", min_value=0, max_value=10, value=0, step=1)

    travelers_parts = [f"{num_adults} Adult{'s' if num_adults>1 else ''}"]
    if num_children > 0:
        travelers_parts.append(f"{num_children} Child{'ren' if num_children>1 else ''} (>2 yrs)")
    if num_infants > 0:
        travelers_parts.append(f"{num_infants} Infant{'s' if num_infants>1 else ''} (<2 yrs)")
    travelers_summary = ", ".join(travelers_parts)

    st.caption(f"👥 Total Group: **{travelers_summary}**")

    st.markdown("---")
    st.markdown("## ✈️ Trip & Transport Details")

    origin = st.text_input(
        "Source City (Origin)",
        value="Singapore",
        placeholder="e.g., Singapore or London",
    )

    destination = st.text_input(
        "Destination City/Country",
        value="Tokyo, Japan",
        placeholder="e.g., Tokyo, Japan or Paris, France",
    )

    self_drive = st.checkbox("Self-Drive Option (Include Car Rental & Tolls)", value=False)

    # Infinite budget as default
    no_budget = st.checkbox("Infinite / Flexible Budget (No Limit)", value=True)

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
        st.caption("ℹ️ Unlimited budget mode active. Agents will focus on best experiences.")

    # Default 5 days: March 10-14, 2025
    dates = st.text_input(
        "Travel Dates (5 Days)",
        value="March 10-14, 2025",
        placeholder="e.g., March 10-14, 2025",
    )

    st.markdown("### 🎭 Traveler Persona")
    persona_options = {
        "🧑 Solo Traveler": "single",
        "💼 Business Traveler": "business",
        "💑 Couple's Getaway": "couple",
        "👨‍👩‍👧‍👦 Family Adventure": "family",
        "🎒 Budget Backpacker": "backpacker",
        "🎨 Custom Persona...": "custom",
    }
    persona_display = st.radio(
        "Select Persona",
        options=list(persona_options.keys()),
        index=3,  # Default Family for 2 adults 1 child
    )
    persona = persona_options[persona_display]

    custom_profile = None
    if persona == "custom":
        with st.expander("🛠️ Define Custom Persona Rules", expanded=True):
            custom_title = st.text_input("Persona Name", value="🧘 Wellness & Slow Travel Retreat")
            custom_tempo = st.selectbox("Pacing Tempo", options=["low", "medium", "high"], index=0)
            custom_mobility = st.text_input("Mobility Preference", value="relaxed walking, private shuttles")
            custom_dining = st.text_input("Dining Style", value="organic farm-to-table, plant-based cafes, tea houses")
            custom_lodging = st.text_input("Accommodation Preference", value="wellness resorts, quiet ryokans, boutique retreats")
            custom_rules = st.text_area(
                "Mandatory Persona Rules (1 per line)",
                value=(
                    "1. Morning yoga or mindfulness before 9:00 AM.\n"
                    "2. Maximum 2 gentle activities per day.\n"
                    "3. Prioritize natural hot springs, gardens, and quiet temples.\n"
                    "4. Include healthy, organic dining options."
                ),
                height=120,
            )
            custom_profile = {
                "label": f"🎨 {custom_title}",
                "tempo": custom_tempo,
                "mobility": custom_mobility,
                "dining_style": custom_dining,
                "accommodation": custom_lodging,
                "rules": custom_rules,
            }

    st.markdown("---")
    plan_button = st.button(
        "🚀 Plan My Trip",
        use_container_width=True,
        type="primary",
    )


# ── Node display labels ──────────────────────────────────────────────────────
NODE_LABELS = {
    "itinerary_agent": ("🗺️", "Itinerary Agent", "Planning 5-day sightseeing & activities..."),
    "food_retail_agent": ("🍽️", "Food & Retail Agent", "Curating dining & shopping..."),
    "hospitality_agent": ("🏨", "Hospitality Agent", "Sourcing accommodation..."),
    "purchasing_agent": ("🛒", "Purchasing & Booking Agent", "Sourcing flights, hotels, car rental & booking links..."),
    "budget_guardrail": ("💰", "Budget Guardrail", "Evaluating total budget constraints..."),
    "agent_as_judge": ("⚖️", "Agent-as-Judge", "Evaluating persona compliance..."),
    "final_output": ("✨", "Final Output", "Compiling approved plan..."),
    "budget_busted_fallback": ("🚨", "Budget Busted", "Budget could not be reconciled."),
}


# ── Main Execution ────────────────────────────────────────────────────────────
if plan_button:
    clear_session_logs()
    logger.info(f"Session started for origin='{origin}', destination='{destination}', travelers='{travelers_summary}', persona='{persona}', self_drive={self_drive}, no_budget={no_budget}")

    if not gemini_key or not tavily_key:
        logger.error("Missing Gemini or Tavily API key.")
        st.error("⚠️ Please provide Gemini and Tavily API keys in sidebar or Streamlit secrets.")
        st.stop()
    if not destination.strip():
        logger.error("Empty destination provided.")
        st.error("⚠️ Please enter a destination.")
        st.stop()

    os.environ["GOOGLE_API_KEY"] = gemini_key
    os.environ["TAVILY_API_KEY"] = tavily_key
    if gmaps_key:
        os.environ["GOOGLE_MAPS_API_KEY"] = gmaps_key
        logger.info("Google Maps API Key configured.")

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
                geocode_location,
                extract_all_itinerary_locations,
            )

            llm = ChatGoogleGenerativeAI(
                model="gemini-3.1-flash-lite",
                temperature=0.7,
                max_output_tokens=8192,
            )
            search_tool = TavilySearchResults(max_results=3)
            app = build_graph(llm, search_tool)
            logger.info("LangGraph application constructed successfully.")
        except Exception as e:
            logger.exception(f"Failed to initialize graph: {e}")
            st.error(f"❌ Failed to initialize graph: {e}")
            st.stop()

    st.success(f"✅ 4 Agents initialized for {travelers_summary}. Starting 5-day planning & purchasing execution...")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    initial_state = {
        "origin": origin,
        "destination": destination,
        "budget": budget,
        "num_adults": num_adults,
        "num_children": num_children,
        "num_infants": num_infants,
        "travelers_summary": travelers_summary,
        "self_drive": self_drive,
        "no_budget": no_budget,
        "currency": "SGD",
        "dates": dates,
        "persona": persona,
        "custom_persona_profile": custom_profile,
        "itinerary": "",
        "food_and_retail": "",
        "hotel_recommendations": "",
        "purchasing_guide": "",
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
        total_expected = 6

        try:
            for step_output in app.stream(initial_state):
                for node_name, node_output in step_output.items():
                    node_count += 1
                    logger.info(f"Graph step completed node='{node_name}'")
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
                            st.success(f"✅ Budget validation passed!")
                        elif status_val == "budget_busted":
                            st.error(f"🚨 Budget busted after {attempt} attempts")
                        else:
                            st.warning(f"🔄 Budget attempt {attempt}/3 failed — retrying...")
                            total_expected += 5

            progress_bar.progress(1.0)
            status_text.markdown("**✅ Pipeline complete!**")
        except Exception as e:
            logger.exception(f"Pipeline execution error: {e}")
            st.error(f"❌ Execution error: {e}")
            st.exception(e)
            st.stop()

    result = dict(initial_state)
    for _, output in completed_nodes:
        if isinstance(output, dict):
            result.update(output)

    status = result.get("status", "unknown")
    st.session_state.current_result = result

    # ── Display Results ───────────────────────────────────────────────────
    with result_container:
        if is_db_ready() and status == "approved":
            if st.button("💾 Save Trip to Supabase"):
                p_label = PERSONA_PROFILES.get(persona, PERSONA_PROFILES["couple"])["label"] if persona != "custom" else "Custom Persona"
                if save_trip_plan(destination, travelers_summary, p_label, dates, result):
                    st.success("Trip saved successfully!")
                else:
                    st.error("Failed to save trip.")

        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        if status == "approved":
            st.markdown(
                f'<span class="badge-approved">✅ TRIP PLAN APPROVED for {travelers_summary}</span>',
                unsafe_allow_html=True,
            )

            tab_itin_map, tab_hotel_food, tab_logistics, tab_chat, tab_advanced = st.tabs([
                "🗺️ Trip Plan & Map",
                "🏨 Hotels & Dining",
                "🛒 Flights & Budget",
                "💬 Travel Assistant",
                "⚙️ Under the Hood",
            ])

            with tab_itin_map:
                st.markdown(result.get("itinerary", "N/A"))
                
                st.markdown("---")
                st.markdown(f"### 📍 Complete Itinerary Map — {destination}")

                itinerary_text = result.get("itinerary", "")
                loc_list = extract_all_itinerary_locations(itinerary_text, destination)
                df_map = pd.DataFrame(loc_list)

                if not df_map.empty:
                    mean_lat = df_map["lat"].mean()
                    mean_lon = df_map["lon"].mean()
                    st.markdown(f"**Mapped Places:** {len(df_map)} venues extracted across all itinerary days.")

                    # 3D Pydeck Map with Day Pins
                    view_state = pdk.ViewState(latitude=mean_lat, longitude=mean_lon, zoom=11, pitch=35)
                    layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=df_map,
                        get_position=["lon", "lat"],
                        get_color="[255, 107, 107, 220]",
                        get_radius=400,
                        pickable=True,
                    )
                    deck = pdk.Deck(
                        layers=[layer],
                        initial_view_state=view_state,
                        tooltip={"text": "[{day}] {title}"},
                    )
                    st.pydeck_chart(deck)

                    with st.expander("📌 View Extracted Itinerary Locations"):
                        st.dataframe(df_map[["day", "title", "lat", "lon"]], use_container_width=True)

                encoded_dest = urllib.parse.quote(destination)
                
                col_gmap, col_osm = st.columns(2)
                with col_osm:
                    st.markdown("#### 🗺️ OpenStreetMap")
                    osm_url = f"https://www.openstreetmap.org/export/embed.html?bbox={mean_lon-0.08:.4f},{mean_lat-0.08:.4f},{mean_lon+0.08:.4f},{mean_lat+0.08:.4f}&layer=mapnik&marker={mean_lat:.4f},{mean_lon:.4f}"
                    st.components.v1.iframe(osm_url, height=300, scrolling=False)
                    st.markdown(f"[👉 Open on OpenStreetMap](https://www.openstreetmap.org/?mlat={mean_lat}&mlon={mean_lon}#map=12/{mean_lat:.4f}/{mean_lon:.4f})")

                with col_gmap:
                    if gmaps_key:
                        st.markdown("#### 🗺️ Google Maps")
                        gmaps_url = f"https://www.google.com/maps/embed/v1/search?key={gmaps_key}&q={encoded_dest}+attractions"
                        st.components.v1.iframe(gmaps_url, height=300, scrolling=True)
                    st.markdown(f"[👉 Open on Google Maps](https://www.google.com/maps/search/?api=1&query={encoded_dest})")

                st.markdown("---")
                with st.expander("📊 Day-by-Day Tabular Itinerary"):
                    guide_text = result.get("purchasing_guide", "")
                    df_itin = parse_itinerary_to_dataframe(itinerary_text, guide_text)
                    st.dataframe(df_itin, use_container_width=True)

                    csv_data = df_itin.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Download Itinerary as CSV",
                        data=csv_data,
                        file_name=f"travel_itinerary_{sanitize_filename(destination).lower()}.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )

            with tab_hotel_food:
                st.markdown("### 🏨 Accommodation")
                st.markdown(result.get("hotel_recommendations", "N/A"))
                st.markdown("---")
                st.markdown("### 🍽️ Food & Retail")
                st.markdown(result.get("food_and_retail", "N/A"))

            with tab_logistics:
                st.markdown(f"### 🛒 Purchasing & Booking Guide ({travelers_summary} • {origin} ✈️ {destination})")
                st.markdown(result.get("purchasing_guide", "N/A"))
                st.markdown("---")
                st.markdown("### 💰 Budget Breakdown & Currency Converter")
                st.code(result.get("budget_breakdown", "N/A"), language=None)

                with st.expander("💱 Live Currency Conversion Tool", expanded=True):
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        amount_sgd = st.number_input("Amount in SGD (S$)", min_value=1.0, value=1000.0, step=50.0)
                        target_curr = st.selectbox("Convert To", options=["USD ($)", "EUR (€)", "JPY (¥)", "GBP (£)", "AUD ($)"])
                    rates = {"USD ($)": 0.74, "EUR (€)": 0.68, "JPY (¥)": 115.5, "GBP (£)": 0.58, "AUD ($)": 1.13}
                    rate = rates.get(target_curr, 0.74)
                    converted = amount_sgd * rate
                    with col_c2:
                        st.metric(label=f"Equivalent in {target_curr.split()[0]}", value=f"{converted:,.2f}")
                        st.caption(f"Estimated rate: 1 SGD = {rate} {target_curr.split()[0]}")

            with tab_chat:
                st.markdown("### 💬 Ask Travel Buddy — Q&A Assistant")
                st.caption(f"Ask follow-up travel questions about {destination}, packing for {travelers_summary}, local transit, or family customs!")

                if "chat_messages" not in st.session_state:
                    st.session_state.chat_messages = []

                for msg in st.session_state.chat_messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

                user_query = st.chat_input("Ask a travel question...")
                if user_query:
                    st.session_state.chat_messages.append({"role": "user", "content": user_query})
                    with st.chat_message("user"):
                        st.markdown(user_query)

                    with st.chat_message("assistant"):
                        with st.spinner("Searching & thinking..."):
                            try:
                                from langchain_core.messages import HumanMessage
                                chat_context = f"Origin: {origin}\\nDestination: {destination}\\nTravelers: {travelers_summary}\\nDates: {dates}\\nItinerary Context:\\n{result.get('itinerary','')[:1000]}"
                                search_res = search_tool.invoke(f"{destination} {user_query}")
                                search_info = "\\n".join(r.get('content', '') for r in search_res) if isinstance(search_res, list) else str(search_res)
                                prompt = f"Context:\\n{chat_context}\\nWeb Info:\\n{search_info}\\nUser Question: {user_query}\\nAnswer helpfully as a travel expert."
                                answer_resp = llm.invoke([HumanMessage(content=prompt)])
                                answer_text = answer_resp.content if isinstance(answer_resp.content, str) else str(answer_resp.content)
                                st.markdown(answer_text)
                                st.session_state.chat_messages.append({"role": "assistant", "content": answer_text})
                            except Exception as e:
                                st.error(f"Failed to generate answer: {e}")

            with tab_advanced:
                with st.expander("⚖️ Quality Verdict (Agent-as-Judge)"):
                    st.markdown(result.get("judge_verdict", "N/A"))
                
                with st.expander("📜 Session Execution & Troubleshooting Logs"):
                    logs_content = get_session_logs()
                    st.markdown(f'<div class="log-box">{logs_content}</div>', unsafe_allow_html=True)
                    st.download_button(
                        label="📥 Download System Debug Log (.log)",
                        data=logs_content.encode("utf-8"),
                        file_name="travel_buddy_debug.log",
                        mime="text/plain",
                        use_container_width=True,
                    )
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

            with st.expander("📜 View Debug Logs"):
                st.markdown(f'<div class="log-box">{get_session_logs()}</div>', unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ Unexpected status: {status}")

        # ── Full Text File Download ──────────────────────────────────────────
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📥 Download Complete Recommendations Report")

        if persona == "custom" and custom_profile:
            persona_label = custom_profile.get("label", "Custom Persona")
        else:
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
            <h3>🤖 4 Collaborative Agents</h3>
            <p>Sightseeing, Food & Retail, Hospitality, and specialized Purchasing & Booking Expert.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="result-card">
            <h3>✈️ Group Travelers & Self-Drive</h3>
            <p>Customizable Adults, Children, and Infant counts + optional car rental & flight costs in SGD.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="result-card">
            <h3>📍 Multi-Location Itinerary Maps</h3>
            <p>Geocodes & plots pins for ALL day-by-day itinerary attractions on Pydeck & OpenStreetMap.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🚀 Getting Started")
    st.info("👈 **Configure travelers, destination & persona in the sidebar and click 'Plan My Trip' to generate your AI-crafted itinerary!**")
