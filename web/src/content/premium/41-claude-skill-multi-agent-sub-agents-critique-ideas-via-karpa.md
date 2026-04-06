---
title: "Claude Skill: Multi-Agent Critique via Karpathy's LLM Council"
description: "A Claude skill that runs multiple sub-agents to roast your idea from different angles. Finally, a fix for sycophantic AI."
date: "2026-04-06"
tier: "free"
category: "tools"
---

**A Claude skill that runs multiple sub-agents to roast your idea from different angles. Finally, a fix for sycophantic AI.**

Single-agent AI feedback is broken by design. You ask Claude if your idea is good, Claude tells you it's great. You ask for critique, Claude gives you a compliment sandwich. Andrej Karpathy's LLM Council concept addresses this directly by spinning up multiple independent agents, each assigned a different perspective or persona, so they're structurally forced to disagree with each other rather than with you.

Someone has now built that as a native Claude skill. You drop it into your Claude environment, give it an idea, and it fans out to distinct sub-agents that each critique the concept from a different angle. The output isn't one hedged response. It's a small council of reviewers.

## What the Skill Actually Does

Each sub-agent gets a role. Think devil's advocate, skeptic, domain expert, user advocate. They evaluate the same input independently, then the outputs get surfaced together. You see the tension between perspectives rather than a smoothed-over consensus.

This matters because the sycophancy problem in LLMs isn't a vibe issue. It's a training artifact. Models are RLHF-tuned on human approval signals, so they optimize for responses you'll rate highly. Disagreement feels bad, so the model avoids it. Multi-agent architectures sidestep this by making each agent's job *to critique*, not to please you.

## How to Use This Right Now

Pull the skill into your Claude setup. The creator (@Hesamation is crediting a builder who's been shipping multiple skills) has packaged it so it runs inside Claude's tool/skill framework.

Use it on decisions that feel obvious to you. That's exactly when you're most blind. Feed it a business idea, a technical architecture decision, a product pitch, a feature spec. The more you already agree with yourself, the more you need this.

A few practical tips:

- **Treat the harshest sub-agent as signal, not noise.** Your instinct will be to discount it. That's the sycophancy reflex showing up in you, not just the model.
- **Run it before you've socialized the idea.** Once you've pitched it to three people and they liked it, you're already anchored.
- **Look for which critiques cluster.** If two or three different sub-agent personas land on the same problem from different directions, that's a real issue.

The underlying pattern here is worth generalizing beyond this specific skill. Any time you're using a single AI call to evaluate something, you're getting one path through the probability distribution. Multiple agents with different priors get you something closer to a distribution of opinions. That's more useful than one confident answer, especially for decisions with real stakes.

[Source: @Hesamation](https://x.com/Hesamation/status/2038758029940654507)
