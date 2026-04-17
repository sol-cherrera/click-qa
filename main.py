"""
main.py — QA Step Recorder Desktop
Punto de entrada de la aplicación.
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.paths import app_icon_path
from src.ui.main_window import MainWindow


def main():
    # Habilitar DPI alto para pantallas 4K / retina
    app = QApplication(sys.argv)
    app.setApplicationName("QA Step Recorder")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("QA Tools")

    ip = app_icon_path()
    if os.path.isfile(ip):
        app.setWindowIcon(QIcon(ip))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
