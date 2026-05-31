from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .github_import import load_json, render_issue_markdown, render_pull_request_markdown, write_markdown
from .presets import get_preset, list_presets
from .runner import AgentResult, run_agent_command
from .workflows import build_prompt, get_workflow, list_workflows


def read_context(path: str | None) -> str:
  if path:
    return Path(path).read_text(encoding="utf-8")
  if not sys.stdin.isatty():
    return sys.stdin.read()
  raise SystemExit("Provide a context file or pipe task context on stdin.")


def run_workflow(
  workflow_name: str,
  context: str,
  *,
  run: bool,
  agent_command: str | None,
  preset: str | None = None,
  timeout: int,
) -> list[AgentResult]:
  workflow = get_workflow(workflow_name)
  results: list[AgentResult] = []

  if agent_command and preset:
    raise SystemExit("Use either --agent-command or --preset, not both.")
  if preset:
    agent_command = get_preset(preset).command
  if run and not agent_command:
    raise SystemExit("--agent-command or --preset is required when --run is used")

  for role in workflow.roles:
    prompt = build_prompt(workflow, role, context)
    if run:
      assert agent_command is not None
      output, returncode = run_agent_command(agent_command, prompt, timeout)
    else:
      output = "DRY RUN: prompt preview only"
      returncode = None
    results.append(AgentResult(role=role.name, prompt=prompt, output=output, returncode=returncode))
  return results


def print_results(results: list[AgentResult], *, show_prompts: bool) -> None:
  for result in results:
    print(f"## {result.role}")
    if show_prompts:
      print()
      print("### Prompt")
      print(result.prompt)
    print()
    print("### Output")
    print(result.output)
    if result.returncode is not None:
      print()
      print(f"Return code: {result.returncode}")
    print()


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    prog="maintainer-agent",
    description="Run dry-run or provider-backed maintainer agent workflows.",
  )
  subparsers = parser.add_subparsers(dest="command", required=True)

  list_parser = subparsers.add_parser("list", help="List available workflows.")
  list_parser.set_defaults(handler=handle_list)

  presets_parser = subparsers.add_parser("presets", help="List provider command presets.")
  presets_parser.set_defaults(handler=handle_presets)

  import_parser = subparsers.add_parser("import-github", help="Convert GitHub JSON into workflow input Markdown.")
  import_subparsers = import_parser.add_subparsers(dest="import_type", required=True)

  issue_parser = import_subparsers.add_parser("issue", help="Convert a GitHub issue JSON file for triage.")
  issue_parser.add_argument("input", help="GitHub issue JSON file.")
  issue_parser.add_argument("-o", "--output", required=True, help="Markdown file to write.")
  issue_parser.set_defaults(handler=handle_import_issue)

  pr_parser = import_subparsers.add_parser("pr", help="Convert a GitHub pull request JSON file for review.")
  pr_parser.add_argument("input", help="GitHub pull request JSON file.")
  pr_parser.add_argument("--files", help="Optional GitHub pull request files JSON file.")
  pr_parser.add_argument("-o", "--output", required=True, help="Markdown file to write.")
  pr_parser.set_defaults(handler=handle_import_pr)

  for workflow in list_workflows():
    workflow_parser = subparsers.add_parser(workflow.name, help=workflow.summary)
    workflow_parser.add_argument("context", nargs="?", help="Markdown/text context file.")
    workflow_parser.add_argument("--run", action="store_true", help="Execute the configured agent command.")
    workflow_parser.add_argument(
      "--dry-run",
      action="store_true",
      help="Preview prompts without executing an agent command. This is the default.",
    )
    workflow_parser.add_argument("--agent-command", help="Command to execute for each role.")
    workflow_parser.add_argument(
      "--preset",
      choices=sorted(preset.name for preset in list_presets()),
      help="Provider command preset to execute for each role.",
    )
    workflow_parser.add_argument("--timeout", type=int, default=900, help="Agent command timeout in seconds.")
    workflow_parser.add_argument(
      "--no-prompts",
      action="store_true",
      help="Hide prompts in output and show only agent results.",
    )
    workflow_parser.set_defaults(handler=handle_workflow)

  return parser


def handle_list(_: argparse.Namespace) -> int:
  for workflow in list_workflows():
    roles = ", ".join(role.name for role in workflow.roles)
    print(f"{workflow.name}: {workflow.summary} ({roles})")
  return 0


def handle_presets(_: argparse.Namespace) -> int:
  for preset in list_presets():
    print(f"{preset.name}: {preset.command}")
    print(f"  {preset.description}")
  return 0


def handle_import_issue(args: argparse.Namespace) -> int:
  issue = load_json(args.input)
  if not isinstance(issue, dict):
    raise SystemExit("GitHub issue input must be a JSON object.")
  write_markdown(args.output, render_issue_markdown(issue))
  print(f"Wrote {args.output}")
  return 0


def handle_import_pr(args: argparse.Namespace) -> int:
  pr = load_json(args.input)
  if not isinstance(pr, dict):
    raise SystemExit("GitHub pull request input must be a JSON object.")
  files = None
  if args.files:
    files_json = load_json(args.files)
    if not isinstance(files_json, list):
      raise SystemExit("GitHub pull request files input must be a JSON array.")
    if any(not isinstance(file_info, dict) for file_info in files_json):
      raise SystemExit("GitHub pull request files input must contain JSON objects.")
    files = files_json
  write_markdown(args.output, render_pull_request_markdown(pr, files))
  print(f"Wrote {args.output}")
  return 0


def handle_workflow(args: argparse.Namespace) -> int:
  if args.run and args.dry_run:
    raise SystemExit("Use either --run or --dry-run, not both.")
  context = read_context(args.context)
  results = run_workflow(
    args.command,
    context,
    run=args.run,
    agent_command=args.agent_command,
    preset=args.preset,
    timeout=args.timeout,
  )
  print_results(results, show_prompts=not args.no_prompts)
  return 0


def main(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)
  return args.handler(args)


if __name__ == "__main__":
  raise SystemExit(main())
