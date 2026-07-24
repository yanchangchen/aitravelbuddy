"""Unit tests for trip details and agent run state persistence."""

import os
import unittest
from core.db import save_trip_plan, get_saved_trips, get_trip_plan


class TestDBPersistence(unittest.TestCase):

    def test_save_and_load_trip_plan_and_agent_state(self):
        dest = "Kyoto, Japan"
        travelers = "2 Adults, 1 Child (>2 yrs)"
        persona = "👨‍👩‍👧‍👦 Family Adventure"
        dates = "Nov 15 - Nov 20, 2026"

        agent_state = {
            "origin": "Singapore",
            "destination": dest,
            "budget": 4500.0,
            "no_budget": False,
            "num_adults": 2,
            "num_children": 1,
            "num_infants": 0,
            "travelers_summary": travelers,
            "self_drive": True,
            "currency": "SGD",
            "dates": dates,
            "num_days": 6,
            "persona": "family",
            "user_preferences": {
                "dietary": ["Kid-Friendly", "Local Delicacies"],
                "accommodation_pref": "Family Suite",
            },
            "status": "unapproved",
            "judge_verdict": "VERDICT: FAIL\nSCORE: 5/10",
            "quality_failure_reason": "⚠️ PLAN UNAPPROVED — DID NOT PASS QUALITY EVALUATION",
            "budget_attempts": 3,
            "critique_history": ["Attempt 1: Too high"],
            "itinerary": "## Day 1: Arashiyama Bamboo Grove\nSIGHTSEEING_TOTAL_SGD: 300",
            "food_and_retail": "FOOD_RETAIL_TOTAL_SGD: 400",
            "hotel_recommendations": "HOTEL_TOTAL_SGD: 1200",
            "purchasing_guide": "AIRFARE_TOTAL_SGD: 1800\nCAR_RENTAL_TOTAL_SGD: 400",
            "budget_breakdown": "Total cost: S$4100 SGD",
        }

        # Save trip plan and full agent state
        save_success = save_trip_plan(dest, travelers, persona, dates, agent_state)
        self.assertTrue(save_success)

        # Retrieve saved trips list
        trips = get_saved_trips()
        self.assertIsInstance(trips, list)
        self.assertGreater(len(trips), 0)

        # Match saved trip
        saved_entry = next((t for t in trips if t.get("destination") == dest), None)
        self.assertIsNotNone(saved_entry)
        self.assertEqual(saved_entry["travelers"], travelers)
        self.assertEqual(saved_entry["persona"], persona)

        # Fetch full state data using trip id
        trip_id = saved_entry["id"]
        loaded_state = get_trip_plan(trip_id)
        self.assertIsNotNone(loaded_state)
        self.assertEqual(loaded_state["destination"], dest)
        self.assertEqual(loaded_state["status"], "unapproved")
        self.assertIn("quality_failure_reason", loaded_state)
        self.assertEqual(loaded_state["user_preferences"]["accommodation_pref"], "Family Suite")


if __name__ == "__main__":
    unittest.main()
