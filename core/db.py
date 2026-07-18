"""Database and local storage interactions for Travel Buddy."""

import os
import json
import uuid
from datetime import datetime
from supabase import create_client, Client
from .logger import get_logger

logger = get_logger("db")

_supabase: Client = None
LOCAL_FILE = ".saved_trips.json"


def _get_seed_trips() -> dict:
    """Pre-populated reference trips for each persona profile."""
    return {
        "seed-family-tokyo": {
            "id": "seed-family-tokyo",
            "created_at": "2026-07-18T10:00:00",
            "destination": "Tokyo, Japan",
            "travelers": "2 Adults, 1 Child (>2 yrs)",
            "persona": "👨‍👩‍👧‍👦 Family Adventure",
            "dates": "Aug 10 - Aug 14, 2026",
            "state_data": {
                "origin": "Singapore",
                "destination": "Tokyo, Japan",
                "dates": "Aug 10 - Aug 14, 2026",
                "num_days": 5,
                "persona": "family",
                "travelers_summary": "2 Adults, 1 Child (>2 yrs)",
                "self_drive": False,
                "no_budget": True,
                "budget": 0.0,
                "currency": "SGD",
                "status": "approved",
                "itinerary": (
                    "## Day 1: Stroller-Friendly Welcome to Asakusa\n"
                    "- **Morning (10:00 AM):** Senso-ji Temple & Nakamise Shopping Street — Est. cost: S$0\n"
                    "- **Afternoon (2:00 PM):** Tokyo Skytree Observation Deck (Stroller accessible) — Est. cost: S$75\n"
                    "- **Evening (5:30 PM):** Sumida River Park & Rest Block — Est. cost: S$0\n"
                    "- Daily transport: S$20\n\n"
                    "## Day 2: Ueno Park & Interactive Museums\n"
                    "- **Morning (9:30 AM):** Ueno Zoo & Panda House — Est. cost: S$18\n"
                    "- **Afternoon (1:30 PM):** National Museum of Nature and Science — Est. cost: S$25\n"
                    "- **Evening (5:00 PM):** Early Dinner & Rest Stop — Est. cost: S$0\n"
                    "- Daily transport: S$15\n\n"
                    "## Day 3: Odaiba Family Fun & teamLab Planets\n"
                    "- **Morning (10:00 AM):** teamLab Planets Digital Art Museum — Est. cost: S$110\n"
                    "- **Afternoon (2:30 PM):** Legoland Discovery Center Odaiba — Est. cost: S$65\n"
                    "- **Evening (6:00 PM):** Odaiba Seaside Park Sunset Walk — Est. cost: S$0\n"
                    "- Daily transport: S$25\n\n"
                    "## Day 4: Shinjuku Gyoen & Toy Museum\n"
                    "- **Morning (10:00 AM):** Tokyo Toy Museum (Interactive Play Areas) — Est. cost: S$30\n"
                    "- **Afternoon (2:00 PM):** Shinjuku Gyoen National Garden & Playground — Est. cost: S$12\n"
                    "- **Evening (5:30 PM):** Rest & Early Night — Est. cost: S$0\n"
                    "- Daily transport: S$15\n\n"
                    "## Day 5: Harajuku Kidzania & Souvenir Shopping\n"
                    "- **Morning (9:30 AM):** Kiddy Land Harajuku (Toys & Character Goods) — Est. cost: S$40\n"
                    "- **Afternoon (1:00 PM):** Yoyogi Park Picnic & Playground — Est. cost: S$15\n"
                    "- **Evening (4:30 PM):** Haneda Airport Transit — Est. cost: S$30\n"
                    "- Daily transport: S$30\n\n"
                    "SIGHTSEEING_TOTAL_SGD: 455"
                ),
                "food_and_retail": (
                    "## Day 1 Food & Shopping\n"
                    "- **Breakfast:** Cafe de L'Ambre — Coffee & Pastries — Est. S$20 per person\n"
                    "- **Lunch:** Ichiran Asakusa (Kid-friendly booths) — Ramen — Est. S$15 per person\n"
                    "- **Dinner:** Kura Sushi Skytree — Conveyor Belt Sushi — Est. S$22 per person\n"
                    "- **Shopping:** Nakamise Street Crafts — Est. S$30 budget\n\n"
                    "FOOD_RETAIL_TOTAL_SGD: 480"
                ),
                "hotel_recommendations": (
                    "### Option 1: Mimaru Tokyo Asakusa Station ⭐⭐⭐⭐\n"
                    "- **Location:** Asakusa, Tokyo\n"
                    "- **Why it fits:** Family suites with kitchenette and bunk beds, stroller accessible.\n"
                    "- **Nightly rate:** S$280 SGD\n"
                    "- **Total for stay:** S$1,120 SGD\n\n"
                    "**🏨 RECOMMENDED OPTION: Mimaru Tokyo Asakusa Station — Total: S$1,120 SGD**\n\n"
                    "HOTEL_TOTAL_SGD: 1120"
                ),
                "purchasing_guide": (
                    "### ✈️ Flights & Airfare\n"
                    "- **Estimated Airfare:** S$650 SGD per person (Total: S$1,950 SGD)\n"
                    "- **Recommended Airlines:** Singapore Airlines / ANA\n"
                    "- **Booking Links:**\n"
                    "  - [Google Flights](https://www.google.com/travel/flights)\n\n"
                    "### 🏨 Hotel & Accommodation Booking\n"
                    "- **Booking Links:**\n"
                    "  - [Booking.com Mimaru Tokyo](https://www.booking.com)\n\n"
                    "AIRFARE_TOTAL_SGD: 1950\n"
                    "CAR_RENTAL_TOTAL_SGD: 0"
                ),
                "budget_breakdown": (
                    "Budget Breakdown — FLEXIBLE / UNLIMITED BUDGET\n"
                    "------------------------------------------------------------\n"
                    "  Sightseeing & Activities:  S$    455.00 SGD\n"
                    "  Food & Retail:             S$    480.00 SGD\n"
                    "  Accommodation:             S$  1,120.00 SGD\n"
                    "  Airfare (Round-trip):      S$  1,950.00 SGD\n"
                    "------------------------------------------------------------\n"
                    "  TOTAL ESTIMATED COST:      S$  4,005.00 SGD\n"
                ),
                "judge_verdict": "VERDICT: PASS\nSCORE: 9/10\n\nOVERALL ASSESSMENT:\nExcellent family itinerary with gentle pacing and stroller accessibility."
            }
        },
        "seed-business-london": {
            "id": "seed-business-london",
            "created_at": "2026-07-18T09:00:00",
            "destination": "London, UK",
            "travelers": "1 Adult",
            "persona": "💼 Business Traveler",
            "dates": "Sep 15 - Sep 17, 2026",
            "state_data": {
                "origin": "Singapore",
                "destination": "London, UK",
                "dates": "Sep 15 - Sep 17, 2026",
                "num_days": 3,
                "persona": "business",
                "travelers_summary": "1 Adult",
                "self_drive": False,
                "no_budget": True,
                "budget": 0.0,
                "currency": "SGD",
                "status": "approved",
                "itinerary": (
                    "## Day 1: Executive Evening in Canary Wharf\n"
                    "- **Early Morning (7:30 AM):** Express Espresso & Morning Briefing — Est. cost: S$15\n"
                    "- **Daytime (9:00 AM - 5:00 PM):** Work & Meetings (No Activities Scheduled)\n"
                    "- **Evening (6:30 PM):** Thames Executive River Cruise & Sunset Views — Est. cost: S$85\n"
                    "- Daily transport: S$45\n\n"
                    "## Day 2: City of London Networking & Fine Dining\n"
                    "- **Early Morning (7:45 AM):** Hyde Park Morning Jog — Est. cost: S$0\n"
                    "- **Daytime (9:00 AM - 5:00 PM):** Work & Corporate Conference\n"
                    "- **Evening (6:00 PM):** Sky Garden Observation Deck & Drinks — Est. cost: S$60\n"
                    "- Daily transport: S$50\n\n"
                    "## Day 3: Mayfair Evening & Departure\n"
                    "- **Early Morning (8:00 AM):** Mayfair Coffee & Executive Check-out — Est. cost: S$20\n"
                    "- **Daytime (9:00 AM - 4:00 PM):** Client Meetings\n"
                    "- **Evening (5:30 PM):** Heathrow Express Transit — Est. cost: S$40\n"
                    "- Daily transport: S$40\n\n"
                    "SIGHTSEEING_TOTAL_SGD: 315"
                ),
                "food_and_retail": (
                    "## Day 1 Food & Shopping\n"
                    "- **Breakfast:** Grind Canary Wharf — S$25 per person\n"
                    "- **Dinner:** Duck & Waffle — British Fine Dining — S$120 per person\n\n"
                    "FOOD_RETAIL_TOTAL_SGD: 350"
                ),
                "hotel_recommendations": (
                    "### Option 1: The Ned London ⭐⭐⭐⭐⭐\n"
                    "- **Location:** City of London\n"
                    "- **Why it fits:** Executive lounge, ultra-fast Wi-Fi, 24/7 business facilities.\n"
                    "- **Total for stay:** S$1,250 SGD\n\n"
                    "**🏨 RECOMMENDED OPTION: The Ned London — Total: S$1,250 SGD**\n\n"
                    "HOTEL_TOTAL_SGD: 1250"
                ),
                "purchasing_guide": (
                    "### ✈️ Flights & Airfare\n"
                    "- **Estimated Airfare:** S$1,850 SGD (Business Class Option available)\n"
                    "AIRFARE_TOTAL_SGD: 1850\n"
                    "CAR_RENTAL_TOTAL_SGD: 0"
                ),
                "budget_breakdown": (
                    "Budget Breakdown — FLEXIBLE / UNLIMITED BUDGET\n"
                    "------------------------------------------------------------\n"
                    "  TOTAL ESTIMATED COST:      S$  3,765.00 SGD\n"
                ),
                "judge_verdict": "VERDICT: PASS\nSCORE: 10/10\n\nOVERALL ASSESSMENT:\nFlawless business itinerary with zero daytime scheduling conflicts and premium executive comfort."
            }
        }
    }


