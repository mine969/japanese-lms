# 📋 CHATGPT LMS BUILD PROMPT
## Copy-paste this prompt when feeding the handoff file to ChatGPT

---

## ═══════════════════════════════════════════════
## PROMPT VERSION 1 — FULL BUILD (Recommended)
## Use this first after uploading the handoff file
## ═══════════════════════════════════════════════

---

You are an expert instructional designer and LMS developer. I have uploaded a complete Japanese language curriculum called **日本語大学** (Nihongo Daigaku). Your job is to transform this curriculum source document into a fully structured LMS package.

---

## CURRICULUM OVERVIEW

This is a complete JLPT N5→N1 Japanese language learning system for:
- **Learner profile:** International student in Tokyo, Japan. Native languages: English, Myanmar, basic Chinese, basic Thai. Starting from zero Japanese.
- **Goal:** Pass JLPT N1 and achieve natural conversational fluency.
- **Structure:** 5 JLPT levels (N5→N4→N3→N2→N1) × 4 modules × 20 lessons = 400 formal lessons, plus Foundations (F01–F07) and Supplement modules (SUP-A through SUP-I).
- **Two tracks:** 🟦 MAIN (JLPT exam-focused) and 🟩 OPTIONAL (real-world Japanese beyond the exam).

---

## YOUR BUILD TASKS

Work through these tasks **in order**. Complete each task fully before moving to the next.

---

### TASK 1 — SCORM COURSE STRUCTURE (Do this first)

Create the complete course architecture as a structured outline. For every level (Foundations → N5 → N4 → N3 → N2 → N1 → Supplements), output:

```
COURSE: [Level Name]
  UNIT: Module 1 — [Module Title]
    SCO: [SCORM ID] | [Lesson Title] | [Est. minutes] | Track: MAIN/OPTIONAL
    SCO: [SCORM ID] | [Lesson Title] | [Est. minutes] | Track: MAIN/OPTIONAL
    ...
  UNIT: Module 2 — [Module Title]
    ...
```

**SCORM ID format:**
- Foundations: F01, F02, F03...F07
- JLPT lessons: N5-M01-L01, N5-M01-L02...N1-M04-L20
- Supplements: SUP-A-01, SUP-A-02...SUP-I-50
- Mock exams: MOCK-N5, MOCK-N4, MOCK-N3, MOCK-N2, MOCK-N1

**Track labels:**
- 🟦 MAIN = Required for JLPT exam pass
- 🟩 OPTIONAL = Real-world/enrichment (beyond exam)

Output the **full** outline for all levels — do not abbreviate.

---

### TASK 2 — QUIZ BANK (Per Level)

For each lesson, extract and format quiz questions in this JSON structure:

```json
{
  "quiz_id": "QUIZ-N5-M01-L04",
  "lesson": "N5-M01-L04",
  "title": "は vs が",
  "level": "N5",
  "skill": "文法",
  "questions": [
    {
      "q_id": "N5-M01-L04-Q01",
      "type": "multiple_choice",
      "question": "誰___来ましたか。",
      "options": ["は", "が", "を", "に"],
      "correct": 1,
      "explanation": "誰が questions always take が to identify new information.",
      "jlpt_skill": "文法",
      "difficulty": "N5"
    }
  ]
}
```

**Question types to create:**
- `multiple_choice` — 4 options, 1 correct (from Exercise Sets and Review Questions)
- `fill_blank` — complete the sentence
- `matching` — match Japanese to English
- `reading_comprehension` — passage + questions
- `listening_comprehension` — transcript + questions

**Sources for questions:**
- Exercise Set A/B/C → multiple_choice and fill_blank
- Review Questions → fill_blank or short_answer
- Reading Practice questions → reading_comprehension
- Listening Practice questions → listening_comprehension
- Mock Exam questions → timed_assessment

**Tag every question with:**
`level`, `module`, `lesson`, `skill` (文字語彙/文法/読解/聴解/会話/作文), `difficulty`

---

### TASK 3 — ANKI FLASHCARD DECKS

Extract all vocabulary tables (marked with `| # | Japanese | Furigana | Meaning |`) and output Anki-compatible TSV files.

**Deck structure:**
```
Deck name: 日本語大学::N5::Vocabulary
Deck name: 日本語大学::N5::Kanji
Deck name: 日本語大学::N5::Grammar_Sentences
Deck name: 日本語大学::N4::Vocabulary
... (continue for all levels)
Deck name: 日本語大学::CORE::Onomatopoeia
Deck name: 日本語大学::CORE::Business_Japanese
Deck name: 日本語大学::CORE::Four_Character_Compounds
Deck name: 日本語大学::CORE::Proverbs
```

