import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from maintainer_agent_kit.cli import main


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_ROOT = REPO_ROOT / "examples" / "maintainer-checklists"
DOC_PATH = REPO_ROOT / "docs" / "MAINTAINER_CHECKLIST_EXAMPLES.md"
PUBLIC_LOG_PATH = REPO_ROOT / "docs" / "PUBLIC_MAINTENANCE_LOG.md"

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

  def test_public_maintenance_log_is_linked(self):
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    demo = (REPO_ROOT / "docs" / "DEMO.md").read_text(encoding="utf-8")
    self.assertIn("docs/PUBLIC_MAINTENANCE_LOG.md", readme)
    self.assertIn("PUBLIC_MAINTENANCE_LOG.md", demo)

  def test_public_maintenance_log_keeps_public_evidence_links(self):
    public_log = PUBLIC_LOG_PATH.read_text(encoding="utf-8")
    self.assertIn("https://github.com/tomiotanaka/maintainer-agent-kit/issues/4", public_log)
    self.assertIn("https://github.com/tomiotanaka/maintainer-agent-kit/releases/tag/v0.2.3", public_log)
    self.assertIn("https://github.com/Eskasia/smart-contract-security-assistant/issues/21", public_log)
    self.assertIn("https://github.com/tomiotanaka/maintainer-agent-kit/actions/workflows/ci.yml", public_log)

  def test_ci_workflow_keeps_compile_and_cli_smoke_checks(self):
    ci = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    self.assertIn("workflow_dispatch", ci)
    self.assertIn("python -m compileall -q src", ci)
    self.assertIn("maintainer-agent list", ci)
    self.assertIn("maintainer-agent import-github issue examples/github-issue.json", ci)

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
