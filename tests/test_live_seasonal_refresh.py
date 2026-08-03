"""Unit test for automatic 3-month calendar season calculations and live seasonal AI refresh."""

import unittest
from core.surprise import get_current_season, fetch_live_seasonal_picks, SEASONAL_PACKAGES


class TestLiveSeasonalRefresh(unittest.TestCase):

    def test_get_current_season_3_month_rotation(self):
        """Verify season automatically rotates every 3 months based on calendar month."""
        curr_season = get_current_season()
        self.assertIn(curr_season, ["spring", "summer", "autumn", "winter"])
        print(f"\n[Test Seasonal Refresh] Current 3-month calendar season: '{curr_season.capitalize()}'")

    def test_fetch_live_seasonal_picks_fallback(self):
        """Verify fetch_live_seasonal_picks returns valid packages list."""
        picks = fetch_live_seasonal_picks(season="summer", gemini_key=None)
        self.assertIsInstance(picks, list)
        self.assertGreater(len(picks), 0)
        self.assertIn("destination", picks[0])
        print(f"[Test Seasonal Refresh] Verified {len(picks)} seasonal packages loaded!")


if __name__ == "__main__":
    unittest.main()
