"""Utility functions and testing tools for HabitEats backend"""

from macro_tracker import MacroTracker
from reminders import ReminderManager
from datetime import datetime, timedelta


def test_macro_tracking():
    """Test macro tracking functionality"""
    print("=" * 50)
    print("Testing Macro Tracking")
    print("=" * 50)

    tracker = MacroTracker()

    # Test 1: Add entries
    print("\n1. Adding macro entries...")
    test_foods = [
        ("Chicken Breast", 165, 31, 3.6, 0),
        ("Rice", 130, 2.7, 0.3, 28),
        ("Broccoli", 34, 2.8, 0.4, 7),
    ]

    for food, cal, prot, fat, carbs in test_foods:
        result = tracker.add_macro(food, cal, prot, fat, carbs)
        print(f"  {food}: {result['message'] if result['success'] else result['errors']}")

    # Test 2: Get today's entries
    print("\n2. Retrieving today's entries...")
    entries = tracker.get_today_entries()
    print(f"  Found {len(entries)} entries:")
    for entry in entries:
        print(f"    - {entry['food_name']}: {entry['calories']} cal, {entry['protein']}g protein")

    # Test 3: Get totals
    print("\n3. Getting daily totals...")
    totals = tracker.get_today_totals()
    print(f"  Calories: {totals['calories']:.0f}")
    print(f"  Protein: {totals['protein']:.1f}g")
    print(f"  Fat: {totals['fat']:.1f}g")
    print(f"  Carbs: {totals['carbs']:.1f}g")

    # Test 4: Get progress
    print("\n4. Getting progress toward goals...")
    progress = tracker.get_today_progress()
    for macro, data in progress.items():
        print(f"  {macro.title()}: {data['current']:.0f} / {data['goal']} ({data['percentage']:.1f}%)")

    # Test 5: Validation error handling
    print("\n5. Testing validation (invalid input)...")
    result = tracker.add_macro("", "", "invalid", -50, 0)
    print(f"  Errors caught: {result['errors']}")

    # Test 6: Clear entries
    print("\n6. Clearing today's entries...")
    result = tracker.clear_today()
    print(f"  Result: {result['message']}")

    # Verify cleared
    remaining = tracker.get_today_entries()
    print(f"  Entries remaining: {len(remaining)}")


def test_reminders():
    """Test reminder functionality"""
    print("\n" + "=" * 50)
    print("Testing Reminder System")
    print("=" * 50)

    reminder_mgr = ReminderManager()

    # Test 1: Add reminders
    print("\n1. Adding reminders...")

    # Tomorrow at 9 AM
    tomorrow_9am = datetime.now() + timedelta(days=1)
    tomorrow_9am = tomorrow_9am.replace(hour=9, minute=0, second=0, microsecond=0)

    result = reminder_mgr.add_reminder("daily", tomorrow_9am.isoformat())
    print(f"  Daily reminder: {result['message'] if result['success'] else result['errors']}")

    # In 5 minutes (for testing)
    soon = datetime.now() + timedelta(minutes=5)
    result = reminder_mgr.add_reminder("daily", soon.isoformat())
    print(f"  Test reminder (5 min): {result['message'] if result['success'] else result['errors']}")

    # Test 2: Get reminders
    print("\n2. Retrieving reminders...")
    reminders = reminder_mgr.get_reminders()
    print(f"  Found {len(reminders)} reminders:")
    for rem in reminders:
        print(f"    - {rem['reminder_type'].title()} at {rem['datetime']}")

    # Test 3: Delete a reminder (if exists)
    print("\n3. Testing deletion...")
    if reminders:
        result = reminder_mgr.delete_reminder(reminders[0]["id"])
        print(f"  Deleted reminder: {result}")

    # Test 4: Start reminder service
    print("\n4. Starting reminder service (30 second demo)...")

    def test_callback(reminder):
        print(f"  🔔 REMINDER TRIGGERED: {reminder['reminder_type'].upper()}")

    reminder_mgr.start_reminder_service(callback=test_callback)
    print("  Service started (monitoring for 30 seconds)...")

    import time
    time.sleep(30)

    reminder_mgr.stop_reminder_service()
    print("  Service stopped")


def test_goals():
    """Test daily goals functionality"""
    print("\n" + "=" * 50)
    print("Testing Daily Goals")
    print("=" * 50)

    tracker = MacroTracker()

    # Test 1: Set custom goals
    print("\n1. Setting custom daily goals...")
    result = tracker.set_daily_goals(2500, 180, 80, 300)
    print(f"  {result['message']}")

    # Test 2: Get current goals
    print("\n2. Retrieving current goals...")
    goals = tracker.db.get_daily_goals()
    print(f"  Calories: {goals['target_calories']}")
    print(f"  Protein: {goals['target_protein']}g")
    print(f"  Fat: {goals['target_fat']}g")
    print(f"  Carbs: {goals['target_carbs']}g")


def run_all_tests():
    """Run all test suites"""
    print("\n")
    print("█" * 50)
    print("HABITÉATS BACKEND TEST SUITE")
    print("█" * 50)

    try:
        test_macro_tracking()
        test_goals()
        test_reminders()

        print("\n" + "█" * 50)
        print("✅ ALL TESTS COMPLETED")
        print("█" * 50 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Uncomment the test suite you want to run:
    run_all_tests()
    # test_macro_tracking()
    # test_reminders()
    # test_goals()
