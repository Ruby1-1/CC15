import sys
from PyQt6 import QtWidgets, uic, QtCore, QtGui
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
        
        # Setup input validators
        self.setup_validators()
        
        # Start reminder service
        self.reminder_manager.start_reminder_service(callback=self.on_reminder)
        
        # --- Navigation Connections ---
        self.pushButton_2.clicked.connect(self.open_reminders)
        self.pushButton_6.clicked.connect(self.open_set_target)  # Set Target button
        self.pushButton_3.clicked.connect(self.open_macros)
        
        # --- Functional Connections ---
        self.pushButton.clicked.connect(self.add_macro_entry)  # Add button
        self.pushButton_4.clicked.connect(self.save_entries)    # Save button
        self.pushButton_5.clicked.connect(self.clear_entries)   # Clear button
    
    def setup_validators(self):
        """Setup input validators for fields"""
        # Food field - only letters and spaces
        letter_validator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression("^[a-zA-Z\\s]*$"))
        self.lineEdit.setValidator(letter_validator)
        
        # Numeric fields - only numbers and decimals
        number_validator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression("^[0-9]*\\.?[0-9]*$"))
        self.lineEdit_2.setValidator(number_validator)  # Calories
        self.lineEdit_3.setValidator(number_validator)  # Fat
        self.lineEdit_4.setValidator(number_validator)  # Protein
        self.lineEdit_5.setValidator(number_validator)  # Carbs
        
    def open_reminders(self):
        """Open reminders dialog"""
        dialog = QtWidgets.QDialog(self)
        uic.loadUi("Dialog1.ui", dialog)
        
        # Connect dialog buttons
        dialog.buttonBox.accepted.connect(
            lambda: self.save_reminder(dialog)
        )
        
        dialog.exec()

    def open_set_target(self):
        """Open set target dialog"""
        dialog = QtWidgets.QDialog(self)
        uic.loadUi("Dialog3.ui", dialog)
        
        # Get current targets and populate fields
        current_goals = self.tracker.db.get_daily_goals()
        
        # Set current values in the dialog fields
        cal_field = dialog.findChild(QtWidgets.QLineEdit, "lineEdit_3")
        fat_field = dialog.findChild(QtWidgets.QLineEdit, "lineEdit_4")
        prot_field = dialog.findChild(QtWidgets.QLineEdit, "lineEdit_5")
        carbs_field = dialog.findChild(QtWidgets.QLineEdit, "lineEdit_10")
        
        if cal_field:
            cal_field.setText(str(current_goals["target_calories"]))
        if fat_field:
            fat_field.setText(str(current_goals["target_fat"]))
        if prot_field:
            prot_field.setText(str(current_goals["target_protein"]))
        if carbs_field:
            carbs_field.setText(str(current_goals["target_carbs"]))
        
        # Connect dialog buttons
        dialog.buttonBox.accepted.connect(
            lambda: self.save_target(dialog)
        )
        
        dialog.exec()
    
    def save_target(self, dialog):
        """Save custom macro targets"""
        try:
            cal_field = dialog.findChild(QtWidgets.QLineEdit, "lineEdit_3")
            fat_field = dialog.findChild(QtWidgets.QLineEdit, "lineEdit_4")
            prot_field = dialog.findChild(QtWidgets.QLineEdit, "lineEdit_5")
            carbs_field = dialog.findChild(QtWidgets.QLineEdit, "lineEdit_10")
            
            calories = cal_field.text() if cal_field else "2000"
            fat = fat_field.text() if fat_field else "70"
            protein = prot_field.text() if prot_field else "150"
            carbs = carbs_field.text() if carbs_field else "250"
            
            # Save the targets
            result = self.tracker.set_daily_goals(calories, protein, fat, carbs)
            
            if result["success"]:
                self.show_message(result["message"], "success")
            else:
                error_text = "\n".join(result.get("errors", ["Unknown error"]))
                self.show_message(error_text, "error")
        except Exception as e:
            self.show_message(f"Error saving targets: {str(e)}", "error")

    def open_macros(self):
        """Open current macros dialog with live data - clean redesign"""
        dialog = QtWidgets.QDialog(self)
        uic.loadUi("Dialog2.ui", dialog)
        
        # Get today's entries and totals
        progress = self.tracker.get_today_progress()
        
        # --- HIDE THE TABLE ---
        table = dialog.findChild(QtWidgets.QTableWidget, "tableWidget")
        if table:
            table.hide()
        
        # --- PROGRESS BARS WITH LABELS ---
        labels = [
            dialog.findChild(QtWidgets.QLabel, "label_3"),  # Calories
            dialog.findChild(QtWidgets.QLabel, "label_4"),  # Protein
            dialog.findChild(QtWidgets.QLabel, "label_5"),  # Fats
            dialog.findChild(QtWidgets.QLabel, "label_6"),  # Carbs
        ]
        
        bars = [
            dialog.findChild(QtWidgets.QProgressBar, "progressBar"),
            dialog.findChild(QtWidgets.QProgressBar, "progressBar_2"),
            dialog.findChild(QtWidgets.QProgressBar, "progressBar_3"),
            dialog.findChild(QtWidgets.QProgressBar, "progressBar_4"),
        ]
        
        # Update each macro
        for label, bar in zip(labels, bars):
            if not label or not bar:
                continue
            
            # Get the current label text to determine which macro it is
            current_text = label.text()
            
            if "Cal" in current_text or "calories" in current_text.lower():
                data = progress["calories"]
                current, goal, percent = data["current"], data["goal"], data["percentage"]
                label.setText(f"Calories")
                bar.setValue(min(100, int(percent)))
                bar.setFormat(f"{percent:.0f}%")
            elif "Protein" in current_text:
                data = progress["protein"]
                current, goal, percent = data["current"], data["goal"], data["percentage"]
                label.setText(f"Protein")
                bar.setValue(min(100, int(percent)))
                bar.setFormat(f"{percent:.0f}%")
            elif "Fats" in current_text or "Fat" in current_text:
                data = progress["fat"]
                current, goal, percent = data["current"], data["goal"], data["percentage"]
                label.setText(f"Fats")
                bar.setValue(min(100, int(percent)))
                bar.setFormat(f"{percent:.0f}%")
            elif "Carbs" in current_text:
                data = progress["carbs"]
                current, goal, percent = data["current"], data["goal"], data["percentage"]
                label.setText(f"Carbs")
                bar.setValue(min(100, int(percent)))
                bar.setFormat(f"{percent:.0f}%")
        
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