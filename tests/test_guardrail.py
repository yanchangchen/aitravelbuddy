"""Unit tests for budget guardrail evaluation logic in Travel Buddy."""

import unittest
from core.evaluation import budget_guardrail


class TestGuardrail(unittest.TestCase):

    def test_budget_guardrail_no_budget_mode(self):
        state = {
            "budget": 0.0,
            "no_budget": True,
            "budget_attempts": 0,
            "itinerary": "SIGHTSEEING_TOTAL_SGD: 500",
            "food_and_retail": "FOOD_RETAIL_TOTAL_SGD: 600",
            "hotel_recommendations": "HOTEL_TOTAL_SGD: 1000",
            "purchasing_guide": "AIRFARE_TOTAL_SGD: 800\nCAR_RENTAL_TOTAL_SGD: 0",
        }
        result = budget_guardrail(state)
        self.assertEqual(result["status"], "budget_passed")
        self.assertIn("FLEXIBLE / UNLIMITED BUDGET", result["budget_breakdown"])

    def test_budget_guardrail_passed_within_range(self):
        # Budget = 3000. Target range: 80% (2400) to 90% (2700)
        state = {
            "budget": 3000.0,
            "no_budget": False,
            "budget_attempts": 0,
            "itinerary": "SIGHTSEEING_TOTAL_SGD: 500",
            "food_and_retail": "FOOD_RETAIL_TOTAL_SGD: 600",
            "hotel_recommendations": "HOTEL_TOTAL_SGD: 600",
            "purchasing_guide": "AIRFARE_TOTAL_SGD: 800\nCAR_RENTAL_TOTAL_SGD: 0", # Total = 2500
        }
        result = budget_guardrail(state)
        self.assertEqual(result["status"], "budget_passed")
        self.assertEqual(result["budget_attempts"], 1)

    def test_budget_guardrail_retry_when_under_budget(self):
        # Budget = 3000. Target range: 2400 to 2700. Total = 1000 (too low)
        state = {
            "budget": 3000.0,
            "no_budget": False,
            "budget_attempts": 0,
            "itinerary": "SIGHTSEEING_TOTAL_SGD: 200",
            "food_and_retail": "FOOD_RETAIL_TOTAL_SGD: 200",
            "hotel_recommendations": "HOTEL_TOTAL_SGD: 300",
            "purchasing_guide": "AIRFARE_TOTAL_SGD: 300",
        }
        result = budget_guardrail(state)
        self.assertEqual(result["status"], "planning")
        self.assertEqual(result["budget_attempts"], 1)
        self.assertEqual(len(result["critique_history"]), 1)
        self.assertIn("TOO LOW", result["critique_history"][0])

    def test_budget_guardrail_busted_after_3_attempts(self):
        state = {
            "budget": 3000.0,
            "no_budget": False,
            "budget_attempts": 2,  # Already at attempt 2 -> 3rd attempt
            "itinerary": "SIGHTSEEING_TOTAL_SGD: 2000",
            "food_and_retail": "FOOD_RETAIL_TOTAL_SGD: 2000",
            "hotel_recommendations": "HOTEL_TOTAL_SGD: 2000",
            "purchasing_guide": "AIRFARE_TOTAL_SGD: 2000",
        }
        result = budget_guardrail(state)
        self.assertEqual(result["status"], "budget_busted")
        self.assertEqual(result["budget_attempts"], 3)


if __name__ == "__main__":
    unittest.main()
