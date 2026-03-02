"""
src/ui/region_selector.py — Overlay tipo Snipping Tool para elegir area de captura.

Dibuja un overlay semitransparente sobre todos los monitores.
El usuario arrastra para seleccionar un rectangulo.
Emite region_selected(x, y, w, h) en coordenadas globales de pantalla.
"""
from PyQt6.QtWidgets import QWidget, QApplication, QLabel
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QCursor


class RegionSelector(QWidget):
    """
    Ventana transparente de pantalla completa.
    El usuario clicka y arrastra para definir el area de grabacion.
    """
    region_selected = pyqtSignal(int, int, int, int)   # x, y, w, h en coords globales
    cancelled       = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Sin borde, encima de todo, fondo transparente
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        # Cubrir TODOS los monitores
        combined = QRect()
        for screen in QApplication.screens():
            combined = combined.united(screen.geometry())
        self.setGeometry(combined)
        self._offset = combined.topLeft()   # offset para convertir widget→global

        self._start: QPoint | None = None
        self._current: QPoint | None = None
        self._dragging = False

    def showEvent(self, event):
        self.showFullScreen()
        super().showEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Overlay oscuro sobre toda la pantalla
        painter.fillRect(self.rect(), QColor(0, 0, 0, 130))

        if self._start and self._current:
            sel = QRect(self._start, self._current).normalized()

            # Recortar el overlay para que la seleccion quede "limpia"
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(sel, QColor(0, 0, 0, 255))
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            # Borde de la seleccion
            pen = QPen(QColor(124, 58, 237), 2)
            painter.setPen(pen)
            painter.drawRect(sel)

            # Esquinas resaltadas
            corner_size = 8
            painter.fillRect(sel.left(),              sel.top(),               corner_size, corner_size, QColor(167, 139, 250))
            painter.fillRect(sel.right()-corner_size, sel.top(),               corner_size, corner_size, QColor(167, 139, 250))
            painter.fillRect(sel.left(),              sel.bottom()-corner_size, corner_size, corner_size, QColor(167, 139, 250))
            painter.fillRect(sel.right()-corner_size, sel.bottom()-corner_size, corner_size, corner_size, QColor(167, 139, 250))

            # Dimension
            w = sel.width()
            h = sel.height()
            dim_text = f"{w} × {h} px"
            painter.setPen(QColor(232, 232, 240))
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            painter.drawText(sel.left() + 6, sel.top() - 8, dim_text)

        # Instrucciones (solo sin seleccion activa)
        if not self._dragging:
            painter.setPen(QColor(220, 220, 240))
            painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            cx = self.rect().center().x()
            cy = self.rect().center().y()
            painter.drawText(cx - 200, cy - 20, 400, 30,
                             Qt.AlignmentFlag.AlignCenter,
                             "Arrastra para seleccionar el area de captura")
            painter.setFont(QFont("Segoe UI", 10))
            painter.setPen(QColor(136, 136, 153))
            painter.drawText(cx - 200, cy + 18, 400, 22,
                             Qt.AlignmentFlag.AlignCenter,
                             "Esc para cancelar")

    # ─── Mouse events ──────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start    = event.pos()
            self._current  = event.pos()
            self._dragging = True
            self.update()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._current = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            sel = QRect(self._start, event.pos()).normalized()

            if sel.width() > 20 and sel.height() > 20:
                # Convertir a coordenadas globales de pantalla
                global_x = sel.x() + self._offset.x()
                global_y = sel.y() + self._offset.y()
                self.region_selected.emit(global_x, global_y, sel.width(), sel.height())
            else:
                self.cancelled.emit()
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            self.close()
