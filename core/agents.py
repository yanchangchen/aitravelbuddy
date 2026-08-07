"""Planning agent nodes for the Travel Buddy graph with search caching, exponential backoff retries, and structured schemas."""

import time
from langchain_core.messages import HumanMessage
from .personas import PERSONA_PROFILES
from .utils import ensure_str, get_persona_context, get_critique_context
from .logger import get_logger

logger = get_logger("agents")

# Module-level references (set by init)
_llm = None
_search_tool = None

# In-memory search cache to prevent redundant web searches
_search_cache = {}


def init(llm, search_tool):
    """Initialize the module with LLM and search tool instances."""
    global _llm, _search_tool
    _llm = llm
    _search_tool = search_tool
    logger.info("Agents module initialized with LLM and Tavily search tool (Caching & Retries enabled).")


def _search(query: str) -> str:
    """Run a Tavily search with in-memory caching to eliminate redundant network roundtrips."""
    clean_query = query.strip().lower()
    if clean_query in _search_cache:
        logger.info(f"[Search Cache Hit] Query: '{query}'")
        return _search_cache[clean_query]

    logger.info(f"[Executing Web Search] Query: '{query}'")
    try:
        results = _search_tool.invoke(query)
        if isinstance(results, list):
            formatted_res = "\n".join(
                f"- {r.get('content', r.get('snippet', ''))}" for r in results
            )
        else:
            formatted_res = str(results)

        _search_cache[clean_query] = formatted_res
        logger.info(f"[Search Cached] Query: '{query}' ({len(results) if isinstance(results, list) else 1} snippets)")
        return formatted_res
    except Exception as e:
        logger.warning(f"Web search failed: {e}. Falling back to LLM training knowledge.")
        return f"(Search unavailable: {e}. Use your training knowledge.)"


def _invoke_llm_with_retry(prompt: str, max_retries: int = 3) -> str:
    """Invoke LLM with exponential backoff retry resilience for rate limits and network glitches."""
    for attempt in range(1, max_retries + 1):
        try:
            logger.debug(f"LLM Invocation attempt {attempt}/{max_retries}...")
            response = _llm.invoke([HumanMessage(content=prompt)])
            return ensure_str(response.content)
        except Exception as e:
            logger.warning(f"LLM invocation attempt {attempt} failed: {e}")
            if attempt == max_retries:
                logger.error("LLM max retries reached. Raising exception.")
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s


