"""Unit test for strict separation between Trip Logistics & Persona Preferences."""

import os
import unittest
from core.profile import save_user_profile, load_user_profile, DEFAULT_PROFILE_FILE


class TestPersonaIsolation(unittest.TestCase):
    TEST_PROFILE_FILE = "test_user_profile_isolation.json"

    def tearDown(self):
        """Clean up temporary test profile file."""
        if os.path.exists(self.TEST_PROFILE_FILE):
            os.remove(self.TEST_PROFILE_FILE)

    def test_save_user_profile_strips_trip_specific_fields(self):
        """Verify saving a persona profile strips out destination, origin, dates, and budget."""
        dirty_profile_data = {
            "saved_persona": {
                "key": "custom",
                "label": "⭐ Gilly Ally Yan",
                "tempo": "relaxed",
                "mobility": "walking & private cars",
                "dining_style": "Michelin & local gems",
                "accommodation": "5-star luxury",
                "rules": "1. Morning matcha tea.",
                # Accidental trip-specific fields passed in:
                "destination": "Tokyo, Japan",
                "origin": "Singapore",
                "budget": 5000.0,
                "self_drive": True,
            },
            "preferences": {
                "dietary": ["Local Delicacies"],
                "accommodation_pref": "Luxury Resort",
                "travel_pace": "Relaxed",
                "interests": ["Culture & History"],
                "custom_instructions": "Quiet rooms",
            },
        }

        success = save_user_profile(dirty_profile_data, file_path=self.TEST_PROFILE_FILE)
        self.assertTrue(success)

        # Load back saved profile
        loaded_prof = load_user_profile(file_path=self.TEST_PROFILE_FILE)
        saved_p = loaded_prof["saved_persona"]

        # Verify persona attributes preserved
        self.assertEqual(saved_p["label"], "⭐ Gilly Ally Yan")
        self.assertEqual(saved_p["tempo"], "relaxed")

        # Verify trip-specific fields were STRIPPED out cleanly!
        self.assertNotIn("destination", saved_p, "Destination MUST NOT be saved inside reusable persona profile!")
        self.assertNotIn("origin", saved_p, "Origin MUST NOT be saved inside reusable persona profile!")
        self.assertNotIn("budget", saved_p, "Budget MUST NOT be saved inside reusable persona profile!")
        self.assertNotIn("self_drive", saved_p, "Self-drive choice MUST NOT be saved inside reusable persona profile!")

        print("\n[Test Isolation] Verified persona profile successfully strips out trip-specific fields!")


if __name__ == "__main__":
    unittest.main()
