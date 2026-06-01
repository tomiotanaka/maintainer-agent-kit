# Release Notes Context

## Version

0.2.1

## Merged changes

- Added changelog coverage checks to the release workflow prompt.
- Added golden prompt snapshots for release research, executor, and audit roles.
- Documented release prompt evaluation coverage.

## Compatibility notes

- No command-line interface changes.
- No runtime dependency changes.

## Known risks

- Release notes still come from maintainer-provided context; the workflow does
  not inspect Git history by itself.
