# Maintainer Checklist Examples

These examples show how maintainers can turn common project situations into
repeatable dry-run workflows. All project names, issues, pull requests, and
release details are synthetic.

## Small library issue triage

Context file:

```text
examples/maintainer-checklists/small-library-issue.md
```

Command:

```bash
maintainer-agent triage examples/maintainer-checklists/small-library-issue.md \
  --dry-run \
  --no-prompts
```

Maintainer checklist:

- Confirm the reporter supplied a minimal reproduction.
- Separate expected API behavior from a regression.
- Ask for one missing environment detail only if it changes the decision.
- Require a regression test before accepting a fix.
- Decide label and release impact before implementation starts.

Expected dry-run shape:

```text
## research
### Output
DRY RUN: prompt preview only

## executor
### Output
DRY RUN: prompt preview only

## memory
### Output
DRY RUN: prompt preview only

## audit
### Output
DRY RUN: prompt preview only
```

## CLI tool pull request review

Context file:

```text
examples/maintainer-checklists/cli-tool-pr.md
```

Command:

```bash
maintainer-agent review examples/maintainer-checklists/cli-tool-pr.md \
  --dry-run \
  --no-prompts
```

Maintainer checklist:

- Verify default command output remains backward compatible.
- Treat new JSON fields as a public contract.
- Ask for tests across success, degraded, and error states.
- Check whether a schema version or experimental note is needed.
- Require a changelog note when user-facing behavior changes.

Expected dry-run shape:

```text
## research
### Output
DRY RUN: prompt preview only

## executor
### Output
DRY RUN: prompt preview only

## audit
### Output
DRY RUN: prompt preview only
```

## Web app release preparation

Context file:

```text
examples/maintainer-checklists/web-app-release.md
```

Command:

```bash
maintainer-agent release examples/maintainer-checklists/web-app-release.md \
  --dry-run \
  --no-prompts
```

Maintainer checklist:

- Separate user-facing changes from admin-only changes.
- Call out migrations, rollback notes, and compatibility risks.
- Verify each release note maps to a merged change.
- List publication blockers before drafting final announcement text.
- Keep release checks tied to commands or manual verification steps.

Expected dry-run shape:

```text
## research
### Output
DRY RUN: prompt preview only

## executor
### Output
DRY RUN: prompt preview only

## audit
### Output
DRY RUN: prompt preview only
```

## Web app final audit

Context file:

```text
examples/maintainer-checklists/web-app-final-audit.md
```

Command:

```bash
maintainer-agent audit examples/maintainer-checklists/web-app-final-audit.md \
  --dry-run \
  --no-prompts
```

Maintainer checklist:

- Put release-blocking risks before nice-to-have follow-ups.
- Check whether migration, auth, and Docker evidence covers supported setups.
- Confirm release notes match the operational risk.
- Identify the next verification command or manual check for each gap.
- Avoid marking a release as latest while known blockers remain untested.

Expected dry-run shape:

```text
## audit
### Output
DRY RUN: prompt preview only
```
