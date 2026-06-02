# Small Library Issue Triage Context

## Project profile

- Project: `datetime-range-utils`
- Type: small Python utility library
- Maintainer risk: compatibility with existing range-boundary behavior
- Release channel: patch releases from `main`

## Incoming issue

Title: `expand_range` returns a duplicate boundary value when the interval is
exactly divisible by the step.

Reporter context:

- Version: 1.4.2
- Python: 3.12
- Reproduction:

```python
from datetime import date
from datetime_range_utils import expand_range

list(expand_range(date(2026, 1, 1), date(2026, 1, 3), step_days=1))
```

Expected:

```text
2026-01-01, 2026-01-02, 2026-01-03
```

Actual:

```text
2026-01-01, 2026-01-02, 2026-01-03, 2026-01-03
```

## Maintainer notes

- There is an old issue about inclusive end dates, but it does not mention
  duplicate boundaries.
- The bug may affect downstream billing code that expands date buckets.
- The report includes a reproduction, but no failing test or patch.

## Checklist focus

- Confirm whether this is a bug or expected inclusive-boundary behavior.
- Ask for any timezone-aware datetime reproduction if relevant.
- Label severity and release impact.
- Identify the minimum regression test needed before accepting a fix.
