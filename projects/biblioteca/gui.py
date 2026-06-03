from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

if __package__ in {None, ""}:
    PACKAGE_DIR = Path(__file__).resolve().parent
    PROJECT_DIR = PACKAGE_DIR.parent
    if str(PROJECT_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_DIR))
    from biblioteca.models import Libro, ValidationError
    from biblioteca.service import Biblioteca
else:
    from .models import Libro, ValidationError
    from .service import Biblioteca


class BibliotecaApp(tk.Tk):
    BG = "#F3F6FB"
    SURFACE = "#FFFFFF"
    TEXT = "#0F172A"
    MUTED = "#64748B"
    BORDER = "#D8E0EC"
    ACCENT = "#2563EB"
    ACCENT_DARK = "#1D4ED8"
    SUCCESS = "#16A34A"
    DANGER = "#DC2626"

    def __init__(self) -> None:
        super().__init__()
        self.title("Biblioteca | Gestión moderna de libros")
        self.geometry("1280x780")
        self.minsize(1120, 680)
        self.configure(bg=self.BG)

        self._configure_style()

        data_path = Path(__file__).resolve().parent / "data" / "libros.json"
        self.biblioteca = Biblioteca(data_path)
        self._selected_isbn: str | None = None

        self._build_ui()
        self._refresh_table(self.biblioteca.repo.listar())
        self._update_dashboard()
        self._set_status("Listo. La biblioteca se cargó correctamente.")

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=self.BG, foreground=self.TEXT, font=("Helvetica", 10))
        style.configure("Root.TFrame", background=self.BG)
        style.configure("Header.TFrame", background=self.TEXT)
        style.configure("HeaderTitle.TLabel", background=self.TEXT, foreground="white", font=("Helvetica", 24, "bold"))
        style.configure("HeaderSub.TLabel", background=self.TEXT, foreground="#CBD5E1", font=("Helvetica", 10))

        style.configure(
            "Card.TFrame",
            background=self.SURFACE,
            relief="flat",
            borderwidth=1,
        )
        style.configure("CardTitle.TLabel", background=self.SURFACE, foreground=self.TEXT, font=("Helvetica", 11, "bold"))
        style.configure("CardText.TLabel", background=self.SURFACE, foreground=self.MUTED)
        style.configure("MetricValue.TLabel", background=self.SURFACE, foreground=self.TEXT, font=("Helvetica", 20, "bold"))
        style.configure("MetricLabel.TLabel", background=self.SURFACE, foreground=self.MUTED, font=("Helvetica", 9))
        style.configure("Section.TLabelframe", background=self.SURFACE, foreground=self.TEXT, borderwidth=1)
        style.configure("Section.TLabelframe.Label", background=self.SURFACE, foreground=self.TEXT, font=("Helvetica", 10, "bold"))
        style.configure("TLabel", background=self.BG, foreground=self.TEXT)
        style.configure("TEntry", fieldbackground="white")
        style.configure("TCheckbutton", background=self.SURFACE)
        style.configure("Treeview", background="white", fieldbackground="white", foreground=self.TEXT, rowheight=30)
        style.configure(
            "Treeview.Heading",
            font=("Helvetica", 10, "bold"),
            background="#E2E8F0",
            foreground=self.TEXT,
            relief="flat",
        )
        style.map("Treeview.Heading", background=[("active", "#CBD5E1")])

        style.configure("Primary.TButton", background=self.ACCENT, foreground="white", padding=(14, 8), borderwidth=0)
        style.map("Primary.TButton", background=[("active", self.ACCENT_DARK), ("pressed", self.ACCENT_DARK)])
        style.configure("Secondary.TButton", background="#E2E8F0", foreground=self.TEXT, padding=(14, 8), borderwidth=0)
        style.map("Secondary.TButton", background=[("active", "#CBD5E1"), ("pressed", "#CBD5E1")])
        style.configure("Danger.TButton", background=self.DANGER, foreground="white", padding=(14, 8), borderwidth=0)
        style.map("Danger.TButton", background=[("active", "#B91C1C"), ("pressed", "#B91C1C")])
        style.configure("Success.TButton", background=self.SUCCESS, foreground="white", padding=(14, 8), borderwidth=0)
        style.map("Success.TButton", background=[("active", "#15803D"), ("pressed", "#15803D")])

    def _build_ui(self) -> None:
        root = ttk.Frame(self, style="Root.TFrame", padding=18)
        root.pack(fill="both", expand=True)

        banner = tk.Frame(root, bg=self.TEXT, padx=22, pady=18)
        banner.pack(fill="x")
        title_box = tk.Frame(banner, bg=self.TEXT)
        title_box.pack(side="left", fill="x", expand=True)
        tk.Label(
            title_box,
            text="Biblioteca",
            bg=self.TEXT,
            fg="white",
            font=("Helvetica", 24, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_box,
            text="CRUD de libros con Tkinter, validaciones, JSON y una interfaz más limpia.",
            bg=self.TEXT,
            fg="#CBD5E1",
            font=("Helvetica", 10),
        ).pack(anchor="w", pady=(4, 0))

        ttk.Button(banner, text="Guardar ahora", style="Primary.TButton", command=self._save).pack(side="right")

        stats = ttk.Frame(root, style="Root.TFrame")
        stats.pack(fill="x", pady=(16, 12))
        self._metric_total = self._metric_card(stats, "Libros", "0")
        self._metric_available = self._metric_card(stats, "Disponibles", "0")
        self._metric_loaned = self._metric_card(stats, "Prestados", "0")

        body = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body, style="Root.TFrame")
        right = ttk.Frame(body, style="Root.TFrame")
        body.add(left, weight=1)
        body.add(right, weight=3)

        self._build_left_panel(left)
        self._build_right_panel(right)

        self.status_var = tk.StringVar(value="")
        status = ttk.Label(root, textvariable=self.status_var, style="CardText.TLabel", anchor="w")
        status.pack(fill="x", pady=(12, 0))

    def _metric_card(self, parent: ttk.Frame, label: str, value: str) -> tk.Frame:
        card = tk.Frame(parent, bg=self.SURFACE, padx=16, pady=16, highlightbackground=self.BORDER, highlightthickness=1)
        card.pack(side="left", fill="x", expand=True, padx=(0, 12))
        if label == "Prestados":
            card.pack_configure(padx=0)

        tk.Label(card, text=label, bg=self.SURFACE, fg=self.MUTED, font=("Helvetica", 9, "bold")).pack(anchor="w")
        value_var = tk.StringVar(value=value)
        tk.Label(card, textvariable=value_var, bg=self.SURFACE, fg=self.TEXT, font=("Helvetica", 20, "bold")).pack(anchor="w", pady=(4, 0))
        if label == "Libros":
            self.var_metric_total = value_var
        elif label == "Disponibles":
            self.var_metric_available = value_var
        else:
            self.var_metric_loaned = value_var
        return card

    def _build_left_panel(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)

        form = ttk.LabelFrame(parent, text="Libro", style="Section.TLabelframe", padding=14)
        form.grid(row=0, column=0, sticky="ew")

        self.var_isbn = tk.StringVar()
        self.var_titulo = tk.StringVar()
        self.var_autor = tk.StringVar()
        self.var_anio = tk.StringVar()
        self.var_copias_total = tk.StringVar(value="1")

        self._field(form, 0, "ISBN", self.var_isbn, width=18)
        self._field(form, 1, "Título", self.var_titulo, width=26, span=3)
        self._field(form, 2, "Autor", self.var_autor, width=18)
        self._field(form, 3, "Año", self.var_anio, width=10)
        self._field(form, 4, "Copias", self.var_copias_total, width=10)

        actions = ttk.Frame(form, style="Card.TFrame")
        actions.grid(row=5, column=0, columnspan=4, sticky="ew", pady=(14, 0))
        ttk.Button(actions, text="Agregar", style="Primary.TButton", command=self._on_add).pack(side="left")
        ttk.Button(actions, text="Actualizar", style="Secondary.TButton", command=self._on_update).pack(side="left", padx=6)
        ttk.Button(actions, text="Eliminar", style="Danger.TButton", command=self._on_delete).pack(side="left", padx=6)
        ttk.Button(actions, text="Limpiar", style="Secondary.TButton", command=self._clear_form).pack(side="left", padx=6)
        ttk.Button(actions, text="Prestar", style="Success.TButton", command=self._on_loan).pack(side="left", padx=(14, 6))
        ttk.Button(actions, text="Devolver", style="Secondary.TButton", command=self._on_return).pack(side="left", padx=6)

        filters = ttk.LabelFrame(parent, text="Filtros", style="Section.TLabelframe", padding=14)
        filters.grid(row=1, column=0, sticky="ew", pady=(14, 0))

        self.var_buscar_isbn = tk.StringVar()
        self.var_buscar_titulo = tk.StringVar()
        self.var_buscar_autor = tk.StringVar()
        self.var_buscar_disponibles = tk.BooleanVar(value=False)

        self._field(filters, 0, "ISBN", self.var_buscar_isbn, width=18)
        self._field(filters, 1, "Título contiene", self.var_buscar_titulo, width=24, span=3)
        self._field(filters, 2, "Autor contiene", self.var_buscar_autor, width=24, span=3)
        ttk.Checkbutton(filters, text="Solo disponibles", variable=self.var_buscar_disponibles).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(6, 0)
        )

        filter_actions = ttk.Frame(filters, style="Card.TFrame")
        filter_actions.grid(row=4, column=0, columnspan=4, sticky="w", pady=(12, 0))
        ttk.Button(filter_actions, text="Buscar", style="Primary.TButton", command=self._on_search).pack(side="left")
        ttk.Button(filter_actions, text="Ver todo", style="Secondary.TButton", command=self._on_view_all).pack(side="left", padx=6)

        detail = ttk.LabelFrame(parent, text="Seleccionado", style="Section.TLabelframe", padding=14)
        detail.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        detail.columnconfigure(1, weight=1)

        self.var_selected_isbn = tk.StringVar(value="Ninguno")
        self.var_selected_titulo = tk.StringVar(value="Ninguno")
        self.var_selected_autor = tk.StringVar(value="Ninguno")
        self.var_selected_estado = tk.StringVar(value="Sin selección")

        self._detail_row(detail, 0, "ISBN", self.var_selected_isbn)
        self._detail_row(detail, 1, "Título", self.var_selected_titulo)
        self._detail_row(detail, 2, "Autor", self.var_selected_autor)
        self._detail_row(detail, 3, "Estado", self.var_selected_estado)

    def _build_right_panel(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        header = ttk.Frame(parent, style="Root.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(header, text="Catálogo", font=("Helvetica", 14, "bold"), background=self.BG).pack(side="left")
        ttk.Button(header, text="Guardar cambios", style="Primary.TButton", command=self._save).pack(side="right")

        table_box = ttk.Frame(parent, style="Card.TFrame", padding=12)
        table_box.grid(row=1, column=0, sticky="nsew")
        table_box.columnconfigure(0, weight=1)
        table_box.rowconfigure(0, weight=1)

        cols = ("isbn", "titulo", "autor", "anio", "total", "disp", "estado")
        self.tree = ttk.Treeview(table_box, columns=cols, show="headings", height=18)
        self.tree.heading("isbn", text="ISBN")
        self.tree.heading("titulo", text="Título")
        self.tree.heading("autor", text="Autor")
        self.tree.heading("anio", text="Año")
        self.tree.heading("total", text="Total")
        self.tree.heading("disp", text="Disp.")
        self.tree.heading("estado", text="Estado")

        self.tree.column("isbn", width=120, anchor="w")
        self.tree.column("titulo", width=360, anchor="w")
        self.tree.column("autor", width=240, anchor="w")
        self.tree.column("anio", width=70, anchor="center")
        self.tree.column("total", width=70, anchor="center")
        self.tree.column("disp", width=70, anchor="center")
        self.tree.column("estado", width=120, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self._on_select_row)

        yscroll = ttk.Scrollbar(table_box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=0, column=1, sticky="ns")

    def _field(
        self,
        parent: ttk.LabelFrame,
        row: int,
        label: str,
        variable: tk.StringVar,
        *,
        width: int,
        span: int = 1,
    ) -> None:
        column = 0 if row % 2 == 0 else 2
        label_widget = ttk.Label(parent, text=label)
        label_widget.grid(row=row, column=column, sticky="w", pady=(0, 6), padx=(0, 8))
        entry = ttk.Entry(parent, textvariable=variable, width=width)
        entry.grid(row=row, column=column + 1, sticky="ew", pady=(0, 6))
        if span > 1:
            parent.grid_columnconfigure(column + 1, weight=1)

    def _detail_row(self, parent: ttk.LabelFrame, row: int, label: str, variable: tk.StringVar) -> None:
        ttk.Label(parent, text=label, style="CardText.TLabel").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Label(parent, textvariable=variable, style="CardText.TLabel").grid(row=row, column=1, sticky="w", pady=2)

    def _validate_form(self) -> Libro:
        isbn = self.var_isbn.get().strip()
        titulo = self.var_titulo.get().strip()
        autor = self.var_autor.get().strip()

        try:
            anio = int(self.var_anio.get().strip())
        except ValueError as exc:
            raise ValidationError("Año debe ser numérico.") from exc

        try:
            copias_total = int(self.var_copias_total.get().strip())
        except ValueError as exc:
            raise ValidationError("Copias debe ser numérico.") from exc

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

        for index, libro in enumerate(rows):
            estado = "Disponible" if libro.disponible else "No disponible"
            tag = "even" if index % 2 == 0 else "odd"
            self.tree.insert(
                "",
                "end",
                iid=libro.isbn,
                values=(libro.isbn, libro.titulo, libro.autor, libro.anio, libro.copias_total, libro.copias_disponibles, estado),
                tags=(tag,),
            )

        self.tree.tag_configure("even", background="#F8FAFC")
        self.tree.tag_configure("odd", background="#FFFFFF")
        self._update_dashboard()

    def _update_dashboard(self) -> None:
        libros = self.biblioteca.repo.listar()
        total = len(libros)
        disponibles = sum(1 for libro in libros if libro.disponible)
        prestados = sum(libro.copias_total - libro.copias_disponibles for libro in libros)

        self.var_metric_total.set(str(total))
        self.var_metric_available.set(str(disponibles))
        self.var_metric_loaned.set(str(prestados))

        if self._selected_isbn:
            libro = self.biblioteca.repo.buscar_por_isbn(self._selected_isbn)
            if libro:
                self.var_selected_isbn.set(libro.isbn)
                self.var_selected_titulo.set(libro.titulo)
                self.var_selected_autor.set(libro.autor)
                estado = f"{libro.copias_disponibles}/{libro.copias_total} disponibles"
                self.var_selected_estado.set(estado)

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

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

        self.var_selected_isbn.set(libro.isbn)
        self.var_selected_titulo.set(libro.titulo)
        self.var_selected_autor.set(libro.autor)
        self.var_selected_estado.set(
            f"{libro.copias_disponibles}/{libro.copias_total} disponibles"
        )
        self._set_status(f"Libro seleccionado: {libro.isbn}")

    def _on_add(self) -> None:
        try:
            libro = self._validate_form()
            self.biblioteca.repo.agregar(libro)
            self._save(silent=True)
            self._refresh_table(self.biblioteca.repo.listar())
            self._selected_isbn = None
            self._clear_form()
            self._set_status(f"Libro agregado: {libro.isbn}")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _on_update(self) -> None:
        try:
            if not self._selected_isbn:
                raise ValidationError("Selecciona un libro de la tabla para actualizar.")

            nuevo = self._validate_form()
            self.biblioteca.repo.actualizar(self._selected_isbn, nuevo)
            self._save(silent=True)
            self._refresh_table(self.biblioteca.repo.listar())
            self._selected_isbn = nuevo.isbn
            self._set_status(f"Libro actualizado: {nuevo.isbn}")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

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
            self._set_status("Libro eliminado.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _on_loan(self) -> None:
        try:
            if not self._selected_isbn:
                raise ValidationError("Selecciona un libro para prestar.")

            self.biblioteca.repo.prestar(self._selected_isbn)
            self._save(silent=True)
            self._refresh_table(self.biblioteca.repo.listar())
            self._set_status("Préstamo registrado.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _on_return(self) -> None:
        try:
            if not self._selected_isbn:
                raise ValidationError("Selecciona un libro para devolver.")

            self.biblioteca.repo.devolver(self._selected_isbn)
            self._save(silent=True)
            self._refresh_table(self.biblioteca.repo.listar())
            self._set_status("Devolución registrada.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _on_search(self) -> None:
        rows = self.biblioteca.repo.buscar(
            isbn=self.var_buscar_isbn.get(),
            titulo=self.var_buscar_titulo.get(),
            autor=self.var_buscar_autor.get(),
            solo_disponibles=bool(self.var_buscar_disponibles.get()),
        )
        self._refresh_table(rows)
        self._set_status(f"Resultados encontrados: {len(rows)}")

    def _on_view_all(self) -> None:
        self.var_buscar_isbn.set("")
        self.var_buscar_titulo.set("")
        self.var_buscar_autor.set("")
        self.var_buscar_disponibles.set(False)
        self._refresh_table(self.biblioteca.repo.listar())
        self._set_status("Filtros limpiados.")

    def _clear_form(self) -> None:
        self.var_isbn.set("")
        self.var_titulo.set("")
        self.var_autor.set("")
        self.var_anio.set("")
        self.var_copias_total.set("1")
        self._selected_isbn = None
        self.var_selected_isbn.set("Ninguno")
        self.var_selected_titulo.set("Ninguno")
        self.var_selected_autor.set("Ninguno")
        self.var_selected_estado.set("Sin selección")
        self._set_status("Formulario limpio.")

    def _save(self, silent: bool = False) -> None:
        self.biblioteca.save()
        if not silent:
            messagebox.showinfo("Guardado", "Los cambios se guardaron en projects/biblioteca/data/libros.json.")
        self._update_dashboard()


def main() -> int:
    BibliotecaApp().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
