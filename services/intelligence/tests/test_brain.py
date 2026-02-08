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

    result = await brain.extract_reminder("sleep now")
    assert result['task'] == "sleep"
    assert result['time'] == "now"


@pytest.mark.asyncio
async def test_analyze_intent_parsing():
    """Test parsing of valid intent JSON."""
    brain = Brain()
    # Mock successful JSON response
    brain.generate = AsyncMock(return_value='{"intent": "CALENDAR", "content": "soccer practice"}')
    
    result = await brain.analyze_intent("Is there soccer practice?")
    
    assert result['intent'] == "CALENDAR"
    assert result['content'] == "soccer practice"


@pytest.mark.asyncio
async def test_analyze_intent_malformed():
    """Test handling of invalid JSON response from LLM."""
    brain = Brain()
    # Mock broken JSON
    brain.generate = AsyncMock(return_value='Not JSON at all')
    
    result = await brain.analyze_intent("Some query")
    
    # Should fallback to NONE and original content
    assert result['intent'] == "NONE"
    assert result['content'] == "Some query"


@pytest.mark.asyncio
async def test_synthesise_cross_silo():
    """Test that synthesis calls generate with correct context."""
    brain = Brain()
    brain.generate = AsyncMock(return_value="Integrated answer")
    
    await brain.synthesise_cross_silo("query", "Context extracted from silos")
    
    brain.generate.assert_called_once()
    args = brain.generate.call_args
    prompt = args[0][0]
    system = args.kwargs['system_prompt']
    
    assert "Context extracted from silos" in prompt
    assert "Chief of Staff" in system
