from PySide6.QtWidgets import QMainWindow, QFileDialog
from PySide6.QtUiTools import loadUi
from src.dialog import AboutDialog
import os

# Import compiled resources
import resources.img_rc

class SoundSourceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file from ui/
        ui_path = os.path.join(os.path.dirname(__file__), "../ui/intro.ui")
        loadUi(ui_path, self)

        # Connect menu actions
        self.actionadd_song.triggered.connect(self.add_song)
        self.actionremove.triggered.connect(self.remove_song)
        self.actionAdd_Playlist.triggered.connect(self.add_playlist)
        self.action_About.triggered.connect(self.show_about)

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