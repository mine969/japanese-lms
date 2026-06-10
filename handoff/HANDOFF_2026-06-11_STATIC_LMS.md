# Handoff: Nihongo Daigaku Static LMS

Date: 2026-06-11  
Repo: `F:\Github\japanese-lms-main`  
Primary mode: zero-budget static LMS

## Current State

The project is a static-first LMS package generated from the active June 7 handoff and prompt.

Active source files:

- `handoff/final/FINAL_LMS_HANDOFF_COMPLETE_2026-06-07.md`
- `handoff/final/GPT_LMS_BUILD_PROMPT_2026-06-07.txt`
- `handoff/final/SUPPLEMENT_J_IT_Japanese_Complete.md`

Do not use old handoff files as curriculum source.

## What Works

- Static app opens at `http://127.0.0.1:4180/#/dashboard` when served from `web/`
- Hash routes work for:
  - `#/dashboard`
  - `#/courses`
  - `#/package`
  - `#/sources`
  - `#/progress`
  - `#/lesson/<NODE_ID>`
- Legacy lesson hashes redirect, e.g. `#/N5-OPT-01` -> `#/lesson/N5-OPT-01`
- Local progress is stored in `localStorage`
- LMS package exports are visible from the Package page
- Generated data currently indexes 942 nodes

## Generated Scope

| Area | Count |
| --- | ---: |
| Total indexed nodes | 942 |
| Formal JLPT lessons | 400 |
| Foundations | 7 |
| Level optional lessons | 30 |
| Mock exam SCOs | 5 |
| Supplement SCOs | 500 |
| Source documents | 31 |
| Direct extracts | 181 |

## Key Files

| File | Purpose |
| --- | --- |
| `scripts/build_static_lms.py` | Main builder |
| `web/index.html` | Static app shell |
| `web/assets/app.js` | Routing, rendering, local progress |
| `web/assets/styles.css` | Layout and responsive styles |
| `web/data/learning-path.json` | Generated lesson/SCO index |
| `web/data/lms-package/package-index.json` | Package artifact index |
| `docs/full-documentation.md` | Full documentation |

## Local Run

```powershell
python -B scripts\build_static_lms.py
python -m http.server 4180 -d web
```

Open:

```text
http://127.0.0.1:4180/#/dashboard
```

If the site does not open, the most likely cause is that the static server is not running.

## Validation Commands

```powershell
python -m py_compile scripts\build_static_lms.py
node --check web\assets\app.js
@'
import json, pathlib
for p in pathlib.Path("web/data").rglob("*.json"):
    json.loads(p.read_text(encoding="utf-8"))
print("json ok")
'@ | python -
```

## Architecture Rules

- Preserve the static, zero-budget deployment path.
- Preserve source Japanese text.
- Do not invent educational content.
- Do not regenerate from old handoffs.
- Do not make the optional FastAPI backend required for learner use.
- Keep generated data and source handoff changes committed together.

## Known Limitations

- Quiz banks are mostly skeletons unless safely extractable from structured source.
- Some lesson nodes open their source document rather than a clean individual lesson extract.
- Supplements are indexed as SCO slots, but many are broad source-backed items.
- Progress is device/browser-local only.

## Recommended Next Agent Steps

1. Confirm GitHub Pages is enabled and serving `web/`.
2. Add a package download/bundle script if the LMS artifacts need one-click export.
3. Improve parser extraction for exercises, vocabulary tables, and mock exam answers.
4. Add a generated extraction report listing exact skipped sections.
5. Keep all changes incremental and scoped.
