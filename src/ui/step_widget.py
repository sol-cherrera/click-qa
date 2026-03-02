"""
src/ui/step_widget.py — Tarjeta de paso para Click (capturas con acciones).
"""
import io
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QDialog, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QImage


class ImageViewerDialog(QDialog):
    def __init__(self, screenshot_bytes, step_number, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Paso {step_number} — Captura completa")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        self.resize(1280, 820)
        self.setStyleSheet("background:#050d0e;")

        from PyQt6.QtWidgets import QScrollArea, QVBoxLayout
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none; background:#050d0e;")
        img_lbl = QLabel()
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_lbl.setStyleSheet("background:#050d0e;")
        pm = _bytes_to_pixmap(screenshot_bytes)
        if pm:
            scaled = pm.scaled(QSize(1240, 780), Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
            img_lbl.setPixmap(scaled)
        scroll.setWidget(img_lbl)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)


class ClickableIcon(QLabel):
    clicked = pyqtSignal()
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class StepWidget(QWidget):
    """Tarjeta de paso: cabecera, botones de acción y miniatura."""

    def __init__(self, step: dict, parent=None):
        super().__init__(parent)
        self.step = step
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("stepCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(8)

        # ── Cabecera ─────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(10)

        is_note = self.step.get("is_note", False)
        color   = "#0f766e" if is_note else "#00B5C8"

        num_lbl = QLabel(str(self.step["number"]))
        num_lbl.setFixedSize(34, 34)
        num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num_lbl.setStyleSheet(
            f"background:{color}; border-radius:17px; color:white;"
            f"font-size:13px; font-weight:700;"
        )

        badge = QLabel(self.step.get("action", "Acción"))
        badge.setStyleSheet(
            "background:rgba(0,181,200,0.1); border:1px solid rgba(0,181,200,0.25);"
            "border-radius:10px; color:#00B5C8; font-size:11px;"
            "font-weight:600; padding:2px 10px;"
        )

        hdr.addWidget(num_lbl)
        hdr.addWidget(badge)
        hdr.addStretch()
        layout.addLayout(hdr)

        # ── Screenshot ───────────────────────────────────────────
        if self.step.get("screenshot_bytes"):
            # Fila de acciones: Editar highlight y Ver completo
            btn_row = QHBoxLayout()
            btn_row.setSpacing(10)
            btn_row.addStretch()

            btn_hl = QPushButton("✏  Editar highlight")
            btn_hl.setToolTip("Editar el área resaltada en la captura")
            btn_hl.setStyleSheet(
                "background:rgba(0,181,200,0.1); border:1px solid rgba(0,181,200,0.25);"
                "border-radius:6px; color:#00B5C8; font-size:11px; font-weight:600;"
                "padding:5px 12px;"
            )
            btn_hl.clicked.connect(self._edit_highlight)

            btn_view = QPushButton("⛶  Ver completo")
            btn_view.setToolTip("Ver la captura a tamaño completo")
            btn_view.setStyleSheet(
                "background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.12);"
                "border-radius:6px; color:#5a8a90; font-size:11px; font-weight:500;"
                "padding:5px 12px;"
            )
            btn_view.clicked.connect(self._view_fullscreen)

            btn_row.addWidget(btn_hl)
            btn_row.addWidget(btn_view)
            layout.addLayout(btn_row)

            self.img_lbl = QLabel()
            self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.img_lbl.setStyleSheet(
                "border:1px solid rgba(0,181,200,0.1); border-radius:8px; background:#070f10;"
            )
            self.img_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            self.img_lbl.mousePressEvent = lambda _: self._view_fullscreen()
            self._refresh_thumbnail()
            layout.addWidget(self.img_lbl)

    def _refresh_thumbnail(self):
        pm = _bytes_to_pixmap(self.step.get("screenshot_bytes", b""))
        if pm:
            scaled = pm.scaledToWidth(700, Qt.TransformationMode.SmoothTransformation)
            if scaled.height() > 360:
                scaled = pm.scaledToHeight(360, Qt.TransformationMode.SmoothTransformation)
            self.img_lbl.setPixmap(scaled)

    def _view_fullscreen(self):
        dlg = ImageViewerDialog(self.step["screenshot_bytes"], self.step["number"], self)
        dlg.exec()

    def _edit_highlight(self):
        from src.ui.highlight_editor import HighlightEditorDialog
        dlg = HighlightEditorDialog(self.step, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._refresh_thumbnail()


def _bytes_to_pixmap(data: bytes) -> QPixmap | None:
    if not data:
        return None
    try:
        qimg = QImage()
        qimg.loadFromData(data)
        return None if qimg.isNull() else QPixmap.fromImage(qimg)
    except Exception:
        return None
