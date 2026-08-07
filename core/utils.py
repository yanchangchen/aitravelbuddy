"""Utility functions for the Travel Buddy agent system."""

import re
import json
import urllib.parse
import urllib.request
from datetime import datetime
import pandas as pd


def ensure_str(content):
    """Safely convert LLM response content to a string.

    Some LangChain model wrappers return content as a list of
    content-part dicts instead of a plain string. This normalizes it.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
            else:
                parts.append(str(part))
        return "\n".join(parts)
    return str(content)


def extract_cost(text: str, label: str) -> float:
    """Extract a numeric amount following a specific label pattern.

    Searches for patterns like SIGHTSEEING_TOTAL_SGD: 450 or AIRFARE_TOTAL_SGD: 800.
    Falls back to scanning for dollar/SGD amounts if label not found.
    """
    if isinstance(text, list):
        text = "\n".join(str(item) for item in text)
    if not isinstance(text, str):
        text = str(text)

    label_stem = label.replace("_SGD", "").replace("_USD", "")
    pattern = rf"(?:{label}|{label_stem}_SGD|{label_stem}_USD):\s*(?:S\$|\$)?\s*([\d,]+\.?\d*)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return float(match.group(1).replace(",", ""))

    amounts = re.findall(r"(?:S\$|\$)\s*([\d,]+\.?\d*)", text)
    if amounts:
        return float(amounts[-1].replace(",", ""))

    return 0.0


def geocode_location(location_name: str):
    """Geocode a location string to (lat, lon) tuple using OpenStreetMap Nominatim."""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(location_name)}&format=json&limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'TravelBuddyStreamlit/1.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        pass
    return None


CITY_COORDINATES = {
    "tokyo": (35.6762, 139.6503),
    "kyoto": (35.0116, 135.7681),
    "banff": (51.1784, -115.5708),
    "lake louise": (51.4254, -116.1773),
    "zermatt": (46.0207, 7.7491),
    "matterhorn": (45.9763, 7.6586),
    "sapporo": (43.0618, 141.3545),
    "hokkaido": (43.0618, 141.3545),
    "zurich": (47.3769, 8.5417),
    "interlaken": (46.6863, 7.8632),
    "switzerland": (46.8182, 8.2275),
    "chengdu": (30.5728, 104.0668),
    "qingdao": (36.0671, 120.3826),
    "beijing": (39.9042, 116.4074),
    "shanghai": (31.2304, 121.4737),
    "bali": (-8.4095, 115.1889),
    "singapore": (1.3521, 103.8198),
    "paris": (48.8566, 2.3522),
    "london": (51.5074, -0.1278),
    "seoul": (37.5665, 126.9780),
    "reykjavik": (64.1466, -21.9426),
    "iceland": (64.1466, -21.9426),
    "amsterdam": (52.3676, 4.9041),
}


def get_city_fallback_coords(destination: str) -> tuple:
    """Get fallback (lat, lon) for major destinations if Nominatim geocoding times out."""
    clean = destination.lower()
    for key, coords in CITY_COORDINATES.items():
        if key in clean:
            return coords
    return (35.6762, 139.6503)


def clean_venue_name(name: str) -> str:
    """Strip action verbs (e.g. Visit, Explore) from venue names before geocoding."""
    cleaned = re.sub(r"[*_#]", "", name).strip()
    action_verbs = [
        r"^visit\s+", r"^explore\s+", r"^head\s+to\s+", r"^discover\s+",
        r"^walk\s+around\s+", r"^walk\s+through\s+", r"^tour\s+", r"^enjoy\s+",
        r"^check\s+in\s+at\s+", r"^check-in\s+at\s+", r"^shop\s+at\s+", r"^dine\s+at\s+"
    ]
    for pattern in action_verbs:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned


def extract_all_plan_locations(result_input, destination: str) -> list:
    """Extract day-by-day sightseeing venues, hotels, and dining locations from agent plan outputs and geocode them."""
    if isinstance(result_input, dict):
        itinerary_text = result_input.get("itinerary", "")
        hotel_text = result_input.get("hotel_recommendations", "")
        food_text = result_input.get("food_and_retail", "")
    else:
        itinerary_text = str(result_input)
        hotel_text = ""
        food_text = ""

    locations = []
    seen_venues = set()

    # Geocode base city center coords
    base_coords = geocode_location(destination) or get_city_fallback_coords(destination)

    # 1. Parse Day-by-Day Sightseeing Itinerary
    current_day = "Day 1"
    lines = itinerary_text.split("\n")
    for line in lines:
        line_str = line.strip()
        day_match = re.match(r"^(?:##|###|\*\*)\s*(Day\s*\d+)", line_str, re.IGNORECASE)
        if day_match:
            current_day = day_match.group(1).strip()
            continue

        activity_match = re.match(r"^[-*]\s*\*\*(.*?)\*\*:?\s*(.*)", line_str)
        if activity_match:
            detail = activity_match.group(2).strip()
            clean_detail = re.sub(r"—\s*Est\.\s*cost:.*", "", detail, flags=re.IGNORECASE).strip()
            parts = re.split(r"—|–|\(|\)", clean_detail)
            raw_venue = parts[0].strip() if parts else clean_detail

            sub_venues = [v.strip() for v in re.split(r"&| and ", raw_venue) if v.strip()]

            for venue in sub_venues:
                v_clean = clean_venue_name(venue)
                if len(v_clean) > 2 and not v_clean.lower().startswith("daily transport") and v_clean.lower() not in seen_venues:
                    seen_venues.add(v_clean.lower())
                    coords = geocode_location(f"{v_clean}, {destination}") or geocode_location(v_clean)
                    is_geocoded = coords is not None

                    if not coords:
                        offset_lat = (hash(v_clean) % 1000 - 500) * 0.00003
                        offset_lon = (hash(v_clean + "lon") % 1000 - 500) * 0.00003
                        coords = (base_coords[0] + offset_lat, base_coords[1] + offset_lon)

                    locations.append({
                        "category": "Sightseeing",
                        "day": current_day,
                        "title": v_clean,
                        "name": v_clean,
                        "query": f"{v_clean}, {destination}",
                        "lat": coords[0],
                        "lng": coords[1],
                        "lon": coords[1],
                        "geocoded": is_geocoded,
                        "color": [255, 75, 75, 220],
                        "google_maps_url": f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(v_clean + ', ' + destination)}"
                    })

    # 2. Parse Hotels
    if hotel_text:
        hotel_lines = hotel_text.split("\n")
        for line in hotel_lines:
            line_str = line.strip()
            hotel_match = re.match(r"^[-*]\s*\*\*(.*?)\*\*:?\s*(.*)", line_str)
            if hotel_match:
                h_name = hotel_match.group(1).strip()
                h_clean = re.sub(r"[*_#]", "", h_name).strip()
                if len(h_clean) > 3 and any(kw in h_clean.lower() for kw in ["hotel", "resort", "ryokan", "inn", "stay", "suite", "lodge"]):
                    if h_clean.lower() not in seen_venues:
                        seen_venues.add(h_clean.lower())
                        coords = geocode_location(f"{h_clean}, {destination}") or geocode_location(h_clean)
                        is_geocoded = coords is not None

                        if not coords:
                            offset_lat = (hash(h_clean) % 1000 - 500) * 0.00003
                            offset_lon = (hash(h_clean + "lon") % 1000 - 500) * 0.00003
                            coords = (base_coords[0] + offset_lat, base_coords[1] + offset_lon)

                        locations.append({
                            "category": "Hotel",
                            "day": "Hotel",
                            "title": h_clean,
                            "query": f"{h_clean}, {destination}",
                            "lat": coords[0],
                            "lon": coords[1],
                            "geocoded": is_geocoded,
                            "color": [50, 130, 246, 220],
                        })

    # 3. Parse Dining & Food
    if food_text:
        food_lines = food_text.split("\n")
        for line in food_lines:
            line_str = line.strip()
            food_match = re.match(r"^[-*]\s*\*\*(.*?)\*\*:?\s*(.*)", line_str)
            if food_match:
                f_name = food_match.group(1).strip()
                f_clean = re.sub(r"[*_#]", "", f_name).strip()
                if len(f_clean) > 3 and f_clean.lower() not in seen_venues:
                    if any(kw in f_clean.lower() for kw in ["restaurant", "cafe", "bistro", "ramen", "market", "tofu", "food", "dining", "grill", "tea", "house", "bar", "noodle"]):
                        seen_venues.add(f_clean.lower())
                        coords = geocode_location(f"{f_clean}, {destination}") or geocode_location(f_clean)
                        is_geocoded = coords is not None

                        if not coords:
                            offset_lat = (hash(f_clean) % 1000 - 500) * 0.00003
                            offset_lon = (hash(f_clean + "lon") % 1000 - 500) * 0.00003
                            coords = (base_coords[0] + offset_lat, base_coords[1] + offset_lon)

                        locations.append({
                            "category": "Dining & Retail",
                            "day": "Dining",
                            "title": f_clean,
                            "query": f"{f_clean}, {destination}",
                            "lat": coords[0],
                            "lon": coords[1],
                            "geocoded": is_geocoded,
                            "color": [255, 165, 0, 220],
                        })

    # Fallback to destination city center if empty
    if not locations:
        locations.append({
            "category": "City Center",
            "day": "Day 1",
            "title": destination,
            "query": destination,
            "lat": base_coords[0],
            "lon": base_coords[1],
            "geocoded": True,
            "color": [255, 75, 75, 220],
        })

    return locations


def extract_all_itinerary_locations(itinerary_text: str, destination: str) -> list:
    """Backward compatible wrapper for extract_all_plan_locations."""
    return extract_all_plan_locations(itinerary_text, destination)


def get_persona_context(state: dict, persona_profiles: dict) -> str:
    """Build persona-aware context string for injection into agent prompts."""
    persona_key = state["persona"].lower().strip()
    if persona_key == "custom" and "custom_persona_profile" in state and isinstance(state["custom_persona_profile"], dict):
        profile = state["custom_persona_profile"]
    else:
        profile = persona_profiles.get(persona_key, persona_profiles["couple"])

    currency = state.get("currency", "SGD")
    no_budget = state.get("no_budget", False)
    budget_desc = "Unlimited / Flexible" if no_budget else f"S$ {state['budget']:,.2f} {currency}"
    origin = state.get("origin", "Singapore")
    travelers = state.get("travelers_summary", "2 Adults, 1 Child (>2 yrs)")
    self_drive = "YES (Car Rental)" if state.get("self_drive", False) else "NO (Public Transport/Taxi)"

    base_context = (
        f"Traveler Persona: {profile.get('label', 'Custom Persona')}\n"
        f"Group Composition: {travelers}\n"
        f"Origin City: {origin}\n"
        f"Pacing Tempo: {profile.get('tempo', 'medium')}\n"
        f"Mobility Preference: {profile.get('mobility', 'balanced')}\n"
        f"Self-Drive Option: {self_drive}\n"
        f"Dining Style: {profile.get('dining_style', 'varied')}\n"
        f"Accommodation Preference: {profile.get('accommodation', 'comfortable')}\n"
        f"Trip Budget Constraint: {budget_desc}\n"
        f"\nMANDATORY PERSONA RULES (you MUST follow all of these):\n"
        f"{profile.get('rules', 'Follow traveler preferences strictly.')}"
    )

    preferences = state.get("user_preferences")
    if preferences:
        from .profile import format_preferences_context
        pref_text = format_preferences_context(preferences)
        if pref_text:
            base_context += f"\n\n{pref_text}"

    return base_context


def get_critique_context(state: dict) -> str:
    """Format any previous budget critiques for refinement guidance."""
    history = state.get("critique_history", [])
    if not history:
        return ""
    formatted = "\n".join(f"  - Attempt {i+1}: {c}" for i, c in enumerate(history))
    return (
        f"\n\n\u26a0\ufe0f PREVIOUS BUDGET CRITIQUES (you MUST address these):\n{formatted}\n"
        f"Adjust your cost estimates to land within 80-90% of the total budget.\n"
    )


def sanitize_filename(name: str) -> str:
    """Remove characters unsafe for filenames."""
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name).strip()


def parse_itinerary_to_dataframe(itinerary_text: str, purchasing_guide_text: str = "") -> pd.DataFrame:
    """Parse day-by-day markdown itinerary and purchasing guide into a structured tabular pandas DataFrame."""
    rows = []
    current_day = "Day 1"
    current_theme = "Sightseeing"

    if purchasing_guide_text:
        airfare_cost = extract_cost(purchasing_guide_text, "AIRFARE_TOTAL_SGD")
        if airfare_cost > 0:
            rows.append({
                "Day": "Pre-Trip",
                "Theme": "Transport & Flight",
                "Time Slot": "Departure Flight",
                "Activity Details": "Round-trip Airfare (Flights for Group)",
                "Est. Cost (SGD)": airfare_cost,
            })
        car_rental_cost = extract_cost(purchasing_guide_text, "CAR_RENTAL_TOTAL_SGD")
        if car_rental_cost > 0:
            rows.append({
                "Day": "Pre-Trip",
                "Theme": "Transport & Car Rental",
                "Time Slot": "Self-Drive Rental",
                "Activity Details": "5-Day Car Rental & Tolls",
                "Est. Cost (SGD)": car_rental_cost,
            })

    lines = itinerary_text.split("\n")
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        day_match = re.match(r"^##\s*(Day\s*\d+)[\s:]*(.*)", line_str, re.IGNORECASE)
        if day_match:
            current_day = day_match.group(1).strip()
            current_theme = day_match.group(2).strip() or "Sightseeing"
            continue

        activity_match = re.match(r"^[-*]\s*\*\*(.*?)\*\*:?\s*(.*)", line_str)
        if activity_match:
            time_slot = activity_match.group(1).strip()
            detail = activity_match.group(2).strip()

            cost = 0.0
            cost_match = re.search(r"Est\.\s*cost:\s*(?:S\$|\$)?\s*([\d,]+\.?\d*)", detail, re.IGNORECASE)
            if cost_match:
                cost = float(cost_match.group(1).replace(",", ""))
                detail = re.sub(r"—\s*Est\.\s*cost:.*", "", detail, flags=re.IGNORECASE).strip()

            rows.append({
                "Day": current_day,
                "Theme": current_theme,
                "Time Slot": time_slot,
                "Activity Details": detail,
                "Est. Cost (SGD)": cost,
            })
        elif line_str.startswith("- Daily transport:") or line_str.startswith("* Daily transport:"):
            cost_match = re.search(r"(?:S\$|\$)\s*([\d,]+\.?\d*)", line_str)
            cost = float(cost_match.group(1).replace(",", "")) if cost_match else 0.0
            rows.append({
                "Day": current_day,
                "Theme": current_theme,
                "Time Slot": "Transport",
                "Activity Details": "Daily transport (Local transit / taxi / tolls)",
                "Est. Cost (SGD)": cost,
            })

    if not rows:
        rows.append({
            "Day": "Day 1",
            "Theme": "Overview",
            "Time Slot": "All Day",
            "Activity Details": itinerary_text[:500],
            "Est. Cost (SGD)": 0.0,
        })

    return pd.DataFrame(rows)


def build_recommendations_text(result: dict, destination: str, budget: float,
                                dates: str, persona_label: str, no_budget: bool = False,
                                currency: str = "SGD") -> str:
    """Build the full text file content for travel recommendations."""
    status = result.get("status", "unknown")
    origin = result.get("origin", "Singapore")
    travelers = result.get("travelers_summary", "2 Adults, 1 Child (>2 yrs)")
    self_drive = "YES (Car Rental)" if result.get("self_drive", False) else "NO"
    budget_str = "Flexible / Unlimited" if no_budget else f"S$ {budget:,.2f} {currency}"

    lines = []
    lines.append("=" * 70)
    lines.append("  TRAVEL BUDDY -- TRAVEL RECOMMENDATIONS")
    lines.append("=" * 70)
    lines.append(f"  Generated:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  Origin:       {origin}")
    lines.append(f"  Destination:  {destination}")
    lines.append(f"  Travelers:    {travelers}")
    lines.append(f"  Self-Drive:   {self_drive}")
    lines.append(f"  Budget:       {budget_str}")
    lines.append(f"  Dates:        {dates}")
    lines.append(f"  Persona:      {persona_label}")
    lines.append(f"  Status:       {status.upper()}")
    lines.append("=" * 70)

    if status == "approved":
        for section_title, key in [
            ("ITINERARY & SIGHTSEEING", "itinerary"),
            ("FOOD & RETAIL GUIDE", "food_and_retail"),
            ("ACCOMMODATION", "hotel_recommendations"),
            ("BOOKING & PURCHASING GUIDE", "purchasing_guide"),
            ("BUDGET BREAKDOWN", "budget_breakdown"),
            ("QUALITY VERDICT (Agent-as-Judge)", "judge_verdict"),
        ]:
            lines.append("")
            lines.append("=" * 70)
            lines.append(f"  {section_title}")
            lines.append("=" * 70)
            lines.append(result.get(key, "N/A"))
    elif status == "budget_busted":
        lines.append("")
        lines.append("=" * 70)
        lines.append("  BUDGET RECONCILIATION FAILED")
        lines.append("=" * 70)
        lines.append(result.get("budget_breakdown", "N/A"))
        if result.get("itinerary"):
            lines.append("")
            lines.append("-" * 70)
            lines.append("  LAST ATTEMPTED ITINERARY (not approved)")
            lines.append("-" * 70)
            lines.append(result.get("itinerary", ""))
    else:
        lines.append("")
        lines.append(f"  Unexpected status: {status}")

    lines.append("")
    lines.append("=" * 70)
    lines.append("  END OF TRAVEL RECOMMENDATIONS")
    lines.append("=" * 70)
    return "\n".join(lines)
