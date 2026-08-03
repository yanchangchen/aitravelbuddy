"""Landing page and Guided Chatbot component for Travel Buddy."""

import json
import re
import streamlit as st
from datetime import date, timedelta
from core.surprise import SEASONAL_PACKAGES, get_current_season


def extract_plan_from_conversation(guided_messages: list, gemini_key: str) -> dict:
    """Analyze full conversation history and extract structured trip logistics & persona preferences."""
    from core.utils import ensure_str
    transcript = "\n".join(
        f"{m['role'].upper()}: {ensure_str(m['content'])}" for m in guided_messages
    )

    if gemini_key:
        try:
            from langchain_core.messages import HumanMessage
            from langchain_google_genai import ChatGoogleGenerativeAI

            prompt = (
                "You are an expert travel planner analyzer. Analyze the following travel concierge conversation transcript "
                "between a user and an AI concierge. Extract the user's travel preferences into a valid JSON object with EXACTLY these keys:\n\n"
                "{\n"
                '  "destination": "Extracted Destination City and Country (e.g. Chengdu, China). Default to Tokyo, Japan if unknown.",\n'
                '  "origin": "Source city (e.g. Singapore)",\n'
                '  "num_days": 5,\n'
                '  "num_adults": 2,\n'
                '  "num_children": 1,\n'
                '  "num_infants": 0,\n'
                '  "persona_title": "Descriptive title summarizing persona (e.g. Foodie Family Retreat)",\n'
                '  "tempo": "low, medium, or high",\n'
                '  "mobility": "Description of mobility & transport style",\n'
                '  "dining_style": "Specific food and dining preferences discussed",\n'
                '  "accommodation": "Accommodation style preferred",\n'
                '  "rules": "3-5 mandatory numbered rules summarizing user requirements discussed in chat",\n'
                '  "custom_instructions": "Detailed summary of all user directives and conversation preferences"\n'
                "}\n\n"
                f"Transcript:\n{transcript}\n\n"
                "Return ONLY the JSON object, wrapped in ```json ... ```."
            )

            llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.2, google_api_key=gemini_key)
            resp = llm.invoke([HumanMessage(content=prompt)])
            text = ensure_str(resp.content)

            json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            else:
                json_match2 = re.search(r"(\{.*\})", text, re.DOTALL)
                if json_match2:
                    return json.loads(json_match2.group(1))
        except Exception as e:
            print(f"LLM conversation extraction error: {e}")

    # Fallback rule-based parser if LLM unavailable or fails
    dest_match = re.search(r"RECOMMENDED_DESTINATION:\s*([^\n\r\"'}]+)", transcript, re.IGNORECASE)
    days_match = re.search(r"RECOMMENDED_DAYS:\s*(\d+)", transcript, re.IGNORECASE)

    extracted_dest = dest_match.group(1).strip() if dest_match else "Chengdu, China"
    extracted_days = int(days_match.group(1).strip()) if days_match else 5

    return {
        "destination": extracted_dest,
        "origin": "Singapore",
        "num_days": extracted_days,
        "num_adults": 2,
        "num_children": 1,
        "num_infants": 0,
        "persona_title": f"Concierge Plan: {extracted_dest}",
        "tempo": "medium",
        "mobility": "balanced walking & transport",
        "dining_style": "local delicacies & curated food stops",
        "accommodation": "family boutique & comfortable hotel",
        "rules": (
            "1. Focus on authentic local culinary highlights.\n"
            "2. Ensure family-friendly comfortable walking pace.\n"
            "3. Include top scenic sights discussed in concierge chat."
        ),
        "custom_instructions": f"Plan derived from AI Concierge conversation for {extracted_dest}."
    }