def itinerary_agent(state: dict) -> dict:
    """Generate a day-by-day sightseeing itinerary with cost estimates in SGD."""
    origin = state.get("origin", "Singapore")
    destination = state.get("destination", "Tokyo, Japan")
    logger.info(f"[Itinerary Agent] Starting planning from origin='{origin}' to destination='{destination}'")
    persona_ctx = get_persona_context(state, PERSONA_PROFILES)
    critique_ctx = get_critique_context(state)
    currency = state.get("currency", "SGD")
    no_budget = state.get("no_budget", False)
    self_drive = state.get("self_drive", False)
    drive_note = "Traveler is SELF-DRIVING via car rental. Focus activities on scenic drives, parking access, and road trips." if self_drive else "Traveler relies on public transit/taxis."

    budget_line = "FLEXIBLE / UNLIMITED BUDGET (Focus on best experiences)" if no_budget else f"TOTAL TRIP BUDGET: S$ {state['budget']:.2f} {currency}\nBUDGET ALLOCATION FOR SIGHTSEEING: Approximately 20-25% of total budget"

    search_context = _search(
        f"top attractions things to do in {destination} {state['dates']}"
    )

    num_days = state.get("num_days", 5)

    orchestrator_directive = ""
    user_prefs = state.get("user_preferences") or {}
    if isinstance(user_prefs, dict) and "orchestrator_directive" in user_prefs:
        orchestrator_directive = f"\nPLANNER LEAD ORCHESTRATOR DIRECTIVE:\n{user_prefs['orchestrator_directive']}\n"

    prompt = (
        f"You are an expert travel itinerary planner.\n\n"
        f"{persona_ctx}\n\n"
        f"ORIGIN: {origin}\n"
        f"DESTINATION: {destination}\n"
        f"TRAVEL DATES: {state['dates']} ({num_days} Days Total)\n"
        f"NUMBER OF DAYS: {num_days}\n"
        f"TRANSPORT MODE: {drive_note}\n"
        f"{budget_line}\n"
        f"{critique_ctx}\n"
        f"{orchestrator_directive}\n"
        f"REAL-TIME RESEARCH (from web search):\n{search_context}\n\n"
        f"GENERATE a detailed day-by-day itinerary covering ALL {num_days} DAYS (Day 1 through Day {num_days}) following this EXACT format:\n\n"
        f"## Day N: [Theme/Title]\n"
        f"- **[Time Block 1] (TIME):** [Activity] — Est. cost: S$XX\n"
        f"- **[Time Block 2] (TIME):** [Activity] — Est. cost: S$XX\n"
        f"- **[Time Block ...] (TIME):** [Activity] — Est. cost: S$XX\n"
        f"- Daily transport/tolls: S$XX\n\n"
        f"**Sightseeing Total: S$[sum]**\n\n"
        f"At the very end, include a line:\n"
        f"SIGHTSEEING_TOTAL_SGD: [number]\n\n"
        f"Rules:\n"
        f"- You MUST generate exactly {num_days} days (from Day 1 through Day {num_days}). Do not skip, omit, or shorten any days under any circumstances, including on retries.\n"
        f"- On retries, KEEP ALL DAYS 1 THROUGH {num_days} FULLY INTACT. Do not compress or reduce the daily schedule; only refine activities specified in feedback.\n"
        f"- Adapt the Time Blocks (Morning/Afternoon/Evening) based on the persona's schedule constraints (e.g. Business traveler only has free time in Evenings/Mornings).\n"
        f"- Be realistic with prices in Singapore Dollars (SGD / S$) for {destination}\n"
        f"- Follow persona pacing rules STRICTLY\n"
        f"- Include specific venue/attraction names, not generic placeholders"
    )

    result_text = _invoke_llm_with_retry(prompt)
    logger.info(f"[Itinerary Agent Output] ({len(result_text)} chars):\n{result_text}")

    return {"itinerary": result_text, "status": "planning"}


