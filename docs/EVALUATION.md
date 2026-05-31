# Evaluation

Maintainer Agent Kit uses deterministic golden prompt tests for workflow quality
review. These tests do not call an AI provider. They verify that generated
workflow prompts keep the expected role structure, task context, and shared
safety rules.

## Running evaluations

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Golden fixtures

The fixtures live in `tests/golden`:

- `contexts/`: synthetic maintainer tasks.
- `snapshots/`: expected generated prompts for each workflow role.

When changing prompts or workflow structure, update the snapshots in the same
pull request and review the diff as product behavior. A prompt change should be
intentional, small enough to inspect, and tied to a maintainer workflow goal.

## Current coverage

- Issue triage workflow: research, executor, memory, audit.
- Pull request review workflow: research, executor, audit.
- Shared safety rules: untrusted input, no invented facts, actionable checks,
  missing evidence, and verification gaps.

