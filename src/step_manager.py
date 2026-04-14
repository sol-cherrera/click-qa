"""
src/step_manager.py — Gestion del listado de pasos en memoria.
"""
from typing import List, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal


class StepManager(QObject):
    """
    Administra la lista de pasos capturados durante la sesion.
    Emite señales cuando cambia el contenido.
    """
    steps_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._steps: List[Dict[str, Any]] = []
        self._next_id: int = 1

    # ─── Propiedades ───────────────────────────────────────────────
    @property
    def steps(self) -> List[Dict[str, Any]]:
        return self._steps

    @property
    def count(self) -> int:
        return len(self._steps)

    # ─── CRUD ──────────────────────────────────────────────────────
    def add_step(self, step: Dict[str, Any]):
        step["id"] = self._next_id
        self._next_id += 1
        step["number"] = len(self._steps) + 1
        self._steps.append(step)
        self.steps_changed.emit()

    def remove_step(self, step_id: int):
        step_id = int(step_id)
        self._steps = [s for s in self._steps if s.get("id") != step_id]
        self._renumber()
        self.steps_changed.emit()

    def update_description(self, step_id: int, description: str):
        for step in self._steps:
            if step.get("id") == step_id:
                step["description"] = description
                break

    def move_step(self, step_id: int, direction: int):
        """direction: -1 = subir, +1 = bajar"""
        idx = next((i for i, s in enumerate(self._steps) if s.get("id") == step_id), None)
        if idx is None:
            return
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(self._steps):
            return
        self._steps[idx], self._steps[new_idx] = self._steps[new_idx], self._steps[idx]
        self._renumber()
        self.steps_changed.emit()

    def add_manual_note(self):
        """Agrega una nota de texto (sin screenshot)."""
        from datetime import datetime
        note = {
            "id":               self._next_id,
            "number":           len(self._steps) + 1,
            "action":           "Nota manual",
            "click_pos":        None,
            "description":      "Escribe tu observacion aqui...",
            "screenshot_bytes": None,
            "timestamp":        datetime.now().isoformat(),
            "is_note":          True,
        }
        self._next_id += 1
        self._steps.append(note)
        self.steps_changed.emit()

    def clear(self):
        self._steps = []
        self._next_id = 1
        self.steps_changed.emit()

    def _renumber(self):
        for i, step in enumerate(self._steps):
            step["number"] = i + 1
