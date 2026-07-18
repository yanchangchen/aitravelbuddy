"""Dual-layer evaluation engine for Travel Buddy with transport cost inclusion & troubleshooting logging."""

from langchain_core.messages import HumanMessage
from .personas import PERSONA_PROFILES
from .utils import extract_cost, ensure_str
from .logger import get_logger

logger = get_logger("evaluation")

_llm = None

# Exchange rate reference: 1 SGD = 0.74 USD
SGD_TO_USD_RATE = 0.74


def init(llm):
    """Initialize the module with LLM instance."""
    global _llm
    _llm = llm
    logger.info("Evaluation module initialized with LLM instance.")


def budget_guardrail(state: dict) -> dict:
    """Deterministic Python budget validation node.

    Includes Sightseeing, Food & Retail, Accommodation, Airfare (Flight), and Car Rental (if self-drive).
    Handles SGD pricing as primary currency and supports optional USD conversion reference.
    Supports no_budget mode (flexible / unlimited budget).
    """
    budget_sgd = state.get("budget", 0.0)
    no_budget = state.get("no_budget", False)
    self_drive = state.get("self_drive", False)
    attempts = state.get("budget_attempts", 0)

    logger.info(f"[Budget Guardrail] Evaluation attempt {attempts + 1}/3. no_budget={no_budget}, self_drive={self_drive}, budget_sgd={budget_sgd:,.2f}")

    sightseeing_sgd = extract_cost(state.get("itinerary", ""), "SIGHTSEEING_TOTAL_SGD")
    food_retail_sgd = extract_cost(state.get("food_and_retail", ""), "FOOD_RETAIL_TOTAL_SGD")
    hotel_sgd = extract_cost(state.get("hotel_recommendations", ""), "HOTEL_TOTAL_SGD")
    airfare_sgd = extract_cost(state.get("purchasing_guide", ""), "AIRFARE_TOTAL_SGD")
    car_rental_sgd = extract_cost(state.get("purchasing_guide", ""), "CAR_RENTAL_TOTAL_SGD") if self_drive else 0.0

    total_sgd = sightseeing_sgd + food_retail_sgd + hotel_sgd + airfare_sgd + car_rental_sgd
    total_usd_ref = total_sgd * SGD_TO_USD_RATE

    logger.info(
        f"[Budget Guardrail] Extracted costs: Sightseeing=S${sightseeing_sgd:,.2f}, "
        f"Food/Retail=S${food_retail_sgd:,.2f}, Hotel=S${hotel_sgd:,.2f}, "
        f"Airfare=S${airfare_sgd:,.2f}, Car Rental=S${car_rental_sgd:,.2f} -> "
        f"TOTAL=S${total_sgd:,.2f} SGD (~${total_usd_ref:,.2f} USD)"
    )

    car_line = f"  Car Rental & Tolls:        S${car_rental_sgd:>10,.2f} SGD  (~${car_rental_sgd * SGD_TO_USD_RATE:,.2f} USD)\n" if self_drive else ""

    if no_budget or budget_sgd <= 0:
        logger.info("[Budget Guardrail] Flexible / Unlimited budget mode active — Guardrail PASSED directly.")
        breakdown = (
            f"Budget Breakdown (Attempt {attempts + 1}/3) — FLEXIBLE / UNLIMITED BUDGET\n"
            f"{'-' * 60}\n"
            f"  Sightseeing & Activities:  S${sightseeing_sgd:>10,.2f} SGD  (~${sightseeing_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
            f"  Food & Retail:             S${food_retail_sgd:>10,.2f} SGD  (~${food_retail_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
            f"  Accommodation:             S${hotel_sgd:>10,.2f} SGD  (~${hotel_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
            f"  Airfare (Round-trip):      S${airfare_sgd:>10,.2f} SGD  (~${airfare_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
            f"{car_line}"
            f"{'-' * 60}\n"
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

    logger.info(f"[Budget Guardrail] Bound check: Target range=S${lower_bound_sgd:,.2f} - S${upper_bound_sgd:,.2f} SGD.")

    breakdown = (
        f"Budget Breakdown (Attempt {attempts + 1}/3)\n"
        f"{'-' * 60}\n"
        f"  Sightseeing & Activities:  S${sightseeing_sgd:>10,.2f} SGD  (~${sightseeing_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
        f"  Food & Retail:             S${food_retail_sgd:>10,.2f} SGD  (~${food_retail_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
        f"  Accommodation:             S${hotel_sgd:>10,.2f} SGD  (~${hotel_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
        f"  Airfare (Round-trip):      S${airfare_sgd:>10,.2f} SGD  (~${airfare_sgd * SGD_TO_USD_RATE:,.2f} USD)\n"
        f"{car_line}"
        f"{'-' * 60}\n"
        f"  TOTAL ESTIMATED COST:      S${total_sgd:>10,.2f} SGD  (~${total_usd_ref:,.2f} USD)\n"
        f"  TARGET RANGE (80-90%):     S${lower_bound_sgd:,.2f} — S${upper_bound_sgd:,.2f} SGD\n"
        f"  USER BUDGET:               S${budget_sgd:>10,.2f} SGD\n"
    )

    if lower_bound_sgd <= total_sgd <= upper_bound_sgd:
        logger.info(f"[Budget Guardrail] PASSED! Total S${total_sgd:,.2f} SGD within 80-90% safety buffer.")
        return {
            "budget_breakdown": breakdown,
            "budget_attempts": attempts + 1,
            "status": "budget_passed",
        }
    else:
        if total_sgd < lower_bound_sgd:
            critique = (
                f"Attempt {attempts + 1}: Total S${total_sgd:,.2f} SGD is TOO LOW "
                f"(below S${lower_bound_sgd:,.2f} SGD). Upgrade accommodations, airfare, or add premium experiences."
            )
        else:
            critique = (
                f"Attempt {attempts + 1}: Total S${total_sgd:,.2f} SGD EXCEEDS "
                f"target limit of S${upper_bound_sgd:,.2f} SGD. Reduce costs."
            )

        new_attempts = attempts + 1
        if new_attempts >= 3:
            logger.error(f"[Budget Guardrail] STRIKE THREE! {critique} -> Routing to budget_busted_fallback.")
            return {
                "budget_breakdown": breakdown,
                "budget_attempts": new_attempts,
                "critique_history": [critique],
                "status": "budget_busted",
            }
        else:
            logger.warning(f"[Budget Guardrail] FAILED attempt {new_attempts}/3. {critique} -> Routing back to planning.")
            return {
                "budget_breakdown": breakdown,
                "budget_attempts": new_attempts,
                "critique_history": [critique],
                "status": "planning",
            }


def agent_as_judge(state: dict) -> dict:
    """Cognitive quality evaluation using a separate LLM call."""
    logger.info(f"[Agent-as-Judge] Starting persona compliance check for persona='{state['persona']}'")
    persona_key = state["persona"].lower().strip()
    profile = PERSONA_PROFILES.get(persona_key, PERSONA_PROFILES["couple"])

    num_days = state.get("num_days", 5)

    prompt = (
        f"You are an impartial travel plan quality inspector.\n\n"
        f"Your task is to evaluate the following travel plan against the MANDATORY persona rules AND the required trip length.\n"
        f"You must be STRICT. Any rule violation or missing days results in a FAIL.\n\n"
        f"## TRIP LENGTH REQUIREMENT:\n"
        f"The itinerary MUST explicitly cover exactly {num_days} days (Day 1 through Day {num_days}). If it plans fewer or more than {num_days} days, fail the evaluation.\n\n"
        f"## PERSONA: {profile['label']}\n"
        f"## MANDATORY RULES:\n{profile['rules']}\n\n"
        f"## TRAVEL PLAN TO EVALUATE:\n\n"
        f"### Itinerary:\n{state.get('itinerary', 'N/A')}\n\n"
        f"### Food & Retail:\n{state.get('food_and_retail', 'N/A')}\n\n"
        f"### Accommodation:\n{state.get('hotel_recommendations', 'N/A')}\n\n"
        f"### Booking & Transport Guide:\n{state.get('purchasing_guide', 'N/A')}\n\n"
        f"## YOUR EVALUATION:\n\n"
        f"Respond in this EXACT format:\n\n"
        f"VERDICT: [PASS or FAIL]\n\n"
        f"SCORE: [1-10]\n\n"
        f"RULE-BY-RULE CHECK:\n"
        f"1. [Rule text] \u2014 [PASS/FAIL] \u2014 [Brief evidence]\n"
        f"...\n"
        f"X. Trip Length ({num_days} Days) \u2014 [PASS/FAIL] \u2014 [Evidence]\n\n"
        f"OVERALL ASSESSMENT:\n"
        f"[2-3 sentences summarizing the quality of the plan]"
    )

    logger.debug("[Agent-as-Judge] Invoking Gemini LLM...")
    response = _llm.invoke([HumanMessage(content=prompt)])
    verdict_text = ensure_str(response.content)
    
    import re
    score_match = re.search(r"SCORE:\s*(\d+)", verdict_text)
    score = int(score_match.group(1)) if score_match else 10
    
    attempts = state.get("budget_attempts", 0)
    
    logger.info(f"[Agent-as-Judge] Evaluation complete ({len(verdict_text)} chars). Score: {score}/10")
    
    if score >= 6:
        return {"judge_verdict": verdict_text, "status": "approved"}
    else:
        new_attempts = attempts + 1
        critique = f"Attempt {new_attempts}: Quality Score was {score}/10 (Below Average). You MUST improve adherence to persona rules: {verdict_text}"
        if new_attempts >= 3:
            logger.error("[Agent-as-Judge] STRIKE THREE on Quality. Routing to terminal fallback.")
            return {
                "judge_verdict": verdict_text,
                "budget_attempts": new_attempts,
                "critique_history": [critique],
                "status": "quality_failed"
            }
        else:
            logger.warning(f"[Agent-as-Judge] Quality failed attempt {new_attempts}/3. Routing back to planning.")
            return {
                "judge_verdict": verdict_text,
                "budget_attempts": new_attempts,
                "critique_history": [critique],
                "status": "planning"
            }


def terminal_fallback(state: dict) -> dict:
    """Terminal fallback when budget or quality cannot be reconciled after 3 attempts."""
    logger.error(f"[Terminal Fallback] Handling terminal failure for destination='{state['destination']}'")
    history = state.get("critique_history", [])
    history_text = "\n".join(f"  - {c}" for c in history)
    budget_sgd = state.get("budget", 0.0)

    notice = (
        f"PLANNING RECONCILIATION FAILED\n"
        f"{'=' * 50}\n"
        f"Origin: {state.get('origin', 'Singapore')}\n"
        f"Destination: {state['destination']}\n"
        f"Budget: S${budget_sgd:,.2f} SGD\n"
        f"Dates: {state['dates']}\n"
        f"Persona: {state['persona']}\n\n"
        f"The system attempted 3 rounds of planning but could not\n"
        f"produce a plan meeting the budget and quality constraints.\n\n"
        f"Attempt History:\n{history_text}\n\n"
        f"RECOMMENDATION: Increase budget, select 'No budget limit', reduce days, choose a cheaper destination, or relax custom persona rules."
    )
    return {"status": "failed", "budget_breakdown": notice}


def final_output(state: dict) -> dict:
    """Terminal success node."""
    logger.info("[Final Output] Compiling approved plan.")
    return {"status": "approved"}
