import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from api.main import app

class MockLLM:
    def __init__(self, response_text="Test response"):
        self.response_text = response_text

    async def ainvoke(self, messages):
        return AIMessage(content=self.response_text)

    def invoke(self, messages):
        return AIMessage(content=self.response_text)

@pytest.fixture
def client():
    mock_llm = MockLLM('{"origin": "Singapore", "destination": "Tokyo, Japan", "num_adults": 2, "num_children": 1}')
    mock_search = MagicMock()
    mock_search.invoke.return_value = [{"content": "Top places to visit"}]

    app.state.llm = mock_llm
    app.state.search_tool = mock_search
    with TestClient(app) as test_client:
        yield test_client

def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "message": "Travel Buddy API is live"}

def test_concierge_chat(client):
    payload = {
        "messages": [{"role": "user", "content": "I want to visit Tokyo with family."}],
        "user_context": "Family of 3"
    }
    res = client.post("/api/concierge/chat", json=payload)
    assert res.status_code == 200
    assert "message" in res.json()

def test_concierge_extract_plan_valid(client):
    payload = {
        "messages": [{"role": "user", "content": "Book 7 days in Banff for 2 adults and 1 child."}]
    }
    res = client.post("/api/concierge/extract-plan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "destination" in data["plan"]

def test_concierge_extract_plan_malformed_llm(client):
    # Simulate LLM outputting non-JSON text
    app.state.llm = MockLLM("I cannot parse this into json. Here is a note: hello world")
    payload = {
        "messages": [{"role": "user", "content": "Hello"}]
    }
    res = client.post("/api/concierge/extract-plan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "plan" in data
    assert data["plan"]["origin"] == "Singapore"
    assert data["plan"]["num_adults"] == 2

def test_get_surprise_packages(client):
    res = client.get("/api/surprise/packages")
    assert res.status_code == 200
    packages = res.json()
    assert isinstance(packages, (dict, list))
    assert len(packages) >= 1

def test_get_saved_trips(client):
    res = client.get("/api/trips/saved")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_rest_plan_trip(client):
    payload = {
        "origin": "Singapore",
        "destination": "Kyoto, Japan",
        "budget": 0,
        "num_adults": 2,
        "num_children": 1,
        "num_infants": 0,
        "self_drive": False,
        "no_budget": True,
        "currency": "SGD",
        "dates": "2026-08-22 - 2026-08-26",
        "num_days": 5,
        "persona": "Family",
        "custom_persona_profile": {"title": "Kyoto Momiji"},
        "user_preferences": {
            "dining": "Agent Recommended",
            "lodging": "Boutique",
            "rules": "Family trip"
        }
    }
    with patch("core.agents._invoke_llm_with_retry", return_value="## Day 1: Ancient Temples\n- **Morning:** Kinkaku-ji\nSIGHTSEEING_TOTAL_SGD: 100\nFOOD_RETAIL_TOTAL_SGD: 100\nHOTEL_TOTAL_SGD: 100\nAIRFARE_TOTAL_SGD: 100"), patch("core.evaluation.quality_agent", return_value={"status": "approved", "judge_verdict": "VERDICT: PASS\nSCORE: 9", "budget_breakdown": "Passed", "budget_attempts": 1, "critique_history": []}):
        res = client.post("/api/trips/plan", json=payload)
    assert res.status_code == 200
    assert "itinerary" in res.json()

def test_export_locations(client):
    payload = {
        "result": {
            "itinerary": "Day 1: Visit Banff National Park. Day 2: Lake Louise canoeing."
        },
        "destination": "Banff & Lake Louise, Canada"
    }
    res = client.post("/api/trips/export/locations", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "locations" in data
    assert isinstance(data["locations"], list)

def test_websocket_plan_stream(client):
    with client.websocket_connect("/api/ws/plan") as websocket:
        websocket.send_json({
            "destination": "Banff & Lake Louise, Canada",
            "num_adults": 2,
            "num_children": 1,
            "num_infants": 0,
            "dates": "Next Month",
            "num_days": 3,
            "persona": "Family",
            "no_budget": True
        })
        # Read messages until complete or error
        received_types = []
        for _ in range(20):
            try:
                data = websocket.receive_json()
                received_types.append(data.get("type"))
                if data.get("type") in ["complete", "error"]:
                    break
            except Exception:
                break
        assert len(received_types) > 0

def test_save_trip_endpoint(client):
    payload = {
        "destination": "Banff & Lake Louise, Canada",
        "travelers": 3,
        "persona": "Family",
        "dates": "Nov 15 - Nov 20, 2026",
        "state_data": {
            "itinerary": "Day 1: Visit Banff National Park",
            "hotel_recommendations": "Hotel Banff Springs",
            "food_and_retail": "Local Dining",
            "purchasing_guide": "Flight Airfare: S$ 600"
        }
    }
    res = client.post("/api/trips/test_plan_999/save", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "success"

def test_export_excel_endpoint(client):
    payload = {
        "result": {
            "itinerary": "Day 1: Sensoji. Day 2: Fuji.",
            "hotel_recommendations": "Tokyo Hotel",
            "food_and_retail": "Ramen Alley",
            "purchasing_guide": "Airfare & Hotels"
        },
        "destination": "Tokyo, Japan"
    }
    res = client.post("/api/trips/export/excel", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "filename" in data
    assert "content" in data
    assert "Travel_Buddy" in data["filename"]
