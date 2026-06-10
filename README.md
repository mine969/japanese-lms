# JLPT LMS

![Static LMS](https://img.shields.io/badge/primary-static_LMS-1f7a68)
![Budget](https://img.shields.io/badge/budget-%240-brightgreen)
![Progress](https://img.shields.io/badge/progress-localStorage-b0842b)
![Backend](https://img.shields.io/badge/optional-FastAPI-009688)
![Deploy](https://img.shields.io/badge/deploy-GitHub_Pages-111827)
![License](https://img.shields.io/badge/license-MIT-blue)

Static-first LMS package for a JLPT 0 to N1 Japanese learning system.

The current build is a fresh June 7 rebuild from `handoff/final/FINAL_LMS_HANDOFF_COMPLETE_2026-06-07.md` and `handoff/final/GPT_LMS_BUILD_PROMPT_2026-06-07.txt`. The learner-facing LMS runs from static files in `web/`, loads generated JSON, and stores learner progress in the browser. The FastAPI backend remains optional future/admin tooling.

## Project Snapshot

| Area | Status |
| --- | --- |
| Static LMS | Browser app in `web/` with search, reading view, local progress, and package export links |
| Source | June 7 handoff and prompt in `handoff/final/` |
| Generated Data | 892 SCO/index nodes, source docs, lesson extracts, and LMS package exports in `web/data/` |
| Backend | Optional FastAPI beta API retained for future tooling |
| Database | Not required for learner-facing zero-budget mode |
| Deployment | GitHub Pages workflow for `web/` |

## Current Generated Scope

| Area | Count |
| --- | --- |
| Formal JLPT lesson SCOs | 400 |
| Foundations | 7 |
| Level optional lessons | 30 |
| Mock exam SCOs | 5 |
| Supplement SCOs | 450 |
| Source documents | 30 |
| Extracted lesson/source blocks | 82 |

## Static Quick Start

```bash
python scripts/build_static_lms.py
python -m http.server 4180 -d web
```

Open:

```text
http://127.0.0.1:4180/#/dashboard
```

## Optional Backend

```bash
docker compose -f deployment/docker-compose.yml up --build
```

## Repository Map

```text
web/          Static LMS app and generated JSON data
backend/      Optional FastAPI app, routers, schemas, models, tests
content/      Source lesson intake, processed lesson JSON, metadata, placeholders
database/     SQL schema and seed files
deployment/   Docker Compose and GitHub Actions
docs/         Architecture, API, database, import pipeline, project status
flashcards/   Anki, Quizlet, and LMS JSON export areas
handoff/      Claude and ChatGPT LMS handoff notes
quizzes/      Quiz source, LMS JSON, and Moodle XML export areas
scripts/      Import and validation utilities
```

## Static Data

- `web/data/learning-path.json`
- `web/data/summary.json`
- `web/data/source-documents.json`
- `web/data/source-docs/*.json`
- `web/data/lessons/*.json`
- `web/data/lms-package/*`

## LMS Package Exports

The static builder also generates export artifacts for the updated LMS build prompt:

- Course structure Markdown
- Quiz bank skeleton JSON
- Anki vocabulary TSV
- Mock exam spec JSON
- PDF workbook spec Markdown
- Progress schema JSON
- IMS manifest XML

## Documentation

- [Full Documentation](docs/full-documentation.md)
- [Architecture](docs/architecture.md)
- [API Design](docs/api-design.md)
- [Database Design](docs/database-design.md)
- [Import Pipeline](docs/import-pipeline.md)
- [Project Status](docs/project-status.md)
- [Static Zero-Budget LMS](docs/static-lms.md)

## Handoff

- [June 11 Static LMS Handoff](handoff/HANDOFF_2026-06-11_STATIC_LMS.md)

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
