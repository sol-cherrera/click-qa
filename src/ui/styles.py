"""
src/ui/styles.py — Hoja de estilos QSS — Paleta SolutoQA (Teal)

Paleta extraida del logo (circulo teal + Sigma blanca):
  Primary:   #00B5C8  (teal principal)
  Accent:    #00D4E8  (teal claro)
  Dark:      #007A8A  (teal oscuro)
  Surface:   #0a1c1f  (fondo muy oscuro con matiz teal)
  Surface2:  #111f22  (tarjetas)
  Text:      #e4f4f6  (casi blanco con matiz frio)
"""

DARK_STYLE = """
/* ═══════════ BASE ═══════════ */
QMainWindow, QDialog, QWidget {
    background-color: #0a1c1f;
    color: #e4f4f6;
    font-family: "Segoe UI Variable Display", "Segoe UI Variable", "Segoe UI", "Arial", sans-serif;
    font-size: 13px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(0,181,200,0.18);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(0,181,200,0.35);
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical { background: transparent; }

QScrollBar:horizontal {
    background: transparent;
    height: 6px;
}
QScrollBar::handle:horizontal {
    background: rgba(0,181,200,0.18);
    border-radius: 3px;
}

/* ═══════════ LABELS ═══════════ */
QLabel {
    background: transparent;
    color: #e4f4f6;
}
QLabel#appTitle {
    font-size: 17px;
    font-weight: 700;
    color: #00D4E8;
}
QLabel#stepCountNum {
    font-size: 38px;
    font-weight: 800;
    color: #00B5C8;
}
QLabel#stepCountSub {
    font-size: 11px;
    color: #3d7a84;
    letter-spacing: 1px;
}
QLabel#dashTitle {
    font-size: 20px;
    font-weight: 800;
    color: #00D4E8;
}
QLabel#dashSub {
    font-size: 12px;
    color: #3d7a84;
}

/* ═══════════ SEPARADOR ═══════════ */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: rgba(0,181,200,0.1);
}

/* ═══════════ BUTTONS ═══════════ */
QPushButton {
    border: 1px solid rgba(0,181,200,0.15);
    border-radius: 8px;
    padding: 8px 14px;
    background-color: rgba(0,181,200,0.05);
    color: #e4f4f6;
    font-size: 12px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: rgba(0,181,200,0.12);
    border-color: rgba(0,181,200,0.3);
}
QPushButton:pressed {
    background-color: rgba(0,181,200,0.06);
}
QPushButton:disabled {
    color: #2a5a62;
    border-color: rgba(0,181,200,0.06);
}

QPushButton#btnRecord {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #008FA0, stop:1 #00B5C8);
    border: none;
    color: white;
    font-size: 13px;
    font-weight: 700;
    padding: 13px;
    border-radius: 10px;
}
QPushButton#btnRecord:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #007A8A, stop:1 #008FA0);
}
QPushButton#btnRecord[state="recording"] {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #b91c1c, stop:1 #ef4444);
}
QPushButton#btnRecord[state="recording"]:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #991b1b, stop:1 #b91c1c);
}

QPushButton#btnPause {
    border: 1px solid rgba(234,88,12,0.35);
    background: rgba(234,88,12,0.1);
    color: #fb923c;
    font-weight: 600;
}
QPushButton#btnPause:hover {
    background: rgba(234,88,12,0.18);
    border-color: rgba(234,88,12,0.55);
}
QPushButton#btnPause[paused="true"] {
    border: 1px solid rgba(0,181,200,0.4);
    background: rgba(0,181,200,0.1);
    color: #00D4E8;
}
QPushButton#btnPause[paused="true"]:hover {
    background: rgba(0,181,200,0.2);
}

QPushButton#btnDashboard {
    border: 1px solid rgba(0,181,200,0.25);
    background: rgba(0,181,200,0.07);
    color: #00B5C8;
    font-weight: 500;
}
QPushButton#btnDashboard:hover {
    background: rgba(0,181,200,0.16);
    border-color: rgba(0,181,200,0.5);
    color: #00D4E8;
}

QPushButton#btnExportPDF {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #008FA0, stop:1 #00B5C8);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    padding: 9px 18px;
}
QPushButton#btnExportPDF:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #007A8A, stop:1 #008FA0);
}
QPushButton#btnExportPDF:disabled {
    background: rgba(0,181,200,0.2);
    color: rgba(255,255,255,0.35);
}

QPushButton#btnExportDOCX {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #1d4ed8, stop:1 #3b82f6);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    padding: 9px 18px;
}
QPushButton#btnExportDOCX:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #1e40af, stop:1 #1d4ed8);
}
QPushButton#btnExportDOCX:disabled {
    background: rgba(29,78,216,0.25);
    color: rgba(255,255,255,0.35);
}

QPushButton#btnAddNote {
    border: 1px solid rgba(0,181,200,0.15);
    background: rgba(0,181,200,0.04);
    color: #4d9ba8;
    font-weight: 500;
    border-radius: 8px;
    padding: 9px 16px;
}
QPushButton#btnAddNote:hover {
    background: rgba(0,181,200,0.1);
    color: #e4f4f6;
}

QPushButton#btnDelete {
    border: 1px solid rgba(239,68,68,0.2);
    background: rgba(239,68,68,0.06);
    color: #ef4444;
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
}
QPushButton#btnDelete:hover {
    background: rgba(239,68,68,0.15);
    border-color: rgba(239,68,68,0.4);
}

QPushButton#btnMove {
    border: 1px solid rgba(0,181,200,0.1);
    background: transparent;
    color: #3d7a84;
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 12px;
}
QPushButton#btnMove:hover {
    background: rgba(0,181,200,0.1);
    border-color: rgba(0,181,200,0.3);
    color: #00D4E8;
}

/* ═══════════ CUADROS ═══════════ */
QWidget#counterBox {
    background: rgba(0,181,200,0.07);
    border: 1px solid rgba(0,181,200,0.18);
    border-radius: 12px;
}

QWidget#stepCard {
    background: #111f22;
    border: 1px solid rgba(0,181,200,0.08);
    border-radius: 12px;
}
QWidget#stepCard:hover {
    border-color: rgba(0,181,200,0.25);
}

QWidget#headerBar {
    background: rgba(8,20,22,0.95);
    border-bottom: 1px solid rgba(0,181,200,0.1);
}

/* ═══════════ TEXT EDIT ═══════════ */
QTextEdit, QLineEdit {
    background: rgba(0,181,200,0.04);
    border: 1px solid rgba(0,181,200,0.12);
    border-radius: 7px;
    padding: 6px 10px;
    color: #e4f4f6;
    selection-background-color: #00B5C8;
}
QTextEdit:focus, QLineEdit:focus {
    border-color: #00B5C8;
    background: rgba(0,181,200,0.07);
}
"""
