# Roadmap

## v0.1.0

- Public seed with dry-run maintainer workflows.
- Prompt files for research, execution planning, memory, and audit.
- Tests, CI, examples, security policy, issue templates, and PR template.

## v0.1.1

- Codex CLI provider presets for OpenAI-compatible maintainer workflows.
- Provider preset documentation.
- Tests for preset listing and safe command selection.

## v0.1.2

- Golden prompt tests for issue triage and pull request review workflows.
- Evaluation documentation for reviewing prompt changes.

## v0.2.0

- GitHub issue and pull request import helpers.
- Synthetic importer fixtures and tests.
- Demo documentation for the issue triage and PR review loop.

## v0.2.1

- Release workflow golden prompt coverage.
- Release-specific output checks for changelog coverage, migration notes,
  publication blockers, and verification steps.

## v0.2.2

- Practical maintainer checklist examples for issue triage, pull request review,
  release preparation, and final audit.
- Dry-run tests that keep example workflow inputs executable.

## v0.2.3

- Direct `gh`-backed import commands for GitHub issue and pull request URLs.
- Explicit opt-in before shelling out to GitHub CLI.
- Dry-run next-step guidance after import so maintainers inspect prompts first.

## v0.2.4

- Public maintenance log for issue, release, CI, and external OSS feedback
  evidence.
- README CI status badge.
- CI compile checks and CLI smoke checks.

## v0.2.5

- Local setup doctor for Python, workflow, preset, and GitHub CLI checks.
- Doctor command configured in CI smoke checks.
- Documentation for non-fatal `gh` warnings before live URL imports.

## v0.2.6

- Machine-readable `maintainer-agent doctor --json` diagnostics.
- Sanitized GitHub CLI version-check failure messages.
- CI smoke coverage for both human-readable and JSON doctor output.

## v0.2.7

- Strict doctor mode for release-readiness checks that should fail on warnings.
- Strict-mode tests for both terminal and JSON output.
- CI smoke coverage for `maintainer-agent doctor --json --strict`.

## v0.3.0

- Release workflow helpers for changelog generation from GitHub context.
- Maintainer memory checklist with explicit promotion and retirement rules.
- Security-focused audit prompts for dependency, permission, and data-flow changes.

## v1.0.0

- Stable workflow config format.
- Documented maintainer playbooks.
- Compatibility tests for supported provider command presets.
