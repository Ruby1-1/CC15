import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from macro_tracker import MacroTracker
from reminders import ReminderManager
from main_window import Ui_MainWindow
from macros_dialog import Ui_Dialog as Ui_MacrosDialog
from reminders_dialog import Ui_Dialog as Ui_RemindersDialog
from set_target import Ui_Dialog as Ui_SetTargetDialog
from datetime import datetime

class HabitEats(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._bind_ui_widgets()
        
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
    
    def _bind_ui_widgets(self):
        for name in [
            "lineEdit", "lineEdit_2", "lineEdit_3", "lineEdit_4", "lineEdit_5",
            "pushButton", "pushButton_2", "pushButton_3", "pushButton_4", "pushButton_5", "pushButton_6",
        ]:
            setattr(self, name, getattr(self.ui, name))

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
        dialog = QtWidgets.QDialog(self)
        ui = Ui_RemindersDialog()
        ui.setupUi(dialog)

        ui.timeEdit.setTime(QtCore.QTime.currentTime())

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            selected_time = ui.timeEdit.time().toString("HH:mm")
            today = datetime.now().strftime("%Y-%m-%d")
            reminder_dt = f"{today} {selected_time}:00"

            result = self.reminder_manager.add_reminder("daily", reminder_dt)
            if result.get("success"):
                QtWidgets.QMessageBox.information(self, "Success", f"Reminder set for {selected_time}")
            else:
                error_message = "; ".join(result.get("errors", ["Failed to save reminder"]))
                QtWidgets.QMessageBox.warning(self, "Database Error", error_message)

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
        ui = Ui_SetTargetDialog()
        ui.setupUi(dialog)

        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.save_goals(ui)

    def save_goals(self, ui):
        res = self.tracker.set_daily_goals(
            ui.lineEdit_3.text(), ui.lineEdit_5.text(),
            ui.lineEdit_4.text(), ui.lineEdit_10.text()
        )
        self.show_message(res["message"] if res["success"] else "Error")

    def open_macros(self):
        dialog = QtWidgets.QDialog(self)
        ui = Ui_MacrosDialog()
        ui.setupUi(dialog)
        totals = self.tracker.get_today_totals()
        goals = self.tracker.db.get_daily_goals()

        # Progress bar mapping
        mapping = [
            (ui.progressBar, totals['calories'], goals['target_calories']),
            (ui.progressBar_3, totals['protein'], goals['target_protein']),
            (ui.progressBar_2, totals['fat'], goals['target_fat']),
            (ui.progressBar_4, totals['carbs'], goals['target_carbs'])
        ]
        for bar, val, goal in mapping:
            bar.setValue(int((val/goal)*100) if goal > 0 else 0)
        dialog.exec()

    def clear_entries(self):
        result = self.tracker.clear_today()
        for f in [self.lineEdit, self.lineEdit_2, self.lineEdit_3, self.lineEdit_4, self.lineEdit_5]:
            f.clear()

        if result.get("success"):
            self.show_message("All saved entries cleared.")
        else:
            self.show_message("Failed to clear saved entries.", m_type="error")

    def save_entries(self):
        success = self.tracker.db.export_to_csv()
        if success:
            self.show_message("All entries saved and exported to backup.csv!")
        else:
            self.show_message("Saving to CSV failed.", m_type="error")

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