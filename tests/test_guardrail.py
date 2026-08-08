"""Unit tests for budget guardrail evaluation logic in Travel Buddy."""

from core.evaluation import quality_agent
from unittest.mock import MagicMock
import core.evaluation as eval_mod
import unittest


class TestGuardrail(unittest.TestCase):

    def setUp(self):
        self.mock_llm = MagicMock()
        eval_mod._llm = self.mock_llm
        # Default LLM response allows passing if budget passes
        self.mock_llm.invoke.return_value = MagicMock(content="VERDICT: PASS\nSCORE: 9\nSURGICAL SUGGESTIONS: None.")

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
        result = quality_agent(state)
        self.assertEqual(result["status"], "approved")
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
        result = quality_agent(state)
        self.assertEqual(result["status"], "approved")
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
        result = quality_agent(state)
        self.assertEqual(result["status"], "planning")
        self.assertEqual(result["budget_attempts"], 1)
        self.assertEqual(len(result["critique_history"]), 1)
        self.assertIn("Score", result["critique_history"][0])

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
        result = quality_agent(state)
        self.assertEqual(result["status"], "quality_failed")
        self.assertEqual(result["budget_attempts"], 3)


if __name__ == "__main__":
    import unittest
    unittest.main()