def food_retail_agent(state: dict) -> dict:
    """Curate dining and retail recommendations in SGD aligned to daily zones."""
    destination = state.get("destination", "Tokyo, Japan")
    logger.info(f"[Food & Retail Agent] Curating dining for destination='{destination}'")
    persona_ctx = get_persona_context(state, PERSONA_PROFILES)
    critique_ctx = get_critique_context(state)
    persona_key = state["persona"].lower().strip()
    if persona_key == "custom" and "custom_persona_profile" in state and isinstance(state["custom_persona_profile"], dict):
        profile = state["custom_persona_profile"]
    else:
        profile = PERSONA_PROFILES.get(persona_key, PERSONA_PROFILES["family"])

    currency = state.get("currency", "SGD")
    no_budget = state.get("no_budget", False)
    budget_line = "FLEXIBLE / UNLIMITED BUDGET (Focus on best dining)" if no_budget else f"TOTAL TRIP BUDGET: S$ {state['budget']:.2f} {currency}\nBUDGET ALLOCATION FOR FOOD & RETAIL: Approximately 25-30% of total budget"

    num_days = state.get("num_days", 5)

    orchestrator_directive = ""
    user_prefs = state.get("user_preferences") or {}
    if isinstance(user_prefs, dict) and "orchestrator_directive" in user_prefs:
        orchestrator_directive = f"\nPLANNER LEAD ORCHESTRATOR DIRECTIVE:\n{user_prefs['orchestrator_directive']}\n"

    search_context = _search(
        f"best {profile.get('dining_style', 'local food')} restaurants in {destination}"
    )

    prompt = (
        f"You are a local food and retail expert for {destination}.\n\n"
        f"{persona_ctx}\n\n"
        f"{budget_line}\n"
        f"{critique_ctx}\n"
        f"{orchestrator_directive}\n"
        f"THE SIGHTSEEING ITINERARY (align your recommendations to these daily zones):\n"
        f"{state.get('itinerary', 'Not yet available')}\n\n"
        f"REAL-TIME RESEARCH (from web search):\n{search_context}\n\n"
        f"GENERATE food and retail recommendations following this EXACT format:\n\n"
        f"## Day N Food & Shopping\n"
        f"- **Breakfast:** [Restaurant/Cafe Name] \u2014 [Cuisine type] \u2014 Est. S$XX per person\n"
        f"- **Lunch:** [Restaurant Name] \u2014 [Cuisine type] \u2014 Est. S$XX per person\n"
        f"- **Dinner:** [Restaurant Name] \u2014 [Cuisine type] \u2014 Est. S$XX per person\n"
        f"- **Shopping/Retail:** [Market/Shop Name] \u2014 [What to buy] \u2014 Est. S$XX budget\n\n"
        f"**Daily Food & Retail Total: S$XX**\n\n"
        f"At the very end, include a line:\n"
        f"FOOD_RETAIL_TOTAL_SGD: [number]\n\n"
        f"Rules:\n"
        f"- You MUST generate food and retail recommendations for EVERY SINGLE DAY (from Day 1 through Day {num_days}). Do not skip or omit any days.\n"
        f"- Recommendations MUST be physically near that specific day's sightseeing locations\n"
        f"- Follow persona dining style STRICTLY\n"
        f"- Include specific real restaurant/shop names\n"
        f"- Prices must be realistic in Singapore Dollars (SGD / S$)"
    )

    result_text = _invoke_llm_with_retry(prompt)
    logger.info(f"[Food & Retail Agent Output] ({len(result_text)} chars):\n{result_text}")

    return {"food_and_retail": result_text}


def hospitality_agent(state: dict) -> dict:
    """Source hotel/accommodation options in SGD matching persona and budget."""
    destination = state.get("destination", "Tokyo, Japan")
    logger.info(f"[Hospitality Agent] Sourcing lodging for destination='{destination}'")
    persona_ctx = get_persona_context(state, PERSONA_PROFILES)
    critique_ctx = get_critique_context(state)
    persona_key = state["persona"].lower().strip()
    if persona_key == "custom" and "custom_persona_profile" in state and isinstance(state["custom_persona_profile"], dict):
        profile = state["custom_persona_profile"]
    else:
        profile = PERSONA_PROFILES.get(persona_key, PERSONA_PROFILES["family"])

    currency = state.get("currency", "SGD")
    no_budget = state.get("no_budget", False)
    budget_line = "FLEXIBLE / UNLIMITED BUDGET (Focus on best lodging)" if no_budget else f"TOTAL TRIP BUDGET: S$ {state['budget']:.2f} {currency}\nBUDGET ALLOCATION FOR ACCOMMODATION: Approximately 30-35% of total budget"

    num_days = state.get("num_days", 5)

    orchestrator_directive = ""
    user_prefs = state.get("user_preferences") or {}
    if isinstance(user_prefs, dict) and "orchestrator_directive" in user_prefs:
        orchestrator_directive = f"\nPLANNER LEAD ORCHESTRATOR DIRECTIVE:\n{user_prefs['orchestrator_directive']}\n"

    search_context = _search(
        f"best {profile.get('accommodation', 'hotels')} in {destination} {state['dates']}"
    )

    prompt = (
        f"You are an expert hospitality broker for {destination}.\n\n"
        f"{persona_ctx}\n\n"
        f"{budget_line}\n"
        f"TRAVEL DATES: {state['dates']}\n"
        f"{critique_ctx}\n"
        f"{orchestrator_directive}\n"
        f"THE SIGHTSEEING ITINERARY (pick hotels near these activity zones):\n"
        f"{state.get('itinerary', 'Not yet available')}\n\n"
        f"REAL-TIME RESEARCH (from web search):\n{search_context}\n\n"
        f"GENERATE accommodation recommendations matching the activity zones of the itinerary above following this EXACT format:\n\n"
        f"### Option 1: [Hotel Name] ⭐⭐⭐⭐\n"
        f"- **Location:** [Neighborhood/Area matching itinerary activity zones]\n"
        f"- **Why it fits:** [1-2 sentences on itinerary & persona match]\n"
        f"- **Nightly rate:** S$XX SGD\n"
        f"- **Total for stay:** S$XX SGD\n"
        f"- **Key amenities:** [list relevant amenities]\n\n"
        f"### Option 2: [Hotel Name] ⭐⭐⭐\n"
        f"(same format)\n\n"
        f"### Option 3: [Hotel Name] (Budget Alternative)\n"
        f"(same format)\n\n"
        f"**🏨 RECOMMENDED OPTION: [Name] — Total: S$XX SGD**\n\n"
        f"At the very end, include a line:\n"
        f"HOTEL_TOTAL_SGD: [number]\n\n"
        f"(Use the RECOMMENDED option's total for the number above.)\n\n"
        f"Rules:\n"
        f"- Hotels MUST be physically located in the exact neighborhood/zones specified in the itinerary above\n"
        f"- Hotels MUST match the persona accommodation style\n"
        f"- At least 3 options at different price points\n"
        f"- Prices must be realistic in Singapore Dollars (SGD / S$)"
    )

    result_text = _invoke_llm_with_retry(prompt)
    logger.info(f"[Hospitality Agent Output] ({len(result_text)} chars):\n{result_text}")

    return {"hotel_recommendations": result_text}


