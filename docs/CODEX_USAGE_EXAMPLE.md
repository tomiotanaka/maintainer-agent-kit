# Codex Usage Example

This example uses only synthetic pull request metadata from `examples/`. It shows
how a maintainer can import local context, then run one read-only Codex audit
pass.

## Commands

```bash
maintainer-agent import-github pr examples/github-pr.json \
  --files examples/github-pr-files.json \
  --output /tmp/mak-pr.md

maintainer-agent audit /tmp/mak-pr.md \
  --run \
  --preset codex-read-only \
  --no-prompts \
  --timeout 120
```

## Example output

```text
## audit

### Output
**Audit Findings**

1. **High: Retry eligibility is not evidenced.**
   The PR summary says token refresh now retries, but no patch evidence shows
   that retries are limited to transient failures.
   Verification: add tests proving permanent auth errors are attempted exactly
   once and surfaced unchanged, while only transient network/timeout/5xx/429
   cases retry.

2. **High: Total wait time may exceed acceptable auth/CLI behavior.**
   Timeout increased from 5s to 30s. If each retry gets the full timeout, total
   blocking time can become much longer than 30s.
   Verification: add a fake-clock or mocked transport test asserting the maximum
   total elapsed time, including retries/backoff.

3. **Medium: Token rotation/concurrency behavior is not covered by the summary.**
   Refresh-token retry logic can be risky if providers rotate refresh tokens or
   if multiple refreshes run concurrently.

4. **Medium: User-visible timeout change needs release documentation.**
   Moving auth refresh timeout from 5s to 30s changes failure latency and
   operational behavior.

Return code: 0
```

The exact model wording may vary. The important behavior is that the workflow
keeps repository context local until `--run` is explicitly supplied, then sends a
focused maintainer prompt to the selected provider command.
