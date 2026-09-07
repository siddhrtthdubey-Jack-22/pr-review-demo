"""Run project tests with coverage when a Node workspace is present."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def run_tests(cwd: Path | None = None) -> str:
    root = cwd or REPO_ROOT
    npm = shutil.which("npm")
    if npm is None:
        return "Tests skipped: npm is not installed."

    package_json = root / "package.json"
    if not package_json.exists():
        return "Tests skipped: no package.json in the repo root."

    try:
        subprocess.run(
            [npm, "run", "test", "--", "--coverage", "--watchAll=false"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        return "Tests passed with coverage enforced."
    except subprocess.CalledProcessError as extra:
        stderr = (extra.stderr or extra.stdout or str(extra)).strip()
        return f"Tests failed: {stderr}"
    except Exception as extra:  # noqa: BLE001
        return f"Tests failed: {extra}"
