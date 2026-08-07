import asyncio
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from core.graph import build_graph
from core.db import get_saved_trips, get_trip_plan, save_trip_plan
from core.utils import build_recommendations_text, extract_all_plan_locations

router = APIRouter()

class TripPlanRequest(BaseModel):
    origin: str
    destination: str
    budget: float
    num_adults: int
    num_children: int
    num_infants: int
    self_drive: bool
    no_budget: bool
    currency: str
    dates: str
    num_days: int
    persona: str
    custom_persona_profile: Optional[str] = None
    user_preferences: Optional[str] = None

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

@router.post("/plan")
async def plan_trip(request_data: TripPlanRequest, request: Request):
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
        "num_days": request_data.num_days,
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
        return accumulated

    try:
        result = await asyncio.to_thread(run_graph)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/saved")
async def get_saved_trips_endpoint():
    try:
        trips = await asyncio.to_thread(get_saved_trips)
        return trips
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{trip_id}")
async def get_trip(trip_id: str):
    try:
        plan = await asyncio.to_thread(get_trip_plan, trip_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Trip not found")
        return plan
    except HTTPException:
        raise
    except Exception as e:
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
        return {"status": "success", "plan_id": plan_id}
    except Exception as e:
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
