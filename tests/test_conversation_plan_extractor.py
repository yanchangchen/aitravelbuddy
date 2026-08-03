"""Unit test for extracting trip plan specs & preferences from concierge conversation history."""

import unittest
from ui.landing import extract_plan_from_conversation


class TestConversationPlanExtractor(unittest.TestCase):

    def test_extract_plan_from_conversation_transcript(self):
        """Verify extract_plan_from_conversation parses conversation history into structured trip specs."""
        guided_messages = [
            {
                "role": "assistant",
                "content": "👋 Hello Traveler! What vibe are you looking for?"
            },
            {
                "role": "user",
                "content": "I am planning a 5-day family trip to Chengdu, China with my wife and daughter in September. We want great food like Dan Dan noodles and mapo tofu, panda visits, and a comfortable walking pace."
            },
            {
                "role": "assistant",
                "content": "Chengdu is fantastic for foodie families! You will love the Giant Panda Breeding Base and Jinli Ancient Street.\n\nRECOMMENDED_DESTINATION: Chengdu, China\nRECOMMENDED_PERSONA: family\nRECOMMENDED_DAYS: 5"
            }
        ]

        specs = extract_plan_from_conversation(guided_messages, gemini_key="")
        self.assertIsInstance(specs, dict)
        self.assertIn("destination", specs)
        self.assertEqual(specs["destination"], "Chengdu, China")
        self.assertEqual(specs["num_days"], 5)
        self.assertIn("rules", specs)
        print(f"\n[Test Conv Plan Extractor] Extracted Specs for destination: '{specs['destination']}' ({specs['num_days']} Days)")


if __name__ == "__main__":
    unittest.main()
