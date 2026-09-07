"""FastAPI entrypoint for the AI agent."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agent import run_agent

app = FastAPI(
    title="PR Review AI Agent",
    description="FastAPI + LangChain agent that can generate a component, lint, test, and review code.",
    version="0.1.0",
)


class AgentRequest(BaseModel):
    component_name: str = Field(..., min_length=1, examples=["user-profile"])
    generate_component: bool = Field(
        default=True,
        description="Set false to skip `ng generate` (useful from GitHub Actions).",
    )
    source_or_diff: str | None = Field(
        default=None,
        description="Optional source or git diff for the AI reviewer.",
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run-agent/")
async def run_ai_agent(payload: AgentRequest) -> dict:
    result = await run_agent(
        payload.component_name,
        generate_component=payload.generate_component,
        source_or_diff=payload.source_or_diff,
    )
    return {"status": "success", "details": result}
