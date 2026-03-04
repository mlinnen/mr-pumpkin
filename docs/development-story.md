---
layout: page
title: Development Story
permalink: /development-story
description: How Mr. Pumpkin was built using Brady Gaster's Squad agentic coding solution.
---

# Development Story

Mr. Pumpkin was built using **[Squad](https://github.com/bradygaster/squad)** — an agentic coding solution created by [Brady Gaster](https://github.com/bradygaster) that orchestrates a team of specialized AI agents to collaboratively design, build, test, and document software.

Rather than a single AI assistant making all decisions, Squad assembles a *team* — each member with a distinct role, memory, and area of ownership. The agents work in parallel, review each other's work, and accumulate project knowledge over time through a shared decision ledger and per-agent history files.

## The Squad Team

Mr. Pumpkin's AI team was cast from the **Arcane** universe:

| Agent | Role | What They Worked On |
|-------|------|---------------------|
| 🏗️ **Jinx** | Lead | Architecture decisions, scope, code review |
| ⚛️ **Ekko** | Graphics Dev | 2D rendering engine, facial expressions, smooth animations |
| 🔧 **Vi** | Backend Dev | TCP/WebSocket servers, command routing, timeline playback |
| 🧪 **Mylo** | Tester | 430+ test suite, integration tests, dual-protocol validation |
| 📋 **Scribe** | Memory & Logging | Decision ledger, session logs, cross-agent context sharing |
| 🔄 **Ralph** | Work Monitor | Issue triage, backlog tracking, GitHub workflow automation |

## How It Worked

Squad runs inside [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli). Each agent is spawned as an autonomous subprocess with its own charter, history, and bounded scope. The coordinator (Squad itself) routes work, enforces reviewer gates, and keeps agents from stepping on each other.

A few highlights from this project's development:

- **Parallel fan-out**: When adding the WebSocket interface, Ekko (rendering), Vi (server), and Mylo (tests) all worked simultaneously — the test suite was being written while the server was being built.
- **Reviewer gates**: Mylo reviewed all feature work before it was considered done. Rejected work went to a different agent for revision — not back to the original author.
- **Persistent memory**: Every agent appended learnings to their `history.md` after each session. By the end of the project, the team "knew" the codebase patterns without re-reading the code every time.
- **Drop-box decisions**: Agents never wrote to a shared file simultaneously. Instead, each wrote to their own inbox file; Scribe merged them into the canonical `decisions.md`.

## Try Squad on Your Own Project

If you'd like to build your next project with an AI team like this, check out Brady Gaster's Squad:

👉 **[https://github.com/bradygaster/squad](https://github.com/bradygaster/squad)**

Squad works with GitHub Copilot CLI and supports any language or stack. You can have a full team — Lead, devs, tester, and Scribe — up and running in a few minutes.
