# Project Status

## June 7 Rebuild

The project has been restarted from the new June 7 handoff and prompt. The active source of truth is `handoff/final/FINAL_LMS_HANDOFF_COMPLETE_2026-06-07.md`; the active build prompt is `handoff/final/GPT_LMS_BUILD_PROMPT_2026-06-07.txt`.

The learner-facing app runs as a zero-budget static LMS in `web/`, with local progress stored in browser `localStorage`. The previous FastAPI backend remains available as optional tooling, but it is not required for learner use.

## Generated Scope

| Area | Count |
| --- | --- |
| Formal JLPT lesson SCOs | 400 |
| Foundations | 7 |
| Level optional lessons | 30 |
| Mock exam SCOs | 5 |
| Supplement SCOs | 450 |
| Total indexed nodes | 892 |
| Source documents | 30 |
| Lesson/source extracts | 82 |

## Static LMS Verification

- June 7 handoff and prompt copied into `handoff/final/`
- Static data builder generated 892 indexed nodes from 30 source documents
- 82 direct lesson/source extracts generated
- LMS package exports generated for course structure, quiz skeleton, Anki TSV, mock specs, workbook specs, progress schema, and IMS manifest
- All generated JSON files parse successfully
- Static site serves locally on `http://127.0.0.1:4180`
- Static app JavaScript syntax check passes
- In-app browser shows the package panel, Task 1-7 links, and Supplements map

## Build Rule

The repo generates LMS-compatible export scaffolds from the prompt while preserving source Japanese and avoiding invented quiz or answer content.

## Architecture Lock

Future contributors must update only affected modules. Do not redesign architecture, change API contracts, change folder structure, or regenerate unrelated project areas.