def purchasing_agent(state: dict) -> dict:
    """Specialized Purchasing & Booking Agent."""
    origin = state.get("origin", "Singapore")
    destination = state.get("destination", "Tokyo, Japan")
    self_drive = state.get("self_drive", False)

    logger.info(f"[Purchasing Agent] Sourcing booking links & transport costs from origin='{origin}' to destination='{destination}', self_drive={self_drive}")

    flight_search = _search(f"flights from {origin} to {destination} {state['dates']} prices airlines")
    hotel_search = _search(f"hotel booking deals {destination}")

    car_search = ""
    if self_drive:
        car_search = _search(f"car rental in {destination} daily rates companies")

    num_days = state.get("num_days", 5)
    prompt = (
        f"You are a specialized Purchasing & Travel Booking Expert.\n\n"
        f"ORIGIN / SOURCE CITY: {origin}\n"
        f"DESTINATION: {destination}\n"
        f"TRAVEL DATES: {state['dates']} ({num_days} Days)\n"
        f"SELF-DRIVE OPTION: {'YES (Include Car Rental)' if self_drive else 'NO (No Car Rental Needed)'}\n"
        f"ITINERARY & SIGHTSEEING:\n{state.get('itinerary', 'N/A')}\n\n"
        f"RECOMMENDED HOTEL:\n{state.get('hotel_recommendations', 'N/A')}\n\n"
        f"REAL-TIME FLIGHT RESEARCH:\n{flight_search}\n\n"
        f"REAL-TIME HOTEL RESEARCH:\n{hotel_search}\n\n"
        f"{'REAL-TIME CAR RENTAL RESEARCH:\n' + car_search if self_drive else ''}\n\n"
        f"Your task is to generate a comprehensive **Purchasing & Booking Guide** with real clickable HTTPS markdown URLs.\n\n"
        f"FORMAT REQUIREMENT:\n\n"
        f"### ✈️ Flights & Airfare (Round-Trip from {origin} to {destination})\n"
        f"- **Estimated Airfare:** S$XX SGD per person (Total: S$XX SGD)\n"
        f"- **Recommended Airlines:** [Airlines]\n"
        f"- **Booking Links:**\n"
        f"  - [Google Flights - {origin} to {destination}](https://www.google.com/travel/flights?q=flights+from+{origin}+to+{destination})\n"
        f"  - [Skyscanner Airfare Comparison](https://www.skyscanner.com/routes/sin/{destination[:3].lower()})\n"
        f"  - [Singapore Airlines / Local Carrier Portal](https://www.singaporeair.com)\n\n"
        f"### 🏨 Hotel & Accommodation Booking\n"
        f"- **Selected Hotel:** [Recommended Hotel Name]\n"
        f"- **Booking Links:**\n"
        f"  - [Agoda Booking Portal](https://www.agoda.com)\n"
        f"  - [Booking.com Deals](https://www.booking.com)\n"
        f"  - [Trip.com Accommodation](https://www.trip.com)\n\n"
        f"{'### 🚗 Self-Drive & Car Rental Guide\n' + f'- **Estimated Car Rental:** S$XX SGD/day (Total: S$XX SGD for {num_days} days)\n- **Estimated Fuel & Tolls:** S$XX SGD\n- **Recommended Car Rental Portals:**\n  - [Rentalcars.com](https://www.rentalcars.com)\n  - [Klook Car Rental Deals](https://www.klook.com)\n  - [Hertz / Local Car Rental](https://www.hertz.com)\n\n' if self_drive else ''}"
        f"### 🎫 Attraction Tickets & Tours\n"
        f"- **Recommended Booking Sites:**\n"
        f"  - [Klook Attraction Tickets](https://www.klook.com)\n"
        f"  - [GetYourGuide Experiences](https://www.getyourguide.com)\n"
        f"  - [TripAdvisor Tours](https://www.tripadvisor.com)\n\n"
        f"At the very end, include these EXACT lines:\n"
        f"AIRFARE_TOTAL_SGD: [number]\n"
        f"{'CAR_RENTAL_TOTAL_SGD: [number]\n' if self_drive else 'CAR_RENTAL_TOTAL_SGD: 0\n'}"
        f"\nRules:\n"
        f"- Provide realistic flight prices in SGD from {origin}\n"
        f"- Every booking link MUST be a valid markdown link with HTTPS URL\n"
        f"- If self-drive is Yes, calculate car rental + fuel/tolls in SGD"
    )

    result_text = _invoke_llm_with_retry(prompt)
    logger.info(f"[Purchasing Agent Output] ({len(result_text)} chars):\n{result_text}")

    return {"purchasing_guide": result_text}


