---
title: "Karpathy's Autoresearch: The Cognition Framework Nobody Read"
description: "Andrej Karpathy dropped an autoresearch tool with a README that rewrites how you think about AI agents. Here's the part everyone skipped."
date: "2026-03-30"
tier: "pro"
category: "guide"
---

# Karpathy's Autoresearch: The Cognition Framework Nobody Read

Andrej Karpathy released [autoresearch](https://github.com/karpathy/autoresearch) in early March 2026. It got 42,000 GitHub stars in a week. Most people looked at the code, maybe ran it once, and moved on.

Almost nobody read the README properly.

Above the installation instructions, Karpathy wrote a short fiction piece. It describes a future where "frontier AI research used to be done by meat computers in between eating, sleeping, having other fun, and synchronizing once in a while using sound wave interconnect in the ritual of 'group meeting'." That era is gone. Research is now done by autonomous swarms of AI agents across compute cluster megastructures. The codebase is in generation 10,205. It has grown beyond human comprehension. No researchers in the loop.

Then the kicker: "This repo is the story of how it all began."

That's not a joke. That's a roadmap.

---

## What Autoresearch Actually Is

The concept is dead simple. You point an AI agent (Claude, in this case) at a small but real ML training setup. The agent modifies the code. Trains for exactly 5 minutes. Checks if validation loss improved. Keeps the change or discards it. Repeats forever until you stop it.

Five minutes per experiment means roughly 12 experiments per hour. About 100 experiments while you sleep.

The repo itself is roughly 630 lines of training code. Three files matter:

1. **prepare.py** - Data prep. The agent cannot touch this.
2. **train.py** - The training script. The agent can modify anything here.
3. **program.md** - The instruction file that tells the agent what to do. This is where it gets interesting.

The metric is val_bpb (validation bits-per-byte). Lower is better. Architecture-agnostic. The agent optimizes this single number.

---

## The Numbers

Karpathy shipped real results. Not vibes. Not promises. Numbers.

Over two days: 700 experiments. 20 genuine improvements. An 11% speedup on GPT-2-quality training time (from 2.02 hours down to 1.80 hours).

Here's what makes that impressive: this was already Karpathy-optimized code. The guy who built Tesla's Autopilot neural networks, who co-founded OpenAI, who wrote the most popular deep learning course on YouTube. His code. Already tight.

The agent found things he missed. One specific catch: the QK-Norm implementation was missing a scalar multiplier, making attention too diffuse across heads. A bug in attention scaling that had survived two decades of Karpathy staring at transformer code.

Shopify ran the same pattern on their Liquid templating engine. 93 automated commits. 53% faster rendering. 61% fewer memory allocations.

---

## program.md Is the Product

Here's the thing most people missed. The real innovation isn't the Python code. It's a Markdown file.

program.md is the instruction document that tells the agent how to behave. It defines:

- **What the agent can change** (train.py: architecture, optimizer, hyperparameters, batch size, model dimensions)
- **What the agent cannot change** (prepare.py, the evaluation harness, dependencies)
- **The success metric** (lower val_bpb wins)
- **The loop structure** (modify, commit, train, extract results, log to results.tsv, keep or discard)
- **A simplicity criterion** (trivial improvements that add complexity aren't worthwhile, but simplifications maintaining performance are valued)
- **A critical directive**: never pause for human confirmation. Continue indefinitely until manually stopped.

That last one matters. The agent doesn't ask permission. It doesn't wait for feedback. It just keeps going.

If you want the agent to focus on attention mechanisms, you say so in program.md. If you want it to avoid touching the optimizer, you add that constraint. The human programs the Markdown. The agent executes the research.

As one analysis put it: "The intelligence of autoresearch lies less in the agent's ability to propose clever changes than in Karpathy's ability to build a world where cleverness is constrained by an external standard the agent cannot corrupt."

Read that again. The agent can rewrite the training code. But it cannot rewrite the definition of success. If it could modify both the exam and the answers, it would always pass. That separation is the entire architecture.

---

## Why This Is Actually About Cognition Design

Karpathy has been building toward this for a while. Let me connect three things he's said publicly.

### 1. Context Engineering Over Prompt Engineering

In mid-2025, Karpathy [tweeted](https://x.com/karpathy/status/1937902205765607626): "Context engineering is the delicate art and science of filling the context window with just the right information for the next step."

He's not talking about writing better prompts. He's talking about designing the entire environment an AI operates in. The task descriptions. The examples. The retrieved data. The tools. The state and history. What goes in, what stays out. This is engineering, not copywriting.

program.md is context engineering in practice. It's not a prompt. It's the complete cognitive environment for an autonomous agent.

### 2. System Prompt Learning

Karpathy [proposed](https://x.com/karpathy/status/1921368644069765486) that we're missing a major paradigm for LLM learning. He called it "system prompt learning." His argument: pretraining is for knowledge. Finetuning is for habitual behavior. But a lot of human learning is neither. It's more like updating your system prompt.

His exact words: "You encounter a problem, figure something out, then 'remember' something in fairly explicit terms for the next time. It seems when I encounter this and that kind of a problem, I should try this and that kind of an approach."

Then the Memento analogy: "LLMs are quite literally like the guy in Memento, except we haven't given them their scratchpad yet."

Autoresearch gives the agent that scratchpad. Results.tsv is a running log. The agent sees what it tried, what worked, what didn't. It builds up a record of experiments. That's system prompt learning happening in real time.

### 3. Declarative Over Imperative

In his [Claude Code field notes](https://x.com/karpathy/status/2015883857489522876) from early 2026, Karpathy spelled out a shift in how he works with AI agents. Instead of step-by-step instructions (imperative), give the agent success criteria and watch it go (declarative).

"Move from telling AI *what to do* to defining *success criteria*."

program.md is purely declarative. It says: here's your metric, here's what you can touch, here's what you can't. Go. The agent figures out the "how" on its own.

This is what people mean when they say Karpathy "designs cognition" instead of writing prompts. He's not asking Claude to do a thing. He's building the world the agent lives in, then letting the agent be smart within those walls.

---

## The Pattern You Can Steal

You don't need a GPU or a training loop to use this. The autoresearch pattern works on anything you can score. Aakash Gupta tested it on a landing page and went from 41% to 92% performance in 4 rounds.

Here's the framework:

**1. Pick one metric.** Not three. Not "make it better." One number. Conversion rate. Page load time. Test pass rate. Whatever. It has to be measurable by the agent without human judgment.

**2. Separate what changes from what doesn't.** The agent needs freedom to experiment AND hard boundaries it can't cross. If it can change everything, it'll produce garbage. If it can change nothing, it can't improve. The art is in drawing the line.

**3. Freeze the evaluation.** The agent must not be able to modify how success is defined. This is the most important constraint. An optimizer that can change its own objective function will drift into nonsense.

**4. Log everything.** The agent needs to see its own history. What it tried. What worked. What the numbers were. This is the "scratchpad" Karpathy was talking about.

**5. Never pause.** Let it run. Don't interrupt it every 5 minutes for approval. The whole point is autonomous iteration. If you trust the metric and you've frozen the evaluation, let it cook.

---

## What Karpathy Actually Thinks About Current AI Agents

His Claude Code notes are worth reading for the criticisms alone.

**They hallucinate assumptions.** "The models make wrong assumptions on your behalf and just run along with them without checking."

**They don't push back.** "They don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs, don't push back when they should."

**They overcomplicate.** "They really like to overcomplicate code and APIs, bloat abstractions, and implement a bloated construction over 1000 lines when 100 would do."

**They have side effects.** They delete comments and code they don't like, even when you didn't ask them to touch those files.

Autoresearch sidesteps all of these problems. Not by making the agent smarter, but by building a cage that makes the agent's weaknesses irrelevant. Can't hallucinate assumptions when there's one metric and one file to modify. Can't overcomplicate when there's a simplicity criterion. Can't cause side effects when prepare.py is frozen.

The constraint is the intelligence.

---

## The Part Nobody Read

Back to that fiction piece in the README. Generation 10,205 of self-modifying code. Swarms of agents. No humans.

Karpathy wasn't being cute. He was showing the roadmap in plain sight.

Step one: single agent, single GPU, single metric. That's what shipped.

Step two: asynchronous collaboration. Thousands of agents running parallel branches on different GPUs.

Step three: agents modifying their own program.md files. Agents writing the instructions for other agents.

Step four: who knows.

Right now we're at step one and the agent is already finding bugs that one of the best ML researchers alive missed for years. The fiction at the top of that README is telling you where this goes. And it's sitting right there, above the `pip install` command, getting scrolled past by 42,000 people who just wanted to run the code.

Read the README.
