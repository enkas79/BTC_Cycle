"""Worker QThread generico: esegue una funzione di backend fuori dal thread GUI."""

from __future__ import annotations

from typing import Any, Callable

from PyQt6.QtCore import QThread, pyqtSignal


class TaskWorker(QThread):
    """Esegue ``fn(*args)``; se ``with_progress`` passa anche ``progress=callback``."""

    progress = pyqtSignal(int, str)
    succeeded = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, fn: Callable[..., Any], *args: Any, with_progress: bool = False,
                 parent=None):
        super().__init__(parent)
        self._fn = fn
        self._args = args
        self._with_progress = with_progress

    def _emit_progress(self, value: int, message: str = "") -> None:
        self.progress.emit(int(value), message)

    def run(self) -> None:
        try:
            if self._with_progress:
                result = self._fn(*self._args, progress=self._emit_progress)
            else:
                result = self._fn(*self._args)
        except Exception as exc:  # l'errore torna alla GUI come segnale, mai crash
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return
        self.succeeded.emit(result)
