import asyncio
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.profile import load_user_profile, save_user_profile
from core.personas import PERSONA_PROFILES

router = APIRouter()

class ProfileData(BaseModel):
    data: Dict[str, Any]
    path: str = "user_profile.json"

@router.get("/profile")
async def get_profile(path: str = "user_profile.json"):
    try:
        profile = await asyncio.to_thread(load_user_profile, path)
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile")
async def update_profile(request: ProfileData):
    try:
        await asyncio.to_thread(save_user_profile, request.data, request.path)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/personas")
async def get_personas():
    return PERSONA_PROFILES
