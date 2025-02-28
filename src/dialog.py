from PySide6.QtWidgets import QDialog, QMessageBox

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        QMessageBox.about(
            self,
            "About Sound Source",
            "Sound Source\nVersion 1.0\nA project by [Your Name]\nBuilt with PySide6"
        )