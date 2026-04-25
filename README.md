# Programación II (Python) — Tutor Offline

Aplicación educativa en **Python (Tkinter)** para apoyar la clase de Programación II: teoría, ejemplos ejecutables, ejercicios y mini‑quizzes, organizada por semanas según el itinerario del curso (adaptado de Java → Python).

## Requisitos

- Python 3.10+ (recomendado 3.11+)
- No requiere dependencias externas

## Ejecutar

Desde la raíz del proyecto:

```bash
python3 -m pyii_tutor
```

En Windows (según instalación):

```bash
py -m pyii_tutor
```

## Proyecto de referencia (POO + GUI)

Incluye un CRUD completo con Tkinter (POO + repositorio + persistencia JSON):

```bash
python3 examples/alumnos_crud_tkinter.py
```

## Proyecto ejemplo para clases: Biblioteca (POO + GUI + JSON)

Proyecto modular, pensado para explicar conceptos por semana:

```bash
python3 projects/biblioteca/app.py
```

Guía de revisión: `projects/biblioteca/CONCEPTOS.md`
Avances semanales: `projects/biblioteca/AVANCES.md`

## Importar / regenerar el itinerario desde un .docx

Incluye un importador simple que extrae el cronograma (Semanas) desde el DOCX y genera un JSON base:

```bash
python3 tools/import_syllabus_docx.py "/ruta/al/Sílabo-Itinerario-Programacion-II.docx" --out content/curriculum_importado.json
```

Luego puedes abrir `content/curriculum.json` y ajustar/expandir teoría, ejemplos y quizzes.

## Nota sobre “Ejecutar” ejemplos

La app puede ejecutar snippets en un proceso separado con timeout. Es un recurso didáctico local; no es un sandbox de seguridad.
