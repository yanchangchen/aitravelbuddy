import json
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

class ExtractPlanRequest(BaseModel):
    messages: List[Message]

@router.post("/chat")
async def chat(request: ChatRequest, req: Request):
    llm = req.app.state.llm
    
    system_prompt = f"""You are a helpful travel concierge AI.
Your goal is to help the user plan their trip. 
User context: {request.user_context}
"""
    langchain_messages = [SystemMessage(content=system_prompt)]
    
    for msg in request.messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=msg.content))
            
    try:
        response = await llm.ainvoke(langchain_messages)
        return {"message": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
            
    try:
        response = await llm.ainvoke(langchain_messages)
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        data = json.loads(content)
        return {"plan": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
