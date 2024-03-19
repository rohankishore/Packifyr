import json

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton
from qfluentwidgets import (LineEdit, StrongBodyLabel, MessageBox)

with open("resources/misc/config.json", "r") as themes_file:
    _themes = json.load(themes_file)


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Settings")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addStretch()

        theming_group = QGroupBox("Theming")
        theming_layout = QVBoxLayout(theming_group)
        layout.addWidget(theming_group)

        # Theme Color Label
        theme_color_label = StrongBodyLabel("Theme Color: ", self)
        theming_layout.addWidget(theme_color_label)

        # Theme Color Line Edit
        self.theme_color_line_edit = LineEdit()
        self.theme_color_line_edit.setText(_themes["theme"])
        theming_layout.addWidget(self.theme_color_line_edit)


        # Apply Button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.save_json)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

    def save_json(self):

        with open("resources/misc/config.json", "w") as json_file:
            json.dump(_themes, json_file)

        w = MessageBox(
            'Settings Applied!',
            "Restart Youtility to view the changes",
            self
        )
        w.yesButton.setText('Cool 🤝')
        w.cancelButton.setText('Extra Cool 😘')

        if w.exec():
            pass
