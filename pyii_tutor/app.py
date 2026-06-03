from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from typing import Type


def _get_TutorApp() -> Type:
    """
    Resuelve la clase principal tanto si se ejecuta como script
    (`python3 pyii_tutor/app.py`) como si se ejecuta como paquete.
    """
    if __package__ in {None, ""}:
        pkg_root = str(Path(__file__).resolve().parents[1])
        if pkg_root not in sys.path:
            sys.path.insert(0, pkg_root)
        from pyii_tutor.ui import TutorApp
        return TutorApp

    from .ui import TutorApp
    return TutorApp


def main() -> int:
    TutorApp = _get_TutorApp()
    try:
        app = TutorApp()
        app.run()
    except tk.TclError as exc:
        raise SystemExit(f"No se pudo iniciar PyII Tutor: {exc}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
