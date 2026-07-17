"""Planning agent nodes for the Travel Buddy graph with troubleshooting logging."""

from langchain_core.messages import HumanMessage
from .personas import PERSONA_PROFILES
from .utils import ensure_str, get_persona_context, get_critique_context
from .logger import get_logger

logger = get_logger("agents")

# Module-level references (set by init)
_llm = None
_search_tool = None


def init(llm, search_tool):
    """Initialize the module with LLM and search tool instances."""
    global _llm, _search_tool
    _llm = llm
    _search_tool = search_tool
    logger.info("Agents module initialized with LLM and Tavily search tool.")


def _search(query: str) -> str:
    """Run a Tavily search and return formatted context string."""
    logger.info(f"Executing web search query: '{query}'")
    try:
        results = _search_tool.invoke(query)
        if isinstance(results, list):
            logger.info(f"Web search returned {len(results)} result snippets.")
            return "\n".join(
                f"- {r.get('content', r.get('snippet', ''))}" for r in results
            )
        logger.info("Web search returned non-list result.")
        return str(results)
    except Exception as e:
        logger.warning(f"Web search failed: {e}. Falling back to LLM training knowledge.")
        return f"(Search unavailable: {e}. Use your training knowledge.)"


def itinerary_agent(state: dict) -> dict:
    """Generate a day-by-day sightseeing itinerary with cost estimates in SGD."""
    logger.info(f"[Itinerary Agent] Starting planning for destination='{state['destination']}', dates='{state['dates']}', persona='{state['persona']}'")
    persona_ctx = get_persona_context(state, PERSONA_PROFILES)
    critique_ctx = get_critique_context(state)
    currency = state.get("currency", "SGD")
    no_budget = state.get("no_budget", False)
    budget_line = "FLEXIBLE / UNLIMITED BUDGET (Focus on best experiences)" if no_budget else f"TOTAL TRIP BUDGET: S$ {state['budget']:.2f} {currency}\nBUDGET ALLOCATION FOR SIGHTSEEING: Approximately 25-30% of total budget"

    search_context = _search(
        f"top attractions things to do in {state['destination']} {state['dates']}"
    )

    prompt = (
        f"You are an expert travel itinerary planner.\n\n"
        f"{persona_ctx}\n\n"
        f"DESTINATION: {state['destination']}\n"
        f"TRAVEL DATES: {state['dates']}\n"
        f"{budget_line}\n"
        f"{critique_ctx}\n\n"
        f"REAL-TIME RESEARCH (from web search):\n{search_context}\n\n"
        f"GENERATE a detailed day-by-day itinerary following this EXACT format:\n\n"
        f"## Day N: [Theme/Title]\n"
        f"- **Morning (TIME):** [Activity] \u2014 Est. cost: S$XX\n"
        f"- **Afternoon (TIME):** [Activity] \u2014 Est. cost: S$XX\n"
        f"- **Evening (TIME):** [Activity] \u2014 Est. cost: S$XX\n"
        f"- Daily transport: S$XX\n\n"
        f"**Sightseeing Total: S$[sum]**\n\n"
        f"At the very end, include a line:\n"
        f"SIGHTSEEING_TOTAL_SGD: [number]\n\n"
        f"Rules:\n"
        f"- Be realistic with prices in Singapore Dollars (SGD / S$) for {state['destination']}\n"
        f"- Follow the persona pacing rules STRICTLY\n"
        f"- Include specific venue/attraction names, not generic placeholders\n"
        f"- Ensure geographic clustering (nearby activities grouped together)"
    )

    logger.debug(f"[Itinerary Agent] Invoking Gemini LLM...")
    response = _llm.invoke([HumanMessage(content=prompt)])
    result_text = ensure_str(response.content)
    logger.info(f"[Itinerary Agent] Generated itinerary ({len(result_text)} chars).")

    return {"itinerary": result_text, "status": "planning"}


