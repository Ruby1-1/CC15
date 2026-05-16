"""Database module for HabitEats - handles SQLite persistence"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


class Database:
    def __init__(self, db_path="habitéats.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Macro entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS macro_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                food_name TEXT NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                fat REAL NOT NULL,
                carbs REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date DATE NOT NULL
            )
        """)

        # Reminders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reminder_type TEXT NOT NULL,
                datetime TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Daily goals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL UNIQUE,
                target_calories REAL DEFAULT 2000,
                target_protein REAL DEFAULT 150,
                target_fat REAL DEFAULT 70,
                target_carbs REAL DEFAULT 250
            )
        """)

        conn.commit()
        conn.close()

    # ===== MACRO ENTRIES =====
    def add_entry(self, food_name, calories, protein, fat, carbs, date=None):
        """Add a macro entry to the database"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO macro_entries 
                (food_name, calories, protein, fat, carbs, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (food_name, calories, protein, fat, carbs, date))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding entry: {e}")
            return False
        finally:
            conn.close()

    def get_entries(self, date=None):
        """Get all entries for a specific date"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM macro_entries WHERE date = ? ORDER BY created_at DESC
        """, (date,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_daily_totals(self, date=None):
        """Get total macros for a specific date"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                SUM(calories) as total_calories,
                SUM(protein) as total_protein,
                SUM(fat) as total_fat,
                SUM(carbs) as total_carbs
            FROM macro_entries WHERE date = ?
        """, (date,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "calories": row["total_calories"] or 0,
                "protein": row["total_protein"] or 0,
                "fat": row["total_fat"] or 0,
                "carbs": row["total_carbs"] or 0,
            }
        return {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}

    def clear_entries(self, date=None):
        """Clear all entries for a specific date"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM macro_entries WHERE date = ?", (date,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing entries: {e}")
            return False
        finally:
            conn.close()

    def delete_entry(self, entry_id):
        """Delete a specific entry"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM macro_entries WHERE id = ?", (entry_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting entry: {e}")
            return False
        finally:
            conn.close()

    # ===== REMINDERS =====
    def add_reminder(self, reminder_type, datetime_str):
        """Add a reminder (daily or weekly)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO reminders (reminder_type, datetime, is_active)
                VALUES (?, ?, 1)
            """, (reminder_type, datetime_str))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding reminder: {e}")
            return False
        finally:
            conn.close()

    def get_reminders(self):
        """Get all active reminders"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM reminders WHERE is_active = 1 ORDER BY datetime
        """)

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def toggle_reminder(self, reminder_id, is_active):
        """Enable/disable a reminder"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE reminders SET is_active = ? WHERE id = ?
            """, (is_active, reminder_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating reminder: {e}")
            return False
        finally:
            conn.close()

    def delete_reminder(self, reminder_id):
        """Delete a reminder"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting reminder: {e}")
            return False
        finally:
            conn.close()

    # ===== DAILY GOALS =====
    def set_daily_goals(self, date, target_calories, target_protein, target_fat, target_carbs):
        """Set daily macro goals"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO daily_goals 
                (date, target_calories, target_protein, target_fat, target_carbs)
                VALUES (?, ?, ?, ?, ?)
            """, (date, target_calories, target_protein, target_fat, target_carbs))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error setting goals: {e}")
            return False
        finally:
            conn.close()

    def get_daily_goals(self, date=None):
        """Get daily goals for a specific date"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM daily_goals WHERE date = ?
        """, (date,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)

        # Return default goals if not set
        return {
            "date": date,
            "target_calories": 2000,
            "target_protein": 150,
            "target_fat": 70,
            "target_carbs": 250,
        }
