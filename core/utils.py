"""Utility functions for the Travel Buddy agent system."""

import re
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
    self_drive = "YES (Car Rental)" if state.get("self_drive", False) else "NO (Public Transport/Taxi)"

    return (
        f"Traveler Persona: {profile.get('label', 'Custom Persona')}\n"
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

    # Add Airfare & Car Rental rows from purchasing guide if present
    if purchasing_guide_text:
        airfare_cost = extract_cost(purchasing_guide_text, "AIRFARE_TOTAL_SGD")
        if airfare_cost > 0:
            rows.append({
                "Day": "Pre-Trip",
                "Theme": "Transport & Flight",
                "Time Slot": "Departure Flight",
                "Activity Details": "Round-trip Airfare (Flights)",
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
    self_drive = "YES (Car Rental)" if result.get("self_drive", False) else "NO"
    budget_str = "Flexible / Unlimited" if no_budget else f"S$ {budget:,.2f} {currency}"

    lines = []
    lines.append("=" * 70)
    lines.append("  TRAVEL BUDDY -- TRAVEL RECOMMENDATIONS")
    lines.append("=" * 70)
    lines.append(f"  Generated:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  Origin:       {origin}")
    lines.append(f"  Destination:  {destination}")
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
