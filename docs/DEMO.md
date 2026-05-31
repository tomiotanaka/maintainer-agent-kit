# Demo

This demo shows the intended maintainer loop: convert GitHub context into a
local Markdown task, preview prompts, then optionally run Codex in a constrained
mode.

## 1. Convert an issue to triage input

```bash
maintainer-agent import-github issue examples/github-issue.json \
  --output /tmp/imported-issue.md
```

Expected output:

```text
Wrote /tmp/imported-issue.md
```

## 2. Preview triage prompts

```bash
maintainer-agent triage /tmp/imported-issue.md --dry-run --no-prompts
```

Expected output:

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

## 3. Convert a pull request to review input

```bash
maintainer-agent import-github pr examples/github-pr.json \
  --files examples/github-pr-files.json \
  --output /tmp/imported-pr.md
```

## 4. Run Codex in read-only mode

```bash
maintainer-agent review /tmp/imported-pr.md \
  --run \
  --preset codex-read-only \
  --no-prompts
```

The dry-run preview is the default. The Codex command only runs when `--run` is
explicitly supplied by the maintainer.
