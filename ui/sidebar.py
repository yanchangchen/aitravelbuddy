"""Sidebar UI component for Travel Buddy.

Strictly separates:
1. Trip Logistics (Trip-Specific & Independent: Destination, Origin, Dates, Group, Self-Drive, Budget)
2. Traveler Persona & Style (Personality & Vibe Suggestions: Pace, Dining, Lodging, Rules)
"""

import json
import streamlit as st
from datetime import date, timedelta
from core.db import save_trip_plan, get_saved_trips, get_trip_plan
from core.profile import save_user_profile
from core.surprise import get_seasonal_surprise


def render_sidebar(gemini_key: str, tavily_key: str, gmaps_key: str) -> dict:
    """Render the setup sidebar and return explicit user input state dict."""
    with st.sidebar:
        st.markdown("# ⚙️ Planning Studio")
        st.caption("Trip Logistics & Traveler Persona Preferences")

        # ── API Key Collapsible Management ─────────────────────────────────────
        with st.expander("🔑 API Key Status", expanded=False):
            if gemini_key:
                st.success("✅ Gemini API Key detected")
            else:
                gemini_key = st.text_input("Gemini API Key", type="password", help="Required for multi-agent execution")

            if tavily_key:
                st.success("✅ Tavily API Key detected")
            else:
                tavily_key = st.text_input("Tavily API Key", type="password", help="Required for live search deals")

            if gmaps_key:
                st.success("✅ Google Maps API Key detected")
            else:
                gmaps_key = st.text_input("Google Maps API Key (Optional)", type="password")

        # ── Saved Trips & Import Section ─────────────────────────────────────
        with st.expander("💾 Saved Trips & State Import", expanded=False):
            saved_trips = get_saved_trips()
            if saved_trips:
                trip_labels = [f"{t['destination']} ({t['dates']})" for t in saved_trips]
                selected_label = st.selectbox("Load Saved Trip", options=trip_labels)
                if st.button("📥 Load Trip State", use_container_width=True):
                    idx = trip_labels.index(selected_label)
                    trip_id = saved_trips[idx]["id"]
                    loaded_data = get_trip_plan(trip_id)
                    if loaded_data:
                        st.session_state.current_result = loaded_data
                        st.toast("✅ Loaded trip from storage!")
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

        # Initialize session_state widget keys ONCE if missing
        if "input_destination_text" not in st.session_state:
            st.session_state["input_destination_text"] = "Tokyo, Japan"
        if "input_origin_text" not in st.session_state:
            st.session_state["input_origin_text"] = "Singapore"
        if "input_dates" not in st.session_state:
            d_start = date.today()
            d_end = d_start + timedelta(days=4)
            st.session_state["input_dates"] = (d_start, d_end)
        if "input_self_drive" not in st.session_state:
            st.session_state["input_self_drive"] = False

        # ── Check if a Surprise Pick was triggered ───────────────────────────
        surprise_data = st.session_state.pop("surprise_pick", None)
        if surprise_data:
            st.session_state.active_surprise_banner = surprise_data
            # Overwrite session_state widget keys directly so Streamlit inputs display the surprise pick
            st.session_state["input_destination_text"] = surprise_data["destination"]
            st.session_state["input_origin_text"] = surprise_data["origin"]
            if "dates_tuple" in surprise_data:
                st.session_state["input_dates"] = surprise_data["dates_tuple"]
            if "self_drive" in surprise_data:
                st.session_state["input_self_drive"] = surprise_data["self_drive"]

        # ── CARD 1: TRIP LOGISTICS (TRIP-SPECIFIC & INDEPENDENT) ─────────────
        st.markdown("## 📍 1. Trip Logistics")
        st.caption("🔒 *Trip-Specific Details (Fixed per trip & independent of persona)*")

        origin = st.text_input(
            "Source City (Origin)",
            key="input_origin_text",
            placeholder="e.g. Singapore",
        )

        destination = st.text_input(
            "Destination City/Country",
            key="input_destination_text",
            placeholder="e.g. Tokyo, Japan",
        )

        st.markdown("##### 👥 Group Composition")
        col_a, col_c, col_i = st.columns(3)
        with col_a:
            num_adults = st.number_input("Adults", min_value=1, max_value=20, value=2, step=1, key="input_num_adults")
        with col_c:
            num_children = st.number_input("Children", min_value=0, max_value=20, value=1, step=1, key="input_num_children")
        with col_i:
            num_infants = st.number_input("Infants", min_value=0, max_value=10, value=0, step=1, key="input_num_infants")

        travelers_parts = [f"{num_adults} Adult{'s' if num_adults>1 else ''}"]
        if num_children > 0:
            travelers_parts.append(f"{num_children} Child{'ren' if num_children>1 else ''}")
        if num_infants > 0:
            travelers_parts.append(f"{num_infants} Infant{'s' if num_infants>1 else ''}")
        travelers_summary = ", ".join(travelers_parts)

        selected_dates = st.date_input(
            "Travel Dates",
            key="input_dates",
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

        # Logistics specifics: Self-drive & Budget
        self_drive = st.checkbox("Self-Drive (Include Car Rental & Tolls)", key="input_self_drive")
        no_budget = st.checkbox("Infinite / Flexible Budget (No Limit)", value=True, key="input_no_budget")

        if not no_budget:
            budget = st.number_input("Budget in SGD (S$)", min_value=100.0, value=3000.0, step=100.0, format="%.2f", key="input_budget_val")
        else:
            budget = 0.0

        st.markdown("---")

        # ── CARD 2: PERSONA & AGENT DIRECTIVES (PERSONALITY & STYLE ONLY) ─────
        st.markdown("## 🎭 2. Persona & Agent Directives")
        st.caption("💡 *Personality Suggestions & Vibe (Applies to your selected destination)*")

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

        persona_display = st.radio(
            "Select Persona Profile",
            options=list(persona_options.keys()),
            index=default_persona_idx,
            key="input_persona_radio",
            help="Selecting a persona updates dining, pace, lodging & rules for your chosen destination.",
        )
        persona = persona_options[persona_display]

        custom_profile = None
        if persona == "saved":
            custom_profile = saved_prof
            persona = "custom"
            st.info(f"Using saved persona preferences: **{saved_label}**")
        elif persona == "custom":
            with st.expander("🛠️ Define Custom Persona Rules", expanded=True):
                custom_title = st.text_input("Persona Name", value="🧘 Wellness & Slow Travel Retreat", key="custom_p_title")
                custom_tempo = st.selectbox("Pacing Tempo", options=["low", "medium", "high"], index=0, key="custom_p_tempo")
                custom_mobility = st.text_input("Mobility Preference", value="relaxed walking, private shuttles", key="custom_p_mobility")
                custom_dining = st.text_input("Dining Style", value="organic farm-to-table, plant-based cafes, tea houses", key="custom_p_dining")
                custom_lodging = st.text_input("Accommodation Preference", value="wellness resorts, quiet ryokans, boutique retreats", key="custom_p_lodging")
                custom_rules = st.text_area(
                    "Mandatory Persona Rules (1 per line)",
                    value=(
                        "1. Morning yoga or mindfulness before 9:00 AM.\n"
                        "2. Maximum 2 gentle activities per day.\n"
                        "3. Prioritize natural hot springs, gardens, and quiet temples.\n"
                        "4. Include healthy, organic dining options."
                    ),
                    height=120,
                    key="custom_p_rules",
                )
                custom_profile = {
                    "label": f"🎨 {custom_title}",
                    "tempo": custom_tempo,
                    "mobility": custom_mobility,
                    "dining_style": custom_dining,
                    "accommodation": custom_lodging,
                    "rules": custom_rules,
                }

        with st.expander("👤 Saved Persona & Preference Settings", expanded=False):
            st.markdown("#### ⚙️ Reusable Persona Profile")
            st.caption("This profile is saved to `user_profile.json` and reused across any destination.")
            edit_label = st.text_input("Saved Persona Name", value=saved_prof.get("label", "⭐ Saved Persona"), key="edit_p_label")
            edit_tempo = st.selectbox(
                "Saved Pacing Tempo",
                options=["low", "medium", "high", "efficient"],
                index=["low", "medium", "high", "efficient"].index(saved_prof.get("tempo", "medium")) if saved_prof.get("tempo") in ["low", "medium", "high", "efficient"] else 1,
                key="edit_p_tempo",
            )
            edit_mobility = st.text_input("Saved Mobility", value=saved_prof.get("mobility", "balanced — walking & public transit"), key="edit_p_mobility")
            edit_dining = st.text_input("Saved Dining Style", value=saved_prof.get("dining_style", "mix of local hidden gems & curated dining"), key="edit_p_dining")
            edit_lodging = st.text_input("Saved Accommodation", value=saved_prof.get("accommodation", "comfortable boutique or 4-star hotels"), key="edit_p_lodging")
            edit_rules = st.text_area("Saved Persona Rules", value=saved_prof.get("rules", "1. Balance highlights with relaxed exploration."), height=100, key="edit_p_rules")

            st.markdown("#### 🍽️ User Preference Settings")
            user_prefs = st.session_state.user_profile.get("preferences", {})

            dietary_options = ["Local Delicacies", "Halal", "Vegetarian", "Vegan", "Gluten-Free", "Seafood", "Michelin Star", "Kid-Friendly"]
            curr_dietary = user_prefs.get("dietary", ["Local Delicacies"])
            if isinstance(curr_dietary, str):
                curr_dietary = [curr_dietary]
            selected_dietary = st.multiselect("Dietary Preferences", options=dietary_options, default=[d for d in curr_dietary if d in dietary_options] or ["Local Delicacies"], key="edit_p_dietary")

            accom_options = ["Boutique & Quiet", "Luxury Resort", "Family Suite", "Hostel / Budget", "Executive Hotel", "Centrally Located"]
            curr_accom = user_prefs.get("accommodation_pref", "Boutique & Quiet")
            selected_accom = st.selectbox("Preferred Accommodation Style", options=accom_options, index=accom_options.index(curr_accom) if curr_accom in accom_options else 0, key="edit_p_accom")

            pace_options = ["Relaxed", "Balanced", "Fast-Paced", "Intensive"]
            curr_pace = user_prefs.get("travel_pace", "Balanced")
            selected_pace = st.selectbox("Preferred Travel Pace", options=pace_options, index=pace_options.index(curr_pace) if curr_pace in pace_options else 1, key="edit_p_pace")

            interest_options = ["Culture & History", "Food & Culinary", "Nature & Outdoors", "Shopping & Retail", "Nightlife", "Wellness & Spa", "Family Attractions"]
            curr_interests = user_prefs.get("interests", ["Culture & History", "Food & Culinary"])
            if isinstance(curr_interests, str):
                curr_interests = [curr_interests]
            selected_interests = st.multiselect("Top Travel Interests", options=interest_options, default=[i for i in curr_interests if i in interest_options] or ["Culture & History"], key="edit_p_interests")

            selected_notes = st.text_area("Special Directives & Custom Needs", value=user_prefs.get("custom_instructions", ""), placeholder="e.g. Senior friendly, quiet rooms, coffee shops nearby...", key="edit_p_notes")

            if st.button("💾 Save Persona & Preferences to JSON", use_container_width=True):
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
                    st.toast("✅ Persona profile & preferences saved to user_profile.json!")
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
