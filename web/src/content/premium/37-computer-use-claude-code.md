---
title: "Claude Code Can Now Click Through Your UI. The Last Mile of Agent Automation Just Closed."
description: "Computer use shipped inside Claude Code. Your agent can now open apps, navigate interfaces, and verify its own work visually — all from the CLI."
date: "2026-04-06"
tier: "free"
category: "news"
---

The gap between "the agent wrote the code" and "the agent shipped a working product" just got a lot smaller.

Anthropic shipped computer use inside Claude Code. Your agent can now open your apps, click through your UI, fill out forms, and verify that what it built actually works — all without you touching the keyboard. Research preview, Pro and Max plans only.

## What Changed

Before this, Claude Code was a code-writing and file-editing tool. It could write the login page. It could not check whether the login page actually logs you in.

That verification step always fell to you. Which meant every agent-built feature still needed a human to click through it. The agent would hand off, you'd spot the broken button or the wrong redirect, you'd report back, it would fix it, you'd check again. Tedious loop.

Computer use closes that loop. The agent writes the code, then opens a browser, navigates the flow, confirms it works, and fixes anything broken — before it ever tells you it's done. The iteration cycle happens inside the agent session, not across the human-agent boundary.

## What This Means for Builders

The immediate use case is frontend verification. Write a component, render it, click through all the states. Agent handles it.

The less obvious use case is multi-system workflows. Agents that need to interact with interfaces that don't have APIs — legacy enterprise software, internal tools, anything where clicking is the only option. Computer use turns those into automatable surfaces.

The constraint right now is speed. Computer use is slower than pure code execution — every action involves a screenshot, an interpretation, and a next action. For tight loops this adds up. Use it for verification passes, not for high-frequency operations.

It's a research preview which means it's rough in places. Anthropic will tune it. The direction is clear: agents that can see and interact with software the way a human does, running from your CLI, without a separate desktop automation framework in the stack.

[Source: @claudeai](https://x.com/claudeai/status/2038663014098899416)
