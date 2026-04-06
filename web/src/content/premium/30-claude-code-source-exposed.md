---
title: "Claude Code's Source Code Is Now Public Knowledge. Here's What's Inside."
description: "A misconfigured .map file exposed Anthropic's full Claude Code source. 60+ tools, 5 compaction strategies, subagent architecture. Most users are running at 10% capacity."
date: "2026-04-06"
tier: "free"
featured_free: true
category: "analysis"
---

Anthropic accidentally published the full, unobfuscated TypeScript source for Claude Code. A misconfigured .map file in their npm package. Someone found it. The community reverse-engineered it. Now everyone knows how the thing actually works.

Here's what was inside.

## The Architecture Nobody Knew About

Eleven layers. That's how deep the Claude Code architecture goes. The community-facing documentation describes a tool that reads files, edits code, and runs commands. The actual implementation is significantly more complex.

The tools list is the first thing that surprised people. There are 60+ tools in the source. Most Claude Code users interact with maybe six of them. The rest are sitting there unused — not because they're hidden, but because nobody knew to look for them. The hooks system is the biggest one. PostToolUse hooks let you run arbitrary commands after any tool fires. Boris Cherny mentioned this in his workflow posts but most people skimmed past it. The source makes clear this is a first-class feature, not an afterthought.

Subagent architecture is the second revelation. When Claude Code spins up a subagent, the subagents share prompt cache with the parent session. This is why running multiple parallel sessions is cheaper than it looks on paper — you're not duplicating the full context each time. The cost model for parallel work is substantially better than anyone had publicly explained.

## The Five Compaction Strategies

Context window management is where Claude Code's real engineering lives. The source shows five distinct compaction strategies:

**Sliding window** — drops the oldest messages when context fills. What most people assume Claude Code is doing.

**Semantic compression** — identifies and preserves the highest-signal content, summarizes the rest. More expensive but dramatically better for long sessions.

**Tool result pruning** — strips verbose tool outputs while keeping the key results. Relevant when you're running a lot of bash commands or file reads.

**Code diff compression** — represents code changes as diffs rather than full file contents. Reduces context dramatically on codebases with large files.

**Checkpoint-based resumption** — saves session state at intervals so you can resume without re-running the full history. This is what powers session resume in the CLI.

The compaction strategy gets selected dynamically based on session length, tool usage patterns, and available context. You don't choose it. Claude Code chooses it for you. But knowing the strategies exist means you can write CLAUDE.md instructions that influence which one gets selected.

## What This Means for Your Setup

The most actionable insight from the source analysis isn't any specific feature — it's the hooks system.

Every tool call fires an event. You can attach commands to those events. The community has already published hooks for auto-formatting, auto-testing, linting on save, and context injection. If you're not using PostToolUse hooks, you're missing the single biggest leverage point in the whole system.

The second most actionable thing is understanding how subagents actually work. The source makes clear that subagent memory is hierarchical — parent context is accessible to subagents, but subagent work stays scoped. This means you should be dispatching subagents for isolated subtasks, not for anything that needs to share state with the parent. The architecture is designed for that pattern. Most people use subagents wrong because they didn't know the memory model.

## The Broader Signal

Anthropic pulled the source files down once they noticed. But this kind of thing doesn't un-happen. The community analysis is still up. The reverse-engineered documentation is still up. The knowledge is now distributed.

What it tells you: Claude Code is not a thin wrapper around an API. There's serious engineering in the compaction, the hooks, and the subagent coordination. The public documentation describes maybe a third of what's actually there.

Read the community analysis by @mal_shaik and @T3chFalcon. It's worth the two hours.

[Source: @mal_shaik](https://x.com/mal_shaik/status/2038919506224132178)
