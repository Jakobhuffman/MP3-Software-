import sys
from PySide6.QtWidgets import QApplication
from src.main_ui import SoundSourceWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SoundSourceWindow()
    window.show()
    sys.exit(app.exec())