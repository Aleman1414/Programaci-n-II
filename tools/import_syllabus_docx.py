from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path


def extract_lines(docx_path: Path) -> list[str]:
    with zipfile.ZipFile(docx_path) as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
    xml = xml.replace("</w:p>", "\n")
    text = re.sub(r"<[^>]+>", "", xml)
    text = (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&apos;", "'")
    )
    lines = [ln.strip() for ln in text.splitlines()]
    return [ln for ln in lines if ln]


def parse_weeks_from_syllabus(lines: list[str]) -> list[dict]:
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("XI.") and "PROGRAMACIÓN DEL CURSO" in ln:
            start = i
            break
    if start is None:
        raise ValueError("No se encontró la sección 'XI. PROGRAMACIÓN DEL CURSO'")

    end = None
    for i in range(start, len(lines)):
        if lines[i].startswith("XII."):
            end = i
            break
    if end is None:
        end = len(lines)

    schedule = lines[start:end]
    week_re = re.compile(r"^Semana\\s+(\\d+)$", re.IGNORECASE)

    weeks: list[dict] = []
    i = 0
    while i < len(schedule):
        m = week_re.match(schedule[i])
        if not m:
            i += 1
            continue
        week = int(m.group(1))
        date_range = schedule[i + 1] if i + 1 < len(schedule) else ""
        i += 2

        topics: list[str] = []
        resources: list[str] = []
        while (
            i < len(schedule)
            and not week_re.match(schedule[i])
            and not schedule[i].startswith("FECHA(S)")
            and not schedule[i].startswith("XII.")
        ):
            ln = schedule[i]
            if re.match(r"^(Clase|Lectura|Tarea|Evaluación|Foro|Bibliografía|Herramienta)\\b", ln):
                resources.append(ln)
            else:
                topics.append(ln)
            i += 1

        # compact: remove duplicated consecutive lines
        compact_topics: list[str] = []
        for t in topics:
            if not compact_topics or compact_topics[-1] != t:
                compact_topics.append(t)

        weeks.append(
            {
                "week": week,
                "date_range": date_range,
                "topics_raw": compact_topics,
                "resources_raw": resources,
            }
        )
    weeks.sort(key=lambda w: w["week"])
    return weeks


def main() -> int:
    p = argparse.ArgumentParser(description="Importa semanas desde un sílabo .docx (Programación II).")
    p.add_argument("docx", type=Path, help="Ruta al archivo .docx")
    p.add_argument("--out", type=Path, default=Path("content/curriculum_importado.json"), help="Salida JSON")
    args = p.parse_args()

    docx_path: Path = args.docx
    if not docx_path.exists():
        raise SystemExit(f"No existe: {docx_path}")

    lines = extract_lines(docx_path)
    weeks = parse_weeks_from_syllabus(lines)

    out = {
        "source_docx": str(docx_path),
        "lessons": [
            {
                "id": f"w{w['week']:02d}",
                "week": w["week"],
                "title": f"Semana {w['week']:02d}",
                "topics": w["topics_raw"],
                "theory": "",
                "examples": [],
                "exercises": [],
                "quiz": [],
                "resources": w["resources_raw"],
            }
            for w in weeks
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

