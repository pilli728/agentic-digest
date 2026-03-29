---
title: "AI Agents Are Like Tree Bark Soup"
description: "We're boiling bark and calling it cuisine. A clear-eyed look at why current AI agents are held together with duct tape, why they work anyway, and where this goes when the ingredients catch up."
date: "2026-03-29"
tier: "pro"
category: "opinion"
---

# AI Agents Are Like Tree Bark Soup

There is a dish, documented across multiple periods of famine and frontier survival, called tree bark soup. You strip bark from a tree — ideally birch or pine — boil it until it softens, and eat it. It contains some calories. It will not kill you. It is nobody's idea of a good meal.

I've been thinking about tree bark soup a lot lately, because I think it's the most honest description of what we're doing when we build AI agents in 2026.

---

## What We're Actually Doing

Here's the thing about language models: they were not designed to be agents. This is not a criticism. It's just true. A language model is a next-token predictor trained on text. It's extraordinarily good at that. But "repeatedly call tools, maintain state across a long-running task, recover from failures gracefully, and make coherent decisions over a 45-minute job" is not what the architecture was designed for.

We are asking language models to do something they were not built to do, and we are patching the gap with scaffolding.

The scaffolding looks like this:

**Tool calls.** We can't give a language model a terminal and tell it to go figure things out. Instead we wrap every capability — run a bash command, read a file, search the web — in a structured JSON interface, teach the model to emit valid JSON, parse that JSON, execute the underlying operation, and feed the result back into context. This works. It's also somewhat baroque. The model doesn't "call a tool" in any meaningful sense. It produces text that looks like a tool call, and then we do the rest.

**Memory systems.** A language model has no memory. Every conversation starts from zero. For agents that need to remember anything across sessions — user preferences, prior context, what they did last Tuesday — we bolt on external storage. Vector databases. Key-value stores. Structured files. Letta's claude-subconscious, which is literally a persistent memory layer that injects relevant memories into context at the start of each turn, is clever and useful and also kind of hilarious if you step back and look at it. We are simulating memory for something that anatomically cannot have memory. It's a prosthetic hippocampus.

**Retry loops.** Language models fail. They call tools with malformed parameters. They get confused and loop. They hallucinate capabilities they don't have. They sometimes just... stop making progress. Our response to this is to wrap everything in try/except blocks, add exponential backoff, detect loop conditions, inject "you seem stuck, try a different approach" into context, and set max_turns limits. We are building immune systems for organisms that don't have immune systems.

**Orchestration.** Multi-agent frameworks — and here I mean everything from LangGraph's stateful graphs to the Claude Agent SDK's supervisor patterns to CrewAI's role-based crews — exist because a single agent context window fills up and loses coherence. So we split the work across agents and build routing logic on top. The orchestrator doesn't know what the subagents are doing. The subagents don't know what the orchestrator needs. We write glue code to make them seem coordinated.

This is tree bark soup. Each ingredient is a workaround for something the underlying model can't natively do. Taken together, they produce something functional. Not elegant. Functional.

---

## It Keeps You Alive

Here's what's easy to miss if you're focused on the duct tape: tree bark soup kept people alive.

Across the genuinely hard survival situations where it was used, it worked. Not well. Not comfortably. But people who ate it survived situations where people who didn't eat it did not. The gap between "crude and functional" and "nothing" is enormous.

Claude Code is tree bark soup. It forgets things. It gets confused on large codebases. It loops on hard problems. It sometimes makes confident changes that are subtly wrong. I use it every single day and it has, without exaggeration, multiplied what I can ship by some factor I'm embarrassed to estimate. The underlying model was not designed to be a coding agent. The scaffolding is extensive. It still represents one of the largest practical capability unlocks I've experienced since I started in this field before most people knew what a transformer was.

Cursor is tree bark soup. MCP is tree bark soup — it's a standard for wiring external tools to agents that deliberately avoids solving the hard problems (composability, auth, error semantics) in favor of getting something working now. It's correct to prioritize that. The ecosystem around it has grown to thousands of servers because "works now, imperfect" beats "architecturally ideal, ships never."

The agents people are running in production right now — the ones automating retail deduction disputes, the ones handling customer service at enterprise scale, the ones doing contract review and code review and research synthesis — are all tree bark soup. They work. They run businesses on them.

