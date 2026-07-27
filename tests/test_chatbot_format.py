"""Unit test for Chatbot response formatting and metadata extraction."""

import re
import unittest
from core.utils import ensure_str


class TestChatbotFormatting(unittest.TestCase):

    def test_ensure_str_handles_list_of_content_blocks(self):
        """Verify ensure_str converts raw Gemini content block lists to clean markdown text."""
        raw_list_response = [
            {"type": "text", "text": "Hello there! It is so wonderful to meet you.\n\n### 1. Chengdu\nGreat food!\n\nRECOMMENDED_DESTINATION: Chengdu, China\nRECOMMENDED_PERSONA: family\nRECOMMENDED_DAYS: 5"}
        ]

        formatted_text = ensure_str(raw_list_response)
        self.assertIsInstance(formatted_text, str)
        self.assertNotIn("{'type'", formatted_text, "Formated text must NOT contain raw Python dict string brackets")
        self.assertTrue(formatted_text.startswith("Hello there!"))
        print("\n[Test Chatbot] Verified ensure_str converts content block list to clean Markdown!")

    def test_recommendation_metadata_parsing(self):
        """Verify RECOMMENDED_DESTINATION metadata is parsed cleanly."""
        reply_text = (
            "Chengdu is wonderful for foodie families!\n\n"
            "RECOMMENDED_DESTINATION: Chengdu, China\n"
            "RECOMMENDED_PERSONA: family\n"
            "RECOMMENDED_DAYS: 6"
        )

        dest_m = re.search(r"RECOMMENDED_DESTINATION:\s*([^\n\r\"'}]+)", reply_text, re.IGNORECASE)
        persona_m = re.search(r"RECOMMENDED_PERSONA:\s*([^\n\r\"'}]+)", reply_text, re.IGNORECASE)
        days_m = re.search(r"RECOMMENDED_DAYS:\s*(\d+)", reply_text, re.IGNORECASE)

        clean_reply = re.sub(r"RECOMMENDED_DESTINATION:.*", "", reply_text, flags=re.IGNORECASE)
        clean_reply = re.sub(r"RECOMMENDED_PERSONA:.*", "", clean_reply, flags=re.IGNORECASE)
        clean_reply = re.sub(r"RECOMMENDED_DAYS:.*", "", clean_reply, flags=re.IGNORECASE).strip()

        self.assertIsNotNone(dest_m)
        self.assertEqual(dest_m.group(1).strip(), "Chengdu, China")
        self.assertEqual(persona_m.group(1).strip(), "family")
        self.assertEqual(int(days_m.group(1).strip()), 6)
        self.assertEqual(clean_reply, "Chengdu is wonderful for foodie families!")
        print("[Test Chatbot] Verified recommendation metadata parsed and stripped cleanly!")


if __name__ == "__main__":
    unittest.main()
