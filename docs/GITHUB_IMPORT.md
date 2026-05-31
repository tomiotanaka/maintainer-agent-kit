# GitHub Import Helpers

The import helpers convert GitHub issue and pull request JSON into local
Markdown files for maintainer workflows. They do not call GitHub, store tokens,
or run an AI provider. Use GitHub CLI or the GitHub API to fetch JSON, then pass
the local files to this tool.

## Issue triage

```bash
maintainer-agent import-github issue examples/github-issue.json \
  --output /tmp/imported-issue.md

maintainer-agent triage /tmp/imported-issue.md --dry-run
```

The generated Markdown includes the issue title, URL, state, author, labels, and
body. It is intended for the `triage` workflow.

## Pull request review

```bash
maintainer-agent import-github pr examples/github-pr.json \
  --files examples/github-pr-files.json \
  --output /tmp/imported-pr.md

maintainer-agent review /tmp/imported-pr.md --dry-run
```

The generated Markdown includes pull request metadata and changed-file stats.
Patch bodies are not imported by default, which keeps review prompts focused and
avoids accidentally storing sensitive diff content in fixtures.

## Fetching JSON with GitHub CLI

```bash
gh issue view 42 --repo owner/project --json number,title,url,state,author,labels,body > issue.json
gh pr view 17 --repo owner/project --json number,title,url,state,author,baseRefName,headRefName,additions,deletions,body > pr.json
gh pr view 17 --repo owner/project --json files --jq '.files' > pr-files.json
```

GitHub CLI field names can differ from REST API field names. The importer
accepts common variants such as `url`, `author.login`, `baseRefName`,
`headRefName`, and file `path`. If your export uses a different shape, normalize
the JSON before importing. The examples in this repository use GitHub REST-style
fields because they are stable and easy to test offline.

## Safety notes

- Keep fetched JSON out of the repository unless it is synthetic.
- Review imported Markdown before passing it to an agent provider.
- Use `--dry-run` first so maintainers can inspect prompts locally.
- Do not import secrets, private customer data, or internal logs.
