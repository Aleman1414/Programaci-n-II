from __future__ import annotations

from .ui import TutorApp


def main() -> int:
    app = TutorApp()
    app.run()
    return 0

