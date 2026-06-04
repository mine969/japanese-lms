# JLPT LMS

Phase 1 repository for an LMS that will host, import, assess, and track JLPT N5 to N1 learning materials.

This repository is the software architecture layer only. Japanese lesson writing, curriculum generation, and educational content revisions are handled by a separate AI/content workflow.

## Tech Stack

- Backend: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Validation: Pydantic
- Auth: JWT bearer tokens
- Deployment: Docker and Docker Compose
- Future frontend: Next.js or React

## Current Status

- Phase: 1 repository scaffold
- Backend: initial FastAPI structure with health check and route groups
- Database: initial SQL schema and SQLAlchemy models
- Content: source/processed/import directories created with status tracking only

## Lesson Status

- N5-M01-L01: Complete source lesson
- N5-M01-L02: Complete source lesson, needs LMS quiz + flashcard repair
- N5-M01-L03: Provisional complete
- N5-M01-L04 onward: Placeholder

## Setup

```bash
docker compose -f deployment/docker-compose.yml up --build
```

Backend health check:

```bash
curl http://localhost:8000/health
```

API docs:

```text
http://localhost:8000/docs
```

## Repository Rules

Future Claude and ChatGPT handoffs must update only affected modules.

- Do not redesign architecture.
- Do not change API contracts without explicit approval.
- Do not change folder structure.
- Do not regenerate the whole project.
- Do not rewrite Japanese lessons in this repository.
