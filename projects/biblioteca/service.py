from __future__ import annotations

from pathlib import Path

from repository import RepositorioLibros
from storage import JsonStorage


class Biblioteca:
    """
    Capa de servicio (composición):
    - Contiene el repositorio (lógica en memoria)
    - Contiene el storage (persistencia)
    """

    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path
        self.repo = RepositorioLibros()
        self._load()

    def _load(self) -> None:
        self.repo.set_items(JsonStorage.load(self.data_path))

    def save(self) -> None:
        JsonStorage.save(self.data_path, self.repo.listar())
