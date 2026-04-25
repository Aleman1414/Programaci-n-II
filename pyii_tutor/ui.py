from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .content import Curriculum, Lesson, load_curriculum, lesson_exercises_text, lesson_topics_text
from .runner import run_code


class TutorApp:
    def __init__(self) -> None:
        self.curriculum: Curriculum = load_curriculum()
        self.root = tk.Tk()
        self.root.title(self.curriculum.course.name)
        self.root.geometry("1120x720")

        self._selected_lesson: Lesson | None = None
        self._quiz_index = 0
        self._quiz_score = 0
        self._quiz_answer_var = tk.IntVar(value=-1)

        self._build_ui()
        if self.curriculum.lessons:
            self.lesson_list.selection_clear(0, "end")
            self.lesson_list.selection_set(0)
            self.lesson_list.activate(0)
            self.lesson_list.see(0)
            self._select_lesson(self.curriculum.lessons[0])

    def run(self) -> None:
        self.root.mainloop()

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="both", expand=True)

        header = ttk.Frame(top)
        header.pack(fill="x")
        title = ttk.Label(header, text=self.curriculum.course.name, font=("TkDefaultFont", 16, "bold"))
        title.pack(side="left")
        if self.curriculum.course.subtitle:
            subtitle = ttk.Label(header, text=self.curriculum.course.subtitle)
            subtitle.pack(side="left", padx=12)

        main = ttk.PanedWindow(top, orient="horizontal")
        main.pack(fill="both", expand=True, pady=(10, 0))

        # Left: lessons list
        left = ttk.Frame(main, padding=(0, 0, 10, 0))
        main.add(left, weight=1)

        ttk.Label(left, text="Semanas").pack(anchor="w")
        self.lesson_list = tk.Listbox(left, activestyle="dotbox", height=24)
        self.lesson_list.pack(fill="both", expand=True, pady=(6, 0))
        for lesson in self.curriculum.lessons:
            self.lesson_list.insert("end", f"Semana {lesson.week:02d} — {lesson.title}")
        self.lesson_list.bind("<<ListboxSelect>>", self._on_lesson_select)

        # Right: tabs
        right = ttk.Frame(main)
        main.add(right, weight=3)

        self.tabs = ttk.Notebook(right)
        self.tabs.pack(fill="both", expand=True)

        self.tab_theory = ttk.Frame(self.tabs, padding=10)
        self.tab_examples = ttk.Frame(self.tabs, padding=10)
        self.tab_exercises = ttk.Frame(self.tabs, padding=10)
        self.tab_quiz = ttk.Frame(self.tabs, padding=10)
        self.tab_glossary = ttk.Frame(self.tabs, padding=10)

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

    def _build_theory_tab(self) -> None:
        self.theory_text = tk.Text(self.tab_theory, wrap="word", height=10)
        self.theory_text.pack(fill="both", expand=True)
        self.theory_text.configure(state="disabled")

    def _build_examples_tab(self) -> None:
        container = ttk.Frame(self.tab_examples)
        container.pack(fill="both", expand=True)

        left = ttk.Frame(container)
        left.pack(side="left", fill="y")
        ttk.Label(left, text="Ejemplos").pack(anchor="w")
        self.examples_list = tk.Listbox(left, height=18, width=36)
        self.examples_list.pack(fill="y", expand=False, pady=(6, 0))
        self.examples_list.bind("<<ListboxSelect>>", self._on_example_select)

        right = ttk.Frame(container)
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self.example_title = ttk.Label(right, text="Selecciona un ejemplo", font=("TkDefaultFont", 12, "bold"))
        self.example_title.pack(anchor="w")

        self.code_text = tk.Text(right, wrap="none", height=14, font=("TkFixedFont", 10))
        self.code_text.pack(fill="both", expand=True, pady=(6, 6))

        actions = ttk.Frame(right)
        actions.pack(fill="x")
        self.run_button = ttk.Button(actions, text="Ejecutar", command=self._run_current_code)
        self.run_button.pack(side="left")
        ttk.Button(actions, text="Copiar", command=self._copy_current_code).pack(side="left", padx=6)

        ttk.Label(right, text="Salida").pack(anchor="w", pady=(10, 0))
        self.output_text = tk.Text(right, wrap="word", height=8, font=("TkFixedFont", 10))
        self.output_text.pack(fill="x", expand=False, pady=(6, 0))

    def _build_exercises_tab(self) -> None:
        self.exercises_text = tk.Text(self.tab_exercises, wrap="word")
        self.exercises_text.pack(fill="both", expand=True)
        self.exercises_text.configure(state="disabled")

    def _build_quiz_tab(self) -> None:
        self.quiz_title = ttk.Label(self.tab_quiz, text="Quiz", font=("TkDefaultFont", 12, "bold"))
        self.quiz_title.pack(anchor="w")

        self.quiz_question = ttk.Label(self.tab_quiz, text="Selecciona una semana con quiz.", wraplength=860)
        self.quiz_question.pack(anchor="w", pady=(10, 6))

        self.quiz_options_frame = ttk.Frame(self.tab_quiz)
        self.quiz_options_frame.pack(fill="x")

        self.quiz_feedback = ttk.Label(self.tab_quiz, text="", wraplength=860)
        self.quiz_feedback.pack(anchor="w", pady=(10, 6))

        controls = ttk.Frame(self.tab_quiz)
        controls.pack(anchor="w", pady=(10, 0))
        self.quiz_submit_btn = ttk.Button(controls, text="Responder", command=self._quiz_submit)
        self.quiz_next_btn = ttk.Button(controls, text="Siguiente", command=self._quiz_next)
        self.quiz_reset_btn = ttk.Button(controls, text="Reiniciar", command=self._quiz_reset)
        self.quiz_submit_btn.pack(side="left")
        self.quiz_next_btn.pack(side="left", padx=6)
        self.quiz_reset_btn.pack(side="left", padx=6)

        self.quiz_progress = ttk.Label(self.tab_quiz, text="")
        self.quiz_progress.pack(anchor="w", pady=(10, 0))

    def _build_glossary_tab(self) -> None:
        self.glossary_text = tk.Text(self.tab_glossary, wrap="word")
        self.glossary_text.pack(fill="both", expand=True)
        self.glossary_text.configure(state="disabled")

        lines = ["Glosario rápido (Java → Python)\n"]
        for item in self.curriculum.glossary:
            if item.java and item.python:
                lines.append(f"- {item.java}  →  {item.python}")
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
        for ex in lesson.examples:
            self.examples_list.insert("end", ex.title)
        self.example_title.configure(text="Selecciona un ejemplo")
        self.code_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.run_button.configure(state=("normal" if lesson.examples else "disabled"))

    def _on_example_select(self, _evt: object) -> None:
        if not self._selected_lesson:
            return
        sel = self.examples_list.curselection()
        if not sel:
            return
        idx = int(sel[0])
        if not (0 <= idx < len(self._selected_lesson.examples)):
            return
        ex = self._selected_lesson.examples[idx]
        self.example_title.configure(text=ex.title)
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", ex.code)
        self.output_text.delete("1.0", "end")
        self.run_button.configure(state=("normal" if ex.runnable else "disabled"))

    def _run_current_code(self) -> None:
        code = self.code_text.get("1.0", "end").strip("\n")
        if not code.strip():
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

    def _copy_current_code(self) -> None:
        code = self.code_text.get("1.0", "end").strip("\n")
        if not code.strip():
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        self.root.update()

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
