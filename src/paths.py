"""Rutas de recursos del proyecto."""
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFICIAL_LOGO = os.path.normpath(
    os.path.join(PROJECT_ROOT, "assets", "solutoria-logo-wfondo.png")
)
LEGACY_ICON = os.path.normpath(os.path.join(PROJECT_ROOT, "assets", "icon128.png"))


def logo_path() -> str:
    """Logo principal; si no existe, icono legado."""
    if os.path.isfile(OFFICIAL_LOGO):
        return OFFICIAL_LOGO
    return LEGACY_ICON
