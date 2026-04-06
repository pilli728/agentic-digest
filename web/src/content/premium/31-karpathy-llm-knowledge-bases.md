---
title: "Karpathy Stopped Using Vector Stores. He Builds Wikis Instead."
description: "Andrej Karpathy shifted most of his token spend from writing code to building personal knowledge bases. Three folders, one schema file, no RAG. Here's the setup."
date: "2026-04-06"
tier: "free"
category: "playbook"
---

Andrej Karpathy posted that he's shifted most of his token spend away from code. He's using LLMs to build personal knowledge bases instead.

Not RAG pipelines. Not vector databases. Wikis — structured, inspectable, human-readable markdown that an LLM organizes and queries on your behalf.

The setup is simple. Three folders.

## The Three-Folder System

**raw/** — you dump everything here. Notes, links, articles, voice memos transcribed to text, code snippets, meeting notes. No organization required. Just paste it in.

**wiki/** — the LLM reads raw/, identifies structure, and writes organized entries. Categories, cross-references, summaries. The AI maintains this. You don't touch it directly.

**outputs/** — when you ask a question, the LLM reads the wiki and writes the answer here. Think of it as a query cache. Answers are persistent and reviewable.

One CLAUDE.md file at the root defines the schema: what categories exist, how entries should be formatted, when to create new categories vs. expand existing ones, how to handle conflicts or duplicates. That schema is the only configuration. Everything else is automatic.

## Why This Beats RAG for Personal Use

Vector stores are great for search over large corpora you don't control. Your own knowledge is different. You know what's in it. You want to be able to read it. You want to edit it by hand when the LLM gets something wrong.

Karpathy's system is fully inspectable. Every wiki entry is a markdown file. You can open it, read it, correct it, and the next LLM session will see the corrected version. There's no embedding to regenerate, no index to rebuild, no semantic drift from a model that learned your content differently than you intended.

The memory is also durable across model changes. When a better model comes out, you point it at the same wiki/ folder. It reads the same structured content. Nothing breaks.

Farzapedia — a personal wikipedia built for his friend Farza — is the first public example of this in practice. The structure is clean enough that you can study it as a reference implementation.

## How to Start Today

Pick one domain where you have accumulated knowledge — a codebase, a research area, a set of meeting notes, a reading list. Create the three folders. Write a minimal CLAUDE.md that defines two or three categories. Then start pasting raw material into raw/ and asking Claude to update the wiki.

The first session will feel slow. By the fifth, it starts to feel like talking to someone who actually knows your work.

[Source: @karpathy](https://x.com/karpathy/status/2039805659525644595)
