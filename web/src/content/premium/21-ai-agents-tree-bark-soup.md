---
title: "AI Agents Are Tree Bark Soup"
description: "We're duct-taping tool calls, memory systems, and retry loops onto language models and calling it agentic AI. It works. Kind of."
date: "2026-03-29"
tier: "pro"
category: "playbook"
---

# AI Agents Are Tree Bark Soup

Tree bark soup is what you make when you have nothing else. You boil bark because you're desperate and resourceful. You add whatever you can find. You drink it because it keeps you alive.

It's not cuisine. Nobody calls it fine dining. But it works, and sometimes working is enough.

AI agents right now are tree bark soup.

I've been building them for two years. I've used every major framework — LangGraph, CrewAI, the Claude Agent SDK, MCP everything. I have a comment in my production code that reads: "this shouldn't work but it does, don't touch it." That comment has survived four refactors. I don't touch it.

We are duct-taping tool calls, memory systems, and retry loops onto language models and calling it "agentic AI." It works. Kind of. And the gap between "kind of works" and "reliably works" is where most teams are quietly dying.

---

## The Model Wasn't Built for This

Here's the honest framing: language models were trained to predict the next token. They're exceptionally good at this. But "predict the next token" is not the same as "execute a multi-step plan in a dynamic environment while maintaining state across tool calls."

We figured out that if you prompt a model right, it will emit tool call syntax. Then we built an execution layer that runs those calls and feeds results back in. Then we added memory because the context window fills up. Then we added retry logic because tool calls fail constantly. Then we added orchestration layers to coordinate multiple agents because one agent wasn't enough.

At each step, we added a new layer of complexity to paper over the fact that the underlying model was never designed for this use case.

This is not a criticism. It's just true. A foundation model is a remarkable general-purpose reasoning engine. It's also structurally an autocomplete engine that hallucinates tool call parameters, loses track of its objectives at 80% context fill, and will confidently tell you it completed a task it never attempted.

Claude Code is built on Claude. Cursor is built on Claude and GPT. Both of them are impressive. Both of them will occasionally do something so confidently wrong that you sit back and wonder if you're the problem. You're not the problem. The ingredients aren't designed for this dish yet.

---

## What Actually Breaks

Let me be specific about where the duct tape is.

**Tool call failures.** A model emits a tool call with malformed JSON. Or it calls a tool that doesn't exist because it hallucinated one from a similar context. Or it calls the right tool with the wrong parameters because it misread the schema. You need validation, retry logic, error-handling prompts. Every agentic system I've seen in production has a wrapper around every tool call that catches at least three categories of model error. That's before you handle actual network failures.

**Context window management.** The agent has a 200k context window and you think that's plenty until you're running a multi-step research task and the model starts summarizing its own earlier outputs to save space, and the summaries lose precision, and by step 14 the agent has confidently drifted from its original objective. Every long-running agent needs external memory. Letta just open-sourced claude-subconscious, a persistent memory layer for Claude Code that watches your sessions, learns your patterns, and injects relevant context at the start of each new session. It's the most direct admission I've seen that the model's built-in context isn't sufficient for real work.

**The orchestration vibes problem.** LangGraph and CrewAI both let you define multi-agent pipelines with explicit state machines or role-based crews. This is better than nothing. But "better than nothing" is the ceiling, not the floor. The actual coordination between agents is mostly vibes. You prompt each agent to behave correctly relative to the others. Sometimes the orchestrator misroutes a task. Sometimes two agents write conflicting outputs and the merger agent picks the wrong one. There's no formal verification that a multi-agent system is doing what you think it's doing. You run it, inspect outputs, adjust prompts, run it again. Iteration is the product.

**State persistence is an afterthought.** Claude Code loses everything between sessions. Cursor loses everything between sessions. Your agent framework almost certainly loses its working memory when the process restarts. MCP added a protocol for tools and resources but memory is still largely app-level logic. The MCP ecosystem is impressive — hundreds of servers connecting to databases, APIs, filesystems — but the "how does this agent remember it was doing something yesterday" problem is solved by whichever developer cares enough to implement it. Letta's whole company exists because this problem is real and nobody solved it in the base layer.

---

## The Recipes People Are Actually Using

