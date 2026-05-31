import unittest

from maintainer_agent_kit.presets import get_preset, list_presets


class PresetTests(unittest.TestCase):
  def test_expected_codex_presets_exist(self):
    names = {preset.name for preset in list_presets()}
    self.assertEqual(names, {"codex", "codex-read-only", "codex-json"})

  def test_read_only_preset_uses_read_only_sandbox(self):
    preset = get_preset("codex-read-only")
    self.assertIn("--sandbox read-only", preset.command)
    self.assertTrue(preset.command.endswith(" -"))

  def test_unknown_preset_error_is_helpful(self):
    with self.assertRaisesRegex(ValueError, "Available"):
      get_preset("missing")


if __name__ == "__main__":
  unittest.main()
