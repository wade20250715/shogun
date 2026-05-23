# Shogun Design Document

## Problem

Two independent AI agents (Python / Node.js) on the same machine need to collaborate on multi-step projects. Neither can call the other's code directly. The only shared resource: a filesystem.

Existing multi-agent frameworks (LangGraph, CrewAI, AutoGen) assume in-process or API-based communication. They do not solve the **cross-language, filesystem-only** case.

Shogun solves this with a minimal protocol backed by JSON files and conventions.

## Design Principles

1. **Zero external dependencies** — Python stdlib only. Node.js side reads plain JSON.
2. **Boot-time self-recovery** — agent restarts recover state from files, not in-memory.
3. **Pipeline isolation** — different project domains use separate tool sets, no cross-contamination.
4. **Full audit trail** — every task from creation to completion leaves file-level breadcrumbs.

## Three-Layer Collaboration Model

### Commander Layer
- **Who**: Human + Lead Agent
- **Responsibility**: Decide direction, create tasks, review results
- **Input**: Natural language from human
- **Output**: `tasks/PENDING/*.json`

### Retainer Layer
- **Who**: Worker Agent (any language runtime)
- **Responsibility**: Self-check on boot, claim tasks, invoke tools, report results
- **Input**: `SHARED_CONTEXT.md` + `tool_registry.json` + `tasks/PENDING/`
- **Output**: `tasks/DONE/*.json` + entries on `AGENT_COLLAB.md`

### Foot Soldier Layer
- **Who**: Scripts, CrewAI, APIs, subprocess calls
- **Responsibility**: Heavy computation
- **Invocation**: subprocess / HTTP API / CLI

## Pipeline Routing Engine

Task description → keyword matching → pipeline ID → tool list.

### How it works

Pipelines are defined entirely by the user in `tool_registry.json`:

```json
{
  "pipelines": {
    "docs": {
      "description": "Document generation",
      "keywords": ["report", "pdf", "markdown", "latex"]
    }
  }
}
```

Match algorithm: iterate all pipeline keyword sets, count hits in task description, take the highest score. No hits → `"general"`.

**The framework has zero built-in keywords.** Every pipeline and every keyword is user-defined.

## Tool Registry

```json
{
  "tools": {
    "pandoc": {
      "type": "cli",
      "description": "Document converter",
      "pipelines": ["docs"]
    }
  }
}
```

Adding a tool: copy the template, fill one JSON entry. All pipelines auto-detect it.

## Hook Engine

- **Boot hook**: load shared context → load registry → scan PENDING
- **Periodic hook**: scan PENDING every N hours (fallback if boot hook missed something)
- **Tool hook**: before saying "I can't do this", re-read registry
- **Custom hooks**: user-defined trigger rules in `HOOKS.md`

## File Structure

```
workspace/
  SHARED_CONTEXT.md       # Shared context (mission briefing)
  tool_registry.json      # Pipeline + tool definitions
  HOOKS.md                # Trigger rules
  AGENT_COLLAB.md         # Whiteboard
  tasks/
    PENDING/              # Unclaimed tasks
    ACTIVE/               # In progress
    DONE/                 # Completed
```

## Relationship to Harness Engineering

Shogun applies Harness Engineering principles to the specific scenario of **cross-language, filesystem-based multi-agent collaboration**:

- **Sensor** ↔ Hook detection (file watchers, periodic scans)
- **Controller** ↔ Decision logic (pipeline routing, tool matching)
- **Actuator** ↔ Tool execution (subprocess, API calls)
- **Feedback** ↔ Audit trail (task queue state machine + whiteboard)

Where frameworks like OpenHarness focus on benchmark evaluation and model comparison, Shogun focuses on operational coordination between independently deployed agents.

## Future Directions

- Web dashboard for task queue visualization
- MCP protocol integration (external tools via MCP → Shogun)
- Agent heartbeat monitoring
- Multi-workspace federation
