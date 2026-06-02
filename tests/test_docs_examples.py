import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from maintainer_agent_kit.cli import main


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_ROOT = REPO_ROOT / "examples" / "maintainer-checklists"
DOC_PATH = REPO_ROOT / "docs" / "MAINTAINER_CHECKLIST_EXAMPLES.md"

EXAMPLE_CASES = (
  ("triage", "small-library-issue.md", ("research", "executor", "memory", "audit")),
  ("review", "cli-tool-pr.md", ("research", "executor", "audit")),
  ("release", "web-app-release.md", ("research", "executor", "audit")),
  ("audit", "web-app-final-audit.md", ("audit",)),
)


class DocsExampleTests(unittest.TestCase):
  def test_maintainer_checklist_examples_are_linked(self):
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    demo = (REPO_ROOT / "docs" / "DEMO.md").read_text(encoding="utf-8")
    self.assertIn("docs/MAINTAINER_CHECKLIST_EXAMPLES.md", readme)
    self.assertIn("MAINTAINER_CHECKLIST_EXAMPLES.md", demo)

  def test_example_context_files_are_documented(self):
    doc = DOC_PATH.read_text(encoding="utf-8")
    for _, filename, _ in EXAMPLE_CASES:
      path = f"examples/maintainer-checklists/{filename}"
      with self.subTest(path=path):
        self.assertTrue((EXAMPLE_ROOT / filename).exists())
        self.assertIn(path, doc)

  def test_examples_run_in_dry_run_mode(self):
    for workflow, filename, roles in EXAMPLE_CASES:
      with self.subTest(workflow=workflow, filename=filename):
        output = io.StringIO()
        with redirect_stdout(output):
          exit_code = main(
            [
              workflow,
              str(EXAMPLE_ROOT / filename),
              "--dry-run",
              "--no-prompts",
            ]
          )
        text = output.getvalue()
        self.assertEqual(exit_code, 0)
        for role in roles:
          self.assertIn(f"## {role}", text)
        self.assertIn("DRY RUN: prompt preview only", text)


if __name__ == "__main__":
  unittest.main()
