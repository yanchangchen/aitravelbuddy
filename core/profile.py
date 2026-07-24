"""Module for user profile and travel persona persistence and preference formatting."""

import os
import json
from datetime import datetime
from .logger import get_logger

logger = get_logger("profile")

DEFAULT_PROFILE_FILE = "user_profile.json"

DEFAULT_SAVED_PERSONA = {
    "key": "custom",
    "label": "🧑 Custom Traveler Profile",
    "tempo": "medium",
    "mobility": "balanced — walking & public transit",
    "dining_style": "mix of local hidden gems & curated dining",
    "accommodation": "comfortable boutique or 4-star hotels",
    "rules": (
        "1. Balance major highlights with relaxed exploration.\n"
        "2. Ensure easy access to local transport or walkable neighborhoods.\n"
        "3. Emphasize authentic local experiences and high-quality food."
    ),
}

DEFAULT_USER_PREFERENCES = {
    "dietary": ["Local Delicacies"],
    "accommodation_pref": "Boutique & Quiet",
    "travel_pace": "Balanced",
    "interests": ["Culture & History", "Food & Culinary"],
    "custom_instructions": "",
}


def get_default_profile() -> dict:
    """Return a fresh default profile dictionary."""
    return {
        "saved_persona": dict(DEFAULT_SAVED_PERSONA),
        "preferences": dict(DEFAULT_USER_PREFERENCES),
        "updated_at": datetime.now().isoformat(),
    }


def load_user_profile(file_path: str = DEFAULT_PROFILE_FILE) -> dict:
    """Load the saved user persona and preferences from a JSON file.

    Returns default profile if file does not exist or is corrupted.
    """
    if not os.path.exists(file_path):
        logger.info(f"Profile file '{file_path}' not found. Returning default profile.")
        return get_default_profile()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        profile = get_default_profile()

        if "saved_persona" in data and isinstance(data["saved_persona"], dict):
            profile["saved_persona"].update(data["saved_persona"])

        if "preferences" in data and isinstance(data["preferences"], dict):
            profile["preferences"].update(data["preferences"])

        if "updated_at" in data:
            profile["updated_at"] = data["updated_at"]

        logger.info(f"User profile successfully loaded from '{file_path}'.")
        return profile
    except Exception as e:
        logger.error(f"Failed to load user profile from '{file_path}': {e}. Falling back to defaults.")
        return get_default_profile()


def save_user_profile(profile_data: dict, file_path: str = DEFAULT_PROFILE_FILE) -> bool:
    """Save the user persona and preferences dictionary safely to a JSON file.

    Returns True on success, False on failure.
    """
    try:
        data_to_save = {
            "saved_persona": profile_data.get("saved_persona", DEFAULT_SAVED_PERSONA),
            "preferences": profile_data.get("preferences", DEFAULT_USER_PREFERENCES),
            "updated_at": datetime.now().isoformat(),
        }

        temp_path = f"{file_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)

        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(temp_path, file_path)

        logger.info(f"User profile successfully saved to '{file_path}'.")
        return True
    except Exception as e:
        logger.error(f"Failed to save user profile to '{file_path}': {e}")
        if os.path.exists(f"{file_path}.tmp"):
            try:
                os.remove(f"{file_path}.tmp")
            except Exception:
                pass
        return False


def format_preferences_context(preferences: dict) -> str:
    """Format user preferences dictionary into a concise markdown context string for LLM prompts."""
    if not preferences or not isinstance(preferences, dict):
        return ""

    lines = ["--- USER EXPLICIT PREFERENCES ---"]

    dietary = preferences.get("dietary", [])
    if isinstance(dietary, list) and dietary:
        lines.append(f"• Dietary Preferences: {', '.join(dietary)}")
    elif isinstance(dietary, str) and dietary.strip():
        lines.append(f"• Dietary Preferences: {dietary.strip()}")

    accom = preferences.get("accommodation_pref", "")
    if accom:
        lines.append(f"• Preferred Accommodation Style: {accom}")

    pace = preferences.get("travel_pace", "")
    if pace:
        lines.append(f"• Preferred Travel Pace: {pace}")

    interests = preferences.get("interests", [])
    if isinstance(interests, list) and interests:
        lines.append(f"• Top Travel Interests: {', '.join(interests)}")
    elif isinstance(interests, str) and interests.strip():
        lines.append(f"• Top Travel Interests: {interests.strip()}")

    notes = preferences.get("custom_instructions", "")
    if notes and notes.strip():
        lines.append(f"• Special Directives & Needs: {notes.strip()}")

    lines.append("---------------------------------")
    return "\n".join(lines) if len(lines) > 2 else ""
