# Public Maintenance Log

This log records public maintenance work that shaped Maintainer Agent Kit. It is
intentionally limited to public repositories, public issues, public releases,
and synthetic or authorized examples. Do not add private repository data,
customer logs, credentials, browser history, or unpublished vulnerability
details.

## 2026-06-05 - CI and release-readiness evidence

Scope: `tomiotanaka/maintainer-agent-kit`

Maintenance activity:

- Kept GitHub Actions CI running on pushes and pull requests.
- Added manual `workflow_dispatch` support for release-readiness checks.
- Added compile and CLI smoke checks to the CI matrix for Python 3.11 and 3.12.
- Linked CI status from the README first screen.

Why it matters:

Public maintainers need a visible test surface for workflow changes after they
land, not only local checks before publication. The smoke checks cover the core
loop: list workflows, preview issue triage, import a GitHub issue fixture, and
preview the generated triage task.

Evidence:

- CI workflow: `.github/workflows/ci.yml`
- CI status page: https://github.com/tomiotanaka/maintainer-agent-kit/actions/workflows/ci.yml

## 2026-06-03 - Issue to release to closure loop

Scope: `tomiotanaka/maintainer-agent-kit`

Maintenance activity:

- Implemented direct GitHub issue and pull request URL imports behind an
  explicit `--use-gh` opt-in.
- Added tests that mock GitHub CLI calls instead of requiring network access or
  credentials.
- Published v0.2.3.
- Posted a completion note and closed the implementation issue as completed.

Why it matters:

This is the core workflow the project is designed to support: take a maintainer
request, implement a narrow behavior change, verify it, release it, and close the
tracked issue with enough context for future readers.

Evidence:

- Issue: https://github.com/tomiotanaka/maintainer-agent-kit/issues/4
- Release: https://github.com/tomiotanaka/maintainer-agent-kit/releases/tag/v0.2.3
- Main commit: `48976af`

## 2026-06-01 - External OSS readiness feedback

Scope: `Eskasia/smart-contract-security-assistant`

Maintenance activity:

- Responded to a public call for authorized tester feedback.
- Limited testing scope to bundled repository fixtures and avoided third-party,
  private, proprietary, or unauthorized contract code.
- Posted environment, command, result, and scope notes as public feedback.

Why it matters:

Maintainer Agent Kit is aimed at repeatable, reviewable maintenance work, not
unchecked automation. This public feedback example demonstrates the kind of
bounded OSS participation the workflows should preserve: state the authorization
basis, run reproducible checks, report results, and avoid private data.

How this kit models the workflow:

```bash
maintainer-agent import-github issue-url \
  https://github.com/Eskasia/smart-contract-security-assistant/issues/21 \
  --use-gh \
  --output /tmp/scsa-readiness.md
maintainer-agent triage /tmp/scsa-readiness.md --dry-run --no-prompts
maintainer-agent audit /tmp/scsa-readiness.md --dry-run --no-prompts
```

Evidence:

- Issue: https://github.com/Eskasia/smart-contract-security-assistant/issues/21
- Public feedback comment: https://github.com/Eskasia/smart-contract-security-assistant/issues/21#issuecomment-4590990146

## Entry requirements

Before adding an entry, verify:

- the repository, issue, pull request, release, or comment is public;
- the entry does not include secrets or private data;
- commands are reproducible or clearly marked as examples;
- the maintenance value is concrete: triage, review, release, audit, security,
  documentation, testing, or user support.
