"""Build a zero-budget static LMS from the final handoff document.

Outputs browser-loadable JSON files under web/data/. The final handoff remains
the source of truth; this script only indexes and extracts LMS-friendly data.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "handoff" / "final" / "FINAL_LMS_HANDOFF_COMPLETE_2026-06-07.md"
BUILD_PROMPT = ROOT / "handoff" / "final" / "GPT_LMS_BUILD_PROMPT_2026-06-07.txt"
EXTRA_SOURCE_FILES = [
    ROOT / "handoff" / "final" / "SUPPLEMENT_J_IT_Japanese_Complete.md",
]
WEB_DATA = ROOT / "web" / "data"
PACKAGE_DATA = WEB_DATA / "lms-package"


@dataclass
class SourceDocument:
    index: str
    filename: str
    title: str
    content: str
    char_count: int


@dataclass
class LessonNode:
    id: str
    title: str
    level: str
    module: str
    lesson: str | None
    track: str
    source_file: str
    source_document: str | None
    skill: str | None = None
    estimated_minutes: int | None = None
    content_ref: str | None = None


def read_handoff() -> str:
    return HANDOFF.read_text(encoding="utf-8")


def split_documents(text: str) -> list[SourceDocument]:
    marker_re = re.compile(r"^# ┌.*$\n^# │\s+\[(\d{2})/30\]\s+(.+?)\s*$\n^# └.*$", re.MULTILINE)
    matches = list(marker_re.finditer(text))
    docs: list[SourceDocument] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        filename = match.group(2).strip()
        content = text[start:end].strip()
        title = next((line.lstrip("# ").strip() for line in content.splitlines() if line.startswith("# ")), filename)
        docs.append(SourceDocument(match.group(1), filename, title, content, len(content)))
    docs.extend(load_extra_source_documents(len(docs)))
    return docs


def load_extra_source_documents(start_index: int) -> list[SourceDocument]:
    docs: list[SourceDocument] = []
    for offset, path in enumerate(EXTRA_SOURCE_FILES, start=1):
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8").strip()
        title = next((line.lstrip("# ").strip() for line in content.splitlines() if line.startswith("# ")), path.name)
        docs.append(SourceDocument(f"X{start_index + offset:02d}", path.name, title, content, len(content)))
    return docs


def map_source_documents(docs: Iterable[SourceDocument]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for doc in docs:
        stem = Path(doc.filename).stem
        mapping[stem] = doc.filename
        compact_stem = stem.replace("_complete", "").replace("_lessons", "")
        mapping[compact_stem] = doc.filename
    return mapping


def parse_curriculum_map(doc: SourceDocument, source_map: dict[str, str]) -> list[LessonNode]:
    nodes: list[LessonNode] = []
    for raw_line in doc.content.splitlines():
        line = raw_line.strip()
        if not (line.startswith("|") and "|" in line[1:]):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] in {"ID", "---"}:
            continue
        identifier = cells[0]
        title = cells[1]
        if re.match(r"^F\d{2}$", identifier):
            track = normalize_track(cells[2] if len(cells) > 2 else "MAIN")
            minutes = parse_minutes(cells[4] if len(cells) > 4 else "")
            nodes.append(
                LessonNode(
                    id=identifier,
                    title=title,
                    level="FOUNDATIONS",
                    module="FOUNDATIONS",
                    lesson=identifier,
                    track=track,
                    source_file=cells[3] if len(cells) > 3 else "FOUNDATIONS_complete.md",
                    source_document=source_map.get(Path(cells[3]).stem) if len(cells) > 3 else "FOUNDATIONS_complete.md",
                    estimated_minutes=minutes,
                )
            )
            continue
        if re.match(r"^N[1-5]-M\d{2}-L\d{2}$", identifier):
            nodes.append(make_jlpt_node(identifier, title, cells, source_map))
            continue
        range_match = re.match(r"^(N[1-5]-M\d{2})-L(\d{2})[–-]L(\d{2})$", identifier)
        if range_match:
            prefix, start, end = range_match.groups()
            for number in range(int(start), int(end) + 1):
                lesson_id = f"{prefix}-L{number:02d}"
                nodes.append(make_jlpt_node(lesson_id, f"{title} · Lesson {number:02d}", cells, source_map))
            continue
        module_match = re.match(r"^(N[1-5]-M\d{2})$", identifier)
        if module_match:
            prefix = module_match.group(1)
            for number in range(1, 21):
                lesson_id = f"{prefix}-L{number:02d}"
                nodes.append(make_jlpt_node(lesson_id, f"{title} · Lesson {number:02d}", cells, source_map))
            continue
        if identifier.startswith("N") and "-OPT-" in identifier:
            level = identifier.split("-", 1)[0]
            nodes.append(
                LessonNode(
                    id=identifier,
                    title=title,
                    level=level,
                    module="OPTIONAL",
                    lesson=identifier,
                    track="OPTIONAL",
                    source_file=cells[2] if len(cells) > 2 else "SUPPLEMENT",
                    source_document=find_source(cells[2] if len(cells) > 2 else "", source_map),
                    skill="real_world",
                )
            )
    nodes = dedupe_nodes(nodes)
    nodes = ensure_formal_jlpt_skeleton(nodes, source_map)
    nodes = add_mock_exam_nodes(nodes)
    nodes = add_supplement_nodes(nodes, source_map)
    return dedupe_nodes(nodes)


def make_jlpt_node(identifier: str, title: str, cells: list[str], source_map: dict[str, str]) -> LessonNode:
    level, module, lesson = identifier.split("-")
    source_file = cells[4] if len(cells) > 4 else ""
    return LessonNode(
        id=identifier,
        title=title,
        level=level,
        module=module,
        lesson=lesson,
        track="MAIN",
        source_file=source_file,
        source_document=find_source(source_file, source_map),
        skill=cells[3] if len(cells) > 3 else None,
        estimated_minutes=90,
    )


def normalize_track(value: str) -> str:
    return "OPTIONAL" if "OPTIONAL" in value.upper() else "MAIN"


def parse_minutes(value: str) -> int | None:
    match = re.search(r"(\d+)", value)
    if not match:
        return None
    hours = int(match.group(1))
    return hours * 60 if "hr" in value.lower() else hours


def find_source(source_hint: str, source_map: dict[str, str]) -> str | None:
    hint = source_hint.replace("*", "").strip()
    if not hint:
        return None
    hint_stem = Path(hint).stem
    candidates = [
        hint_stem,
        hint_stem.replace("-", "_"),
        hint_stem.replace("_*", ""),
        hint_stem.split("_*")[0],
        hint_stem.split("*")[0],
    ]
    for key in candidates:
        if key in source_map:
            return source_map[key]
    for key, filename in source_map.items():
        if hint_stem and (hint_stem in key or key in hint_stem):
            return filename
    return hint


def dedupe_nodes(nodes: Iterable[LessonNode]) -> list[LessonNode]:
    seen: dict[str, LessonNode] = {}
    for node in nodes:
        seen.setdefault(node.id, node)
    return sorted(seen.values(), key=sort_key)


def sort_key(node: LessonNode) -> tuple[int, int, int, str]:
    level_order = {"FOUNDATIONS": 0, "N5": 1, "N4": 2, "N3": 3, "N2": 4, "N1": 5, "SUPPLEMENTS": 6}
    if node.module == "OPTIONAL":
        module_number = 0
    elif node.module == "MOCK":
        module_number = 99
    elif node.module.startswith("SUP-"):
        module_number = 100 + (ord(node.module[-1]) - ord("A"))
    else:
        module_number = int(re.sub(r"\D", "", node.module) or 0)
    lesson_number = int(re.sub(r"\D", "", node.lesson or "") or 0)
    return (level_order.get(node.level, 99), module_number, lesson_number, node.id)


def ensure_formal_jlpt_skeleton(nodes: list[LessonNode], source_map: dict[str, str]) -> list[LessonNode]:
    by_id = {node.id: node for node in nodes}
    for level in ["N5", "N4", "N3", "N2", "N1"]:
        for module_number in range(1, 5):
            module = f"M{module_number:02d}"
            siblings = [node for node in nodes if node.level == level and node.module == module]
            source_document = most_common([node.source_document for node in siblings if node.source_document]) or default_level_source(level, source_map)
            source_file = most_common([node.source_file for node in siblings if node.source_file]) or source_document or ""
            base_title = infer_module_title(level, module, siblings)
            for lesson_number in range(1, 21):
                lesson = f"L{lesson_number:02d}"
                lesson_id = f"{level}-{module}-{lesson}"
                if lesson_id in by_id:
                    continue
                by_id[lesson_id] = LessonNode(
                    id=lesson_id,
                    title=f"{base_title} - Lesson {lesson_number:02d}",
                    level=level,
                    module=module,
                    lesson=lesson,
                    track="MAIN",
                    source_file=source_file,
                    source_document=source_document,
                    skill="mixed",
                    estimated_minutes=90,
                )
    return list(by_id.values())


def add_mock_exam_nodes(nodes: list[LessonNode]) -> list[LessonNode]:
    output = list(nodes)
    for level in ["N5", "N4", "N3", "N2", "N1"]:
        output.append(
            LessonNode(
                id=f"MOCK-{level}",
                title=f"JLPT {level} Mock Examination",
                level=level,
                module="MOCK",
                lesson=f"MOCK-{level}",
                track="MAIN",
                source_file=mock_source_for_level(level),
                source_document=mock_source_for_level(level),
                skill="timed_assessment",
                estimated_minutes=mock_minutes(level),
            )
        )
    return output


def add_supplement_nodes(nodes: list[LessonNode], source_map: dict[str, str]) -> list[LessonNode]:
    output = list(nodes)
    for letter in "ABCDEFGHIJ":
        filename = supplement_source_for_letter(letter, source_map)
        title = supplement_title(letter, filename)
        for number in range(1, 51):
            output.append(
                LessonNode(
                    id=f"SUP-{letter}-{number:02d}",
                    title=f"{title} - Item {number:02d}",
                    level="SUPPLEMENTS",
                    module=f"SUP-{letter}",
                    lesson=f"{number:02d}",
                    track="OPTIONAL",
                    source_file=filename or f"SUPPLEMENT_{letter}",
                    source_document=filename,
                    skill="enrichment",
                    estimated_minutes=30,
                )
            )
    return output


def most_common(values: list[str]) -> str | None:
    if not values:
        return None
    return max(set(values), key=values.count)


def default_level_source(level: str, source_map: dict[str, str]) -> str | None:
    for key in [f"{level}_complete", f"{level}_expanded_lessons", f"{level}_M3_M4_complete"]:
        if key in source_map:
            return source_map[key]
    return None


def infer_module_title(level: str, module: str, siblings: list[LessonNode]) -> str:
    if siblings:
        compact = siblings[0].title.split(":", 1)[0].split("(", 1)[0].strip()
        if compact:
            return compact
    titles = {
        "M01": "Core grammar and vocabulary",
        "M02": "Applied reading/listening",
        "M03": "Skill expansion",
        "M04": "Review and assessment",
    }
    return f"{level} {titles.get(module, module)}"


def mock_source_for_level(level: str) -> str:
    if level in {"N5", "N4"}:
        return "MOCK_EXAM_N5_N4.md"
    if level in {"N3", "N2"}:
        return "MOCK_EXAM_N3_N2.md"
    return "MOCK_EXAM_N1.md"


def mock_minutes(level: str) -> int:
    return {"N5": 110, "N4": 125, "N3": 140, "N2": 155, "N1": 170}[level]


def supplement_source_for_letter(letter: str, source_map: dict[str, str]) -> str | None:
    needle = f"SUPPLEMENT_{letter}"
    for key, filename in source_map.items():
        if needle in key or needle in filename:
            return filename
    return None


def supplement_title(letter: str, filename: str | None) -> str:
    if not filename:
        return f"Supplement {letter}"
    stem = Path(filename).stem.replace("_", " ")
    return stem.replace("SUPPLEMENT", f"Supplement {letter}:").strip()


def extract_content_blocks(docs: list[SourceDocument], nodes: list[LessonNode]) -> dict[str, dict[str, object]]:
    by_filename = {doc.filename: doc for doc in docs}
    blocks: dict[str, dict[str, object]] = {}
    for node in nodes:
        doc = by_filename.get(node.source_document or "")
        if not doc:
            continue
        block = find_lesson_block(doc.content, node)
        if not block and node.id.startswith("F"):
            block = find_foundation_block(doc.content, node.id)
        if not block and node.id.startswith("SUP-"):
            block = find_supplement_block(doc.content, node)
        if block:
            blocks[node.id] = {
                "id": node.id,
                "title": node.title,
                "source_document": doc.filename,
                "markdown": block.strip(),
                "objectives": extract_numbered_section(block, "Learning Objectives"),
                "vocabulary": extract_vocab_rows(block),
                "checklist": extract_checklist(block),
            }
            node.content_ref = f"data/lessons/{node.id}.json"
    return blocks


def find_lesson_block(content: str, node: LessonNode) -> str:
    if not node.lesson:
        return ""
    lesson_num = int(re.sub(r"\D", "", node.lesson) or 0)
    if not lesson_num:
        return ""
    pattern = re.compile(rf"^#{{1,4}}\s+Lesson\s+{lesson_num}\s+[—-].*$", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        return ""
    next_match = re.search(r"^#{1,4}\s+Lesson\s+\w+\s+[—-].*$", content[match.end():], flags=re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(content)
    return content[match.start():end]


def find_foundation_block(content: str, lesson_id: str) -> str:
    pattern = re.compile(rf"^#\s+Lesson\s+{lesson_id[-2:].lstrip('0') if lesson_id != 'F01' else 'F1'}\s+[—-].*$", re.MULTILINE)
    alt = re.compile(rf"^#\s+Lesson\s+{lesson_id}\s+[—-].*$", re.MULTILINE)
    match = alt.search(content) or pattern.search(content)
    if not match:
        return ""
    next_match = re.search(r"^#\s+Lesson\s+F?\d+\s+[—-].*$", content[match.end():], flags=re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(content)
    return content[match.start():end]


def find_supplement_block(content: str, node: LessonNode) -> str:
    match = re.match(r"^SUP-([A-Z])-(\d{2})$", node.id)
    if not match:
        return ""
    letter, number = match.groups()
    heading = re.compile(rf"^##\s+{letter}{int(number)}\s+[—-].*$", re.MULTILINE)
    found = heading.search(content)
    if not found:
        return ""
    next_heading = re.search(rf"^##\s+{letter}\d+\s+[—-].*$", content[found.end():], flags=re.MULTILINE)
    end = found.end() + next_heading.start() if next_heading else len(content)
    return content[found.start():end]


def extract_numbered_section(text: str, heading: str) -> list[str]:
    block = section(text, heading)
    return [re.sub(r"^\d+\.\s*", "", line).strip() for line in block.splitlines() if re.match(r"^\d+\.\s+", line)]


def extract_checklist(text: str) -> list[str]:
    return [line.replace("- [ ]", "", 1).strip() for line in text.splitlines() if line.strip().startswith("- [ ]")]


def extract_vocab_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current: list[str] = []
    for line in text.splitlines() + [""]:
        if line.strip().startswith("|"):
            current.append(line.strip())
            continue
        if len(current) >= 3:
            headers = [cell.strip() for cell in current[0].strip("|").split("|")]
            if {"Japanese", "Furigana", "Meaning"}.issubset(headers):
                for row in current[2:]:
                    cells = [cell.strip() for cell in row.strip("|").split("|")]
                    if len(cells) == len(headers):
                        rows.append(dict(zip(headers, cells)))
            elif {"Japanese", "Reading", "English"}.issubset(headers):
                for row in current[2:]:
                    cells = [cell.strip() for cell in row.strip("|").split("|")]
                    if len(cells) == len(headers):
                        item = dict(zip(headers, cells))
                        rows.append(
                            {
                                "Japanese": item.get("Japanese", ""),
                                "Furigana": item.get("Reading", ""),
                                "Meaning": item.get("English", ""),
                            }
                        )
        current = []
    return rows


def section(text: str, heading: str) -> str:
    match = re.search(rf"^#+\s+{re.escape(heading)}\s*$", text, flags=re.MULTILINE)
    if not match:
        return ""
    next_match = re.search(r"^#+\s+.+$", text[match.end():], flags=re.MULTILINE)
    end = match.end() + next_match.start() if next_match else len(text)
    return text[match.end():end].strip()


def build_summary(nodes: list[LessonNode], docs: list[SourceDocument], blocks: dict[str, dict[str, object]]) -> dict[str, object]:
    levels: dict[str, dict[str, object]] = {}
    for node in nodes:
        level = levels.setdefault(node.level, {"lesson_count": 0, "main": 0, "optional": 0, "modules": {}})
        level["lesson_count"] += 1
        level["main" if node.track == "MAIN" else "optional"] += 1
        modules = level["modules"]
        modules[node.module] = modules.get(node.module, 0) + 1
    return {
        "title": "日本語大学 — JLPT 0→N1 Static LMS",
        "source": str(HANDOFF.relative_to(ROOT)),
        "build_prompt": str(BUILD_PROMPT.relative_to(ROOT)),
        "source_documents": len(docs),
        "indexed_nodes": len(nodes),
        "content_blocks": len(blocks),
        "levels": levels,
        "storage": "browser localStorage",
        "backend_required": False,
    }


def build_course_structure_markdown(nodes: list[LessonNode]) -> str:
    lines = ["## TASK 1 — COURSE STRUCTURE", ""]
    current_course = ""
    current_unit = ""
    for node in nodes:
        if node.level != current_course:
            current_course = node.level
            current_unit = ""
            lines.extend(["", f"COURSE: {course_label(node.level)}"])
        unit = f"{node.module} - {module_title(node)}"
        if unit != current_unit:
            current_unit = unit
            lines.append(f"  UNIT: {unit}")
        minutes = node.estimated_minutes or 90
        lines.append(f"    SCO: {node.id} | {node.title} | {minutes} min | Track: {node.track}")
    lines.extend(["", "## TASK 1 COMPLETE ✅", "Ready for TASK 2. Type \"continue\" to proceed."])
    return "\n".join(lines).strip() + "\n"


def course_label(level: str) -> str:
    if level == "FOUNDATIONS":
        return "Foundations"
    if level == "SUPPLEMENTS":
        return "Supplements"
    return level


def module_title(node: LessonNode) -> str:
    if node.module == "FOUNDATIONS":
        return "Before N5 Begins"
    if node.module == "OPTIONAL":
        return "Optional / Real-World Japanese"
    if node.module == "MOCK":
        return "Mock Examination Gate"
    if node.level == "SUPPLEMENTS":
        return "Enrichment / Beyond JLPT"
    return f"{node.level} {node.module}"


def build_quiz_bank_skeleton(nodes: list[LessonNode], blocks: dict[str, dict[str, object]]) -> dict[str, object]:
    quizzes = []
    for node in nodes:
        has_content = node.id in blocks
        quizzes.append(
            {
                "quiz_id": f"QUIZ-{node.id}",
                "lesson": node.id,
                "title": f"{node.title} Quiz",
                "level": node.level,
                "module": node.module,
                "track": node.track,
                "skill": node.skill or "mixed",
                "difficulty": node.level,
                "status": "needs_question_extraction" if has_content else "awaiting_lesson_content",
                "question_count": 0,
                "questions": [],
            }
        )
    return {
        "schema": "nihongo-daigaku.quiz-bank.v1",
        "note": "Question objects are intentionally not invented. Extract from Exercise Sets, Review Questions, Reading Practice, Listening Practice, and mock exams.",
        "quizzes": quizzes,
    }


def build_anki_vocab_tsv(blocks: dict[str, dict[str, object]]) -> str:
    rows = ["Front\tBack\tTags"]
    for lesson_id, payload in sorted(blocks.items()):
        level = lesson_id.split("-", 1)[0] if lesson_id.startswith("N") else "FOUNDATIONS"
        for item in payload.get("vocabulary", []):
            japanese = item.get("Japanese", "").strip()
            furigana = item.get("Furigana", "").strip()
            meaning = item.get("Meaning", "").strip()
            if not japanese or not meaning:
                continue
            front = f"{japanese} ({furigana})" if furigana else japanese
            tags = f"{level} vocabulary {lesson_id}"
            rows.append(f"{tsv_cell(front)}\t{tsv_cell(meaning)}\t{tsv_cell(tags)}")
    return "\n".join(rows) + "\n"


def tsv_cell(value: str) -> str:
    return re.sub(r"[\t\r\n]+", " ", value).strip()


def build_mock_exam_specs(docs: list[SourceDocument]) -> dict[str, dict[str, object]]:
    exam_sources = {
        "MOCK-N5": ("N5", "MOCK_EXAM_N5_N4.md", 110),
        "MOCK-N4": ("N4", "MOCK_EXAM_N5_N4.md", 125),
        "MOCK-N3": ("N3", "MOCK_EXAM_N3_N2.md", 140),
        "MOCK-N2": ("N2", "MOCK_EXAM_N3_N2.md", 155),
        "MOCK-N1": ("N1", "MOCK_EXAM_N1.md", 170),
    }
    by_filename = {doc.filename: doc for doc in docs}
    specs: dict[str, dict[str, object]] = {}
    for exam_id, (level, filename, minutes) in exam_sources.items():
        doc = by_filename.get(filename)
        specs[exam_id] = {
            "exam_id": exam_id,
            "title": f"JLPT {level} Mock Examination",
            "level": level,
            "source_document": filename,
            "total_time_minutes": minutes,
            "pass_score": 80,
            "max_score": 180,
            "sections": default_exam_sections(level),
            "status": "source_preserved_needs_question_extraction",
            "source_excerpt": extract_exam_excerpt(doc.content, level) if doc else "",
            "feedback": {
                "pass": f"Passed {level}. Review weak sections before moving forward.",
                "fail_total": "Not yet passing overall. Review all sections and retake later.",
                "fail_section": "Overall score may pass, but a section minimum was missed. Review that section.",
            },
        }
    return specs


def default_exam_sections(level: str) -> list[dict[str, object]]:
    return [
        {
            "section_id": f"{level}-VOCAB",
            "title": "Language Knowledge: Vocabulary",
            "time_minutes": 25,
            "min_pass_score": 19,
            "questions": [],
        },
        {
            "section_id": f"{level}-GRAMMAR-READING",
            "title": "Language Knowledge: Grammar / Reading",
            "time_minutes": 55,
            "min_pass_score": 19,
            "questions": [],
        },
        {
            "section_id": f"{level}-LISTENING",
            "title": "Listening",
            "time_minutes": 40,
            "min_pass_score": 19,
            "questions": [],
        },
    ]


def extract_exam_excerpt(content: str, level: str) -> str:
    match = re.search(rf"^#\s+JLPT\s+{level}\s+.+$", content, flags=re.MULTILINE)
    if not match:
        return content[:4000]
    next_match = re.search(r"^#\s+JLPT\s+N[1-5]\s+.+$", content[match.end():], flags=re.MULTILINE)
    end = match.end() + next_match.start() if next_match else min(len(content), match.start() + 8000)
    return content[match.start():end].strip()


def build_workbook_specs(nodes: list[LessonNode]) -> str:
    lines = ["# PDF WORKBOOK SPECS", ""]
    grouped: dict[tuple[str, str], list[LessonNode]] = {}
    for node in nodes:
        if node.module not in {"FOUNDATIONS", "OPTIONAL"}:
            grouped.setdefault((node.level, node.module), []).append(node)
    for (level, module), module_nodes in sorted(grouped.items(), key=lambda item: sort_key(item[1][0])):
        lines.extend([f"## PDF WORKBOOK: {level}_{module}_Workbook.pdf", "### Contents:"])
        lines.append("1. Module Overview")
        for index, node in enumerate(module_nodes, start=2):
            lines.append(f"{index}. Lesson {node.lesson}: {node.title}")
            lines.append("   - Vocabulary table when present in source")
            lines.append("   - Grammar summary from approved lesson source")
            lines.append("   - Exercise sets and answer key when present")
            lines.append("   - Writing / self-check prompt when present")
        lines.append(f"{len(module_nodes) + 2}. Module Review + Self-assessment checklist")
        lines.append("Appendix A: Module vocabulary")
        lines.append("Appendix B: Module kanji")
        lines.append("Appendix C: Module grammar quick reference")
        lines.append("")
    lines.append("Formatting: A4 or US Letter, readable sans-serif body, Japanese-capable font fallback, answer keys at back.")
    return "\n".join(lines).strip() + "\n"


def build_progress_schema() -> dict[str, object]:
    return {
        "learner_id": "local-browser-user",
        "current_level": "N5|N4|N3|N2|N1",
        "lessons_completed": ["N5-M01-L01"],
        "quiz_scores": {
            "N5-M01-L01": {"score": 85, "attempts": 1, "last_attempt": "YYYY-MM-DD"}
        },
        "mock_exam_scores": {
            "MOCK-N5": {
                "total": 142,
                "vocab_section": 38,
                "grammar_reading_section": 65,
                "listening_section": 39,
                "passed": True,
                "date": "YYYY-MM-DD",
            }
        },
        "anki_stats": {
            "N5_Vocabulary": {"cards_due": 12, "retention_rate": 0.87}
        },
        "level_unlock_status": {"N5": "in_progress", "N4": "locked", "N3": "locked", "N2": "locked", "N1": "locked"},
        "unlock_conditions": {
            "N4": "Complete N5 and pass MOCK-N5",
            "N3": "Complete N4 and pass MOCK-N4",
            "N2": "Complete N3 and pass MOCK-N3",
            "N1": "Complete N2 and pass MOCK-N2",
        },
        "storage": "localStorage for static LMS; server-side schema can mirror this object later.",
    }


def build_manifest(nodes: list[LessonNode]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<manifest identifier="nihongo-daigaku-static" version="1.0" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2">',
        '  <organizations default="nihongo-daigaku-org">',
        '    <organization identifier="nihongo-daigaku-org">',
        "      <title>Nihongo Daigaku</title>",
    ]
    current_level = ""
    for node in nodes:
        if node.level != current_level:
            if current_level:
                lines.append("      </item>")
            current_level = node.level
            lines.append(f'      <item identifier="{xml_escape(node.level)}">')
            lines.append(f"        <title>{xml_escape(node.level)}</title>")
        lines.append(f'        <item identifier="ITEM-{xml_escape(node.id)}" identifierref="{xml_escape(node.id)}">')
        lines.append(f"          <title>{xml_escape(node.id)} - {xml_escape(node.title)}</title>")
        lines.append("        </item>")
    if current_level:
        lines.append("      </item>")
    lines.extend(["    </organization>", "  </organizations>", "  <resources>"])
    for node in nodes:
        href = f"index.html#/{node.id}"
        lines.append(f'    <resource identifier="{xml_escape(node.id)}" type="webcontent" adlcp:scormtype="sco" href="{href}">')
        lines.append("      <metadata>")
        lines.append(f"        <title>{xml_escape(node.id)} - {xml_escape(node.title)}</title>")
        lines.append(f"        <difficulty>{xml_escape(node.level)}</difficulty>")
        lines.append(f"        <typicallearningtime>PT{node.estimated_minutes or 90}M</typicallearningtime>")
        lines.append("      </metadata>")
        lines.append("    </resource>")
    lines.extend(["  </resources>", "</manifest>", ""])
    return "\n".join(lines)


def xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def build_package_index(nodes: list[LessonNode], docs: list[SourceDocument], blocks: dict[str, dict[str, object]]) -> dict[str, object]:
    formal_count = len([node for node in nodes if re.match(r"^N[1-5]-M0[1-4]-L\d{2}$", node.id)])
    optional_count = len([node for node in nodes if "-OPT-" in node.id])
    mock_count = len([node for node in nodes if node.id.startswith("MOCK-")])
    supplement_count = len([node for node in nodes if node.id.startswith("SUP-")])
    return {
        "schema": "nihongo-daigaku.lms-package-index.v1",
        "source": str(HANDOFF.relative_to(ROOT)),
        "build_prompt": str(BUILD_PROMPT.relative_to(ROOT)),
        "status": "static_package_generated",
        "counts": {
            "sco_nodes": len(nodes),
            "formal_jlpt_lessons": formal_count,
            "level_optional_lessons": optional_count,
            "mock_exam_scos": mock_count,
            "supplement_scos": supplement_count,
            "source_documents": len(docs),
            "lesson_extracts": len(blocks),
        },
        "artifacts": [
            {"task": 1, "name": "Course structure", "path": "data/lms-package/course-structure.md", "format": "markdown"},
            {"task": 2, "name": "Quiz bank skeleton", "path": "data/lms-package/quiz-bank-skeleton.json", "format": "json"},
            {"task": 3, "name": "Anki vocabulary TSV", "path": "data/lms-package/anki-vocabulary.tsv", "format": "tsv"},
            {"task": 4, "name": "Mock exam specs", "path": "data/lms-package/mock-exams.json", "format": "json"},
            {"task": 5, "name": "Workbook specs", "path": "data/lms-package/workbook-specs.md", "format": "markdown"},
            {"task": 6, "name": "Progress schema", "path": "data/lms-package/progress-schema.json", "format": "json"},
            {"task": 7, "name": "IMS manifest", "path": "data/lms-package/imsmanifest.xml", "format": "xml"},
        ],
        "rule": "Preserve source Japanese. Do not invent lesson, quiz, or answer content.",
    }


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def reset_generated_outputs() -> None:
    for path in [WEB_DATA / "source-docs", WEB_DATA / "lessons", PACKAGE_DATA]:
        if path.exists():
            shutil.rmtree(path)
    WEB_DATA.mkdir(parents=True, exist_ok=True)


def main() -> None:
    reset_generated_outputs()
    text = read_handoff()
    docs = split_documents(text)
    source_map = map_source_documents(docs)
    curriculum_doc = next(doc for doc in docs if doc.filename == "CURRICULUM_STRUCTURE_MAP.md")
    nodes = parse_curriculum_map(curriculum_doc, source_map)
    blocks = extract_content_blocks(docs, nodes)

    write_json(WEB_DATA / "source-documents.json", [asdict(doc) | {"content": None} for doc in docs])
    source_dir = WEB_DATA / "source-docs"
    source_dir.mkdir(parents=True, exist_ok=True)
    for doc in docs:
        write_json(
            source_dir / f"{safe_filename(doc.filename)}.json",
            {
                "index": doc.index,
                "filename": doc.filename,
                "title": doc.title,
                "markdown": doc.content,
            },
        )
    write_json(WEB_DATA / "learning-path.json", [asdict(node) for node in nodes])
    write_json(WEB_DATA / "summary.json", build_summary(nodes, docs, blocks))
    lesson_dir = WEB_DATA / "lessons"
    lesson_dir.mkdir(parents=True, exist_ok=True)
    for payload in blocks.values():
        write_json(lesson_dir / f"{payload['id']}.json", payload)
    mock_specs = build_mock_exam_specs(docs)
    write_text(PACKAGE_DATA / "course-structure.md", build_course_structure_markdown(nodes))
    write_json(PACKAGE_DATA / "quiz-bank-skeleton.json", build_quiz_bank_skeleton(nodes, blocks))
    write_text(PACKAGE_DATA / "anki-vocabulary.tsv", build_anki_vocab_tsv(blocks))
    write_json(PACKAGE_DATA / "mock-exams.json", mock_specs)
    write_text(PACKAGE_DATA / "workbook-specs.md", build_workbook_specs(nodes))
    write_json(PACKAGE_DATA / "progress-schema.json", build_progress_schema())
    write_text(PACKAGE_DATA / "imsmanifest.xml", build_manifest(nodes))
    write_json(PACKAGE_DATA / "package-index.json", build_package_index(nodes, docs, blocks))


def safe_filename(filename: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", filename)


if __name__ == "__main__":
    main()
