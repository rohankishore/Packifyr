import json
import os

from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton, QComboBox, QFileDialog, QHBoxLayout, \
    QSpacerItem, QLabel, QListView, QDialogButtonBox, QDialog
from qfluentwidgets import (TextEdit,
                            ListWidget)

with open("resources/misc/config.json", "r") as themes_file:
    _themes = json.load(themes_file)

theme_color = _themes["theme"]
progressive = _themes["progressive"]


class PyInstaller(QWidget):
    def __init__(self):
        super().__init__()

        spacer_item_small = QSpacerItem(0, 10)
        spacer_item_medium = QSpacerItem(0, 20)

        self.setObjectName("PyInstaller")

        self.icon_file = ""
        self.py_file = ""

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # YouTube Link Entry
        self.link_layout = QVBoxLayout()
        self.main_layout.addLayout(self.link_layout)
        self.link_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.select_file_button = QPushButton("Select Python Script")
        self.select_file_button.clicked.connect(self.select_python_script)
        self.link_layout.addWidget(self.select_file_button)

        self.selected_file_label = QLabel("")
        self.selected_file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.link_layout.addWidget(self.selected_file_label)

        self.main_layout.addSpacerItem(spacer_item_small)

        # Option menu for Quality
        self.options_layout = QVBoxLayout()
        self.main_layout.addLayout(self.options_layout)
        self.exe_type = QComboBox()
        self.exe_type.setPlaceholderText("onedir")
        self.exe_type.addItems(["onedir", "onefile"])
        self.options_layout.addWidget(self.exe_type)

        self.app_type = QComboBox()
        self.app_type.setPlaceholderText("Console Based")
        self.app_type.addItems(["Console Based", "Window Based"])
        self.options_layout.addWidget(self.app_type)

        self.options_layout.addSpacerItem(spacer_item_medium)

        self.icon_select = QPushButton("Select Icon File  (--icon)")
        self.icon_select.clicked.connect(self.select_icon_file)
        self.selected_icon_label = QLabel("")
        self.selected_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.options_layout.addWidget(self.icon_select)
        self.options_layout.addWidget(self.selected_icon_label)

        self.additional_files = QPushButton('Add Files')
        self.additional_files.clicked.connect(self.additional_files_open)
        self.additional_folder = QPushButton('Add Folder')
        self.additional_folder.clicked.connect(self.additional_folders_open)

        self.options_group = QGroupBox("Additional Files / Folders (--add-data)")
        self.options_group_layout = QVBoxLayout(self.options_group)
        self.options_group_layout.addWidget(self.additional_files)
        self.options_group_layout.addWidget(self.additional_folder)
        self.options_layout.addWidget(self.options_group)

        self.main_layout.addSpacerItem(spacer_item_small)

        self.script_layout = QHBoxLayout()
        self.script_layout.addSpacerItem(spacer_item_medium)
        self.main_layout.addLayout(self.script_layout)

        self.cscript = TextEdit()
        self.script_layout.addWidget(self.cscript)

        # Download Button
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.download_button = QPushButton("Execute")
        self.download_button.clicked.connect(self.execute)
        self.button_layout.addWidget(self.download_button)

        # GIF Loading Screen
        self.gif_layout = QHBoxLayout()
        self.main_layout.addLayout(self.gif_layout)
        self.loading_label = QLabel()
        self.main_layout.addWidget(self.loading_label)

        # Progress Area
        self.count_layout = QHBoxLayout()
        # Create a QListWidget to display downloading status
        self.download_list_widget = ListWidget()
        self.count_layout.addWidget(self.download_list_widget)
        self.main_layout.addLayout(self.count_layout)

        self.setLayout(self.main_layout)
        self.caption_list = None  # Define the caption_list attribute

        self.add_files_dialog = QDialog()
        self.add_files_dialog.setWindowTitle("Select Additional Files")
        self.add_files_dialog.setModal(True)

        self.add_folders_dialog = QDialog()
        self.add_folders_dialog.setWindowTitle("Select Additional Folders")
        self.add_folders_dialog.setModal(True)

    def add_files(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                self.file_model.insertRow(self.file_model.rowCount())
                index = self.file_model.index(self.file_model.rowCount() - 1)
                self.file_model.setData(index, file_path)

    def remove_selected(self):
        indexes = self.file_list_view.selectedIndexes()
        for index in sorted(indexes, reverse=True):
            self.file_model.removeRow(index.row())

    def additional_files_open(self):
        if not hasattr(self, 'file_model'):
            self.file_model = QStringListModel()
            self.file_list_view = QListView()
            self.file_list_view.setModel(self.file_model)

            self.add_button = QPushButton("Add Files")
            self.add_button.clicked.connect(self.add_files)

            self.remove_button = QPushButton("Remove Selected")
            self.remove_button.clicked.connect(self.remove_selected)

            self.button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

            layout = QVBoxLayout()
            layout.addWidget(self.file_list_view)
            button_layout = QHBoxLayout()
            button_layout.addWidget(self.add_button)
            button_layout.addWidget(self.remove_button)
            layout.addLayout(button_layout)
            layout.addWidget(self.button_box)

            self.add_files_dialog.setLayout(layout)

        self.add_files_dialog.show()

    def add_folders(self):
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory)
        if folder_dialog.exec():
            selected_folders = folder_dialog.selectedFiles()
            for folder_path in selected_folders:
                self.folder_model.insertRow(self.folder_model.rowCount())
                index = self.folder_model.index(self.folder_model.rowCount() - 1)
                self.folder_model.setData(index, folder_path)

    def remove_folders(self):
        self.folder_list_view = QListView()
        self.folder_list_view.setModel(self.folder_model)
        indexes = self.folder_list_view.selectedIndexes()
        for index in sorted(indexes, reverse=True):
            self.folder_model.removeRow(index.row())

    def additional_folders_open(self):
        if not hasattr(self, 'folder_model'):
            self.folder_model = QStringListModel()
            self.folder_list_view = QListView()
            self.folder_list_view.setModel(self.folder_model)

            self.add_folders_button = QPushButton("Add Folders")
            self.add_folders_button.clicked.connect(self.add_folders)

            self.remove_folders_button = QPushButton("Remove Selected Folders")
            self.remove_folders_button.clicked.connect(self.remove_folders)

            layout = QVBoxLayout()
            layout.addWidget(self.folder_list_view)
            button_layout = QHBoxLayout()
            button_layout.addWidget(self.add_folders_button)
            button_layout.addWidget(self.remove_folders_button)
            layout.addLayout(button_layout)

            self.add_folders_dialog.setLayout(layout)

        self.add_folders_dialog.show()

    def select_python_script(self):
        selected_files = ""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Python files (*.py)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.selected_file_label.setText(selected_files[0])
        self.py_file = selected_files[0]

    def select_icon_file(self):
        selected_files = ""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Icon Files (*.ico)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.selected_icon_label.setText(selected_files[0])
        self.icon_file = selected_files[0]

    def get_selected_files(self):
        file_paths = []
        for row in range(self.folder_model.rowCount()):
            index = self.folder_model.index(row)
            file_paths.append(self.folder_model.data(index))
        return file_paths

    def get_selected_folders(self):
        folder_paths = []
        for row in range(self.folder_model.rowCount()):
            index = self.folder_model.index(row)
            file_path = self.folder_model.data(index)
            if os.path.isdir(file_path):
                folder_paths.append(file_path)
        return folder_paths

    def get_window_status(self):
        status = self.app_type.currentText()
        win_status = ""
        if status == "Console Based":
            win_status = "console"
        else:
            win_status = "windowed"
        return win_status

    def execute(self):

        window_status = self.get_window_status()
        file_status = self.exe_type.currentText()
        
        if file_status == "":
            file_status = "onedir"

        additional_files = ""
        additional_folders = ""
        try:
            additional_files = self.get_selected_files()
            additional_folders = self.get_selected_folders()
        except AttributeError:
            pass

        formatted_list_file = ""
        formatted_list = ""
        for folder_path in additional_folders:
            folder_name = os.path.basename(folder_path)
            formatted_list += f'--add-data "{folder_path}";{folder_name} '
        formatted_list = formatted_list.strip()  # Remove leading/trailing whitespace

        if formatted_list != "":
            formatted_list = formatted_list.strip()
            print(formatted_list)
        else:
            formatted_list = ""

        try:
            install_cmd = "pyinstaller --noconfirm --" + window_status + "--" + file_status + " " + self.py_file
            print(install_cmd)
        except Exception:
            print("oops broski")
