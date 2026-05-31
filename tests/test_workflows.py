import unittest

from maintainer_agent_kit.workflows import build_prompt, get_workflow, list_workflows, load_role_prompt


class WorkflowTests(unittest.TestCase):
  def test_expected_workflows_exist(self):
    names = {workflow.name for workflow in list_workflows()}
    self.assertEqual(names, {"triage", "review", "release", "audit"})

  def test_triage_has_audit_role(self):
    workflow = get_workflow("triage")
    role_names = [role.name for role in workflow.roles]
    self.assertIn("audit", role_names)

  def test_prompt_contains_context_and_role(self):
    workflow = get_workflow("review")
    role = workflow.roles[0]
    prompt = build_prompt(workflow, role, "PR changes auth timeout handling.")
    self.assertIn("PR changes auth timeout handling.", prompt)
    self.assertIn(role.name, prompt)
    self.assertIn("Shared Rules", prompt)

  def test_unknown_workflow_error_is_helpful(self):
    with self.assertRaisesRegex(ValueError, "Available"):
      get_workflow("unknown")

  def test_prompt_resource_loads(self):
    self.assertIn("audit pass", load_role_prompt("audit"))


if __name__ == "__main__":
  unittest.main()
