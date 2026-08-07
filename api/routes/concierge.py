import json
import re
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    user_context: Optional[str] = ""
    current_itinerary: Optional[str] = ""
    destination: Optional[str] = ""

class ExtractPlanRequest(BaseModel):
    messages: List[Message]

@router.post("/chat")
async def chat(request: ChatRequest, req: Request):
    llm = req.app.state.llm
    
    system_prompt = f"""You are Travel Buddy — a warm, knowledgeable, and helpful AI travel concierge buddy.
Your job is to talk with the traveler about their trip, discuss their active itinerary, offer personalized dining & activity recommendations, ask preference questions, and help refine or modify their plan.

Target Destination: {request.destination or 'Not specified'}
Traveler Context: {request.user_context or 'Standard Traveler'}

Active Generated Itinerary:
{request.current_itinerary if request.current_itinerary else '(No itinerary generated yet. Help the user plan one by asking about their preferences!)'}

Instructions:
1. Be friendly, encouraging, and clear.
2. If the user asks to modify, replace, or add activities/restaurants to their itinerary, provide your helpful AI response AND if modifying the plan, include the updated day-by-day itinerary block starting with '## Day 1:'.
3. Ask 1-2 thoughtful preference questions (e.g. food tastes, pace, interests) to help tailor their experience even further!
"""
    langchain_messages = [SystemMessage(content=system_prompt)]
    
    for msg in request.messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=msg.content))
            
    try:
        response = await llm.ainvoke(langchain_messages)
        content = response.content
        if isinstance(content, list):
            content = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])
        return {"message": str(content)}
    except Exception as e:
        return {"message": f"I'm your AI Travel Concierge! How can I assist with your trip planning today? (Note: {str(e)})"}

@router.post("/extract-plan")
async def extract_plan(request: ExtractPlanRequest, req: Request):
    llm = req.app.state.llm
    
    system_prompt = """You are a travel plan extractor. Read the conversation and extract trip parameters as JSON.
Required fields:
- origin
- destination 
- budget (number)
- num_adults (number)
- num_children (number)
- num_infants (number)
- self_drive (boolean)
- no_budget (boolean)
- currency (string)
- dates (string)
- num_days (number)
- persona (string)
- custom_persona_profile (string)
- user_preferences (string)

Return ONLY valid JSON.
"""
    langchain_messages = [SystemMessage(content=system_prompt)]
    
    for msg in request.messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=msg.content))
            
    defaults = {
        "origin": "Singapore",
        "destination": "Tokyo, Japan",
        "budget": 0.0,
        "num_adults": 2,
        "num_children": 1,
        "num_infants": 0,
        "self_drive": False,
        "no_budget": True,
        "currency": "SGD",
        "dates": "Next Month",
        "num_days": 7,
        "persona": "Family",
        "custom_persona_profile": {},
        "user_preferences": {}
    }
    
    try:
        response = await llm.ainvoke(langchain_messages)
        content = response.content
        if isinstance(content, list):
            content = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])
        content = str(content)
        
        match = re.search(r'\{[\s\S]*\}', content)
        json_str = match.group(0) if match else content
        data = json.loads(json_str)
        
        for k, v in defaults.items():
            if k not in data or data[k] is None:
                data[k] = v
                
        return {"plan": data}
    except Exception as e:
        return {"plan": defaults}
