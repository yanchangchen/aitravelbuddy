"""Seasonal destination recommendation engine for Travel Buddy."""

import random
from datetime import date, timedelta
from .logger import get_logger

logger = get_logger("surprise")

# Curated top global destinations categorized by season
SEASONAL_PACKAGES = {
    "summer": [
        {
            "destination": "Hokkaido, Japan",
            "origin": "Singapore",
            "persona": "family",
            "persona_label": "👨‍👩‍👧‍👦 Family Adventure",
            "self_drive": True,
            "title": "🌾 Hokkaido Furano Lavender & Lakes Road Trip",
            "reason": "Peak summer bloom in Furano lavender fields, mild 22°C weather, and scenic self-drive routes around Lake Toya.",
            "duration_days": 5,
        },
        {
            "destination": "Bali, Indonesia",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": False,
            "title": "🌺 Bali Ubud Culture & Uluwatu Sunset Retreat",
            "reason": "Dry season with sunny skies, ideal for beach sunsets in Uluwatu and jungle infinity pools in Ubud.",
            "duration_days": 4,
        },
        {
            "destination": "Zurich & Interlaken, Switzerland",
            "origin": "Singapore",
            "persona": "custom",
            "persona_label": "🏔️ Swiss Alps & Alpine Lake Explorer",
            "self_drive": False,
            "title": "🏔️ Swiss Alps Scenic Trains & Jungfrau Summit",
            "reason": "Lush green alpine hiking trails, pristine mountain lakes, and iconic Glacier Express train rides.",
            "duration_days": 6,
        },
        {
            "destination": "Reykjavik, Iceland",
            "origin": "Singapore",
            "persona": "single",
            "persona_label": "🧑 Solo Traveler",
            "self_drive": True,
            "title": "🌋 Iceland Midnight Sun & Golden Circle Drive",
            "reason": "24-hour daylight under the Midnight Sun, geothermal spas at Blue Lagoon, and dramatic waterfalls.",
            "duration_days": 5,
        },
    ],
    "autumn": [
        {
            "destination": "Kyoto, Japan",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": False,
            "title": "🍁 Kyoto Autumn Momiji & Temple Illumination",
            "reason": "Breathtaking red and gold maple foliage at Tofuku-ji and Kiyomizu-dera illuminated at night.",
            "duration_days": 5,
        },
        {
            "destination": "Seoul, South Korea",
            "origin": "Singapore",
            "persona": "single",
            "persona_label": "🧑 Solo Traveler",
            "self_drive": False,
            "title": "🍂 Seoul Ginkgo Leaves, Palaces & Street Food",
            "reason": "Golden ginkgo tree avenues at Deoksugung Palace, crisp 15°C weather, and vibrant night markets.",
            "duration_days": 5,
        },
        {
            "destination": "Paris, France",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": False,
            "title": "🥖 Paris Autumn Romance & Seine Walks",
            "reason": "Fewer crowds, pleasant fall walks through Tuileries Garden, and cosy bistros along Saint-Germain.",
            "duration_days": 5,
        },
    ],
    "winter": [
        {
            "destination": "Sapporo, Japan",
            "origin": "Singapore",
            "persona": "family",
            "persona_label": "👨‍👩‍👧‍👦 Family Adventure",
            "self_drive": False,
            "title": "❄️ Sapporo Snow Festival & Niseko Skiing",
            "reason": "World-famous powder snow, giant ice sculptures at Odori Park, and relaxing outdoor hot springs.",
            "duration_days": 6,
        },
        {
            "destination": "Lapland, Finland",
            "origin": "Singapore",
            "persona": "family",
            "persona_label": "👨‍👩‍👧‍👦 Family Adventure",
            "self_drive": False,
            "title": "🎅 Rovaniemi Santa Claus Village & Northern Lights",
            "reason": "Magical winter wonderland with reindeer sleigh rides, glass igloo stays, and Aurora Borealis.",
            "duration_days": 5,
        },
        {
            "destination": "London, UK",
            "origin": "Singapore",
            "persona": "business",
            "persona_label": "💼 Business Traveler",
            "self_drive": False,
            "title": "🎄 London Festive Lights & Winter Wonderland",
            "reason": "Sparkling Regent Street Christmas lights, Hyde Park Winter Wonderland, and festive West End shows.",
            "duration_days": 4,
        },
    ],
    "spring": [
        {
            "destination": "Tokyo, Japan",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": False,
            "title": "🌸 Tokyo Cherry Blossom Sakura Picnic",
            "reason": "Peak cherry blossom bloom at Shinjuku Gyoen and Meguro River night illuminations.",
            "duration_days": 5,
        },
        {
            "destination": "Amsterdam, Netherlands",
            "origin": "Singapore",
            "persona": "single",
            "persona_label": "🧑 Solo Traveler",
            "self_drive": False,
            "title": "🌷 Keukenhof Tulip Gardens & Canal Cycling",
            "reason": "Millions of blooming tulips at Keukenhof Gardens and sunny canal-side bike rides.",
            "duration_days": 5,
        },
    ],
}


def get_current_season() -> str:
    """Return current season string based on current month."""
    month = date.today().month
    if month in (12, 1, 2):
        return "winter"
    elif month in (3, 4, 5):
        return "spring"
    elif month in (6, 7, 8):
        return "summer"
    else:
        return "autumn"


def get_seasonal_surprise(override_season: str = None) -> dict:
    """Return a pre-configured surprise travel package based on the current season."""
    season = override_season or get_current_season()
    packages = SEASONAL_PACKAGES.get(season, SEASONAL_PACKAGES["summer"])
    pick = random.choice(packages)

    # Calculate optimal travel dates starting 2 weeks from today
    start_date = date.today() + timedelta(days=14)
    end_date = start_date + timedelta(days=pick["duration_days"] - 1)

    dates_str = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"

    result = {
        "title": pick["title"],
        "reason": pick["reason"],
        "season": season.capitalize(),
        "destination": pick["destination"],
        "origin": pick["origin"],
        "persona": pick["persona"],
        "persona_label": pick["persona_label"],
        "self_drive": pick["self_drive"],
        "no_budget": True,
        "budget": 0.0,
        "dates_tuple": (start_date, end_date),
        "dates_str": dates_str,
        "num_days": pick["duration_days"],
    }
    logger.info(f"Generated seasonal surprise pick: '{pick['title']}' for season={season}")
    return result
