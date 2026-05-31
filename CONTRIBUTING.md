# Contributing

Thanks for helping improve maintainer workflows.

## Local setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests
```

## Pull request checklist

- Keep prompts concrete and auditable.
- Add or update tests for behavior changes.
- Do not add secrets, private repository data, browser histories, or API keys.
- Prefer dry-run examples over provider-specific behavior.
- Document any new workflow in `README.md`.

## Prompt changes

Prompt updates should explain the maintainer behavior they improve. Avoid vague
instructions such as "be careful" unless they are paired with a concrete check.
