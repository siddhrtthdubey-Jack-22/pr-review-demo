# pr-review-demo

FastAPI + LangChain AI agent that can generate an Angular component, lint, run tests, and produce an AI review. A GitHub Action runs the same agent on every pull request.

## Project structure

```
ai-agent/
 ├── app.py              # FastAPI entrypoint
 ├── agent.py            # LangChain AI Agent logic
 ├── cli.py              # GitHub Actions / local CLI
 ├── utils/
 │    ├── lint.py        # Run ESLint + clean code
 │    ├── test.py        # Run Jest + coverage check
 │    └── review.py      # AI code review
 └── requirements.txt
.eslintrc.json
.github/workflows/ai-agent.yml
```

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r ai-agent/requirements.txt
cp .env.example .env   # then set OPENAI_API_KEY
```

Start the API from `ai-agent/`:

```bash
cd ai-agent
uvicorn app:app --reload --port 8000
```

Trigger the workflow:

```bash
curl -X POST http://127.0.0.1:8000/run-agent/ \
  -H "Content-Type: application/json" \
  -d '{"component_name": "user-profile", "generate_component": false}'
```

`POST /run-agent/` will:

1. Optionally generate a component (`ng generate component …` when Angular CLI is installed)
2. Run `npm run lint:fix` when `package.json` exists
3. Run `npm run test -- --coverage --watchAll=false` when `package.json` exists
4. Ask LangChain/OpenAI to review the component or provided diff

Lint and test steps are skipped cleanly when this repo has no Node/Angular app yet. Point them at your app by adding `package.json` (and Angular CLI for generation).

## GitHub Action

`.github/workflows/ai-agent.yml` runs on `pull_request` (opened, synchronize, reopened).

It checks out the PR, installs the Python agent, reviews the git diff against the base branch, writes a job summary, and comments on the PR.

Add a repository secret:

- `OPENAI_API_KEY` — required for the AI review step
- optional repository variable `OPENAI_MODEL` (defaults to `gpt-4o-mini` in code)

Without the secret, lint/test still run (if present) and the review step reports that the key is missing.

## CLI

```bash
python ai-agent/cli.py --pr --component-name my-widget
```
