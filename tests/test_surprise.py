"""Unit tests for seasonal recommendation engine in Travel Buddy."""

import unittest
from core.surprise import get_seasonal_surprise, get_current_season, SEASONAL_PACKAGES


class TestSurpriseEngine(unittest.TestCase):

    def test_get_current_season(self):
        season = get_current_season()
        self.assertIn(season, ["spring", "summer", "autumn", "winter"])

    def test_get_seasonal_surprise_fields(self):
        surprise = get_seasonal_surprise("summer")
        self.assertIn("destination", surprise)
        self.assertIn("origin", surprise)
        self.assertIn("persona", surprise)
        self.assertIn("title", surprise)
        self.assertIn("reason", surprise)
        self.assertIn("dates_str", surprise)
        self.assertTrue(surprise["no_budget"])
        self.assertGreater(surprise["num_days"], 0)

    def test_all_seasons_have_valid_packages(self):
        for s in ["spring", "summer", "autumn", "winter"]:
            pick = get_seasonal_surprise(s)
            self.assertEqual(pick["season"], s.capitalize())
            self.assertIsNotNone(pick["destination"])


if __name__ == "__main__":
    unittest.main()
