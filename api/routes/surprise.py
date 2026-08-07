import asyncio
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.surprise import get_seasonal_surprise, get_current_season, fetch_live_seasonal_picks, SEASONAL_PACKAGES

router = APIRouter()

class RefreshRequest(BaseModel):
    season: str

@router.get("/seasonal")
async def get_seasonal():
    try:
        season, pick = await asyncio.to_thread(get_seasonal_surprise)
        return {"season": season, "surprise": pick}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/packages")
async def get_packages():
    return SEASONAL_PACKAGES

@router.post("/refresh")
async def refresh_seasonal(request: RefreshRequest):
    gemini_key = os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        raise HTTPException(status_code=500, detail="Google API Key not configured")
    try:
        results = await asyncio.to_thread(fetch_live_seasonal_picks, request.season, gemini_key)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
