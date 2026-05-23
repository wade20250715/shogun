# Shogun

> Lightweight multi-agent filesystem collaboration scheduler.

Two independently deployed AI Agents — one Python, one Node.js. No shared memory, no message queue, no RPC. They coordinate through JSON files and shared conventions.

That is what Shogun enables.

## Why Shogun

Multi-agent frameworks exist (LangGraph, CrewAI, AutoGen), but they assume agents live in the same process or talk through the same API.

Reality is messier. You might have a Python agent on Lark and a Node.js agent on Discord. Neither can call the other's code directly. You need a **zero-dependency, filesystem-native, language-agnostic** collaboration protocol.

Shogun is that protocol, packaged as a Python scheduler.

## Three-Layer Model

```
Commander  → Human + Lead Agent (decide, review, dispatch tasks)
    ↓  filesystem
Retainer   → Worker Agent (claim tasks, use tools, report back)
    ↓  subprocess / API
Foot Soldier → Scripts / Crews (heavy computation)
```

## What It Does

- **Boot self-check**: reads shared context, loads tool registry, scans pending tasks
- **Pipeline routing**: task description → keyword match → pipeline → matched tool list. Keywords are user-defined in `tool_registry.json` — the framework ships with zero domain knowledge.
- **Task queue**: PENDING → ACTIVE → DONE state machine, fully file-tracked
- **Tool registry**: JSON-driven. Add a tool entry, all pipelines auto-detect it.
- **Whiteboard**: append-only collaboration log via `AGENT_COLLAB.md`

## Install

```bash
pip install shogun-agent
```

## Quick Start

### 1. Create a workspace

```bash
mkdir my-workspace
cd my-workspace
```

### 2. Define your tool registry

Create `tool_registry.json`:

```json
{
  "pipelines": {
    "images": {
      "description": "Image processing",
      "keywords": ["resize", "crop", "filter", "convert", "png", "jpg"]
    },
    "data": {
      "description": "Data analysis",
      "keywords": ["csv", "plot", "chart", "statistics", "pandas"]
    }
  },
  "tools": {
    "pillow": {
      "type": "pip",
      "description": "Image manipulation",
      "pipelines": ["images"]
    },
    "pandas": {
      "type": "pip",
      "description": "Data analysis library",
      "pipelines": ["data"]
    },
    "matplotlib": {
      "type": "pip",
      "description": "Chart plotting",
      "pipelines": ["images", "data"]
    }
  }
}
```

### 3. Use the scheduler

```python
from shogun import Shogun

sg = Shogun(root_dir="./my-workspace")
sg.startup()

# Pipeline routing auto-detects the right toolset
print(sg.route_pipeline("resize product photos to 800x600"))
# → "images"

# Create a task — tools are auto-matched
task_id = sg.create_task(
    title="Resize product images",
    description="Batch resize all product photos to 800x600 PNG",
    assigned_to="worker-agent"
)

# Worker claims it
task = sg.claim_task(task_id)

# Worker completes it
sg.complete_task(task_id, result="Done. 47 images resized.")

# Check status
print(sg.status())
# → {'pipeline': 'images', 'tools_loaded': 3, 'pending': 0, 'active': 0, 'done': 1}
```

## How Pipeline Routing Works

1. You define pipelines with keywords in `tool_registry.json`
2. `route_pipeline()` scans the task description against all keyword sets
3. Highest keyword match wins
4. No match → falls back to `"general"`

The framework has **no built-in keywords**. Zero domain knowledge. Your tool registry IS the configuration.

## Comparison

| Feature | Shogun | LangGraph | CrewAI |
|---------|--------|-----------|--------|
| Communication | JSON files | Python objects | In-process |
| Cross-language | Any language | Python only | Python only |
| Dependencies | stdlib only | Heavy | Heavy |
| Pipeline routing | Keyword-driven | Manual | Manual |
| State machine | PENDING→ACTIVE→DONE | Custom | Built-in |
| Domain knowledge | Zero (user-defined) | N/A | N/A |

## Control-Engineering Philosophy

- **Sensor** → Hook detection (file changes, timed scans)
- **Controller** → Decision logic (pipeline routing, tool matching)
- **Actuator** → Tool execution (subprocess, API calls)
- **Feedback** → Audit trail (task queue + whiteboard)

## File Structure

```
workspace/
  SHARED_CONTEXT.md      ← shared context (read by all agents)
  tool_registry.json     ← pipeline + tool definitions
  HOOKS.md               ← trigger rules
  AGENT_COLLAB.md        ← whiteboard messages
  tasks/
    PENDING/             ← unclaimed tasks
    ACTIVE/              ← in-progress
    DONE/                ← completed
```

## Requirements

- Python ≥ 3.10
- No external dependencies (stdlib only)

## License

MIT
