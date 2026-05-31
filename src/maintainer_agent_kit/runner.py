from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentResult:
  role: str
  prompt: str
  output: str
  returncode: int | None


def run_agent_command(command: str, prompt: str, timeout: int) -> tuple[str, int]:
  if not command.strip():
    raise ValueError("agent command cannot be empty")

  argv = shlex.split(command)
  if any("{prompt}" in arg and arg != "{prompt}" for arg in argv):
    raise ValueError("{prompt} must be its own command argument")
  if "{prompt}" in argv:
    argv = [prompt if arg == "{prompt}" else arg for arg in argv]
    stdin = None
  else:
    stdin = prompt

  completed = subprocess.run(
    argv,
    input=stdin,
    capture_output=True,
    text=True,
    timeout=timeout,
    check=False,
  )
  output = completed.stdout.strip()
  if not output:
    output = completed.stderr.strip()
  return output, completed.returncode
