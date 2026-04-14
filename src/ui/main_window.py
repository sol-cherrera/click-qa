"""
src/ui/main_window.py — Panel de control de Click.
"""
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QIcon

from src.recorder import RecordingEngine
from src.step_manager import StepManager
from src.paths import logo_path
from src.ui.styles import DARK_STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClickQA")
        self.setFixedWidth(360)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)

        self._is_recording = False
        self._is_paused    = False
        self._dashboard    = None
        self._region_selector = None

        self.step_manager = StepManager()
        self.recorder = RecordingEngine(excluded_rects_fn=self._get_excluded_rects)
        self.recorder.step_captured.connect(self._on_step_captured)
        self.recorder.status_message.connect(self._on_status_message)
        self.step_manager.steps_changed.connect(self._refresh_counter)

        lp = logo_path()
        if os.path.isfile(lp):
            self.setWindowIcon(QIcon(lp))

        self._build_ui()
        self.setStyleSheet(DARK_STYLE)
        self._apply_panel_fixed_geometry()
        self._panel_idle_height = self.height()

    # ─── UI ────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        # ── Header con logo ───────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(10)

        logo_lbl = QLabel()
        lp = logo_path()
        if os.path.isfile(lp):
            pm = QPixmap(lp).scaled(
                QSize(108, 36),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pm)
        else:
            logo_lbl.setText("C")
            logo_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
            logo_lbl.setStyleSheet("color:#00B5C8;")
        logo_lbl.setFixedHeight(40)
        logo_lbl.setMinimumWidth(44)

        title = QLabel("ClickQA")
        title.setObjectName("appTitle")

        self.badge = QLabel("● Inactivo")
        self._style_badge("inactive")

        hdr.addWidget(logo_lbl)
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self.badge)
        root.addLayout(hdr)

        # ── Contador ─────────────────────────────────────────────
        counter_box = QWidget()
        counter_box.setObjectName("counterBox")
        cb = QVBoxLayout(counter_box)
        cb.setContentsMargins(12, 14, 12, 14)
        cb.setSpacing(4)
        self.lbl_count = QLabel("0")
        self.lbl_count.setObjectName("stepCountNum")
        self.lbl_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_count.setMinimumHeight(48)
        sub = QLabel("pasos capturados")
        sub.setObjectName("stepCountSub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cb.addWidget(self.lbl_count)
        cb.addWidget(sub)
        root.addWidget(counter_box)

        # ── Boton Start/Stop ─────────────────────────────────────
        self.btn_record = QPushButton("▶   Iniciar Grabacion")
        self.btn_record.setObjectName("btnRecord")
        self.btn_record.setMinimumHeight(46)
        self.btn_record.clicked.connect(self._toggle_recording)
        root.addWidget(self.btn_record)

        # ── Boton Pausar (solo visible grabando) ────────────────
        self.row_pause = QWidget()
        rp = QHBoxLayout(self.row_pause)
        rp.setContentsMargins(0, 0, 0, 0)
        self.btn_pause = QPushButton("⏸  Pausar")
        self.btn_pause.setObjectName("btnPause")
        self.btn_pause.setMinimumHeight(36)
        self.btn_pause.clicked.connect(self._toggle_pause)
        rp.addWidget(self.btn_pause)
        self.row_pause.hide()
        root.addWidget(self.row_pause)

        # ── Boton Dashboard (siempre visible) ─────────────────────
        self.btn_dash = QPushButton("Dashboard  →")
        self.btn_dash.setObjectName("btnDashboard")
        self.btn_dash.setMinimumHeight(36)
        self.btn_dash.clicked.connect(self._open_dashboard)
        root.addWidget(self.btn_dash)

        # ── Separador ────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)

        # ── Region de captura (conservada, util para VPN) ────────
        region_box = QWidget()
        region_box.setStyleSheet(
            "background: rgba(0,181,200,0.06); border: 1px solid rgba(0,181,200,0.18);"
            "border-radius: 10px;"
        )
        rb = QVBoxLayout(region_box)
        rb.setContentsMargins(12, 10, 12, 10)
        rb.setSpacing(6)

        rb_title = QLabel("▣   Region de captura")
        rb_title.setStyleSheet(
            "font-size:11px; font-weight:600; color:#00B5C8; background:transparent; border:none;"
        )
        rb.addWidget(rb_title)

        self.lbl_region = QLabel("Pantalla completa")
        self.lbl_region.setStyleSheet(
            "font-size:11px; color:#3d7a84; background:transparent; border:none;"
        )
        rb.addWidget(self.lbl_region)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_select_region = QPushButton("✂  Seleccionar region")
        self.btn_select_region.setStyleSheet(
            "background: rgba(0,181,200,0.1); border:1px solid rgba(0,181,200,0.3);"
            "border-radius:7px; color:#00B5C8; font-size:11px; font-weight:600; padding:5px 10px;"
        )
        self.btn_select_region.clicked.connect(self._start_region_selection)

        self.btn_clear_region = QPushButton("✕  Pantalla completa")
        self.btn_clear_region.setStyleSheet(
            "background: transparent; border:1px solid rgba(0,181,200,0.1);"
            "border-radius:7px; color:#3d7a84; font-size:11px; padding:5px 10px;"
        )
        self.btn_clear_region.clicked.connect(self._clear_region)
        self.btn_clear_region.hide()

        btn_row.addWidget(self.btn_select_region)
        btn_row.addWidget(self.btn_clear_region)
        rb.addLayout(btn_row)
        root.addWidget(region_box)

        # ── Estado + pie (espaciado compacto entre líneas) ───────
        self.lbl_status = QLabel("Listo para grabar")
        self.lbl_status.setStyleSheet(
            "font-size:11px; color:#3d7a84; background:transparent; margin:0; padding:0;"
        )
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setWordWrap(True)

        self.lbl_shortcut = QLabel("Captura: Mayús + S")
        self.lbl_shortcut.setStyleSheet(
            "font-size:12px; color:#3d7a84; background:transparent; margin:0; padding:0;"
        )
        self.lbl_shortcut.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_love = QLabel("Con \u2665 para Solutoria")
        self.lbl_love.setStyleSheet(
            "font-size:10px; color:#2a5a62; background:transparent; margin:0; padding:0;"
        )
        self.lbl_love.setAlignment(Qt.AlignmentFlag.AlignCenter)

        foot = QWidget()
        foot_l = QVBoxLayout(foot)
        foot_l.setContentsMargins(0, 0, 0, 0)
        foot_l.setSpacing(2)
        foot_l.addWidget(self.lbl_status)
        foot_l.addWidget(self.lbl_shortcut)
        foot_l.addWidget(self.lbl_love)
        root.addWidget(foot)

    # ─── Grabacion ─────────────────────────────────────────────────
    def _toggle_recording(self):
        if not self._is_recording:
            self.step_manager.clear()
            self.recorder.start()
            self._is_recording = True
            self._is_paused    = False
            self.showMinimized()  # Minimizar a la barra de tareas (no ocultar)
        else:
            self.recorder.stop()
            self._is_recording = False
            self._is_paused    = False
            self._open_dashboard()
        self._update_ui()

    def _toggle_pause(self):
        if not self._is_paused:
            self.recorder.pause()
            self._is_paused = True
        else:
            self.recorder.resume()
            self._is_paused = False
        self._update_ui()

    # ─── Region ────────────────────────────────────────────────────
    def _start_region_selection(self):
        from src.ui.region_selector import RegionSelector
        self.showMinimized()
        import time; time.sleep(0.25)
        self._region_selector = RegionSelector()
        self._region_selector.region_selected.connect(self._on_region_selected)
        self._region_selector.cancelled.connect(self._on_region_cancelled)
        self._region_selector.show()

    @pyqtSlot(int, int, int, int)
    def _on_region_selected(self, x, y, w, h):
        self.recorder.set_region(x, y, w, h)
        self.lbl_region.setText(f"{w} × {h} px  en ({x}, {y})")
        self.lbl_region.setStyleSheet(
            "font-size:11px; color:#00B5C8; background:transparent; border:none; font-weight:600;"
        )
        self.btn_clear_region.show()
        self.showNormal(); self.raise_()

    @pyqtSlot()
    def _on_region_cancelled(self):
        self.showNormal(); self.raise_()

    def _clear_region(self):
        self.recorder.clear_region()
        self.lbl_region.setText("Pantalla completa")
        self.lbl_region.setStyleSheet(
            "font-size:11px; color:#3d7a84; background:transparent; border:none;"
        )
        self.btn_clear_region.hide()

    # ─── Dashboard ─────────────────────────────────────────────────
    def _open_dashboard(self):
        self.hide()  # Ocultamos el panel principal
        from src.ui.dashboard_window import DashboardWindow
        if self._dashboard is None or not self._dashboard.isVisible():
            self._dashboard = DashboardWindow(
                self.step_manager, self.recorder, main_window=self
            )
        self._dashboard.show()
        self._dashboard.raise_()
        self._dashboard.refresh()

    # ─── Slots ─────────────────────────────────────────────────────
    @pyqtSlot(dict)
    def _on_step_captured(self, step):
        self.step_manager.add_step(step)
        if self._dashboard and self._dashboard.isVisible():
            self._dashboard.refresh()

    @pyqtSlot(str)
    def _on_status_message(self, msg):
        self.lbl_status.setText(msg)

    @pyqtSlot()
    def _refresh_counter(self):
        self.lbl_count.setText(str(self.step_manager.count))

    # ─── Exclusion ─────────────────────────────────────────────────
    def _get_excluded_rects(self):
        rects = []
        g = self.geometry()
        rects.append(QRect(g.x(), g.y(), g.width(), g.height()))
        if self._dashboard and self._dashboard.isVisible():
            g2 = self._dashboard.geometry()
            rects.append(QRect(g2.x(), g2.y(), g2.width(), g2.height()))
        return rects

    # ─── UI updates ────────────────────────────────────────────────
    def _update_ui(self):
        if self._is_recording:
            self.btn_record.setProperty("state", "recording")
            self.row_pause.show()
            if self._is_paused:
                self.btn_record.setText("⏹   Detener y Revisar")
                self.btn_pause.setText("▶  Reanudar")
                self.btn_pause.setProperty("paused", "true")
                self._style_badge("paused")
            else:
                self.btn_record.setText("⏹   Detener y Revisar")
                self.btn_pause.setText("⏸  Pausar")
                self.btn_pause.setProperty("paused", "false")
                self._style_badge("recording")
        else:
            self.btn_record.setText("▶   Iniciar Grabacion")
            self.btn_record.setProperty("state", "")
            self.row_pause.hide()
            self._style_badge("inactive")

        for w in (self.btn_record, self.btn_pause):
            w.style().unpolish(w)
            w.style().polish(w)

        self._apply_panel_fixed_geometry(force_idle=not self._is_recording)

    def _apply_panel_fixed_geometry(self, force_idle: bool = False):
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.adjustSize()
        target_height = self.height()
        if force_idle and hasattr(self, "_panel_idle_height"):
            target_height = self._panel_idle_height
        self.setFixedSize(360, target_height)

    def _style_badge(self, state: str):
        styles = {
            "inactive":  ("● Inactivo", "background:rgba(0,181,200,0.05);border:1px solid rgba(0,181,200,0.12);border-radius:12px;padding:3px 10px;font-size:11px;color:#3d7a84;"),
            "recording": ("🔴  Grabando","background:rgba(255,50,50,0.12);border:1px solid rgba(255,50,50,0.3);border-radius:12px;padding:3px 10px;font-size:11px;color:#ff6b6b;"),
            "paused":    ("⏸  Pausado", "background:rgba(234,88,12,0.12);border:1px solid rgba(234,88,12,0.35);border-radius:12px;padding:3px 10px;font-size:11px;color:#fb923c;"),
        }
        text, style = styles.get(state, styles["inactive"])
        self.badge.setText(text)
        self.badge.setStyleSheet(style)

    def closeEvent(self, event):
        self.recorder.stop()
        if self._dashboard:
            self._dashboard.close()
        super().closeEvent(event)
