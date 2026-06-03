from __future__ import annotations

import json
from pathlib import Path

from .models import Libro


class JsonStorage:
    @staticmethod
    def load(path: Path) -> list[Libro]:
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return [Libro.from_dict(d) for d in data]

    @staticmethod
    def save(path: Path, libros: list[Libro]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [l.to_dict() for l in libros]
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
