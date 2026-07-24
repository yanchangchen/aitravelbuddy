"""Plan view renderer component for Travel Buddy Streamlit interface."""

import json
import urllib.parse
from datetime import datetime
import streamlit as st
import pandas as pd
import pydeck as pdk

from core.logger import get_session_logs
from core.db import save_trip_plan
from core.personas import PERSONA_PROFILES
from core.utils import (
    build_recommendations_text,
    sanitize_filename,
    parse_itinerary_to_dataframe,
    extract_all_itinerary_locations,
)


def render_plan_results(result: dict, inputs: dict, search_tool=None, llm=None):
    """Render complete trip plan results, 5 tabs, Pydeck maps, day-by-day table, Q&A chat, logs, and report downloads."""
    status = result.get("status", "unknown")
    res_destination = result.get("destination", inputs.get("destination", "Tokyo, Japan"))
    res_travelers = result.get("travelers_summary", inputs.get("travelers_summary", "2 Adults"))
    res_dates = result.get("dates", inputs.get("dates", ""))
    res_origin = result.get("origin", inputs.get("origin", "Singapore"))
    res_persona = result.get("persona", inputs.get("persona", "couple"))
    res_no_budget = result.get("no_budget", inputs.get("no_budget", True))
    res_budget = result.get("budget", inputs.get("budget", 0.0))
    res_custom_profile = result.get("custom_persona_profile", inputs.get("custom_profile", None))
    gmaps_key = inputs.get("gmaps_key", None)
    persona_options = inputs.get("persona_options", {})

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        p_label = PERSONA_PROFILES.get(res_persona, PERSONA_PROFILES["couple"])["label"] if res_persona != "custom" else "Custom Persona"
        if res_custom_profile and isinstance(res_custom_profile, dict):
            p_label = res_custom_profile.get("label", p_label)

        if st.button("💾 Save Trip & Agent State", type="primary", use_container_width=True, key="save_trip_view_btn"):
            if save_trip_plan(res_destination, res_travelers, p_label, res_dates, result):
                st.toast(f"✅ Trip details & agent run state saved for {res_destination}!")
            else:
                st.error("Failed to save trip plan.")

    with col_s2:
        agent_json_bytes = json.dumps(result, indent=2, ensure_ascii=False).encode("utf-8")
        safe_dest_name = sanitize_filename(res_destination).lower().replace(" ", "_")
        st.download_button(
            label="📥 Export Agent State (.json)",
            data=agent_json_bytes,
            file_name=f"agent_run_state_{safe_dest_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )

    logs_content = result.get("session_logs") or get_session_logs()

    with st.expander("📜 View Real-Time Agent Console & Debug Logs", expanded=False):
        st.markdown(f'<div class="log-box">{logs_content}</div>', unsafe_allow_html=True)
        st.download_button(
            label="📥 Download Debug Log (.log)",
            data=logs_content.encode("utf-8"),
            file_name="travel_buddy_debug.log",
            mime="text/plain",
            use_container_width=True,
            key="dl_debug_log_top"
        )

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    if status == "approved":
        st.markdown(
            f'<span class="badge-approved">✅ TRIP PLAN APPROVED for {res_travelers}</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<span class="badge-busted">⚠️ UNAPPROVED PROVISIONAL PLAN — Quality / Budget Criteria Not Met</span>',
            unsafe_allow_html=True,
        )
        with st.expander("🚨 WHY QUALITY / BUDGET EVALUATION FAILED & HOW TO RELAX CRITERIA", expanded=True):
            failure_reason = result.get("quality_failure_reason") or result.get("budget_breakdown", "Plan did not meet strict criteria.")
            st.code(failure_reason, language=None)

            st.markdown("#### 🛠️ Relax Criteria & Rerun Pipeline")
            st.markdown("You can relax criteria below to allow agents to rerun and approve your plan:")

            col_r1, col_r2 = st.columns(2)
            with col_r1:
                relax_no_budget = st.checkbox("Enable Unlimited / Flexible Budget Mode", value=True, key="relax_nobudget_chk")
                relax_persona = st.selectbox("Switch to Persona Profile", options=list(persona_options.keys()), index=0, key="relax_persona_sel")
            with col_r2:
                relax_dates = st.text_input("Adjust Travel Dates / Duration", value=str(res_dates), key="relax_dates_inp")
                relax_notes = st.text_input("Additional Custom Guidance", placeholder="e.g. Relax daily activity count limits", key="relax_notes_inp")

            if st.button("🔄 Relax Criteria & Rerun Pipeline", type="primary", use_container_width=True, key="relax_rerun_btn"):
                if relax_no_budget:
                    st.session_state.force_no_budget = True
                if persona_options.get(relax_persona):
                    st.session_state.force_persona = persona_options[relax_persona]
                st.session_state.force_dates = relax_dates
                if relax_notes.strip():
                    st.session_state.force_custom_instructions = relax_notes
                st.info("🔄 Criteria relaxed! Rerunning agent pipeline...")
                st.rerun()

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
        st.markdown(f"### 📍 Complete Itinerary Map — {res_destination}")

        itinerary_text = result.get("itinerary", "")
        loc_list = extract_all_itinerary_locations(itinerary_text, res_destination)
        df_map = pd.DataFrame(loc_list)

        if not df_map.empty:
            mean_lat = df_map["lat"].mean()
            mean_lon = df_map["lon"].mean()
            st.markdown(f"**Mapped Places:** {len(df_map)} venues extracted across all itinerary days.")

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

        encoded_dest = urllib.parse.quote(res_destination)
        col_gmap, col_osm = st.columns(2)
        with col_osm:
            st.markdown("#### 🗺️ OpenStreetMap")
            if not df_map.empty:
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

            import io
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_itin.to_excel(writer, index=False, sheet_name='Itinerary')
            excel_data = excel_buffer.getvalue()

            st.download_button(
                label="📥 Download Itinerary as Excel (.xlsx)",
                data=excel_data,
                file_name=f"travel_itinerary_{sanitize_filename(res_destination).lower()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    with tab_hotel_food:
        st.markdown("### 🏨 Accommodation")
        st.markdown(result.get("hotel_recommendations", "N/A"))
        st.markdown("---")
        st.markdown("### 🍽️ Food & Retail")
        st.markdown(result.get("food_and_retail", "N/A"))

    with tab_logistics:
        st.markdown(f"### 🛒 Purchasing & Booking Guide ({res_travelers} • {res_origin} ✈️ {res_destination})")
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
        st.markdown("### 💬 Ask Travel Buddy — Q&A Assistant & Trip Modifier")
        st.caption(f"Ask follow-up travel questions about {res_destination}, packing for {res_travelers}, or iterate on preferences below to regenerate the plan!")

        with st.expander("✏️ Iterate & Regenerate Loaded Plan", expanded=True):
            st.markdown("Want to modify this trip plan for a different persona or duration?")
            col_mod1, col_mod2 = st.columns(2)
            with col_mod1:
                mod_persona_disp = st.selectbox(
                    "Switch Persona Profile",
                    options=list(persona_options.keys()),
                    key="chat_mod_persona"
                )
            with col_mod2:
                mod_dates = st.text_input("Adjust Travel Dates / Duration", value=str(res_dates), key="chat_mod_dates")

            mod_instructions = st.text_input("Additional Custom Requests", placeholder="e.g. Add 2 days of luxury hot spring ryokans", key="chat_mod_inst")

            if st.button("🔄 Apply Preferences & Regenerate Trip Plan", type="primary", use_container_width=True, key="chat_mod_btn"):
                st.session_state.force_persona = persona_options[mod_persona_disp]
                st.session_state.force_dates = mod_dates
                if mod_instructions.strip():
                    st.session_state.force_custom_instructions = mod_instructions
                st.info("🔄 Preferences updated! Triggering agent pipeline...")
                st.rerun()

        st.markdown("---")

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_query = st.chat_input("Ask a travel question...", key="chat_input_main")
        if user_query:
            st.session_state.chat_messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                with st.spinner("Searching & thinking..."):
                    try:
                        from langchain_core.messages import HumanMessage
                        chat_context = f"Origin: {res_origin}\nDestination: {res_destination}\nTravelers: {res_travelers}\nDates: {res_dates}\nItinerary Context:\n{result.get('itinerary','')[:1000]}"
                        if search_tool:
                            search_res = search_tool.invoke(f"{res_destination} {user_query}")
                            search_info = "\n".join(r.get('content', '') for r in search_res) if isinstance(search_res, list) else str(search_res)
                        else:
                            search_info = "Search tool unavailable."
                        prompt = f"Context:\n{chat_context}\nWeb Info:\n{search_info}\nUser Question: {user_query}\nAnswer helpfully as a travel expert."
                        if llm:
                            answer_resp = llm.invoke([HumanMessage(content=prompt)])
                            answer_text = answer_resp.content if isinstance(answer_resp.content, str) else str(answer_resp.content)
                        else:
                            answer_text = f"I am ready to help answer questions about your trip to {res_destination}!"
                        st.markdown(answer_text)
                        st.session_state.chat_messages.append({"role": "assistant", "content": answer_text})
                    except Exception as e:
                        st.error(f"Failed to generate answer: {e}")

    with tab_advanced:
        with st.expander("⚖️ Quality Verdict (Agent-as-Judge)", expanded=True):
            st.markdown(result.get("judge_verdict", "N/A"))

        with st.expander("📜 Session Execution & Real-Time Agent Logs", expanded=True):
            st.markdown(f'<div class="log-box">{logs_content}</div>', unsafe_allow_html=True)
            st.download_button(
                label="📥 Download System Debug Log (.log)",
                data=logs_content.encode("utf-8"),
                file_name="travel_buddy_debug.log",
                mime="text/plain",
                use_container_width=True,
                key="dl_debug_log_plan_view"
            )

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📥 Download Complete Recommendations Report")

    if res_persona == "custom" and res_custom_profile:
        p_name = res_custom_profile.get("label", "Custom Persona")
    else:
        p_name = PERSONA_PROFILES.get(res_persona, PERSONA_PROFILES["couple"])["label"]

    file_content = build_recommendations_text(
        result, res_destination, res_budget, res_dates, p_name, no_budget=res_no_budget, currency="SGD"
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_dest = sanitize_filename(res_destination).replace(" ", "_").lower()
    filename = f"travel_buddy_{safe_dest}_{timestamp}.txt"

    st.download_button(
        label=f"💾 Download Full Text Report ({filename})",
        data=file_content,
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
        key="dl_full_report_plan_view"
    )
