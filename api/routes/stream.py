import json
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.graph import build_graph
from core.logger import get_logger

router = APIRouter()
logger = get_logger("ws_stream")

PROGRESS_MAPPING = {
    "itinerary_agent": 0.17,
    "food_retail_agent": 0.33,
    "hospitality_agent": 0.50,
    "purchasing_agent": 0.67,
    "budget_guardrail": 0.75,
    "agent_as_judge": 0.88,
    "final_output": 1.0,
    "terminal_fallback": 1.0
}

@router.websocket("/plan")
async def websocket_plan(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔌 Client connected to WebSocket /api/ws/plan")
    
    try:
        data = await websocket.receive_text()
        request_data = json.loads(data)
        
        destination = request_data.get("destination", "Unknown")
        persona = request_data.get("persona", "Default")
        logger.info(f"⚡ Starting Multi-Agent Stream: destination='{destination}', persona='{persona}', origin='{request_data.get('origin')}'")
        
        llm = websocket.app.state.llm
        search_tool = websocket.app.state.search_tool
        
        graph = build_graph(llm, search_tool)
        
        # Build travelers summary
        parts = []
        na = request_data.get("num_adults", 1)
        nc = request_data.get("num_children", 0)
        ni = request_data.get("num_infants", 0)
        if na:
            parts.append(f"{na} Adult{'s' if na > 1 else ''}")
        if nc:
            parts.append(f"{nc} Child{'ren' if nc > 1 else ''} (>2 yrs)")
        if ni:
            parts.append(f"{ni} Infant{'s' if ni > 1 else ''}")
        travelers_summary = ", ".join(parts) if parts else "1 Adult"

        initial_state = {
            "origin": request_data.get("origin", ""),
            "destination": request_data.get("destination", ""),
            "budget": request_data.get("budget", 0.0),
            "num_adults": na,
            "num_children": nc,
            "num_infants": ni,
            "travelers_summary": travelers_summary,
            "self_drive": request_data.get("self_drive", False),
            "no_budget": request_data.get("no_budget", False),
            "currency": request_data.get("currency", "SGD"),
            "dates": request_data.get("dates", ""),
            "num_days": request_data.get("num_days", 1),
            "persona": request_data.get("persona", ""),
            "custom_persona_profile": request_data.get("custom_persona_profile") or {},
            "user_preferences": request_data.get("user_preferences") or {},
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
        
        queue = asyncio.Queue()
        accumulated_state = dict(initial_state)
        
        loop = asyncio.get_running_loop()
        
        def run_graph_sync():
            try:
                for event in graph.stream(initial_state):
                    for node_name, node_output in event.items():
                        if isinstance(node_output, dict):
                            accumulated_state.update(node_output)
                        loop.call_soon_threadsafe(queue.put_nowait, {"type": "node", "name": node_name, "output": node_output})
                loop.call_soon_threadsafe(queue.put_nowait, {"type": "done", "result": accumulated_state})
            except Exception as e:
                loop.call_soon_threadsafe(queue.put_nowait, {"type": "error", "message": str(e)})
                
        # Start thread
        task = asyncio.create_task(asyncio.to_thread(run_graph_sync))
        
        while True:
            msg = await queue.get()
            if msg["type"] == "node":
                node_name = msg["name"]
                node_output = msg["output"]
                progress = PROGRESS_MAPPING.get(node_name, 0.0)
                logger.info(f"  [Agent Node] {node_name} finished (progress={progress:.0%})")
                
                await websocket.send_json({
                    "type": "node_update",
                    "node": node_name,
                    "progress": progress,
                    "data": node_output
                })
            elif msg["type"] == "done":
                res = msg["result"]
                logger.info(f"✅ Multi-Agent Graph complete: destination='{destination}', status='{res.get('status')}', judge='{res.get('judge_verdict')}'")
                await websocket.send_json({
                    "type": "complete",
                    "result": res
                })
                break
            elif msg["type"] == "error":
                logger.error(f"❌ Graph execution error: {msg['message']}")
                await websocket.send_json({
                    "type": "error",
                    "message": msg["message"]
                })
                break
                
        await task

    except WebSocketDisconnect:
        logger.info("🔌 WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
