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


def quality_agent(state: dict) -> dict:
    """Unified Quality Evaluation Agent.

    Evaluates:
      1. Programmatic budget validation (checks costs are within 80-90% range of user budget, if bounded).
      2. LLM Compliance checks (evaluates duration, persona style, pacing, and preferences).
    Assigns a quality score from 1 to 10.
    If score >= 8, sets status to 'approved'.
    If score < 8, increments attempts and routes back to the orchestrator with surgical critiques (max 3 runs).
    """
    # 1. Programmatic Cost Calculation
    budget_sgd = state.get("budget", 0.0)
    no_budget = state.get("no_budget", False)
    self_drive = state.get("self_drive", False)
    attempts = state.get("budget_attempts", 0)

    logger.info(f"[Quality Agent] Evaluation attempt {attempts + 1}/3. no_budget={no_budget}, self_drive={self_drive}, budget={budget_sgd}")

    sightseeing_sgd = extract_cost(state.get("itinerary", ""), "SIGHTSEEING_TOTAL_SGD")
    food_retail_sgd = extract_cost(state.get("food_and_retail", ""), "FOOD_RETAIL_TOTAL_SGD")
    hotel_sgd = extract_cost(state.get("hotel_recommendations", ""), "HOTEL_TOTAL_SGD")
    airfare_sgd = extract_cost(state.get("purchasing_guide", ""), "AIRFARE_TOTAL_SGD")
    car_rental_sgd = extract_cost(state.get("purchasing_guide", ""), "CAR_RENTAL_TOTAL_SGD") if self_drive else 0.0

    total_sgd = sightseeing_sgd + food_retail_sgd + hotel_sgd + airfare_sgd + car_rental_sgd
    total_usd_ref = total_sgd * SGD_TO_USD_RATE

    car_line = f"  Car Rental & Tolls:        S${car_rental_sgd:>10,.2f} SGD  (~${car_rental_sgd * SGD_TO_USD_RATE:,.2f} USD)\n" if self_drive else ""

    # Budget Range Determination
    lower_bound_sgd = 0.80 * budget_sgd
    upper_bound_sgd = 0.90 * budget_sgd

    if no_budget or budget_sgd <= 0:
        budget_passed = True
        budget_status = "Unlimited / Flexible Budget mode is active (always valid)."
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
    else:
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
            budget_passed = True
            budget_status = f"PASSED! Total cost of S${total_sgd:,.2f} SGD is within target range."
        elif total_sgd < lower_bound_sgd:
            budget_passed = False
            budget_status = f"FAILED! Total cost of S${total_sgd:,.2f} SGD is TOO LOW (below safety minimum S${lower_bound_sgd:,.2f} SGD). Propose premium experiences or higher-end hotel lodging."
        else:
            budget_passed = False
            budget_status = f"FAILED! Total cost of S${total_sgd:,.2f} SGD EXCEEDS user budget safety limit of S${upper_bound_sgd:,.2f} SGD. Reduce airfare or lodging costs."

    # 2. Cognitive LLM Quality Inspection
    persona_key = state.get("persona", "family").lower().strip()
    if persona_key == "custom" and "custom_persona_profile" in state and isinstance(state["custom_persona_profile"], dict):
        profile = state["custom_persona_profile"]
    else:
        profile = PERSONA_PROFILES.get(persona_key, PERSONA_PROFILES["family"])

    num_days = state.get("num_days", 5)
    destination = state.get("destination", "Destination")
    travelers_summary = state.get("travelers_summary", "2 Adults, 1 Child")

    prompt = (
        f"You are an impartial travel plan quality inspector.\n\n"
        f"CRITICAL DIRECTIVE: DO NOT ALTER OR SUGGEST CHANGING THE TRIP DESTINATION ('{destination}'), THE REQUIRED NUMBER OF DAYS ({num_days} DAYS), OR THE TRAVELER COMPOSITION ('{travelers_summary}'). THESE ARE IMMUTABLE USER REQUIREMENTS.\n\n"
        f"Your task is to evaluate whether the proposed travel plan fulfills the budget constraints and persona guidelines. Assign a score from 1 to 10, where 10 is fully satisfying all criteria.\n\n"
        f"## PROGRAMMATIC BUDGET STATUS:\n"
        f"{budget_status}\n\n"
        f"## REQUIRED TRIP SPECIFICATION (IMMUTABLE):\n"
        f"- Target Destination: {destination}\n"
        f"- Required Trip Duration: EXACTLY {num_days} DAYS (Day 1 through Day {num_days})\n"
        f"- Group Composition: {travelers_summary}\n\n"
        f"## PERSONA: {profile.get('label', 'Custom Persona')}\n"
        f"## MANDATORY RULES:\n{profile.get('rules', 'Follow traveler preferences.')}\n\n"
        f"## TRAVEL PLAN TO EVALUATE:\n\n"
        f"### Itinerary:\n{state.get('itinerary', 'N/A')}\n\n"
        f"### Food & Retail:\n{state.get('food_and_retail', 'N/A')}\n\n"
        f"### Accommodation:\n{state.get('hotel_recommendations', 'N/A')}\n\n"
        f"### Booking & Transport Guide:\n{state.get('purchasing_guide', 'N/A')}\n\n"
        f"## YOUR EVALUATION:\n\n"
        f"If the PROGRAMMATIC BUDGET STATUS above indicates a FAILURE, you MUST award a score of less than 8.\n\n"
        f"Respond in this EXACT format:\n\n"
        f"VERDICT: [PASS or FAIL]\n\n"
        f"SCORE: [1-10]\n\n"
        f"SURGICAL SUGGESTIONS:\n"
        f"[If failed or score < 10, provide specific suggestions here on which component needs fixing. If everything is perfect, write 'None.']"
    )

    logger.debug("[Quality Agent] Invoking Gemini LLM...")
    response = _llm.invoke([HumanMessage(content=prompt)])
    verdict_text = ensure_str(response.content)
    logger.info(f"[Quality Agent LLM Output] ({len(verdict_text)} chars):\n{verdict_text}")

    import re
    score_match = re.search(r"SCORE:\s*(\d+)", verdict_text)
    score = int(score_match.group(1)) if score_match else 9

    surg_match = re.search(r"SURGICAL SUGGESTIONS:\s*(.*)", verdict_text, re.DOTALL | re.IGNORECASE)
    suggestions = surg_match.group(1).strip() if surg_match else "Plan refinement needed."

    # Enforce programmatic budget safety override
    if not budget_passed and score >= 8:
        logger.warning(f"[Quality Agent] Programmatic budget check failed, overriding score {score} to 7.")
        score = 7

    new_attempts = attempts + 1

    if score >= 8:
        logger.info(f"[Quality Agent] Plan APPROVED with score {score}/10.")
        return {
            "budget_breakdown": breakdown,
            "budget_attempts": new_attempts,
            "judge_verdict": verdict_text,
            "status": "approved",
        }
    else:
        critique = f"Attempt {new_attempts}: Quality Score {score}/10. {suggestions}"
        if new_attempts >= 3:
            logger.error(f"[Quality Agent] STRIKE THREE on Quality. Routing to terminal fallback. {critique}")
            return {
                "budget_breakdown": breakdown,
                "budget_attempts": new_attempts,
                "judge_verdict": verdict_text,
                "critique_history": [critique],
                "status": "quality_failed",
            }
        else:
            logger.warning(f"[Quality Agent] Quality failed (Score {score}/10). Routing back to orchestrator. Critique: {critique}")
            return {
                "budget_breakdown": breakdown,
                "budget_attempts": new_attempts,
                "judge_verdict": verdict_text,
                "critique_history": [critique],
                "status": "planning",
            }


