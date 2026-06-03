from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText

if __package__ in {None, ""}:
    pkg_root = Path(__file__).resolve().parent.parent
    if str(pkg_root) not in sys.path:
        sys.path.insert(0, str(pkg_root))
    from pyii_tutor.content import Curriculum, Lesson, load_curriculum, lesson_exercises_text, lesson_topics_text
    from pyii_tutor.runner import run_code
else:
    from .content import Curriculum, Lesson, load_curriculum, lesson_exercises_text, lesson_topics_text
    from .runner import run_code


class TutorApp:
    BG = "#F5F7FB"
    SURFACE = "#FFFFFF"
    SURFACE_ALT = "#E2E8F0"
    TEXT = "#0F172A"
    MUTED = "#475569"
    BORDER = "#D6DEEA"
    ACCENT = "#2563EB"
    ACCENT_HOVER = "#1D4ED8"
    ACCENT_SOFT = "#DBEAFE"
    CODE_BG = "#0F172A"
    CODE_FG = "#E2E8F0"

    def __init__(self) -> None:
        self.curriculum: Curriculum = load_curriculum()
        self.root = tk.Tk()
        self.root.title(self.curriculum.course.name)
        self.root.geometry("1120x720")
        self.root.minsize(1080, 700)
        self.root.configure(bg=self.BG)

        self._selected_lesson: Lesson | None = None
        self._selected_example_index: int | None = None
        self._quiz_index = 0
        self._quiz_score = 0
        self._quiz_answer_var = tk.IntVar(value=-1)

        self._configure_style()
        self._build_ui()
        if self.curriculum.lessons:
            self.lesson_list.selection_clear(0, "end")
            self.lesson_list.selection_set(0)
            self.lesson_list.activate(0)
            self.lesson_list.see(0)
            self._select_lesson(self.curriculum.lessons[0])

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=self.BG)
        style.configure("TLabel", background=self.BG, foreground=self.TEXT)
        style.configure("Header.TLabel", font="Segoe UI 18 bold", foreground=self.TEXT, background=self.BG)
        style.configure("SubHeader.TLabel", font="Segoe UI 11", foreground=self.MUTED, background=self.BG)
        style.configure("Card.TFrame", background=self.SURFACE)
        style.configure("Card.TLabelframe", background=self.SURFACE, foreground=self.TEXT, font="Segoe UI 10 bold")
        style.configure("Card.TLabelframe.Label", background=self.SURFACE, foreground=self.TEXT)
        style.configure("Accent.TButton", font="Segoe UI 10 bold", foreground="white", background=self.ACCENT)
        style.map(
            "Accent.TButton",
            background=[("active", self.ACCENT_HOVER), ("pressed", self.ACCENT_HOVER)],
            foreground=[("disabled", "#CBD5E1")],
        )
        style.configure("TNotebook", background=self.BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=self.SURFACE_ALT,
            foreground=self.TEXT,
            padding=[14, 10],
            font="Segoe UI 10 bold",
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.ACCENT), ("active", self.ACCENT_SOFT)],
            foreground=[("selected", "#ffffff"), ("active", self.TEXT)],
        )
        style.configure(
            "Treeview",
            background=self.SURFACE,
            fieldbackground=self.SURFACE,
            foreground=self.TEXT,
            rowheight=28,
            bordercolor=self.BORDER,
            borderwidth=0,
        )
        style.map(
            "Treeview",
            background=[("selected", self.ACCENT_SOFT)],
            foreground=[("selected", self.TEXT)],
        )
        style.configure(
            "Treeview.Heading",
            background=self.SURFACE_ALT,
            foreground=self.TEXT,
            relief="flat",
            font="Segoe UI 10 bold",
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "#CBD5E1")],
        )
        style.configure("TScrollbar", background=self.SURFACE_ALT, troughcolor=self.BG, arrowcolor=self.TEXT)

    def run(self) -> None:
        self.root.mainloop()

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=12, style="TFrame")
        top.pack(fill="both", expand=True)

        header = ttk.Frame(top, style="TFrame")
        header.pack(fill="x", pady=(0, 12))
        title = ttk.Label(header, text=self.curriculum.course.name, style="Header.TLabel")
        title.pack(side="left")
        if self.curriculum.course.subtitle:
            subtitle = ttk.Label(header, text=self.curriculum.course.subtitle, style="SubHeader.TLabel")
            subtitle.pack(side="left", padx=16, pady=6)

        main = ttk.PanedWindow(top, orient="horizontal")
        main.pack(fill="both", expand=True)

        # Left: lessons list
        left = ttk.Frame(main, style="TFrame", padding=(0, 0, 10, 0))
        main.add(left, weight=1)

        lesson_panel = ttk.LabelFrame(left, text="Semanas", style="Card.TLabelframe", padding=10)
        lesson_panel.pack(fill="both", expand=True)

        lesson_list_container = ttk.Frame(lesson_panel, style="Card.TFrame")
        lesson_list_container.pack(fill="both", expand=True)

        self.lesson_list = tk.Listbox(
            lesson_list_container,
            activestyle="dotbox",
            height=28,
            bg=self.SURFACE,
            fg=self.TEXT,
            selectbackground=self.ACCENT_SOFT,
            selectforeground=self.TEXT,
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        lesson_scroll = ttk.Scrollbar(lesson_list_container, orient="vertical", command=self.lesson_list.yview)
        self.lesson_list.configure(yscrollcommand=lesson_scroll.set)
        self.lesson_list.pack(side="left", fill="both", expand=True)
        lesson_scroll.pack(side="right", fill="y")

        for lesson in self.curriculum.lessons:
            self.lesson_list.insert("end", f"Semana {lesson.week:02d} — {lesson.title}")
        self.lesson_list.bind("<<ListboxSelect>>", self._on_lesson_select)

        # Right: tabs
        right = ttk.Frame(main, style="TFrame")
        main.add(right, weight=3)

        right_header = ttk.Frame(right, style="TFrame")
        right_header.pack(fill="x", pady=(0, 10))

        self.lesson_info = ttk.Frame(right_header, style="Card.TFrame", padding=14)
        self.lesson_info.pack(fill="x")
        self.lesson_title = ttk.Label(self.lesson_info, text="Selecciona una semana", style="Header.TLabel")
        self.lesson_title.pack(anchor="w")
        self.lesson_meta = ttk.Label(self.lesson_info, text="Explora la teoría, ejemplos y ejercicios disponibles.", style="SubHeader.TLabel")
        self.lesson_meta.pack(anchor="w", pady=(4, 0))

        self.tabs = ttk.Notebook(right)
        self.tabs.pack(fill="both", expand=True)

        self.tab_theory = ttk.Frame(self.tabs, padding=10, style="Card.TFrame")
        self.tab_examples = ttk.Frame(self.tabs, padding=10, style="Card.TFrame")
        self.tab_exercises = ttk.Frame(self.tabs, padding=10, style="Card.TFrame")
        self.tab_quiz = ttk.Frame(self.tabs, padding=10, style="Card.TFrame")
        self.tab_glossary = ttk.Frame(self.tabs, padding=10, style="Card.TFrame")

        self.tabs.add(self.tab_theory, text="Teoría")
        self.tabs.add(self.tab_examples, text="Ejemplos")
        self.tabs.add(self.tab_exercises, text="Ejercicios")
        self.tabs.add(self.tab_quiz, text="Quiz")
        self.tabs.add(self.tab_glossary, text="Java → Python")

        self._build_theory_tab()
        self._build_examples_tab()
        self._build_exercises_tab()
        self._build_quiz_tab()
        self._build_glossary_tab()

        status_bar = ttk.Frame(self.root, style="Card.TFrame", padding=(10, 6))
        status_bar.pack(fill="x")
        self.status_label = ttk.Label(status_bar, text="Interfaz mejorada — selecciona una semana para comenzar.", style="SubHeader.TLabel")
        self.status_label.pack(side="left")

    def _build_theory_tab(self) -> None:
        self.theory_text = ScrolledText(
            self.tab_theory,
            wrap="word",
            font=("Segoe UI", 11),
            background=self.SURFACE,
            foreground=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=12,
        )
        self.theory_text.pack(fill="both", expand=True)
        self.theory_text.configure(state="disabled")

    def _build_examples_tab(self) -> None:
        container = ttk.Frame(self.tab_examples, style="TFrame")
        container.pack(fill="both", expand=True)

        left = ttk.Frame(container, style="TFrame")
        left.pack(side="left", fill="y", padx=(0, 10), pady=(0, 2))
        examples_card = ttk.LabelFrame(left, text="Ejemplos", style="Card.TLabelframe", padding=10)
        examples_card.pack(fill="both", expand=True)

        list_container = ttk.Frame(examples_card, style="Card.TFrame")
        list_container.pack(fill="both", expand=True)
        self.examples_list = tk.Listbox(
            list_container,
            activestyle="dotbox",
            height=18,
            bg=self.SURFACE,
            fg=self.TEXT,
            selectbackground=self.ACCENT_SOFT,
            selectforeground=self.TEXT,
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        example_scroll = ttk.Scrollbar(list_container, orient="vertical", command=self.examples_list.yview)
        self.examples_list.configure(yscrollcommand=example_scroll.set)
        self.examples_list.pack(side="left", fill="both", expand=True)
        example_scroll.pack(side="right", fill="y")
        self.examples_list.bind("<<ListboxSelect>>", self._on_example_select)

        right = ttk.Frame(container, style="TFrame")
        right.pack(side="left", fill="both", expand=True)

        self.example_title = ttk.Label(right, text="Selecciona un ejemplo", style="Header.TLabel")
        self.example_title.pack(anchor="w")

        code_card = ttk.LabelFrame(right, text="Código", style="Card.TLabelframe", padding=10)
        code_card.pack(fill="both", expand=True, pady=(10, 0))
        self.code_text = ScrolledText(
            code_card,
            wrap="none",
            font=("Consolas", 11),
            background=self.CODE_BG,
            foreground=self.CODE_FG,
            insertbackground="#ffffff",
            relief="flat",
            borderwidth=0,
            height=14,
        )
        self.code_text.pack(fill="both", expand=True)

        actions = ttk.Frame(right, style="TFrame")
        actions.pack(fill="x", pady=(10, 0))
        self.run_button = ttk.Button(actions, text="Ejecutar", command=self._run_current_code, style="Accent.TButton")
        self.run_button.pack(side="left")
        ttk.Button(actions, text="Copiar", command=self._copy_current_code, style="Accent.TButton").pack(side="left", padx=8)
        ttk.Button(actions, text="Limpiar salida", command=self._clear_output, style="Accent.TButton").pack(side="left")

        output_card = ttk.LabelFrame(right, text="Salida", style="Card.TLabelframe", padding=10)
        output_card.pack(fill="both", expand=False, pady=(10, 0))
        self.output_text = ScrolledText(
            output_card,
            wrap="word",
            height=8,
            font=("Consolas", 11),
            background=self.SURFACE,
            foreground=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            borderwidth=0,
        )
        self.output_text.pack(fill="both", expand=True)

    def _build_exercises_tab(self) -> None:
        exercises_card = ttk.LabelFrame(self.tab_exercises, text="Ejercicios", style="Card.TLabelframe", padding=12)
        exercises_card.pack(fill="both", expand=True)
        self.exercises_text = ScrolledText(
            exercises_card,
            wrap="word",
            font=("Segoe UI", 11),
            background=self.SURFACE,
            foreground=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=12,
        )
        self.exercises_text.pack(fill="both", expand=True)
        self.exercises_text.configure(state="disabled")

    def _build_quiz_tab(self) -> None:
        quiz_card = ttk.LabelFrame(self.tab_quiz, text="Quiz", style="Card.TLabelframe", padding=12)
        quiz_card.pack(fill="both", expand=True)

        self.quiz_question = ttk.Label(quiz_card, text="Selecciona una semana con quiz.", wraplength=820, style="SubHeader.TLabel")
        self.quiz_question.pack(anchor="w", pady=(0, 12))

        self.quiz_options_frame = ttk.Frame(quiz_card, style="TFrame")
        self.quiz_options_frame.pack(fill="x", pady=(0, 12))

        self.quiz_feedback = ttk.Label(quiz_card, text="", wraplength=820, style="SubHeader.TLabel")
        self.quiz_feedback.pack(anchor="w", pady=(0, 12))

        controls = ttk.Frame(quiz_card, style="TFrame")
        controls.pack(anchor="w", pady=(0, 12))
        self.quiz_submit_btn = ttk.Button(controls, text="Responder", command=self._quiz_submit, style="Accent.TButton")
        self.quiz_next_btn = ttk.Button(controls, text="Siguiente", command=self._quiz_next, style="Accent.TButton")
        self.quiz_reset_btn = ttk.Button(controls, text="Reiniciar", command=self._quiz_reset, style="Accent.TButton")
        self.quiz_submit_btn.pack(side="left")
        self.quiz_next_btn.pack(side="left", padx=8)
        self.quiz_reset_btn.pack(side="left", padx=8)

        self.quiz_progress = ttk.Label(quiz_card, text="", style="SubHeader.TLabel")
        self.quiz_progress.pack(anchor="w")

    def _build_glossary_tab(self) -> None:
        glossary_card = ttk.LabelFrame(self.tab_glossary, text="Glosario rápido (Java → Python)", style="Card.TLabelframe", padding=12)
        glossary_card.pack(fill="both", expand=True)
        self.glossary_text = ScrolledText(
            glossary_card,
            wrap="word",
            font=("Segoe UI", 11),
            background=self.SURFACE,
            foreground=self.TEXT,
            insertbackground=self.TEXT,
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=12,
        )
        self.glossary_text.pack(fill="both", expand=True)
        self.glossary_text.configure(state="disabled")

        lines = ["Glosario rápido (Java → Python)\n"]
        for item in self.curriculum.glossary:
            if item.java and item.python:
                lines.append(f"• {item.java}  →  {item.python}")
        self._set_text(self.glossary_text, "\n".join(lines))

    def _on_lesson_select(self, _evt: object) -> None:
        sel = self.lesson_list.curselection()
        if not sel:
            return
        idx = int(sel[0])
        if 0 <= idx < len(self.curriculum.lessons):
            self._select_lesson(self.curriculum.lessons[idx])

    def _select_lesson(self, lesson: Lesson) -> None:
        self._selected_lesson = lesson
        self._selected_example_index = None
        self.lesson_title.configure(text=f"Semana {lesson.week:02d} — {lesson.title}")
        example_count = len(lesson.examples)
        quiz_count = len(lesson.quiz)
        self.lesson_meta.configure(
            text=f"{len(lesson.topics)} temas · {example_count} ejemplos · {quiz_count} preguntas de quiz"
        )
        self.status_label.configure(text=f"Semana {lesson.week:02d} seleccionada — Abre una pestaña para ver la teoría, ejercicios y ejemplos.")

        theory = []
        if self.curriculum.course.note:
            theory.append(self.curriculum.course.note)
            theory.append("")
        if lesson_topics_text(lesson):
            theory.append(lesson_topics_text(lesson))
            theory.append("")
        theory.append(lesson.theory.strip() or "Sin teoría aún para esta semana.")
        self._set_text(self.theory_text, "\n".join(theory).strip())

        self._set_text(self.exercises_text, lesson_exercises_text(lesson))
        self._load_examples(lesson)
        self._quiz_reset()

    def _load_examples(self, lesson: Lesson) -> None:
        self.examples_list.delete(0, "end")
        self.example_title.configure(text="Ejemplos")
        self.code_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        for ex in lesson.examples:
            self.examples_list.insert("end", ex.title)
        if lesson.examples:
            self.examples_list.selection_clear(0, "end")
            self.examples_list.selection_set(0)
            self.examples_list.activate(0)
            self.examples_list.see(0)
            self._show_example(0)
        else:
            self.example_title.configure(text="Sin ejemplos disponibles")
            self.run_button.configure(state="disabled")

    def _on_example_select(self, _evt: object) -> None:
        if not self._selected_lesson:
            return
        sel = self.examples_list.curselection()
        if not sel:
            return
        idx = int(sel[0])
        self._show_example(idx)

    def _show_example(self, idx: int) -> None:
        if not self._selected_lesson:
            return
        if not (0 <= idx < len(self._selected_lesson.examples)):
            return
        ex = self._selected_lesson.examples[idx]
        self._selected_example_index = idx
        self.example_title.configure(text=ex.title)
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", ex.code)
        self.output_text.delete("1.0", "end")
        self.run_button.configure(state=("normal" if ex.runnable else "disabled"))

    def _run_current_code(self) -> None:
        code = self.code_text.get("1.0", "end").strip("\n")
        if not code.strip():
            self.status_label.configure(text="No hay código para ejecutar.")
            return
        res = run_code(code)
        out = []
        if res.timeout:
            out.append("[Tiempo excedido]\n")
        if res.stdout:
            out.append(res.stdout)
        if res.stderr:
            out.append("\n[stderr]\n" + res.stderr)
        if not out:
            out.append("(sin salida)")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", "".join(out))
        self.status_label.configure(text="Ejecución completada.")

    def _copy_current_code(self) -> None:
        code = self.code_text.get("1.0", "end").strip("\n")
        if not code.strip():
            self.status_label.configure(text="No hay código para copiar.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        self.root.update()
        self.status_label.configure(text="Código copiado al portapapeles.")

    def _clear_output(self) -> None:
        self.output_text.delete("1.0", "end")
        self.status_label.configure(text="Salida limpiada.")

    def _set_text(self, widget: tk.Text, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def _quiz_reset(self) -> None:
        self._quiz_index = 0
        self._quiz_score = 0
        self._quiz_answer_var.set(-1)
        self.quiz_feedback.configure(text="")
        self._render_quiz_item()

    def _render_quiz_item(self) -> None:
        lesson = self._selected_lesson
        if not lesson or not lesson.quiz:
            self.quiz_question.configure(text="Esta semana no tiene quiz aún.")
            self.quiz_progress.configure(text="")
            for child in list(self.quiz_options_frame.children.values()):
                child.destroy()
            self.quiz_submit_btn.configure(state="disabled")
            self.quiz_next_btn.configure(state="disabled")
            return

        item = lesson.quiz[self._quiz_index]
        self.quiz_question.configure(text=item.q)
        for child in list(self.quiz_options_frame.children.values()):
            child.destroy()

        self._quiz_answer_var.set(-1)
        for i, opt in enumerate(item.options):
            rb = ttk.Radiobutton(
                self.quiz_options_frame,
                text=opt,
                value=i,
                variable=self._quiz_answer_var,
            )
            rb.pack(anchor="w", pady=2)

        self.quiz_submit_btn.configure(state="normal")
        self.quiz_next_btn.configure(state=("normal" if len(lesson.quiz) > 1 else "disabled"))
        self.quiz_progress.configure(text=f"Pregunta {self._quiz_index + 1}/{len(lesson.quiz)} — Puntos: {self._quiz_score}")

    def _quiz_submit(self) -> None:
        lesson = self._selected_lesson
        if not lesson or not lesson.quiz:
            return
        item = lesson.quiz[self._quiz_index]
        selected = int(self._quiz_answer_var.get())
        if selected < 0:
            messagebox.showinfo("Quiz", "Selecciona una opción.")
            return
        ok = selected == item.answer
        if ok:
            self._quiz_score += 1
            msg = "Correcto."
        else:
            correct = item.options[item.answer] if 0 <= item.answer < len(item.options) else "(desconocida)"
            msg = f"Incorrecto. Respuesta correcta: {correct}"
        if item.explanation:
            msg += "\n\n" + item.explanation
        self.quiz_feedback.configure(text=msg)
        self.quiz_progress.configure(text=f"Pregunta {self._quiz_index + 1}/{len(lesson.quiz)} — Puntos: {self._quiz_score}")
        self.quiz_submit_btn.configure(state="disabled")

    def _quiz_next(self) -> None:
        lesson = self._selected_lesson
        if not lesson or not lesson.quiz:
            return
        if self._quiz_index + 1 >= len(lesson.quiz):
            messagebox.showinfo("Quiz", f"Fin del quiz. Puntos: {self._quiz_score}/{len(lesson.quiz)}")
            return
        self._quiz_index += 1
        self.quiz_feedback.configure(text="")
        self.quiz_submit_btn.configure(state="normal")
        self._render_quiz_item()
