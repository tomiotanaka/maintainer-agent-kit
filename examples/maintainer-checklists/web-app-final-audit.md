# Web App Final Audit Context

## Project profile

- Project: `boardroom-lite`
- Type: self-hosted web app for team decision logs
- Maintainer risk: data loss, auth regressions, and incomplete release notes

## Release candidate

Version: 2.3.0-rc.1

## Pre-release evidence

- Unit tests passed on Python 3.12.
- Browser smoke test passed for login, project creation, and search.
- SQLite migration test passed.
- Postgres migration test has not been run yet.
- Docker image built locally but has not been pulled from the registry.

## Open questions

- Does `SameSite=Strict` break deployments embedded under an internal portal?
- Is there a documented rollback for `decision_template_id`?
- Are release notes clear enough for self-hosted admins?

## Checklist focus

- Identify publication blockers.
- Separate must-fix issues from follow-up issues.
- List verification gaps that should be resolved before marking latest.
- Keep the output concrete enough for a maintainer to act on immediately.
