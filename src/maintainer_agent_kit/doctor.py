from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass

from .presets import list_presets
from .workflows import list_workflows


@dataclass(frozen=True)
class DoctorCheck:
  name: str
  status: str
  detail: str


def run_doctor_checks() -> list[DoctorCheck]:
  checks = [
    check_python_version(),
    check_workflows(),
    check_presets(),
    check_github_cli(),
  ]
  return checks


def check_python_version() -> DoctorCheck:
  version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
  if sys.version_info >= (3, 11):
    return DoctorCheck("python", "ok", f"{version} satisfies >=3.11")
  return DoctorCheck("python", "error", f"{version} is below the required >=3.11")


def check_workflows() -> DoctorCheck:
  workflows = ", ".join(workflow.name for workflow in list_workflows())
  return DoctorCheck("workflows", "ok", workflows)


def check_presets() -> DoctorCheck:
  presets = ", ".join(preset.name for preset in list_presets())
  return DoctorCheck("presets", "ok", presets)


def check_github_cli() -> DoctorCheck:
  gh_path = shutil.which("gh")
  if not gh_path:
    return DoctorCheck(
      "github-cli",
      "warn",
      "gh not found; local JSON imports and dry-run workflows still work",
    )

  try:
    result = subprocess.run(
      [gh_path, "--version"],
      check=False,
      capture_output=True,
      text=True,
      timeout=5,
    )
  except (OSError, subprocess.TimeoutExpired) as error:
    return DoctorCheck("github-cli", "warn", f"gh found, but version check failed: {error}")

  first_line = (result.stdout or result.stderr).splitlines()[0] if (result.stdout or result.stderr) else "unknown version"
  if result.returncode == 0:
    return DoctorCheck("github-cli", "ok", f"gh found ({first_line}); auth/access not checked")
  return DoctorCheck("github-cli", "warn", f"gh returned {result.returncode}: {first_line}")


def format_doctor_checks(checks: list[DoctorCheck]) -> str:
  lines = ["Doctor checks:"]
  for check in checks:
    lines.append(f"[{check.status}] {check.name}: {check.detail}")
  lines.append("")
  lines.append("Next: maintainer-agent triage examples/issue.md --dry-run")
  return "\n".join(lines)


def doctor_exit_code(checks: list[DoctorCheck]) -> int:
  return 1 if any(check.status == "error" for check in checks) else 0
