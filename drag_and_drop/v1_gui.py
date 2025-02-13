import sys
from PyQt6.QtWidgets import QApplication, QWidget

app = QApplication(sys.argv)  # Fix: Correct spelling of QApplication

window = QWidget()  # Fix: Instantiate QWidget properly

window.show()

sys.exit(app.exec())
