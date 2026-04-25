# Biblioteca — Mapa de conceptos (para revisión en clase)

Usa este archivo como “guía de lectura” del proyecto.

## Semana 1 — Clases, objetos, constructor, atributos, métodos

- `models.py`: `Material`, `Libro`, `__init__`, atributos y métodos.
- `gui.py`: la clase `BibliotecaApp` como ejemplo de “una clase grande” que compone UI.

## Semana 2 — Encapsulación, properties, herencia, métodos estáticos/de clase

- Encapsulación con convención `_atributo`: `Libro._copias_disponibles`.
- `@property` y validación: `Libro.copias_total`, `Libro.copias_disponibles`.
- Herencia: `Libro(Material)` y `Material.descripcion()`.
- `@staticmethod`: `Libro.validar_isbn()`.
- `@classmethod`: `Libro.from_dict()` (constructor alternativo).

## Semana 3 — Composición, polimorfismo, I/O, excepciones, listas de objetos

- Composición: `Biblioteca` (en `service.py`) contiene `RepositorioLibros` + `JsonStorage`.
- Polimorfismo: `Material.descripcion()` se puede usar para distintos materiales (aquí implementamos `Libro`).
- Excepciones: `ValidationError` y reglas de negocio (prestar/devolver).
- Estructuras: lista de `Libro` en `RepositorioLibros`.

## Semana 4 — Control de flujo + CRUD (buscar/modificar/eliminar)

- `repository.py`: CRUD + búsquedas por criterios.
- Uso de `if`, `for`, `next(...)`, comprensiones.

## Semanas 7–13 — GUI (Tkinter) + Treeview + validaciones + UX + búsquedas avanzadas

- `gui.py`: formulario, botones, eventos, `Treeview`, confirmaciones.
- Búsqueda multi‑parámetro: sección “Búsqueda” (`_on_search`).
- Validación y mensajes: `messagebox.showerror/showinfo/askyesno`.

## Semana 8 — Persistencia en JSON

- `storage.py`: `JsonStorage.load/save`
- `service.py`: carga al iniciar y guarda después de operaciones

## Ejercicios sugeridos (para estudiantes)

1. Agregar una entidad `Usuario` y permitir “prestar” por usuario.
2. Agregar “categoría” y un filtro por categoría.
3. Exportar listado a CSV.
4. Agregar un “historial de préstamos” (lista de eventos).

