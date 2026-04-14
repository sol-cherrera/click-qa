"""
src/ui/dashboard_window.py — Dashboard de Click.
"""
from functools import partial

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame,
    QFileDialog, QMessageBox, QDialog,
    QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal, QObject, QSize
from PyQt6.QtGui import QPixmap, QIcon
import os

from src.step_manager import StepManager
from src.paths import logo_path
from src.ui.step_widget import StepWidget
from src.ui.styles import DARK_STYLE


# ─── Worker de exportacion ─────────────────────────────────────────
class ExportWorker(QObject):
    finished = pyqtSignal(bool, str)

    def __init__(self, fn, steps, filepath):
        super().__init__()
        self._fn       = fn
        self._steps    = steps
        self._filepath = filepath

    def run(self):
        try:
            self._fn(self._steps, self._filepath)
            self.finished.emit(True, self._filepath)
        except Exception as e:
            self.finished.emit(False, str(e))


# ─── Dialogo Exportar a Excel ──────────────────────────────────────
class ExcelExportDialog(QDialog):
    """Dialogo para seleccionar un .xlsx existente e insertar las capturas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_path = None
        self.setWindowTitle("Exportar a Excel")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        self.sheet_name = ""
        self.setFixedSize(520, 268)
        self.setStyleSheet("""
            QDialog    { background:#0a1c1f; color:#e4f4f6; font-family:"Segoe UI Variable Display","Segoe UI",sans-serif; }
            QLabel     { background:transparent; color:#e4f4f6; }
            QLineEdit  { background:rgba(0,181,200,0.05); border:1px solid rgba(0,181,200,0.2);
                         border-radius:7px; padding:6px 10px; color:#e4f4f6; font-size:12px; }
            QLineEdit:focus { border-color:#00B5C8; }
            QPushButton {
                background:rgba(0,181,200,0.08); border:1px solid rgba(0,181,200,0.2);
                border-radius:8px; color:#00B5C8; font-size:12px;
                font-weight:600; padding:8px 16px;
            }
            QPushButton:hover { background:rgba(0,181,200,0.16); }
            QPushButton#btnConfirm {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #008FA0,stop:1 #00B5C8);
                border:none; color:white; font-size:13px; font-weight:700;
                padding:10px 24px;
            }
            QPushButton#btnConfirm:hover {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #007A8A,stop:1 #008FA0);
            }
        """)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        title = QLabel("Exportar capturas a Excel")
        title.setStyleSheet("font-size:16px; font-weight:700; color:#00D4E8;")
        root.addWidget(title)

        hint = QLabel("Selecciona un archivo .xlsx existente. Se añadirá una hoja nueva con todas las capturas.")
        hint.setStyleSheet("font-size:11px; color:#3d7a84;")
        hint.setWordWrap(True)
        root.addWidget(hint)

        from src.exporters.excel_exporter import suggested_export_sheet_title
        sheet_lbl = QLabel("Nombre de la hoja")
        sheet_lbl.setStyleSheet("font-size:11px; font-weight:600; color:#5a8a90;")
        root.addWidget(sheet_lbl)
        self.sheet_edit = QLineEdit()
        self.sheet_edit.setText(suggested_export_sheet_title())
        self.sheet_edit.setPlaceholderText("Ej. Prueba login — vacío = automático")
        root.addWidget(self.sheet_edit)

        # Fila de ruta
        row = QHBoxLayout()
        row.setSpacing(8)
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Ruta del archivo Excel (.xlsx)...")
        self.path_edit.setReadOnly(True)
        btn_browse = QPushButton("Examinar...")
        btn_browse.setFixedWidth(100)
        btn_browse.clicked.connect(self._browse)
        row.addWidget(self.path_edit)
        row.addWidget(btn_browse)
        root.addLayout(row)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_confirm = QPushButton("Insertar →")
        btn_confirm.setObjectName("btnConfirm")
        btn_confirm.clicked.connect(self._confirm)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_confirm)
        root.addLayout(btn_row)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo Excel",
            "", "Excel Files (*.xlsx *.xlsm)"
        )
        if path:
            self.selected_path = path
            self.path_edit.setText(path)

    def _confirm(self):
        if not self.selected_path:
            QMessageBox.warning(self, "Sin archivo", "Por favor selecciona un archivo Excel primero.")
            return
        self.sheet_name = (self.sheet_edit.text() or "").strip()
        self.accept()


# ─── Ventana Dashboard ─────────────────────────────────────────────
class DashboardWindow(QMainWindow):
    def __init__(self, step_manager: StepManager, recorder,
                 main_window=None, parent=None):
        super().__init__(parent)
        self.step_manager   = step_manager
        self.recorder       = recorder
        self._main_window   = main_window   # referencia para navegacion inversa
        self._export_thread = None
        self._worker        = None

        self.setWindowTitle("Click — Dashboard")
        self.resize(960, 740)
        self.setMinimumSize(720, 520)

        lp = logo_path()
        if os.path.isfile(lp):
            self.setWindowIcon(QIcon(lp))

        self._build_ui()
        self.setStyleSheet(DARK_STYLE)

    # ─── Build UI ──────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────
        hdr_w = QWidget()
        hdr_w.setObjectName("headerBar")
        hdr_w.setFixedHeight(66)
        hdr = QHBoxLayout(hdr_w)
        hdr.setContentsMargins(28, 0, 24, 0)
        hdr.setSpacing(14)

        # Logo
        logo_lbl = QLabel()
        lp = logo_path()
        if os.path.isfile(lp):
            pm = QPixmap(lp).scaled(
                QSize(120, 40),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_lbl.setPixmap(pm)
        else:
            logo_lbl.setText("C")
            logo_lbl.setStyleSheet("font-size:18px; font-weight:700; color:#00B5C8;")
        logo_lbl.setFixedHeight(40)
        logo_lbl.setMinimumWidth(120)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title_lbl = QLabel("Click")
        title_lbl.setStyleSheet(
            "font-family:'Segoe UI Variable Display','Segoe UI',sans-serif;"
            "font-size:18px; font-weight:700; color:#00D4E8; background:transparent;"
        )
        self.lbl_sub = QLabel("0 capturas")
        self.lbl_sub.setStyleSheet(
            "font-size:11px; color:#2a5a62; background:transparent;"
        )
        title_col.addWidget(title_lbl)
        title_col.addWidget(self.lbl_sub)

        hdr.addWidget(logo_lbl)
        hdr.addLayout(title_col)
        hdr.addStretch()

        # Boton volver al panel
        if self._main_window is not None:
            btn_panel = QPushButton("← Panel")
            btn_panel.setStyleSheet(
                "background:transparent; border:1px solid rgba(0,181,200,0.2);"
                "border-radius:8px; color:#3d7a84; font-size:12px; font-weight:600;"
                "padding:9px 14px;"
            )
            btn_panel.clicked.connect(self._go_to_panel)
            hdr.addWidget(btn_panel)

        # Separador
        vsep = QFrame()
        vsep.setFrameShape(QFrame.Shape.VLine)
        vsep.setStyleSheet("color:rgba(0,181,200,0.1);")
        hdr.addWidget(vsep)

        # Boton Excel — solido
        self.btn_excel = QPushButton("✔  Exportar a Excel")
        self.btn_excel.setStyleSheet(
            "background:#1d8a3e; border:none; color:white; font-size:12px; font-weight:700;"
            "border-radius:8px; padding:9px 18px;"
        )
        self.btn_excel.clicked.connect(self._export_excel_dialog)

        hdr.addWidget(self.btn_excel)
        root.addWidget(hdr_w)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:rgba(0,181,200,0.07);")
        root.addWidget(sep)

        # ── Area de pasos ─────────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("border:none;")

        self._steps_container = QWidget()
        self._steps_container.setStyleSheet("background:transparent;")
        self._steps_layout = QVBoxLayout(self._steps_container)
        self._steps_layout.setContentsMargins(32, 28, 32, 48)
        self._steps_layout.setSpacing(14)
        self._steps_layout.addStretch()

        self._scroll.setWidget(self._steps_container)
        root.addWidget(self._scroll)

    # ─── Render ────────────────────────────────────────────────────
    def refresh(self):
        # Limpiar existentes (excepto stretch final)
        while self._steps_layout.count() > 1:
            item = self._steps_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        steps = self.step_manager.steps
        count = len(steps)
        self.lbl_sub.setText(
            f"{count} captura{'s' if count != 1 else ''} grabada{'s' if count != 1 else ''}"
        )
        self._set_export_enabled(count > 0)

        if count == 0:
            self._steps_layout.insertWidget(0, self._make_empty_widget())
            return

        for step in steps:
            widget = StepWidget(step)
            widget.delete_requested.connect(self._on_delete_step)
            self._steps_layout.insertWidget(self._steps_layout.count() - 1, widget)

    def _make_empty_widget(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl = QLabel(
            "Sin capturas aún\n\n"
            "Inicia una grabación desde el panel de Click\n"
            "e interactúa con cualquier ventana."
        )
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(
            "color:#1e4a52; font-size:14px; font-family:'Segoe UI Variable Display','Segoe UI',sans-serif;"
        )
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
        return w

    def _set_export_enabled(self, enabled: bool):
        self.btn_excel.setEnabled(enabled)

    @pyqtSlot(int)
    def _on_delete_step(self, step_id: int):
        r = QMessageBox.question(
            self,
            "Eliminar captura",
            "¿Eliminar este paso de la sesión? No se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if r != QMessageBox.StandardButton.Yes:
            return
        self.step_manager.remove_step(step_id)
        self.recorder.set_step_count(self.step_manager.count)
        self.refresh()

    @pyqtSlot()
    def _go_to_panel(self):
        if self._main_window:
            self.hide()  # Ocultamos el dashboard
            self._main_window.showNormal()
            self._main_window.raise_()
            self._main_window.activateWindow()

    # ─── Export: Excel dialog ─────────────────────────────────────
    def _export_excel_dialog(self):
        if not self.step_manager.steps:
            return
        dlg = ExcelExportDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_path:
            from src.exporters.excel_exporter import export_excel
            title = dlg.sheet_name or None
            export_fn = partial(export_excel, sheet_name=title)
            self._run_export(export_fn, dlg.selected_path, "excel")

    # ─── Export: PDF / DOCX ───────────────────────────────────────
    def _export_pdf(self):
        if not self.step_manager.steps:
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", "plan-de-prueba.pdf", "PDF Files (*.pdf)"
        )
        if filepath:
            from src.exporters.pdf_exporter import export_pdf
            self._run_export(export_pdf, filepath, "pdf")

    def _export_docx(self):
        if not self.step_manager.steps:
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Guardar DOCX", "plan-de-prueba.docx", "Word Documents (*.docx)"
        )
        if filepath:
            from src.exporters.docx_exporter import export_docx
            self._run_export(export_docx, filepath, "docx")

    def _run_export(self, fn, filepath: str, fmt: str):
        self._set_export_enabled(False)
        self.btn_excel.setText("Exportando...")
        steps_copy = list(self.step_manager.steps)
        self._export_thread = QThread()
        self._worker = ExportWorker(fn, steps_copy, filepath)
        self._worker.moveToThread(self._export_thread)
        self._export_thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_export_done)
        self._worker.finished.connect(self._export_thread.quit)
        self._export_thread.start()

    @pyqtSlot(bool, str)
    def _on_export_done(self, success: bool, msg: str):
        self.btn_excel.setText("✔  Exportar a Excel")
        self._set_export_enabled(self.step_manager.count > 0)
        if success:
            QMessageBox.information(self, "Listo", f"Archivo guardado:\n{msg}")
        else:
            QMessageBox.critical(self, "Error", f"No se pudo exportar:\n{msg}")
