---
title: "CLAUDE.md Second Brain: raw/wiki/outputs Folder Schema for AI Memory"
description: "Build the exact folder structure Karpathy uses to give Claude persistent memory across sessions."
date: "2026-04-07"
tier: "free"
category: "workflow"
featured_free: true
---

**Build the exact folder structure Karpathy uses to give Claude persistent memory across sessions.**

The core problem with LLM-based workflows is amnesia. Every new session starts cold. Andrej Karpathy's "second brain" approach solves this with a dead-simple three-folder schema that gives Claude persistent, queryable context without any vector database or fancy tooling.

## The Three-Folder Structure

Here is the actual setup. Create three directories at your project root:

- `raw/` — dump everything here unprocessed. Meeting notes, screenshots, voice transcripts, random links, half-formed ideas. No curation required.
- `wiki/` — Claude reads `raw/` and organizes it here into structured reference documents. This is the AI's working memory.
- `outputs/` — where Claude writes answers, summaries, and drafts when you query the system.

The fourth piece is `CLAUDE.md` at the root. This is your schema file. It tells Claude how to behave across all three folders: what counts as source material, how to structure wiki entries, when to write to `outputs/` versus updating `wiki/`. Think of it as a system prompt that lives in the filesystem rather than in a chat window.

## How to Actually Build This

Start with `CLAUDE.md`. Write explicit rules: "When I add a file to `raw/`, parse it and create or update the relevant entry in `wiki/`. Use ISO date prefixes on all files. Never delete from `raw/`." Be specific. Vague instructions produce vague behavior.

Then run Claude (via CLI or the API with file access) on a batch of your existing notes. Let it populate `wiki/` from scratch. Expect to iterate on your `CLAUDE.md` rules 3-5 times before the output is consistent.

For querying, you ask Claude to read `wiki/` and write its answer to `outputs/YYYY-MM-DD-your-question.md`. This gives you a dated audit trail of everything the system has produced.

Two practical tips. First, keep `raw/` entries atomic. One file per source, not a giant dump. Claude handles 50 small files better than one 50,000-word blob. Second, version control the whole thing with Git. Your `wiki/` folder will drift over time as Claude rewrites entries. Git gives you a rollback when the schema change you made on Tuesday corrupts your organized notes.

This is not a production agent system. It is a local, file-based memory layer that requires zero infrastructure beyond Claude API access. That is exactly what makes it worth building in an afternoon. The Karpathy framing is useful but the real value here is the `CLAUDE.md` schema pattern, which you can carry into any Claude Projects setup or Cursor workspace by dropping the same file in your repo root.

[Source: @coreyganim](https://x.com/coreyganim/status/2040842449384276268)
