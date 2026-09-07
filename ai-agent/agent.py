"""LangChain AI agent workflow: generate → lint → test → review."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from utils.lint import run_lint
from utils.review import ai_review
from utils.test import run_tests

REPO_ROOT = Path(__file__).resolve().parents[1]


async def run_agent(
    component_name: str,
    *,
    generate_component: bool = True,
    source_or_diff: str | None = None,
) -> dict[str, str]:
    results: dict[str, str] = {}

    if generate_component:
        results["generate"] = _generate_component(component_name)
    else:
        results["generate"] = "Skipped component generation (PR / review-only mode)."

    results["lint"] = run_lint()
    results["tests"] = run_tests()
    results["review"] = ai_review(component_name, source_or_diff)
    return results


def _generate_component(component_name: str) -> str:
    ng = shutil.which("ng")
    if ng is None:
        return "Generate skipped: Angular CLI (`ng`) is not installed."

    name = (component_name or "").strip()
    if not name:
        return "Generate skipped: component_name is empty."

    try:
        subprocess.run(
            [ng, "generate", "component", name, "--skip-tests=false"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return f"Generated Angular component `{name}`."
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or exc.stdout or str(exc)).strip()
        return f"Generate failed: {stderr}"
    except Exception as exc:  # noqa: BLE001
        return f"Generate failed: {exc}"
