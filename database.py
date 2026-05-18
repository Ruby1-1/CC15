"""CSV storage module for HabitEats - handles file persistence."""

import csv
from datetime import datetime
from pathlib import Path


class Database:
    def __init__(self, db_path="habiteats_entries.csv"):
        self.db_path = Path(db_path)
        self.goals_path = self.db_path.parent / "habiteats_goals.csv"
        self.reminders_path = self.db_path.parent / "habiteats_reminders.csv"
        self.init_storage()

    def init_storage(self):
        """Initialize CSV storage files and headers."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._ensure_csv(
            self.db_path,
            ["id", "food_name", "calories", "protein", "fat", "carbs", "created_at", "date"],
        )
        self._ensure_csv(
            self.goals_path,
            ["date", "target_calories", "target_protein", "target_fat", "target_carbs"],
        )
        self._ensure_csv(
            self.reminders_path,
            ["id", "reminder_type", "datetime", "is_active", "created_at"],
        )

    def _ensure_csv(self, path: Path, headers):
        if not path.exists():
            with path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(headers)

    def _read_rows(self, path: Path):
        if not path.exists():
            return []
        with path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return [row for row in reader]

    def _write_rows(self, path: Path, rows, headers):
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    def _next_id(self, rows):
        if not rows:
            return 1
        existing_ids = [int(row.get("id", 0)) for row in rows if row.get("id")]
        return max(existing_ids, default=0) + 1

    # ===== MACRO ENTRIES =====
    def add_entry(self, food_name, calories, protein, fat, carbs, date=None):
        """Add a macro entry to the CSV store."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        rows = self._read_rows(self.db_path)
        entry_id = self._next_id(rows)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        rows.append(
            {
                "id": str(entry_id),
                "food_name": food_name,
                "calories": str(calories),
                "protein": str(protein),
                "fat": str(fat),
                "carbs": str(carbs),
                "created_at": created_at,
                "date": date,
            }
        )

        self._write_rows(
            self.db_path,
            rows,
            ["id", "food_name", "calories", "protein", "fat", "carbs", "created_at", "date"],
        )
        return True

    def get_entries(self, date=None):
        """Get all entries for a specific date."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        rows = self._read_rows(self.db_path)
        entries = [
            {
                "id": int(row["id"]),
                "food_name": row["food_name"],
                "calories": float(row["calories"]),
                "protein": float(row["protein"]),
                "fat": float(row["fat"]),
                "carbs": float(row["carbs"]),
                "created_at": row["created_at"],
                "date": row["date"],
            }
            for row in rows
            if row["date"] == date
        ]

        return sorted(entries, key=lambda item: item["created_at"], reverse=True)

    def get_daily_totals(self, date=None):
        """Get total macros for a specific date."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        rows = self._read_rows(self.db_path)
        totals = {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0}

        for row in rows:
            if row["date"] != date:
                continue
            totals["calories"] += float(row["calories"])
            totals["protein"] += float(row["protein"])
            totals["fat"] += float(row["fat"])
            totals["carbs"] += float(row["carbs"])

        return totals

    def clear_entries(self, date=None):
        """Clear all entries for a specific date."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        rows = self._read_rows(self.db_path)
        filtered = [row for row in rows if row["date"] != date]
        self._write_rows(
            self.db_path,
            filtered,
            ["id", "food_name", "calories", "protein", "fat", "carbs", "created_at", "date"],
        )
        return True

    def delete_entry(self, entry_id):
        """Delete a specific entry."""
        rows = self._read_rows(self.db_path)
        filtered = [row for row in rows if int(row["id"]) != int(entry_id)]
        self._write_rows(
            self.db_path,
            filtered,
            ["id", "food_name", "calories", "protein", "fat", "carbs", "created_at", "date"],
        )
        return True

    # ===== REMINDERS =====
    def add_reminder(self, reminder_type, datetime_str):
        """Add a reminder (daily or weekly)."""
        rows = self._read_rows(self.reminders_path)
        reminder_id = self._next_id(rows)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        rows.append(
            {
                "id": str(reminder_id),
                "reminder_type": reminder_type,
                "datetime": datetime_str,
                "is_active": "1",
                "created_at": created_at,
            }
        )

        self._write_rows(
            self.reminders_path,
            rows,
            ["id", "reminder_type", "datetime", "is_active", "created_at"],
        )
        return True

    def get_reminders(self):
        """Get all reminders."""
        rows = self._read_rows(self.reminders_path)
        reminders = [
            {
                "id": int(row["id"]),
                "reminder_type": row["reminder_type"],
                "datetime": row["datetime"],
                "is_active": bool(int(row["is_active"])),
                "created_at": row["created_at"],
            }
            for row in rows
        ]
        return sorted(reminders, key=lambda item: item["datetime"])

    def toggle_reminder(self, reminder_id, is_active):
        """Enable/disable a reminder."""
        rows = self._read_rows(self.reminders_path)
        for row in rows:
            if int(row["id"]) == int(reminder_id):
                row["is_active"] = "1" if is_active else "0"
        self._write_rows(
            self.reminders_path,
            rows,
            ["id", "reminder_type", "datetime", "is_active", "created_at"],
        )
        return True

    def delete_reminder(self, reminder_id):
        """Delete a reminder."""
        rows = self._read_rows(self.reminders_path)
        filtered = [row for row in rows if int(row["id"]) != int(reminder_id)]
        self._write_rows(
            self.reminders_path,
            filtered,
            ["id", "reminder_type", "datetime", "is_active", "created_at"],
        )
        return True

    # ===== DAILY GOALS =====
    def set_daily_goals(self, date, target_calories, target_protein, target_fat, target_carbs):
        """Set daily macro goals."""
        rows = self._read_rows(self.goals_path)
        replaced = False

        for row in rows:
            if row["date"] == date:
                row["target_calories"] = str(target_calories)
                row["target_protein"] = str(target_protein)
                row["target_fat"] = str(target_fat)
                row["target_carbs"] = str(target_carbs)
                replaced = True
                break

        if not replaced:
            rows.append(
                {
                    "date": date,
                    "target_calories": str(target_calories),
                    "target_protein": str(target_protein),
                    "target_fat": str(target_fat),
                    "target_carbs": str(target_carbs),
                }
            )

        self._write_rows(
            self.goals_path,
            rows,
            ["date", "target_calories", "target_protein", "target_fat", "target_carbs"],
        )
        return True

    def get_daily_goals(self, date=None):
        """Get daily goals for a specific date."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        rows = self._read_rows(self.goals_path)
        for row in rows:
            if row["date"] == date:
                return {
                    "date": row["date"],
                    "target_calories": float(row["target_calories"]),
                    "target_protein": float(row["target_protein"]),
                    "target_fat": float(row["target_fat"]),
                    "target_carbs": float(row["target_carbs"]),
                }

        return {
            "date": date,
            "target_calories": 2000,
            "target_protein": 150,
            "target_fat": 70,
            "target_carbs": 250,
        }

    def export_to_csv(self, filename="habit_eats_backup.csv"):
        """Create a backup CSV copy of macro entries."""
        rows = self._read_rows(self.db_path)
        if not rows:
            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Food Name", "Calories", "Protein (g)", "Fat (g)", "Carbs (g)", "Date"])
            return True

        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Food Name", "Calories", "Protein (g)", "Fat (g)", "Carbs (g)", "Date"])
            for row in rows:
                writer.writerow(
                    [
                        row["food_name"],
                        row["calories"],
                        row["protein"],
                        row["fat"],
                        row["carbs"],
                        row["date"],
                    ]
                )
        return True
