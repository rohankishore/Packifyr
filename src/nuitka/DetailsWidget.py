from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

"""
This file contains the class for the widget which acts like a dop down layout (kinda like <details> tag in HTML.
"""


class DetailsWidget(QWidget):
    def __init__(self, summary_text, parent=None):
        super().__init__(parent)

        self.is_open = True

        layout = QVBoxLayout()

        self.summary_button = QPushButton(summary_text)
        self.summary_button.clicked.connect(self.toggle_details)
        layout.addWidget(self.summary_button)

        self.details_layout = QVBoxLayout()
        self.details_layout.setContentsMargins(10, 0, 0, 0)  # Set left margin to indent
        layout.addLayout(self.details_layout)

        self.setLayout(layout)

    def add_detail_widget(self, widget):
        self.details_layout.addWidget(widget)

    def add_detail_layout(self, layout):
        self.details_layout.addLayout(layout)

    def toggle_details(self):
        self.is_open = not self.is_open
        for i in range(self.details_layout.count()):
            self.details_layout.itemAt(i).widget().setVisible(self.is_open)
        if self.is_open:
            self.summary_button.setText("Advanced Options <")
        else:
            self.summary_button.setText("Advanced Options >")
