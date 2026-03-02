"""
src/ui/highlight_editor.py v2 — Editor con selector de color.
"""
import io
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QCheckBox, QScrollArea, QWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QColor

from src.recorder import draw_highlight
from PIL import Image


# Colores disponibles: (nombre, RGBA tuple, hex para CSS)
COLORS = [
    ("Rojo",      (255,  17,  17, 255), "#FF1111"),
    ("Naranja",   (255, 140,   0, 255), "#FF8C00"),
    ("Amarillo",  (255, 220,   0, 255), "#FFDC00"),
    ("Verde",     (  0, 200,  60, 255), "#00C83C"),
    ("Cian",      (  0, 181, 200, 255), "#00B5C8"),
    ("Azul",      (  0, 100, 255, 255), "#0064FF"),
    ("Morado",    (150,  50, 255, 255), "#9632FF"),
    ("Blanco",    (255, 255, 255, 255), "#FFFFFF"),
]


class ClickableImageLabel(QLabel):
    clicked_pos = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setToolTip("Haz click aqui para reposicionar el highlight")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pm = self.pixmap()
            if pm and not pm.isNull():
                lw, lh = self.width(), self.height()
                iw, ih = pm.width(), pm.height()
                ox = (lw - iw) / 2
                oy = (lh - ih) / 2
                px = event.position().x() - ox
                py = event.position().y() - oy
                if 0 <= px <= iw and 0 <= py <= ih:
                    self.clicked_pos.emit(px / iw, py / ih)


class HighlightEditorDialog(QDialog):
    def __init__(self, step: dict, parent=None):
        super().__init__(parent)
        self.step = step
        self._raw_bytes  = step.get("screenshot_raw_bytes", step.get("screenshot_bytes"))
        self._rel_x: float = step.get("click_pos_rel", (0, 0))[0]
        self._rel_y: float = step.get("click_pos_rel", (0, 0))[1]
        self._hl_enabled: bool = step.get("highlight_enabled", True)
        # Color actual: leer del step o usar rojo por defecto
        self._color: tuple = step.get("highlight_color", (255, 17, 17, 255))

        self.setWindowTitle(f"Editar highlight — Paso {step['number']}")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        self.resize(920, 680)
        self.setStyleSheet("""
            QDialog    { background:#0a1c1f; color:#e4f4f6; }
            QLabel     { background:transparent; color:#e4f4f6; font-size:13px; }
            QCheckBox  { color:#e4f4f6; font-size:13px; }
            QPushButton {
                background:rgba(0,181,200,0.1); border:1px solid rgba(0,181,200,0.25);
                border-radius:7px; color:#00B5C8; font-size:12px;
                font-weight:600; padding:7px 16px;
            }
            QPushButton:hover { background:rgba(0,181,200,0.2); }
            QPushButton#btnSave {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #008FA0,stop:1 #00B5C8);
                border:none; color:white;
            }
            QPushButton#btnSave:hover {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #007A8A,stop:1 #008FA0);
            }
        """)
        self._build_ui()
        self._refresh_preview()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        hint = QLabel("Click en la imagen para mover el highlight   |   Elige color   |   \"Sin highlight\" para eliminar el marcador")
        hint.setStyleSheet("color:#3d7a84; font-size:11px; background:transparent;")
        root.addWidget(hint)

        # ── Imagen ────────────────────────────────────────────────
        self.img_label = ClickableImageLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.img_label.setStyleSheet(
            "background:#07101180; border:1px solid rgba(0,181,200,0.1); border-radius:8px;"
        )
        self.img_label.clicked_pos.connect(self._on_image_clicked)

        scroll = QScrollArea()
        scroll.setWidget(self.img_label)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none; background:#071011;")
        root.addWidget(scroll)

        # ── Fila inferior ─────────────────────────────────────────
        bottom = QVBoxLayout()
        bottom.setSpacing(8)

        # Selector de color
        color_row = QHBoxLayout()
        color_row.setSpacing(6)
        color_lbl = QLabel("Color:")
        color_lbl.setStyleSheet("font-size:11px; font-weight:600; color:#e4f4f6; background:transparent;")
        color_row.addWidget(color_lbl)

        self._color_btns = []
        for name, rgba, hex_color in COLORS:
            btn = QPushButton()
            btn.setFixedSize(28, 28)
            btn.setToolTip(name)
            is_selected = (rgba == self._color)
            border = "3px solid white" if is_selected else "2px solid rgba(255,255,255,0.15)"
            btn.setStyleSheet(
                f"background:{hex_color}; border-radius:14px; border:{border};"
            )
            btn.clicked.connect(lambda _, r=rgba, h=hex_color: self._select_color(r, h))
            self._color_btns.append((btn, rgba, hex_color))
            color_row.addWidget(btn)

        color_row.addStretch()

        self.chk_no_hl = QCheckBox("Sin highlight")
        self.chk_no_hl.setChecked(not self._hl_enabled)
        self.chk_no_hl.toggled.connect(self._on_toggle)
        color_row.addWidget(self.chk_no_hl)

        bottom.addLayout(color_row)

        # Botones OK / Cancelar
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Guardar cambios")
        btn_save.setObjectName("btnSave")
        btn_save.clicked.connect(self._save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        bottom.addLayout(btn_row)

        root.addLayout(bottom)

    # ─── Interaccion ───────────────────────────────────────────────
    def _select_color(self, rgba: tuple, hex_color: str):
        self._color = rgba
        # Actualizar borde de botones
        for btn, btn_rgba, btn_hex in self._color_btns:
            is_sel = (btn_rgba == rgba)
            border = "3px solid white" if is_sel else "2px solid rgba(255,255,255,0.15)"
            btn.setStyleSheet(f"background:{btn_hex}; border-radius:14px; border:{border};")
        self._refresh_preview()

    def _on_image_clicked(self, fx: float, fy: float):
        if self.chk_no_hl.isChecked():
            return
        raw = self._load_raw()
        if raw:
            self._rel_x = fx * raw.width
            self._rel_y = fy * raw.height
        self._refresh_preview()

    def _on_toggle(self, no_hl: bool):
        self._hl_enabled = not no_hl
        self._refresh_preview()

    def _refresh_preview(self):
        raw = self._load_raw()
        if not raw:
            return
        preview = draw_highlight(raw, int(self._rel_x), int(self._rel_y), color=self._color) \
                  if self._hl_enabled else raw

        buf = io.BytesIO()
        preview.save(buf, format="PNG")
        qimg = QImage()
        qimg.loadFromData(buf.getvalue())
        pm = QPixmap.fromImage(qimg)
        scaled = pm.scaledToWidth(min(880, pm.width()), Qt.TransformationMode.SmoothTransformation)
        self.img_label.setPixmap(scaled)
        self.img_label.setMinimumSize(scaled.size())

    def _load_raw(self) -> Image.Image | None:
        try:
            return Image.open(io.BytesIO(self._raw_bytes))
        except Exception:
            return None

    def _save(self):
        raw = self._load_raw()
        if raw:
            result = draw_highlight(raw, int(self._rel_x), int(self._rel_y), color=self._color) \
                     if self._hl_enabled else raw
            buf = io.BytesIO()
            result.save(buf, format="PNG", optimize=True)
            self.step["screenshot_bytes"]  = buf.getvalue()
            self.step["click_pos_rel"]     = (self._rel_x, self._rel_y)
            self.step["highlight_enabled"] = self._hl_enabled
            self.step["highlight_color"]   = self._color
        self.accept()
