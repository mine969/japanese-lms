# Architecture

## Purpose

The JLPT LMS stores imported lesson assets, quizzes, flashcards, assignments, and learner progress for JLPT N5 to N1 study.

The system separates curriculum/content generation from LMS delivery. This repository owns ingestion, storage, APIs, authentication, progress tracking, and deployment.

## Components

- FastAPI backend exposes REST endpoints.
- PostgreSQL stores users, course hierarchy, assessments, flashcards, assignments, and progress.
- Import scripts transform approved source content into LMS-ready JSON and database records.
- Future frontend consumes the API using JWT authentication.

## Boundaries

In scope:

- LMS architecture
- API contracts
- Database schema
- Import pipeline
- Validation utilities
- Deployment configuration

Out of scope:

- Rewriting lesson content
- Regenerating curriculum
- Replacing content-authoring workflows

## Handoff Rule

Handoffs must be incremental. Update only the affected module, route, model, script, or document. Do not restructure the project or regenerate unrelated files.

