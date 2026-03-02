"""
src/recorder.py — Motor de grabacion v3

Cambios v3:
  - Highlight en forma de cursor de mouse (flecha de puntero)
    → No tapa el contenido, señala exactamente dónde se hizo clic
    → Contorno teal (#00B5C8) con relleno blanco semi-transparente
  - Paleta SolutoQA (teal)
"""
import io
import time
import threading
from datetime import datetime

from pynput import mouse, keyboard
from PIL import Image, ImageDraw
import mss

from PyQt6.QtCore import QObject, pyqtSignal


# ─── Cursor shape ──────────────────────────────────────────────────
def _cursor_polygon(x: int, y: int, s: float = 1.6):
    """
    Genera los vertices de una flecha tipo cursor de mouse.
    El TIP (punta) esta en (x, y). El cuerpo se extiende hacia abajo-derecha.
    s = factor de escala (1.6 ≈ 26px de alto)
    """
    def p(dx, dy):
        return (int(x + dx * s), int(y + dy * s))

    return [
        p(0,   0),     # 0  tip (punta exacta del clic)
        p(0,   14),    # 1  borde izquierdo
        p(3.5, 10.5),  # 2  muesca interior
        p(6,   15),    # 3  mango izquierdo
        p(8,   14),    # 4  mango derecho
        p(5.5,  9.5),  # 5  muesca interior derecha
        p(9,    9.5),  # 6  tope derecho
        p(3,    3),    # 7  borde superior derecho
    ]


def draw_highlight(img: Image.Image, x: int, y: int,
                   step_number: int = None,
                   color: tuple = (255, 17, 17, 255)) -> Image.Image:
    """
    Dibuja un cursor de mouse cuya punta apunta EXACTAMENTE a (x, y).
    color: RGBA tuple — por defecto rojo. Configurable desde el editor.
    """
    out  = img.copy()
    draw = ImageDraw.Draw(out, "RGBA")

    WHITE  = (255, 255, 255, 200)
    SHADOW = (0, 0, 0, 110)

    shadow_pts = _cursor_polygon(x + 2, y + 2, s=1.6)
    draw.polygon(shadow_pts, fill=SHADOW)

    cursor_pts = _cursor_polygon(x, y, s=1.6)
    draw.polygon(cursor_pts, fill=WHITE)

    closed = cursor_pts + [cursor_pts[0]]
    for i in range(len(closed) - 1):
        draw.line([closed[i], closed[i + 1]], fill=color, width=2)

    draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=color)

    return out


