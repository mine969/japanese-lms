# API Design

Base path: `/api/v1`

## Route Groups

- `/auth`: registration, login, token refresh, current user
- `/lessons`: course, level, module, and lesson discovery
- `/quizzes`: quiz metadata, questions, attempts, scoring
- `/flashcards`: flashcard decks and review items
- `/progress`: learner completion and mastery tracking
- `/dashboard`: learner summary data
- `/admin/import`: controlled import and validation endpoints

## Phase 1 Contracts

Phase 1 beta endpoints are backed by SQLAlchemy sessions and startup-seeded LMS assets.

Important contract rule: future work may add fields but should not rename or remove existing response fields without explicit approval.

## Auth

JWT bearer auth protects user-specific dashboard, progress, quiz submission, and admin seed workflows.
