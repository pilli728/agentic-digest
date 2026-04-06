---
title: "Sierra Ghostwriter: Describe the Agent You Want. It Builds It."
description: "Sierra's new tool generates production-grade agent configs from plain language descriptions. The 'builder of builders' pattern just arrived at enterprise scale."
date: "2026-04-06"
tier: "pro"
category: "tools"
---

Sierra shipped Ghostwriter. You describe an agent in plain language. It builds it.

Not a rough prototype. A production-grade agent with voice support, chat support, multilingual handling, and action hooks into your systems of record — Salesforce, ServiceNow, whatever you're running.

Blake Taylor, Sierra's CEO, announced it. The positioning is deliberate: this is for the enterprise teams who need agents but don't have a team of AI engineers to build them.

---

## Why Agent Configs, Not Code

The critical architectural decision in Ghostwriter is what it generates: agent configs, not code.

This isn't a limitation. It's a feature.

Code-generating agent builders create a maintenance problem. The non-engineer who described the agent can't read or maintain what got generated. Every change requires a developer. The bottleneck you were trying to remove moves, it doesn't disappear.

Config-based agents are different. The config is readable. A product manager can open it, understand what the agent does, and propose changes. The generated configs are version-controlled, reviewable in PRs, and auditable by compliance teams who don't know Python.

Sierra's platform enforces this separation: the config layer describes behavior, and the execution layer (Sierra's infrastructure) handles the hard parts — multi-turn memory, handoff to human agents, integration with back-end systems, rate limiting, logging, PII handling.

You get the benefits of a well-engineered agent without building the engineering.

---

## The Builder of Builders Pattern

What Ghostwriter represents at the meta level is more interesting than the feature itself.

The standard agent-building workflow today: an engineer writes a system prompt, wires up tool calls, handles errors, tests edge cases, deploys to some cloud function, and monitors it. That takes days to weeks for a production agent.

Ghostwriter compresses that to a description. The compression works because enterprise agent use cases are heavily patterned: answer questions about orders, route support tickets, collect intake information, escalate to humans. Sierra has seen enough of these to encode the patterns.

The "builder of builders" pattern — where the agent-building capability itself becomes a product — is the next architectural layer above agent platforms. We're watching it arrive. Ghostwriter is the first serious enterprise-grade implementation.

---

## What This Means If You Build on Sierra

If you're already on Sierra's platform or evaluating it, Ghostwriter changes the economics of agent deployment.

Before: one engineer-week per production agent, minimum.
After: a product manager describes it, Ghostwriter drafts it, engineering reviews the config.

The bottleneck moves from building to reviewing. That's a meaningful shift. Your AI engineering team becomes a quality gate rather than a construction crew.

The practical implication: you can now run more agents with the same headcount. The question changes from "how many agents can we build?" to "how many can we actually monitor and maintain?" That's a much better problem to have.

One caveat worth stating plainly: Ghostwriter produces Sierra-platform agents, not portable code. You're building on Sierra's infrastructure. If you ever need to migrate, you're re-describing your agents into whatever you migrate to. That's not a dealbreaker for most enterprise contexts, but it's the trade-off you're making.

[Source: Blake Taylor](https://x.com/btaylor/status/2036858449032863898)
