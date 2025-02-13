from PyQt6.QtWidgets import QApplication, QWidget 
from PyQt6.QtGui import QIcon
import sys

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sound Source")
        self.setGeometry(500, 500, 300, 200)



app = QApplication(sys.argv)

window = Window()
window.show()
sys.exit(app.exec())

