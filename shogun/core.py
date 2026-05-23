"""
Shogun — Lightweight Multi-Agent Filesystem Collaboration Scheduler.

Three-layer model:
  Commander  = Human + Lead Agent (decide / review / dispatch)
  Retainer   = Worker Agent (claim tasks / use tools / report)
  Foot Soldier = Scripts / Crews (heavy lifting)

Filesystem-driven. Zero dependencies. One Agent in Python, another in Node.js — still works.
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, List, Any


class Shogun:
    """Main scheduler. Reads shared context + tool registry on startup."""

    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.context_path = self.root / "SHARED_CONTEXT.md"
        self.registry_path = self.root / "tool_registry.json"
        self.hooks_path = self.root / "HOOKS.md"
        self.tasks_dir = self.root / "tasks"
        self.pending_dir = self.tasks_dir / "PENDING"
        self.active_dir = self.tasks_dir / "ACTIVE"
        self.done_dir = self.tasks_dir / "DONE"
        self.registry: Dict[str, Any] = {}
        self.current_pipeline: Optional[str] = None

    def startup(self) -> Dict[str, Any]:
        """Three-step boot: load context -> load registry -> scan tasks."""
        return {
            "context_loaded": self._load_context(),
            "registry_loaded": self._load_registry(),
            "pending_tasks": self._scan_tasks(),
        }

    def _load_context(self) -> bool:
        return self.context_path.exists()

    def _load_registry(self) -> bool:
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)
            return True
        return False

    def _scan_tasks(self) -> List[str]:
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        return [f.name for f in self.pending_dir.glob("*.json")]

    # -- pipeline routing --

    def route_pipeline(self, task_description: str) -> str:
        """Match a task description to a pipeline using the registry.

        Pipelines are defined in tool_registry.json under a top-level
        `pipelines` key. Each pipeline has a `keywords` list.

        Falls back to "general" when no keywords match.
        """
        pipelines = self.registry.get("pipelines", {})
        if not pipelines:
            self.current_pipeline = "general"
            return "general"

        scores: Dict[str, int] = {}
        text = task_description.lower()
        for pipe_id, definition in pipelines.items():
            keywords = definition.get("keywords", [])
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                scores[pipe_id] = score

        if not scores:
            self.current_pipeline = "general"
            return "general"

        self.current_pipeline = max(scores, key=scores.get)
        return self.current_pipeline

    def get_tools(self, pipeline_id: Optional[str] = None) -> List[str]:
        """Return tools assigned to the given (or current) pipeline."""
        pid = pipeline_id or self.current_pipeline or "general"
        tools: List[str] = []
        for name, info in self.registry.get("tools", {}).items():
            if pid in info.get("pipelines", []):
                tools.append(f"{name} ({info.get('description', '')})")
        return tools

    # -- task queue --

    def create_task(
        self, title: str, description: str,
        assigned_to: str = "worker",
        pipeline: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a task JSON and place it in PENDING."""
        task_id = f"task-{int(time.time())}"
        task: Dict[str, Any] = {
            "id": task_id,
            "title": title,
            "description": description,
            "assigned_to": assigned_to,
            "pipeline": pipeline or self.route_pipeline(description),
            "status": "pending",
            "created": time.strftime("%Y-%m-%d %H:%M"),
            "tools_available": self.get_tools(pipeline),
        }
        if extra:
            task["extra"] = extra
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        path = self.pending_dir / f"{task_id}.json"
        path.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding='utf-8')
        return task_id

    def claim_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Claim a task: PENDING -> ACTIVE."""
        pending_file = self.pending_dir / f"{task_id}.json"
        if not pending_file.exists():
            return None
        self.active_dir.mkdir(parents=True, exist_ok=True)
        active_file = self.active_dir / f"{task_id}.json"
        pending_file.rename(active_file)
        task = json.loads(active_file.read_text(encoding='utf-8'))
        task["status"] = "active"
        task["claimed"] = time.strftime("%Y-%m-%d %H:%M")
        active_file.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding='utf-8')
        return task

    def complete_task(self, task_id: str, result: str = "", success: bool = True) -> bool:
        """Complete a task: ACTIVE -> DONE."""
        active_file = self.active_dir / f"{task_id}.json"
        if not active_file.exists():
            return False
        self.done_dir.mkdir(parents=True, exist_ok=True)
        done_file = self.done_dir / f"{task_id}.json"
        active_file.rename(done_file)
        task = json.loads(done_file.read_text(encoding='utf-8'))
        task["status"] = "done" if success else "failed"
        task["result"] = result
        task["completed"] = time.strftime("%Y-%m-%d %H:%M")
        done_file.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding='utf-8')
        return True

    # -- status --

    def status(self) -> Dict[str, Any]:
        """Return a snapshot of current state."""
        return {
            "pipeline": self.current_pipeline,
            "tools_loaded": len(self.registry.get("tools", {})),
            "pipelines_defined": len(self.registry.get("pipelines", {})),
            "pending": len(list(self.pending_dir.glob("*.json"))) if self.pending_dir.exists() else 0,
            "active": len(list(self.active_dir.glob("*.json"))) if self.active_dir.exists() else 0,
            "done": len(list(self.done_dir.glob("*.json"))) if self.done_dir.exists() else 0,
        }

    # -- whiteboard --

    def write_note(self, message: str, author: str = "shogun") -> None:
        """Append a timestamped note to AGENT_COLLAB.md."""
        board_path = self.root / "AGENT_COLLAB.md"
        timestamp = time.strftime("%Y-%m-%d %H:%M")
        entry = f"\n[{timestamp}] **{author}**: {message}\n"
        with open(board_path, 'a', encoding='utf-8') as f:
            f.write(entry)

    def read_board(self, max_lines: int = 50) -> str:
        """Read the last N lines of the collaboration whiteboard."""
        board_path = self.root / "AGENT_COLLAB.md"
        if not board_path.exists():
            return ""
        lines = board_path.read_text(encoding='utf-8').splitlines()
        return "\n".join(lines[-max_lines:])
