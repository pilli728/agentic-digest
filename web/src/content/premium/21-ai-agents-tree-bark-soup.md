---
title: "AI Agents Are Like Tree Bark Soup"
description: "We're boiling bark and calling it cuisine. Tool calls, retry loops, and duct-taped memory systems are keeping us alive — but nobody's calling it fine dining. Here's where this goes."
date: "2026-03-29"
tier: "pro"
category: "opinion"
---

# AI Agents Are Like Tree Bark Soup

Tree bark soup is what you make when you have nothing else.

You strip the inner bark off a birch or pine, boil it for an hour, maybe throw in some lichen if you're feeling ambitious. It's caloric. It keeps you alive. People have survived winters on it. But nobody who has ever eaten it has done so by choice, and no one has ever written a Substack about their bark soup journey with a "recipe card at the bottom of this post."

I've been building AI agents for two years. Before that, I was one of maybe a few thousand people who actually paid attention when GPT-3 dropped and realized something had fundamentally changed. And I'm here to tell you: we are making tree bark soup.

It's good soup. It's keeping us alive. But let's be honest about what we're doing.

---

## What "Agentic AI" Actually Looks Like Right Now

Here's the reality underneath the demos and the funding announcements.

A language model is, at its core, a next-token predictor. It was trained to continue text. That's it. Somewhere along the way, we discovered that if you give it a list of tools and write "you are an intelligent agent capable of using these tools to accomplish goals," it kind of... does that? It reasons about which tool to call. It remembers (sort of) what it just did. It retries when things fail.

We didn't build an agent. We found one hiding inside a text predictor and we've been coaxing it out with prompts ever since.

