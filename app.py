import sys
from PyQt6 import QtWidgets, uic, QtCore
from macro_tracker import MacroTracker
from reminders import ReminderManager
from datetime import datetime

class HabitEats(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("MainWindow.ui", self)
        
        # Initialize backend
        self.tracker = MacroTracker()
        self.reminder_manager = ReminderManager()
        
        # Start reminder service
        self.reminder_manager.start_reminder_service(callback=self.on_reminder)
        
        # --- Navigation Connections ---
        self.pushButton_2.clicked.connect(self.open_reminders)
        self.pushButton_3.clicked.connect(self.open_macros)
        
        # --- Functional Connections ---
        self.pushButton.clicked.connect(self.add_macro_entry)  # Add button
        self.pushButton_4.clicked.connect(self.save_entries)    # Save button
        self.pushButton_5.clicked.connect(self.clear_entries)   # Clear button
        
    def open_reminders(self):
        """Open reminders dialog"""
        dialog = QtWidgets.QDialog(self)
        uic.loadUi("Dialog1.ui", dialog)
        
        # Connect dialog buttons
        dialog.buttonBox.accepted.connect(
            lambda: self.save_reminder(dialog)
        )
        
        dialog.exec()

    def open_macros(self):
        """Open current macros dialog with live data"""
        dialog = QtWidgets.QDialog(self)
        uic.loadUi("Dialog2.ui", dialog)
        
        # Get today's entries and totals
        entries = self.tracker.get_today_entries()
        progress = self.tracker.get_today_progress()
        
        # Populate table with entries
        table = dialog.findChild(QtWidgets.QTableWidget, "tableWidget")
        if table and entries:
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Food", "Calories", "Protein", "Fat", "Carbs"])
            table.setRowCount(len(entries))
            
            for row, entry in enumerate(entries):
                table.setItem(row, 0, QtWidgets.QTableWidgetItem(entry["food_name"]))
                table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(entry["calories"])))
                table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(entry["protein"])))
                table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(entry["fat"])))
                table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(entry["carbs"])))
        
        # Update progress bars
        progress_bar_cal = dialog.findChild(QtWidgets.QProgressBar, "progressBar")
        progress_bar_protein = dialog.findChild(QtWidgets.QProgressBar, "progressBar_2")
        progress_bar_fat = dialog.findChild(QtWidgets.QProgressBar, "progressBar_3")
        progress_bar_carbs = dialog.findChild(QtWidgets.QProgressBar, "progressBar_4")
        
        if progress_bar_cal:
            progress_bar_cal.setValue(min(100, int(progress["calories"]["percentage"])))
        if progress_bar_protein:
            progress_bar_protein.setValue(min(100, int(progress["protein"]["percentage"])))
        if progress_bar_fat:
            progress_bar_fat.setValue(min(100, int(progress["fat"]["percentage"])))
        if progress_bar_carbs:
            progress_bar_carbs.setValue(min(100, int(progress["carbs"]["percentage"])))
        
        dialog.exec()

    def add_macro_entry(self):
        """Add a macro entry with validation"""
        try:
            # Capture input fields - note the actual object names from main_window.py
            food = self.lineEdit.text()  # lineEdit has placeholder "Food"
            cals = self.lineEdit_2.text()  # lineEdit_2 has placeholder "Calories"
            fat = self.lineEdit_3.text()  # lineEdit_3 has placeholder "Fat"
            prot = self.lineEdit_4.text()  # lineEdit_4 has placeholder "Protein"
            carbs = self.lineEdit_5.text()  # lineEdit_5 has placeholder "Carbohydrates"
            
            # Add to tracker (with validation)
            result = self.tracker.add_macro(food, cals, prot, fat, carbs)
            
            if result["success"]:
                self.show_message(result["message"], "success")
                # Clear fields for speed of entry
                self.lineEdit.clear()
                self.lineEdit_2.clear()
                self.lineEdit_3.clear()
                self.lineEdit_4.clear()
                self.lineEdit_5.clear()
            else:
                error_text = "\n".join(result.get("errors", ["Unknown error"]))
                self.show_message(error_text, "error")

        except Exception as e:
            self.show_message(f"Error: {str(e)}", "error")

    def save_entries(self):
        """Save current entries (persists to database)"""
        try:
            # The database auto-saves, so this confirms the action
            totals = self.tracker.get_today_totals()
            self.show_message(
                f"Saved! Today's totals:\n"
                f"Calories: {totals['calories']:.0f}\n"
                f"Protein: {totals['protein']:.1f}g\n"
                f"Fat: {totals['fat']:.1f}g\n"
                f"Carbs: {totals['carbs']:.1f}g",
                "success"
            )
        except Exception as e:
            self.show_message(f"Error: {str(e)}", "error")

    def clear_entries(self):
        """Clear today's entries"""
        try:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Confirm Clear",
                "Are you sure you want to clear today's entries?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                result = self.tracker.clear_today()
                if result["success"]:
                    self.show_message(result["message"], "success")
                else:
                    error_text = "\n".join(result.get("errors", ["Unknown error"]))
                    self.show_message(error_text, "error")
        except Exception as e:
            self.show_message(f"Error: {str(e)}", "error")

    def save_reminder(self, dialog):
        """Save reminder from dialog"""
        try:
            # Get datetime from dialog
            datetime_edit = dialog.findChild(QtWidgets.QDateTimeEdit, "dateTimeEdit")
            daily_btn = dialog.findChild(QtWidgets.QPushButton, "pushButton")
            weekly_btn = dialog.findChild(QtWidgets.QPushButton, "pushButton_2")
            
            if not datetime_edit:
                self.show_message("Reminder dialog error", "error")
                return
            
            reminder_datetime = datetime_edit.dateTime().toPyDateTime()
            reminder_type = "daily"  # Default
            
            # Add reminder to database
            result = self.reminder_manager.add_reminder(
                reminder_type,
                reminder_datetime.isoformat()
            )
            
            if result["success"]:
                self.show_message(result["message"], "success")
            else:
                error_text = "\n".join(result.get("errors", ["Unknown error"]))
                self.show_message(error_text, "error")
        except Exception as e:
            self.show_message(f"Error saving reminder: {str(e)}", "error")

    def on_reminder(self, reminder):
        """Callback when a reminder triggers"""
        QtWidgets.QMessageBox.information(
            self,
            "HabitEats Reminder",
            f"Time to log your macros!\n\nReminder: {reminder['reminder_type'].upper()}"
        )

    def show_message(self, message, msg_type="info"):
        """Show message to user"""
        if msg_type == "success":
            QtWidgets.QMessageBox.information(self, "Success", message)
        elif msg_type == "error":
            QtWidgets.QMessageBox.warning(self, "Error", message)
        else:
            QtWidgets.QMessageBox.information(self, "Info", message)
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.reminder_manager.stop_reminder_service()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = HabitEats()
    window.show()
    sys.exit(app.exec())