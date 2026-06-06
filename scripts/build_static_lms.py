"""Build a zero-budget static LMS from the final handoff document.

Outputs browser-loadable JSON files under web/data/. The final handoff remains
the source of truth; this script only indexes and extracts LMS-friendly data.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "handoff" / "final" / "FINAL_LMS_HANDOFF_COMPLETE.md"
WEB_DATA = ROOT / "web" / "data"


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
    level_order = {"FOUNDATIONS": 0, "N5": 1, "N4": 2, "N3": 3, "N2": 4, "N1": 5}
    module_number = int(re.sub(r"\D", "", node.module) or 0)
    lesson_number = int(re.sub(r"\D", "", node.lesson or "") or 0)
    return (level_order.get(node.level, 99), module_number, lesson_number, node.id)


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
        "source_documents": len(docs),
        "indexed_nodes": len(nodes),
        "content_blocks": len(blocks),
        "levels": levels,
        "storage": "browser localStorage",
        "backend_required": False,
    }


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
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


def safe_filename(filename: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", filename)


if __name__ == "__main__":
    main()
