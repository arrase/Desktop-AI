from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
)


class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Task")

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

    def get_task_data(self):
        return {
            "description": self.description_input.text(),
            "frequency": self.frequency_input.text(),
        }
