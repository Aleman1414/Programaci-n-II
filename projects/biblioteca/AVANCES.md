# Biblioteca — Avances semanales (formato del itinerario)

Esta guía convierte el proyecto **Biblioteca** en entregas incrementales (“Avances”) para Programación II con enfoque **POO + GUI**.

La idea es que el estudiante construya el sistema en dos fases:

1) **Consola (Semanas 1–5)**: POO + repositorio + menú + reglas.
2) **GUI (Semanas 6–14)**: Tkinter + Treeview + búsqueda + validación + persistencia.

## Estructura recomendada (para estudiantes)

- `models.py` → clases del dominio (`Libro`, etc.)
- `repository.py` → clase contenedora (CRUD + reglas)
- `storage.py` → JSON (cargar/guardar)
- `service.py` → composición (repo + storage)
- `console_app.py` / `gui.py` → interfaz (consola o GUI)

En este repo, el **proyecto completo** está implementado en `projects/biblioteca/` y sirve como referencia para revisión.

## Semana 1 — Avance C1 (Diseño + clases base)

**Entregar**
- Diagrama de clases (UML) de una biblioteca.
- Clases mínimas implementadas:
  - `Libro` con atributos: `isbn`, `titulo`, `autor`, `anio`.
  - Métodos: `descripcion()` (o similar).

**Criterios de revisión**
- Se entiende la diferencia entre clase/objeto/atributo/método.
- Constructor y validaciones mínimas.

**Referencia para revisar**
- `projects/biblioteca/models.py`

## Semana 2 — Avance C2 (Encapsulación + herencia + métodos)

**Entregar**
- Herencia: clase base `Material` y `Libro(Material)` (o equivalente).
- Encapsulación con `@property` para al menos 1 regla (ej. copias).
- Demostración de:
  - `@staticmethod` (validación de ISBN).
  - `@classmethod` (constructor alternativo desde dict/JSON).

**Referencia para revisar**
- `projects/biblioteca/models.py`

## Semana 3 — Avance C3 (Clase contenedora + listas + excepciones)

**Entregar**
- Clase contenedora `RepositorioLibros` con:
  - `agregar`, `listar`, `buscar_por_isbn`
- Manejo de excepciones para reglas de negocio (cuenta/ISBN duplicado, etc.)

**Referencia para revisar**
- `projects/biblioteca/repository.py`
- `projects/biblioteca/models.py` (`ValidationError`)

## Semana 4 — Avance C4 (CRUD completo + control de flujo)

**Entregar**
- CRUD completo en el repositorio:
  - `actualizar`, `eliminar`
  - búsqueda por criterios (por título/autor)
- Reglas de negocio mínimas:
  - prestar/devolver (con excepciones)

**Referencia para revisar**
- `projects/biblioteca/repository.py`

## Semana 5 — Avance C5 (Menú de consola + persistencia)

**Entregar**
- Menú en consola con opciones:
  - Agregar / Listar / Buscar / Actualizar / Eliminar
  - Prestar / Devolver
  - Guardar / Cargar (JSON)

**Referencia para revisar**
- Persistencia: `projects/biblioteca/storage.py`
- Composición (servicio): `projects/biblioteca/service.py`

## Semana 6 — Avance G1 (Preparación GUI + carga inicial)

**Entregar**
- Proyecto configurado para GUI.
- Al iniciar la GUI:
  - carga JSON si existe
  - muestra lista en una tabla (aunque sea simple)

**Referencia para revisar**
- `projects/biblioteca/gui.py`
- `projects/biblioteca/service.py`

## Semana 7 — Avance G2 (GUI Parte I: formulario + agregar)

**Entregar**
- Formulario para capturar libro.
- Botón **Agregar** + validación + mensajes.
- Tabla actualiza al agregar.

**Referencia para revisar**
- `projects/biblioteca/gui.py` (`_on_add`, `_validate_form`)

## Semana 8 — Avance G3 (Archivos: guardar/cargar desde GUI)

**Entregar**
- Botón “Guardar” y guardado automático al operar (opcional).
- Manejo de archivo inexistente.

**Referencia para revisar**
- `projects/biblioteca/storage.py`
- `projects/biblioteca/gui.py` (`_save`)

## Semana 9 — Avance G4 (GUI Parte III: tabla con Treeview + selección)

**Entregar**
- `ttk.Treeview` con columnas.
- Selección de fila carga datos al formulario.

**Referencia para revisar**
- `projects/biblioteca/gui.py` (`Treeview`, `_on_select_row`)

## Semana 10 — Avance G5 (Buscar + modificar)

**Entregar**
- Búsqueda por criterios (ISBN exacto, título/autor contiene).
- Botón **Actualizar** que modifica el registro y refresca tabla.

**Referencia para revisar**
- `projects/biblioteca/repository.py` (`buscar`, `actualizar`)
- `projects/biblioteca/gui.py` (`_on_search`, `_on_update`)

## Semana 11 — Avance G6 (Eliminar + prestar/devolver)

**Entregar**
- Botón **Eliminar** con confirmación.
- Botones **Prestar** y **Devolver** con reglas.

**Referencia para revisar**
- `projects/biblioteca/repository.py` (`prestar`, `devolver`)
- `projects/biblioteca/gui.py` (`_on_delete`, `_on_loan`, `_on_return`)

## Semana 12 — Avance G7 (Validaciones completas)

**Entregar**
- Validación de inputs (obligatorios, numéricos, rango de año, ISBN).
- Mensajes claros (showerror/showinfo).
- Manejo de casos borde (sin selección, duplicados).

**Referencia para revisar**
- `projects/biblioteca/models.py` (reglas + `ValidationError`)
- `projects/biblioteca/gui.py` (errores y confirmaciones)

## Semana 13 — Avance G8 (UX + búsqueda avanzada)

**Entregar**
- Búsqueda multi‑parámetro.
- Filtro “Solo disponibles”.
- Botón “Ver todo / limpiar filtros”.

**Referencia para revisar**
- `projects/biblioteca/repository.py` (`buscar`)
- `projects/biblioteca/gui.py` (`_on_search`, `_on_view_all`)

## Semana 14 — Entrega y defensa (Proyecto final)

**Checklist**
- CRUD completo en GUI
- Persistencia JSON
- Préstamos/devoluciones
- Validaciones
- Código organizado por módulos
- Demostración (5–10 min)

## Semana 15 — Cierre

- Revisión de examen, retroalimentación y mejoras sugeridas:
  - agregar `Usuario`
  - historial de préstamos
  - exportar CSV
  - pruebas unitarias básicas al repositorio

