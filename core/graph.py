"""LangGraph StateGraph compilation for Travel Buddy."""

from langgraph.graph import StateGraph, END, START
from .state import TravelBuddyState
from . import agents, evaluation


def build_graph(llm, search_tool):
    """Construct and compile the Travel Buddy agent graph.

    Args:
        llm: LangChain chat model instance
        search_tool: Tavily search tool instance

    Returns:
        Compiled LangGraph application ready for .stream() or .invoke()
    """
    # Initialize modules with dependencies
    agents.init(llm, search_tool)
    evaluation.init(llm)

    # Build graph
    workflow = StateGraph(TravelBuddyState)
    workflow.add_node("itinerary_agent", agents.itinerary_agent)
    workflow.add_node("food_retail_agent", agents.food_retail_agent)
    workflow.add_node("hospitality_agent", agents.hospitality_agent)
    workflow.add_node("budget_guardrail", evaluation.budget_guardrail)
    workflow.add_node("agent_as_judge", evaluation.agent_as_judge)
    workflow.add_node("budget_busted_fallback", evaluation.budget_busted_fallback)
    workflow.add_node("final_output", evaluation.final_output)

    # Sequential pipeline
    workflow.add_edge(START, "itinerary_agent")
    workflow.add_edge("itinerary_agent", "food_retail_agent")
    workflow.add_edge("food_retail_agent", "hospitality_agent")
    workflow.add_edge("hospitality_agent", "budget_guardrail")

    # Conditional routing
    def route_after_budget_check(state):
        status = state.get("status", "planning")
        if status == "budget_passed":
            return "agent_as_judge"
        elif status == "budget_busted":
            return "budget_busted_fallback"
        else:
            return "itinerary_agent"

    workflow.add_conditional_edges(
        "budget_guardrail",
        route_after_budget_check,
        {
            "agent_as_judge": "agent_as_judge",
            "itinerary_agent": "itinerary_agent",
            "budget_busted_fallback": "budget_busted_fallback",
        },
    )

    workflow.add_edge("agent_as_judge", "final_output")
    workflow.add_edge("final_output", END)
    workflow.add_edge("budget_busted_fallback", END)

    return workflow.compile()
