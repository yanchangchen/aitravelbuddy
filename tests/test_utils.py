"""Unit tests for utility functions in Travel Buddy."""

import unittest
import pandas as pd
from core.utils import (
    extract_cost,
    sanitize_filename,
    parse_itinerary_to_dataframe,
    build_recommendations_text,
    extract_all_itinerary_locations,
)


class TestUtils(unittest.TestCase):

    def test_extract_cost_exact_label(self):
        text = "Day 1 itinerary...\nSIGHTSEEING_TOTAL_SGD: 450.50\nEnd of text."
        cost = extract_cost(text, "SIGHTSEEING_TOTAL_SGD")
        self.assertEqual(cost, 450.50)

    def test_extract_cost_fallback_dollar(self):
        text = "Day 1 itinerary...\nTotal cost: S$320.00\nEnd."
        cost = extract_cost(text, "SIGHTSEEING_TOTAL_SGD")
        self.assertEqual(cost, 320.00)

    def test_sanitize_filename(self):
        raw_name = "Tokyo, Japan! @2025"
        clean = sanitize_filename(raw_name)
        self.assertEqual(clean, "Tokyo_ Japan_ _2025")

    def test_parse_itinerary_to_dataframe(self):
        sample_text = """
## Day 1: Shibuya & Harajuku — Urban Romance
- **Morning (10:00 AM):** Meiji Jingu Shrine — Est. cost: S$0
- **Afternoon (12:30 PM):** Takeshita Street & Harajuku — Est. cost: S$30
- Daily transport: S$15
        """
        guide_text = "AIRFARE_TOTAL_SGD: 800\nCAR_RENTAL_TOTAL_SGD: 250"
        df = parse_itinerary_to_dataframe(sample_text, guide_text)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)
        self.assertIn("Day", df.columns)
        self.assertIn("Est. Cost (SGD)", df.columns)
        self.assertEqual(df.iloc[0]["Activity Details"], "Round-trip Airfare (Flights for Group)")
        self.assertEqual(df.iloc[0]["Est. Cost (SGD)"], 800.0)

    def test_extract_all_itinerary_locations(self):
        sample_text = """
## Day 1: Asakusa
- **Morning (9:30 AM):** Senso-ji Temple — Est. cost: S$20
- **Afternoon (3:30 PM):** Tokyo Tower — Est. cost: S$40
        """
        locs = extract_all_itinerary_locations(sample_text, "Tokyo, Japan")
        self.assertIsInstance(locs, list)
        self.assertGreaterEqual(len(locs), 2)
        self.assertEqual(locs[0]["title"], "Senso-ji Temple")
        self.assertEqual(locs[1]["title"], "Tokyo Tower")

    def test_build_recommendations_text(self):
        result = {"status": "approved", "itinerary": "Day 1 itinerary"}
        text = build_recommendations_text(result, "Tokyo", 3000.0, "March 10-14", "Solo", no_budget=False)
        self.assertIn("TRAVEL BUDDY -- TRAVEL RECOMMENDATIONS", text)
        self.assertIn("APPROVED", text)
        self.assertIn("Tokyo", text)

    def test_dynamic_date_calculation(self):
        from datetime import date
        start_d = date(2026, 11, 10)
        end_d = date(2026, 11, 24)
        num_days = (end_d - start_d).days + 1
        dates_str = f"{start_d.strftime('%b %d, %Y')} - {end_d.strftime('%b %d, %Y')}"
        self.assertEqual(num_days, 15)
        self.assertEqual(dates_str, "Nov 10, 2026 - Nov 24, 2026")


if __name__ == "__main__":
    unittest.main()
