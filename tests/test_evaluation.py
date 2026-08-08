"""Unit tests for terminal fallback and quality evaluation failure explanations."""

import unittest
from core.evaluation import terminal_fallback, quality_agent
import unittest
from unittest.mock import MagicMock
import core.evaluation as eval_mod


class TestEvaluation(unittest.TestCase):

    def setUp(self):
        self.mock_llm = MagicMock()
        eval_mod._llm = self.mock_llm

    def test_terminal_fallback_preserves_plan_and_provides_reasons(self):
        sample_state = {
            "origin": "Singapore",
            "destination": "Tokyo, Japan",
            "budget": 1000.0,
            "no_budget": False,
            "dates": "Mar 1 - Mar 5, 2026",
            "travelers_summary": "2 Adults",
            "persona": "single",
            "itinerary": "## Day 1: Tokyo Sightseeing...",
            "food_and_retail": "### Food: Ramen stalls...",
            "hotel_recommendations": "### Hotel: Tokyo Budget Inn...",
            "purchasing_guide": "AIRFARE_TOTAL_SGD: 800",
            "judge_verdict": "VERDICT: FAIL\nSCORE: 4/10\nRULE-BY-RULE CHECK:\n1. Pace - FAIL - Too many activities.",
            "critique_history": [
                "Attempt 1: Total S$2800.00 SGD EXCEEDS target limit of S$900.00 SGD.",
                "Attempt 2: Total S$2700.00 SGD EXCEEDS target limit.",
                "Attempt 3: Quality Score was 4/10 (Below Average).",
            ],
        }

        fallback_output = terminal_fallback(sample_state)

        self.assertEqual(fallback_output["status"], "unapproved")
        self.assertIn("quality_failure_reason", fallback_output)

        reason = fallback_output["quality_failure_reason"]
        self.assertIn("PLAN UNAPPROVED", reason)
        self.assertIn("Singapore", reason)
        self.assertIn("Tokyo, Japan", reason)
        self.assertIn("REASON FOR REJECTION", reason)
        self.assertIn("Attempt 1", reason)
        self.assertIn("SCORE: 4/10", reason)
        self.assertIn("HOW TO RELAX CRITERIA", reason)

    def test_quality_agent_score_parsing(self):
        # Mock LLM response with high score
        self.mock_llm.invoke.return_value = MagicMock(content="VERDICT: PASS\nSCORE: 9\nSURGICAL SUGGESTIONS: None.")
        state = {
            "budget": 3000.0,
            "no_budget": True,
            "itinerary": "SIGHTSEEING_TOTAL_SGD: 100",
            "food_and_retail": "FOOD_RETAIL_TOTAL_SGD: 100",
            "hotel_recommendations": "HOTEL_TOTAL_SGD: 100",
            "purchasing_guide": "AIRFARE_TOTAL_SGD: 100",
            "persona": "family",
            "num_days": 5,
        }
        res = quality_agent(state)
        self.assertEqual(res["status"], "approved")

        # Mock LLM response with low score
        self.mock_llm.invoke.return_value = MagicMock(content="VERDICT: FAIL\nSCORE: 5\nSURGICAL SUGGESTIONS: Missing Day 5 details.")
        state["no_budget"] = False
        res = quality_agent(state)
        self.assertEqual(res["status"], "planning")
        self.assertIn("Quality Score 5/10", res["critique_history"][0])


if __name__ == "__main__":
    unittest.main()
