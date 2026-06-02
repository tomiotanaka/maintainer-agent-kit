# Web App Release Preparation Context

## Project profile

- Project: `boardroom-lite`
- Type: self-hosted web app for team decision logs
- Maintainer risk: database migrations and session behavior
- Release channel: tagged releases with Docker image builds

## Target release

Version: 2.3.0

## Merged changes

- Added project-level decision templates.
- Added a database migration for `decision_template_id`.
- Changed session cookie `SameSite` from `Lax` to `Strict`.
- Fixed a bug where archived projects appeared in global search.
- Updated the Docker image base from Python 3.11 to Python 3.12.

## Known risks

- The migration has only been tested on SQLite, not Postgres.
- The cookie change may affect embedded deployments.
- The Docker base image change may alter native dependency behavior.

## Release checklist input

- Draft release notes for maintainers and self-hosted admins.
- Call out migration and rollback considerations.
- Identify blockers before publishing the release.
- List verification commands that should run before tagging.
