# Nihongo Daigaku: Japanese LMS

Nihongo Daigaku is a self-contained Japanese learning web app for studying from pre-JLPT foundations through JLPT N1, with additional real-world Japanese and IT professional Japanese material.

The app is designed as a single offline-ready `index.html` file. It has no CDN, no external JavaScript, no external CSS, no backend, and no build step.

## Live Site

```text
https://mine969.github.io/japanese-lms/
```

## Course Scope

The course is built from a complete JLPT 0 to N1 handoff document and includes:

- Pre-N5 foundations: hiragana, katakana, pitch accent, IME input, kanji strategy, and survival Japanese.
- JLPT N5 to N1 curriculum map and structured study content.
- Grammar, vocabulary, kanji, reading, listening, and mock-exam preparation.
- Real-world Japanese supplements for life in Japan, dialects, slang, culture, media, and business situations.
- IT Professional Japanese, including programming vocabulary, Git, code review, DevOps, cloud, cybersecurity, project management, Slack/email templates, and Japanese IT workplace language.
- Mock exam sections for JLPT practice and review loops.

## Learning Paths

The app includes eight study paths:

- JLPT Exam Sprint
- Life in Japan
- Fluency First
- IT Professional
- Business & Keigo
- Media Reader
- Kanji Builder
- Mock Exam Loop

The path quiz asks about the learner's goal, current level, and study style, then recommends a route through the material.

## App Features

- Four-page app: home, path quiz, course library, and reader.
- Embedded Markdown curriculum loaded from inside `index.html`.
- Works from `file://` and GitHub Pages.
- Local progress tracking with `localStorage`.
- Bookmarks, notes, recent lessons, and last-read tracking.
- Export/import progress as JSON.
- Reader font controls using fixed size indexes.
- Chapter search and global search.
- Table of contents generation for longer chapters.
- Copy buttons for code blocks.
- Four visual themes: Kuro, Sakura, Matcha, and Denki.
- Print-friendly reader layout.
- Inline service worker for installable/offline behavior on supported browsers.

## Repository Structure

This repository is intentionally minimal:

```text
.github/workflows/deploy.yml  GitHub Pages deployment workflow
README.md                     Course and project documentation
index.html                    Full standalone offline LMS app
```

## Deployment

GitHub Pages deploys automatically when changes are pushed to `main`.

The deployment workflow uploads the repository root, so `index.html` is served directly at the site root.

## Offline Use

Open `index.html` directly in a browser to use the course offline.

Browser data such as progress, bookmarks, notes, and recent lessons is stored locally on the same device and browser profile.

## Attribution

Author: Hein Htet Zaw  
Content: AI-driven

## Maintainer Notes

- Keep the app as a single `index.html` file.
- Do not add external dependencies unless the project direction changes.
- Keep the repository minimal: `README.md`, `index.html`, and `.github/workflows/deploy.yml`.
- When updating course content, regenerate or edit the embedded Markdown inside `index.html`.
