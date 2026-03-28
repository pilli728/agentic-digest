---
title: "Agentic Design Patterns — The 424-Page Google Engineer Doc, Broken Down"
description: "A senior Google engineer dropped a 424-page doc covering every agentic design pattern at the frontier. Every chapter is code-backed. Here's what matters and what you can use today."
date: "2026-03-26"
tier: "pro"
category: "playbook"
---

# Agentic Design Patterns: The Breakdown

Antonio Gulli, Senior Director and Distinguished Engineer in Google's CTO Office, published a 424-page book called *Agentic Design Patterns: A Hands-On Guide to Building Intelligent Systems*. It covers 21 distinct patterns for building AI agents, with code examples using LangChain/LangGraph, CrewAI, and Google's Agent Developer Kit (ADK). Springer published it in December 2025. Royalties go to Save the Children.

Most people won't read 424 pages. Here's what you need to know, updated with what's actually working in production as of March 2026.

[Full PDF (free Google Docs version)](https://irp.cdn-website.com/ca79032a/files/uploaded/Agentic-Design-Patterns.pdf)

---

## The Core Patterns That Matter

The book covers 21 patterns. Six of them account for 90% of what production agents actually use. Here they are, ranked by how often I see them in real codebases.

### 1. Tool Use + MCP

This is the foundation now. An agent that can't use tools is just a chatbot.

The Model Context Protocol (MCP), introduced by Anthropic in November 2024 and donated to the Linux Foundation's Agentic AI Foundation in December 2025, is the standard. Over 10,000 MCP servers in production as of early 2026. 500+ clients across major platforms. OpenAI, Google, and Anthropic all support it.

MCP uses a JSON-RPC 2.0 client-host-server architecture. Three levels of tool use:

- **Simple tool calling.** Agent picks a tool, calls it, gets a result.
- **Tool chains.** Agent sequences multiple tools. Search, then read, then write.
- **Dynamic tool discovery.** Agent finds tools it needs at runtime through MCP server negotiation. This is the pattern that scales.

Three things MCP still lacks for production (flagged in a recent arXiv paper): identity propagation between servers, adaptive tool budgeting (how many tool calls should this task get?), and structured error semantics. Workarounds exist for all three, but expect protocol-level fixes in 2026.

### 2. ReAct (Reasoning + Acting)

The agent thinks, acts, observes the result, then thinks again. This is the loop at the heart of every serious agent. Claude Code uses it. ChatGPT's code interpreter uses it. Every agent framework implements it.

**When to use it:** Any task where the agent needs to make decisions based on intermediate results.

### 3. Reflection and Self-Correction

The agent reviews its own output before returning it. Two patterns:

- **Inner monologue.** Agent critiques its work silently (extended thinking in Claude).
- **Explicit reflection.** Agent writes a review, then revises based on it.

This is the difference between "agent that sometimes works" and "agent that reliably works." The book has a solid section on building reflection into CI/CD pipelines.

### 4. Plan-and-Execute

The agent creates an explicit plan, then executes each step. Different from ReAct because the plan is visible and revisable. Better for complex, multi-step tasks where you want to see what the agent intends before it starts.

**When to use it:** Research tasks, multi-file code changes, anything with 5+ steps.

### 5. Multi-Agent Orchestration

Multiple specialized agents working together. Three patterns:

- **Supervisor.** One agent coordinates others (most common in production).
- **Peer-to-peer.** Agents negotiate directly (rare in practice, complex to debug).
- **Hierarchical.** Tree structure of agents (useful at scale).

**Key insight from the book:** Most teams over-architect multi-agent systems. Start with one agent and a good tool set. Only split into multiple agents when a single agent's context gets too cluttered. The book backs this up with cost data showing single-agent-with-tools outperforms multi-agent on tasks under moderate complexity.

### 6. Memory and State Management

Three types:

- **Working memory.** Current conversation context.
- **Episodic memory.** Past interactions (what happened last session).
- **Semantic memory.** Learned facts and preferences.

The practical takeaway: episodic memory is the most underused and highest-ROI pattern. Most developers implement working memory (it's automatic) and skip the other two.

---

## Code Examples: Top 3 Patterns with the Claude Agent SDK

The book uses LangChain/CrewAI/Google ADK. Here's how the top patterns look with Anthropic's Claude Agent SDK, which shipped in early 2026 and gives you the same agentic loop that powers Claude Code.

### Pattern 1: ReAct with Tool Use

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def react_agent():
    """Simple ReAct agent: thinks, uses tools, observes, repeats."""
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-20250514",
        allowed_tools=["Bash", "Read", "Write", "Glob", "Grep"],
        max_turns=20,
        system_prompt="You are a code reviewer. Find bugs, explain them, suggest fixes."
    )

    async for message in query(
        prompt="Review the auth module in src/auth/ for security issues.",
        options=options
    ):
        print(message)

asyncio.run(react_agent())
```

The `query` function creates the agentic loop. Claude thinks, picks a tool, calls it, observes the result, thinks again. The `async for` loop yields each step: reasoning, tool calls, tool results, and the final answer. You just consume the stream.

### Pattern 2: Reflection (Evaluate and Revise)

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def reflect_and_revise():
    """Two-pass pattern: generate, then critique and revise."""

    # Pass 1: Generate
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-20250514",
        allowed_tools=["Bash", "Read", "Write"],
        max_turns=15,
    )

    result = None
    async for message in query(
        prompt="Write a rate limiter middleware for Express in src/middleware/rate-limit.ts",
        options=options
    ):
        result = message

    # Pass 2: Reflect and fix
    async for message in query(
        prompt=(
            "Review the rate limiter you just wrote. Check for: "
            "1) Race conditions under concurrent requests. "
            "2) Memory leaks from unbounded Maps. "
            "3) Missing edge cases. "
            "Fix any issues you find."
        ),
        options=options
    ):
        print(message)

asyncio.run(reflect_and_revise())
```

The two-pass approach costs roughly 2x in tokens but catches 60-80% of bugs that a single pass misses. Worth it for any code that touches security, payments, or data integrity.

### Pattern 3: Plan-and-Execute with Custom Tools

```python
import asyncio
from typing import Any
from claude_agent_sdk import query, ClaudeAgentOptions, tool

@tool("check_test_coverage", "Run tests and return coverage percentage", {
    "directory": str
})
async def check_coverage(args: dict[str, Any]) -> dict[str, Any]:
    """Custom tool: runs pytest with coverage and returns the result."""
    import subprocess
    result = subprocess.run(
        ["pytest", "--cov", args["directory"], "--cov-report=json", "-q"],
        capture_output=True, text=True
    )
    return {"stdout": result.stdout, "stderr": result.stderr, "code": result.returncode}

async def plan_and_execute():
    """Plan first, then execute with progress tracking."""
    options = ClaudeAgentOptions(
        model="claude-sonnet-4-20250514",
        allowed_tools=["Bash", "Read", "Write", "Glob", "Grep", "check_test_coverage"],
        max_turns=30,
    )

    async for message in query(
        prompt=(
            "I need to improve test coverage in src/api/ from 45% to 80%. "
            "First, write a plan to PLAN.md listing which files need tests and "
            "what cases to cover. Then execute the plan one file at a time, "
            "running coverage after each file to track progress."
        ),
        options=options
    ):
        print(message)

asyncio.run(plan_and_execute())
```

Custom tools are implemented as in-process MCP servers. The `@tool` decorator registers them with the agent loop. Claude sees them alongside the built-in tools and calls them when needed.

---

## Evaluation Frameworks: How to Measure Agent Quality

The book covers evaluation, but the ecosystem has moved fast since December 2025. Here's the current state.

### The Problem

Traditional software testing (unit tests, integration tests) doesn't work for agents. An agent can solve the same problem ten different ways. "Did it produce the right output?" is necessary but not sufficient. You also need: Did it use a reasonable number of steps? Did it call the right tools? Did it stay within scope?

### Tools That Work

**Braintrust.** Best for CI/CD integration. Runs evaluation scorers automatically, analyzes statistical significance, blocks merges when quality degrades. If you want "tests that fail when the agent gets worse," this is the tool.

**Langfuse.** Open source (MIT license), 19k+ GitHub stars. Self-hostable. Best for teams that want full control over their data. Good tracing, prompt management, and evaluation in one platform.

**Promptfoo.** Specifically built for prompt/agent testing. Define test cases in YAML, run them against your agent, get pass/fail results. Closest to traditional unit testing.

**DeepEval.** Python-native evaluation framework. Good for "LLM-as-a-judge" scoring, where you use one model to evaluate another model's output.

### What to Measure

1. **Task completion rate.** Did the agent finish the job? Binary metric.
2. **Step efficiency.** How many tool calls did it take? Fewer is better (and cheaper).
3. **Scope adherence.** Did the agent stay within what you asked for, or did it wander?
4. **Cost per task.** Total tokens consumed. Track this over time.
5. **Regression rate.** After changes, does the agent get worse on previous tasks?

The highest-leverage move: build an eval suite of 20-30 representative tasks for your agent and run it on every change. Takes a day to set up. Pays off forever.

---

## Agent Observability: Seeing What Your Agent Actually Does

In 2026, agent observability moved from "nice to have" to "non-negotiable." Every production agent failure I've seen traces back to the same root cause: the team couldn't see what the agent was doing.

### What You Need to See

- **Reasoning chains.** What did the agent think at each step? Why did it pick that tool?
- **Tool call flows.** Which tools were called, in what order, with what inputs/outputs?
- **Cost attribution.** Which step cost the most tokens? Where are the waste loops?
- **Latency breakdown.** Is the bottleneck the model, the tool call, or the network?
- **Quality degradation.** Is the agent getting worse over time? On which task types?

### The Platforms

**LangSmith** (from LangChain). Zero-config tracing for LangChain apps. Virtually no performance overhead. Best if you're already in the LangChain ecosystem.

**Langfuse** (open source). Self-hostable. Best for teams with compliance requirements who can't send traces to a third party. Supports nested spans for multi-step agent workflows.

**Braintrust.** Optimized for trace search across large datasets. Good if you're running thousands of agent invocations per day and need to find specific patterns.

**OpenTelemetry + custom dashboards.** The DIY option. More work to set up, but zero vendor lock-in. Several agent frameworks now export OTEL-compatible traces natively.

### The Minimum Viable Setup

At bare minimum, log every tool call with its input, output, latency, and token count. Store these as structured JSON. Even without a fancy platform, you can grep through these logs when something goes wrong.

```python
import json, time, logging

logger = logging.getLogger("agent_trace")

def trace_tool_call(tool_name: str, inputs: dict, func):
    """Minimal tracing wrapper for any tool call."""
    start = time.time()
    result = func(inputs)
    elapsed = time.time() - start

    logger.info(json.dumps({
        "tool": tool_name,
        "inputs": inputs,
        "output_preview": str(result)[:200],
        "latency_ms": round(elapsed * 1000),
        "timestamp": time.time()
    }))
    return result
```

---

## What's Actually New Since the Book

The book was written in late 2025. Here's what changed:

1. **MCP is the standard.** The book covers it as emerging. It's now dominant. If you're building tool use without MCP, you're building something you'll have to rewrite.

2. **The Claude Agent SDK exists.** Anthropic released a Python and TypeScript SDK that gives you the same agent loop Claude Code uses. This didn't exist when the book was written. It's the easiest way to build production agents with Claude.

3. **Flow design beats prompt tricks.** The biggest shift in early 2026: people stopped obsessing over prompt engineering and started designing better agent workflows. How you structure the loop matters more than how you phrase the prompt.

4. **Deterministic where possible, LLM where necessary.** The agents that reach production fastest use LLM reasoning only for genuinely ambiguous decisions. Input validation, output formatting, API call construction, error handling? All deterministic code. Don't burn tokens on things with known correct answers.

5. **Observability is table stakes.** No serious team ships an agent without tracing now. This was optional in 2025. It's mandatory in 2026.

## The One Thing to Do Today

Read Chapters 4 (Multi-Agent Orchestration) and 6 (Reflection) from the book. Then build one agent using the Claude Agent SDK with the ReAct + Reflection combo shown above. That combination, with proper tool use via MCP, will handle 80% of real-world agent tasks.

[Download the full 424-page PDF](https://irp.cdn-website.com/ca79032a/files/uploaded/Agentic-Design-Patterns.pdf)
