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


def _load_local_data() -> dict:
    if os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load local trips file: {e}")
    return {}


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