---

## Why The Metaphor Matters

I want to push back against two failure modes I see constantly.

**Failure mode one: dismissing agents because they're not reliable enough.**

I've talked to teams who've evaluated agent frameworks, found they fail 15-20% of the time on their task set, and concluded that "AI agents aren't ready." This is like evaluating tree bark soup in a restaurant. Of course it's not good enough for a restaurant. But if you're in a situation where tree bark soup is the best available option, rejecting it because it doesn't meet restaurant standards is not a principled position. It's a category error.

The question is not "is this as reliable as deterministic software?" It is "is this better than what we had before?" For an enormous number of tasks, the answer is yes, by a wide margin.

**Failure mode two: treating the current state as if it's the final state.**

The other error is building deeply against the current scaffolding without noticing that the scaffolding is actively changing. Agentic memory that required a vector database and a custom ingestion pipeline in 2024 is handled by system prompts with longer context and auto-memory tools in 2026. Tool use that required careful prompt engineering to get reliable JSON is now native to the models and enforced at the API level. Each generation of models is better at being an agent even though no generation was designed for it.

The recipes are getting refined. The ingredients are getting better. These are not the same thing, and both are happening simultaneously.

---

## What Real Cuisine Looks Like

The terminal state is not "better duct tape." The terminal state is models that are natively agentic — architectures where long-horizon task execution, tool use, memory, and self-correction are first-class properties of the model itself rather than properties of the scaffolding around it.

We're not there. We're also not that far. Here's what the trajectory looks like from where I sit.

**The scaffolding gets thinner.** Every year, things that lived in the framework migrate into the model. Reliable tool use used to require prompt engineering. It's now enforced in training and at the API level. Memory used to require external databases. It now happens partially in context and partially in model-side caching. The layer of code between "I want an agent to do X" and "agent does X" is shrinking.

**The recipes get standardized.** MCP is real and it's winning. The Claude Agent SDK is real. The fact that there's a standard way to wire tools to agents, and a standard loop that powers the best production agent in the world (Claude Code), means that knowledge about how to build good agents is becoming more transferable. In 2023, every agent builder was reinventing fundamentals. Now there are cookbooks.

**The evaluation problem gets solved.** Right now, testing agents is genuinely hard. The nondeterminism makes traditional software testing inadequate. You can't unit test a model. The field is converging on eval frameworks — Braintrust, Langfuse, Promptfoo, DeepEval — that treat agent quality as a statistical property rather than a binary. This is the right framing. You don't test that the agent always does exactly the right thing. You test that it does the right thing 97% of the time and that number doesn't degrade.

**The models catch up.** ARC-AGI-3, which tests genuine open-ended exploration in interactive environments, scores 0.26% for frontier models. Humans score 100%. That gap will close. Not this year. Probably not next year. But the pressure is explicit, the benchmark is public, and the labs know that the gap between "follows instructions" and "figures things out" is where the real value lies.

When it closes, the soup becomes cuisine.

---

## What To Do While The Kitchen Is Still a Mess

None of this is an argument to wait. Waiting for the architecture to mature before building agents is like waiting for roads to exist before moving somewhere. The roads are being built. You navigate the current roads.

Practically, this means a few things.

Build at the current abstraction level, not one below it. Don't reimplement tool use from scratch when MCP exists. Don't hand-roll memory when claude-subconscious or equivalent works for your use case. The value of being one abstraction level up is that when the layer below you improves, you get the improvement for free.

Know where the duct tape is. Every production agent has failure modes baked into its architecture. The teams that operate agents successfully are the ones who know exactly which parts are fragile and have monitoring on those parts. The teams that get surprised are the ones who treated "it works in testing" as "it's reliable."

Invest in evals before you invest in features. The agent that has 30 representative test cases running on every deploy is more valuable than the agent with three more capabilities and no way to know when it regresses.

And keep your sense of humor about it. We are boiling bark. We are also making something genuinely useful out of materials that were not designed for the purpose, and that is, historically, how all cooking started.

---

The first fire was probably an accident. The first bread was probably rock-hard and dense and nothing like what bread became. The people who ate it weren't wrong to eat it, and they weren't naive for imagining something better. They were just early.

We're early. The soup is hot. Eat it.
