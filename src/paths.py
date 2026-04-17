"""Rutas de recursos del proyecto."""
import os
import sys


def _project_root() -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


PROJECT_ROOT = _project_root()
OFFICIAL_LOGO = os.path.normpath(
    os.path.join(PROJECT_ROOT, "assets", "solutoria-logo-wfondo.png")
)
LEGACY_ICON = os.path.normpath(os.path.join(PROJECT_ROOT, "assets", "icon128.png"))
APP_ICON_ICO = os.path.normpath(os.path.join(PROJECT_ROOT, "assets", "clickqa.ico"))


def app_icon_path() -> str:
    """Ícono de aplicación y barra de tareas (mismo .ico que PyInstaller embebe en el .exe)."""
    if os.path.isfile(APP_ICON_ICO):
        return APP_ICON_ICO
    if os.path.isfile(OFFICIAL_LOGO):
        return OFFICIAL_LOGO
    return LEGACY_ICON


def logo_path() -> str:
    """Logo principal; si no existe, icono legado."""
    if os.path.isfile(OFFICIAL_LOGO):
        return OFFICIAL_LOGO
    return LEGACY_ICON