def food_retail_agent(state: dict) -> dict:
    """Curate dining and retail recommendations in SGD aligned to daily zones."""
    logger.info(f"[Food & Retail Agent] Curating dining for destination='{state['destination']}'")
    persona_ctx = get_persona_context(state, PERSONA_PROFILES)
    critique_ctx = get_critique_context(state)
    persona_key = state["persona"].lower().strip()
    profile = PERSONA_PROFILES.get(persona_key, PERSONA_PROFILES["couple"])
    currency = state.get("currency", "SGD")
    no_budget = state.get("no_budget", False)
    budget_line = "FLEXIBLE / UNLIMITED BUDGET (Focus on best dining)" if no_budget else f"TOTAL TRIP BUDGET: S$ {state['budget']:.2f} {currency}\nBUDGET ALLOCATION FOR FOOD & RETAIL: Approximately 30-35% of total budget"

    search_context = _search(
        f"best {profile['dining_style']} restaurants in {state['destination']}"
    )

    prompt = (
        f"You are a local food and retail expert for {state['destination']}.\n\n"
        f"{persona_ctx}\n\n"
        f"{budget_line}\n"
        f"{critique_ctx}\n\n"
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
        f"- Recommendations MUST be physically near the day's sightseeing locations\n"
        f"- Follow the persona dining style STRICTLY\n"
        f"- Include specific real restaurant/shop names\n"
        f"- Prices must be realistic in Singapore Dollars (SGD / S$)"
    )

    logger.debug(f"[Food & Retail Agent] Invoking Gemini LLM...")
    response = _llm.invoke([HumanMessage(content=prompt)])
    result_text = ensure_str(response.content)
    logger.info(f"[Food & Retail Agent] Generated dining plan ({len(result_text)} chars).")

    return {"food_and_retail": result_text}


def hospitality_agent(state: dict) -> dict:
    """Source hotel/accommodation options in SGD matching persona and budget."""
    logger.info(f"[Hospitality Agent] Sourcing lodging for destination='{state['destination']}'")
    persona_ctx = get_persona_context(state, PERSONA_PROFILES)
    critique_ctx = get_critique_context(state)
    persona_key = state["persona"].lower().strip()
    profile = PERSONA_PROFILES.get(persona_key, PERSONA_PROFILES["couple"])
    currency = state.get("currency", "SGD")
    no_budget = state.get("no_budget", False)
    budget_line = "FLEXIBLE / UNLIMITED BUDGET (Focus on best lodging)" if no_budget else f"TOTAL TRIP BUDGET: S$ {state['budget']:.2f} {currency}\nBUDGET ALLOCATION FOR ACCOMMODATION: Approximately 35-40% of total budget"

    search_context = _search(
        f"best {profile['accommodation']} in {state['destination']} {state['dates']}"
    )

    prompt = (
        f"You are an expert hospitality broker for {state['destination']}.\n\n"
        f"{persona_ctx}\n\n"
        f"{budget_line}\n"
        f"TRAVEL DATES: {state['dates']}\n"
        f"{critique_ctx}\n\n"
        f"THE SIGHTSEEING ITINERARY (pick hotels near these activity zones):\n"
        f"{state.get('itinerary', 'Not yet available')}\n\n"
        f"REAL-TIME RESEARCH (from web search):\n{search_context}\n\n"
        f"GENERATE accommodation recommendations following this EXACT format:\n\n"
        f"### Option 1: [Hotel Name] \u2b50\u2b50\u2b50\u2b50\n"
        f"- **Location:** [Neighborhood/Area]\n"
        f"- **Why it fits:** [1-2 sentences on persona match]\n"
        f"- **Nightly rate:** S$XX SGD\n"
        f"- **Total for stay:** S$XX SGD\n"
        f"- **Key amenities:** [list relevant amenities]\n\n"
        f"### Option 2: [Hotel Name] \u2b50\u2b50\u2b50\n"
        f"(same format)\n\n"
        f"### Option 3: [Hotel Name] (Budget Alternative)\n"
        f"(same format)\n\n"
        f"**\U0001f3e8 RECOMMENDED OPTION: [Name] \u2014 Total: S$XX SGD**\n\n"
        f"At the very end, include a line:\n"
        f"HOTEL_TOTAL_SGD: [number]\n\n"
        f"(Use the RECOMMENDED option's total for the number above.)\n\n"
        f"Rules:\n"
        f"- Hotels MUST match the persona accommodation style\n"
        f"- At least 3 options at different price points\n"
        f"- Prices must be realistic in Singapore Dollars (SGD / S$)\n"
        f"- The recommended option should optimize for persona fit AND budget"
    )

    logger.debug(f"[Hospitality Agent] Invoking Gemini LLM...")
    response = _llm.invoke([HumanMessage(content=prompt)])
    result_text = ensure_str(response.content)
    logger.info(f"[Hospitality Agent] Generated hotel recommendations ({len(result_text)} chars).")

    return {"hotel_recommendations": result_text}
