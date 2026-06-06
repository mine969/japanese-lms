# Project Status

## Phase 1

The project has been restarted around a zero-budget static LMS. The learner-facing app now lives in `web/`, loads JSON generated from the final complete handoff, and stores progress in browser `localStorage`.

The previous FastAPI backend remains available as optional tooling, but it is no longer required for learner use.

## Lesson Intake Status

| Lesson | Status | LMS Work Needed |
| --- | --- | --- |
| N5-M01-L01 | Complete source lesson | Import validation |
| N5-M01-L02 | Complete source lesson | LMS quiz and flashcards repaired for beta |
| N5-M01-L03 | Provisional complete | Packaged from provided handoff file |
| N5-M01-L04 onward | Placeholder | Await source content |

## Beta Verification

- Python syntax parse: passing
- Docker Compose config: passing
- Backend API smoke tests: passing on Python 3.12
- Docker image build: not run locally because Docker Desktop is not running

## Static LMS Verification

- Final handoff copied into `handoff/final/`
- Static data builder generated 367 indexed nodes from 30 source documents
- 56 direct lesson content extracts generated
- All generated JSON files parse successfully
- Static site serves locally on `http://127.0.0.1:4180`
- Static app JavaScript syntax check passes

## Architecture Lock

Future contributors must update only affected modules. Do not redesign architecture, change API contracts, change folder structure, or regenerate the whole project.
