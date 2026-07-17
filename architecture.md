# Travel Buddy — Engineering Architecture & System Improvement Roadmap

## 🏛️ 1. Current System Architecture

Travel Buddy is built on a modular, multi-agent architecture powered by **LangGraph**, **Google Gemini** (`gemini-3.1-flash-lite`), **Tavily Search API**, and **Streamlit**.

```
                           +------------------------+
                           |   Streamlit UI App     |
                           |       (app.py)         |
                           +-----------+------------+
                                       |
                                       v
                           +------------------------+
                           |  LangGraph StateGraph  |
                           |    (core/graph.py)     |
                           +-----------+------------+
                                       |
     +-------------------+-------------+---------------+--------------------+
     |                   |                             |                    |
     v                   v                             v                    v
+----+------------+ +----+------------+       +--------+--------+  +--------+--------+
| itinerary_agent | |food_retail_agent|       |hospitality_agent|  |purchasing_agent |
| (Sightseeing)   | | (Dining/Retail) |       | (Lodging)       |  |(Flights/Rental) |
+----+------------+ +----+------------+       +--------+--------+  +--------+--------+
     |                   |                             |                    |
     +-------------------+-------------+---------------+--------------------+
                                       |
                                       v
                           +------------------------+
                           |    budget_guardrail    |
                           | (Python Cost Summation)|
                           +-----------+------------+
                                       |
                      +----------------+----------------+
                      | (Pass / Infinite)               | (Retry < 3)
                      v                                 v
           +--------------------+             +-------------------+
           |   agent_as_judge   |             |  itinerary_agent  |
           | (Quality Inspector)|             |   (Retry Loop)    |
           +----------+---------+             +-------------------+
                      |
                      v
           +--------------------+
           |    final_output    |
           +--------------------+
```

---

## 🛠️ 2. Core Engineering Principles

### 2.1 State Immutability & Concurrency
- `TravelBuddyState` uses `TypedDict` with `Annotated[list[str], operator.add]` for thread-safe accumulation of critique history.
- Pure node functions accept state dictionary copies and return delta updates.

### 2.2 Dual-Layer Guardrail Architecture
- **Layer 1 (Deterministic):** Pure Python execution (zero LLM token overhead) for cost parsing and range checking.
- **Layer 2 (Cognitive):** LLM-as-a-Judge inspects persona rules compliance only after budget validation passes.

### 2.3 Dependency Injection Pattern
- Node modules (`agents.py`, `evaluation.py`) expose `init(llm, search_tool)` functions to avoid global state coupling and enable easy unit testing with mock LLMs.

---

## 📈 3. Recommended Engineering Improvements

### 3.1 Structured Outputs via Pydantic Schemas
- **Current State:** Relies on regex pattern matching (`SIGHTSEEING_TOTAL_SGD: [number]`).
- **Proposed Improvement:** Enforce Pydantic schemas using LangChain `.with_structured_output(ItinerarySchema)` to guarantee 100% type-safe JSON returns from LLMs, eliminating regex parsing edge cases.

```python
class ActivityItem(BaseModel):
    time_slot: str
    activity: str
    est_cost_sgd: float

class DailyItinerary(BaseModel):
    day_number: int
    theme: str
    activities: List[ActivityItem]
    sightseeing_total_sgd: float
```

### 3.2 Async Parallel Agent Execution
- **Current State:** Agents run sequentially (`itinerary` -> `food_retail` -> `hospitality` -> `purchasing`).
- **Proposed Improvement:** Once `itinerary_agent` defines daily activity zones, run `food_retail_agent`, `hospitality_agent`, and `purchasing_agent` concurrently via `asyncio.gather()`, reducing total execution latency by **~50%**.

### 3.3 Response Caching & Rate Limit Resilience
- **LLM Caching:** Implement `langchain.caching.InMemoryCache` or Redis caching for Tavily web search queries to prevent redundant API calls for identical destination queries within short timeframes.
- **Exponential Backoff:** Wrap LLM invocations with `tenacity` retry logic to gracefully handle temporary API rate limits (HTTP 429) or network timeouts.

### 3.4 Telemetry & Distributed Tracing
- Integrate **LangSmith** or OpenTelemetry tracing by configuring environment variables (`LANGCHAIN_TRACING_V2=true`). This provides deep visibility into LLM token counts, latency per node, and prompt efficiency.

### 3.5 Automated Testing Suite
- Create `tests/` directory with `pytest` test suites:
  - `test_utils.py`: Unit test regex cost extraction and DataFrame parsing.
  - `test_guardrail.py`: Unit test budget bounds (80-90% SGD calculation, no_budget bypass, 3-strike escalation).
  - `test_graph.py`: Integration test graph compilation and routing logic with synthetic state.

---

## 📜 4. Future Code Modification Directives
Whenever modifying or expanding the codebase in future turns:
1. Maintain Light Mode aesthetic tokens in `app.py` and `.streamlit/config.toml`.
2. Keep `TravelBuddyState` schema backwards compatible.
3. Always validate Python syntax AST before committing code changes.
4. Ensure all external booking URLs use HTTPS markdown link format.
