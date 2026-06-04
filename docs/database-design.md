# Database Design

## Core Entities

- users
- courses
- levels
- modules
- lessons
- quizzes
- questions
- flashcards
- assignments
- progress

## Hierarchy

Course -> Level -> Module -> Lesson

Lessons may have quizzes, flashcards, and assignments. Progress records are user-specific and can reference a lesson, quiz, or flashcard set.

## Design Notes

- Store imported content references and metadata, not raw authoring workflows.
- Preserve source identifiers such as `N5-M01-L01`.
- Keep import status and validation status visible for admin workflows.
- Prefer additive migrations for future schema evolution.

