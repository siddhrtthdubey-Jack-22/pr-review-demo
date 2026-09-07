"""Run project lint (npm run lint:fix) when a Node workspace is present."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def run_lint(cwd: Path | None = None) -> str:
    root = cwd or REPO_ROOT
    npm = shutil.which("npm")
    if npm is None:
        return "Lint skipped: npm is not installed."

    package_json = root / "package.json"
    if not package_json.exists():
        return "Lint skipped: no package.json in the repo root."

    try:
        subprocess.run(
            [npm, "run", "lint:fix"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        return "Linting complete. Commented/unwanted code removed where auto-fixable."
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or exc.stdout or str(exc)).strip()
        return f"Lint failed: {stderr}"
    except Exception as exc:  # noqa: BLE001 — surface unexpected runner errors
        return f"Lint failed: {exc}"
