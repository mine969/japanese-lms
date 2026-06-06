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
