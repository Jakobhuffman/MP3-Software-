from PySide6.QtWidgets import QMainWindow, QFileDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from src.dialog import AboutDialog
import os
import resources.img_rc

class SoundSourceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file using QUiLoader
        ui_path = os.path.join(os.path.dirname(__file__), "../ui/main_window.ui")
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.ReadOnly):
            raise Exception(f"Cannot open {ui_path}: {ui_file.errorString()}")
        loader = QUiLoader()
        self.window = loader.load(ui_file, self)  # Store the loaded window
        ui_file.close()

        # Set central widget and reassign menu/status bars
        self.setCentralWidget(self.window.centralwidget)
        self.setMenuBar(self.window.menubar)  # Use setMenuBar for proper integration
        self.setStatusBar(self.window.statusbar)  # Use setStatusBar

        # Connect menu actions from the loaded window
        self.window.actionadd_song.triggered.connect(self.add_song)
        self.window.actionremove.triggered.connect(self.remove_song)
        self.window.actionAdd_Playlist.triggered.connect(self.add_playlist)
        self.window.action_About.triggered.connect(self.show_about)

    def add_song(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Add Song", "", "Audio Files (*.mp3 *.wav *.flac)"
        )
        if file_path:
            self.statusBar().showMessage(f"Selected song: {file_path}", 5000)

    def remove_song(self):
        self.statusBar().showMessage("Remove Song clicked - add song list first!", 5000)

    def add_playlist(self):
        self.statusBar().showMessage("Add Playlist clicked - implement me!", 5000)

    def show_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()