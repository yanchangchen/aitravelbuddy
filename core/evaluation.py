"""Dual-layer evaluation engine for Travel Buddy."""

from langchain_core.messages import HumanMessage
from .personas import PERSONA_PROFILES
from .utils import extract_cost, ensure_str

_llm = None

# Exchange rate reference: 1 SGD = 0.74 USD
SGD_TO_USD_RATE = 0.74


def init(llm):
    """Initialize the module with LLM instance."""
    global _llm
    _llm = llm


def budget_guardrail(state: dict) -> dict:
    """Deterministic Python budget validation node.

    Handles SGD pricing as primary currency and supports optional USD conversion reference.
    Supports no_budget mode (flexible / unlimited budget).
    """
    budget_sgd = state.get("budget", 0.0)
    no_budget = state.get("no_budget", False)
    attempts = state.get("budget_attempts", 0)

    sightseeing_sgd = extract_cost(state.get("itinerary", ""), "SIGHTSEEING_TOTAL_SGD")
    food_retail_sgd = extract_cost(state.get("food_and_retail", ""), "FOOD_RETAIL_TOTAL_SGD")
    hotel_sgd = extract_cost(state.get("hotel_recommendations", ""), "HOTEL_TOTAL_SGD")

    total_sgd = sightseeing_sgd + food_retail_sgd + hotel_sgd
    total_usd_ref = total_sgd * SGD_TO_USD_RATE

    if no_budget or budget_sgd <= 0:
        breakdown = (
            f"Budget Breakdown (Attempt {attempts + 1}/3) — FLEXIBLE / UNLIMITED BUDGET\n"
            f"{'-' * 55}\n"
            f"  Sightseeing & Activities:  S${sightseeing_sgd:>10,.2f} SGD  (~${sightseeing_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
            f"  Food & Retail:             S${food_retail_sgd:>10,.2f} SGD  (~${food_retail_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
            f"  Accommodation:             S${hotel_sgd:>10,.2f} SGD  (~${hotel_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
            f"{'-' * 55}\n"
            f"  TOTAL ESTIMATED COST:      S${total_sgd:>10,.2f} SGD  (~${total_usd_ref:,.2f} USD)\n"
            f"  BUDGET MODE:               Unlimited / Flexible (Guardrail Bypassed)\n"
        )
        return {
            "budget_breakdown": breakdown,
            "budget_attempts": attempts + 1,
            "status": "budget_passed",
        }

    # Bounded budget check in SGD
    lower_bound_sgd = 0.80 * budget_sgd
    upper_bound_sgd = 0.90 * budget_sgd

    breakdown = (
        f"Budget Breakdown (Attempt {attempts + 1}/3)\n"
        f"{'-' * 55}\n"
        f"  Sightseeing & Activities:  S${sightseeing_sgd:>10,.2f} SGD  (~${sightseeing_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
        f"  Food & Retail:             S${food_retail_sgd:>10,.2f} SGD  (~${food_retail_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
        f"  Accommodation:             S${hotel_sgd:>10,.2f} SGD  (~${hotel_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
        f"{'-' * 55}\n"
        f"  TOTAL ESTIMATED COST:      S${total_sgd:>10,.2f} SGD  (~${total_usd_ref:,.2f} USD)\n"
        f"  TARGET RANGE (80-90%):     S${lower_bound_sgd:,.2f} — S${upper_bound_sgd:,.2f} SGD\n"
        f"  USER BUDGET:               S${budget_sgd:>10,.2f} SGD\n"
    )

    if lower_bound_sgd <= total_sgd <= upper_bound_sgd:
        return {
            "budget_breakdown": breakdown,
            "budget_attempts": attempts + 1,
            "status": "budget_passed",
        }
    else:
        if total_sgd < lower_bound_sgd:
            critique = (
                f"Attempt {attempts + 1}: Total S${total_sgd:,.2f} SGD is TOO LOW "
                f"(below S${lower_bound_sgd:,.2f} SGD). Upgrade accommodations or add premium experiences."
            )
        else:
            critique = (
                f"Attempt {attempts + 1}: Total S${total_sgd:,.2f} SGD EXCEEDS "
                f"target limit of S${upper_bound_sgd:,.2f} SGD. Reduce costs."
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
    budget_sgd = state.get("budget", 0.0)

    notice = (
        f"BUDGET RECONCILIATION FAILED\n"
        f"{'=' * 50}\n"
        f"Destination: {state['destination']}\n"
        f"Budget: S${budget_sgd:,.2f} SGD\n"
        f"Dates: {state['dates']}\n"
        f"Persona: {state['persona']}\n\n"
        f"The system attempted 3 rounds of planning but could not\n"
        f"produce a plan within the 80-90% budget safety buffer.\n\n"
        f"Attempt History:\n{history_text}\n\n"
        f"RECOMMENDATION: Increase budget, select 'No budget limit', reduce days, or choose a cheaper destination."
    )
    return {"status": "budget_busted", "budget_breakdown": notice}


def final_output(state: dict) -> dict:
    """Terminal success node."""
    return {"status": "approved"}
