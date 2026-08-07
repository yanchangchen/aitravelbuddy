"""Seasonal destination recommendation engine for Travel Buddy."""

import re
import json
import random
from datetime import date, timedelta
from .logger import get_logger

logger = get_logger("surprise")

# Curated top global destinations categorized by season (covers all 6 major continents: Asia, Europe, North America, South America, Africa, Oceania)
SEASONAL_PACKAGES = {
    "summer": [
        {
            "destination": "Kyoto & Hokkaido, Japan",
            "origin": "Singapore",
            "persona": "family",
            "persona_label": "👨‍👩‍👧‍👦 Family Adventure",
            "self_drive": True,
            "continent": "Asia",
            "title": "🌾 Hokkaido Lavender & Kyoto Momiji Road Trip",
            "reason": "Peak summer bloom in Furano lavender fields, mild 22°C weather, and serene temple gardens.",
            "duration_days": 5,
        },
        {
            "destination": "Zurich & Interlaken, Switzerland",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": False,
            "continent": "Europe",
            "title": "🏔️ Swiss Alps Scenic Trains & Jungfrau Summit",
            "reason": "Lush green alpine hiking trails, pristine mountain lakes, and iconic Glacier Express train rides.",
            "duration_days": 6,
        },
        {
            "destination": "Banff & Lake Louise, Canada",
            "origin": "Singapore",
            "persona": "single",
            "persona_label": "🧑 Solo Explorer",
            "self_drive": True,
            "continent": "North America",
            "title": "🌲 Canadian Rockies Turquoise Lakes & Glacier Drive",
            "reason": "Crystal clear turquoise glacial waters at Moraine Lake and spectacular Icefields Parkway views.",
            "duration_days": 6,
        },
        {
            "destination": "Cusco & Machu Picchu, Peru",
            "origin": "Singapore",
            "persona": "custom",
            "persona_label": "🏛️ Culture & Heritage",
            "self_drive": False,
            "continent": "South America",
            "title": "🦙 Machu Picchu Inca Trail & Sacred Valley",
            "reason": "Dry season offering clear blue skies over ancient Inca ruins and vibrant Andean craft markets.",
            "duration_days": 6,
        },
        {
            "destination": "Cape Town & Garden Route, South Africa",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": True,
            "continent": "Africa",
            "title": "🦁 Cape Town Table Mountain & Coastal Safari",
            "reason": "Prime whale-watching season along Hermanus coast and wine tasting in Stellenbosch.",
            "duration_days": 6,
        },
        {
            "destination": "Queenstown & Milford Sound, New Zealand",
            "origin": "Singapore",
            "persona": "single",
            "persona_label": "🧑 Solo Explorer",
            "self_drive": True,
            "continent": "Oceania",
            "title": "⛷️ Queenstown Alpine Snow & Fjordland Cruise",
            "reason": "Southern Hemisphere ski season with snow-capped peaks and dramatic cruises through Milford Sound.",
            "duration_days": 6,
        },
    ],
    "autumn": [
        {
            "destination": "Kyoto, Japan",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": False,
            "continent": "Asia",
            "title": "🍁 Kyoto Autumn Momiji & Temple Illumination",
            "reason": "Breathtaking red and gold maple foliage at Tofuku-ji and Kiyomizu-dera illuminated at night.",
            "duration_days": 5,
        },
        {
            "destination": "Paris, France",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": False,
            "continent": "Europe",
            "title": "🥖 Paris Autumn Romance & Seine Walks",
            "reason": "Fewer crowds, pleasant fall walks through Tuileries Garden, and cosy bistros along Saint-Germain.",
            "duration_days": 5,
        },
        {
            "destination": "New England & Boston, USA",
            "origin": "Singapore",
            "persona": "family",
            "persona_label": "👨‍👩‍👧‍👦 Family Adventure",
            "self_drive": True,
            "continent": "North America",
            "title": "🍁 New England Fall Foliage & Coastal Villages",
            "reason": "World famous vibrant orange and scarlet foliage across Vermont, Kancamagus Highway, and Boston.",
            "duration_days": 5,
        },
        {
            "destination": "Patagonia & Torres del Paine, Chile",
            "origin": "Singapore",
            "persona": "single",
            "persona_label": "🧑 Solo Explorer",
            "self_drive": True,
            "continent": "South America",
            "title": "🏔️ Patagonia Granite Towers & Glacier Trekking",
            "reason": "Spring awakening in the Southern Hemisphere with mild winds, blooming wildflowers, and clear mountain trails.",
            "duration_days": 6,
        },
        {
            "destination": "Serengeti & Ngorongoro, Tanzania",
            "origin": "Singapore",
            "persona": "family",
            "persona_label": "👨‍👩‍👧‍👦 Family Adventure",
            "self_drive": False,
            "continent": "Africa",
            "title": "🐆 Serengeti Great Migration & Big Five Safari",
            "reason": "Witness millions of wildebeest crossing the Mara River under golden autumn skies.",
            "duration_days": 6,
        },
        {
            "destination": "Sydney & Blue Mountains, Australia",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": True,
            "continent": "Oceania",
            "title": "🐨 Sydney Harbour & Jacaranda Purple Bloom",
            "reason": "Purple Jacaranda trees blooming across Sydney, sunny harbour cruises, and crisp Blue Mountains hikes.",
            "duration_days": 5,
        },
    ],
    "winter": [
        {
            "destination": "Sapporo & Niseko, Japan",
            "origin": "Singapore",
            "persona": "family",
            "persona_label": "👨‍👩‍👧‍👦 Family Adventure",
            "self_drive": False,
            "continent": "Asia",
            "title": "❄️ Sapporo Snow Festival & Niseko Powder Ski",
            "reason": "World-famous powder snow, giant ice sculptures at Odori Park, and outdoor hot springs.",
            "duration_days": 6,
        },
        {
            "destination": "Lapland, Finland",
            "origin": "Singapore",
            "persona": "family",
            "persona_label": "👨‍👩‍👧‍👦 Family Adventure",
            "self_drive": False,
            "continent": "Europe",
            "title": "🎅 Rovaniemi Santa Village & Glass Igloo Aurora",
            "reason": "Magical winter wonderland with reindeer sleigh rides, glass igloo stays, and Aurora Borealis.",
            "duration_days": 5,
        },
        {
            "destination": "New York City, USA",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": False,
            "continent": "North America",
            "title": "🗽 NYC Rockefeller Holiday Lights & Central Park",
            "reason": "Iconic Rockefeller Christmas tree, ice skating in Central Park, and holiday window displays on 5th Ave.",
            "duration_days": 5,
        },
        {
            "destination": "Rio de Janeiro & Iguazu, Brazil",
            "origin": "Singapore",
            "persona": "single",
            "persona_label": "🧑 Solo Explorer",
            "self_drive": False,
            "continent": "South America",
            "title": "🎷 Rio Carnival Beats & Iguazu Falls Sunset",
            "reason": "Sizzling summer heat on Copacabana Beach, Christ the Redeemer, and roaring waterfalls.",
            "duration_days": 6,
        },
        {
            "destination": "Marrakech & Sahara, Morocco",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": True,
            "continent": "Africa",
            "title": "🐪 Marrakech Souks & Sahara Stargazing Dunes",
            "reason": "Mild winter temperatures ideal for exploring spice souks and camel glamping under desert stars.",
            "duration_days": 5,
        },
        {
            "destination": "Melbourne & Great Ocean Road, Australia",
            "origin": "Singapore",
            "persona": "single",
            "persona_label": "🧑 Solo Explorer",
            "self_drive": True,
            "continent": "Oceania",
            "title": "🌊 Melbourne Coastal Drive & 12 Apostles Sunset",
            "reason": "Sizzling summer beach days, Australian Open tennis atmosphere, and scenic coastal road trips.",
            "duration_days": 5,
        },
    ],
    "spring": [
        {
            "destination": "Tokyo & Kyoto, Japan",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": False,
            "continent": "Asia",
            "title": "🌸 Tokyo & Kyoto Cherry Blossom Sakura Picnic",
            "reason": "Peak cherry blossom bloom at Shinjuku Gyoen and Meguro River night illuminations.",
            "duration_days": 5,
        },
        {
            "destination": "Amsterdam, Netherlands",
            "origin": "Singapore",
            "persona": "single",
            "persona_label": "🧑 Solo Explorer",
            "self_drive": False,
            "continent": "Europe",
            "title": "🌷 Keukenhof Tulip Gardens & Canal Cycling",
            "reason": "Millions of blooming tulips at Keukenhof Gardens and sunny canal-side bike rides.",
            "duration_days": 5,
        },
        {
            "destination": "Washington D.C. & Virginia, USA",
            "origin": "Singapore",
            "persona": "family",
            "persona_label": "👨‍👩‍👧‍👦 Family Adventure",
            "self_drive": False,
            "continent": "North America",
            "title": "🌸 National Cherry Blossom Festival & Monuments",
            "reason": "Pink cherry blossoms encircling the Tidal Basin and free Smithsonian museums.",
            "duration_days": 5,
        },
        {
            "destination": "Galapagos Islands, Ecuador",
            "origin": "Singapore",
            "persona": "custom",
            "persona_label": "🐢 Eco Wildlife Explorer",
            "self_drive": False,
            "continent": "South America",
            "title": "🐢 Galapagos Tortoise & Sea Lion Snorkeling",
            "reason": "Warm calm waters ideal for swimming with sea tortoises, penguins, and marine iguanas.",
            "duration_days": 6,
        },
        {
            "destination": "Cairo & Nile Cruise, Egypt",
            "origin": "Singapore",
            "persona": "couple",
            "persona_label": "💑 Couple's Getaway",
            "self_drive": False,
            "continent": "Africa",
            "title": "🏺 Pyramids of Giza & Luxury Nile River Sail",
            "reason": "Comfortable 24°C spring weather before summer heat, ideal for exploring ancient temples.",
            "duration_days": 6,
        },
        {
            "destination": "Auckland & Rotorua, New Zealand",
            "origin": "Singapore",
            "persona": "family",
            "persona_label": "👨‍👩‍👧‍👦 Family Adventure",
            "self_drive": True,
            "continent": "Oceania",
            "title": "🥝 Hobbiton Movie Set & Geothermal Springs",
            "reason": "Autumn gold in Middle-earth, geothermal mud baths in Rotorua, and wine tasting in Waiheke.",
            "duration_days": 5,
        },
    ],
}


