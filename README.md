# JLPT LMS

![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Database](https://img.shields.io/badge/database-PostgreSQL-336791)
![Auth](https://img.shields.io/badge/auth-JWT-111827)
![Deploy](https://img.shields.io/badge/deploy-Docker-2496ED)
![Phase](https://img.shields.io/badge/phase-1_scaffold-f59e0b)
![License](https://img.shields.io/badge/license-MIT-blue)

Software architecture for a JLPT N5 to N1 learning management system.

This repository owns the LMS platform: backend APIs, database design, content import paths, quiz/flashcard export structure, deployment, and handoff discipline. Japanese lesson writing and curriculum generation are handled by a separate content workflow.

## Project Snapshot

| Area | Status |
| --- | --- |
| Backend | FastAPI beta API with auth, lesson, quiz, flashcard, progress, dashboard, and admin import routes |
| Database | PostgreSQL schema, SQLAlchemy models, and startup seed loading |
| Auth | JWT registration/login/me flow with password hashing |
| Deployment | Dockerfile and Docker Compose for backend + Postgres |
| Import Pipeline | Markdown-to-LMS JSON packaging for provided handoff lessons |
| Frontend | Planned for Next.js or React |

## Current Lesson Intake

| Lesson | Source Status | LMS Work Needed |
| --- | --- | --- |
| N5-M01-L01 | Complete source lesson | Import validation |
| N5-M01-L02 | Complete source lesson | Quiz and flashcard repair |
| N5-M01-L03 | Provisional complete | Review before import |
| N5-M01-L04 onward | Placeholder | Await source content |

## Quick Start

```bash
docker compose -f deployment/docker-compose.yml up --build
```

Health check:

```bash
curl http://localhost:8000/health
```

Interactive API docs:

```text
http://localhost:8000/docs
```

Beta admin seed:

```text
email: admin@example.com
password: change-me
```

Change this before exposing a public beta.

## Repository Map

```text
backend/      FastAPI app, routers, schemas, models, tests
content/      Source lesson intake, processed lesson JSON, metadata, placeholders
database/     SQL schema and seed files
deployment/   Docker Compose and GitHub Actions
docs/         Architecture, API, database, import pipeline, project status
flashcards/   Anki, Quizlet, and LMS JSON export areas
handoff/      Claude and ChatGPT LMS handoff notes
quizzes/      Quiz source, LMS JSON, and Moodle XML export areas
scripts/      Import and validation utilities
```

## API Surface

Base path: `/api/v1`

- `/auth/register`, `/auth/login`, `/auth/me`
- `/lessons`, `/lessons/courses`, `/lessons/{lesson_code}`
- `/quizzes`, `/quizzes/{lesson_code}`, `/quizzes/{lesson_code}/submit`
- `/flashcards`, `/flashcards/{lesson_code}`
- `/progress/summary`, `/progress/lesson`
- `/dashboard`
- `/admin/import/status`, `/admin/import/seed`

## Documentation

- [Architecture](docs/architecture.md)
- [API Design](docs/api-design.md)
- [Database Design](docs/database-design.md)
- [Import Pipeline](docs/import-pipeline.md)
- [Project Status](docs/project-status.md)

## Development Rules

Future handoffs must be scoped and incremental.

- Do not redesign architecture.
- Do not change API contracts without explicit approval.
- Do not change folder structure.
- Do not regenerate the whole project.
- Do not rewrite Japanese lessons in this repository.
- Update only affected modules, scripts, schemas, routes, or docs.

## License

MIT License. See [LICENSE](LICENSE).