def orchestrator_agent(state: dict) -> dict:
    """Planner Lead Orchestrator Agent.
    
    Acts as the project manager:
    - Lock and enforce global requirements (destination, num_days, travelers_summary, currency).
    - Checks critique history and creates surgical instructions for down-stream agents.
    """
    logger.info(f"[Orchestrator] Auditing requirements. destination='{state.get('destination')}', num_days={state.get('num_days', 5)}")
    
    # Strictly lock the days and core parameters
    num_days = state.get("num_days", 5)
    if num_days <= 1:
        num_days = 5
        
    critique_history = state.get("critique_history", [])
    
    if critique_history:
        latest_critique = critique_history[-1]
        logger.info(f"[Orchestrator] Active critique found: '{latest_critique}'")
        
        # Prepare surgical routing directives to guide specific agents
        surgical_directive = (
            f"The LLM quality judge provided feedback:\n"
            f"'{latest_critique}'\n\n"
            f"You MUST refine your recommendations to address this feedback. "
            f"Do NOT shorten, compress, or rewrite other valid sections. Keep all {num_days} days fully detailed."
        )
        
        user_prefs = state.get("user_preferences") or {}
        if not isinstance(user_prefs, dict):
            user_prefs = {"rules": str(user_prefs)}
            
        return {
            "num_days": num_days,
            "status": "planning",
            "user_preferences": {
                **user_prefs,
                "orchestrator_directive": surgical_directive
            }
        }
    
    return {
        "num_days": num_days,
        "status": "planning"
    }
