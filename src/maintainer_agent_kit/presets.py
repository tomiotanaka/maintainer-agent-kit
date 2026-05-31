from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderPreset:
  name: str
  command: str
  description: str


PRESETS: dict[str, ProviderPreset] = {
  "codex": ProviderPreset(
    name="codex",
    command="codex exec -",
    description="Run Codex CLI non-interactively with the workflow prompt on stdin.",
  ),
  "codex-read-only": ProviderPreset(
    name="codex-read-only",
    command="codex exec --sandbox read-only -",
    description="Run Codex CLI with a read-only sandbox for review and audit workflows.",
  ),
  "codex-json": ProviderPreset(
    name="codex-json",
    command="codex exec --json -",
    description="Run Codex CLI with JSONL event output for automation pipelines.",
  ),
}


def list_presets() -> tuple[ProviderPreset, ...]:
  return tuple(PRESETS.values())


def get_preset(name: str) -> ProviderPreset:
  try:
    return PRESETS[name]
  except KeyError as exc:
    names = ", ".join(sorted(PRESETS))
    raise ValueError(f"Unknown preset '{name}'. Available: {names}") from exc

