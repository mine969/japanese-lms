# Security

## Reporting

Do not open public issues for secrets, authentication bypasses, or data exposure risks.

Report security concerns privately to the repository owner.

## Current Security Status

Phase 1 contains placeholder JWT configuration and development defaults.

Before production:

- Replace `JWT_SECRET_KEY`.
- Use managed secrets for deployment.
- Enforce password hashing and auth flows.
- Add database migration review.
- Add role-based authorization for admin import endpoints.

