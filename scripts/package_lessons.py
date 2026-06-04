"""Package approved lesson markdown into beta LMS JSON assets.

The parser preserves source lesson text and extracts structure for LMS delivery.
It does not rewrite Japanese instructional content.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "content" / "source-lessons"
PROCESSED_DIR = ROOT / "content" / "processed-lessons"
QUIZ_DIR = ROOT / "quizzes" / "lms-json"
FLASHCARD_DIR = ROOT / "flashcards" / "lms-json"


LESSON_CODE_RE = re.compile(r"^(N[1-5])_M(\d+)_L(\d+)_")


def lesson_code_from_path(path: Path) -> str:
    match = LESSON_CODE_RE.match(path.name)
    if not match:
        raise ValueError(f"Cannot derive lesson code from {path.name}")
    level, module, lesson = match.groups()
    return f"{level}-M{int(module):02d}-L{int(lesson):02d}"


def section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(r"^## .+$", text[start:], flags=re.MULTILINE)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def metadata(lines: list[str]) -> dict[str, object]:
    lesson_title = next((line[4:].strip() for line in lines if line.startswith("### Lesson")), "Untitled lesson")
    title = lesson_title.split("—", 1)[-1].strip() if "—" in lesson_title else lesson_title
    header = "\n".join(lines[:10])
    minutes_match = re.search(r"Estimated Study Time:\*\*\s*([0-9]+)", header)
    prereq_match = re.search(r"Prerequisites:\*\*\s*(.+)", header)
    return {
        "title": title,
        "estimated_minutes": int(minutes_match.group(1)) if minutes_match else None,
        "prerequisites": prereq_match.group(1).strip() if prereq_match else None,
    }


def numbered_items(block: str) -> list[str]:
    return [re.sub(r"^\d+\.\s*", "", line).strip() for line in block.splitlines() if re.match(r"^\d+\.\s+", line)]


def checklist_items(block: str) -> list[str]:
    return [line.replace("- [ ]", "", 1).strip() for line in block.splitlines() if line.strip().startswith("- [ ]")]


def markdown_tables(block: str) -> list[list[dict[str, str]]]:
    tables: list[list[dict[str, str]]] = []
    current: list[str] = []
    for line in block.splitlines() + [""]:
        if line.strip().startswith("|"):
            current.append(line.strip())
            continue
        if len(current) >= 3:
            headers = [cell.strip() for cell in current[0].strip("|").split("|")]
            rows: list[dict[str, str]] = []
            for row in current[2:]:
                cells = [cell.strip() for cell in row.strip("|").split("|")]
                if len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))
            if rows:
                tables.append(rows)
        current = []
    return tables


def vocabulary_rows(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for table in markdown_tables(section(text, "Vocabulary")):
        for row in table:
            if {"Japanese", "Furigana", "Meaning"}.issubset(row):
                rows.append(row)
    return rows


def kanji_cards(text: str) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    kanji_block = section(text, "Kanji")
    matches = list(re.finditer(r"^### ([^\s]+) — (.+)$", kanji_block, flags=re.MULTILINE))
    for index, match in enumerate(matches):
        kanji, meaning = match.groups()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(kanji_block)
        body = kanji_block[start:end]
        onyomi = _field(body, "On")
        kunyomi = _field(body, "Kun")
        strokes = _field(body, "Stroke count")
        answer_parts = [part for part in [onyomi, kunyomi, meaning, f"{strokes} strokes" if strokes else ""] if part]
        cards.append({"front": f"Kanji {kanji} — readings & meaning", "back": " | ".join(answer_parts), "card_type": "kanji"})
    return cards


def _field(body: str, label: str) -> str:
    match = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+)", body)
    return match.group(1).strip() if match else ""


def source_flashcards(text: str) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    block = section(text, "Flashcards (Anki-ready Q/A)") or section(text, "Flashcards")
    for line in block.splitlines():
        line = line.strip("` ").strip()
        if not line.startswith("Q:") or "| A:" not in line:
            continue
        front, back = line.split("| A:", 1)
        cards.append({"front": front.replace("Q:", "", 1).strip(), "back": back.strip(), "card_type": "source"})
    return cards


def generated_flashcards(code: str, text: str) -> list[dict[str, str]]:
    cards = source_flashcards(text)
    if cards:
        return cards
    generated: list[dict[str, str]] = []
    for row in vocabulary_rows(text):
        generated.append(
            {
                "front": f"{row['Japanese']} (reading + meaning)",
                "back": f"{row['Furigana']} — {row['Meaning']}",
                "card_type": "vocabulary",
            }
        )
    generated.extend(kanji_cards(text))
    return generated


def quiz_questions(code: str, text: str) -> list[dict[str, object]]:
    if code == "N5-M01-L02":
        return l2_repaired_quiz()
    if code == "N5-M01-L03":
        return l3_exercise_quiz()
    quiz_block = section(text, "Quiz")
    questions: list[dict[str, object]] = []
    for line in quiz_block.splitlines():
        match = re.match(r"^(\d+)\.\s+(.+)$", line.strip())
        if not match or "Answer Key" in line:
            continue
        number, prompt = match.groups()
        qtype = "translation" if int(number) >= 10 else "fill_blank"
        if "→" in prompt and "(a)" in prompt:
            qtype = "multiple_choice"
        if "Matching" in quiz_block[: quiz_block.find(line)] and "|" in line:
            qtype = "matching"
        questions.append({"question_type": qtype, "prompt": prompt, "choices": None, "answer_key": {"answer": ""}})
    answer_key = re.search(r"\*\*Answer Key\*\*\s*(.+)", quiz_block, flags=re.DOTALL)
    if answer_key:
        answers = [part.strip() for part in re.split(r"·", answer_key.group(1).split("---")[0]) if part.strip()]
        for question, answer in zip(questions, answers):
            question["answer_key"] = {"answer": answer}
    return questions


def l2_repaired_quiz() -> list[dict[str, object]]:
    return [
        {"question_type": "multiple_choice", "prompt": "Which reading is commonly safer in speech for 四?", "choices": {"a": "し", "b": "よん", "c": "ろく", "d": "なな"}, "answer_key": {"answer": "b"}},
        {"question_type": "multiple_choice", "prompt": "What does 何時 mean?", "choices": {"a": "what time", "b": "which one", "c": "half", "d": "PM"}, "answer_key": {"answer": "a"}},
        {"question_type": "multiple_choice", "prompt": "Which demonstrative means 'that over there'?", "choices": {"a": "これ", "b": "それ", "c": "あれ", "d": "どれ"}, "answer_key": {"answer": "c"}},
        {"question_type": "fill_blank", "prompt": "これは ___ の本です。", "choices": None, "answer_key": {"answer": "私"}},
        {"question_type": "fill_blank", "prompt": "あの人は先生です. Fill from こそあど: ___人", "choices": None, "answer_key": {"answer": "あの"}},
        {"question_type": "fill_blank", "prompt": "午後三時半 means 3:___ PM.", "choices": None, "answer_key": {"answer": "30"}},
        {"question_type": "matching", "prompt": "Match 73 to its Japanese reading.", "choices": {"answer": "七十三（ななじゅうさん）"}, "answer_key": {"answer": "七十三（ななじゅうさん）"}},
        {"question_type": "matching", "prompt": "Match 4:00 to its reading.", "choices": {"answer": "よじ"}, "answer_key": {"answer": "よじ"}},
        {"question_type": "matching", "prompt": "Match ここ to its meaning.", "choices": {"answer": "here"}, "answer_key": {"answer": "here"}},
        {"question_type": "translation", "prompt": "Translate to Japanese: What time is it now?", "choices": None, "answer_key": {"answer": "今、何時ですか。"}},
        {"question_type": "translation", "prompt": "Translate to English: それは私の本です。", "choices": None, "answer_key": {"answer": "That is my book."}},
    ]


def l3_exercise_quiz() -> list[dict[str, object]]:
    return [
        {"question_type": "multiple_choice", "prompt": "What is the ます form of 食べる?", "choices": {"a": "食べます", "b": "食べません", "c": "食べるます", "d": "食べります"}, "answer_key": {"answer": "a"}},
        {"question_type": "multiple_choice", "prompt": "Which group is する?", "choices": {"a": "Group 1", "b": "Group 2", "c": "Group 3", "d": "adjective"}, "answer_key": {"answer": "c"}},
        {"question_type": "multiple_choice", "prompt": "Which particle marks a direct object?", "choices": {"a": "を", "b": "で", "c": "へ", "d": "か"}, "answer_key": {"answer": "a"}},
        {"question_type": "fill_blank", "prompt": "飲む → 飲み___", "choices": None, "answer_key": {"answer": "ます"}},
        {"question_type": "fill_blank", "prompt": "見ます → 見___", "choices": None, "answer_key": {"answer": "ません"}},
        {"question_type": "fill_blank", "prompt": "図書館___日本語を勉強します。", "choices": None, "answer_key": {"answer": "で"}},
        {"question_type": "matching", "prompt": "Match 書く to its ます form.", "choices": {"answer": "書きます"}, "answer_key": {"answer": "書きます"}},
        {"question_type": "matching", "prompt": "Match 来る to its group.", "choices": {"answer": "Group 3"}, "answer_key": {"answer": "Group 3"}},
        {"question_type": "matching", "prompt": "Match 待つ to its ます form.", "choices": {"answer": "待ちます"}, "answer_key": {"answer": "待ちます"}},
        {"question_type": "translation", "prompt": "Translate to Japanese: I do not go to university on Sunday.", "choices": None, "answer_key": {"answer": "日曜日は大学へ行きません。"}},
    ]


def package(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    code = lesson_code_from_path(path)
    meta = metadata(lines)
    summary = section(text, "Lesson Summary")
    processed = {
        "code": code,
        "title": meta["title"],
        "status": "packaged",
        "source_path": str(path.relative_to(ROOT)),
        "estimated_minutes": meta["estimated_minutes"],
        "prerequisites": meta["prerequisites"],
        "learning_objectives": numbered_items(section(text, "Learning Objectives")),
        "progress_checklist": checklist_items(section(text, "Progress Checklist")),
        "summary": summary,
        "raw_markdown": text,
    }
    quiz = {
        "lesson_code": code,
        "title": f"{code} Lesson Quiz",
        "status": "ready",
        "source": "source_markdown" if code == "N5-M01-L01" else "lms_gap_repair",
        "questions": quiz_questions(code, text),
    }
    cards = {
        "lesson_code": code,
        "status": "ready",
        "source": "source_markdown" if source_flashcards(text) else "lms_gap_repair",
        "cards": generated_flashcards(code, text),
    }
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    QUIZ_DIR.mkdir(parents=True, exist_ok=True)
    FLASHCARD_DIR.mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / f"{code}.json").write_text(json.dumps(processed, ensure_ascii=False, indent=2), encoding="utf-8")
    (QUIZ_DIR / f"{code}.json").write_text(json.dumps(quiz, ensure_ascii=False, indent=2), encoding="utf-8")
    (FLASHCARD_DIR / f"{code}.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    for path in sorted(SOURCE_DIR.glob("N*_M*_L*_*.md")):
        package(path)


if __name__ == "__main__":
    main()
