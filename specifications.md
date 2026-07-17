# Travel Buddy — System Specifications & Architecture

## 1. Overview
**Travel Buddy** is an advanced multi-agent travel planning system built with **LangGraph** and **Google Gemini** (`gemini-3.1-flash-lite`). It orchestrates four specialized planning agents to create persona-aware 5-day travel itineraries backed by real-time web research via Tavily. The system features a dual-layer evaluation engine combining deterministic Python budget guardrails in **Singapore Dollars (SGD / S$)** (including airfare, accommodation, dining, sightseeing, and optional self-drive car rentals) with a cognitive LLM-as-a-Judge quality check, custom persona builders, purchasing agents with direct booking links, interactive Google Maps visualizers, and a follow-up Q&A Chat Assistant.

---

## 2. Technical Stack & Core Framework
- **Orchestration:** LangGraph (`StateGraph`) using a centralized `TypedDict` state.
- **LLM Layer:** `ChatGoogleGenerativeAI` (`gemini-3.1-flash-lite`).
- **Search Tooling:** `TavilySearchResults` bound directly to planning nodes, purchasing agents, and chat assistant.
- **Maps Grounding:** Google Maps Embed API & interactive location visualization.
- **Frontend / Deployment:** Streamlit application (`app.py`) with native `st.secrets` integration.

---

## 3. Multi-Agent Pipeline & Nodes

The system consists of four specialized generation nodes and a dual-layer evaluation process:

### 3.1 Planning & Purchasing Agents
1. **Itinerary Agent (`itinerary_agent`):**
   - Researches top attractions and activities for 5-day trips using real-time search.
   - Generates a day-by-day sightseeing plan with estimated costs in SGD and geographic clustering.
   - Outputs `SIGHTSEEING_TOTAL_SGD: [number]` at the end.

2. **Food & Retail Agent (`food_retail_agent`):**
   - Reads the itinerary's daily activity zones to ensure geographic proximity.
   - Recommends real-world breakfast, lunch, dinner, and shopping spots matching the user's persona in SGD.
   - Outputs `FOOD_RETAIL_TOTAL_SGD: [number]` at the end.

3. **Hospitality Agent (`hospitality_agent`):**
   - Sources 3 distinct hotel/accommodation options (at varied price points) in SGD convenient to activity zones.
   - Recommends one primary option matching persona and budget constraints.
   - Outputs `HOTEL_TOTAL_SGD: [number]` at the end.

4. **Purchasing & Booking Agent (`purchasing_agent`):**
   - Sourcing round-trip flight costs from origin city to target destination.
   - Calculates daily car rental rates and toll/fuel estimates if `self_drive` mode is enabled.
   - Generates real, clickable HTTPS markdown URLs for Flights (Google Flights, Skyscanner), Hotels (Agoda, Booking.com), Car Rentals (Rentalcars.com, Klook), and Attraction Tickets (Klook, GetYourGuide).
   - Outputs `AIRFARE_TOTAL_SGD: [number]` and `CAR_RENTAL_TOTAL_SGD: [number]` at the end.

---

## 4. Dual-Layer Evaluation Engine & Transport Inclusion

### Layer 1: Deterministic Budget Guardrail (`budget_guardrail`)
- **Transport Inclusion:** Sums Sightseeing + Food & Retail + Accommodation + Airfare + Car Rental (if self-drive).
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
- Audits the plan against all mandatory persona rules (built-in or custom).
- Outputs `VERDICT: [PASS/FAIL]`, `SCORE: [1-10]`, a rule-by-rule checklist with evidence, and an overall assessment.

---

## 5. Persona Profiles (Built-In & Custom)

1. **Solo Traveler (`single`):** High tempo (4-6 activities/day), public transit/walking, street food (<$15), hostels/capsule hotels, nightlife & social spots.
2. **Couple's Getaway (`couple`):** Medium tempo (2-4 activities/day), relaxed mornings (>9:30 AM), aesthetic/romantic dining, boutique lodging, wraps up by 10:30 PM.
3. **Family Adventure (`family`):** Low tempo (2-3 activities/day), stroller-accessible, early nights (<7:30 PM), kid-friendly dining & playgrounds.
4. **Budget Backpacker (`backpacker`):** Ultra-lean spending, free/cheap sights, night markets, public transport/walking, social hostels, money-saving tips.
5. **Custom Persona (`custom`):** User-defined persona title, tempo, mobility preference, dining style, accommodation preference, and custom constraint rules.

---

## 6. Visualization, Purchasing Links, Tabular Export & Chat Assistant

- **Purchasing Guide:** Direct HTTPS booking links for flights, accommodations, car rentals, and attraction tickets curated by the specialized purchasing agent.
- **Google Maps Integration:** Visualizes the destination and key daily activity locations using Google Maps Embed API / interactive iframe components. Includes step-by-step API key setup guide.
- **Tabular Itinerary:** Parses raw Markdown itinerary and purchasing data into a structured Pandas DataFrame (`Day`, `Theme`, `Time Slot`, `Activity Details`, `Est. Cost (SGD)`).
- **Travel Q&A Assistant:** Interactive chatbot tab using Gemini + Tavily search for follow-up questions, packing advice, and local travel tips.
- **Download Options:** One-click downloads for both **CSV Data** (`travel_itinerary.csv`), **Full Text Report** (`travel_recommendations.txt`), and **System Debug Logs** (`travel_buddy_debug.log`).
