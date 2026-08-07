from typing import Optional
import asyncio
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.surprise import get_seasonal_surprise, get_current_season, fetch_live_seasonal_picks, SEASONAL_PACKAGES

router = APIRouter()

class RefreshRequest(BaseModel):
    season: Optional[str] = None

@router.get("/seasonal")
async def get_seasonal():
    try:
        pick = await asyncio.to_thread(get_seasonal_surprise)
        return {"season": pick.get("season", "Summer"), "surprise": pick}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/packages")
async def get_packages():
    return SEASONAL_PACKAGES

@router.post("/refresh")
async def refresh_seasonal(request: Optional[RefreshRequest] = None):
    gemini_key = os.getenv("GOOGLE_API_KEY")
    season = request.season if request and request.season else get_current_season()
    try:
        results = await asyncio.to_thread(fetch_live_seasonal_picks, season, gemini_key)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
