# Travel Buddy — System Specifications & Architecture

## 1. Overview
**Travel Buddy** is an advanced multi-agent travel planning system built with **LangGraph**, **Google Gemini** (`gemini-3.1-flash-lite`), **FastAPI**, **Streamlit**, and **React / Vite**. It orchestrates specialized planning agents to create persona-aware travel itineraries backed by real-time web research via Tavily. The system features a unified **Quality Agent** combining deterministic Python budget calculations in **Singapore Dollars (SGD / S$)** (including airfare for custom group compositions, accommodation, dining, sightseeing, and optional self-drive car rentals) with cognitive LLM evaluation scoring compliance from `1 to 10`, custom persona builders, purchasing agents with direct booking links, interactive Google Maps multi-venue location visualizers in a clean **Light Mode UI**, a follow-up Q&A Chat Assistant, and persistent trip-saving capabilities via Supabase.

---

## 2. Technical Stack & Core Framework
- **Orchestration:** LangGraph (`StateGraph`) using a centralized `TypedDict` state.
- **LLM Layer:** `ChatGoogleGenerativeAI` (`gemini-3.1-flash-lite`).
- **Search Tooling:** `TavilySearchResults` bound directly to planning nodes, purchasing agents, and chat assistant.
- **Backend Service:** FastAPI REST & WebSocket streaming endpoints hosted on Render.
- **Frontend Layers:** 
  1. React 18 / Vite Single Page Application deployed on Vercel (`https://aitravelbu88y.vercel.app/`).
  2. Streamlit Cloud Application (`https://aitripbuddy.streamlit.app/`).
- **Maps Grounding:** Embedded Google Maps Location Explorer with multi-venue extraction and day-by-day filtering.
- **Persistence Layer:** Supabase via `core/db.py` to save/load full JSON state records.

---

## 3. Multi-Agent Pipeline & Nodes

The system consists of a central Planner Lead Orchestrator coordinating specialized generation nodes and a unified Quality Agent:

### 3.1 Orchestration, Planning & Purchasing Agents
1. **Planner Lead Orchestrator (`orchestrator_agent`):**
   - Serves as the graph entry point and project coordinator.
   - Enforces invariant requirement constraints (origin, destination, duration, group composition, SGD currency).
   - On retry loops, reviews quality consultant feedback and issues surgical, non-destructive directives to downstream agents to preserve valid outputs.

2. **Itinerary Agent (`itinerary_agent`):**
   - Researches top attractions and activities for trips using real-time search.
   - Generates a day-by-day sightseeing plan with estimated costs in SGD and geographic clustering.
   - Outputs `SIGHTSEEING_TOTAL_SGD: [number]` at the end.

3. **Food & Retail Agent (`food_retail_agent`):**
   - Reads the itinerary's daily activity zones to ensure geographic proximity.
   - Recommends real-world breakfast, lunch, dinner, and shopping spots matching the group size and persona in SGD.
   - Outputs `FOOD_RETAIL_TOTAL_SGD: [number]` at the end.

4. **Hospitality Agent (`hospitality_agent`):**
   - Sources 3 distinct hotel/accommodation options (at varied price points) in SGD suitable for group size.
   - Recommends one primary option matching persona and budget constraints.
   - Outputs `HOTEL_TOTAL_SGD: [number]` at the end.

5. **Purchasing & Booking Agent (`purchasing_agent`):**
   - Sourcing round-trip flight costs for the group composition (Adults, Children, Infants) from origin city to target destination.
   - Calculates daily car rental rates and toll/fuel estimates if `self_drive` mode is enabled.
   - Generates real, clickable HTTPS markdown URLs for Flights (Google Flights, Skyscanner), Hotels (Agoda, Booking.com), Car Rentals (Rentalcars.com, Tabirai), and Attraction Tickets (Klook, GetYourGuide).
   - Outputs `AIRFARE_TOTAL_SGD: [number]` and `CAR_RENTAL_TOTAL_SGD: [number]` at the end.

6. **Quality Agent (`quality_agent`):**
   - Combines programmatic budget computation with an LLM judge evaluating duration, budget adherence, and persona fit.
   - Scores the plan on a `1 to 10` scale.
   - If score is $\ge 8$ or retry limit is reached (3 attempts), routes to `final_output`; otherwise routes feedback back to `orchestrator_agent`.

---

## 4. Group Composition & Transport Inclusion
- **Group Composition:** Configurable Adults (default 2), Children >2 yrs (default 1), and Infants <2 yrs (default 0).
- **Transport Inclusion:** Sums Sightseeing + Food & Retail + Accommodation + Airfare (for entire group) + Car Rental (if self-drive).
- **Default Currency:** Singapore Dollars (SGD / S$).
- **No-Budget Option:** If `no_budget` mode is enabled, the budget guardrail displays cost breakdown but bypasses bounds testing (`status = 'approved'`).
