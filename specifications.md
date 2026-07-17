# Travel Buddy — System Specifications & Architecture

## 1. Overview
**Travel Buddy** is an advanced multi-agent travel planning system built with **LangGraph** and **Google Gemini** (`gemini-3.1-flash-lite`). It orchestrates four specialized planning agents to create persona-aware 5-day travel itineraries backed by real-time web research via Tavily. The system features a dual-layer evaluation engine combining deterministic Python budget guardrails in **Singapore Dollars (SGD / S$)** (including airfare for custom group compositions, accommodation, dining, sightseeing, and optional self-drive car rentals) with a cognitive LLM-as-a-Judge quality check, custom persona builders, purchasing agents with direct booking links, interactive Google Maps & Pydeck multi-venue location visualizers in a clean **Light Mode UI**, and a follow-up Q&A Chat Assistant.

---

## 2. Technical Stack & Core Framework
- **Orchestration:** LangGraph (`StateGraph`) using a centralized `TypedDict` state.
- **LLM Layer:** `ChatGoogleGenerativeAI` (`gemini-3.1-flash-lite`).
- **Search Tooling:** `TavilySearchResults` bound directly to planning nodes, purchasing agents, and chat assistant.
- **Maps Grounding:** Pydeck 3D multi-pin scatterplot maps, OpenStreetMap, & Google Maps Embed API.
- **Frontend / Deployment:** Streamlit application (`app.py`) in Light Mode theme with native `st.secrets` integration.

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
   - Recommends real-world breakfast, lunch, dinner, and shopping spots matching the group size and persona in SGD.
   - Outputs `FOOD_RETAIL_TOTAL_SGD: [number]` at the end.

3. **Hospitality Agent (`hospitality_agent`):**
   - Sources 3 distinct hotel/accommodation options (at varied price points) in SGD suitable for group size.
   - Recommends one primary option matching persona and budget constraints.
   - Outputs `HOTEL_TOTAL_SGD: [number]` at the end.

4. **Purchasing & Booking Agent (`purchasing_agent`):**
   - Sourcing round-trip flight costs for the group composition (Adults, Children, Infants) from origin city to target destination.
   - Calculates daily car rental rates and toll/fuel estimates if `self_drive` mode is enabled.
   - Generates real, clickable HTTPS markdown URLs for Flights (Google Flights, Skyscanner), Hotels (Agoda, Booking.com), Car Rentals (Rentalcars.com, Klook), and Attraction Tickets (Klook, GetYourGuide).
   - Outputs `AIRFARE_TOTAL_SGD: [number]` and `CAR_RENTAL_TOTAL_SGD: [number]` at the end.

---

## 4. Group Composition & Transport Inclusion

- **Group Composition:** Configurable Adults (default 2), Children >2 yrs (default 1), and Infants <2 yrs (default 0).
- **Transport Inclusion:** Sums Sightseeing + Food & Retail + Accommodation + Airfare (for entire group) + Car Rental (if self-drive).
- **Default Currency:** Singapore Dollars (SGD / S$).
- Pure Python calculation (no LLM reasoning overhead).
- Parses numeric totals output by each planning node using regex (`LABEL_TOTAL_SGD: amount`).
- **No-Budget Option:** If `no_budget` mode is enabled, the budget guardrail displays cost breakdown but bypasses bounds testing (`status = 'budget_passed'`).

---

## 5. Persona Profiles (Built-In & Custom)

1. **Solo Traveler (`single`):** High tempo (4-6 activities/day), public transit/walking, street food (<$15), hostels/capsule hotels, nightlife & social spots.
2. **Couple's Getaway (`couple`):** Medium tempo (2-4 activities/day), relaxed mornings (>9:30 AM), aesthetic/romantic dining, boutique lodging, wraps up by 10:30 PM.
3. **Family Adventure (`family`):** Low tempo (2-3 activities/day), stroller-accessible, early nights (<7:30 PM), kid-friendly dining & playgrounds.
4. **Budget Backpacker (`backpacker`):** Ultra-lean spending, free/cheap sights, night markets, public transport/walking, social hostels, money-saving tips.
5. **Custom Persona (`custom`):** User-defined persona title, tempo, mobility preference, dining style, accommodation preference, and custom constraint rules.

---

## 6. Full Itinerary Location Mapping, Purchasing Links, Tabular Export & Chat Assistant

- **Full Itinerary Location Mapping:** `extract_all_itinerary_locations` parses all day-by-day sightseeing venues, geocodes their coordinates via Nominatim, and plots interactive pins for every single itinerary attraction on a Pydeck 3D map with day tooltips.
- **Light Mode Aesthetics:** Clean white background, slate sidebar, soft grey containers, dark text typography.
- **Purchasing Guide:** Direct HTTPS booking links for flights, accommodations, car rentals, and attraction tickets curated by the specialized purchasing agent.
- **Google Maps & OpenStreetMap:** Embedded interactive maps for destination attractions with step-by-step API key setup guide.
- **Tabular Itinerary:** Parses raw Markdown itinerary and purchasing data into a structured Pandas DataFrame (`Day`, `Theme`, `Time Slot`, `Activity Details`, `Est. Cost (SGD)`).
- **Travel Q&A Assistant:** Interactive chatbot tab using Gemini + Tavily search for follow-up questions, packing advice, and local travel tips.
- **Download Options:** One-click downloads for both **CSV Data** (`travel_itinerary.csv`), **Full Text Report** (`travel_recommendations.txt`), and **System Debug Logs** (`travel_buddy_debug.log`).
