import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt6.uic import loadUi

# If you’ve compiled img.qrc, uncomment this line after running: pyrcc6 img.qrc -o img_rc.py
#import img_rc

class SoundSourceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
       
        loadUi("main_window.ui", self) #load ui 

        # Connect menu actions to methods
        self.actionadd_song.triggered.connect(self.add_song)
        self.actionremove.triggered.connect(self.remove_song)
        self.actionAdd_Playlist.triggered.connect(self.add_playlist)
        self.action_About.triggered.connect(self.show_about)

    def add_song(self):
        # Open a file dialog to select audio files
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Add Song", "", "Audio Files (*.mp3 *.wav *.flac)"
        )
        if file_path:
            self.statusBar().showMessage(f"Selected song: {file_path}", 5000)
            # TODO: Add logic to store or play the song

    def remove_song(self):
        # Placeholder for removing a song (needs a list or UI to select from)
        self.statusBar().showMessage("Remove Song clicked - add song list first!", 5000)
        # TODO: Implement song removal logic later

    def add_playlist(self):
        # Placeholder for playlist creation
        self.statusBar().showMessage("Add Playlist clicked - implement me!", 5000)
        # TODO: Add playlist creation logic

    def show_about(self):
        # Show a simple About dialog
        QMessageBox.about(
            self,
            "About Sound Source",
            "Sound Source\nVersion 1.0\nA project by [Your Name]\nBuilt with PyQt6"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoundSourceWindow()
    window.show()
    sys.exit(app.exec())