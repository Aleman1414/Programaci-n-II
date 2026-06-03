from __future__ import annotations

import sys
from pathlib import Path


if __package__ in {None, ""}:
    PROJECT_DIR = Path(__file__).resolve().parent.parent
    if str(PROJECT_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_DIR))
    from biblioteca.gui import main
else:
    from .gui import main


if __name__ == "__main__":
    raise SystemExit(main())
