import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer

class VeroraOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Frameless, always-on-top, transparent background
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setGeometry(50, 50, 320, 160)
        self.setStyleSheet("background-color: rgba(20, 20, 30, 180); border-radius: 12px;")

        layout = QVBoxLayout()

        self.file_label = QLabel("Watching: train.py")
        self.log_label = QLabel("Last accuracy: 0.61")
        self.status_label = QLabel("Status: idle")

        for label in (self.file_label, self.log_label, self.status_label):
            label.setStyleSheet("color: white; font-size: 13px; padding: 4px;")

        layout.addWidget(self.file_label)
        layout.addWidget(self.log_label)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def update_status(self, file=None, accuracy=None, status=None):
        if file:
            self.file_label.setText(f"Watching: {file}")
        if accuracy:
            self.log_label.setText(f"Last accuracy: {accuracy}")
        if status:
            self.status_label.setText(f"Status: {status}")


def run_overlay():
    app = QApplication(sys.argv)
    overlay = VeroraOverlay()
    overlay.show()

    # Temporary test: change the label after 3 seconds
    def test_update():
        overlay.update_status(file="test_changed.py", accuracy="0.74", status="testing")

    QTimer.singleShot(3000, test_update)

    sys.exit(app.exec())


if __name__ == "__main__":
    run_overlay()