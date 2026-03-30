---
title: "Letta Fixed Claude Code's Worst Problem"
description: "Claude Code forgets everything between sessions. Letta's claude-subconscious gives it a persistent brain. Two commands to install."
date: "2026-03-30"
tier: "free"
category: "tools"
---

# Letta Fixed Claude Code's Worst Problem

Claude Code has amnesia. Every time you start a new session, it has no idea who you are, what you're building, or that you spent three hours yesterday explaining your database schema. You either re-explain everything or you dump context into CLAUDE.md and pray it reads the right parts.

Letta just fixed this. Two commands. Done.

## What Letta shipped

[claude-subconscious](https://github.com/letta-ai/claude-subconscious) is a background agent that watches your Claude Code sessions and builds persistent memory. It tracks your patterns, your preferences, your unfinished work. Then it injects that memory into every new session automatically.

First session gets the full memory dump. After that, it sends diffs only. It works across parallel sessions too. So if you're running Claude Code in three terminals on different parts of your codebase, the memory stays in sync.

Letta is the team behind MemGPT. Berkeley PhDs who've been thinking about LLM memory longer than most people have been using LLMs. They raised a $10M seed at a $70M valuation from Felicis. This isn't a weekend hack someone pushed to GitHub. It's the core thesis of a well-funded research company, packaged as a free tool.

## Why this actually matters

The dirty secret of AI coding tools is that memory is the bottleneck, not intelligence. Claude is smart enough to write most code you need. The problem is that it doesn't *know* you. Every session starts cold. You lose 10-15 minutes of context-setting on every interaction. Over a week, that's hours of wasted time just getting your AI back to baseline.

CLAUDE.md helps but it's a blunt instrument. You have to manually maintain it. You have to decide what goes in and what stays out. And it's static. It doesn't learn from watching you work.

claude-subconscious is dynamic. It watches what you do and extracts the patterns itself. The things you always ask for. The conventions you follow. The files you always edit together. The mistakes you keep correcting. It builds a model of you as a developer and brings that model into every session.

This is what Karpathy was talking about with "system prompt learning." The idea that LLMs need a scratchpad that persists across sessions and updates itself based on experience. Letta built exactly that.

## The builder's take

Install it. Seriously. It takes two commands and the upside is immediate. If you use Claude Code daily, you'll feel the difference in your first session after setup.

But the bigger signal here is strategic. Memory infrastructure for AI agents is becoming its own category. Right now it's developer tools. Soon it'll be enterprise. Every company deploying agents will need persistent memory that works across sessions, users, and contexts. Letta is positioning to own that layer.

If you're building agents of any kind, pay attention to how claude-subconscious handles memory indexing and retrieval. The "full dump on first session, diffs after" pattern is clever and efficient. Steal that architecture for your own agent memory systems.

The age of stateless AI is ending. Your tools should remember you.
