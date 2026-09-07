"""LangChain-powered AI code review."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[2]

SYSTEM_PROMPT = """You are a senior Angular/TypeScript reviewer.
Review the provided change for:
- Angular best practices and component design
- Unused, commented, or dead code
- Test coverage gaps
- Accessibility, typing, and maintainability issues

Be concise. Use markdown with clear findings and suggested fixes.
If no source/diff is provided, say what is missing."""


def ai_review(component_name: str, source_or_diff: str | None = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Review skipped: OPENAI_API_KEY is not set."

    model = os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
    llm = ChatOpenAI(model=model, temperature=0, api_key=api_key)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "Review target: {component_name}\n\n"
                "Code or diff:\n```\n{source}\n```",
            ),
        ]
    )
    chain = prompt | llm
    result = chain.invoke(
        {
            "component_name": component_name or "(unspecified)",
            "source": source_or_diff or _fallback_source(component_name),
        }
    )
    content = getattr(result, "content", None)
    return content if isinstance(content, str) else str(result)


def _fallback_source(component_name: str) -> str:
    if not component_name:
        return "(no file contents available)"

    matches = list(REPO_ROOT.rglob(f"*{component_name}*"))
    snippets: list[str] = []
    for path in matches[:8]:
        if path.is_file() and path.suffix in {".ts", ".html", ".scss", ".css", ".js"}:
            try:
                snippets.append(f"// {path.relative_to(REPO_ROOT)}\n{path.read_text(encoding='utf-8')[:4000]}")
            except OSError:
                continue
    return "\n\n".join(snippets) if snippets else "(no matching source files found)"