**Card format (tab-separated):**
```
Front	Back	Tags
{Japanese} ({Furigana})	{English meaning}\n\n例: {example sentence}	N5 vocabulary M01 L04
```

**Kanji card format:**
```
Front	Back	Tags
{Kanji} — {meaning}	Onyomi: {on}\nKunyomi: {kun}\nExample: {word} ({reading}) — {meaning}	N5 kanji
```

**Grammar card format:**
```
Front	Back	Tags
～{pattern}	Meaning: {explanation}\nStructure: {formation}\nExample: {sentence}\nTranslation: {translation}	N5 grammar M01
```

---

### TASK 4 — MOCK EXAMINATION SCORM PACKAGES

For each level's mock exam (found in MOCK_EXAM_N5_N4, MOCK_EXAM_N3_N2, MOCK_EXAM_N1), create a timed SCORM assessment package spec:

```json
{
  "exam_id": "MOCK-N5",
  "title": "JLPT N5 模擬試験 Mock Examination",
  "total_time_minutes": 110,
  "pass_score": 80,
  "max_score": 180,
  "sections": [
    {
      "section_id": "N5-VOCAB",
      "title": "言語知識（文字・語彙）",
      "time_minutes": 25,
      "min_pass_score": 38,
      "questions": ["N5-V-Q01", "N5-V-Q02", ...]
    },
    {
      "section_id": "N5-GRAMMAR-READING",
      "title": "言語知識（文法）・読解",
      "time_minutes": 50,
      "min_pass_score": 38,
      "questions": [...]
    },
    {
      "section_id": "N5-LISTENING",
      "title": "聴解",
      "time_minutes": 40,
      "min_pass_score": 19,
      "questions": [...]
    }
  ],
  "feedback": {
    "pass": "合格！You are ready for JLPT N5. Review any weak sections and maintain your study momentum.",
    "fail_total": "Not yet passing overall. Review all sections and retake in 2 weeks.",
    "fail_section": "You passed overall but fell below the minimum in {section}. Focus your review there."
  }
}
```

Include all questions from the mock exam JSON, with correct answers and explanations.

---

### TASK 5 — PDF WORKBOOK SPECS

For each module (e.g., N5 Module 1), define the PDF workbook contents:

```markdown
## PDF WORKBOOK: N5_M1_Workbook.pdf
### Contents:
1. Module 1 Overview (1 page)
2. Lesson 1: [Title]
   - Vocabulary table (full)
   - Kanji with stroke order reference
   - Grammar points summary
   - Exercise Set A + B (with answer key at back)
   - Writing practice prompt
3. Lesson 2: ...
...
20. Module Review + Self-assessment checklist
Appendix A: All Module 1 vocabulary (alphabetical)
Appendix B: All Module 1 kanji (by stroke count)
Appendix C: All Module 1 grammar patterns (quick reference)
```

Specify page layout, fonts, and any formatting notes.

---

### TASK 6 — PROGRESS TRACKING SCHEMA

Define the learner progress data model:

```json
{
  "learner_id": "string",
  "current_level": "N5|N4|N3|N2|N1",
  "lessons_completed": ["N5-M01-L01", "N5-M01-L02"],
  "quiz_scores": {
    "N5-M01-L01": {"score": 85, "attempts": 1, "last_attempt": "date"},
  },
  "mock_exam_scores": {
    "MOCK-N5": {
      "total": 142,
      "vocab_section": 38,
      "grammar_reading_section": 65,
      "listening_section": 39,
      "passed": true,
      "date": "date"
    }
  },
  "anki_stats": {
    "N5_Vocabulary": {"cards_due": 12, "retention_rate": 0.87}
  },
  "level_unlock_status": {
    "N5": "completed",
    "N4": "in_progress",
    "N3": "locked"
  },
  "unlock_conditions": {
    "N4": "Complete N5 M4 mock exam with score ≥ 80/180"
  }
}
```

---

### TASK 7 — METADATA & MANIFEST

Generate an imsmanifest.xml-compatible metadata structure for all SCOs:

```xml
<resource identifier="N5-M01-L01" 
          type="webcontent" 
          adlcp:scormtype="sco"
          href="N5/M01/L01/index.html">
  <metadata>
    <lom:general>
      <lom:title><lom:string>N5 · M1 · L1 — Self-Introduction</lom:string></lom:title>
      <lom:language>ja</lom:language>
      <lom:description>Introduces は・です・か・の sentence structure</lom:description>
    </lom:general>
    <lom:educational>
      <lom:difficulty>very easy</lom:difficulty>
      <lom:typicallearningtime>PT90M</lom:typicallearningtime>
    </lom:educational>
  </metadata>
</resource>
```

