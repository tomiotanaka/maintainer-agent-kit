import io
import sys
import unittest
from contextlib import redirect_stdout

from maintainer_agent_kit.cli import main, run_workflow
from maintainer_agent_kit.runner import run_agent_command


class CliTests(unittest.TestCase):
  def test_list_command_prints_workflows(self):
    output = io.StringIO()
    with redirect_stdout(output):
      exit_code = main(["list"])
    self.assertEqual(exit_code, 0)
    self.assertIn("triage", output.getvalue())
    self.assertIn("review", output.getvalue())

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
