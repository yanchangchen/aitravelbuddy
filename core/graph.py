"""LangGraph StateGraph compilation for Travel Buddy with purchasing agent & troubleshooting logging."""

from langgraph.graph import StateGraph, END, START
from .state import TravelBuddyState
from . import agents, evaluation
from .logger import get_logger

logger = get_logger("graph")


def build_graph(llm, search_tool):
    """Construct and compile the Travel Buddy agent graph.

    Pipeline:
      START -> itinerary_agent -> food_retail_agent -> hospitality_agent
            -> purchasing_agent -> budget_guardrail --(pass)--> agent_as_judge -> final_output -> END
                                                    --(retry)--> itinerary_agent
                                                    --(busted)--> budget_busted_fallback -> END
    """
    logger.info("Initializing graph modules and registering StateGraph nodes...")
    agents.init(llm, search_tool)
    evaluation.init(llm)

    workflow = StateGraph(TravelBuddyState)
    workflow.add_node("orchestrator_agent", agents.orchestrator_agent)
    workflow.add_node("itinerary_agent", agents.itinerary_agent)
    workflow.add_node("food_retail_agent", agents.food_retail_agent)
    workflow.add_node("hospitality_agent", agents.hospitality_agent)
    workflow.add_node("purchasing_agent", agents.purchasing_agent)
    workflow.add_node("quality_agent", evaluation.quality_agent)
    workflow.add_node("terminal_fallback", evaluation.terminal_fallback)
    workflow.add_node("final_output", evaluation.final_output)

    workflow.add_edge(START, "orchestrator_agent")

    def route_from_orchestrator(state):
        next_agent = state.get("next_agent", "itinerary_agent")
        logger.info(f"[Orchestrator Router] Routing to '{next_agent}'")
        return next_agent

    workflow.add_conditional_edges(
        "orchestrator_agent",
        route_from_orchestrator,
        {
            "itinerary_agent": "itinerary_agent",
            "food_retail_agent": "food_retail_agent",
            "hospitality_agent": "hospitality_agent",
            "purchasing_agent": "purchasing_agent",
        }
    )
    workflow.add_edge("itinerary_agent", "food_retail_agent")
    workflow.add_edge("food_retail_agent", "hospitality_agent")
    workflow.add_edge("hospitality_agent", "purchasing_agent")
    workflow.add_edge("purchasing_agent", "quality_agent")

    def route_after_quality_check(state):
        status = state.get("status", "approved")
        logger.info(f"[Graph Router] Routing decision based on status='{status}'")
        if status == "approved":
            return "final_output"
        elif status == "quality_failed":
            return "terminal_fallback"
        else:
            return "orchestrator_agent"

    workflow.add_conditional_edges(
        "quality_agent",
        route_after_quality_check,
        {
            "final_output": "final_output",
            "terminal_fallback": "terminal_fallback",
            "orchestrator_agent": "orchestrator_agent",
        },
    )
    workflow.add_edge("final_output", END)
    workflow.add_edge("terminal_fallback", END)

    compiled_app = workflow.compile()
    logger.info("StateGraph compiled successfully with 8 nodes including orchestrator_agent.")
    return compiled_app
