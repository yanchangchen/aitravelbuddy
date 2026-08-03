"""Unit test for complete plan location extraction, geocoding, and map rendering."""

import unittest
from core.utils import extract_all_plan_locations, get_city_fallback_coords


class TestPlanMapLocations(unittest.TestCase):

    def test_city_fallback_coords(self):
        """Verify city fallback coordinates registry returns valid lat/lon tuples."""
        zurich_coords = get_city_fallback_coords("Zurich, Switzerland")
        self.assertEqual(zurich_coords, (47.3769, 8.5417))

        chengdu_coords = get_city_fallback_coords("Chengdu, Sichuan, China")
        self.assertEqual(chengdu_coords, (30.5728, 104.0668))

    def test_extract_all_plan_locations(self):
        """Verify extract_all_plan_locations extracts sightseeing, hotel, and dining locations."""
        sample_plan = {
            "itinerary": (
                "## Day 1: Historic Chengdu\n"
                "- **Morning**: Visit Chengdu Giant Panda Breeding Research Base — Est. cost: S$ 15\n"
                "- **Afternoon**: Explore Jinli Ancient Street — Est. cost: S$ 10\n\n"
                "## Day 2: Cultural Exploration\n"
                "- **Morning**: Visit Wuhou Shrine & People's Park — Est. cost: S$ 12\n"
            ),
            "hotel_recommendations": (
                "- **Hotel 1**: St. Regis Chengdu (Luxury 5-star hotel in city center)\n"
                "- **Hotel 2**: The Temple House Chengdu (Boutique heritage hotel)\n"
            ),
            "food_and_retail": (
                "- **Restaurant 1**: Chen Mapo Tofu Restaurant (Traditional Sichuan cuisine)\n"
                "- **Dining 2**: Jinli Street Food Stall & Teahouse\n"
            )
        }

        locs = extract_all_plan_locations(sample_plan, "Chengdu, China")
        self.assertIsInstance(locs, list)
        self.assertGreaterEqual(len(locs), 5, "Must extract at least 5 locations across sightseeing, hotels, and dining")

        categories = {loc["category"] for loc in locs}
        self.assertIn("Sightseeing", categories)
        self.assertIn("Hotel", categories)
        self.assertIn("Dining & Retail", categories)

        for item in locs:
            self.assertIn("lat", item)
            self.assertIn("lon", item)
            self.assertIn("color", item)
            self.assertIsInstance(item["lat"], float)
            self.assertIsInstance(item["lon"], float)

        print(f"\n[Test Plan Map] Extracted {len(locs)} venues across categories: {list(categories)}")


if __name__ == "__main__":
    unittest.main()