---

## BUILD ORDER PRIORITY

If you cannot complete everything in one session, prioritize:

1. **TASK 1** (Course Structure) — Do FIRST. This is the skeleton.
2. **TASK 4** (Mock Exams) — High priority. These are the level gates.
3. **TASK 2** (Quiz Bank) — Build for N5 first, then each level.
4. **TASK 3** (Anki Decks) — Build N5 vocabulary deck first.
5. **TASK 5** (PDF specs) — After all digital content is defined.
6. **TASK 6** (Progress tracking) — After content structure is complete.
7. **TASK 7** (Manifest) — Final step.

---

## IMPORTANT RULES

1. **Never skip levels.** Build N5 fully before starting N4.
2. **Preserve the MAIN/OPTIONAL split.** Every quiz question must be tagged with its track.
3. **Keep Japanese text as-is.** Do not translate Japanese content unless specifically creating an English explanation field.
4. **Use the CURRICULUM_STRUCTURE_MAP** (first section in the document) as the authoritative lesson index.
5. **Every mock exam must include:** section breakdown scores, pass/fail per section (not just overall), answer explanations in Japanese AND English.
6. **Anki decks must be exportable** — output as TSV (tab-separated) which Anki can import directly.

---

## OUTPUT FORMAT

For each task, output in the most LMS-compatible format:
- Course structure → Markdown outline
- Quiz banks → JSON
- Anki decks → TSV
- Mock exams → JSON
- PDF workbook specs → Markdown
- Progress schema → JSON
- Manifest → XML snippet

---

## HOW TO START

After reading the uploaded document, begin with this exact response structure:

```
## TASK 1 — COURSE STRUCTURE
[Complete output]

## TASK 1 COMPLETE ✅
Ready for TASK 2. Type "continue" to proceed.
```

Wait for my "continue" command between tasks so I can verify each one before proceeding.

**BEGIN NOW with TASK 1.**

---

---

## ═══════════════════════════════════════════════
## PROMPT VERSION 2 — TARGETED BUILD
## Use this for specific components only
## ═══════════════════════════════════════════════

### 2A — Build Quiz Bank for One Level Only

> I've uploaded the 日本語大学 curriculum. Using the content in the N[X] sections only, build a complete quiz bank for JLPT N[X]. Format as JSON with fields: q_id, type, question, options (array of 4), correct (0-indexed), explanation, skill, difficulty. Extract questions from every Exercise Set, Review Questions section, and the Mock Exam. Output all questions for N[X] only.

---

### 2B — Build Anki Deck for One Level

> I've uploaded the 日本語大学 curriculum. Extract ALL vocabulary tables from the N[X] sections (rows formatted as | # | Japanese | Furigana | Meaning |). Output as TSV with columns: Japanese_Furigana | English_Meaning | Example_Sentence | Tags. Tags should include: N[X], the module number, and the skill type (vocabulary/kanji/grammar). Ready to import into Anki.

---

### 2C — Build One Level's SCORM Structure Only

> I've uploaded the 日本語大学 curriculum. Create the complete SCORM unit structure for N[X] only. For each of the 4 modules and 20 lessons, output: SCORM_ID | Lesson_Title | Duration_Minutes | Learning_Objectives (bullet list) | Track (MAIN or OPTIONAL) | Prerequisites. Format as a table.

---

### 2D — Build Mock Exam SCORM Package

> I've uploaded the 日本語大学 curriculum. Find the MOCK_EXAM_N[X] section. Convert the entire mock exam into a SCORM-compatible assessment JSON. Include: exam metadata (timing, pass score, section minimums), all questions with 4 options and correct answer index, answer explanations in both Japanese and English, scoring logic (total + per-section with section minimums), and pass/fail feedback messages. Output complete JSON.

---

### 2E — Build PDF Workbook for One Module

> I've uploaded the 日本語大学 curriculum. Generate the complete content spec for N[X] Module [M] PDF workbook. For each of the 20 lessons in that module, output: lesson title, vocabulary table (full), grammar point summaries (concise), exercise sets with answer keys, and writing prompts. Format as clean Markdown suitable for conversion to PDF with pandoc or similar.

---

### 2F — Build Progress & Gamification System

> I've uploaded the 日本語大学 curriculum. Design a complete learner progress and gamification system. Include: (1) XP point system (how many XP per lesson/quiz/mock exam), (2) badges/achievements (e.g., "Kanji Master N5", "Perfect Mock N3"), (3) level unlock gates (criteria to advance from N5→N4 etc.), (4) streak system, (5) leaderboard schema, (6) the full data model as JSON. Make it motivating for a solo international student in Tokyo.

---

---

