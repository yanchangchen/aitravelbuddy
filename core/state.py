"""Centralized state schema for the Travel Buddy agent graph."""

import operator
from typing import Annotated
from typing_extensions import TypedDict


class TravelBuddyState(TypedDict):
    """State flowing through the Travel Buddy agent graph.

    User Inputs (set once at invocation):
        destination, budget, dates, persona
    Agent Outputs (populated by planning nodes):
        itinerary, food_and_retail, hotel_recommendations, budget_breakdown
    Loop Control & Evaluation:
        budget_attempts, critique_history, status, judge_verdict
    """

    destination: str
    budget: float
    dates: str
    persona: str
    itinerary: str
    food_and_retail: str
    hotel_recommendations: str
    budget_breakdown: str
    budget_attempts: int
    critique_history: Annotated[list[str], operator.add]
    status: str
    judge_verdict: str
