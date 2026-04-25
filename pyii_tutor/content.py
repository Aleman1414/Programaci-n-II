from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True)
class QuizItem:
    q: str
    options: list[str]
    answer: int
    explanation: str | None = None


@dataclass(frozen=True)
class Example:
    title: str
    code: str
    runnable: bool = True


@dataclass(frozen=True)
class Lesson:
    id: str
    week: int
    title: str
    topics: list[str]
    theory: str
    examples: list[Example]
    exercises: list[str]
    quiz: list[QuizItem]


@dataclass(frozen=True)
class GlossaryItem:
    java: str
    python: str


@dataclass(frozen=True)
class CourseMeta:
    name: str
    subtitle: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class Curriculum:
    course: CourseMeta
    lessons: list[Lesson]
    glossary: list[GlossaryItem]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_curriculum(path: str | Path | None = None) -> Curriculum:
    if path is None:
        path = _repo_root() / "content" / "curriculum.json"
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))

    course = raw.get("course") or {}
    course_meta = CourseMeta(
        name=str(course.get("name", "Programación II (Python)")),
        subtitle=course.get("subtitle"),
        note=course.get("note"),
    )

    glossary_items = []
    for item in raw.get("glossary", []):
        glossary_items.append(GlossaryItem(java=str(item.get("java", "")), python=str(item.get("python", ""))))

    lessons: list[Lesson] = []
    for item in raw.get("lessons", []):
        examples = [
            Example(
                title=str(ex.get("title", "Ejemplo")),
                code=str(ex.get("code", "")),
                runnable=bool(ex.get("runnable", True)),
            )
            for ex in item.get("examples", []) or []
        ]
        quiz = [
            QuizItem(
                q=str(q.get("q", "")),
                options=[str(o) for o in (q.get("options", []) or [])],
                answer=int(q.get("answer", 0)),
                explanation=q.get("explanation"),
            )
            for q in item.get("quiz", []) or []
        ]
        lessons.append(
            Lesson(
                id=str(item.get("id", "")),
                week=int(item.get("week", 0)),
                title=str(item.get("title", "")),
                topics=[str(t) for t in (item.get("topics", []) or [])],
                theory=str(item.get("theory", "")),
                examples=examples,
                exercises=[str(e) for e in (item.get("exercises", []) or [])],
                quiz=quiz,
            )
        )

    lessons.sort(key=lambda l: (l.week, l.title))
    return Curriculum(course=course_meta, lessons=lessons, glossary=glossary_items)


TextTab = Literal["Teoría", "Ejercicios"]


def lesson_topics_text(lesson: Lesson) -> str:
    if not lesson.topics:
        return ""
    return "Temas:\n" + "\n".join(f"- {t}" for t in lesson.topics)


def lesson_exercises_text(lesson: Lesson) -> str:
    if not lesson.exercises:
        return "No hay ejercicios aún para esta semana."
    return "Ejercicios:\n" + "\n".join(f"{i+1}. {e}" for i, e in enumerate(lesson.exercises))

