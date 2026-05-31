# Publishing

This repository is prepared for `tomiotanaka/maintainer-agent-kit`.

## Final local checks

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m maintainer_agent_kit.cli list
PYTHONPATH=src python3 -m maintainer_agent_kit.cli triage examples/issue.md --dry-run --no-prompts
```

## Create the GitHub repository

If GitHub CLI is authenticated:

```bash
git status --short --ignored
git add .
git commit -m "Initial public maintainer-agent-kit release"
gh repo create tomiotanaka/maintainer-agent-kit --public --source=. --remote=origin --push
git tag v0.1.0
git push origin v0.1.0
```

If using the GitHub web UI:

1. Create a new public repository named `maintainer-agent-kit`.
2. Do not initialize it with README, license, or gitignore.
3. Run:

```bash
git status --short --ignored
git add .
git commit -m "Initial public maintainer-agent-kit release"
git remote add origin https://github.com/tomiotanaka/maintainer-agent-kit.git
git push -u origin main
git tag v0.1.0
git push origin v0.1.0
```

## Suggested repository metadata

Description:

```text
Provider-neutral maintainer workflows for issue triage, PR review, release notes, and audit.
```

Topics:

```text
open-source, maintainers, agents, triage, pull-request-review, release-notes, audit, cli
```
