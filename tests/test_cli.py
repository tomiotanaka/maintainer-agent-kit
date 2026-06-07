import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from maintainer_agent_kit.cli import main, run_workflow
from maintainer_agent_kit.doctor import (
  DoctorCheck,
  doctor_exit_code,
  format_doctor_checks,
  format_doctor_json,
)
from maintainer_agent_kit.presets import get_preset
from maintainer_agent_kit.runner import run_agent_command


class CliTests(unittest.TestCase):
  def test_list_command_prints_workflows(self):
    output = io.StringIO()
    with redirect_stdout(output):
      exit_code = main(["list"])
    self.assertEqual(exit_code, 0)
    self.assertIn("triage", output.getvalue())
    self.assertIn("review", output.getvalue())

  def test_presets_command_prints_codex_presets(self):
    output = io.StringIO()
    with redirect_stdout(output):
      exit_code = main(["presets"])
    self.assertEqual(exit_code, 0)
    self.assertIn("codex-read-only", output.getvalue())
    self.assertIn("codex exec", output.getvalue())

  @patch("maintainer_agent_kit.doctor.shutil.which", return_value=None)
  @patch("maintainer_agent_kit.doctor.subprocess.run")
  def test_doctor_warns_when_gh_is_missing_without_shelling_out(self, run_mock, _):
    output = io.StringIO()
    with redirect_stdout(output):
      exit_code = main(["doctor"])

    self.assertEqual(exit_code, 0)
    self.assertIn("[ok] python:", output.getvalue())
    self.assertIn("[ok] workflows: triage, review, release, audit", output.getvalue())
    self.assertIn("[warn] github-cli: gh not found", output.getvalue())
    run_mock.assert_not_called()

  @patch("maintainer_agent_kit.doctor.shutil.which", return_value="/usr/bin/gh")
  @patch("maintainer_agent_kit.doctor.subprocess.run")
  def test_doctor_reports_gh_version_when_available(self, run_mock, _):
    run_mock.return_value = subprocess.CompletedProcess(["gh"], 0, stdout="gh version 2.0.0\n", stderr="")

    output = io.StringIO()
    with redirect_stdout(output):
      exit_code = main(["doctor"])

    self.assertEqual(exit_code, 0)
    self.assertIn("[ok] github-cli: gh found (gh version 2.0.0); auth/access not checked", output.getvalue())
    self.assertEqual(run_mock.call_args.args[0], ["/usr/bin/gh", "--version"])

  @patch("maintainer_agent_kit.doctor.shutil.which", return_value="/usr/bin/gh")
  @patch("maintainer_agent_kit.doctor.subprocess.run")
  def test_doctor_json_reports_structured_status(self, run_mock, _):
    run_mock.return_value = subprocess.CompletedProcess(["gh"], 0, stdout="gh version 2.0.0\n", stderr="")

    output = io.StringIO()
    with redirect_stdout(output):
      exit_code = main(["doctor", "--json"])

    payload = json.loads(output.getvalue())
    self.assertEqual(exit_code, 0)
    self.assertEqual(payload["status"], "ok")
    self.assertEqual(payload["next_step"], "maintainer-agent triage examples/issue.md --dry-run")
    self.assertIn(
      {
        "name": "github-cli",
        "status": "ok",
        "detail": "gh found (gh version 2.0.0); auth/access not checked",
      },
      payload["checks"],
    )

  @patch("maintainer_agent_kit.doctor.shutil.which", return_value="/usr/bin/gh")
  @patch("maintainer_agent_kit.doctor.subprocess.run")
  def test_doctor_sanitizes_gh_version_exceptions(self, run_mock, _):
    run_mock.side_effect = OSError("raw local path /private/tmp/gh failed")

    output = io.StringIO()
    with redirect_stdout(output):
      exit_code = main(["doctor"])

    self.assertEqual(exit_code, 0)
    self.assertIn("[warn] github-cli: gh found, but version check failed", output.getvalue())
    self.assertNotIn("/private/tmp/gh", output.getvalue())

  @patch("maintainer_agent_kit.doctor.shutil.which", return_value="/usr/bin/gh")
  @patch("maintainer_agent_kit.doctor.subprocess.run")
  def test_doctor_json_sanitizes_gh_version_exceptions(self, run_mock, _):
    run_mock.side_effect = OSError("raw local path /private/tmp/gh failed")

    output = io.StringIO()
    with redirect_stdout(output):
      exit_code = main(["doctor", "--json"])

    payload = json.loads(output.getvalue())
    self.assertEqual(exit_code, 0)
    self.assertEqual(payload["status"], "warn")
    self.assertNotIn("/private/tmp/gh", output.getvalue())

  def test_doctor_exit_code_only_fails_on_errors(self):
    self.assertEqual(doctor_exit_code([DoctorCheck("github-cli", "warn", "missing")]), 0)
    self.assertEqual(doctor_exit_code([DoctorCheck("python", "error", "old")]), 1)

  def test_format_doctor_checks_includes_next_step(self):
    text = format_doctor_checks([DoctorCheck("python", "ok", "3.11")])
    self.assertIn("Doctor checks:", text)
    self.assertIn("[ok] python: 3.11", text)
    self.assertIn("Next: maintainer-agent triage examples/issue.md --dry-run", text)

  def test_format_doctor_json_summarizes_warnings(self):
    payload = json.loads(format_doctor_json([DoctorCheck("github-cli", "warn", "missing")]))
    self.assertEqual(payload["status"], "warn")
    self.assertEqual(payload["checks"][0]["name"], "github-cli")

  def test_dry_run_does_not_require_agent_command(self):
    results = run_workflow(
      "audit",
      "Check whether release notes mention breaking changes.",
      run=False,
      agent_command=None,
      timeout=1,
    )
    self.assertEqual(len(results), 1)
    self.assertEqual(results[0].output, "DRY RUN: prompt preview only")
    self.assertIsNone(results[0].returncode)

  def test_codex_preset_is_stdin_based(self):
    preset = get_preset("codex")
    self.assertEqual(preset.command, "codex exec -")

  def test_agent_command_and_preset_are_mutually_exclusive(self):
    with self.assertRaisesRegex(SystemExit, "either --agent-command or --preset"):
      run_workflow(
        "audit",
        "Check command selection.",
        run=True,
        agent_command="cat",
        preset="codex",
        timeout=1,
      )

  def test_run_uses_stdin_command(self):
    results = run_workflow(
      "audit",
      "Need final audit.",
      run=True,
      agent_command=f"{sys.executable} -c \"import sys; print(sys.stdin.read().splitlines()[0])\"",
      timeout=5,
    )
    self.assertEqual(results[0].returncode, 0)
    self.assertEqual(results[0].output, "# Workflow")

  def test_prompt_placeholder_keeps_prompt_as_one_argument(self):
    results = run_workflow(
      "audit",
      "alpha beta\n--extra-option value\n'unmatched quote",
      run=True,
      agent_command=(
        f"{sys.executable} -c "
        "\"import sys; p=sys.argv[1]; print(len(sys.argv)); "
        "print('alpha beta' in p); print('--extra-option value' in p); "
        "print('\\'unmatched quote' in p)\" "
        "{prompt}"
      ),
      timeout=5,
    )
    self.assertEqual(results[0].returncode, 0)
    self.assertEqual(results[0].output, "2\nTrue\nTrue\nTrue")

  def test_prompt_placeholder_must_be_standalone_argument(self):
    with self.assertRaisesRegex(ValueError, "own command argument"):
      run_agent_command(f"{sys.executable} -c pass --prompt={{prompt}}", "hello", 5)


if __name__ == "__main__":
  unittest.main()
