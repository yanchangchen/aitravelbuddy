"""Utility functions for the Travel Buddy agent system."""

import re
from datetime import datetime


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
    """Extract a dollar amount following a specific label pattern.

    Searches for patterns like SIGHTSEEING_TOTAL_USD: 450.
    Falls back to scanning for the last dollar amount if label not found.
    """
    if isinstance(text, list):
        text = "\n".join(str(item) for item in text)
    if not isinstance(text, str):
        text = str(text)
    pattern = label + r":\s*\$?([\d,]+\.?\d*)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return float(match.group(1).replace(",", ""))
    dollar_amounts = re.findall(r"\$([\d,]+\.?\d*)", text)
    if dollar_amounts:
        return float(dollar_amounts[-1].replace(",", ""))
    return 0.0


def get_persona_context(state: dict, persona_profiles: dict) -> str:
    """Build persona-aware context string for injection into agent prompts."""
    persona_key = state["persona"].lower().strip()
    profile = persona_profiles.get(persona_key, persona_profiles["couple"])
    return (
        f"Traveler Persona: {profile['label']}\n"
        f"Pacing Tempo: {profile['tempo']}\n"
        f"Mobility Preference: {profile['mobility']}\n"
        f"Dining Style: {profile['dining_style']}\n"
        f"Accommodation Preference: {profile['accommodation']}\n"
        f"\nMANDATORY PERSONA RULES (you MUST follow all of these):\n"
        f"{profile['rules']}"
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


def build_recommendations_text(result: dict, destination: str, budget: float,
                                dates: str, persona_label: str) -> str:
    """Build the full text file content for travel recommendations."""
    status = result.get("status", "unknown")
    lines = []
    lines.append("=" * 70)
    lines.append("  TRAVEL BUDDY -- TRAVEL RECOMMENDATIONS")
    lines.append("=" * 70)
    lines.append(f"  Generated:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  Destination:  {destination}")
    lines.append(f"  Budget:       ${budget:,.2f} USD")
    lines.append(f"  Dates:        {dates}")
    lines.append(f"  Persona:      {persona_label}")
    lines.append(f"  Status:       {status.upper()}")
    lines.append("=" * 70)

    if status == "approved":
        for section_title, key in [
            ("ITINERARY & SIGHTSEEING", "itinerary"),
            ("FOOD & RETAIL GUIDE", "food_and_retail"),
            ("ACCOMMODATION", "hotel_recommendations"),
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
