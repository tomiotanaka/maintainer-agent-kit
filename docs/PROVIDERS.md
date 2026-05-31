# Provider Presets

Maintainer Agent Kit stays provider-neutral. By default, workflows run in
`--dry-run` mode and print the prompts that would be sent to each role.

When you are ready to run an agent, use either a raw command:

```bash
maintainer-agent review examples/pr-review.md \
  --run \
  --agent-command "codex exec -"
```

or a built-in preset:

```bash
maintainer-agent review examples/pr-review.md \
  --run \
  --preset codex-read-only
```

## Built-in presets

| Preset | Command | Use case |
| --- | --- | --- |
| `codex` | `codex exec -` | General Codex CLI workflow execution. |
| `codex-read-only` | `codex exec --sandbox read-only -` | Review, audit, and triage where the agent should not modify files. |
| `codex-json` | `codex exec --json -` | Automation pipelines that consume Codex JSONL events. |

All built-in presets pass prompts through stdin. They do not use shell execution,
do not include sandbox bypass flags, and do not require secrets for dry-run mode.

## Listing presets

```bash
maintainer-agent presets
```

## Custom OpenAI-compatible runners

If your team wraps the OpenAI API or another OpenAI-compatible provider in a
local command, keep that wrapper outside this repository and pass it explicitly:

```bash
maintainer-agent triage issue.md \
  --run \
  --agent-command "python scripts/run_openai_agent.py"
```

The command should read the workflow prompt from stdin. This keeps credentials
and provider-specific configuration in your own environment, not in this public
repository.