# ─── Motor de grabacion ────────────────────────────────────────────
class RecordingEngine(QObject):
    step_captured  = pyqtSignal(dict)
    status_message = pyqtSignal(str)

    def __init__(self, excluded_rects_fn=None):
        super().__init__()
        self.active            = False
        self.paused            = False
        self._step_count       = 0
        self._capturing        = False
        self._mouse_listener   = None
        self._hotkey_listener  = None
        self._excluded_rects   = excluded_rects_fn or (lambda: [])
        self._region: dict | None = None

    # ─── Region ────────────────────────────────────────────────────
    def set_region(self, x: int, y: int, w: int, h: int):
        self._region = {"left": x, "top": y, "width": w, "height": h}
        self.status_message.emit(f"Region: {w}×{h}px en ({x},{y})")

    def clear_region(self):
        self._region = None
        self.status_message.emit("Region: pantalla completa")

    def get_region(self) -> dict | None:
        return self._region

    # ─── Ciclo de vida ─────────────────────────────────────────────
    def start(self):
        self._step_count = 0
        self.active  = True
        self.paused  = False
        self._start_listeners()
        self.status_message.emit("Grabacion iniciada")

    def pause(self):
        self.paused = True
        self.status_message.emit("Grabacion pausada")

    def resume(self):
        self.paused = False
        self.status_message.emit("Grabacion reanudada")

    def stop(self):
        self.active = False
        self.paused = False
        self._stop_listeners()
        self.status_message.emit("Grabacion detenida")

    def set_step_count(self, count: int):
        self._step_count = count

    # ─── Listeners ─────────────────────────────────────────────────
    def _start_listeners(self):
        self._mouse_listener = mouse.Listener(on_click=self._on_click)
        self._mouse_listener.daemon = True
        self._mouse_listener.start()

        self._hotkey_listener = keyboard.GlobalHotKeys({
            "<ctrl>+<shift>+s": self._on_hotkey
        })
        self._hotkey_listener.daemon = True
        self._hotkey_listener.start()

    def _stop_listeners(self):
        for listener in (self._mouse_listener, self._hotkey_listener):
            if listener:
                try:
                    listener.stop()
                except Exception:
                    pass
        self._mouse_listener  = None
        self._hotkey_listener = None

    # ─── Callbacks ─────────────────────────────────────────────────
    def _on_click(self, x, y, button, pressed):
        if not pressed or not self.active or self.paused or self._capturing:
            return
        if button != mouse.Button.left:
            return
        if self._is_in_excluded_rect(x, y):
            return
        threading.Thread(target=self._capture, args=(x, y, "Click"), daemon=True).start()

    def _on_hotkey(self):
        if not self.active or self.paused or self._capturing:
            return
        ctrl = mouse.Controller()
        x, y = ctrl.position
        threading.Thread(
            target=self._capture,
            args=(x, y, "Captura manual (Ctrl+Shift+S)"),
            daemon=True
        ).start()

    # ─── Captura ───────────────────────────────────────────────────
    def _capture(self, x: int, y: int, action_label: str):
        if self._capturing:
            return
        self._capturing = True
        try:
            time.sleep(0.07)
            raw_bytes, hl_bytes, rel_x, rel_y = self._take_screenshot(x, y)
            if not raw_bytes:
                return

            self._step_count += 1
            step = {
                "id":                   int(time.time() * 1000),
                "number":               self._step_count,
                "action":               action_label,
                "click_pos":            (x, y),
                "click_pos_rel":        (rel_x, rel_y),
                "description":          "Click en pantalla",
                "screenshot_bytes":     hl_bytes,
                "screenshot_raw_bytes": raw_bytes,
                "timestamp":            datetime.now().isoformat(),
                "highlight_enabled":    True,
                "highlight_color":      (255, 17, 17, 255),  # rojo por defecto
            }
            self.step_captured.emit(step)
        except Exception as e:
            self.status_message.emit(f"Error al capturar: {e}")
        finally:
            self._capturing = False

    def _take_screenshot(self, click_x: int, click_y: int):
        try:
            with mss.mss() as sct:
                monitor = self._region or self._monitor_containing(sct, click_x, click_y)
                raw     = sct.grab(monitor)
                img     = Image.frombytes(
                    "RGB", (raw.width, raw.height), raw.bgra, "raw", "BGRX"
                )

            rel_x = click_x - monitor["left"]
            rel_y = click_y - monitor["top"]

            # RAW (sin highlight)
            raw_buf = io.BytesIO()
            img.save(raw_buf, format="PNG", optimize=True)

            # Con highlight (cursor flecha)
            hl_img = draw_highlight(img, rel_x, rel_y, self._step_count + 1)
            hl_buf = io.BytesIO()
            hl_img.save(hl_buf, format="PNG", optimize=True)

            return raw_buf.getvalue(), hl_buf.getvalue(), rel_x, rel_y

        except Exception as e:
            print(f"[Recorder] Screenshot error: {e}")
            return None, None, 0, 0

    # ─── Helpers ───────────────────────────────────────────────────
    def _monitor_containing(self, sct, x: int, y: int) -> dict:
        for mon in sct.monitors[1:]:
            if (mon["left"] <= x < mon["left"] + mon["width"] and
                    mon["top"] <= y < mon["top"] + mon["height"]):
                return mon
        return sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]

    def _is_in_excluded_rect(self, x: int, y: int) -> bool:
        try:
            for rect in self._excluded_rects():
                if rect.left() <= x <= rect.right() and rect.top() <= y <= rect.bottom():
                    return True
        except Exception:
            pass
        return False
