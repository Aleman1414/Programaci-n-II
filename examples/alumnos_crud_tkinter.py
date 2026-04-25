from __future__ import annotations

import json
import tkinter as tk
from dataclasses import asdict, dataclass
from pathlib import Path
from tkinter import messagebox, ttk


@dataclass
class Alumno:
    cuenta: str
    nombre: str
    correo: str = ""


class RepositorioAlumnos:
    def __init__(self) -> None:
        self._items: list[Alumno] = []

    def listar(self) -> list[Alumno]:
        return list(self._items)

    def buscar_por_cuenta(self, cuenta: str) -> Alumno | None:
        return next((a for a in self._items if a.cuenta == cuenta), None)

    def buscar_por_nombre(self, texto: str) -> list[Alumno]:
        texto = texto.strip().lower()
        if not texto:
            return self.listar()
        return [a for a in self._items if texto in a.nombre.lower()]

    def agregar(self, alumno: Alumno) -> None:
        if self.buscar_por_cuenta(alumno.cuenta) is not None:
            raise ValueError("La cuenta ya existe.")
        self._items.append(alumno)

    def actualizar(self, cuenta: str, nuevo: Alumno) -> None:
        actual = self.buscar_por_cuenta(cuenta)
        if actual is None:
            raise ValueError("No existe el alumno.")
        if nuevo.cuenta != cuenta and self.buscar_por_cuenta(nuevo.cuenta) is not None:
            raise ValueError("La nueva cuenta ya existe.")
        actual.cuenta = nuevo.cuenta
        actual.nombre = nuevo.nombre
        actual.correo = nuevo.correo

    def eliminar(self, cuenta: str) -> None:
        before = len(self._items)
        self._items = [a for a in self._items if a.cuenta != cuenta]
        if len(self._items) == before:
            raise ValueError("No existe el alumno.")

    def cargar_json(self, path: Path) -> None:
        if not path.exists():
            self._items = []
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        self._items = [Alumno(**d) for d in data]

    def guardar_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(a) for a in self._items]
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CRUD de Alumnos (POO + Tkinter)")
        self.geometry("920x560")

        self.data_path = Path("data/alumnos.json")
        self.repo = RepositorioAlumnos()
        self.repo.cargar_json(self.data_path)

        self._selected_cuenta: str | None = None

        self._build_ui()
        self._refresh_table(self.repo.listar())

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        header = ttk.Frame(root)
        header.pack(fill="x")
        ttk.Label(header, text="Alumnos", font=("TkDefaultFont", 14, "bold")).pack(side="left")

        # Form
        form = ttk.LabelFrame(root, text="Formulario", padding=10)
        form.pack(fill="x", pady=(12, 10))

        self.var_cuenta = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_correo = tk.StringVar()

        ttk.Label(form, text="Cuenta").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_cuenta, width=18).grid(row=0, column=1, sticky="w", padx=(8, 16))
        ttk.Label(form, text="Nombre").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.var_nombre, width=40).grid(row=0, column=3, sticky="we", padx=(8, 16))
        ttk.Label(form, text="Correo").grid(row=0, column=4, sticky="w")
        ttk.Entry(form, textvariable=self.var_correo, width=30).grid(row=0, column=5, sticky="we", padx=(8, 0))

        form.grid_columnconfigure(3, weight=1)
        form.grid_columnconfigure(5, weight=1)

        actions = ttk.Frame(form)
        actions.grid(row=1, column=0, columnspan=6, sticky="w", pady=(10, 0))
        ttk.Button(actions, text="Agregar", command=self._on_add).pack(side="left")
        ttk.Button(actions, text="Actualizar", command=self._on_update).pack(side="left", padx=6)
        ttk.Button(actions, text="Eliminar", command=self._on_delete).pack(side="left", padx=6)
        ttk.Button(actions, text="Limpiar", command=self._clear_form).pack(side="left", padx=6)

        # Search
        search = ttk.LabelFrame(root, text="Búsqueda", padding=10)
        search.pack(fill="x", pady=(0, 10))
        self.var_buscar = tk.StringVar()
        ttk.Label(search, text="Nombre contiene").pack(side="left")
        ttk.Entry(search, textvariable=self.var_buscar, width=40).pack(side="left", padx=8)
        ttk.Button(search, text="Buscar", command=self._on_search).pack(side="left")
        ttk.Button(search, text="Ver todo", command=self._on_view_all).pack(side="left", padx=6)

        # Table
        table_box = ttk.Frame(root)
        table_box.pack(fill="both", expand=True)
        cols = ("cuenta", "nombre", "correo")
        self.tree = ttk.Treeview(table_box, columns=cols, show="headings", height=12)
        self.tree.heading("cuenta", text="Cuenta")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("correo", text="Correo")
        self.tree.column("cuenta", width=120, anchor="w")
        self.tree.column("nombre", width=340, anchor="w")
        self.tree.column("correo", width=260, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select_row)

        yscroll = ttk.Scrollbar(table_box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side="left", fill="y")

        footer = ttk.Frame(root)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Button(footer, text="Guardar a JSON", command=self._save).pack(side="left")
        ttk.Label(footer, text="Archivo: data/alumnos.json").pack(side="left", padx=10)

    def _validate_form(self) -> Alumno:
        cuenta = self.var_cuenta.get().strip()
        nombre = self.var_nombre.get().strip()
        correo = self.var_correo.get().strip()

        if not cuenta or not nombre:
            raise ValueError("Cuenta y Nombre son obligatorios.")
        if not cuenta.isdigit():
            raise ValueError("La cuenta debe ser numérica.")
        if correo and ("@" not in correo or "." not in correo):
            raise ValueError("Correo inválido (validación básica).")
        return Alumno(cuenta=cuenta, nombre=nombre, correo=correo)

    def _refresh_table(self, rows: list[Alumno]) -> None:
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for a in rows:
            self.tree.insert("", "end", iid=a.cuenta, values=(a.cuenta, a.nombre, a.correo))

    def _on_select_row(self, _evt: object) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        cuenta = str(sel[0])
        alumno = self.repo.buscar_por_cuenta(cuenta)
        if alumno is None:
            return
        self._selected_cuenta = cuenta
        self.var_cuenta.set(alumno.cuenta)
        self.var_nombre.set(alumno.nombre)
        self.var_correo.set(alumno.correo)

    def _on_add(self) -> None:
        try:
            alumno = self._validate_form()
            self.repo.agregar(alumno)
            self._save(silent=True)
            self._refresh_table(self.repo.listar())
            self._selected_cuenta = None
            self._clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_update(self) -> None:
        try:
            if not self._selected_cuenta:
                raise ValueError("Selecciona un alumno de la tabla para actualizar.")
            alumno = self._validate_form()
            self.repo.actualizar(self._selected_cuenta, alumno)
            self._save(silent=True)
            self._refresh_table(self.repo.listar())
            self._selected_cuenta = alumno.cuenta
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_delete(self) -> None:
        try:
            if not self._selected_cuenta:
                raise ValueError("Selecciona un alumno de la tabla para eliminar.")
            if not messagebox.askyesno("Confirmar", f"¿Eliminar cuenta {self._selected_cuenta}?"):
                return
            self.repo.eliminar(self._selected_cuenta)
            self._save(silent=True)
            self._refresh_table(self.repo.listar())
            self._selected_cuenta = None
            self._clear_form()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_search(self) -> None:
        rows = self.repo.buscar_por_nombre(self.var_buscar.get())
        self._refresh_table(rows)

    def _on_view_all(self) -> None:
        self.var_buscar.set("")
        self._refresh_table(self.repo.listar())

    def _clear_form(self) -> None:
        self.var_cuenta.set("")
        self.var_nombre.set("")
        self.var_correo.set("")

    def _save(self, silent: bool = False) -> None:
        self.repo.guardar_json(self.data_path)
        if not silent:
            messagebox.showinfo("OK", "Guardado en data/alumnos.json")


def main() -> int:
    App().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

