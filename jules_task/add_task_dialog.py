from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
)
from .database import DatabaseManager


class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Task")
        self.db_manager = DatabaseManager()

        self.description_input = QLineEdit()
        self.frequency_input = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow("Frequency:", self.frequency_input)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def accept(self):
        description = self.description_input.text().strip()
        frequency = self.frequency_input.text().strip()
        if not description or not frequency:
            QMessageBox.warning(
                self, "Required fields", "Please fill in all fields."
            )
            return

        super().accept()

    def get_task_data(self):
        return {
            "description": self.description_input.text(),
            "frequency": self.frequency_input.text(),
        }