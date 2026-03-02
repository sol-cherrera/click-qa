"""
src/exporters/pdf_exporter.py — Exporta pasos a PDF con fpdf2.
"""
import os
import io
import tempfile
from datetime import datetime
from typing import List, Dict, Any

from fpdf import FPDF
from PIL import Image


def export_pdf(steps: List[Dict[str, Any]], filepath: str) -> None:
    """
    Genera un PDF profesional con todos los pasos.
    Cada paso ocupa su propia pagina con: numero, accion, descripcion,
    timestamp e imagen del screenshot con el highlight rojo ya embebido.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Portada ─────────────────────────────────────────────────────
    pdf.add_page()
    _draw_page_background(pdf)

    # Titulo
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(167, 139, 250)  # lila
    pdf.ln(30)
    pdf.cell(0, 12, "Plan de Prueba Manual", ln=True, align="C")

    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(136, 136, 153)
    pdf.ln(4)
    pdf.cell(0, 8, f"{len(steps)} paso{'s' if len(steps)!=1 else ''} documentado{'s' if len(steps)!=1 else ''}",
             ln=True, align="C")
    pdf.cell(0, 8, f"Generado el {datetime.now().strftime('%d/%m/%Y — %H:%M')}",
             ln=True, align="C")

    # Linea decorativa
    pdf.ln(10)
    pdf.set_draw_color(124, 58, 237)
    pdf.set_line_width(0.5)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())

    # ── Pagina por paso ──────────────────────────────────────────────
    tmp_files = []
    try:
        for step in steps:
            pdf.add_page()
            _draw_page_background(pdf)
            y = 15

            # Numero del paso + badge de accion
            pdf.set_fill_color(124, 58, 237)
            pdf.ellipse(15, y, 10, 10, style="F")
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(255, 255, 255)
            pdf.set_xy(15, y + 0.5)
            pdf.cell(10, 10, str(step["number"]), align="C")

            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(167, 139, 250)
            pdf.set_xy(28, y + 2)
            pdf.cell(0, 6, step.get("action", "Accion"))
            y += 16

            # Descripcion
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(232, 232, 240)
            pdf.set_xy(15, y)
            desc = step.get("description", "")
            lines = pdf.multi_cell(180, 7, desc, dry_run=True, output="LINES")
            pdf.multi_cell(180, 7, desc)
            y += len(lines) * 7 + 5

            # Timestamp
            if step.get("timestamp"):
                try:
                    ts = datetime.fromisoformat(step["timestamp"])
                    ts_str = ts.strftime("%H:%M:%S — %d/%m/%Y")
                except Exception:
                    ts_str = step["timestamp"]
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(85, 85, 102)
                pdf.set_xy(15, y)
                pdf.cell(0, 6, ts_str)
                y += 10

            # Screenshot
            if step.get("screenshot_bytes"):
                tmp_path = _save_temp_image(step["screenshot_bytes"])
                if tmp_path:
                    tmp_files.append(tmp_path)
                    try:
                        available_h = pdf.h - y - 20  # espacio disponible en puntos
                        img_w       = 180
                        # Calcular alto proporcional
                        with Image.open(tmp_path) as img:
                            w_orig, h_orig = img.size
                        ratio  = h_orig / w_orig if w_orig > 0 else 0.5
                        img_h  = min(img_w * ratio, available_h)

                        # Borde sutil
                        pdf.set_draw_color(80, 80, 100)
                        pdf.set_line_width(0.3)
                        pdf.rect(15, y, img_w, img_h)
                        pdf.image(tmp_path, x=15, y=y, w=img_w, h=img_h)
                    except Exception as e:
                        pdf.set_xy(15, y)
                        pdf.set_text_color(200, 80, 80)
                        pdf.cell(0, 8, f"[Error al cargar imagen: {e}]")

    finally:
        for p in tmp_files:
            try:
                os.unlink(p)
            except Exception:
                pass

    pdf.output(filepath)


# ─── Helpers ──────────────────────────────────────────────────────
def _draw_page_background(pdf: FPDF):
    """Relleno gris muy oscuro como fondo de pagina."""
    pdf.set_fill_color(15, 15, 19)
    pdf.rect(0, 0, pdf.w, pdf.h, style="F")


def _save_temp_image(screenshot_bytes: bytes) -> str | None:
    """Guarda los bytes como PNG en un archivo temporal y retorna la ruta."""
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.write(screenshot_bytes)
        tmp.close()
        return tmp.name
    except Exception:
        return None