## ═══════════════════════════════════════════════
## PROMPT VERSION 3 — QUICK REFERENCE OUTPUTS
## For rapid single-output requests
## ═══════════════════════════════════════════════

### 3A — Generate imsmanifest.xml
> Using the SCORM IDs from the 日本語大学 curriculum (F01-F07, N5-M01-L01 through N1-M04-L20, SUP-A through SUP-I, MOCK-N5 through MOCK-N1), generate a complete imsmanifest.xml file for SCORM 1.2 compliance. Include all resources, organizations, and items in the correct hierarchy.

---

### 3B — Moodle Course Backup XML
> Convert the 日本語大学 curriculum structure into a Moodle-compatible course backup XML (moodle2 format). Create sections for each module, activities for each lesson (as SCORM activities or lessons), quizzes for each Exercise Set, and a gradebook structure that tracks: lesson completion, quiz scores, and mock exam results.

---

### 3C — Canvas Course Import
> Create a Canvas LMS course import package (course.imscc format spec) for the 日本語大学 N5 level. Include: modules for each of the 4 N5 modules, pages for each lesson, quizzes from exercise sets, assignments for writing practice, and a final exam (MOCK-N5). Use the Canvas QTI format for quiz questions.

---

### 3D — SCORM 2004 Sequencing Rules
> For the 日本語大学 curriculum, write SCORM 2004 sequencing and navigation rules that: (1) require lessons to be completed in order within each module, (2) require 75% quiz score to advance to the next lesson, (3) require passing the module mock exam before unlocking the next module, (4) allow OPTIONAL lessons to be accessed at any time without gating, (5) allow review of any completed lesson at any time.

---

### 3E — xAPI (Tin Can) Statement Templates
> Create xAPI statement templates for the 日本語大学 LMS. Include statements for: lesson_started, lesson_completed, quiz_attempted, quiz_passed, quiz_failed, vocabulary_reviewed (Anki), mock_exam_passed, mock_exam_failed, level_unlocked, streak_maintained. Use proper xAPI verb URIs and include example actor/object/result structures.

---

### 3F — Learning Path JSON for LMS
> Output the complete 日本語大学 learning path as a machine-readable JSON file for any modern LMS. Include: all 400+ lessons in order, dependencies (prerequisites), estimated_minutes per lesson, track (MAIN/OPTIONAL), level, module, skills_covered, and pass_threshold for any associated quiz. This should work as a learning path import for platforms like Docebo, TalentLMS, or LearnDash.

---

---

## ═══════════════════════════════════════════════
## HOW TO USE THESE PROMPTS WITH CHATGPT
## ═══════════════════════════════════════════════

### Method 1 — ChatGPT Plus (File Upload)
1. Open ChatGPT (GPT-4o or above)
2. Upload: FINAL_LMS_HANDOFF_COMPLETE.md
3. Wait for "File analyzed" confirmation
4. Paste PROMPT VERSION 1 and send
5. Type "continue" between tasks

### Method 2 — API (For Developers)
```python
import anthropic  # or openai

with open("FINAL_LMS_HANDOFF_COMPLETE.md", "r") as f:
    curriculum = f.read()

prompt = f"""
{curriculum}

---

{PASTE_PROMPT_VERSION_1_HERE}
"""

# Send to your preferred LLM API
```

### Method 3 — Split by Section (If Context Too Large)
If ChatGPT hits context limits, split the file:
1. Upload CURRICULUM_STRUCTURE_MAP.md first → run TASK 1
2. Upload N5 files → run TASK 2 for N5
3. Upload N4 files → run TASK 2 for N4
4. Continue per level
5. Upload MOCK_EXAM files → run TASK 4
6. Upload all remaining → run TASK 7

### Method 4 — Iterative Building (Safest)
1. Start with just PROMPT 2C for N5 (SCORM structure only)
2. Verify output → "Continue with N4"
3. After all structures: PROMPT 2B for N5 Anki decks
4. After all Anki: PROMPT 2D for N5 mock exam
5. Build one complete level at a time

---

## VERIFICATION CHECKLIST
After ChatGPT completes each task, verify:

- [ ] All 400 lessons appear in TASK 1 output (not abbreviated)
- [ ] SCORM IDs match the N5-M01-L01 format exactly
- [ ] MAIN/OPTIONAL track labels are on every lesson
- [ ] Quiz JSON is valid (use jsonlint.com)
- [ ] Anki TSV has the right column count (importable)
- [ ] Mock exams have SECTION minimums (not just total pass score)
- [ ] Answer explanations exist for every mock exam question
- [ ] Japanese text is preserved exactly (no mistranslation)
- [ ] Supplement modules are labeled SUP-A through SUP-I
