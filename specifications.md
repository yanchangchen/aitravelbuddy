# Travel Buddy — System Specifications & Architecture

## 1. Overview
**Travel Buddy** is an advanced multi-agent travel planning system built with **LangGraph** and **Google Gemini** (`gemini-3.1-flash-lite`). It orchestrates three specialized planning agents to create persona-aware travel itineraries backed by real-time web research via Tavily. The system features a dual-layer evaluation engine combining deterministic Python budget guardrails in **Singapore Dollars (SGD / S$)** with a cognitive LLM-as-a-Judge quality check.

---

## 2. Technical Stack & Core Framework
- **Orchestration:** LangGraph (`StateGraph`) using a centralized `TypedDict` state.
- **LLM Layer:** `ChatGoogleGenerativeAI` (`gemini-3.1-flash-lite`).
- **Search Tooling:** `TavilySearchResults` bound directly to planning nodes for real-time web research.
- **Maps Grounding:** Google Maps Embed API & interactive location visualization.
- **Frontend / Deployment:** Streamlit application (`app.py`) with native `st.secrets` integration.

---

## 3. Multi-Agent Pipeline & Nodes

The system consists of three specialized generation nodes and a dual-layer evaluation process:

### 3.1 Planning Agents
1. **Itinerary Agent (`itinerary_agent`):**
   - Researches top attractions and activities using real-time search.
   - Generates a day-by-day sightseeing plan with estimated costs in SGD and geographic clustering.
   - Allocates ~25–30% of total budget.
   - Outputs `SIGHTSEEING_TOTAL_SGD: [number]` at the end.

2. **Food & Retail Agent (`food_retail_agent`):**
   - Reads the itinerary's daily activity zones to ensure geographic proximity.
   - Recommends real-world breakfast, lunch, dinner, and shopping spots matching the user's persona in SGD.
   - Allocates ~30–35% of total budget.
   - Outputs `FOOD_RETAIL_TOTAL_SGD: [number]` at the end.

3. **Hospitality Agent (`hospitality_agent`):**
   - Sources 3 distinct hotel/accommodation options (at varied price points) in SGD convenient to activity zones.
   - Recommends one primary option matching persona and budget constraints.
   - Allocates ~35–40% of total budget.
   - Outputs `HOTEL_TOTAL_SGD: [number]` at the end.

---

## 4. Dual-Layer Evaluation Engine & Currency Defaults

### Layer 1: Deterministic Budget Guardrail (`budget_guardrail`)
- **Default Currency:** Singapore Dollars (SGD / S$).
- Pure Python calculation (no LLM reasoning overhead).
- Parses numeric totals output by each planning node using regex (`LABEL_TOTAL_SGD: amount`).
- **No-Budget Option:** If `no_budget` mode is enabled, the budget guardrail displays cost breakdown but bypasses bounds testing (`status = 'budget_passed'`).
- **Bounded Target Range:** When a budget is set, total estimated cost must land strictly within **80% to 90%** of the user's SGD budget. Converts SGD to USD reference (`1 SGD = 0.74 USD`).
- **Retry Loop & Strike-Three Rule:**
  - If total cost < 80% or > 90%, increments `budget_attempts`.
  - Appends actionable feedback to `critique_history` (via `operator.add`) and routes back to `itinerary_agent`.
  - If `budget_attempts >= 3` and budget is still violated, routes immediately to terminal fallback `budget_busted_fallback` setting `status = 'budget_busted'`.

### Layer 2: Cognitive Agent-as-Judge (`agent_as_judge`)
- Runs **only** after the deterministic budget check passes (`status == 'budget_passed'`).
- Prompts an independent LLM call acting as an impartial quality inspector.
- Audits the plan against all mandatory persona rules.
- Outputs `VERDICT: [PASS/FAIL]`, `SCORE: [1-10]`, a rule-by-rule checklist with evidence, and an overall assessment.

---

## 5. State Schema (`TravelBuddyState`)

```python
class TravelBuddyState(TypedDict):
    destination: str           # Target city/region (e.g., "Tokyo, Japan")
    budget: float              # Total trip budget in SGD (S$)
    no_budget: bool            # True if flexible / unlimited budget mode selected
    currency: str              # Default "SGD"
    dates: str                 # Date range string
    persona: str               # "single" | "couple" | "family"
    itinerary: str             # Generated sightseeing output in SGD
    food_and_retail: str       # Generated dining/shopping output in SGD
    hotel_recommendations: str # Generated lodging output in SGD
    budget_breakdown: str      # Calculated financial report in SGD & USD ref
    budget_attempts: int       # Iteration counter (max 3)
    critique_history: Annotated[list[str], operator.add] # Accumulated feedback
    status: str                # "planning" | "budget_passed" | "approved" | "budget_busted"
    judge_verdict: str         # LLM-as-a-Judge report
```

---

## 6. Visualization & Tabular Export

- **Google Maps Integration:** Visualizes the destination and key daily activity locations using Google Maps Embed API / interactive iframe components.
- **Tabular Itinerary:** Parses raw Markdown itinerary into a structured Pandas DataFrame (`Day`, `Theme`, `Time Slot`, `Activity Details`, `Est. Cost (SGD)`).
- **Download Options:** One-click downloads for both **CSV Data** (`travel_itinerary.csv`) and **Full Text Report** (`travel_recommendations.txt`).
