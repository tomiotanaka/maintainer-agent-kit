import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from maintainer_agent_kit.cli import main
from maintainer_agent_kit.github_import import load_json, render_issue_markdown, render_pull_request_markdown


ISSUE = {
  "number": 42,
  "title": "Crash when importing large JSON",
  "html_url": "https://github.com/example/project/issues/42",
  "state": "open",
  "user": {"login": "reporter"},
  "labels": [{"name": "bug"}, {"name": "needs-repro"}],
  "body": "Importing a 75 MB JSON file exits without an error message.",
}

PR = {
  "number": 17,
  "title": "Retry authentication refresh",
  "html_url": "https://github.com/example/project/pull/17",
  "state": "open",
  "user": {"login": "contributor"},
  "base": {"ref": "main", "repo": {"full_name": "example/project"}},
  "head": {"ref": "auth-retry", "repo": {"full_name": "contributor/project"}},
  "additions": 120,
  "deletions": 18,
  "body": "Adds retry handling around token refresh.",
}

FILES = [
  {"filename": "src/auth.py", "status": "modified", "additions": 90, "deletions": 12, "changes": 102},
  {"filename": "tests/test_auth.py", "status": "modified", "additions": 30, "deletions": 6, "changes": 36},
]


class GithubImportTests(unittest.TestCase):
  def test_render_issue_markdown_keeps_triage_context(self):
    markdown = render_issue_markdown(ISSUE)
    self.assertIn("# GitHub Issue #42: Crash when importing large JSON", markdown)
    self.assertIn("Labels: bug, needs-repro", markdown)
    self.assertIn("Importing a 75 MB JSON file", markdown)

  def test_render_pr_markdown_uses_file_metadata_without_patch_body(self):
    markdown = render_pull_request_markdown(PR, FILES)
    self.assertIn("# GitHub Pull Request #17: Retry authentication refresh", markdown)
    self.assertIn("Base: example/project:main", markdown)
    self.assertIn("- `src/auth.py` (modified, +90/-12, 102 changes)", markdown)
    self.assertNotIn("diff --git", markdown)

  def test_render_pr_markdown_accepts_github_cli_style_fields(self):
    markdown = render_pull_request_markdown(
      {
        "number": 18,
        "title": "Document timeout behavior",
        "url": "https://github.com/example/project/pull/18",
        "author": {"login": "docs-maintainer"},
        "baseRefName": "main",
        "headRefName": "docs-timeout",
      }
    )
    self.assertIn("Source: https://github.com/example/project/pull/18", markdown)
    self.assertIn("Author: docs-maintainer", markdown)
    self.assertIn("Base: main", markdown)

  def test_render_pr_markdown_accepts_github_cli_file_paths(self):
    markdown = render_pull_request_markdown(PR, [{"path": "docs/auth.md", "additions": 5, "deletions": 2}])
    self.assertIn("- `docs/auth.md` (modified, +5/-2, 7 changes)", markdown)

  def test_cli_import_issue_writes_markdown_file(self):
    with tempfile.TemporaryDirectory() as temp_dir:
      temp_path = Path(temp_dir)
      input_path = temp_path / "issue.json"
      output_path = temp_path / "issue.md"
      input_path.write_text(json.dumps(ISSUE), encoding="utf-8")

      with redirect_stdout(StringIO()):
        exit_code = main(["import-github", "issue", str(input_path), "--output", str(output_path)])

      self.assertEqual(exit_code, 0)
      self.assertIn("GitHub Issue #42", output_path.read_text(encoding="utf-8"))

  def test_cli_import_pr_writes_markdown_file_with_files(self):
    with tempfile.TemporaryDirectory() as temp_dir:
      temp_path = Path(temp_dir)
      pr_path = temp_path / "pr.json"
      files_path = temp_path / "files.json"
      output_path = temp_path / "nested" / "pr.md"
      pr_path.write_text(json.dumps(PR), encoding="utf-8")
      files_path.write_text(json.dumps(FILES), encoding="utf-8")

      with redirect_stdout(StringIO()):
        exit_code = main(["import-github", "pr", str(pr_path), "--files", str(files_path), "-o", str(output_path)])

      self.assertEqual(exit_code, 0)
      self.assertIn("Changed files: 2", output_path.read_text(encoding="utf-8"))

  def test_cli_import_pr_rejects_non_object_file_entries(self):
    with tempfile.TemporaryDirectory() as temp_dir:
      temp_path = Path(temp_dir)
      pr_path = temp_path / "pr.json"
      files_path = temp_path / "files.json"
      pr_path.write_text(json.dumps(PR), encoding="utf-8")
      files_path.write_text(json.dumps(["not-a-file-object"]), encoding="utf-8")

      with self.assertRaisesRegex(SystemExit, "must contain JSON objects"):
        main(["import-github", "pr", str(pr_path), "--files", str(files_path), "-o", str(temp_path / "pr.md")])

  def test_load_json_reports_invalid_json_cleanly(self):
    with tempfile.TemporaryDirectory() as temp_dir:
      input_path = Path(temp_dir) / "broken.json"
      input_path.write_text("{not json", encoding="utf-8")

      with self.assertRaisesRegex(SystemExit, "Invalid JSON"):
        load_json(input_path)


if __name__ == "__main__":
  unittest.main()
