# Nihongo Daigaku Static LMS Documentation

## Purpose

This repository contains a zero-budget, static-first LMS package for `Nihongo Daigaku`, a Japanese learning system covering Foundations, JLPT N5 through N1, optional enrichment lessons, mock exams, and supplement modules.

The learner-facing site is static. It can run on GitHub Pages or any static file host without a backend, database, or always-on PC. Learner progress is saved in browser `localStorage`.

## Current Source Of Truth

Use only these active June 7 source files for the current build:

- `handoff/final/FINAL_LMS_HANDOFF_COMPLETE_2026-06-07.md`
- `handoff/final/GPT_LMS_BUILD_PROMPT_2026-06-07.txt`
- `handoff/final/SUPPLEMENT_J_IT_Japanese_Complete.md`

Older curriculum handoffs are historical only. Do not use them as active curriculum input.

## Current Generated Scope

| Area | Count |
| --- | ---: |
| Total indexed SCO/nodes | 942 |
| Formal JLPT lessons | 400 |
| Foundations | 7 |
| Level optional lessons | 30 |
| Mock exam SCOs | 5 |
| Supplement SCOs | 500 |
| Source documents | 31 |
| Direct lesson/source extracts | 181 |

## Architecture

The app is a static browser application:

```text
handoff/final/*.md, *.txt
        |
        v
scripts/build_static_lms.py
        |
        v
web/data/*.json + web/data/lms-package/*
        |
        v
web/index.html + web/assets/app.js + web/assets/styles.css
```

The optional FastAPI backend remains in `backend/`, but it is not required for the static LMS.

## Main Directories

| Path | Purpose |
| --- | --- |
| `web/` | Static LMS app and generated data |
| `web/assets/` | Browser UI JavaScript and CSS |
| `web/data/` | Generated JSON, source docs, lesson extracts, package exports |
| `scripts/build_static_lms.py` | Main static data/package builder |
| `handoff/final/` | Active source handoff and build prompt |
| `docs/` | Project documentation |
| `backend/` | Optional FastAPI backend retained for future tooling |
| `deployment/` | Docker Compose and GitHub Actions |

## Static Routes

The app uses hash routes so it works on GitHub Pages:

| Route | Purpose |
| --- | --- |
| `#/dashboard` | First-screen dashboard and sitemap |
| `#/courses` | Course, level, module, and gate overview |
| `#/package` | Task 1-7 LMS package exports |
| `#/sources` | Source document library |
| `#/progress` | Local learner progress |
| `#/lesson/N5-M01-L01` | Lesson/source reader |

Legacy lesson hashes such as `#/N5-OPT-01` redirect to `#/lesson/N5-OPT-01`.

## Local Run

Build or rebuild generated data:

```bash
python scripts/build_static_lms.py
```

Serve the static app:

```bash
python -m http.server 4180 -d web
```

Open:

```text
http://127.0.0.1:4180/#/dashboard
```

If the site does not open locally, first check whether the static server is running.

## Generated Data Files

| File/Folder | Description |
| --- | --- |
| `web/data/summary.json` | Counts, levels, source metadata |
| `web/data/learning-path.json` | All indexed lesson/SCO nodes |
| `web/data/source-documents.json` | Source document index |
| `web/data/source-docs/*.json` | Full preserved source document payloads |
| `web/data/lessons/*.json` | Direct lesson/source extracts when parser can identify blocks |

## LMS Package Exports

Generated under `web/data/lms-package/`:

| Artifact | Prompt Task | Format |
| --- | ---: | --- |
| `course-structure.md` | Task 1 | Markdown |
| `quiz-bank-skeleton.json` | Task 2 | JSON |
| `anki-vocabulary.tsv` | Task 3 | TSV |
| `mock-exams.json` | Task 4 | JSON |
| `workbook-specs.md` | Task 5 | Markdown |
| `progress-schema.json` | Task 6 | JSON |
| `imsmanifest.xml` | Task 7 | XML |
| `package-index.json` | Index | JSON |

Important: quiz and answer content is not invented. Empty or skeleton question banks mean extraction is pending or source content was not structured enough for safe extraction.

## Builder Behavior

`scripts/build_static_lms.py`:

- reads the active June 7 source handoff and Supplement J add-on
- splits embedded source documents
- parses `CURRICULUM_STRUCTURE_MAP.md`
- preserves Japanese source text
- creates a complete formal JLPT skeleton
- adds mock exam nodes
- adds SUP-A through SUP-I supplement SCO slots
- writes browser-loadable JSON and LMS package artifacts

The builder intentionally favors traceability over invented content.

## Progress Storage

Learner progress is local only:

```text
localStorage key: nihongo-daigaku-progress
```

No account, server, database, or paid storage provider is required.

## Deployment

The intended zero-budget deployment target is GitHub Pages serving `web/`.

The GitHub Actions workflow for static deployment is in:

```text
.github/workflows/static-pages.yml
```

If Pages is not live, enable GitHub Pages in the repository settings and use the workflow/static site output.

## Verification Checklist

Run before handoff or push:

```bash
python -B scripts/build_static_lms.py
python -m py_compile scripts/build_static_lms.py
node --check web/assets/app.js
```

Validate generated JSON:

```bash
python - <<'PY'
import json, pathlib
for p in pathlib.Path("web/data").rglob("*.json"):
    json.loads(p.read_text(encoding="utf-8"))
print("json ok")
PY
```

On PowerShell, use:

```powershell
@'
import json, pathlib
for p in pathlib.Path("web/data").rglob("*.json"):
    json.loads(p.read_text(encoding="utf-8"))
print("json ok")
'@ | python -
```

Then open:

```text
http://127.0.0.1:4180/#/dashboard
```

Confirm:

- dashboard loads
- routes work
- lesson reader opens
- package links appear
- no JavaScript console errors

## Development Rules

- Do not rewrite Japanese lesson content.
- Do not invent quiz questions, answer keys, or explanations.
- Do not use older handoff files as source of truth.
- Do not redesign the architecture without explicit approval.
- Do not change the folder structure without explicit approval.
- Do not change route/API contracts casually.
- Update only the affected module, file, script, or documentation section.
- If the source handoff changes, rerun the builder and commit generated data together with the source change.

## Recommended Next Work

1. Improve safe quiz extraction from source exercise sections.
2. Add a source-aware Anki extraction report showing skipped tables.
3. Add a static search index for faster filtering across 942 nodes.
4. Add downloadable package bundle generation.
5. Add GitHub Pages deployment status documentation once Pages is enabled.