def get_current_season() -> str:
    """Return current season string based on current calendar month (refreshes every 3 months)."""
    month = date.today().month
    if month in (12, 1, 2):
        return "winter"
    elif month in (3, 4, 5):
        return "spring"
    elif month in (6, 7, 8):
        return "summer"
    else:
        return "autumn"


def fetch_live_seasonal_picks(season: str = None, gemini_key: str = None) -> list:
    """Fetch live trending seasonal travel suggestions using Gemini LLM and current year information."""
    s = season or get_current_season()
    year = date.today().year

    if gemini_key:
        try:
            from langchain_core.messages import HumanMessage
            from langchain_google_genai import ChatGoogleGenerativeAI
            from .utils import ensure_str

            prompt = (
                f"You are a global travel curator. Generate 6 unique, top trending seasonal travel packages for {s.capitalize()} {year}, covering ALL 6 major continents (Asia, Europe, North America, South America, Africa, Oceania).\n"
                f"Return a JSON array of 6 objects with EXACTLY these fields:\n"
                f"[\n"
                f"  {{\n"
                f'    "title": "Emoji + Catchy Title",\n'
                f'    "destination": "City, Country",\n'
                f'    "continent": "Asia / Europe / North America / South America / Africa / Oceania",\n'
                f'    "origin": "Singapore",\n'
                f'    "persona": "couple",\n'
                f'    "persona_label": "💑 Couple\'s Getaway",\n'
                f'    "self_drive": false,\n'
                f'    "reason": "Compelling 1-sentence reason why this destination is top-trending for {s.capitalize()} {year}.",\n'
                f'    "duration_days": 5\n'
                f"  }}\n"
                f"]\n\n"
                f"Return ONLY valid JSON wrapped in ```json ... ```."
            )

            llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.8, google_api_key=gemini_key)
            resp = llm.invoke([HumanMessage(content=prompt)])
            text = ensure_str(resp.content)

            json_match = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
            if json_match:
                items = json.loads(json_match.group(1))
                if isinstance(items, list) and len(items) > 0:
                    logger.info(f"Fetched {len(items)} live seasonal picks for season={s}")
                    return items
        except Exception as e:
            logger.warning(f"Failed to fetch live seasonal picks via LLM: {e}")

    # Fallback to curated packages
    return SEASONAL_PACKAGES.get(s, SEASONAL_PACKAGES["summer"])