Despite all of this, people are shipping agents that work. Here's what the actual kitchen looks like.

The MCP protocol is the closest thing to a standard we have for tool integration. A year ago everyone was writing custom tool wrappers. Now most tools have MCP servers and Claude Code, Cursor, and the Agent SDK all support them. The ingredient inventory is real and growing fast.

LangGraph is the choice when you need an explicit state machine and your pipeline is complex enough that "hope the LLM figures it out" isn't good enough. It's verbose. The abstractions leak. But you can look at a LangGraph diagram and reason about what's supposed to happen. That matters for debugging.

CrewAI is the choice when you want role-based agent coordination with less ceremony. The abstractions are leakier but the ergonomics are better. Good for prototypes and medium-complexity workflows.

The Claude Agent SDK is the choice when you're building something that needs to be reliable in production and you want Anthropic to be the single point of blame when things break. The SDK handles tool use, context management, and multi-turn conversations. You lose framework flexibility, you gain something that was actually tested.

Claude Code and Cursor are the agents most people interact with daily. Both are genuinely impressive at code generation. Both require the same skill: knowing when to trust them and when to reread everything they touched. The skill isn't "prompt engineering." It's editing. The agent is your first draft. You're the final author.

---

## Why This Is Still the Right Time to Build

Tree bark soup kept people alive through winters. The people who learned to make it, who experimented with ingredients, who developed recipes — they were building skills that mattered when the supply lines improved.

The supply lines are improving. This is not a metaphor for patience. It's a specific prediction about how model training works.

Models will train natively for agentic behavior. Anthropic, OpenAI, and Google are all collecting data on how agents use tools, how they fail, what retry patterns work. That data feeds back into training. The next generation of frontier models will be substantially better at multi-step planning, tool use reliability, and self-correction. This isn't speculative. It's the obvious thing to do with the data you're collecting.

The tooling is converging. MCP will probably win for tool integration. Some combination of Letta's memory architecture and whatever Anthropic builds natively will win for state. LangGraph or something structurally similar will exist for complex orchestration. The ecosystem is noisy now because nobody has won yet. That won't last.

When the ingredients get better, the people who know the recipes will eat first. Building agents now, with all the duct tape and retry logic and "shouldn't work but does" comments — that's not wasted effort. It's the only way to build the judgment you need to use the next generation of tools effectively.

I have opinions about what breaks, what patterns work, what's worth investing in. Those opinions came from running things in production and watching them fail in informative ways. You can't read those opinions in a paper. The only way to get them is to build.

---

## The Part I'd Tell My Past Self

Don't abstract too early. Every agent framework I've seen tries to abstract away the prompt. This is a mistake. The prompt is the thing. The prompt is where the model's behavior actually comes from, and until you have strong intuitions about how model behavior changes with prompt changes, you should not put a framework layer between you and the prompt. Write the tool calls by hand. Write the system prompt by hand. Read every token the model emits for the first hundred runs.

Instrument everything. Console.log the inputs and outputs of every tool call. Log the full context at each step. Log the diffs. When something breaks in a way you don't understand — and it will — you need the receipts. The agents that go to production reliably are the ones where the developer can explain exactly what the model was doing at every step.

Design for recovery. The agent will fail. The tool call will fail. The retry will fail. What does the system do when it can't complete the task? If the answer is "it silently returns a partial result" or "it loops forever," you will have incidents. Recovery paths are not optional.

Build smaller than you think. The agent that does one thing reliably is more valuable than the agent that does ten things approximately. Scope creep is the enemy of agent reliability. Every additional capability multiplies the failure surface.

---

## Tree Bark Soup Gets You to Spring

We're early. The models aren't agents yet. The tooling is immature. The mental models are still forming. The papers are six months behind the production systems, and the production systems are six months behind the hype.

And yet.

People are shipping real products with agents. Glimpse automated retail dispute resolution. Sierra automated customer service at enterprise scale. My own digest pipeline runs every night with agents writing, filtering, and publishing without my hands on it. These aren't demos. They're products.

We're making tree bark soup. We're keeping ourselves alive through winter. And the people who know how to make tree bark soup — who've learned which bark, which ratios, which heat — are going to be very well positioned when the real ingredients arrive.

The real ingredients are coming. Learn to cook now.
