import sys
import os
from PyQt6 import QtWidgets, uic, QtCore, QtGui
from macro_tracker import MacroTracker
from reminders import ReminderManager
from datetime import datetime

class HabitEats(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("MainWindow.ui", self)
        
        self.tracker = MacroTracker()
        self.reminder_manager = ReminderManager()
        self.setup_validators()

        self.reminder_timer = QtCore.QTimer()
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(10000)

        self.pushButton_2.clicked.connect(self.open_reminders)
        self.pushButton_6.clicked.connect(self.open_set_target)
        self.pushButton_3.clicked.connect(self.open_macros)

        self.pushButton.clicked.connect(self.add_macro_entry)
        self.pushButton_4.clicked.connect(self.save_entries)
        self.pushButton_5.clicked.connect(self.clear_entries)
    
    def trigger_reminder(self, reminder):
        self.reminder_manager.delete_reminder(reminder['id'])
        QtWidgets.QMessageBox.information(self, "HabitEats", f"Reminder: {reminder['reminder_type']}!")

    def setup_validators(self):
        letter_validator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression("^[a-zA-Z\\s]*$"))
        number_validator = QtGui.QDoubleValidator(0.0, 10000.0, 2)
        self.lineEdit.setValidator(letter_validator)
        for field in [self.lineEdit_2, self.lineEdit_3, self.lineEdit_4, self.lineEdit_5]:
            field.setValidator(number_validator)

    def add_macro_entry(self):
        data = {
            "name": self.lineEdit.text(),
            "cal": self.lineEdit_2.text(),
            "prot": self.lineEdit_4.text(),
            "fat": self.lineEdit_3.text(),
            "carb": self.lineEdit_5.text()
        }
        res = self.tracker.add_macro(data['name'], data['cal'], data['prot'], data['fat'], data['carb'])
        if res["success"]:
            self.show_message("Macro added!")
            self.clear_entries()
        else:
            self.show_message("\n".join(res["errors"]), "error")

    def open_reminders(self):
        try:
            dialog = QtWidgets.QDialog(self)
            ui_path = os.path.join(os.path.dirname(__file__), "Dialog1.ui")
            uic.loadUi(ui_path, dialog)

            dialog.timeEdit.setTime(QtCore.QTime.currentTime())

            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                selected_time = dialog.timeEdit.time().toString("HH:mm")
                today = datetime.now().strftime("%Y-%m-%d")
                reminder_dt = f"{today} {selected_time}:00"

                result = self.reminder_manager.add_reminder("daily", reminder_dt)
                if result.get("success"):
                    QtWidgets.QMessageBox.information(self, "Success", f"Reminder set for {selected_time}")
                else:
                    error_message = "; ".join(result.get("errors", ["Failed to save reminder"]))
                    QtWidgets.QMessageBox.warning(self, "Database Error", error_message)

        except AttributeError as e:
            QtWidgets.QMessageBox.warning(self, "UI Error", f"Widget tracking error: {e}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Reminder dialog error: {e}")

    def check_reminders(self):
        now = datetime.now()
        active = self.reminder_manager.get_active_reminders()

        for r in active:
            try:
                r_time = datetime.fromisoformat(r["datetime"])
            except Exception:
                continue

            if now >= r_time:
                self.trigger_reminder(r)

    def open_set_target(self):
        dialog = QtWidgets.QDialog(self)
        uic.loadUi("Dialog3.ui", dialog)
        dialog.buttonBox.accepted.connect(lambda: self.save_goals(dialog))
        dialog.exec()

    def save_goals(self, dialog):
        res = self.tracker.set_daily_goals(
            dialog.lineEdit_3.text(), dialog.lineEdit_5.text(),
            dialog.lineEdit_4.text(), dialog.lineEdit_10.text()
        )
        self.show_message(res["message"] if res["success"] else "Error")

    def open_macros(self):
        dialog = QtWidgets.QDialog(self)
        uic.loadUi("Dialog2.ui", dialog)
        totals = self.tracker.get_today_totals()
        goals = self.tracker.db.get_daily_goals()

        # Progress bar mapping
        mapping = [
            (dialog.progressBar, totals['calories'], goals['target_calories']),
            (dialog.progressBar_3, totals['protein'], goals['target_protein']),
            (dialog.progressBar_2, totals['fat'], goals['target_fat']),
            (dialog.progressBar_4, totals['carbs'], goals['target_carbs'])
        ]
        for bar, val, goal in mapping:
            bar.setValue(int((val/goal)*100) if goal > 0 else 0)
        dialog.exec()

    def clear_entries(self):
        for f in [self.lineEdit, self.lineEdit_2, self.lineEdit_3, self.lineEdit_4, self.lineEdit_5]:
            f.clear()

    def save_entries(self):
        self.show_message("All entries synced to database.")

    def show_message(self, msg, m_type="info"):
        if m_type == "error":
            QtWidgets.QMessageBox.warning(self, "Error", msg)
        else:
            QtWidgets.QMessageBox.information(self, "Success", msg)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = HabitEats()
    window.show()
    sys.exit(app.exec())