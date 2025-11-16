import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from main import HearthIntelligence


class TestHearthIntelligence(unittest.TestCase):
    @patch('main.psycopg2')
    @patch('main.httpx')
    async def test_handle_summarize(self, mock_httpx, mock_psycopg2):
        # Create an instance of the HearthIntelligence class
        intelligence = HearthIntelligence()

        # Create a mock message
        message = {
            "room_id": "test_room",
        }

        # Mock the generate_daily_summary method
        intelligence.generate_daily_summary = AsyncMock(
            return_value="This is a summary"
        )

        # Call the handle_summarize method
        result = await intelligence.process_message(
            {"content": "/summarize", "room_id": "test_room"}
        )

        # Assert that the generate_daily_summary method was called with the correct room_id
        intelligence.generate_daily_summary.assert_called_with("test_room")

        # Assert that the handle_summarize method returned the correct action
        self.assertEqual(
            result,
            {
                "action": "send_message",
                "room_id": "test_room",
                "content": "This is a summary",
            },
        )


if __name__ == "__main__":
    unittest.main()