The scaffolding around modern agents is extraordinary in its resourcefulness. You want memory? Great — you can use a vector database, or a key-value store, or a summary loop, or [Letta's claude-subconscious](https://github.com/letta-ai/claude-subconscious), which literally teaches Claude to manage its own memory by writing to and reading from a structured store mid-conversation. You want tool use? The APIs are there — Anthropic's function calling, OpenAI's, MCP if you want something that actually composes. You want multi-step reasoning? Chain-of-thought, reflection loops, or just hope the model figures it out.

It works. Kind of. The way bark soup works. Every one of these solutions is a workaround for the fact that the underlying model was not designed to be an agent. We're bolting agentic behavior onto something that was fundamentally built to do something else.

---

## The Specific Shape of the Duct Tape

Let me be concrete, because vague criticism is just noise.

**Tool calls break in ways that are hard to debug.** Models hallucinate arguments to functions that don't exist. They call tools in the wrong order. They get stuck in retry loops where they make the same mistake repeatedly with increasing confidence. I have a codebase with a retry wrapper that wraps a retry wrapper — not because I'm bad at software, but because the underlying behavior is stochastic enough that you need redundancy at multiple levels.

**Context windows are still a real constraint.** Claude's 200k context window is genuinely remarkable, but agents doing real work burn through it fast. Tool call outputs pile up. Conversation history accumulates. You spend a non-trivial amount of engineering effort deciding what to summarize, what to truncate, what to store externally. Memory is a solved problem the way "having a place to sleep" is a solved problem — technically true, but the solutions vary wildly in quality.

**Orchestration is mostly vibes.** If you want multiple agents to work together — one doing research, one writing, one reviewing — you're stitching that together yourself. LangGraph gives you a graph. CrewAI gives you roles. AutoGen gives you a chat room where the agents argue. None of them feel like they were designed; they feel like they were discovered, then documented, then shipped. MCP is the first real attempt at a standard for how tools compose across agent boundaries, and it's promising precisely because it acknowledges that agents need to call other agents' tools and the current state of that is chaos.

**Claude Code and Cursor are the best evidence that agentic AI works.** They're also the best evidence of how much hidden complexity it takes to make it work. Cursor has an entire invisible layer of context management — figuring out which files are relevant, which symbols to include, what to summarize — that runs before the model ever sees your prompt. Claude Code has hooks, memory systems, and a parallel agent architecture. These aren't simple wrappers around an API. They're production engineering on top of a foundation that wasn't built for production use.

---

## Nobody Would Call It Fine Dining

And here's the thing: it's impressive. I want to be clear that I'm not dismissing what exists. The agents I've built in the last two years have done things I genuinely didn't believe were possible two years ago. I have an agent that wakes up every morning, reads a few hundred RSS feeds, scores each article against a set of criteria that would take a human editor thirty seconds to articulate but a developer three weeks to specify, and generates a newsletter that's good enough that people pay for it.

That's remarkable. Six months earlier I would have called it a research demo.

But I also have, in my codebase: five different retry mechanisms, three memory solutions that don't quite talk to each other, a prompt file that is 847 lines long, and at least one comment that reads `# this shouldn't work but it does, don't touch it`.

That is not fine dining. That is survival cooking. That is "I found some bark and I know how to boil water and I will not die today."

---

## Where This Goes

The trajectory is clear if you've been watching long enough.

The models are getting better at being agents. Not because anyone declared "now we're training for agentic behavior" — though that's happening too — but because the feedback loop is tightening. RLHF with tool use trajectories. Constitutional AI applied to multi-step reasoning. Training on synthetic agent rollouts where the model learns to plan and recover. The thing that's currently "coaxed out" of the model through clever prompting is slowly becoming a first-class property of the model itself.

The tooling is converging. MCP is becoming the standard for tool composition. The memory solutions are consolidating — not around one winner, but around a handful of patterns that actually work. The frameworks that survive will be the ones that acknowledge the duct tape and hide it gracefully, rather than the ones that pretend it doesn't exist.

The recipes are being written down. Two years ago, agent patterns were transmitted orally — "here's how I handle retry logic, here's my trick for keeping context under control." Now they're in documentation, in open-source repos, in talks. The accumulated craft knowledge of building agents is becoming legible. That's how bark soup becomes bread. Not by discovering wheat — by figuring out fermentation, milling, heat, timing. The craft catches up to the ingredients.

And the ingredients are improving. We're already seeing models that maintain coherent multi-step plans without external scaffolding, that manage their own context more gracefully, that fail more predictably. "Fail more predictably" sounds like a low bar until you've debugged an agent that failed in six different ways across three retries and left your database in an inconsistent state.

Eventually — not soon, but eventually — the agents we build won't feel like survival cooking. They'll feel like software. Designed, not discovered. Reliable, not merely probabilistic. The current generation of agent developers is figuring out where the rocks are in this river so the next generation doesn't have to.

---

## What To Do With This

If you're building agents right now:

**Embrace the bark.** The duct tape isn't failure; it's adaptation. The engineers who built the first reliable bridges used materials that were poorly understood and empirical methods that would embarrass a modern structural engineer. They built anyway, and the bridges stood, and we learned from them.

**Document your workarounds.** The most valuable knowledge in agentic AI right now isn't the research papers — it's the production hacks. Write down why you have five retry mechanisms. Write down what broke when you had three. That's the knowledge that ages poorly but matters most right now.

**Don't wait for the cuisine.** The people who wait for the technology to mature before building will arrive to a market that's already been shaped by the people who built with bark. The tree bark soup veterans are going to have an enormous advantage when the real ingredients arrive, because they'll understand the constraints from first principles, not just from documentation.

**Stay honest about what you have.** The hype cycle wants you to call it "production-grade autonomous AI" when you have a Python loop with a 3-second sleep between API calls. Resist that. Not for humility's sake, but because the gap between what you claim and what you have is where technical debt hides. Name the duct tape. Then you can replace it when something better comes along.

---

I've been building agents with bark. I'll keep building agents with bark, because it's what's available and because something that was impossible eighteen months ago is now merely difficult, which means something that's difficult now will be routine in eighteen months.

The soup is getting better. The recipes are improving. The fire management is becoming an art.

And someday someone will look back at the tools we used to build the first real AI agents — the retry wrappers and the 800-line prompt files and the memory systems that didn't quite talk to each other — the way we look back at analog computers and punch cards. Not with contempt, but with something like affection. Look what they built with that.

In the meantime: stir the pot.
