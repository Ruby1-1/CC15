"""Macro Tracker module - business logic for HabitEats"""

from database import Database
from datetime import datetime


class MacroTracker:
    def __init__(self):
        self.db = Database()

    def add_macro(self, food_name, calories, protein, fat, carbs):
        """Validate and add a macro entry"""
        # Validation
        errors = []

        if not food_name or not food_name.strip():
            errors.append("Food name is required")
        if not self._is_valid_number(calories):
            errors.append("Calories must be a valid number")
        if not self._is_valid_number(protein):
            errors.append("Protein must be a valid number")
        if not self._is_valid_number(fat):
            errors.append("Fat must be a valid number")
        if not self._is_valid_number(carbs):
            errors.append("Carbs must be a valid number")

        if errors:
            return {"success": False, "errors": errors}

        # Convert to float
        try:
            calories = float(calories)
            protein = float(protein)
            fat = float(fat)
            carbs = float(carbs)
        except ValueError:
            return {"success": False, "errors": ["Invalid numeric values"]}

        # Add to database
        if self.db.add_entry(food_name, calories, protein, fat, carbs):
            return {"success": True, "message": f"Added {food_name}"}
        else:
            return {"success": False, "errors": ["Failed to add entry to database"]}

    def get_today_entries(self):
        """Get all entries for today"""
        return self.db.get_entries()

    def get_today_totals(self):
        """Get today's macro totals"""
        return self.db.get_daily_totals()

    def get_today_progress(self):
        """Get today's progress towards goals"""
        totals = self.get_today_totals()
        goals = self.db.get_daily_goals()

        return {
            "calories": {
                "current": totals["calories"],
                "goal": goals["target_calories"],
                "percentage": (
                    (totals["calories"] / goals["target_calories"] * 100)
                    if goals["target_calories"] > 0
                    else 0
                ),
            },
            "protein": {
                "current": totals["protein"],
                "goal": goals["target_protein"],
                "percentage": (
                    (totals["protein"] / goals["target_protein"] * 100)
                    if goals["target_protein"] > 0
                    else 0
                ),
            },
            "fat": {
                "current": totals["fat"],
                "goal": goals["target_fat"],
                "percentage": (
                    (totals["fat"] / goals["target_fat"] * 100)
                    if goals["target_fat"] > 0
                    else 0
                ),
            },
            "carbs": {
                "current": totals["carbs"],
                "goal": goals["target_carbs"],
                "percentage": (
                    (totals["carbs"] / goals["target_carbs"] * 100)
                    if goals["target_carbs"] > 0
                    else 0
                ),
            },
        }

    def clear_today(self):
        """Clear all today's entries"""
        if self.db.clear_entries():
            return {"success": True, "message": "Entries cleared"}
        else:
            return {"success": False, "errors": ["Failed to clear entries"]}

    def delete_entry(self, entry_id):
        """Delete a specific entry"""
        if self.db.delete_entry(entry_id):
            return {"success": True}
        else:
            return {"success": False}

    def set_daily_goals(self, calories, protein, fat, carbs):
        """Set daily macro goals"""
        errors = []

        if not self._is_valid_number(calories):
            errors.append("Calories must be a valid number")
        if not self._is_valid_number(protein):
            errors.append("Protein must be a valid number")
        if not self._is_valid_number(fat):
            errors.append("Fat must be a valid number")
        if not self._is_valid_number(carbs):
            errors.append("Carbs must be a valid number")

        if errors:
            return {"success": False, "errors": errors}

        try:
            calories = float(calories)
            protein = float(protein)
            fat = float(fat)
            carbs = float(carbs)
        except ValueError:
            return {"success": False, "errors": ["Invalid numeric values"]}

        today = datetime.now().strftime("%Y-%m-%d")
        if self.db.set_daily_goals(today, calories, protein, fat, carbs):
            return {"success": True, "message": "Goals updated"}
        else:
            return {"success": False, "errors": ["Failed to update goals"]}

    def add_reminder(self, reminder_type, datetime_str):
        """Add a reminder"""
        if reminder_type not in ["daily", "weekly"]:
            return {"success": False, "errors": ["Invalid reminder type"]}

        if self.db.add_reminder(reminder_type, datetime_str):
            return {"success": True, "message": f"Added {reminder_type} reminder"}
        else:
            return {"success": False, "errors": ["Failed to add reminder"]}

    def get_reminders(self):
        """Get all reminders"""
        return self.db.get_reminders()

    def delete_reminder(self, reminder_id):
        """Delete a reminder"""
        if self.db.delete_reminder(reminder_id):
            return {"success": True}
        else:
            return {"success": False}

    @staticmethod
    def _is_valid_number(value):
        """Check if value is a valid number"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
