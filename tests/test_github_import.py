import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from maintainer_agent_kit.cli import main
from maintainer_agent_kit.github_import import (
  load_json,
  parse_github_url,
  render_issue_markdown,
  render_pull_request_markdown,
)


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

      output = StringIO()
      with redirect_stdout(output):
        exit_code = main(["import-github", "issue", str(input_path), "--output", str(output_path)])

      self.assertEqual(exit_code, 0)
      self.assertIn("GitHub Issue #42", output_path.read_text(encoding="utf-8"))
      self.assertIn(f"Next: maintainer-agent triage {output_path} --dry-run", output.getvalue())

  def test_cli_import_pr_writes_markdown_file_with_files(self):
    with tempfile.TemporaryDirectory() as temp_dir:
      temp_path = Path(temp_dir)
      pr_path = temp_path / "pr.json"
      files_path = temp_path / "files.json"
      output_path = temp_path / "nested" / "pr.md"
      pr_path.write_text(json.dumps(PR), encoding="utf-8")
      files_path.write_text(json.dumps(FILES), encoding="utf-8")

      output = StringIO()
      with redirect_stdout(output):
        exit_code = main(["import-github", "pr", str(pr_path), "--files", str(files_path), "-o", str(output_path)])

      self.assertEqual(exit_code, 0)
      self.assertIn("Changed files: 2", output_path.read_text(encoding="utf-8"))
      self.assertIn(f"Next: maintainer-agent review {output_path} --dry-run", output.getvalue())

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

  def test_parse_github_url_extracts_issue_context(self):
    parsed = parse_github_url("https://github.com/example/project/issues/42", expected_kind="issue")
    self.assertEqual(parsed.kind, "issue")
    self.assertEqual(parsed.repo, "example/project")
    self.assertEqual(parsed.number, 42)

  def test_parse_github_url_rejects_wrong_kind(self):
    with self.assertRaisesRegex(SystemExit, "Expected a GitHub issue URL"):
      parse_github_url("https://github.com/example/project/pull/17", expected_kind="issue")

  def test_parse_github_url_requires_https_github_url(self):
    with self.assertRaisesRegex(SystemExit, "https://github.com"):
      parse_github_url("http://github.com/example/project/issues/42", expected_kind="issue")

  @patch("maintainer_agent_kit.github_import.subprocess.run")
  def test_cli_issue_url_requires_gh_opt_in_without_shelling_out(self, run_mock):
    with tempfile.TemporaryDirectory() as temp_dir:
      with self.assertRaisesRegex(SystemExit, "Pass --use-gh"):
        main(
          [
            "import-github",
            "issue-url",
            "https://github.com/example/project/issues/42",
            "--output",
            str(Path(temp_dir) / "issue.md"),
          ]
        )
    run_mock.assert_not_called()

  @patch("maintainer_agent_kit.github_import.subprocess.run")
  def test_cli_pr_url_requires_gh_opt_in_without_shelling_out(self, run_mock):
    with tempfile.TemporaryDirectory() as temp_dir:
      with self.assertRaisesRegex(SystemExit, "Pass --use-gh"):
        main(
          [
            "import-github",
            "pr-url",
            "https://github.com/example/project/pull/17",
            "--output",
            str(Path(temp_dir) / "pr.md"),
          ]
        )
    run_mock.assert_not_called()

  def test_import_next_step_quotes_paths_with_spaces(self):
    with tempfile.TemporaryDirectory() as temp_dir:
      temp_path = Path(temp_dir)
      input_path = temp_path / "issue.json"
      output_path = temp_path / "path with spaces" / "issue.md"
      input_path.write_text(json.dumps(ISSUE), encoding="utf-8")

      output = StringIO()
      with redirect_stdout(output):
        exit_code = main(["import-github", "issue", str(input_path), "--output", str(output_path)])

      self.assertEqual(exit_code, 0)
      self.assertIn(f"Next: maintainer-agent triage '{output_path}' --dry-run", output.getvalue())

  @patch("maintainer_agent_kit.github_import.subprocess.run")
  def test_cli_issue_url_fetches_with_gh_and_prints_dry_run_next_step(self, run_mock):
    gh_issue = {
      "number": 42,
      "title": "Crash when importing large JSON",
      "url": "https://github.com/example/project/issues/42",
      "state": "open",
      "author": {"login": "reporter"},
      "labels": [{"name": "bug"}],
      "body": "Importing a 75 MB JSON file exits without an error message.",
    }
    run_mock.return_value = subprocess.CompletedProcess(["gh"], 0, stdout=json.dumps(gh_issue), stderr="")

    with tempfile.TemporaryDirectory() as temp_dir:
      output_path = Path(temp_dir) / "issue.md"
      output = StringIO()
      with redirect_stdout(output):
        exit_code = main(
          [
            "import-github",
            "issue-url",
            "https://github.com/example/project/issues/42",
            "--use-gh",
            "--output",
            str(output_path),
          ]
        )

      self.assertEqual(exit_code, 0)
      self.assertIn("GitHub Issue #42", output_path.read_text(encoding="utf-8"))
      self.assertIn(f"Next: maintainer-agent triage {output_path} --dry-run", output.getvalue())

    self.assertEqual(
      run_mock.call_args.args[0],
      [
        "gh",
        "issue",
        "view",
        "42",
        "--repo",
        "example/project",
        "--json",
        "number,title,url,state,author,labels,body",
      ],
    )

  @patch("maintainer_agent_kit.github_import.subprocess.run")
  def test_cli_pr_url_fetches_pr_and_files_with_gh(self, run_mock):
    gh_pr = {
      "number": 17,
      "title": "Retry authentication refresh",
      "url": "https://github.com/example/project/pull/17",
      "state": "open",
      "author": {"login": "contributor"},
      "baseRefName": "main",
      "headRefName": "auth-retry",
      "additions": 120,
      "deletions": 18,
      "body": "Adds retry handling around token refresh.",
    }
    run_mock.side_effect = [
      subprocess.CompletedProcess(["gh"], 0, stdout=json.dumps(gh_pr), stderr=""),
      subprocess.CompletedProcess(["gh"], 0, stdout=json.dumps(FILES), stderr=""),
    ]

    with tempfile.TemporaryDirectory() as temp_dir:
      output_path = Path(temp_dir) / "pr.md"
      output = StringIO()
      with redirect_stdout(output):
        exit_code = main(
          [
            "import-github",
            "pr-url",
            "https://github.com/example/project/pull/17",
            "--use-gh",
            "--output",
            str(output_path),
          ]
        )

      markdown = output_path.read_text(encoding="utf-8")
      self.assertEqual(exit_code, 0)
      self.assertIn("GitHub Pull Request #17", markdown)
      self.assertIn("Changed files: 2", markdown)
      self.assertIn(f"Next: maintainer-agent review {output_path} --dry-run", output.getvalue())

    self.assertEqual(len(run_mock.call_args_list), 2)
    self.assertEqual(run_mock.call_args_list[0].args[0][:6], ["gh", "pr", "view", "17", "--repo", "example/project"])
    self.assertIn("--jq", run_mock.call_args_list[1].args[0])

  @patch("maintainer_agent_kit.github_import.subprocess.run")
  def test_cli_pr_url_no_files_skips_file_fetch(self, run_mock):
    gh_pr = {
      "number": 17,
      "title": "Retry authentication refresh",
      "url": "https://github.com/example/project/pull/17",
      "state": "open",
      "author": {"login": "contributor"},
    }
    run_mock.return_value = subprocess.CompletedProcess(["gh"], 0, stdout=json.dumps(gh_pr), stderr="")

    with tempfile.TemporaryDirectory() as temp_dir:
      with redirect_stdout(StringIO()):
        exit_code = main(
          [
            "import-github",
            "pr-url",
            "https://github.com/example/project/pull/17",
            "--use-gh",
            "--no-files",
            "--output",
            str(Path(temp_dir) / "pr.md"),
          ]
        )

    self.assertEqual(exit_code, 0)
    self.assertEqual(len(run_mock.call_args_list), 1)


if __name__ == "__main__":
  unittest.main()
