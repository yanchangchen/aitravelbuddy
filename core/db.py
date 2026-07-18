"""Supabase database interactions for Travel Buddy."""

from supabase import create_client, Client
from .logger import get_logger

logger = get_logger("db")

_supabase: Client = None


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
        logger.warning("Supabase URL or Key missing. DB features disabled.")


def is_db_ready() -> bool:
    return _supabase is not None


def save_trip_plan(destination: str, travelers: str, persona: str, dates: str, state_data: dict) -> bool:
    """Save a trip plan to the trip_plans table."""
    if not _supabase:
        logger.warning("Cannot save trip: DB not ready.")
        return False

    try:
        data = {
            "destination": destination,
            "travelers": travelers,
            "persona": persona,
            "dates": dates,
            "state_data": state_data
        }
        _supabase.table("trip_plans").insert(data).execute()
        logger.info(f"Trip plan for {destination} saved successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to save trip plan to Supabase: {e}")
        return False


def get_saved_trips() -> list:
    """Retrieve summarized list of saved trip plans."""
    if not _supabase:
        return []

    try:
        response = _supabase.table("trip_plans").select("id, created_at, destination, travelers, persona, dates").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        logger.error(f"Failed to fetch trip plans from Supabase: {e}")
        return []


def get_trip_plan(trip_id: str) -> dict:
    """Fetch a specific trip plan's full state data."""
    if not _supabase:
        return None

    try:
        response = _supabase.table("trip_plans").select("state_data").eq("id", trip_id).execute()
        if response.data:
            return response.data[0]["state_data"]
        return None
    except Exception as e:
        logger.error(f"Failed to fetch trip plan {trip_id}: {e}")
        return None
