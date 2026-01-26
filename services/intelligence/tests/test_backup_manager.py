"""
Tests for BackupManager module.

Following TDD: These tests are written FIRST, before implementation.
Run with: pytest tests/test_backup_manager.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def mock_memory():
    """Create a mock MemoryStore."""
    memory = AsyncMock()
    return memory


@pytest.fixture
def backup_manager(mock_memory):
    """Create a BackupManager with mocked dependencies."""
    from backup_manager import BackupManager
    manager = BackupManager(mock_memory)
    return manager, mock_memory


# =============================================================================
# Test: get_status returns correct health assessment
# =============================================================================

@pytest.mark.asyncio
async def test_get_status_healthy(backup_manager):
    """When backups are recent and USB is recent, status is healthy."""
    manager, mock_memory = backup_manager

    mock_memory.get_latest_backup.return_value = {
        'id': 1,
        'filename': 'memu_backup_20250126_020500.tar.gz',
        'size_bytes': 245_000_000,
        'status': 'success',
        'error': None,
        'created_at': datetime.now() - timedelta(hours=6),
        'usb_copied_at': datetime.now() - timedelta(days=2)
    }
    mock_memory.get_backup_count.return_value = 7
    mock_memory.get_total_backup_size.return_value = 1_700_000_000
    mock_memory.get_last_usb_backup_time.return_value = datetime.now() - timedelta(days=2)

    status = await manager.get_status()

    assert status['health'] == 'healthy'
    assert 'hours ago' in status['last_backup_human']
    assert status['backup_count'] == 7


@pytest.mark.asyncio
async def test_get_status_warning_usb_overdue(backup_manager):
    """When USB backup is > 7 days old, status shows warning."""
    manager, mock_memory = backup_manager

    mock_memory.get_latest_backup.return_value = {
        'id': 1,
        'filename': 'memu_backup_20250126_020500.tar.gz',
        'size_bytes': 245_000_000,
        'status': 'success',
        'error': None,
        'created_at': datetime.now() - timedelta(hours=6),
        'usb_copied_at': None
    }
    mock_memory.get_backup_count.return_value = 7
    mock_memory.get_total_backup_size.return_value = 1_700_000_000
    mock_memory.get_last_usb_backup_time.return_value = datetime.now() - timedelta(days=10)

    status = await manager.get_status()

    assert status['health'] == 'warning'
    assert 'usb_overdue' in status['warnings']


@pytest.mark.asyncio
async def test_get_status_critical_backup_failed(backup_manager):
    """When last backup failed, status is critical."""
    manager, mock_memory = backup_manager

    mock_memory.get_latest_backup.return_value = {
        'id': 1,
        'filename': 'memu_backup_20250126_020500.tar.gz',
        'size_bytes': 0,
        'status': 'failed',
        'error': 'Disk full',
        'created_at': datetime.now() - timedelta(hours=6),
        'usb_copied_at': None
    }
    mock_memory.get_backup_count.return_value = 6
    mock_memory.get_total_backup_size.return_value = 1_500_000_000
    mock_memory.get_last_usb_backup_time.return_value = None

    status = await manager.get_status()

    assert status['health'] == 'critical'
    assert status['error'] == 'Disk full'


@pytest.mark.asyncio
async def test_get_status_no_backups(backup_manager):
    """When no backups exist, status reflects this."""
    manager, mock_memory = backup_manager

    mock_memory.get_latest_backup.return_value = None
    mock_memory.get_backup_count.return_value = 0
    mock_memory.get_total_backup_size.return_value = 0
    mock_memory.get_last_usb_backup_time.return_value = None

    status = await manager.get_status()

    assert status['health'] == 'critical'
    assert status['backup_count'] == 0
    assert 'no_backups' in status['warnings']


# =============================================================================
# Test: format_status_message returns human-readable text
# =============================================================================

def test_format_status_message_healthy():
    """Healthy status message includes all key info."""
    from backup_manager import BackupManager

    manager = BackupManager(None)
    status = {
        'health': 'healthy',
        'last_backup_human': '6 hours ago',
        'last_backup_size_human': '245 MB',
        'backup_count': 7,
        'total_size_human': '1.7 GB',
        'usb_days_ago': 2,
        'warnings': [],
        'error': None
    }

    message = manager.format_status_message(status)

    assert 'Backup Status' in message
    assert '6 hours ago' in message
    assert '245 MB' in message
    assert '7' in message
    assert '2 days ago' in message or '2' in message
    assert 'healthy' in message.lower() or 'All systems healthy' in message


def test_format_status_message_warning():
    """Warning status message highlights the issue."""
    from backup_manager import BackupManager

    manager = BackupManager(None)
    status = {
        'health': 'warning',
        'last_backup_human': '6 hours ago',
        'last_backup_size_human': '245 MB',
        'backup_count': 7,
        'total_size_human': '1.7 GB',
        'usb_days_ago': 12,
        'warnings': ['usb_overdue'],
        'error': None
    }

    message = manager.format_status_message(status)

    assert 'USB' in message or 'usb' in message.lower()
    assert 'overdue' in message.lower() or '12' in message


def test_format_status_message_critical():
    """Critical status message shows error prominently."""
    from backup_manager import BackupManager

    manager = BackupManager(None)
    status = {
        'health': 'critical',
        'last_backup_human': '6 hours ago',
        'last_backup_size_human': '0 B',
        'backup_count': 6,
        'total_size_human': '1.5 GB',
        'usb_days_ago': None,
        'warnings': [],
        'error': 'Disk full'
    }

    message = manager.format_status_message(status)

    assert 'Disk full' in message or 'failed' in message.lower()


# =============================================================================
# Test: should_send_usb_reminder logic
# =============================================================================

@pytest.mark.asyncio
async def test_should_send_usb_reminder_true(backup_manager):
    """Reminder should be sent when USB backup is overdue."""
    manager, mock_memory = backup_manager

    mock_memory.get_last_usb_backup_time.return_value = datetime.now() - timedelta(days=8)

    should_remind = await manager.should_send_usb_reminder()

    assert should_remind is True


@pytest.mark.asyncio
async def test_should_send_usb_reminder_false_recent(backup_manager):
    """No reminder when USB backup is recent."""
    manager, mock_memory = backup_manager

    mock_memory.get_last_usb_backup_time.return_value = datetime.now() - timedelta(days=3)

    should_remind = await manager.should_send_usb_reminder()

    assert should_remind is False


@pytest.mark.asyncio
async def test_should_send_usb_reminder_true_never_backed_up(backup_manager):
    """Reminder should be sent if never backed up to USB."""
    manager, mock_memory = backup_manager

    mock_memory.get_last_usb_backup_time.return_value = None

    should_remind = await manager.should_send_usb_reminder()

    assert should_remind is True


# =============================================================================
# Test: format_size utility
# =============================================================================

def test_format_size_bytes():
    """Small sizes shown in bytes."""
    from backup_manager import BackupManager

    assert BackupManager.format_size(500) == '500 B'


def test_format_size_kilobytes():
    """Kilobyte sizes formatted correctly."""
    from backup_manager import BackupManager

    assert BackupManager.format_size(1024) == '1.0 KB'
    assert BackupManager.format_size(1536) == '1.5 KB'


def test_format_size_megabytes():
    """Megabyte sizes formatted correctly."""
    from backup_manager import BackupManager

    assert BackupManager.format_size(1024 * 1024) == '1.0 MB'
    assert BackupManager.format_size(245 * 1024 * 1024) == '245.0 MB'


def test_format_size_gigabytes():
    """Gigabyte sizes formatted correctly."""
    from backup_manager import BackupManager

    assert BackupManager.format_size(1024 * 1024 * 1024) == '1.0 GB'
    assert BackupManager.format_size(int(1.7 * 1024 * 1024 * 1024)) == '1.7 GB'


# =============================================================================
# Test: format_time_ago utility
# =============================================================================

def test_format_time_ago_minutes():
    """Recent times shown in minutes."""
    from backup_manager import BackupManager

    result = BackupManager.format_time_ago(datetime.now() - timedelta(minutes=30))
    assert 'minutes ago' in result or '30' in result


def test_format_time_ago_hours():
    """Hours ago formatted correctly."""
    from backup_manager import BackupManager

    result = BackupManager.format_time_ago(datetime.now() - timedelta(hours=6))
    assert 'hours ago' in result or '6' in result


def test_format_time_ago_days():
    """Days ago formatted correctly."""
    from backup_manager import BackupManager

    result = BackupManager.format_time_ago(datetime.now() - timedelta(days=3))
    assert 'days ago' in result or '3' in result
