import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bot import MemuBot
from nio import RoomMessageText, MatrixRoom, InviteMemberEvent
from datetime import datetime

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
