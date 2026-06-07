# Static Zero-Budget LMS

The primary deployment path is now a static LMS in `web/`.

## Why Static

- No always-on PC
- No paid database
- No backend hosting
- Browser progress saved in `localStorage`
- GitHub Pages can host it for free

## Build

```bash
python scripts/build_static_lms.py
```

Generated files:

- `web/data/summary.json`
- `web/data/learning-path.json`
- `web/data/source-documents.json`
- `web/data/source-docs/*.json`
- `web/data/lessons/*.json`
- `web/data/lms-package/course-structure.md`
- `web/data/lms-package/quiz-bank-skeleton.json`
- `web/data/lms-package/anki-vocabulary.tsv`
- `web/data/lms-package/mock-exams.json`
- `web/data/lms-package/workbook-specs.md`
- `web/data/lms-package/progress-schema.json`
- `web/data/lms-package/imsmanifest.xml`

## LMS Package Exports

The static build also creates LMS-compatible package artifacts from the handoff prompt. These exports preserve the approved source content and avoid inventing quiz answers or lesson text. Items that still need instructional extraction are marked as pending in the generated JSON.

## Run Locally

```bash
python -m http.server 4173 -d web
```

Open:

```text
http://127.0.0.1:4173
```

## Deployment

The GitHub Actions workflow `.github/workflows/static-pages.yml` builds the JSON data and deploys the `web/` folder to GitHub Pages.

## Source Of Truth

`handoff/final/FINAL_LMS_HANDOFF_COMPLETE.md`

The static builder indexes the handoff and preserves full source documents as browser-readable JSON. It does not rewrite Japanese content.
