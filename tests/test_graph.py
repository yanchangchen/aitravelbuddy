"""Integration tests for LangGraph StateGraph setup in Travel Buddy."""

import unittest
from unittest.mock import MagicMock
from core.graph import build_graph


class TestGraph(unittest.TestCase):

    def test_build_graph_structure(self):
        mock_llm = MagicMock()
        mock_search = MagicMock()

        app = build_graph(mock_llm, mock_search)
        self.assertIsNotNone(app)

        # Check registered nodes in graph
        nodes = app.nodes
        expected_nodes = [
            "itinerary_agent",
            "food_retail_agent",
            "hospitality_agent",
            "purchasing_agent",
            "budget_guardrail",
            "agent_as_judge",
            "budget_busted_fallback",
            "final_output",
        ]
        for node in expected_nodes:
            self.assertIn(node, nodes)


if __name__ == "__main__":
    unittest.main()
