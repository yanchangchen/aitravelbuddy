"""Unit tests for user profile and travel persona JSON persistence."""

import os
import unittest
import tempfile
from core.profile import (
    load_user_profile,
    save_user_profile,
    format_preferences_context,
    get_default_profile,
)
from core.utils import get_persona_context
from core.personas import PERSONA_PROFILES


class TestProfilePersistence(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_json_path = os.path.join(self.temp_dir.name, "test_user_profile.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_profile(self):
        profile = get_default_profile()
        self.assertIn("saved_persona", profile)
        self.assertIn("preferences", profile)
        self.assertIn("updated_at", profile)
        self.assertEqual(profile["saved_persona"]["key"], "custom")

    def test_load_non_existent_file(self):
        profile = load_user_profile(self.test_json_path)
        self.assertIn("saved_persona", profile)
        self.assertIn("preferences", profile)

    def test_save_and_load_user_profile(self):
        custom_data = {
            "saved_persona": {
                "key": "custom",
                "label": "🎨 Gourmet Photography Explorer",
                "tempo": "medium",
                "mobility": "high walking",
                "dining_style": "Michelin guide & local street markets",
                "accommodation": "Boutique design hotels",
                "rules": "1. Focus on scenic viewpoints.\n2. Must include food tours.",
            },
            "preferences": {
                "dietary": ["Halal", "Seafood"],
                "accommodation_pref": "Boutique & Quiet",
                "travel_pace": "Balanced",
                "interests": ["Culture & History", "Food & Culinary"],
                "custom_instructions": "Require coffee shops near hotel and quiet nights.",
            },
        }

        save_success = save_user_profile(custom_data, self.test_json_path)
        self.assertTrue(save_success)
        self.assertTrue(os.path.exists(self.test_json_path))

        loaded_profile = load_user_profile(self.test_json_path)
        self.assertEqual(
            loaded_profile["saved_persona"]["label"],
            "🎨 Gourmet Photography Explorer",
        )
        self.assertIn("Halal", loaded_profile["preferences"]["dietary"])
        self.assertIn("Seafood", loaded_profile["preferences"]["dietary"])
        self.assertEqual(
            loaded_profile["preferences"]["custom_instructions"],
            "Require coffee shops near hotel and quiet nights.",
        )

    def test_format_preferences_context(self):
        prefs = {
            "dietary": ["Vegetarian", "Gluten-Free"],
            "accommodation_pref": "Luxury Resort",
            "travel_pace": "Relaxed",
            "interests": ["Wellness & Spa", "Nature & Outdoors"],
            "custom_instructions": "Must have elevator and wheelchair accessibility.",
        }

        formatted = format_preferences_context(prefs)
        self.assertIn("USER EXPLICIT PREFERENCES", formatted)
        self.assertIn("Vegetarian, Gluten-Free", formatted)
        self.assertIn("Luxury Resort", formatted)
        self.assertIn("Relaxed", formatted)
        self.assertIn("Wellness & Spa, Nature & Outdoors", formatted)
        self.assertIn("Must have elevator and wheelchair accessibility.", formatted)

    def test_get_persona_context_integration(self):
        state = {
            "persona": "custom",
            "custom_persona_profile": {
                "label": "🎨 Custom Persona",
                "tempo": "medium",
                "mobility": "balanced",
                "dining_style": "varied",
                "accommodation": "comfortable",
                "rules": "1. Test custom rule",
            },
            "budget": 3000.0,
            "currency": "SGD",
            "no_budget": False,
            "origin": "Singapore",
            "travelers_summary": "2 Adults",
            "user_preferences": {
                "dietary": ["Halal"],
                "accommodation_pref": "Boutique & Quiet",
                "travel_pace": "Balanced",
                "interests": ["Culture & History"],
                "custom_instructions": "Early morning coffee required.",
            },
        }

        context = get_persona_context(state, PERSONA_PROFILES)
        self.assertIn("Traveler Persona: 🎨 Custom Persona", context)
        self.assertIn("USER EXPLICIT PREFERENCES", context)
        self.assertIn("Dietary Preferences: Halal", context)
        self.assertIn("Early morning coffee required.", context)

    def test_corrupted_json_file(self):
        with open(self.test_json_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json format... }")

        profile = load_user_profile(self.test_json_path)
        self.assertIn("saved_persona", profile)
        self.assertIn("preferences", profile)


if __name__ == "__main__":
    unittest.main()
