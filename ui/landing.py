"""Landing page and Guided Chatbot component for Travel Buddy."""

import re
import streamlit as st
from datetime import date, timedelta
from core.surprise import SEASONAL_PACKAGES, get_current_season


def render_landing_view(gemini_key):
    """Render interactive landing view with Guided Plan Chatbot & Seasonal Picks."""
    if "active_surprise_banner" in st.session_state and st.session_state.active_surprise_banner:
        b = st.session_state.pop("active_surprise_banner")
        st.info(
            f"🎲 **Seasonal Pick Active:** {b.get('title', 'Seasonal Trip')}\n\n"
            f"📍 **Destination:** {b.get('destination', '')} • 📅 **Dates:** {b.get('dates_str', '')} ({b.get('num_days', 5)} Days)\n\n"
            f"👈 **Search criteria pre-filled in sidebar!** You can **edit any criteria in the sidebar** or click **'🚀 Plan My Trip'** to generate your AI itinerary!"
        )

    st.markdown("### 🌟 Welcome to Travel Buddy — Undecided? We've Got You!")

    land_tab_guided, land_tab_surprise, land_tab_features = st.tabs([
        "💬 Guided Plan With Me (Interactive Assistant)",
        "🎲 Surprise Me! (Seasonal Inspiration)",
        "✨ Key Features & Architecture",
    ])

    with land_tab_guided:
        st.markdown("#### 🤖 Chat with Travel Buddy Concierge")
        st.caption("Not sure where to go or how to plan your trip? Chat with our AI concierge below to discover destination ideas, budget recommendations, and travel styles!")

        if "guided_messages" not in st.session_state:
            st.session_state.guided_messages = [
                {
                    "role": "assistant",
                    "content": "👋 **Hello Traveler!** I'm your AI Travel Concierge. Tell me a bit about what you're looking for:\n\n- What's the main vibe you want? *(e.g. relaxing beach retreat, food & city adventure, scenic nature, family fun)*\n- Who is traveling with you?\n- Any preferred region or season?"
                }
            ]

        for msg in st.session_state.guided_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        guided_user_input = st.chat_input("Tell me what travel vibe or destination idea you have in mind...", key="guided_chat_input")
        if guided_user_input:
            st.session_state.guided_messages.append({"role": "user", "content": guided_user_input})
            with st.chat_message("user"):
                st.markdown(guided_user_input)

            with st.chat_message("assistant"):
                with st.spinner("Concierge is thinking & searching best recommendations..."):
                    try:
                        from langchain_core.messages import HumanMessage
                        curr_season = get_current_season()

                        prompt = (
                            f"You are a friendly, highly knowledgeable AI Travel Concierge helping an undecided traveler.\n"
                            f"Current Season: {curr_season.capitalize()}\n"
                            f"User Query: {guided_user_input}\n\n"
                            f"Chat History:\n" + "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.guided_messages[-4:]) + "\n\n"
                            f"Respond warmly and recommend 2-3 specific destinations matching their vibe.\n"
                            f"At the bottom of your response, specify a recommended trip package in this EXACT format:\n"
                            f"RECOMMENDED_DESTINATION: [City, Country]\n"
                            f"RECOMMENDED_PERSONA: [family / couple / single / business / backpacker]\n"
                            f"RECOMMENDED_DAYS: [number of days]\n"
                        )

                        if gemini_key:
                            from langchain_google_genai import ChatGoogleGenerativeAI
                            llm_guided = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7, google_api_key=gemini_key)
                            resp = llm_guided.invoke([HumanMessage(content=prompt)])
                            reply_text = resp.content if isinstance(resp.content, str) else str(resp.content)
                        else:
                            reply_text = (
                                "Based on your preferences, I recommend:\n"
                                "1. **Tokyo, Japan** (Urban food, culture, tech)\n"
                                "2. **Bali, Indonesia** (Tropical relaxation & beach sunsets)\n\n"
                                "RECOMMENDED_DESTINATION: Tokyo, Japan\n"
                                "RECOMMENDED_PERSONA: couple\n"
                                "RECOMMENDED_DAYS: 5"
                            )

                        dest_m = re.search(r"RECOMMENDED_DESTINATION:\s*(.*)", reply_text)
                        clean_reply = re.sub(r"RECOMMENDED_.*", "", reply_text).strip()

                        st.markdown(clean_reply)
                        st.session_state.guided_messages.append({"role": "assistant", "content": clean_reply})

                        if dest_m:
                            rec_dest = dest_m.group(1).strip()
                            st.markdown("---")
                            if st.button(f"🚀 Launch Trip Plan for {rec_dest}", type="primary", use_container_width=True, key=f"launch_guided_{rec_dest}"):
                                st.session_state.surprise_pick = {
                                    "title": f"Guided Pick: {rec_dest}",
                                    "reason": "Recommended by AI Travel Concierge",
                                    "destination": rec_dest,
                                    "origin": "Singapore",
                                    "persona": "couple",
                                    "self_drive": False,
                                    "no_budget": True,
                                    "dates_tuple": (date.today() + timedelta(days=14), date.today() + timedelta(days=18)),
                                    "duration_days": 5
                                }
                                st.rerun()
                    except Exception as e:
                        st.error(f"Concierge error: {e}")

    with land_tab_surprise:
        st.markdown("#### 🎲 Seasonal Top Pick Inspiration")
        st.caption("Click any seasonal package below to auto-fill specs and launch your trip plan instantly!")

        season_now = get_current_season()
        col_p1, col_p2 = st.columns(2)
        season_picks = SEASONAL_PACKAGES.get(season_now, SEASONAL_PACKAGES["summer"])

        for idx, p in enumerate(season_picks):
            col_target = col_p1 if idx % 2 == 0 else col_p2
            with col_target:
                st.markdown(f"### {p['title']}")
                st.markdown(f"**Season:** {season_now.capitalize()} • **Duration:** {p['duration_days']} Days")
                st.markdown(f"_{p['reason']}_")
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button(f"🚀 Apply Destination & Vibe", key=f"btn_pick_full_{idx}", use_container_width=True):
                        start_d = date.today() + timedelta(days=14)
                        end_d = start_d + timedelta(days=p['duration_days'] - 1)
                        st.session_state.surprise_pick = {
                            "title": p["title"],
                            "reason": p["reason"],
                            "destination": p["destination"],
                            "origin": p["origin"],
                            "persona": p["persona"],
                            "self_drive": p["self_drive"],
                            "no_budget": True,
                            "dates_tuple": (start_d, end_d),
                            "duration_days": p["duration_days"]
                        }
                        st.rerun()
                with col_b2:
                    if st.button(f"🎨 Apply Vibe Only", key=f"btn_pick_vibe_{idx}", use_container_width=True, help="Applies this seasonal persona style to your current destination without changing your destination!"):
                        st.session_state.user_profile["saved_persona"]["key"] = p["persona"]
                        st.session_state.user_profile["saved_persona"]["label"] = f"🌟 {p['title']}"
                        st.toast(f"🎨 Applied '{p['title']}' vibe to your current destination!")
                        st.rerun()
                st.markdown("---")

    with land_tab_features:
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
