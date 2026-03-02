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

from src.ui.main_window import MainWindow


def main():
    # Habilitar DPI alto para pantallas 4K / retina
    app = QApplication(sys.argv)
    app.setApplicationName("QA Step Recorder")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("QA Tools")

    # Ícono de la aplicación (si existe)
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