def _load_local_data() -> dict:
    if os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE, "r", encoding="utf-8") as f:
                content = json.load(f)
                if content:
                    return content
        except Exception as e:
            logger.error(f"Failed to load local trips file: {e}")
    
    # Initialize with default seed trips if no file exists
    seed_data = _get_seed_trips()
    _save_local_data(seed_data)
    return seed_data


def _save_local_data(data: dict):
    try:
        with open(LOCAL_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to write local trips file: {e}")


def init_db(url: str, key: str):
    """Initialize the Supabase client."""
    global _supabase
    if url and key:
        try:
            _supabase = create_client(url, key)
            logger.info("Supabase client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            _supabase = None
    else:
        logger.warning("Supabase URL or Key missing. Using local file storage fallback.")


def is_db_ready() -> bool:
    """Always return True to indicate storage capability (Supabase or Local JSON)."""
    return True


def save_trip_plan(destination: str, travelers: str, persona: str, dates: str, state_data: dict) -> bool:
    """Save a trip plan to Supabase or local storage fallback."""
    if _supabase:
        try:
            data = {
                "destination": destination,
                "travelers": travelers,
                "persona": persona,
                "dates": dates,
                "state_data": state_data
            }
            _supabase.table("trip_plans").insert(data).execute()
            logger.info(f"Trip plan for {destination} saved to Supabase successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to save trip plan to Supabase ({e}). Falling back to local storage.")

    try:
        local_db = _load_local_data()
        trip_id = str(uuid.uuid4())
        local_db[trip_id] = {
            "id": trip_id,
            "created_at": datetime.now().isoformat(),
            "destination": destination,
            "travelers": travelers,
            "persona": persona,
            "dates": dates,
            "state_data": state_data
        }
        _save_local_data(local_db)
        logger.info(f"Trip plan for {destination} saved to local file fallback.")
        return True
    except Exception as e:
        logger.error(f"Failed to save trip plan locally: {e}")
        return False


def get_saved_trips() -> list:
    """Retrieve summarized list of saved trip plans from Supabase or local storage."""
    trips = []
    if _supabase:
        try:
            response = _supabase.table("trip_plans").select("id, created_at, destination, travelers, persona, dates").order("created_at", desc=True).execute()
            if response.data:
                trips = response.data
        except Exception as e:
            logger.error(f"Failed to fetch trip plans from Supabase ({e}). Reading local file fallback.")

    local_db = _load_local_data()
    for trip_id, item in local_db.items():
        if not any(t.get("id") == trip_id for t in trips):
            trips.append({
                "id": item.get("id"),
                "created_at": item.get("created_at"),
                "destination": item.get("destination"),
                "travelers": item.get("travelers"),
                "persona": item.get("persona"),
                "dates": item.get("dates")
            })

    trips.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return trips


def get_trip_plan(trip_id: str) -> dict:
    """Fetch a specific trip plan's full state data from Supabase or local storage."""
    if _supabase:
        try:
            response = _supabase.table("trip_plans").select("state_data").eq("id", trip_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]["state_data"]
        except Exception as e:
            logger.error(f"Failed to fetch trip plan from Supabase: {e}")

    local_db = _load_local_data()
    if trip_id in local_db:
        return local_db[trip_id].get("state_data")

    return None

