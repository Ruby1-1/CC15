"""Reminders module for HabitEats"""

from database import Database
from datetime import datetime
import threading
import time


class ReminderManager:
    def __init__(self):
        self.db = Database()
        self.active_thread = None
        self.running = False

    def add_reminder(self, reminder_type, datetime_str):
        """Add a new reminder"""
        try:
            # Parse the datetime
            reminder_datetime = datetime.fromisoformat(datetime_str)

            if self.db.add_reminder(reminder_type, reminder_datetime.isoformat()):
                return {"success": True, "message": f"{reminder_type.title()} reminder set"}
            else:
                return {"success": False, "errors": ["Failed to add reminder"]}
        except Exception as e:
            return {"success": False, "errors": [str(e)]}

    def get_reminders(self):
        """Get all active reminders"""
        return self.db.get_reminders()

    def delete_reminder(self, reminder_id):
        """Delete a reminder"""
        if self.db.delete_reminder(reminder_id):
            return {"success": True}
        else:
            return {"success": False}

    def toggle_reminder(self, reminder_id, is_active):
        """Enable or disable a reminder"""
        if self.db.toggle_reminder(reminder_id, is_active):
            return {"success": True}
        else:
            return {"success": False}

    def start_reminder_service(self, callback=None):
        """Start background reminder checking service"""
        if self.running:
            return

        self.running = True

        def reminder_loop():
            while self.running:
                try:
                    reminders = self.get_reminders()
                    now = datetime.now()

                    for reminder in reminders:
                        reminder_datetime = datetime.fromisoformat(reminder["datetime"])

                        # Check if reminder should trigger (within 1 minute window)
                        time_diff = (reminder_datetime - now).total_seconds()

                        if 0 <= time_diff <= 60:
                            if callback:
                                callback(reminder)

                    # Check every 30 seconds
                    time.sleep(30)

                except Exception as e:
                    print(f"Reminder service error: {e}")
                    time.sleep(30)

        self.active_thread = threading.Thread(target=reminder_loop, daemon=True)
        self.active_thread.start()

    def stop_reminder_service(self):
        """Stop the background reminder service"""
        self.running = False
