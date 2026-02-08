import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bot import MemuBot
from nio import RoomMessageText, MatrixRoom, InviteMemberEvent
from datetime import datetime

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def mock_bot():
    with patch("bot.AsyncClient") as mock_client:
        with patch("bot.MemoryStore") as mock_memory:
            with patch("bot.Brain") as mock_brain:
                bot = MemuBot()
                bot.client = AsyncMock()
                bot.client.user_id = "@bot:test"
                # Mock next_batch for summarize test
                bot.client.next_batch = "s12345"
                bot.memory = AsyncMock()
                bot.brain = AsyncMock()
                return bot

@pytest.mark.asyncio
async def test_process_message_remember(mock_bot):
    await mock_bot.process_message("room1", "@user:test", "/remember the sky is blue")

    mock_bot.memory.remember_fact.assert_called_with("room1", "@user:test", "the sky is blue")
    mock_bot.client.room_send.assert_called_once()

@pytest.mark.asyncio
async def test_invite_callback(mock_bot):
    room = MagicMock(spec=MatrixRoom)
    room.room_id = "room1"
    event = MagicMock(spec=InviteMemberEvent)
    event.sender = "@user:test"

    await mock_bot.invite_callback(room, event)

    mock_bot.client.join.assert_called_with("room1")

@pytest.mark.asyncio
async def test_process_message_addtolist(mock_bot):
    await mock_bot.process_message("room1", "@user:test", "/addtolist milk, eggs")

    mock_bot.memory.add_to_list.assert_called_with("room1", "@user:test", ["milk", "eggs"])
    mock_bot.client.room_send.assert_called_once()

@pytest.mark.asyncio
async def test_process_message_remind_explicit(mock_bot):
    # Mock brain extraction to fail
    mock_bot.brain.extract_reminder.return_value = {}

    # Mock dateparser to return a fixed future date
    future_date = datetime(2030, 1, 1, 12, 0, 0)

    with patch("bot.dateparser.parse", return_value=future_date):
        await mock_bot.process_message("room1", "@user:test", "/remind call mom tomorrow")

    mock_bot.memory.add_reminder.assert_called()
    call_args = mock_bot.memory.add_reminder.call_args
    assert call_args[0][0] == "room1"
    assert call_args[0][2] == "call mom tomorrow"
    assert call_args[0][3] == future_date

@pytest.mark.asyncio
async def test_callback_ignores_self(mock_bot):
    room = MagicMock(spec=MatrixRoom)
    room.room_id = "room1"
    event = MagicMock(spec=RoomMessageText)
    event.sender = "@bot:test" # Same as bot
    event.body = "hello"

    await mock_bot.message_callback(room, event)

    mock_bot.memory.remember_fact.assert_not_called()

@pytest.mark.asyncio
async def test_handle_summarize_success(mock_bot):
    # Mock room_messages response
    mock_response = MagicMock()
    mock_response.chunk = []
    # Add a mock message
    msg = MagicMock(spec=RoomMessageText)
    msg.sender = "@user:test"
    msg.body = "Hello"
    mock_response.chunk.append(msg)

    mock_bot.client.room_messages = AsyncMock(return_value=mock_response)
    mock_bot.brain.summarize_chat.return_value = "Summary of chat"

    await mock_bot.handle_summarize("room1")

    # Check it called room_messages with correct args
    mock_bot.client.room_messages.assert_called_with("room1", start="s12345", direction='b', limit=50)
    mock_bot.brain.summarize_chat.assert_called()
    mock_bot.client.room_send.assert_called()




@pytest.mark.asyncio
async def test_process_message_help(mock_bot):
    """Bot responds to /help with command list."""
    await mock_bot.process_message("room1", "@user:test", "/help")


    mock_bot.client.room_send.assert_called_once()
    call_args = mock_bot.client.room_send.call_args
    assert 'Memu Bot Commands' in call_args.kwargs['content']['body']


@pytest.mark.asyncio
async def test_handle_recall_integration(mock_bot):
    """Test full cross-silo recall flow with all silos returning data."""
    # Mock search results
    mock_bot.memory.unified_recall = AsyncMock(return_value={
        "facts": [{"fact": "The sky is blue", "created_at": 1234567890}],
        "chat": [{"sender": "@mom:test", "body": "Look at the blue sky", "timestamp": 1234567890}]
    })
    mock_bot.calendar.is_available = AsyncMock(return_value=True)
    mock_bot.calendar.search_events = AsyncMock(return_value=[
        {"summary": "Blue Sky Festival", "start": datetime(2025, 5, 1), "location": "Park"}
    ])
    
    # Mock internal methods that would call external APIs
    with patch.object(mock_bot, '_search_photos', new_callable=AsyncMock) as mock_photos:
        mock_photos.return_value = [
            {"filename": "sky.jpg", "city": "London", "date": "2025-05-01"}
        ]
        
        # Mock brain synthesis
        mock_bot.brain.synthesise_cross_silo = AsyncMock(return_value="Synthesis: The sky is blue and you have photos of it.")

        await mock_bot.handle_recall("room1", "/recall blue")

        # Verify all silos were queried
        mock_bot.memory.unified_recall.assert_called_with("room1", "blue")
        mock_bot.calendar.search_events.assert_called_with("blue")
        mock_photos.assert_called_with("blue")
        
        # Verify brain was called for synthesis
        mock_bot.brain.synthesise_cross_silo.assert_called()
        
        # Verify response sent
        mock_bot.client.room_send.assert_called_once()
        args = mock_bot.client.room_send.call_args[1]
        assert "Synthesis: The sky is blue" in args['content']['body']


@pytest.mark.asyncio
async def test_cross_silo_search_partial_failure(mock_bot):
    """Test that search continues even if one silo fails."""
    # Memory works
    mock_bot.memory.unified_recall = AsyncMock(return_value={
        "facts": [{"fact": "Fact 1", "created_at": 123}],
        "chat": []
    })
    
    # Calendar works
    mock_bot.calendar.is_available = AsyncMock(return_value=True)
    mock_bot.calendar.search_events = AsyncMock(return_value=[
        {"summary": "Event 1", "start": datetime(2025,1,1), "location": "Loc"}
    ])
    
    # Photos fail
    with patch.object(mock_bot, '_search_photos', new_callable=AsyncMock) as mock_photos:
        mock_photos.side_effect = Exception("Immich down")
        
        # Brain works
        mock_bot.brain.synthesise_cross_silo = AsyncMock(return_value="Sythesis result")

        await mock_bot.handle_recall("room1", "/recall test")

        # Verify bot didn't crash and sent a response
        mock_bot.client.room_send.assert_called_once()
        
        # Verify call arguments to synthesis ONLY contained the working silo data
        # We expect synthesis because we have Facts and Calendar (2 silos)
        mock_bot.brain.synthesise_cross_silo.assert_called()
        call_args = mock_bot.brain.synthesise_cross_silo.call_args
        context_str = call_args[0][1] # second arg is context
        
        assert "Fact 1" in context_str
        assert "Event 1" in context_str
        assert "Photos" not in context_str

