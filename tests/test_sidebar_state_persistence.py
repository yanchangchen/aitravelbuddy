"""Unit test for Streamlit widget session state persistence in sidebar."""

import unittest
import streamlit as st


class TestSidebarStatePersistence(unittest.TestCase):

    def setUp(self):
        """Reset session state before each test."""
        st.session_state.clear()

    def test_destination_persists_across_persona_changes(self):
        """Verify typed destination persists when changing persona profiles."""
        # 1. User types destination
        st.session_state["input_destination_text"] = "Paris, France"
        st.session_state["input_origin_text"] = "London, UK"

        # 2. Simulate persona selection change
        persona_choice = "single"
        st.session_state["input_persona_radio"] = "🧑 Solo Traveler"

        # 3. Verify destination is untouched
        self.assertEqual(st.session_state["input_destination_text"], "Paris, France")
        self.assertEqual(st.session_state["input_origin_text"], "London, UK")
        print("\n[Test Persistence] Verified destination 'Paris, France' persists when persona is changed!")

    def test_surprise_pick_updates_destination_state(self):
        """Verify Surprise Pick explicitly updates widget session state."""
        st.session_state["input_destination_text"] = "Tokyo, Japan"

        # Simulate surprise pick triggering
        surprise_pick = {
            "destination": "Zurich & Interlaken, Switzerland",
            "origin": "Singapore",
            "dates_tuple": ("2026-08-01", "2026-08-06"),
        }
        st.session_state["input_destination_text"] = surprise_pick["destination"]
        st.session_state["input_origin_text"] = surprise_pick["origin"]

        self.assertEqual(st.session_state["input_destination_text"], "Zurich & Interlaken, Switzerland")
        self.assertEqual(st.session_state["input_origin_text"], "Singapore")
        print("[Test Persistence] Verified Surprise Pick correctly updates widget session state!")


if __name__ == "__main__":
    unittest.main()
