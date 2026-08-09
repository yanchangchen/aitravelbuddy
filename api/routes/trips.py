import asyncio
from typing import Optional, Dict, Any, List, Union
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

from core.graph import build_graph
from core.db import get_saved_trips, get_trip_plan, save_trip_plan, delete_trip_plan
from core.utils import build_recommendations_text, extract_all_plan_locations
from core.logger import get_logger

router = APIRouter()
logger = get_logger("trips_api")

class TripPlanRequest(BaseModel):
    origin: Optional[str] = "Singapore"
    destination: str
    budget: Optional[float] = 0.0
    num_adults: Optional[int] = 2
    num_children: Optional[int] = 1
    num_infants: Optional[int] = 0
    self_drive: Optional[bool] = False
    no_budget: Optional[bool] = True
    currency: Optional[str] = "SGD"
    dates: Optional[str] = "Nov 15 - Nov 19, 2026"
    num_days: Optional[int] = 5
    persona: Optional[str] = "Family"
    custom_persona_profile: Optional[Union[Dict[str, Any], str]] = None
    user_preferences: Optional[Union[Dict[str, Any], str]] = None

class TripSaveRequest(BaseModel):
    destination: str
    travelers: int
    persona: str
    dates: str
    state_data: Dict[str, Any]

class ExportTextRequest(BaseModel):
    result: Dict[str, Any]
    destination: str
    budget: float
    dates: str
    persona_label: str
    no_budget: bool
    currency: str

class ExportLocationsRequest(BaseModel):
    result: Dict[str, Any]
    destination: str

class ExportExcelRequest(BaseModel):
    result: Dict[str, Any]
    destination: Optional[str] = "Travel_Buddy_Itinerary"

@router.post("/plan")
async def plan_trip(request_data: TripPlanRequest, request: Request):
    logger.info(f"📥 REST POST /api/trips/plan: destination='{request_data.destination}', persona='{request_data.persona}', dates='{request_data.dates}'")
    llm = request.app.state.llm
    search_tool = request.app.state.search_tool
    
    graph = build_graph(llm, search_tool)
    
    # Build travelers summary
    parts = []
    if request_data.num_adults:
        parts.append(f"{request_data.num_adults} Adult{'s' if request_data.num_adults > 1 else ''}")
    if request_data.num_children:
        parts.append(f"{request_data.num_children} Child{'ren' if request_data.num_children > 1 else ''} (>2 yrs)")
    if request_data.num_infants:
        parts.append(f"{request_data.num_infants} Infant{'s' if request_data.num_infants > 1 else ''}")
    travelers_summary = ", ".join(parts) if parts else "1 Adult"

    initial_state = {
        "origin": request_data.origin,
        "destination": request_data.destination,
        "budget": request_data.budget,
        "num_adults": request_data.num_adults,
        "num_children": request_data.num_children,
        "num_infants": request_data.num_infants,
        "travelers_summary": travelers_summary,
        "self_drive": request_data.self_drive,
        "no_budget": request_data.no_budget,
        "currency": request_data.currency,
        "dates": request_data.dates,
        "num_days": request_data.num_days or 5,
        "persona": request_data.persona,
        "custom_persona_profile": request_data.custom_persona_profile or {},
        "user_preferences": request_data.user_preferences or {},
        "itinerary": "",
        "food_and_retail": "",
        "hotel_recommendations": "",
        "purchasing_guide": "",
        "budget_breakdown": "",
        "budget_attempts": 0,
        "critique_history": [],
        "status": "planning",
        "judge_verdict": "",
        "quality_failure_reason": None,
    }
    
    def run_graph():
        """Stream graph and accumulate final state from all node outputs."""
        accumulated = dict(initial_state)
        for event in graph.stream(initial_state):
            for node_name, node_output in event.items():
                if isinstance(node_output, dict):
                    accumulated.update(node_output)
                    logger.info(f"  [REST Graph Node] {node_name} completed.")
        return accumulated

    try:
        result = await asyncio.to_thread(run_graph)
        logger.info(f"✅ REST Plan completed: status='{result.get('status')}', judge='{result.get('judge_verdict')}'")
        return result
    except Exception as e:
        logger.error(f"❌ REST Plan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/saved")