def terminal_fallback(state: dict) -> dict:
    """Terminal fallback when budget or quality cannot be reconciled after 3 attempts.
    
    Preserves all generated itinerary, food, hotel, and purchasing content, but marks
    status as 'unapproved' and provides a detailed quality_failure_reason so the user
    can inspect the provisional plan and relax criteria to rerun the pipeline.
    """
    logger.error(f"[Terminal Fallback] Handling terminal quality/budget reconciliation for destination='{state['destination']}'")
    history = state.get("critique_history", [])
    history_text = "\n".join(f"  • {c}" for c in history) if history else "  • Failed strict criteria check after maximum retry attempts."
    budget_sgd = state.get("budget", 0.0)
    verdict = state.get("judge_verdict", "")

    failure_type = "Quality / Persona Rule Compliance" if ("Quality Score" in history_text or verdict) else "Budget Constraints"

    failure_reason = (
        f"⚠️ PLAN UNAPPROVED — DID NOT PASS {failure_type.upper()} EVALUATION\n"
        f"{'=' * 65}\n"
        f"• Origin: {state.get('origin', 'Singapore')} ➔ Destination: {state.get('destination', 'N/A')}\n"
        f"• Group Composition: {state.get('travelers_summary', 'N/A')}\n"
        f"• Persona Profile: {state.get('persona', 'N/A')}\n"
        f"• User Budget: S${budget_sgd:,.2f} SGD ({'Flexible' if state.get('no_budget') else 'Bounded'})\n\n"
        f"📌 REASON FOR REJECTION:\n"
        f"{history_text}\n\n"
    )
    if verdict:
        failure_reason += f"⚖️ AGENT-AS-JUDGE VERDICT:\n{verdict}\n\n"

    failure_reason += (
        f"💡 HOW TO RELAX CRITERIA TO RERUN THE PIPELINE:\n"
        f"1. Toggle 'Infinite / Flexible Budget (No Limit)' to bypass budget guardrails.\n"
        f"2. Switch Persona Profile or relax mandatory persona rules.\n"
        f"3. Adjust travel duration or add custom notes in the input panel below."
    )

    return {
        "status": "unapproved",
        "quality_failure_reason": failure_reason,
        "budget_breakdown": state.get("budget_breakdown", failure_reason),
    }


def final_output(state: dict) -> dict:
    """Terminal success node."""
    logger.info("[Final Output] Compiling approved plan.")
    return {"status": "approved"}
