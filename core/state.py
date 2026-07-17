"""Centralized state schema for the Travel Buddy agent graph."""

import operator
from typing import Annotated, Optional
from typing_extensions import TypedDict


class TravelBuddyState(TypedDict, total=False):
    """State flowing through the Travel Buddy agent graph.

    User Inputs (set once at invocation):
        origin, destination, budget, dates, persona, num_adults, num_children, num_infants,
        travelers_summary, self_drive, no_budget, currency, custom_persona_profile
    Agent Outputs (populated by planning nodes):
        itinerary, food_and_retail, hotel_recommendations, purchasing_guide, budget_breakdown
    Loop Control & Evaluation:
        budget_attempts, critique_history, status, judge_verdict
    """

    origin: str                # Origin / Source city (e.g., "Singapore")
    destination: str           # Target city/country (e.g., "Tokyo, Japan")
    budget: float              # Total trip budget in specified currency (default SGD)
    num_adults: int            # Number of adult travelers (default 2)
    num_children: int          # Number of children (>2 years) (default 1)
    num_infants: int           # Number of infants (<2 years) (default 0)
    travelers_summary: str     # E.g., "2 Adults, 1 Child (>2 yrs)"
    self_drive: bool           # True if user selects self-drive / car rental option
    no_budget: bool            # True if user selected flexible/unlimited budget
    currency: str              # Currency code, e.g. "SGD"
    dates: str
    persona: str
    custom_persona_profile: Optional[dict]
    itinerary: str
    food_and_retail: str
    hotel_recommendations: str
    purchasing_guide: str      # Booking links, airfare, car rental & ticket recommendations
    budget_breakdown: str
    budget_attempts: int
    critique_history: Annotated[list[str], operator.add]
    status: str
    judge_verdict: str
