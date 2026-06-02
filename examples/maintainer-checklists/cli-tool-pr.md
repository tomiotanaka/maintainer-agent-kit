# CLI Tool Pull Request Review Context

## Project profile

- Project: `northstar-log-demo`
- Type: command-line log shipping tool
- Maintainer risk: breaking automation scripts and CI jobs
- Release channel: minor releases with changelog notes

## Pull request summary

The pull request adds `--json` output to `northstar-log status`.

## Patch notes

- Adds a `StatusRecord` dataclass.
- Adds `--json` to the `status` subcommand.
- Keeps the existing human-readable text output as the default.
- Adds one unit test for the happy path.

## Diff summary

```text
src/northstar_log/cli.py    | 48 +++++++++++++++++++++++++++++++++++++-----
src/northstar_log/status.py | 31 +++++++++++++++++++++++++++
tests/test_status_cli.py | 24 +++++++++++++++++++++
```

## Maintainer concerns

- JSON field names will become a public contract once released.
- The test only covers `healthy` status, not degraded or error states.
- Existing scripts may parse stdout; default behavior must stay unchanged.
- The changelog does not mention the new machine-readable output.

## Checklist focus

- Review backward compatibility for default stdout.
- Require tests for degraded and error states.
- Ask whether JSON should include a schema version.
- Decide whether the release note should call this experimental or stable.
