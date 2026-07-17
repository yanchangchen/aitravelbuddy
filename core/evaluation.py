"""Dual-layer evaluation engine for Travel Buddy."""

from langchain_core.messages import HumanMessage
from .personas import PERSONA_PROFILES
from .utils import extract_cost, ensure_str

_llm = None


def init(llm):
    """Initialize the module with LLM instance."""
    global _llm
    _llm = llm


def budget_guardrail(state: dict) -> dict:
    """Deterministic Python budget validation node."""
    budget = state["budget"]
    attempts = state.get("budget_attempts", 0)

    sightseeing_cost = extract_cost(state.get("itinerary", ""), "SIGHTSEEING_TOTAL_USD")
    food_retail_cost = extract_cost(state.get("food_and_retail", ""), "FOOD_RETAIL_TOTAL_USD")
    hotel_cost = extract_cost(state.get("hotel_recommendations", ""), "HOTEL_TOTAL_USD")
    total_cost = sightseeing_cost + food_retail_cost + hotel_cost

    lower_bound = 0.80 * budget
    upper_bound = 0.90 * budget

    breakdown = (
        f"Budget Breakdown (Attempt {attempts + 1}/3)\n"
        f"{'-' * 45}\n"
        f"  Sightseeing & Activities:  ${sightseeing_cost:>10,.2f}\n"
        f"  Food & Retail:             ${food_retail_cost:>10,.2f}\n"
        f"  Accommodation:             ${hotel_cost:>10,.2f}\n"
        f"{'-' * 45}\n"
        f"  TOTAL ESTIMATED COST:      ${total_cost:>10,.2f}\n"
        f"  TARGET RANGE:              ${lower_bound:,.2f} \u2014 ${upper_bound:,.2f}\n"
        f"  USER BUDGET:               ${budget:>10,.2f}\n"
    )

    if lower_bound <= total_cost <= upper_bound:
        return {
            "budget_breakdown": breakdown,
            "budget_attempts": attempts + 1,
            "status": "budget_passed",
        }
    else:
        if total_cost < lower_bound:
            critique = (
                f"Attempt {attempts + 1}: Total ${total_cost:,.2f} is TOO LOW "
                f"(below ${lower_bound:,.2f}). Agents are under-utilizing the "
                f"budget. Upgrade accommodations, add premium activities, or "
                f"include more dining experiences."
            )
        else:
            critique = (
                f"Attempt {attempts + 1}: Total ${total_cost:,.2f} EXCEEDS "
                f"${upper_bound:,.2f}. Agents must reduce costs."
            )

        new_attempts = attempts + 1
        if new_attempts >= 3:
            return {
                "budget_breakdown": breakdown,
                "budget_attempts": new_attempts,
                "critique_history": [critique],
                "status": "budget_busted",
            }
        else:
            return {
                "budget_breakdown": breakdown,
                "budget_attempts": new_attempts,
                "critique_history": [critique],
                "status": "planning",
            }


def agent_as_judge(state: dict) -> dict:
    """Cognitive quality evaluation using a separate LLM call."""
    persona_key = state["persona"].lower().strip()
    profile = PERSONA_PROFILES.get(persona_key, PERSONA_PROFILES["couple"])

    prompt = (
        f"You are an impartial travel plan quality inspector.\n\n"
        f"Your task is to evaluate the following travel plan against the MANDATORY persona rules.\n"
        f"You must be STRICT. Any rule violation results in a FAIL.\n\n"
        f"## PERSONA: {profile['label']}\n"
        f"## MANDATORY RULES:\n{profile['rules']}\n\n"
        f"## TRAVEL PLAN TO EVALUATE:\n\n"
        f"### Itinerary:\n{state.get('itinerary', 'N/A')}\n\n"
        f"### Food & Retail:\n{state.get('food_and_retail', 'N/A')}\n\n"
        f"### Accommodation:\n{state.get('hotel_recommendations', 'N/A')}\n\n"
        f"## YOUR EVALUATION:\n\n"
        f"Respond in this EXACT format:\n\n"
        f"VERDICT: [PASS or FAIL]\n\n"
        f"SCORE: [1-10]\n\n"
        f"RULE-BY-RULE CHECK:\n"
        f"1. [Rule text] \u2014 [PASS/FAIL] \u2014 [Brief evidence]\n"
        f"...\n\n"
        f"OVERALL ASSESSMENT:\n"
        f"[2-3 sentences summarizing the quality of the plan]"
    )

    response = _llm.invoke([HumanMessage(content=prompt)])
    verdict_text = ensure_str(response.content)
    return {"judge_verdict": verdict_text, "status": "approved"}


def budget_busted_fallback(state: dict) -> dict:
    """Terminal fallback when budget cannot be reconciled after 3 attempts."""
    history = state.get("critique_history", [])
    history_text = "\n".join(f"  - {c}" for c in history)
    notice = (
        f"BUDGET RECONCILIATION FAILED\n"
        f"{'=' * 50}\n"
        f"Destination: {state['destination']}\n"
        f"Budget: ${state['budget']:,.2f}\n"
        f"Dates: {state['dates']}\n"
        f"Persona: {state['persona']}\n\n"
        f"The system attempted 3 rounds of planning but could not\n"
        f"produce a plan within the 80-90% budget safety buffer.\n\n"
        f"Attempt History:\n{history_text}\n\n"
        f"RECOMMENDATION: Increase budget, reduce days, or choose cheaper destination."
    )
    return {"status": "budget_busted", "budget_breakdown": notice}


def final_output(state: dict) -> dict:
    """Terminal success node."""
    return {"status": "approved"}
