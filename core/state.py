"""Centralized state schema for the Travel Buddy agent graph."""

import operator
from typing import Annotated, Optional
from typing_extensions import TypedDict


class TravelBuddyState(TypedDict, total=False):
    """State flowing through the Travel Buddy agent graph.

    User Inputs (set once at invocation):
        destination, budget, dates, persona, no_budget, currency, custom_persona_profile
    Agent Outputs (populated by planning nodes):
        itinerary, food_and_retail, hotel_recommendations, budget_breakdown
    Loop Control & Evaluation:
        budget_attempts, critique_history, status, judge_verdict
    """

    destination: str
    budget: float              # Total trip budget in specified currency (default SGD)
    no_budget: bool            # True if user selected flexible/unlimited budget
    currency: str              # Currency code, e.g. "SGD"
    dates: str
    persona: str
    custom_persona_profile: Optional[dict]
    itinerary: str
    food_and_retail: str
    hotel_recommendations: str
    budget_breakdown: str
    budget_attempts: int
    critique_history: Annotated[list[str], operator.add]
    status: str
    judge_verdict: str
