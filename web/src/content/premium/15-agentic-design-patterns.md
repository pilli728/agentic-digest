---
title: "Agentic Design Patterns — The 424-Page Google Engineer Doc, Broken Down"
description: "A senior Google engineer dropped a 424-page doc covering every agentic design pattern at the frontier. Every chapter is code-backed. Here's what matters and what you can use today."
date: "2026-03-26"
tier: "pro"
category: "playbook"
---

# Agentic Design Patterns — The Breakdown

A Google engineer published a 424-page document called *Agentic Design Patterns*. It covers every major pattern for building AI agents, with code examples for each. Most people won't read 424 pages. Here's what you need to know.

[Full PDF](https://irp.cdn-website.com/ca79032a/files/uploaded/Agentic-Design-Patterns.pdf)

---

## The 8 Core Patterns

### 1. ReAct (Reasoning + Acting)
The agent thinks, then acts, then observes the result, then thinks again. This is the foundation of every serious agent. If you're not using ReAct, you're prompting, not building agents.

**When to use it:** Any task where the agent needs to make decisions based on intermediate results.

### 2. Plan-and-Execute
The agent creates a plan upfront, then executes each step. Different from ReAct because the plan is explicit and revisable. Better for complex, multi-step tasks where you want visibility into what the agent intends to do before it does it.

**When to use it:** Research tasks, multi-file code changes, anything with 5+ steps.

### 3. Tool Use Patterns
Three levels of tool use covered in the doc:
- **Simple tool calling** — agent picks a tool and calls it
- **Tool chains** — agent sequences multiple tools
- **Dynamic tool discovery** — agent finds tools it needs at runtime (MCP pattern)

The doc argues MCP will become the standard. Hard to disagree given OpenAI, Google, and Anthropic all support it now.

### 4. Multi-Agent Orchestration
Multiple specialized agents working together. The doc covers:
- **Supervisor pattern** — one agent coordinates others
- **Peer-to-peer** — agents negotiate directly
- **Hierarchical** — tree structure of agents

**Key insight from the doc:** Most teams over-architect multi-agent systems. Start with one agent and a good tool set. Only split into multiple agents when a single agent's context gets too cluttered.

### 5. Memory and State Management
Three types of memory covered:
- **Working memory** — current conversation context
- **Episodic memory** — past interactions (what happened last time)
- **Semantic memory** — learned facts and preferences

The doc shows how to implement each with vector stores, SQLite, and structured JSON. The practical takeaway: episodic memory is the most underused and highest-ROI pattern.

### 6. Reflection and Self-Correction
The agent reviews its own output before returning it. Two patterns:
- **Inner monologue** — agent critiques its work silently
- **Explicit reflection** — agent writes a review, then revises

This is how you go from "agent that sometimes works" to "agent that reliably works." The doc has a section on building reflection into CI/CD pipelines.

### 7. Retrieval-Augmented Generation (RAG)
Covered extensively but the interesting part is the section on **agentic RAG** — where the agent decides what to retrieve, evaluates if the retrieval was useful, and re-queries if not. Standard RAG is "search and dump." Agentic RAG is "search, evaluate, refine, search again."

### 8. Human-in-the-Loop Patterns
When to involve humans, how to structure approval workflows, and how to gradually remove human checkpoints as confidence increases. The doc's framework:
- **Level 0:** Human does everything, agent suggests
- **Level 1:** Agent does routine work, human approves
- **Level 2:** Agent does everything, human reviews exceptions
- **Level 3:** Fully autonomous with audit trail

---

## What's Actually New Here

Most of these patterns exist in LangChain/LlamaIndex docs. What the Google doc adds:

1. **Production failure modes** — each pattern includes "what goes wrong" sections with real examples
2. **Cost analysis** — token usage estimates per pattern, which matters when you're running agents at scale
3. **Evaluation frameworks** — how to measure if your agent is actually getting better
4. **Composition patterns** — how to combine patterns (ReAct + RAG + Reflection is the killer combo)

## The One Thing to Do Today

Read Chapter 4 (Multi-Agent Orchestration) and Chapter 6 (Reflection). Those two patterns, combined, will make any existing agent 3-5x more reliable. The rest is useful context but those chapters are immediately actionable.

[Download the full 424-page PDF](https://irp.cdn-website.com/ca79032a/files/uploaded/Agentic-Design-Patterns.pdf)
