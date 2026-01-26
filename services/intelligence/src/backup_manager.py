"""
Backup Manager for Memu.

Handles backup status monitoring, notifications, and USB backup coordination.
"""

import logging
import json
import os
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

logger = logging.getLogger("memu.backup")

# USB detection paths
USB_MARKER_FILE = "/tmp/memu/usb_detected"
USB_RESULT_FILE = "/tmp/memu/usb_result"
USB_BACKUP_SCRIPT = "/opt/memu/scripts/usb-backup.sh"


class BackupManager:
    """Manages backup status, notifications, and USB coordination."""

    # Threshold for USB backup warning (days)
    USB_WARNING_DAYS = 7

    def __init__(self, memory):
        """Initialize the backup manager.

        Args:
            memory: MemoryStore instance for database access
        """
        self.memory = memory

    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive backup status.

        Returns:
            Dictionary containing:
            - health: 'healthy', 'warning', or 'critical'
            - last_backup_human: Human-readable time since last backup
            - last_backup_size_human: Human-readable size
            - backup_count: Number of local backups
            - total_size_human: Total size of all backups
            - usb_days_ago: Days since last USB backup (or None)
            - warnings: List of warning codes
            - error: Error message if last backup failed
        """
        latest = await self.memory.get_latest_backup()
        backup_count = await self.memory.get_backup_count()
        total_size = await self.memory.get_total_backup_size()
        last_usb = await self.memory.get_last_usb_backup_time()

        warnings = []
        health = 'healthy'
        error = None

        # Calculate time since last USB backup
        usb_days_ago = None
        if last_usb:
            usb_days_ago = (datetime.now() - last_usb).days
            if usb_days_ago > self.USB_WARNING_DAYS:
                warnings.append('usb_overdue')
                health = 'warning'
        else:
            # Never backed up to USB
            warnings.append('usb_overdue')
            health = 'warning'

        # Check if we have any backups
        if not latest:
            warnings.append('no_backups')
            return {
                'health': 'critical',
                'last_backup_human': 'Never',
                'last_backup_size_human': '0 B',
                'backup_count': 0,
                'total_size_human': '0 B',
                'usb_days_ago': None,
                'warnings': warnings,
                'error': 'No backups found'
            }

        # Check if last backup failed
        if latest.get('status') == 'failed':
            health = 'critical'
            error = latest.get('error', 'Unknown error')

        # Calculate human-readable values
        last_backup_time = latest.get('created_at')
        last_backup_human = self.format_time_ago(last_backup_time) if last_backup_time else 'Unknown'
        last_backup_size_human = self.format_size(latest.get('size_bytes', 0))
        total_size_human = self.format_size(total_size)

        return {
            'health': health,
            'last_backup_human': last_backup_human,
            'last_backup_size_human': last_backup_size_human,
            'backup_count': backup_count,
            'total_size_human': total_size_human,
            'usb_days_ago': usb_days_ago,
            'warnings': warnings,
            'error': error
        }

    def format_status_message(self, status: Dict[str, Any]) -> str:
        """Format backup status as a human-readable message for the bot.

        Args:
            status: Status dictionary from get_status()

        Returns:
            Formatted message string for Element chat
        """
        lines = ["**Backup Status**", ""]

        # Last backup info
        lines.append(f"Last backup: {status['last_backup_human']} ({status['last_backup_size_human']})")
        lines.append(f"Local backups: {status['backup_count']} stored ({status['total_size_human']} total)")

        # USB backup info
        if status['usb_days_ago'] is not None:
            lines.append(f"USB backup: {status['usb_days_ago']} days ago")
        else:
            lines.append("USB backup: Never")

        lines.append("")

        # Health status
        if status['health'] == 'healthy':
            lines.append("Health: All systems healthy")
        elif status['health'] == 'warning':
            if 'usb_overdue' in status.get('warnings', []):
                lines.append("Health: USB backup overdue - plug in your backup drive!")
        elif status['health'] == 'critical':
            if status.get('error'):
                lines.append(f"Health: BACKUP FAILED - {status['error']}")
            elif 'no_backups' in status.get('warnings', []):
                lines.append("Health: No backups found!")
            else:
                lines.append("Health: Critical issue detected")

        return "\n".join(lines)

    async def should_send_usb_reminder(self) -> bool:
        """Check if a USB backup reminder should be sent.

        Returns:
            True if reminder should be sent (USB backup > 7 days old or never done)
        """
        last_usb = await self.memory.get_last_usb_backup_time()

        if last_usb is None:
            # Never backed up to USB
            return True

        days_since = (datetime.now() - last_usb).days
        return days_since > self.USB_WARNING_DAYS

    async def get_unnotified_failures(self) -> List[Dict[str, Any]]:
        """Get failed backups that haven't been notified yet.

        Returns:
            List of failed backup records
        """
        return await self.memory.get_unnotified_failures()

    async def mark_notification_sent(self, backup_id: int):
        """Mark a backup's failure notification as sent.

        Args:
            backup_id: ID of the backup record
        """
        await self.memory.mark_notification_sent(backup_id)

    def format_failure_message(self, backup: Dict[str, Any]) -> str:
        """Format a backup failure as a notification message.

        Args:
            backup: Backup record dictionary

        Returns:
            Formatted message string
        """
        error = backup.get('error', 'Unknown error')
        filename = backup.get('filename', 'Unknown')

        lines = [
            "**Backup Alert**",
            "",
            f"Last night's backup failed: {error}",
            "",
            "Action needed: Check disk space or system logs",
            "",
            "Use `/backup-status` for details"
        ]

        return "\n".join(lines)

    def format_usb_reminder_message(self, status: Dict[str, Any]) -> str:
        """Format USB backup reminder message.

        Args:
            status: Current backup status

        Returns:
            Formatted reminder message
        """
        days = status.get('usb_days_ago')
        if days:
            days_text = f"It's been {days} days since your last USB backup."
        else:
            days_text = "You haven't made a USB backup yet."

        lines = [
            "**Weekly Backup Reminder**",
            "",
            days_text,
            "",
            "Plug in your backup drive to save a copy of your family's data.",
            f"Current backup size: ~{status.get('total_size_human', 'unknown')}"
        ]

        return "\n".join(lines)

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format bytes as human-readable size.

        Args:
            size_bytes: Size in bytes

        Returns:
            Human-readable string (e.g., '245.0 MB')
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    @staticmethod
    def format_time_ago(dt: datetime) -> str:
        """Format a datetime as human-readable time ago.

        Args:
            dt: Datetime to format

        Returns:
            Human-readable string (e.g., '6 hours ago')
        """
        if dt is None:
            return "Unknown"

        now = datetime.now()
        diff = now - dt

        if diff.days > 0:
            if diff.days == 1:
                return "1 day ago"
            return f"{diff.days} days ago"

        hours = diff.seconds // 3600
        if hours > 0:
            if hours == 1:
                return "1 hour ago"
            return f"{hours} hours ago"

        minutes = diff.seconds // 60
        if minutes > 0:
            if minutes == 1:
                return "1 minute ago"
            return f"{minutes} minutes ago"

        return "Just now"

    # =========================================================================
    # USB Backup Handling
    # =========================================================================

    async def check_usb_detected(self) -> bool:
        """Check if a USB drive has been detected.

        Returns:
            True if USB marker file exists
        """
        return os.path.exists(USB_MARKER_FILE)

    async def handle_usb_backup(self) -> Optional[Dict[str, Any]]:
        """Handle USB backup when drive is detected.

        Runs the USB backup script and returns the result.

        Returns:
            Result dictionary or None if no USB detected
        """
        if not os.path.exists(USB_MARKER_FILE):
            return None

        logger.info("USB drive detected, starting backup copy...")

        try:
            # Run the USB backup script
            if os.path.exists(USB_BACKUP_SCRIPT):
                result = subprocess.run(
                    [USB_BACKUP_SCRIPT],
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour timeout
                )

                if result.returncode != 0:
                    logger.error(f"USB backup failed: {result.stderr}")
                    return {
                        'status': 'error',
                        'message': result.stderr or 'USB backup failed'
                    }

            # Read result file
            if os.path.exists(USB_RESULT_FILE):
                with open(USB_RESULT_FILE, 'r') as f:
                    result_data = json.load(f)

                # Mark backup as USB copied in database
                if result_data.get('status') == 'success':
                    latest = await self.memory.get_latest_backup()
                    if latest:
                        await self.memory.mark_usb_copied(latest['id'])

                # Clean up result file
                os.remove(USB_RESULT_FILE)

                return result_data

        except subprocess.TimeoutExpired:
            logger.error("USB backup timed out")
            return {'status': 'error', 'message': 'USB backup timed out'}
        except Exception as e:
            logger.error(f"USB backup error: {e}")
            return {'status': 'error', 'message': str(e)}

        return None

    def format_usb_success_message(self, result: Dict[str, Any]) -> str:
        """Format USB backup success message.

        Args:
            result: Result dictionary from USB backup

        Returns:
            Formatted message for Element chat
        """
        label = result.get('usb_label', 'USB drive')
        filename = result.get('filename', 'backup')
        size = result.get('size', 'unknown size')

        lines = [
            "**USB Backup Complete**",
            "",
            f"Copied latest backup to '{label}' drive.",
            f"File: {filename} ({size})",
            "",
            "Safe to remove the drive."
        ]

        return "\n".join(lines)

    def format_usb_error_message(self, result: Dict[str, Any]) -> str:
        """Format USB backup error message.

        Args:
            result: Result dictionary from USB backup

        Returns:
            Formatted error message
        """
        error = result.get('message', 'Unknown error')

        lines = [
            "**USB Backup Failed**",
            "",
            f"Error: {error}",
            "",
            "Please check the USB drive and try again."
        ]

        return "\n".join(lines)