def get_seasonal_default_dates(season: str = None) -> tuple:
    """Calculate an optimal 7-day date window within the specified 3-month season."""
    s = (season or get_current_season()).lower()
    year = date.today().year

    if s == "spring":
        start_date = date(year, 4, 5)
    elif s == "summer":
        start_date = date(year, 7, 10)
    elif s == "autumn":
        start_date = date(year, 10, 15)
    elif s == "winter":
        # If current month is past Feb, winter belongs to next year
        w_year = year + 1 if date.today().month > 2 else year
        start_date = date(w_year, 1, 10)
    else:
        start_date = date.today() + timedelta(days=14)

    end_date = start_date + timedelta(days=6) # 7 days total inclusive
    dates_str = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
    return start_date, end_date, dates_str


def get_seasonal_surprise(override_season: str = None) -> dict:
    """Return a pre-configured surprise travel package based on the current season with 7-day optimal dates."""
    season = override_season or get_current_season()
    packages = SEASONAL_PACKAGES.get(season, SEASONAL_PACKAGES["summer"])
    pick = random.choice(packages)

    start_date, end_date, dates_str = get_seasonal_default_dates(season)

    result = {
        "title": pick["title"],
        "reason": pick["reason"],
        "season": season.capitalize(),
        "destination": pick["destination"],
        "origin": pick["origin"],
        "num_adults": 2,
        "num_children": 1,
        "num_infants": 0,
        "persona": pick["persona"],
        "persona_label": pick["persona_label"],
        "self_drive": pick["self_drive"],
        "no_budget": True,
        "budget": 0.0,
        "dates_tuple": (start_date, end_date),
        "dates_str": dates_str,
        "num_days": 7,
    }
    logger.info(f"Generated seasonal surprise pick: '{pick['title']}' for season={season} (7 days: {dates_str})")
    return result
