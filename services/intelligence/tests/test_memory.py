"""
Tests for MemoryStore backup functionality.

Following TDD: These tests are written FIRST, before implementation.
Run with: pytest tests/test_memory.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


# Mock the config before importing memory module
@pytest.fixture(autouse=True)
def mock_config():
    with patch('config.Config') as mock:
        mock.DB_HOST = 'localhost'
        mock.DB_NAME = 'test_db'
        mock.DB_USER = 'test_user'
        mock.DB_PASSWORD = 'test_pass'
        yield mock


@pytest.fixture
def mock_pool():
    """Create a mock database pool with async context manager support."""
    pool = AsyncMock()
    conn = AsyncMock()

    # Make pool.acquire() return an async context manager
    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
    pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

    return pool, conn


@pytest.fixture
def memory_store(mock_pool):
    """Create a MemoryStore with mocked pool."""
    from memory import MemoryStore

    pool, conn = mock_pool
    store = MemoryStore()
    store.pool = pool
    return store, conn


# =============================================================================
# Test: init_db creates backup_history table
# =============================================================================

@pytest.mark.asyncio
async def test_init_db_creates_backup_history_table(memory_store):
    """init_db should create the backup_history table with correct schema."""
    store, conn = memory_store

    await store.init_db()

    # Verify execute was called
    conn.execute.assert_called_once()

    # Get the SQL that was executed
    sql = conn.execute.call_args[0][0]

    # Verify backup_history table is in the SQL
    assert 'backup_history' in sql
    assert 'CREATE TABLE IF NOT EXISTS backup_history' in sql

    # Verify required columns exist
    assert 'filename TEXT NOT NULL' in sql
    assert 'size_bytes BIGINT NOT NULL' in sql
    assert 'status TEXT NOT NULL' in sql
    assert 'error TEXT' in sql
    assert 'duration_seconds INT' in sql
    assert 'usb_copied_at TIMESTAMP' in sql
    assert 'notification_sent BOOLEAN' in sql
    assert 'created_at TIMESTAMP' in sql

    # Verify index is created
    assert 'idx_backup_created' in sql


# =============================================================================
# Test: record_backup stores backup metadata
# =============================================================================

@pytest.mark.asyncio
async def test_record_backup_success(memory_store):
    """record_backup should insert a successful backup record."""
    store, conn = memory_store

    await store.record_backup(
        filename='memu_backup_20250126_020500.tar.gz',
        size_bytes=245_000_000,
        status='success',
        duration_seconds=180
    )

    conn.execute.assert_called_once()
    sql = conn.execute.call_args[0][0]
    args = conn.execute.call_args[0][1:]

    assert 'INSERT INTO backup_history' in sql
    assert 'memu_backup_20250126_020500.tar.gz' in args
    assert 245_000_000 in args
    assert 'success' in args
    assert 180 in args


@pytest.mark.asyncio
async def test_record_backup_failure(memory_store):
    """record_backup should store error message for failed backups."""
    store, conn = memory_store

    await store.record_backup(
        filename='memu_backup_20250126_020500.tar.gz',
        size_bytes=0,
        status='failed',
        duration_seconds=5,
        error='Disk full'
    )

    conn.execute.assert_called_once()
    args = conn.execute.call_args[0][1:]

    assert 'failed' in args
    assert 'Disk full' in args


# =============================================================================
# Test: get_latest_backup returns most recent backup
# =============================================================================

@pytest.mark.asyncio
async def test_get_latest_backup_returns_dict(memory_store):
    """get_latest_backup should return backup details as dictionary."""
    store, conn = memory_store

    # Mock the database response
    mock_row = {
        'id': 1,
        'filename': 'memu_backup_20250126_020500.tar.gz',
        'size_bytes': 245_000_000,
        'status': 'success',
        'error': None,
        'duration_seconds': 180,
        'usb_copied_at': datetime(2025, 1, 24, 10, 30, 0),
        'notification_sent': False,
        'created_at': datetime(2025, 1, 26, 2, 5, 0)
    }
    conn.fetchrow.return_value = mock_row

    result = await store.get_latest_backup()

    conn.fetchrow.assert_called_once()
    sql = conn.fetchrow.call_args[0][0]
    assert 'SELECT' in sql
    assert 'backup_history' in sql
    assert 'ORDER BY created_at DESC' in sql
    assert 'LIMIT 1' in sql

    assert result['filename'] == 'memu_backup_20250126_020500.tar.gz'
    assert result['status'] == 'success'
    assert result['size_bytes'] == 245_000_000


@pytest.mark.asyncio
async def test_get_latest_backup_returns_none_when_empty(memory_store):
    """get_latest_backup should return None if no backups exist."""
    store, conn = memory_store
    conn.fetchrow.return_value = None

    result = await store.get_latest_backup()

    assert result is None


# =============================================================================
# Test: get_backup_count returns number of backups
# =============================================================================

@pytest.mark.asyncio
async def test_get_backup_count(memory_store):
    """get_backup_count should return total number of successful backups."""
    store, conn = memory_store
    conn.fetchval.return_value = 7

    result = await store.get_backup_count()

    conn.fetchval.assert_called_once()
    sql = conn.fetchval.call_args[0][0]
    assert 'COUNT' in sql
    assert 'backup_history' in sql
    assert result == 7


# =============================================================================
# Test: get_total_backup_size returns sum of sizes
# =============================================================================

@pytest.mark.asyncio
async def test_get_total_backup_size(memory_store):
    """get_total_backup_size should return sum of all backup sizes."""
    store, conn = memory_store
    conn.fetchval.return_value = 1_700_000_000  # 1.7 GB

    result = await store.get_total_backup_size()

    conn.fetchval.assert_called_once()
    sql = conn.fetchval.call_args[0][0]
    assert 'SUM' in sql or 'sum' in sql.lower()
    assert 'size_bytes' in sql
    assert result == 1_700_000_000


@pytest.mark.asyncio
async def test_get_total_backup_size_returns_zero_when_empty(memory_store):
    """get_total_backup_size should return 0 if no backups exist."""
    store, conn = memory_store
    conn.fetchval.return_value = None

    result = await store.get_total_backup_size()

    assert result == 0


# =============================================================================
# Test: mark_usb_copied updates timestamp
# =============================================================================

@pytest.mark.asyncio
async def test_mark_usb_copied(memory_store):
    """mark_usb_copied should update usb_copied_at for latest backup."""
    store, conn = memory_store

    await store.mark_usb_copied(backup_id=5)

    conn.execute.assert_called_once()
    sql = conn.execute.call_args[0][0]
    args = conn.execute.call_args[0][1:]

    assert 'UPDATE backup_history' in sql
    assert 'usb_copied_at' in sql
    assert 5 in args


# =============================================================================
# Test: get_unnotified_failures returns failed backups not yet notified
# =============================================================================

@pytest.mark.asyncio
async def test_get_unnotified_failures(memory_store):
    """get_unnotified_failures should return failed backups where notification_sent is False."""
    store, conn = memory_store

    mock_rows = [
        {'id': 3, 'filename': 'backup1.tar.gz', 'error': 'Disk full', 'created_at': datetime.now()},
        {'id': 5, 'filename': 'backup2.tar.gz', 'error': 'Permission denied', 'created_at': datetime.now()}
    ]
    conn.fetch.return_value = mock_rows

    result = await store.get_unnotified_failures()

    conn.fetch.assert_called_once()
    sql = conn.fetch.call_args[0][0]
    assert "status = 'failed'" in sql or 'status' in sql
    assert 'notification_sent' in sql

    assert len(result) == 2
    assert result[0]['error'] == 'Disk full'


# =============================================================================
# Test: mark_notification_sent marks backup as notified
# =============================================================================

@pytest.mark.asyncio
async def test_mark_notification_sent(memory_store):
    """mark_notification_sent should set notification_sent to True."""
    store, conn = memory_store

    await store.mark_notification_sent(backup_id=3)

    conn.execute.assert_called_once()
    sql = conn.execute.call_args[0][0]
    args = conn.execute.call_args[0][1:]

    assert 'UPDATE backup_history' in sql
    assert 'notification_sent' in sql
    assert 3 in args


# =============================================================================
# Test: get_last_usb_backup_time returns most recent USB backup timestamp
# =============================================================================

@pytest.mark.asyncio
async def test_get_last_usb_backup_time(memory_store):
    """get_last_usb_backup_time should return the most recent usb_copied_at timestamp."""
    store, conn = memory_store

    expected_time = datetime(2025, 1, 24, 10, 30, 0)
    conn.fetchval.return_value = expected_time

    result = await store.get_last_usb_backup_time()

    conn.fetchval.assert_called_once()
    sql = conn.fetchval.call_args[0][0]
    assert 'usb_copied_at' in sql
    assert 'MAX' in sql or 'ORDER BY' in sql

    assert result == expected_time


@pytest.mark.asyncio
async def test_get_last_usb_backup_time_returns_none_when_never_copied(memory_store):
    """get_last_usb_backup_time should return None if no USB backup ever made."""
    store, conn = memory_store
    conn.fetchval.return_value = None

    result = await store.get_last_usb_backup_time()

    assert result is None
