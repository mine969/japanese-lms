# Import Pipeline

## Goal

Convert approved external lesson assets into LMS-safe records without rewriting educational content.

## Pipeline

1. Place approved source lesson files in `content/source-lessons/`.
2. Validate metadata and required structure with `scripts/validate_lesson.py`.
3. Convert lesson markdown to LMS JSON with `scripts/import_markdown.py`.
4. Generate quiz JSON from approved quiz source with `scripts/generate_quiz_json.py`.
5. Generate flashcard exports with `scripts/generate_flashcards.py`.
6. Review generated assets before importing to the database.

## Rule

Import scripts transform and validate. They must not rewrite Japanese lessons or invent missing educational content.

