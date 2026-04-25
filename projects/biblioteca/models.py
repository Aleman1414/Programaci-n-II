from __future__ import annotations

from dataclasses import dataclass


class ValidationError(ValueError):
    pass


@dataclass
class Material:
    """
    Clase base (para explicar herencia).
    En un sistema real podrías tener: Libro, Revista, DVD, etc.
    """

    titulo: str

    def descripcion(self) -> str:
        return self.titulo


@dataclass
class Libro(Material):
    """
    Libro hereda de Material.

    Encapsulación:
    - `copias_disponibles` se guarda internamente en `_copias_disponibles`.
    - Se expone a través de `@property` para validar y controlar cambios.
    """

    isbn: str
    autor: str
    anio: int
    _copias_total: int = 1
    _copias_disponibles: int = 1

    def __post_init__(self) -> None:
        self.titulo = self.titulo.strip()
        self.autor = self.autor.strip()
        self.isbn = self.isbn.strip()

        if not self.titulo:
            raise ValidationError("El título es obligatorio.")
        if not self.autor:
            raise ValidationError("El autor es obligatorio.")
        self.validar_isbn(self.isbn)
        self._validar_anio(self.anio)

        self.copias_total = self._copias_total
        self.copias_disponibles = self._copias_disponibles

    @staticmethod
    def validar_isbn(isbn: str) -> None:
        """
        Método estático: no depende de la instancia (self).
        Validación “didáctica” (simple): ISBN de 10 o 13 dígitos.
        """
        if not isbn.isdigit():
            raise ValidationError("ISBN debe ser numérico.")
        if len(isbn) not in (10, 13):
            raise ValidationError("ISBN debe tener 10 o 13 dígitos.")

    @staticmethod
    def _validar_anio(anio: int) -> None:
        if anio < 1400 or anio > 2100:
            raise ValidationError("Año inválido.")

    @property
    def copias_total(self) -> int:
        return self._copias_total

    @copias_total.setter
    def copias_total(self, value: int) -> None:
        value = int(value)
        if value <= 0:
            raise ValidationError("Copias total debe ser mayor que 0.")
        if self._copias_disponibles > value:
            raise ValidationError("Copias disponibles no puede ser mayor que copias total.")
        self._copias_total = value

    @property
    def copias_disponibles(self) -> int:
        return self._copias_disponibles

    @copias_disponibles.setter
    def copias_disponibles(self, value: int) -> None:
        value = int(value)
        if value < 0:
            raise ValidationError("Copias disponibles no puede ser negativa.")
        if value > self._copias_total:
            raise ValidationError("Copias disponibles no puede superar copias total.")
        self._copias_disponibles = value

    @property
    def disponible(self) -> bool:
        return self._copias_disponibles > 0

    def prestar(self) -> None:
        if self._copias_disponibles <= 0:
            raise ValidationError("No hay copias disponibles para préstamo.")
        self._copias_disponibles -= 1

    def devolver(self) -> None:
        if self._copias_disponibles >= self._copias_total:
            raise ValidationError("Todas las copias ya están disponibles.")
        self._copias_disponibles += 1

    def descripcion(self) -> str:
        return f"{self.titulo} — {self.autor} ({self.anio})"

    def to_dict(self) -> dict:
        return {
            "titulo": self.titulo,
            "isbn": self.isbn,
            "autor": self.autor,
            "anio": self.anio,
            "copias_total": self.copias_total,
            "copias_disponibles": self.copias_disponibles,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Libro":
        """
        Método de clase: constructor alternativo.
        Útil para cargar desde JSON.
        """
        return cls(
            titulo=str(data.get("titulo", "")),
            isbn=str(data.get("isbn", "")),
            autor=str(data.get("autor", "")),
            anio=int(data.get("anio", 0)),
            _copias_total=int(data.get("copias_total", 1)),
            _copias_disponibles=int(data.get("copias_disponibles", 1)),
        )

