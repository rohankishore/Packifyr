import os
import threading
from subprocess import Popen, PIPE, CalledProcessError

from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QPushButton, QComboBox, QFileDialog, QHBoxLayout, \
    QSpacerItem, QLabel, QListView, QDialogButtonBox, QDialog, QInputDialog, QListWidget, QCheckBox
from qfluentwidgets import (TextEdit,
                            ListWidget, LineEdit)


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


class PyInstaller(QWidget):
    def __init__(self):
        super().__init__()

        spacer_item_small = QSpacerItem(0, 10)
        spacer_item_medium = QSpacerItem(0, 20)

        self.setObjectName("PyInstaller")

        self.icon_file = ""
        self.py_file = ""
        self.install_cmd = ""
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

        self.advanced_group = QGroupBox("")
        self.advanced_layout = QVBoxLayout(self.advanced_group)
        # self.options_layout.addWidget(self.advanced_group)

        self.options_layout.addSpacerItem(spacer_item_small)

        self.hidden_import_button = QPushButton("Add Hidden Imports")
        self.hidden_import_button.clicked.connect(self.hidden_imports)
        # self.advanced_layout.addWidget(self.hidden_import_button)

        self.advanced_layout.addSpacerItem(spacer_item_small)

        self.more_options_menu = DetailsWidget("Advanced Options <")
        self.advanced_layout.addWidget(self.hidden_import_button)
        self._name = LineEdit()
        self._name.setPlaceholderText("--name")
        self.advanced_layout.addWidget(self._name)

        self._clean = QCheckBox("--clean")
        self.advanced_layout.addWidget(self._clean)

        self._log_level = QComboBox()
        self._log_level.setPlaceholderText("LOG LEVEL")
        self._log_level.addItems(["TRACE", "DEBUG", "INFO", "WARN", "DEPRECATION", "ERROR", "FATAL"])
        self.advanced_layout.addWidget(self._log_level)
        self.main_layout.addWidget(self.more_options_menu)

        self.more_options_menu.add_detail_widget(self.advanced_group)

        # self.advanced_layout.addSpacerItem(spacer_item_small)

        self.cmd_layout = QVBoxLayout()

        self.output_textedit = TextEdit()
        self.cmd_layout.addWidget(self.output_textedit)

        # self.custom_process = CustomProcess(install_cmd=self.install_cmd, output_textedit=self.output_textedit)  # Create an instance of CustomProcess

        self.main_layout.addLayout(self.cmd_layout)

        self.script_layout = QHBoxLayout()
        self.script_layout.addSpacerItem(spacer_item_medium)
        self.main_layout.addLayout(self.script_layout)

        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.download_button = QPushButton("Execute")
        self.download_button.clicked.connect(self.execute)
        self.button_layout.addWidget(self.download_button)

        self.count_layout = QHBoxLayout()
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

        self.hidden_import_dialog = QDialog()
        self.hidden_import_dialog.setWindowTitle("Add Hidden Imports")
        self.hidden_import_dialog.setModal(True)

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

    def hidden_imports(self):
        layout = QVBoxLayout()
        self.hidden_import_dialog.setLayout(layout)
        self.hidden_imports_list = QListWidget()
        layout.addWidget(self.hidden_imports_list)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_import)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_import)
        button_layout.addWidget(self.remove_button)

        self.hidden_import_dialog.show()

    def add_import(self):
        import_name, ok = QInputDialog.getText(self, "Add Hidden Import", "Enter the name of the hidden import:")
        if ok and import_name:
            self.hidden_imports_list.addItem(import_name)

    def remove_import(self):
        selected_item = self.hidden_imports_list.currentItem()
        if selected_item:
            self.hidden_imports_list.takeItem(self.hidden_imports_list.row(selected_item))

    def get_hidden_imports(self):
        imports = []
        for index in range(self.hidden_imports_list.count()):
            item = self.hidden_imports_list.item(index)
            imports.append(f"--hidden-imports {item.text()}")
        return imports

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
        hidden_imports = ""
        icon_cmd = ""
        hidden_import_list = ""
        _name = self._name.text()
        _log_level = self._log_level.currentText()
        _clean = ""

        name_cmd = ""
        log_cmd = ""

        if _name == "":
            pass
        else:
            name = self._name.text()
            name_cmd = "--name " + f'"{_name}"'

        if self._clean.isChecked():
            _clean = "--clean"
        else:
            pass

        if _log_level == "" or _name == "LOG LEVEL":
            pass
        else:
            _log_level = self._log_level.currentText()
            log_cmd = "--log-level " + f'"{_log_level}"'

        try:
            hidden_imports = self.get_hidden_imports()
            hidden_import_list = ""
            for item in hidden_imports:
                hidden_import_list += item + ' '
            hidden_import_list = hidden_import_list.strip()  # to remove the trailing space
        except AttributeError:
            pass

        if hidden_imports == "":
            pass
        else:
            hidden_imports = hidden_imports

        if self.icon_file == "":
            pass
        else:
            icon_cmd = f"--icon=\"{self.icon_file}\""  # Fix icon_cmd formatting

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
        formatted_list_folder = ""
        for folder_path in additional_folders:
            folder_name = os.path.basename(folder_path)
            formatted_list_folder += f'--add-data="{folder_path};." '
        formatted_list_folder = formatted_list_folder.strip()  # Remove leading/trailing whitespace
        formatted_list_folder = formatted_list_folder + " "

        if formatted_list_folder != "":
            formatted_list_folder = formatted_list_folder.strip()
            # print(formatted_list_folder)
        else:
            formatted_list_folder = ""

        for file_path in additional_files:
            file_name = os.path.basename(file_path)
            formatted_list_file += f'--add-data="{file_path};." '
        formatted_list_file = formatted_list_file.strip()  # Remove leading/trailing whitespace
        formatted_list_file = formatted_list_file + " "

        if formatted_list_file != "":
            formatted_list_file = formatted_list_file.strip()
            # print(formatted_list_file)
        else:
            formatted_list_file = ""

        try:
            self.install_cmd = "pyinstaller --noconfirm" + " " + icon_cmd + " --" + window_status + " --" + file_status + " " + formatted_list_folder + formatted_list_file + hidden_import_list + _clean + name_cmd + log_cmd + " " + self.py_file
            print(self.install_cmd)
        except Exception:
            print("oops broski")

        try:
            self.output_textedit.clear()

            self.read_output()

        except Exception as e:
            print("Error:", e)

    def read_output(self):
        def run():
            with Popen(self.install_cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
                for line in p.stdout:
                    print(line, end='')  # process line here
                    self.output_textedit.append(line)

            if p.returncode != 0:
                raise CalledProcessError(p.returncode, p.args)

        thread = threading.Thread(target=run)
        thread.start()

    def process_finished(self):
        self.output_textedit.append("DONE")
        print("done")
