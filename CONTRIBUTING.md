# Contributing

This repository is the LMS/software layer for the JLPT N5 to N1 project.

## Scope

Allowed changes:

- FastAPI backend implementation
- PostgreSQL schema and migrations
- JWT auth implementation
- Import and validation scripts
- LMS JSON, quiz, and flashcard tooling
- Documentation for architecture, API contracts, and handoffs

Out of scope:

- Rewriting Japanese lessons
- Regenerating curriculum content
- Changing the repository folder structure without explicit approval
- Replacing the architecture without explicit approval

## Change Discipline

Keep changes small and module-focused.

- Update only files related to the task.
- Prefer additive API/schema changes.
- Document any contract change before implementation.
- Include validation steps in handoff notes or pull request summaries.

## Local Checks

```bash
python -B -m pytest backend/tests
docker compose -f deployment/docker-compose.yml config
```

