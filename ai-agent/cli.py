"""CLI used by GitHub Actions to run the agent against a pull request."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agent import run_agent  # noqa: E402


def git_diff() -> str:
    base = os.getenv("GITHUB_BASE_REF") or "origin/main"
    commands = [
        ["git", "diff", f"{base}...HEAD"],
        ["git", "diff", "HEAD~1...HEAD"],
        ["git", "diff"],
    ]
    for cmd in commands:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()[:20000]
    return ""


async def main() -> int:
    parser = argparse.ArgumentParser(description="Run the FastAPI AI agent workflow.")
    parser.add_argument("--component-name", default="pull-request")
    parser.add_argument("--pr", action="store_true", help="PR mode: skip ng generate, review the git diff.")
    parser.add_argument("--output", default="ai-agent-results.json")
    args = parser.parse_args()

    diff = git_diff() if args.pr else None
    results = await run_agent(
        args.component_name,
        generate_component=not args.pr,
        source_or_diff=diff,
    )

    payload = {"status": "success", "details": results}
    Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        lines = ["## AI Agent results", ""]
        for key, value in results.items():
            lines.append(f"### {key}")
            lines.append("")
            lines.append(str(value))
            lines.append("")
        Path(summary_path).write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