def launch_plan_from_conversation(gemini_key: str):
    """Extract conversation history preferences, populate sidebar widgets, and auto-trigger 4-agent graph execution."""
    with st.spinner("Extracting conversation preferences & initiating 4-agent planner..."):
        plan_specs = extract_plan_from_conversation(st.session_state.guided_messages, gemini_key)

        # Pre-fill sidebar widget state directly
        st.session_state["input_destination_text"] = plan_specs["destination"]
        st.session_state["input_origin_text"] = plan_specs.get("origin", "Singapore")
        st.session_state["input_num_adults"] = plan_specs.get("num_adults", 2)
        st.session_state["input_num_children"] = plan_specs.get("num_children", 0)
        st.session_state["input_num_infants"] = plan_specs.get("num_infants", 0)

        # Set custom persona & rules extracted from conversation
        st.session_state["input_persona_radio"] = "🎨 Custom Persona..."
        st.session_state["custom_p_title"] = plan_specs.get("persona_title", f"Concierge Plan: {plan_specs['destination']}")
        st.session_state["custom_p_tempo"] = plan_specs.get("tempo", "medium")
        st.session_state["custom_p_mobility"] = plan_specs.get("mobility", "balanced walking & transport")
        st.session_state["custom_p_dining"] = plan_specs.get("dining_style", "mix of local hidden gems & curated dining")
        st.session_state["custom_p_lodging"] = plan_specs.get("accommodation", "comfortable boutique hotel")
        st.session_state["custom_p_rules"] = plan_specs.get("rules", "1. Follow conversation directives strictly.")

        if "user_profile" in st.session_state and isinstance(st.session_state.user_profile, dict):
            if "preferences" not in st.session_state.user_profile:
                st.session_state.user_profile["preferences"] = {}
            st.session_state.user_profile["preferences"]["custom_instructions"] = plan_specs.get("custom_instructions", "")

        # Trigger automatic plan execution in app.py
        st.session_state.auto_launch_plan = True
        st.toast(f"🤖 Initiating planner for {plan_specs['destination']} based on conversation history!")
        st.rerun()


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

        from core.utils import ensure_str
        for msg in st.session_state.guided_messages:
            with st.chat_message(msg["role"]):
                st.markdown(ensure_str(msg["content"]))

        # Action bar to initiate planner directly from current conversation
        if len(st.session_state.guided_messages) > 1:
            st.markdown("---")
            col_act1, col_act2 = st.columns([3, 1])
            with col_act1:
                st.info("💡 **Ready to plan?** Click **'Plan with current conversation'** to convert your chat history into trip specs and start the 4-agent planner!")
            with col_act2:
                if st.button("🚀 Plan with current conversation", type="primary", use_container_width=True, key="btn_plan_conv_top"):
                    launch_plan_from_conversation(gemini_key)

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
                            from core.utils import ensure_str
                            llm_guided = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7, google_api_key=gemini_key)
                            resp = llm_guided.invoke([HumanMessage(content=prompt)])
                            reply_text = ensure_str(resp.content)
                        else:
                            reply_text = (
                                "Based on your preferences, I recommend:\n"
                                "1. **Tokyo, Japan** (Urban food, culture, tech)\n"
                                "2. **Bali, Indonesia** (Tropical relaxation & beach sunsets)\n\n"
                                "RECOMMENDED_DESTINATION: Tokyo, Japan\n"
                                "RECOMMENDED_PERSONA: couple\n"
                                "RECOMMENDED_DAYS: 5"
                            )

                        dest_m = re.search(r"RECOMMENDED_DESTINATION:\s*([^\n\r\"'}]+)", reply_text, re.IGNORECASE)
                        persona_m = re.search(r"RECOMMENDED_PERSONA:\s*([^\n\r\"'}]+)", reply_text, re.IGNORECASE)
                        days_m = re.search(r"RECOMMENDED_DAYS:\s*(\d+)", reply_text, re.IGNORECASE)

                        clean_reply = re.sub(r"RECOMMENDED_DESTINATION:.*", "", reply_text, flags=re.IGNORECASE)
                        clean_reply = re.sub(r"RECOMMENDED_PERSONA:.*", "", clean_reply, flags=re.IGNORECASE)
                        clean_reply = re.sub(r"RECOMMENDED_DAYS:.*", "", clean_reply, flags=re.IGNORECASE).strip()

                        st.markdown(clean_reply)
                        st.session_state.guided_messages.append({"role": "assistant", "content": clean_reply})

                        if dest_m:
                            rec_dest = dest_m.group(1).strip()
                            rec_persona = persona_m.group(1).strip() if persona_m else "couple"
                            rec_days = int(days_m.group(1).strip()) if days_m else 5

                            st.markdown("---")
                            st.info(f"✨ **AI Concierge Pick:** {rec_dest} ({rec_days} Days)")

                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button(f"🚀 Plan with current conversation", type="primary", use_container_width=True, key=f"launch_guided_conv_{rec_dest}"):
                                    launch_plan_from_conversation(gemini_key)
                            with col_btn2:
                                if st.button(f"🎨 Apply Vibe Only to My Current Destination", use_container_width=True, key=f"launch_guided_vibe_{rec_dest}", help="Applies this concierge recommendation style to your current destination without changing your destination!"):
                                    st.session_state.user_profile["saved_persona"]["key"] = rec_persona
                                    st.session_state.user_profile["saved_persona"]["label"] = f"🌟 Guided Concierge Vibe ({rec_dest})"
                                    st.toast(f"🎨 Applied Concierge Vibe to your current destination!")
                                    st.rerun()
                    except Exception as e:
                        st.error(f"Concierge error: {e}")

    with land_tab_surprise:
        st.markdown("#### 🎲 Seasonal Top Pick Inspiration")
        st.caption("Auto-refreshes every 3 months based on real-world calendar seasons. Click 'Fetch Live AI Updates' for on-demand new seasonal suggestions!")

        season_now = get_current_season()
        year_now = date.today().year

        col_hdr1, col_hdr2 = st.columns([3, 1])
        with col_hdr1:
            st.info(f"📅 **Current Season:** {season_now.capitalize()} {year_now} *(Auto-switches every 3 months)*")
        with col_hdr2:
            if st.button("🔄 Fetch Live AI Updates", type="secondary", use_container_width=True, help="Queries live AI search for new trending travel destinations for this season!"):
                with st.spinner("Fetching live AI trending seasonal picks..."):
                    from core.surprise import fetch_live_seasonal_picks
                    live_picks = fetch_live_seasonal_picks(season_now, gemini_key)
                    if "custom_seasonal_picks" not in st.session_state:
                        st.session_state.custom_seasonal_picks = {}
                    st.session_state.custom_seasonal_picks[season_now] = live_picks
                    st.toast(f"✨ Refreshed 3 brand new live seasonal picks for {season_now.capitalize()} {year_now}!")
                    st.rerun()

        # Retrieve custom live picks if user initiated a refresh, else use curated packages
        if "custom_seasonal_picks" in st.session_state and season_now in st.session_state.custom_seasonal_picks:
            season_picks = st.session_state.custom_seasonal_picks[season_now]
        else:
            season_picks = SEASONAL_PACKAGES.get(season_now, SEASONAL_PACKAGES["summer"])

        col_p1, col_p2 = st.columns(2)
        for idx, p in enumerate(season_picks):
            col_target = col_p1 if idx % 2 == 0 else col_p2
            with col_target:
                st.markdown(f"### {p['title']}")
                st.markdown(f"**Season:** {season_now.capitalize()} • **Duration:** {p.get('duration_days', 5)} Days")
                st.markdown(f"_{p['reason']}_")
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button(f"🚀 Apply Destination & Vibe", key=f"btn_pick_full_{idx}", use_container_width=True):
                        start_d = date.today() + timedelta(days=14)
                        duration = p.get('duration_days', 5)
                        end_d = start_d + timedelta(days=duration - 1)
                        st.session_state.surprise_pick = {
                            "title": p["title"],
                            "reason": p["reason"],
                            "destination": p["destination"],
                            "origin": p.get("origin", "Singapore"),
                            "persona": p.get("persona", "couple"),
                            "self_drive": p.get("self_drive", False),
                            "no_budget": True,
                            "dates_tuple": (start_d, end_d),
                            "duration_days": duration
                        }
                        st.rerun()
                with col_b2:
                    if st.button(f"🎨 Apply Vibe Only", key=f"btn_pick_vibe_{idx}", use_container_width=True, help="Applies this seasonal persona style to your current destination without changing your destination!"):
                        st.session_state.user_profile["saved_persona"]["key"] = p.get("persona", "couple")
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
                <h3>⚖️ Quality & Budget Verification</h3>
                <p>Iterative LLM budget evaluation and Persona compliance verification before approving outputs.</p>
            </div>
            """, unsafe_allow_html=True)
