import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from brain import Brain

@pytest.mark.asyncio
async def test_brain_generate_success():
    brain = Brain()
    # Mock httpx response
    with patch("httpx.AsyncClient") as mock_client:
        # Create the mock response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test AI Response"}
        mock_response.raise_for_status = MagicMock()

        # Create the post method mock (must be async)
        mock_post = AsyncMock(return_value=mock_response)

        # Mock the context manager __aenter__ to return an object with the .post method
        mock_context = AsyncMock()
        mock_context.post = mock_post

        # Wire it up: Client() returns the context manager that has __aenter__
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value = mock_context
        mock_client_instance.__aexit__.return_value = None

        # When httpx.AsyncClient() is called, return the instance
        mock_client.return_value = mock_client_instance

        response = await brain.generate("Test prompt")
        assert response == "Test AI Response"

@pytest.mark.asyncio
async def test_extract_reminder_json():
    brain = Brain()
    brain.generate = AsyncMock(return_value='{"task": "buy milk", "time": "tomorrow"}')

    result = await brain.extract_reminder("remind me to buy milk tomorrow")
    assert result['task'] == "buy milk"
    assert result['time'] == "tomorrow"

@pytest.mark.asyncio
async def test_extract_reminder_json_with_markdown():
    brain = Brain()
    brain.generate = AsyncMock(return_value='```json\n{"task": "sleep", "time": "now"}\n```')

    result = await brain.extract_reminder("sleep now")
    assert result['task'] == "sleep"
    assert result['time'] == "now"
