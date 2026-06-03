from __future__ import annotations

import os
import sys
from typing import Type


def _get_TutorApp() -> Type:
    try:
        from pyii_tutor.ui import TutorApp
        return TutorApp
    except ModuleNotFoundError:
        pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        if pkg_root not in sys.path:
            sys.path.insert(0, pkg_root)
        from pyii_tutor.ui import TutorApp
        return TutorApp


def main() -> int:
    TutorApp = _get_TutorApp()
    app = TutorApp()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

