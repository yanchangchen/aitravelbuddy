"""Sidebar setup component for Travel Buddy Streamlit UI."""

import json
import streamlit as st
from datetime import date, timedelta
from core.db import is_db_ready, get_saved_trips, get_trip_plan
from core.profile import save_user_profile
from core.surprise import get_seasonal_surprise


def render_sidebar(secret_gemini, secret_tavily, secret_gmaps):
    """Render streamlined setup sidebar and return user inputs dictionary."""
    with st.sidebar:
        gemini_key = secret_gemini
        tavily_key = secret_tavily
        gmaps_key = secret_gmaps

        st.markdown("## 🎲 Inspiration & Past Trips")
        col_surp, col_load = st.columns([1.2, 1])
        with col_surp:
            if st.button("🎲 Surprise Me!", use_container_width=True, type="secondary", help="Auto-generate a trending seasonal trip pick!"):
                surprise = get_seasonal_surprise()
                st.session_state.surprise_pick = surprise
                st.toast(f"🎲 Surprise Pick: {surprise['title']}!\n{surprise['reason']}")
                st.rerun()

        if is_db_ready():
            saved_trips = get_saved_trips()
            if saved_trips:
                trip_options = {
                    f"{t.get('destination', 'Trip')} ({t.get('persona', 'Plan')}) - {t.get('dates', '')}": t.get("id")
                    for t in saved_trips
                }
                selected_trip_label = st.selectbox("Select Saved Trip", options=list(trip_options.keys()))
                if st.button("📂 Load Selected Plan", use_container_width=True):
                    trip_id = trip_options[selected_trip_label]
                    loaded_state = get_trip_plan(trip_id)
                    if loaded_state:
                        st.session_state.current_result = loaded_state
                        st.success("Loaded trip from storage!")
                        st.rerun()
                    else:
                        st.error("Failed to load plan.")

        uploaded_state_file = st.file_uploader("📤 Import Agent State (.json)", type=["json"], key="sidebar_import_state")
        if uploaded_state_file is not None:
            try:
                import_data = json.load(uploaded_state_file)
                if isinstance(import_data, dict) and ("itinerary" in import_data or "destination" in import_data):
                    st.session_state.current_result = import_data
                    st.toast("✅ Agent run state imported successfully!")
                    st.rerun()
                else:
                    st.error("Invalid agent state JSON file format.")
            except Exception as e:
                st.error(f"Failed to import agent state: {e}")
        st.markdown("---")

        # Check if a Surprise Pick was triggered
        surprise_data = st.session_state.pop("surprise_pick", None)
        if surprise_data:
            st.session_state.active_surprise_banner = surprise_data

        st.markdown("## 📍 1. Destination & Logistics")

        default_origin = surprise_data["origin"] if surprise_data else "Singapore"
        default_dest = surprise_data["destination"] if surprise_data else "Tokyo, Japan"

        origin = st.text_input("Source City (Origin)", value=default_origin, placeholder="e.g. Singapore")
        destination = st.text_input("Destination City/Country", value=default_dest, placeholder="e.g. Tokyo, Japan")

        st.markdown("##### 👥 Group Composition")
        col_a, col_c, col_i = st.columns(3)
        with col_a:
            num_adults = st.number_input("Adults", min_value=1, max_value=20, value=2, step=1)
        with col_c:
            num_children = st.number_input("Children", min_value=0, max_value=20, value=1, step=1)
        with col_i:
            num_infants = st.number_input("Infants", min_value=0, max_value=10, value=0, step=1)

        travelers_parts = [f"{num_adults} Adult{'s' if num_adults>1 else ''}"]
        if num_children > 0:
            travelers_parts.append(f"{num_children} Child{'ren' if num_children>1 else ''}")
        if num_infants > 0:
            travelers_parts.append(f"{num_infants} Infant{'s' if num_infants>1 else ''}")
        travelers_summary = ", ".join(travelers_parts)

        default_start = surprise_data["dates_tuple"][0] if surprise_data else date.today()
        default_end = surprise_data["dates_tuple"][1] if surprise_data else (default_start + timedelta(days=4))

        selected_dates = st.date_input(
            "Travel Dates",
            value=(default_start, default_end),
            min_value=date.today(),
        )

        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            start_d, end_d = selected_dates
            num_days = max(1, (end_d - start_d).days + 1)
            dates_str = f"{start_d.strftime('%b %d, %Y')} - {end_d.strftime('%b %d, %Y')}"
        elif isinstance(selected_dates, tuple) and len(selected_dates) == 1:
            start_d = selected_dates[0]
            num_days = 1
            dates_str = f"{start_d.strftime('%b %d, %Y')}"
        else:
            start_d = selected_dates
            num_days = 1
            dates_str = f"{start_d.strftime('%b %d, %Y')}"

        st.caption(f"📅 Duration: **{num_days} Day{'s' if num_days > 1 else ''}** ({dates_str})")
        dates = dates_str

        st.markdown("---")
        st.markdown("## 🎭 2. Persona & Agent Directives")

        saved_prof = st.session_state.user_profile.get("saved_persona", {})
        saved_label = saved_prof.get("label", "⭐ Saved Persona")

        persona_options = {
            f"{saved_label}": "saved",
            "🧑 Solo Traveler": "single",
            "💼 Business Traveler": "business",
            "💑 Couple's Getaway": "couple",
            "👨‍👩‍👧‍👦 Family Adventure": "family",
            "🎒 Budget Backpacker": "backpacker",
            "🎨 Custom Persona...": "custom",
        }

        default_persona_idx = 0
        if surprise_data:
            p_key = surprise_data["persona"]
            for idx, (lbl, k) in enumerate(persona_options.items()):
                if k == p_key:
                    default_persona_idx = idx
                    break

        persona_display = st.radio("Select Persona Profile", options=list(persona_options.keys()), index=default_persona_idx)
        persona = persona_options[persona_display]

        self_drive = st.checkbox("Self-Drive (Include Car Rental)", value=surprise_data["self_drive"] if surprise_data else False)
        no_budget = st.checkbox("Infinite / Flexible Budget (No Limit)", value=True)

        if not no_budget:
            budget = st.number_input("Budget in SGD (S$)", min_value=100.0, value=3000.0, step=100.0, format="%.2f")
        else:
            budget = 0.0

        custom_profile = None
        if persona == "saved":
            custom_profile = saved_prof
            persona = "custom"
            st.info(f"Using saved persona: **{saved_label}**")
        elif persona == "custom":
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

        with st.expander("👤 Saved Persona & Preferences Settings", expanded=False):
            st.markdown("#### ⚙️ Saved Persona Profile")
            edit_label = st.text_input("Saved Persona Name", value=saved_prof.get("label", "⭐ Saved Persona"))
            edit_tempo = st.selectbox(
                "Saved Pacing Tempo",
                options=["low", "medium", "high", "efficient"],
                index=["low", "medium", "high", "efficient"].index(saved_prof.get("tempo", "medium")) if saved_prof.get("tempo") in ["low", "medium", "high", "efficient"] else 1,
            )
            edit_mobility = st.text_input("Saved Mobility", value=saved_prof.get("mobility", "balanced — walking & public transit"))
            edit_dining = st.text_input("Saved Dining Style", value=saved_prof.get("dining_style", "mix of local hidden gems & curated dining"))
            edit_lodging = st.text_input("Saved Accommodation", value=saved_prof.get("accommodation", "comfortable boutique or 4-star hotels"))
            edit_rules = st.text_area("Saved Persona Rules", value=saved_prof.get("rules", "1. Balance highlights with relaxed exploration."), height=100)

            st.markdown("#### 🍽️ User Preferences Section")
            user_prefs = st.session_state.user_profile.get("preferences", {})

            dietary_options = ["Local Delicacies", "Halal", "Vegetarian", "Vegan", "Gluten-Free", "Seafood", "Michelin Star", "Kid-Friendly"]
            curr_dietary = user_prefs.get("dietary", ["Local Delicacies"])
            if isinstance(curr_dietary, str):
                curr_dietary = [curr_dietary]
            selected_dietary = st.multiselect("Dietary Preferences", options=dietary_options, default=[d for d in curr_dietary if d in dietary_options] or ["Local Delicacies"])

            accom_options = ["Boutique & Quiet", "Luxury Resort", "Family Suite", "Hostel / Budget", "Executive Hotel", "Centrally Located"]
            curr_accom = user_prefs.get("accommodation_pref", "Boutique & Quiet")
            selected_accom = st.selectbox("Preferred Accommodation Style", options=accom_options, index=accom_options.index(curr_accom) if curr_accom in accom_options else 0)

            pace_options = ["Relaxed", "Balanced", "Fast-Paced", "Intensive"]
            curr_pace = user_prefs.get("travel_pace", "Balanced")
            selected_pace = st.selectbox("Preferred Travel Pace", options=pace_options, index=pace_options.index(curr_pace) if curr_pace in pace_options else 1)

            interest_options = ["Culture & History", "Food & Culinary", "Nature & Outdoors", "Shopping & Retail", "Nightlife", "Wellness & Spa", "Family Attractions"]
            curr_interests = user_prefs.get("interests", ["Culture & History", "Food & Culinary"])
            if isinstance(curr_interests, str):
                curr_interests = [curr_interests]
            selected_interests = st.multiselect("Top Travel Interests", options=interest_options, default=[i for i in curr_interests if i in interest_options] or ["Culture & History"])

            selected_notes = st.text_area("Special Directives & Custom Needs", value=user_prefs.get("custom_instructions", ""), placeholder="e.g. Senior friendly, quiet rooms, coffee shops nearby...")

            if st.button("💾 Save Profile to JSON", use_container_width=True):
                new_profile_data = {
                    "saved_persona": {
                        "key": "custom",
                        "label": edit_label,
                        "tempo": edit_tempo,
                        "mobility": edit_mobility,
                        "dining_style": edit_dining,
                        "accommodation": edit_lodging,
                        "rules": edit_rules,
                    },
                    "preferences": {
                        "dietary": selected_dietary,
                        "accommodation_pref": selected_accom,
                        "travel_pace": selected_pace,
                        "interests": selected_interests,
                        "custom_instructions": selected_notes,
                    },
                }
                if save_user_profile(new_profile_data):
                    st.session_state.user_profile = new_profile_data
                    st.toast("✅ Profile & Preferences saved to user_profile.json!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save profile to JSON.")

        st.markdown("---")
        plan_button = st.button("🚀 Plan My Trip", use_container_width=True, type="primary")

    return {
        "gemini_key": gemini_key,
        "tavily_key": tavily_key,
        "gmaps_key": gmaps_key,
        "origin": origin,
        "destination": destination,
        "num_adults": num_adults,
        "num_children": num_children,
        "num_infants": num_infants,
        "travelers_summary": travelers_summary,
        "dates": dates,
        "num_days": num_days,
        "persona": persona,
        "persona_display": persona_display,
        "persona_options": persona_options,
        "custom_profile": custom_profile,
        "self_drive": self_drive,
        "no_budget": no_budget,
        "budget": budget,
        "plan_button": plan_button,
    }
