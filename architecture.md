# Travel Buddy — Engineering Architecture & System Roadmap

## 🏛️ 1. Multi-Agent System Architecture

Travel Buddy is built on a modular, multi-agent architecture powered by **LangGraph**, **Google Gemini** (`gemini-3.1-flash-lite`), **Tavily Search API**, **FastAPI**, **Streamlit**, and **React / Vite**.

```
                           +------------------------+      +------------------------+
                           |   Streamlit UI App     |      |   React SPA (Vercel)   |
                           |       (app.py)         |      |    (frontend/src)      |
                           +-----------+------------+      +-----------+------------+
                                       |                               | (WebSocket / REST)
                                       +---------------+---------------+
                                                       |
                                                       v
                                           +-----------------------+
                                           |  FastAPI Backend Host |
                                           |      (api/main.py)    |
                                           +-----------+-----------+
                                                       |
                                                       v
                                           +-----------------------+
                                           | LangGraph StateGraph  |
                                           |    (core/graph.py)    |
                                           +-----------+-----------+
                                                       |
                                                       v
                                           +-----------------------+
                                           |  orchestrator_agent   |
                                           | (Lead Orchestrator)   |
                                           +-----------+-----------+
                                                       |
                                                       v
                                           +-----------------------+
                                           |   itinerary_agent     |
                                           |    (Sightseeing)      |
                                           +-----------+-----------+
                                                       |
                                                       v
                                           +-----------------------+
                                           |  food_retail_agent    |
                                           |   (Dining/Retail)     |
                                           +-----------+-----------+
                                                       |
                                                       v
                                           +-----------------------+
                                           |  hospitality_agent    |
                                           |     (Lodging)         |
                                           +-----------+-----------+
                                                       |
                                                       v
                                           +-----------------------+
                                           |   purchasing_agent    |
                                           |   (Flights/Rental)    |
                                           +-----------+-----------+
                                                       |
                                                       v
                                           +-----------------------+
                                           |     quality_agent     |
                                           | (Budget & Quality QA) |
                                           +-----------+-----------+
                                                       |
                                      +----------------+----------------+
                                      | (Score >= 8 or Attempts >= 3)   | (Score < 8 & Attempts < 3)
                                      v                                 v
                           +--------------------+             +----------------------+
                           |    final_output    |             |  orchestrator_agent  |
                           | (Approved / Limit) |             |    (Surgical Fix)    |
                           +--------------------+             +----------------------+
```

---

## 🛠️ 2. Core Engineering Principles

### 2.1 Unified Quality Agent Evaluation
- Merged deterministic Python cost calculation with LLM-as-a-Judge persona/duration compliance into a single `quality_agent` node.
- Computes mathematical cost totals and feeds them into the evaluation model, assigning an objective score from `1 to 10`.
- If the score is $< 8$ and retry attempts $< 3$, surgical feedback is provided to the `orchestrator_agent` to route only to the components requiring adjustment.

### 2.2 Dual-Layer Frontend Ecosystem
1. **React 18 + Vite SPA (Vercel):**
   - Live WebSocket event streaming with real-time node progress.
   - Traffic light connection indicator (🟠 waking up, 🟢 active, 🔴 offline) with startup ping `/api/health`.
   - 5 CenterCanvas view modes: `Timeline`, `Map` (Google Maps multi-venue plotting & day filtering), `Hotels` (rich accommodation cards), `Bookings` (airfare, car rental, and attraction passes), and `Split View`.
2. **Streamlit Application:**
   - Interactive guided plan chatbot, live seasonal inspiration, full-width Google Maps Explorer, and Excel export.

### 2.3 Dependency Injection & Stateless Execution
- Node modules (`agents.py`, `evaluation.py`) use dependency injection (`init(llm, search_tool)`), avoiding global state coupling.
- WebSockets handle long-running multi-agent pipelines with 25–30s connection timeout allowances, overcoming serverless HTTP gateway limits.

---

## 📈 3. System Verification & Test Coverage

- **Pytest Suite:** 44 comprehensive test cases covering API routes, database transactions, LangGraph state machine, quality evaluations, geocoding, persona isolation, and seasonal refresh engines.
- **AST Code Validation:** AST syntax verification is enforced on all Python modules prior to check-in.
