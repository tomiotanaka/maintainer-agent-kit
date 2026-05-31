from __future__ import annotations

import json
from pathlib import Path
from typing import Any


JsonObject = dict[str, Any]


def load_json(path: str | Path) -> JsonObject | list[JsonObject]:
  input_path = Path(path)
  try:
    with input_path.open(encoding="utf-8") as input_file:
      return json.load(input_file)
  except json.JSONDecodeError as exc:
    raise SystemExit(f"Invalid JSON in {input_path}: {exc}") from exc
  except OSError as exc:
    raise SystemExit(f"Could not read {input_path}: {exc}") from exc


def write_markdown(path: str | Path, content: str) -> None:
  output_path = Path(path)
  output_path.parent.mkdir(parents=True, exist_ok=True)
  output_path.write_text(content.rstrip() + "\n", encoding="utf-8")


def render_issue_markdown(issue: JsonObject) -> str:
  number = _value(issue, "number", "unknown")
  title = _value(issue, "title", "Untitled issue")
  body = _markdown_text(issue.get("body"))
  labels = _labels(issue.get("labels"))

  lines = [
    f"# GitHub Issue #{number}: {title}",
    "",
    f"- Source: {_url(issue)}",
    f"- State: {_value(issue, 'state', 'unknown')}",
    f"- Author: {_login(issue.get('user') or issue.get('author'))}",
    f"- Labels: {labels or 'none'}",
    "",
    "## Body",
    "",
    body or "_No issue body provided._",
  ]
  return "\n".join(lines).rstrip()


def render_pull_request_markdown(pr: JsonObject, files: list[JsonObject] | None = None) -> str:
  number = _value(pr, "number", "unknown")
  title = _value(pr, "title", "Untitled pull request")
  body = _markdown_text(pr.get("body"))
  base_ref = _ref(pr.get("base"))
  head_ref = _ref(pr.get("head"))
  if base_ref == "unknown":
    base_ref = _value(pr, "baseRefName", "unknown")
  if head_ref == "unknown":
    head_ref = _value(pr, "headRefName", "unknown")
  changed_files = _file_objects(files) if files is not None else _inline_files(pr)

  lines = [
    f"# GitHub Pull Request #{number}: {title}",
    "",
    f"- Source: {_url(pr)}",
    f"- State: {_value(pr, 'state', 'unknown')}",
    f"- Author: {_login(pr.get('user') or pr.get('author'))}",
    f"- Base: {base_ref}",
    f"- Head: {head_ref}",
    f"- Changed files: {len(changed_files)}",
    f"- Additions: {_value(pr, 'additions', 'unknown')}",
    f"- Deletions: {_value(pr, 'deletions', 'unknown')}",
    "",
    "## Summary",
    "",
    body or "_No pull request body provided._",
    "",
    "## Changed Files",
    "",
  ]

  if not changed_files:
    lines.append("_No changed-file metadata provided._")
  else:
    for file_info in changed_files:
      lines.append(_file_line(file_info))

  return "\n".join(lines).rstrip()


def _inline_files(pr: JsonObject) -> list[JsonObject]:
  files = pr.get("files")
  if isinstance(files, list):
    return _file_objects(files)
  return []


def _file_objects(files: list[Any]) -> list[JsonObject]:
  return [file_info for file_info in files if isinstance(file_info, dict)]


def _file_line(file_info: JsonObject) -> str:
  filename = _value(file_info, "filename", "") or _value(file_info, "path", "unknown")
  status = _value(file_info, "status", "modified")
  additions_value = _number(file_info.get("additions"), 0)
  deletions_value = _number(file_info.get("deletions"), 0)
  additions = str(additions_value)
  deletions = str(deletions_value)
  changes_value = file_info.get("changes")
  changes = str(_number(changes_value, additions_value + deletions_value))
  return f"- `{filename}` ({status}, +{additions}/-{deletions}, {changes} changes)"


def _labels(labels: Any) -> str:
  if not isinstance(labels, list):
    return ""
  names: list[str] = []
  for label in labels:
    if isinstance(label, dict):
      name = label.get("name")
      if isinstance(name, str) and name:
        names.append(name)
    elif isinstance(label, str) and label:
      names.append(label)
  return ", ".join(names)


def _login(user: Any) -> str:
  if isinstance(user, dict):
    return _value(user, "login", "unknown")
  return "unknown"


def _url(data: JsonObject) -> str:
  if "html_url" in data:
    return _value(data, "html_url", "unknown")
  return _value(data, "url", "unknown")


def _ref(ref_data: Any) -> str:
  if not isinstance(ref_data, dict):
    return "unknown"
  repo = ref_data.get("repo")
  repo_name = "unknown"
  if isinstance(repo, dict):
    repo_name = _value(repo, "full_name", "unknown")
  return f"{repo_name}:{_value(ref_data, 'ref', 'unknown')}"


def _markdown_text(value: Any) -> str:
  if not isinstance(value, str):
    return ""
  return value.strip()


def _value(data: JsonObject, key: str, default: Any) -> str:
  value = data.get(key, default)
  if value is None or value == "":
    value = default
  return str(value)


def _number(value: Any, default: int) -> int:
  if isinstance(value, bool):
    return default
  if isinstance(value, int):
    return value
  return default