async def get_saved_trips_endpoint():
    try:
        trips = await asyncio.to_thread(get_saved_trips)
        logger.info(f"💾 Fetched {len(trips) if trips else 0} saved trips.")
        return trips
    except Exception as e:
        logger.error(f"❌ Error fetching saved trips: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{trip_id}")
async def get_trip(trip_id: str):
    try:
        plan = await asyncio.to_thread(get_trip_plan, trip_id)
        if not plan:
            logger.warning(f"⚠️ Trip plan not found: trip_id='{trip_id}'")
            raise HTTPException(status_code=404, detail="Trip not found")
        logger.info(f"📖 Loaded trip plan: trip_id='{trip_id}'")
        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting trip plan '{trip_id}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{plan_id}/save")
async def save_trip(plan_id: str, request_data: TripSaveRequest):
    try:
        await asyncio.to_thread(
            save_trip_plan,
            request_data.destination,
            request_data.travelers,
            request_data.persona,
            request_data.dates,
            request_data.state_data
        )
        logger.info(f"💾 Saved trip plan successfully: plan_id='{plan_id}', destination='{request_data.destination}'")
        return {"status": "success", "plan_id": plan_id}
    except Exception as e:
        logger.error(f"❌ Error saving trip plan '{plan_id}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{trip_id}")
async def delete_trip(trip_id: str):
    try:
        deleted = await asyncio.to_thread(delete_trip_plan, trip_id)
        if not deleted:
            logger.warning(f"⚠️ Trip plan not found for deletion: trip_id='{trip_id}'")
            raise HTTPException(status_code=404, detail="Trip plan not found")
        logger.info(f"🗑️ Deleted trip plan: trip_id='{trip_id}'")
        return {"status": "success", "trip_id": trip_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting trip plan '{trip_id}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/text")
async def export_text(request_data: ExportTextRequest):
    try:
        text = await asyncio.to_thread(
            build_recommendations_text,
            request_data.result,
            request_data.destination,
            request_data.budget,
            request_data.dates,
            request_data.persona_label,
            request_data.no_budget,
            request_data.currency
        )
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/locations")
async def export_locations(request_data: ExportLocationsRequest):
    try:
        locations = await asyncio.to_thread(
            extract_all_plan_locations,
            request_data.result,
            request_data.destination
        )
        return {"locations": locations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/excel")
async def export_excel(request_data: ExportExcelRequest):
    try:
        res = request_data.result
        dest = request_data.destination or "Travel_Buddy_Itinerary"
        
        csv_lines = [
            f"=== TRAVEL BUDDY ITINERARY: {dest} ===",
            "",
            "--- DAY-BY-DAY ITINERARY ---",
            res.get("itinerary", "N/A"),
            "",
            "--- HOTELS & ACCOMMODATIONS ---",
            res.get("hotel_recommendations", "N/A"),
            "",
            "--- DINING & RETAIL HIGHLIGHTS ---",
            res.get("food_and_retail", "N/A"),
            "",
            "--- PURCHASING & BOOKING LOGISTICS ---",
            res.get("purchasing_guide", "N/A"),
        ]
        content = "\n".join(csv_lines)
        return {
            "filename": f"Travel_Buddy_{dest.replace(' ', '_')}.csv",
            "content": content,
            "itinerary": res.get("itinerary", ""),
            "hotels": res.get("hotel_recommendations", ""),
            "dining": res.get("food_and_retail", ""),
            "purchasing": res.get("purchasing_guide", "")
        }
    except Exception as e:
        logger.error(f"❌ Error generating Excel export: {e}")
        raise HTTPException(status_code=500, detail=str(e))
