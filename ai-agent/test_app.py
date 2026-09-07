from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app import app
from utils.lint import run_lint
from utils.test import run_tests
from utils.review import ai_review


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_agent_skips_missing_tooling(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post(
        "/run-agent/",
        json={"component_name": "demo-widget", "generate_component": False},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    details = body["details"]
    assert "Skipped component generation" in details["generate"]
    assert "Review skipped" in details["review"]


def test_lint_and_tests_skip_without_package_json(tmp_path: Path) -> None:
    assert "no package.json" in run_lint(tmp_path)
    assert "no package.json" in run_tests(tmp_path)


def test_review_skips_without_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert "OPENAI_API_KEY" in ai_review("demo")
