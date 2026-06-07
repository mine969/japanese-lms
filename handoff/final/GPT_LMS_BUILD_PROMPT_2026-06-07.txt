You are an expert instructional designer and LMS developer. I have uploaded a complete Japanese language curriculum called 日本語大学 (Nihongo Daigaku). Your job is to transform this curriculum source document into a fully structured LMS package.

CURRICULUM OVERVIEW
This is a complete JLPT N5→N1 Japanese language learning system for:

Learner profile: International student in Tokyo, Japan. Native languages: English, Myanmar, basic Chinese, basic Thai. Starting from zero Japanese.
Goal: Pass JLPT N1 and achieve natural conversational fluency.
Structure: 5 JLPT levels (N5→N4→N3→N2→N1) × 4 modules × 20 lessons = 400 formal lessons, plus Foundations (F01–F07) and Supplement modules (SUP-A through SUP-I).
Two tracks: 🟦 MAIN (JLPT exam-focused) and 🟩 OPTIONAL (real-world Japanese beyond the exam).


YOUR BUILD TASKS
Work through these tasks in order. Complete each task fully before moving to the next.

TASK 1 — SCORM COURSE STRUCTURE (Do this first)
Create the complete course architecture as a structured outline. For every level (Foundations → N5 → N4 → N3 → N2 → N1 → Supplements), output:
COURSE: [Level Name]
  UNIT: Module 1 — [Module Title]
    SCO: [SCORM ID] | [Lesson Title] | [Est. minutes] | Track: MAIN/OPTIONAL
    SCO: [SCORM ID] | [Lesson Title] | [Est. minutes] | Track: MAIN/OPTIONAL
    ...
  UNIT: Module 2 — [Module Title]
    ...
SCORM ID format:

Foundations: F01, F02, F03...F07
JLPT lessons: N5-M01-L01, N5-M01-L02...N1-M04-L20
Supplements: SUP-A-01, SUP-A-02...SUP-I-50
Mock exams: MOCK-N5, MOCK-N4, MOCK-N3, MOCK-N2, MOCK-N1

Track labels:

🟦 MAIN = Required for JLPT exam pass
🟩 OPTIONAL = Real-world/enrichment (beyond exam)

Output the full outline for all levels — do not abbreviate.

TASK 2 — QUIZ BANK (Per Level)
For each lesson, extract and format quiz questions in this JSON structure:
json{
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
Question types to create:

multiple_choice — 4 options, 1 correct (from Exercise Sets and Review Questions)
fill_blank — complete the sentence
matching — match Japanese to English
reading_comprehension — passage + questions
listening_comprehension — transcript + questions

Sources for questions:

Exercise Set A/B/C → multiple_choice and fill_blank
Review Questions → fill_blank or short_answer
Reading Practice questions → reading_comprehension
Listening Practice questions → listening_comprehension
Mock Exam questions → timed_assessment

Tag every question with:
level, module, lesson, skill (文字語彙/文法/読解/聴解/会話/作文), difficulty

TASK 3 — ANKI FLASHCARD DECKS
Extract all vocabulary tables (marked with | # | Japanese | Furigana | Meaning |) and output Anki-compatible TSV files.
Deck structure:
Deck name: 日本語大学::N5::Vocabulary
Deck name: 日本語大学::N5::Kanji
Deck name: 日本語大学::N5::Grammar_Sentences
Deck name: 日本語大学::N4::Vocabulary
... (continue for all levels)
Deck name: 日本語大学::CORE::Onomatopoeia
Deck name: 日本語大学::CORE::Business_Japanese
Deck name: 日本語大学::CORE::Four_Character_Compounds
Deck name: 日本語大学::CORE::Proverbs
Card format (tab-separated):
Front	Back	Tags
{Japanese} ({Furigana})	{English meaning}\n\n例: {example sentence}	N5 vocabulary M01 L04
Kanji card format:
Front	Back	Tags
{Kanji} — {meaning}	Onyomi: {on}\nKunyomi: {kun}\nExample: {word} ({reading}) — {meaning}	N5 kanji
Grammar card format:
Front	Back	Tags
～{pattern}	Meaning: {explanation}\nStructure: {formation}\nExample: {sentence}\nTranslation: {translation}	N5 grammar M01

TASK 4 — MOCK EXAMINATION SCORM PACKAGES
For each level's mock exam (found in MOCK_EXAM_N5_N4, MOCK_EXAM_N3_N2, MOCK_EXAM_N1), create a timed SCORM assessment package spec:
json{
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
Include all questions from the mock exam JSON, with correct answers and explanations.

TASK 5 — PDF WORKBOOK SPECS
For each module (e.g., N5 Module 1), define the PDF workbook contents:
markdown## PDF WORKBOOK: N5_M1_Workbook.pdf
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
Specify page layout, fonts, and any formatting notes.

TASK 6 — PROGRESS TRACKING SCHEMA
Define the learner progress data model:
json{
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

TASK 7 — METADATA & MANIFEST
Generate an imsmanifest.xml-compatible metadata structure for all SCOs:
xml<resource identifier="N5-M01-L01" 
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

BUILD ORDER PRIORITY
If you cannot complete everything in one session, prioritize:

TASK 1 (Course Structure) — Do FIRST. This is the skeleton.
TASK 4 (Mock Exams) — High priority. These are the level gates.
TASK 2 (Quiz Bank) — Build for N5 first, then each level.
TASK 3 (Anki Decks) — Build N5 vocabulary deck first.
TASK 5 (PDF specs) — After all digital content is defined.
TASK 6 (Progress tracking) — After content structure is complete.
TASK 7 (Manifest) — Final step.


IMPORTANT RULES

Never skip levels. Build N5 fully before starting N4.
Preserve the MAIN/OPTIONAL split. Every quiz question must be tagged with its track.
Keep Japanese text as-is. Do not translate Japanese content unless specifically creating an English explanation field.
Use the CURRICULUM_STRUCTURE_MAP (first section in the document) as the authoritative lesson index.
Every mock exam must include: section breakdown scores, pass/fail per section (not just overall), answer explanations in Japanese AND English.
Anki decks must be exportable — output as TSV (tab-separated) which Anki can import directly.


OUTPUT FORMAT
For each task, output in the most LMS-compatible format:

Course structure → Markdown outline
Quiz banks → JSON
Anki decks → TSV
Mock exams → JSON
PDF workbook specs → Markdown
Progress schema → JSON
Manifest → XML snippet


HOW TO START
After reading the uploaded document, begin with this exact response structure:
## TASK 1 — COURSE STRUCTURE
[Complete output]

## TASK 1 COMPLETE ✅
Ready for TASK 2. Type "continue" to proceed.
Wait for my "continue" command between tasks so I can verify each one before proceeding.
BEGIN NOW with TASK 1.
