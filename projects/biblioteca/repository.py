from __future__ import annotations

from .models import Libro, ValidationError


class RepositorioLibros:
    """
    Clase contenedora: encapsula la lista de libros y el CRUD.
    """

    def __init__(self) -> None:
        self._items: list[Libro] = []

    def listar(self) -> list[Libro]:
        return list(self._items)

    def existe_isbn(self, isbn: str) -> bool:
        return any(l.isbn == isbn for l in self._items)

    def buscar_por_isbn(self, isbn: str) -> Libro | None:
        return next((l for l in self._items if l.isbn == isbn), None)

    def buscar(self, *, isbn: str = "", titulo: str = "", autor: str = "", solo_disponibles: bool = False) -> list[Libro]:
        """
        Búsqueda multi‑parámetro (para semanas de GUI/UX).
        """
        isbn = isbn.strip()
        titulo = titulo.strip().lower()
        autor = autor.strip().lower()

        resultados: list[Libro] = []
        for libro in self._items:
            if isbn and libro.isbn != isbn:
                continue
            if titulo and titulo not in libro.titulo.lower():
                continue
            if autor and autor not in libro.autor.lower():
                continue
            if solo_disponibles and not libro.disponible:
                continue
            resultados.append(libro)
        return resultados

    def agregar(self, libro: Libro) -> None:
        if self.existe_isbn(libro.isbn):
            raise ValidationError("Ya existe un libro con ese ISBN.")
        self._items.append(libro)

    def actualizar(self, isbn_actual: str, nuevo: Libro) -> None:
        existente = self.buscar_por_isbn(isbn_actual)
        if existente is None:
            raise ValidationError("No existe el libro a actualizar.")
        if nuevo.isbn != isbn_actual and self.existe_isbn(nuevo.isbn):
            raise ValidationError("El nuevo ISBN ya existe.")

        existente.isbn = nuevo.isbn
        existente.titulo = nuevo.titulo
        existente.autor = nuevo.autor
        existente.anio = nuevo.anio

        # Ajuste de copias: conserva préstamos si es posible.
        # Regla: no permitir que disponibles supere total.
        existentes_prestadas = existente.copias_total - existente.copias_disponibles
        if nuevo.copias_total < existentes_prestadas:
            raise ValidationError("Copias total no puede ser menor que copias prestadas actualmente.")
        existente.copias_total = nuevo.copias_total
        existente.copias_disponibles = nuevo.copias_total - existentes_prestadas

    def eliminar(self, isbn: str) -> None:
        before = len(self._items)
        self._items = [l for l in self._items if l.isbn != isbn]
        if len(self._items) == before:
            raise ValidationError("No existe el libro a eliminar.")

    def prestar(self, isbn: str) -> None:
        libro = self.buscar_por_isbn(isbn)
        if libro is None:
            raise ValidationError("No existe el libro.")
        libro.prestar()

    def devolver(self, isbn: str) -> None:
        libro = self.buscar_por_isbn(isbn)
        if libro is None:
            raise ValidationError("No existe el libro.")
        libro.devolver()

    def set_items(self, items: list[Libro]) -> None:
        self._items = list(items)
