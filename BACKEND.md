# HabitEats - Nutrition Tracking Application

## Backend Architecture

### Overview
HabitEats is a PyQt6-based macro tracking application with a complete backend system for persistent data storage, reminder management, and macro calculations.

---

## Project Structure

```
app.py                  # Main application entry point
main_window.py          # Auto-generated UI code (MainWindow)
macros_dialog.py        # Auto-generated UI code (Dialog2 - Current Macros)
reminders_dialog.py     # Auto-generated UI code (Dialog1 - Set Reminders)
database.py             # Database layer with SQLite
macro_tracker.py        # Business logic for macro management
reminders.py            # Reminder management and background service
config.py               # Configuration and defaults
test_backend.py         # Backend testing suite
```

---

## Backend Modules

### 1. **database.py** - Data Persistence Layer
Handles all SQLite database operations.

**Key Classes:**
- `Database`: Main database interface

**Main Methods:**
- `add_entry(food_name, calories, protein, fat, carbs)` - Add a macro entry
- `get_entries(date)` - Retrieve entries for a specific date
- `get_daily_totals(date)` - Get sum of all macros for a date
- `clear_entries(date)` - Delete all entries for a date
- `delete_entry(entry_id)` - Delete a specific entry
- `add_reminder(reminder_type, datetime)` - Add a reminder
- `get_reminders()` - Get all active reminders
- `set_daily_goals(date, calories, protein, fat, carbs)` - Set daily targets
- `get_daily_goals(date)` - Get daily goals

**Database Schema:**
- `macro_entries` - Stores individual food entries
- `reminders` - Stores reminder settings
- `daily_goals` - Stores daily macro targets

---

### 2. **macro_tracker.py** - Business Logic
Higher-level logic with validation and calculations.

**Key Class:**
- `MacroTracker`: Main tracker interface

**Main Methods:**
- `add_macro(food, calories, protein, fat, carbs)` - Validates and adds entry
- `get_today_entries()` - Get all today's entries
- `get_today_totals()` - Get today's macro totals
- `get_today_progress()` - Get progress toward daily goals with percentages
- `clear_today()` - Clear today's entries
- `set_daily_goals(cal, prot, fat, carbs)` - Update daily goals
- `add_reminder(type, datetime)` - Add a reminder

**Validation:**
All numeric inputs are validated before database storage.

---

### 3. **reminders.py** - Reminder Management
Manages reminders with background service.

**Key Class:**
- `ReminderManager`: Manages reminders

**Main Methods:**
- `add_reminder(reminder_type, datetime)` - Add reminder
- `get_reminders()` - Get all active reminders
- `delete_reminder(reminder_id)` - Delete a reminder
- `start_reminder_service(callback)` - Start background monitoring
- `stop_reminder_service()` - Stop background service

**Background Service:**
- Checks for reminders every 30 seconds
- Triggers callback when reminder time is reached

---

### 4. **config.py** - Configuration
Centralized settings for the application.

**Customizable Options:**
- `DEFAULT_DAILY_GOALS` - Set default macro targets
- `DATABASE_PATH` - Database file location
- `REMINDER_CHECK_INTERVAL` - How often to check reminders (seconds)

---

### 5. **app.py** - Main Application
PyQt6 UI controller that connects frontend to backend.

**Key Methods:**
- `add_macro_entry()` - Handle add button click
- `save_entries()` - Display today's summary
- `clear_entries()` - Clear today with confirmation
- `open_reminders()` - Show reminders dialog
- `open_macros()` - Show macro progress dialog
- `on_reminder()` - Callback for triggered reminders

---

## Features

### Core Features
✅ **Add Macro Entries**
- Food name
- Calories
- Protein (grams)
- Fat (grams)  
- Carbohydrates (grams)

✅ **View Daily Totals**
- Aggregate all entries for today
- Display in table format

✅ **Progress Tracking**
- Visual progress bars for each macro
- Percentage of daily goals achieved
- Customizable daily targets

✅ **Reminder System**
- Set daily/weekly reminders
- Background monitoring
- UI notifications when triggered

✅ **Data Persistence**
- SQLite database (survives app restart)
- Date-based entry organization
- Full entry history

---

## Usage Examples

### Add a Macro Entry
```python
tracker = MacroTracker()
result = tracker.add_macro("Chicken Breast", 165, 31, 3.6, 0)
if result["success"]:
    print(result["message"])
else:
    print(result["errors"])
```

### Get Today's Progress
```python
progress = tracker.get_today_progress()
print(f"Calories: {progress['calories']['current']} / {progress['calories']['goal']}")
print(f"Progress: {progress['calories']['percentage']:.1f}%")
```

### Set Reminders
```python
reminder_mgr = ReminderManager()
result = reminder_mgr.add_reminder("daily", "2024-05-15T09:00:00")
reminder_mgr.start_reminder_service(callback=my_callback_function)
```

---

## Data Flow

```
User Input (GUI)
    ↓
app.py (Validation & UI Control)
    ↓
macro_tracker.py (Business Logic)
    ↓
database.py (SQLite Storage)
    ↓
Display in UI (Tables, Progress Bars, Messages)
```

---

## Daily Goals

Default daily targets (customizable in `config.py`):
- **Calories**: 2000 kcal
- **Protein**: 150g
- **Fat**: 70g
- **Carbs**: 250g

Goals can be updated per-day via `set_daily_goals()`.

---

## Database File

- **Location**: `habitéats.db` (in application directory)
- **Type**: SQLite 3
- **Auto-created**: Yes, on first run
- **Portable**: Can be backed up and moved between systems

---

## Error Handling

All operations return a result dictionary:
```python
{
    "success": bool,
    "message": str,      # Success message
    "errors": [str, ...] # List of error messages
}
```

Validation includes:
- Non-empty food names
- Valid numeric values
- Reasonable numeric ranges
- Datetime format validation

---

## Testing

Run the complete test suite:
```bash
python test_backend.py
```

This will test:
- Macro entry addition and retrieval
- Daily totals calculation
- Progress tracking
- Goal setting
- Reminder management
- Background reminder service

---

## Requirements

```
PyQt6>=6.4.0
```

Install with: `pip install PyQt6`

---

## Running the Application

```bash
python app.py
```

The application will:
1. Create/open `habitéats.db`
2. Initialize database tables (if new)
3. Start the reminder background service
4. Display the main window

---

## Notes

- Database is automatically saved after each operation
- Reminders check every 30 seconds (configurable)
- All timestamps use local timezone
- Dates use YYYY-MM-DD format
- Clearing entries requires confirmation
