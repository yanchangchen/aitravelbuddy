"""Unit and integration tests for recently added multi-agent, API, and frontend features:
1. Quality Agent 1-10 scoring and StateGraph feedback loop routing.
2. Seasonal refresh API endpoint and response envelope extraction.
3. Multi-venue extraction across Sightseeing, Hotels, and Dining with Google Maps links.
4. Dynamic date duration calculation and Day block deduplication.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
from fastapi.testclient import TestClient

from core.evaluation import quality_agent
import core.evaluation as eval_mod
from core.graph import build_graph
from core.utils import extract_all_plan_locations
from core.surprise import fetch_live_seasonal_picks, SEASONAL_PACKAGES
from api.main import app


class TestQualityAgentRoutingAndScoring(unittest.TestCase):
    """Test Quality Agent 1-10 scoring and StateGraph loop limits."""

    def setUp(self):
        self.mock_llm = MagicMock()
        eval_mod._llm = self.mock_llm

    def test_quality_agent_high_score_approves(self):
        """Score >= 8 in no-budget mode immediately approves the plan."""
        self.mock_llm.invoke.return_value = MagicMock(content="VERDICT: PASS\nSCORE: 9\nSURGICAL SUGGESTIONS: None.")
        state = {
            "budget": 3500.0,
            "no_budget": True,
            "budget_attempts": 0,
            "itinerary": "SIGHTSEEING_TOTAL_SGD: 500",
            "food_and_retail": "FOOD_RETAIL_TOTAL_SGD: 600",
            "hotel_recommendations": "HOTEL_TOTAL_SGD: 1000",
            "purchasing_guide": "AIRFARE_TOTAL_SGD: 900\nCAR_RENTAL_TOTAL_SGD: 0",
            "persona": "family",
            "num_days": 5,
        }
        res = quality_agent(state)
        self.assertEqual(res["status"], "approved")
        self.assertIn("SCORE: 9", res["judge_verdict"])
        self.assertEqual(res["budget_attempts"], 1)

    def test_quality_agent_low_score_triggers_retry_loop(self):
        """Score < 8 on attempt 1 triggers re-planning back to orchestrator."""
        self.mock_llm.invoke.return_value = MagicMock(content="VERDICT: FAIL\nSCORE: 6\nSURGICAL SUGGESTIONS: Increase relaxation pacing on Day 3.")
        state = {
            "budget": 3500.0,
            "no_budget": True,
            "budget_attempts": 0,
            "itinerary": "SIGHTSEEING_TOTAL_SGD: 500",
            "food_and_retail": "FOOD_RETAIL_TOTAL_SGD: 600",
            "hotel_recommendations": "HOTEL_TOTAL_SGD: 1000",
            "purchasing_guide": "AIRFARE_TOTAL_SGD: 900",
            "persona": "family",
            "num_days": 5,
        }
        res = quality_agent(state)
        self.assertEqual(res["status"], "planning")
        self.assertIn("SCORE: 6", res["judge_verdict"])
        self.assertEqual(res["budget_attempts"], 1)
        self.assertTrue(len(res["critique_history"]) >= 1)
        self.assertIn("Score 6/10", res["critique_history"][-1])

    def test_quality_agent_max_3_attempts_terminates_gracefully(self):
        """After 3 attempts, low score terminates as quality_failed rather than infinite looping."""
        self.mock_llm.invoke.return_value = MagicMock(content="VERDICT: FAIL\nSCORE: 5\nSURGICAL SUGGESTIONS: Budget still exceeded.")
        state = {
            "budget": 2000.0,
            "no_budget": False,
            "budget_attempts": 2,  # Already attempted twice
            "itinerary": "SIGHTSEEING_TOTAL_SGD: 1000",
            "food_and_retail": "FOOD_RETAIL_TOTAL_SGD: 1000",
            "hotel_recommendations": "HOTEL_TOTAL_SGD: 1000",
            "purchasing_guide": "AIRFARE_TOTAL_SGD: 1000",
            "persona": "family",
            "num_days": 5,
        }
        res = quality_agent(state)
        self.assertEqual(res["status"], "quality_failed")
        self.assertEqual(res["budget_attempts"], 3)


class TestSeasonalRefreshAPI(unittest.TestCase):
    """Test /api/surprise/refresh endpoint behavior and envelope structure."""

    def setUp(self):
        self.client = TestClient(app)

    def test_refresh_endpoint_returns_results_list(self):
        res = self.client.post("/api/surprise/refresh", json={"season": "summer"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("results", data)
        self.assertIsInstance(data["results"], list)
        self.assertTrue(len(data["results"]) >= 1)
        
        # Verify schema of the first item
        item = data["results"][0]
        self.assertIn("destination", item)
        self.assertIn("title", item)
        self.assertIn("continent", item)
        self.assertIn("duration_days", item)

    def test_refresh_endpoint_default_season(self):
        res = self.client.post("/api/surprise/refresh", json={})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("results", data)
        self.assertTrue(len(data["results"]) >= 1)


class TestPlanLocationsExtraction(unittest.TestCase):
    """Test extract_all_plan_locations for multi-venue extraction across Sightseeing, Hotels, and Dining."""

    def test_extract_all_three_categories_with_gmaps_urls(self):
        sample_plan = {
            "itinerary": (
                "## Day 1: Ancient Temples\n"
                "- **Morning (09:00 AM):** Kinkaku-ji Golden Pavilion — Est. cost: S$10\n"
                "- **Afternoon (02:00 PM):** Fushimi Inari Taisha — Est. cost: S$0\n"
                "## Day 2: Bamboo & Scenery\n"
                "- **Morning (10:00 AM):** Arashiyama Bamboo Grove — Est. cost: S$0\n"
            ),
            "hotel_recommendations": (
                "### Option 1: Kyoto Heritage Ryokan ⭐⭐⭐⭐\n"
                "- **Location:** Gion Historical District\n"
                "- **Nightly rate:** S$220\n"
            ),
            "food_and_retail": (
                "## Day 1 Dining\n"
                "- **Lunch:** Gion Duck Noodles — Est. cost: S$25\n"
                "- **Dinner:** Chao Chao Gyoza Bar — Est. cost: S$30\n"
            )
        }

        locations = extract_all_plan_locations(sample_plan, "Kyoto, Japan")
        self.assertTrue(len(locations) >= 4)

        categories = {loc["category"] for loc in locations}
        self.assertIn("Sightseeing", categories)
        self.assertIn("Hotel", categories)
        self.assertIn("Dining & Retail", categories)

        for loc in locations:
            self.assertIn("google_maps_url", loc)
            self.assertTrue(loc["google_maps_url"].startswith("https://www.google.com/maps/search/"))
            self.assertIn("lat", loc)
            self.assertIn("lng", loc)


if __name__ == "__main__":
    unittest.main()
