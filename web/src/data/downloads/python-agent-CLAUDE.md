# CLAUDE.md — Python AI Agent Project

## what this project is
[Your app description]

## tech stack
- Language: Python 3.11+
- Framework: FastAPI
- Database: PostgreSQL via SQLAlchemy
- AI: Anthropic Claude API via anthropic SDK
- Agent Framework: Claude Agent SDK / LangGraph / custom
- Testing: pytest + httpx
- Package manager: uv (or pip + venv)

## essential commands
```bash
source .venv/bin/activate   # activate venv (or use `uv run` prefix)
uv sync                     # install deps (or pip install -r requirements.txt)
uvicorn main:app --reload   # dev server on :8000
pytest                      # run tests
pytest --cov                # with coverage
ruff check .                # lint
ruff format .               # format
mypy .                      # type check
```

## architecture
```
src/
├── api/              # FastAPI route handlers
├── agents/           # Agent definitions, tools, prompts
├── db/               # SQLAlchemy models and repositories
├── services/         # Business logic
├── schemas/          # Pydantic models for request/response
└── utils/            # Pure utility functions
tests/
├── unit/             # Unit tests
├── integration/      # Integration tests (real DB)
└── conftest.py       # Fixtures
```

## agent-specific rules
- Agent prompts in `agents/prompts/` as Python strings (no f-strings with user input)
- Tools in `agents/tools/` — one file per tool, each with docstring
- Model name from `ANTHROPIC_MODEL` env var, never hardcoded
- Always set `max_tokens` explicitly
- Validate Claude output with Pydantic before using it
- Never pass raw user input into agent prompts — sanitize first
- Log every agent call: model, tokens, latency, success/fail
- Use `asyncio.timeout()` on all agent calls — never let them hang

## structured output with Pydantic
Always validate Claude responses into typed models:
```python
from pydantic import BaseModel, Field
from anthropic import Anthropic

class AnalysisResult(BaseModel):
    summary: str = Field(description="One-paragraph summary")
    sentiment: float = Field(ge=-1.0, le=1.0, description="Sentiment score")
    topics: list[str] = Field(max_length=10, description="Key topics")
    confidence: float = Field(ge=0.0, le=1.0)

client = Anthropic()

def analyze_text(text: str) -> AnalysisResult:
    response = client.messages.create(
        model=os.environ["ANTHROPIC_MODEL"],
        max_tokens=1024,
        messages=[{"role": "user", "content": f"Analyze this text and respond in JSON:\n\n{text}"}],
        system="You are an analysis agent. Always respond with valid JSON matching the requested schema.",
    )
    raw = response.content[0].text
    return AnalysisResult.model_validate_json(raw)  # raises ValidationError if invalid
```

## async agent patterns
Use async for concurrent tool execution and non-blocking I/O:
```python
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

async def run_agent(query: str) -> str:
    response = await client.messages.create(
        model=os.environ["ANTHROPIC_MODEL"],
        max_tokens=4096,
        messages=[{"role": "user", "content": query}],
    )
    return response.content[0].text

# Streaming responses
async def stream_agent(query: str):
    async with client.messages.stream(
        model=os.environ["ANTHROPIC_MODEL"],
        max_tokens=4096,
        messages=[{"role": "user", "content": query}],
    ) as stream:
        async for text in stream.text_stream:
            yield text

# FastAPI streaming endpoint
from fastapi.responses import StreamingResponse

@app.post("/api/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        stream_agent(request.message),
        media_type="text/plain",
    )
```

## async tool execution
Run multiple tools concurrently when the agent requests them:
```python
async def execute_tools_concurrently(tool_calls: list[ToolCall]) -> list[ToolResult]:
    """Execute independent tool calls in parallel."""
    tasks = [execute_single_tool(tc) for tc in tool_calls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    tool_results = []
    for tc, result in zip(tool_calls, results):
        if isinstance(result, Exception):
            tool_results.append(ToolResult(
                tool_use_id=tc.id,
                content=f"Error: {type(result).__name__}: {result}",
                is_error=True,
            ))
        else:
            tool_results.append(ToolResult(
                tool_use_id=tc.id,
                content=result,
            ))
    return tool_results
```

## Claude Agent SDK patterns
If using the Claude Agent SDK (`claude-agent`):
```python
from claude_agent import Agent, Tool

# Define tools as typed functions
@Tool
async def search_database(query: str, limit: int = 10) -> list[dict]:
    """Search the database for records matching the query."""
    return await db.search(query, limit=limit)

@Tool
async def send_email(to: str, subject: str, body: str) -> bool:
    """Send an email to the specified address."""
    return await email_service.send(to=to, subject=subject, body=body)

# Create agent with tools
agent = Agent(
    model=os.environ["ANTHROPIC_MODEL"],
    tools=[search_database, send_email],
    system="You are a helpful assistant with access to the database and email.",
    max_turns=10,  # prevent infinite loops
)

# Run the agent
result = await agent.run("Find all overdue invoices and email reminders")
```

## what NOT to do
- Do not use `eval()` or `exec()` with any external input
- Do not construct SQL strings — use SQLAlchemy ORM or parameterized queries
- Do not catch broad `Exception` without logging
- Do not store secrets in code — use .env + python-dotenv (or pydantic-settings)
- Do not assume Claude returns valid JSON — always try/except json.loads or use Pydantic
- Do not use `requests` — use `httpx` (async support)
- Do not use `time.sleep()` in async code — use `await asyncio.sleep()`
- Do not create sync wrappers around async code — keep the async chain intact
- Do not use mutable default arguments in function signatures

## before finishing a task
1. `pytest` — all pass
2. `ruff check .` — zero errors
3. `mypy .` — zero errors
4. If you touched agents: test with real API call
5. If you touched DB: verify migration runs on empty database
6. Check git diff

## lessons learned
<!-- append here when mistakes are corrected -->
