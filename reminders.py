from database import Database
from datetime import datetime

class ReminderManager:
    def __init__(self):
        self.db = Database()

    def add_reminder(self, reminder_type, dt_str):
        try:
            reminder_datetime = datetime.fromisoformat(dt_str)
        except Exception as e:
            return {"success": False, "errors": [f"Invalid datetime format: {e}"]}

        if self.db.add_reminder(reminder_type, reminder_datetime.isoformat(sep=" ")):
            return {"success": True, "message": f"{reminder_type.title()} reminder set"}

        return {"success": False, "errors": ["Failed to add reminder to database"]}

    def get_active_reminders(self):
        return [r for r in self.db.get_reminders() if r['is_active']]

    def delete_reminder(self, r_id):
        return self.db.delete_reminder(r_id)