from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from models import Libro, ValidationError
from service import Biblioteca


class BibliotecaApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Biblioteca — POO + Tkinter + JSON")
        self.geometry("1080x640")

        data_path = Path(__file__).resolve().parent / "data" / "libros.json"
        self.biblioteca = Biblioteca(data_path)
        self._selected_isbn: str | None = None

        self._build_ui()
        self._refresh_table(self.biblioteca.repo.listar())

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        header = ttk.Frame(root)
        header.pack(fill="x")
        ttk.Label(header, text="Biblioteca", font=("TkDefaultFont", 14, "bold")).pack(side="left")
        ttk.Label(header, text="CRUD + préstamos/devoluciones").pack(side="left", padx=12)

        # Formulario
        form = ttk.LabelFrame(root, text="Libro (Formulario)", padding=10)
        form.pack(fill="x", pady=(12, 10))

        self.var_isbn = tk.StringVar()
        self.var_titulo = tk.StringVar()
        self.var_autor = tk.StringVar()
        self.var_anio = tk.StringVar()
        self.var_copias_total = tk.StringVar(value="1")

        ttk.Label(form, text="ISBN").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_isbn, width=18).grid(row=0, column=1, sticky="w", padx=(8, 16))

        ttk.Label(form, text="Título").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.var_titulo, width=44).grid(row=0, column=3, sticky="we", padx=(8, 16))

        ttk.Label(form, text="Autor").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(form, textvariable=self.var_autor, width=32).grid(row=1, column=1, sticky="we", padx=(8, 16), pady=(8, 0))

        ttk.Label(form, text="Año").grid(row=1, column=2, sticky="w", pady=(8, 0))
        ttk.Entry(form, textvariable=self.var_anio, width=10).grid(row=1, column=3, sticky="w", padx=(8, 16), pady=(8, 0))

        ttk.Label(form, text="Copias total").grid(row=1, column=4, sticky="w", pady=(8, 0))
        ttk.Entry(form, textvariable=self.var_copias_total, width=10).grid(row=1, column=5, sticky="w", padx=(8, 0), pady=(8, 0))

        form.grid_columnconfigure(3, weight=1)

        actions = ttk.Frame(form)
        actions.grid(row=2, column=0, columnspan=6, sticky="w", pady=(10, 0))
        ttk.Button(actions, text="Agregar", command=self._on_add).pack(side="left")
        ttk.Button(actions, text="Actualizar", command=self._on_update).pack(side="left", padx=6)
        ttk.Button(actions, text="Eliminar", command=self._on_delete).pack(side="left", padx=6)
        ttk.Button(actions, text="Prestar", command=self._on_loan).pack(side="left", padx=12)
        ttk.Button(actions, text="Devolver", command=self._on_return).pack(side="left", padx=6)
        ttk.Button(actions, text="Limpiar", command=self._clear_form).pack(side="left", padx=12)

        # Búsqueda
        search = ttk.LabelFrame(root, text="Búsqueda", padding=10)
        search.pack(fill="x", pady=(0, 10))

        self.var_buscar_isbn = tk.StringVar()
        self.var_buscar_titulo = tk.StringVar()
        self.var_buscar_autor = tk.StringVar()
        self.var_buscar_disponibles = tk.BooleanVar(value=False)

        ttk.Label(search, text="ISBN").grid(row=0, column=0, sticky="w")
        ttk.Entry(search, textvariable=self.var_buscar_isbn, width=18).grid(row=0, column=1, sticky="w", padx=(8, 16))

        ttk.Label(search, text="Título contiene").grid(row=0, column=2, sticky="w")
        ttk.Entry(search, textvariable=self.var_buscar_titulo, width=32).grid(row=0, column=3, sticky="we", padx=(8, 16))

        ttk.Label(search, text="Autor contiene").grid(row=0, column=4, sticky="w")
        ttk.Entry(search, textvariable=self.var_buscar_autor, width=24).grid(row=0, column=5, sticky="we", padx=(8, 16))

        ttk.Checkbutton(search, text="Solo disponibles", variable=self.var_buscar_disponibles).grid(row=0, column=6, sticky="w")

        ttk.Button(search, text="Buscar", command=self._on_search).grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Button(search, text="Ver todo", command=self._on_view_all).grid(row=1, column=1, sticky="w", pady=(10, 0))

        search.grid_columnconfigure(3, weight=1)
        search.grid_columnconfigure(5, weight=1)

        # Tabla
        table_box = ttk.Frame(root)
        table_box.pack(fill="both", expand=True)

        cols = ("isbn", "titulo", "autor", "anio", "total", "disp", "estado")
        self.tree = ttk.Treeview(table_box, columns=cols, show="headings", height=14)
        self.tree.heading("isbn", text="ISBN")
        self.tree.heading("titulo", text="Título")
        self.tree.heading("autor", text="Autor")
        self.tree.heading("anio", text="Año")
        self.tree.heading("total", text="Total")
        self.tree.heading("disp", text="Disp.")
        self.tree.heading("estado", text="Estado")

        self.tree.column("isbn", width=120, anchor="w")
        self.tree.column("titulo", width=340, anchor="w")
        self.tree.column("autor", width=220, anchor="w")
        self.tree.column("anio", width=60, anchor="center")
        self.tree.column("total", width=60, anchor="center")
        self.tree.column("disp", width=60, anchor="center")
        self.tree.column("estado", width=100, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select_row)

        yscroll = ttk.Scrollbar(table_box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side="left", fill="y")

        footer = ttk.Frame(root)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Button(footer, text="Guardar a JSON", command=self._save).pack(side="left")
        ttk.Label(footer, text="Archivo: projects/biblioteca/data/libros.json").pack(side="left", padx=10)

    def _validate_form(self) -> Libro:
        isbn = self.var_isbn.get().strip()
        titulo = self.var_titulo.get().strip()
        autor = self.var_autor.get().strip()

        try:
            anio = int(self.var_anio.get().strip())
        except ValueError:
            raise ValidationError("Año debe ser numérico.")

        try:
            copias_total = int(self.var_copias_total.get().strip())
        except ValueError:
            raise ValidationError("Copias total debe ser numérico.")

        # Al crear/editar desde formulario, asumimos disponibles = total (regla simple didáctica).
        return Libro(
            titulo=titulo,
            isbn=isbn,
            autor=autor,
            anio=anio,
            _copias_total=copias_total,
            _copias_disponibles=copias_total,
        )

    def _refresh_table(self, rows: list[Libro]) -> None:
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for l in rows:
            estado = "Disponible" if l.disponible else "No disponible"
            self.tree.insert(
                "",
                "end",
                iid=l.isbn,
                values=(l.isbn, l.titulo, l.autor, l.anio, l.copias_total, l.copias_disponibles, estado),
            )

    def _on_select_row(self, _evt: object) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        isbn = str(sel[0])
        libro = self.biblioteca.repo.buscar_por_isbn(isbn)
        if libro is None:
            return
        self._selected_isbn = isbn

        self.var_isbn.set(libro.isbn)
        self.var_titulo.set(libro.titulo)
        self.var_autor.set(libro.autor)
        self.var_anio.set(str(libro.anio))
        self.var_copias_total.set(str(libro.copias_total))

    def _on_add(self) -> None:
        try:
            libro = self._validate_form()
            self.biblioteca.repo.agregar(libro)
            self._save(silent=True)
            self._refresh_table(self.biblioteca.repo.listar())
            self._selected_isbn = None
            self._clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_update(self) -> None:
        try:
            if not self._selected_isbn:
                raise ValidationError("Selecciona un libro de la tabla para actualizar.")

            nuevo = self._validate_form()
            self.biblioteca.repo.actualizar(self._selected_isbn, nuevo)
            self._save(silent=True)
            self._refresh_table(self.biblioteca.repo.listar())
            self._selected_isbn = nuevo.isbn
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_delete(self) -> None:
        try:
            if not self._selected_isbn:
                raise ValidationError("Selecciona un libro de la tabla para eliminar.")
            if not messagebox.askyesno("Confirmar", f"¿Eliminar ISBN {self._selected_isbn}?"):
                return
            self.biblioteca.repo.eliminar(self._selected_isbn)
            self._save(silent=True)
            self._refresh_table(self.biblioteca.repo.listar())
            self._selected_isbn = None
            self._clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_loan(self) -> None:
        try:
            if not self._selected_isbn:
                raise ValidationError("Selecciona un libro para prestar.")
            self.biblioteca.repo.prestar(self._selected_isbn)
            self._save(silent=True)
            self._refresh_table(self.biblioteca.repo.listar())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_return(self) -> None:
        try:
            if not self._selected_isbn:
                raise ValidationError("Selecciona un libro para devolver.")
            self.biblioteca.repo.devolver(self._selected_isbn)
            self._save(silent=True)
            self._refresh_table(self.biblioteca.repo.listar())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_search(self) -> None:
        rows = self.biblioteca.repo.buscar(
            isbn=self.var_buscar_isbn.get(),
            titulo=self.var_buscar_titulo.get(),
            autor=self.var_buscar_autor.get(),
            solo_disponibles=bool(self.var_buscar_disponibles.get()),
        )
        self._refresh_table(rows)

    def _on_view_all(self) -> None:
        self.var_buscar_isbn.set("")
        self.var_buscar_titulo.set("")
        self.var_buscar_autor.set("")
        self.var_buscar_disponibles.set(False)
        self._refresh_table(self.biblioteca.repo.listar())

    def _clear_form(self) -> None:
        self.var_isbn.set("")
        self.var_titulo.set("")
        self.var_autor.set("")
        self.var_anio.set("")
        self.var_copias_total.set("1")

    def _save(self, silent: bool = False) -> None:
        self.biblioteca.save()
        if not silent:
            messagebox.showinfo("OK", "Guardado en projects/biblioteca/data/libros.json")


def main() -> int:
    BibliotecaApp().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
