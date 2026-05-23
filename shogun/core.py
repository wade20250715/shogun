"""
Shogun — 将军：轻量级多Agent文件系统协作调度器

将军家老足轻三层模型：
  将军层 = 人类 + 主Agent（决策/验收）
  家老层 = 辅助Agent（执行/汇报）
  足轻层 = 脚本/CrewAI（重体力活）

纯文件系统驱动。零外部依赖。两Agent一个Python一个Node.js也能跑。
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, List, Any


class Shogun:
    """主调度器。启动即读上下文，自动匹管线路由工具。"""

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
        self.tools_for_task: List[str] = []

    def startup(self) -> Dict[str, Any]:
        """启动三步：读上下文 → 读武器库 → 扫描任务"""
        status = {
            "context_loaded": self._load_context(),
            "registry_loaded": self._load_registry(),
            "pending_tasks": self._scan_tasks(),
        }
        return status

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

    # --- 管线路由 ---

    PIPELINE_KEYWORDS = {
        "pharma": ["地黄饮子", "网药", "PPI", "KEGG", "对接", "docking", "靶点", "AD", "阿尔茨海默"],
        "nano": ["纳米", "递送", "脂质体", "BBB", "血脑屏障", "PLGA"],
        "game": ["江岛之夏", "游戏", "Blender", "3D", "素材", "Unity"],
        "paper": ["论文", "写作", "翻译", "PDF", "参考文献", "润色"],
    }

    def route_pipeline(self, task_description: str) -> str:
        """根据任务描述匹配管线"""
        scores = {}
        for pipe_id, keywords in self.PIPELINE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in task_description.lower())
            if score > 0:
                scores[pipe_id] = score
        if not scores:
            return "general"
        self.current_pipeline = max(scores, key=scores.get)
        return self.current_pipeline

    def get_tools(self, pipeline_id: Optional[str] = None) -> List[str]:
        """获取指定管线的工具列表"""
        pid = pipeline_id or self.current_pipeline or "general"
        tools = []
        if self.registry:
            for name, info in self.registry.get("tools", {}).items():
                if pid in info.get("pipelines", []):
                    tools.append(f"{name} ({info.get('description', '')})")
        return tools

    # --- 任务管理 ---

    def create_task(self, title: str, description: str, assigned_to: str = "openclaw",
                    pipeline: Optional[str] = None) -> str:
        """创建任务JSON放入PENDING"""
        task_id = f"task-{int(time.time())}"
        task = {
            "id": task_id,
            "title": title,
            "description": description,
            "assigned_to": assigned_to,
            "pipeline": pipeline or self.route_pipeline(description),
            "status": "pending",
            "created": time.strftime("%Y-%m-%d %H:%M"),
            "tools_available": self.get_tools(pipeline),
        }
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        with open(self.pending_dir / f"{task_id}.json", 'w', encoding='utf-8') as f:
            json.dump(task, f, ensure_ascii=False, indent=2)
        return task_id

    def claim_task(self, task_id: str) -> Optional[Dict]:
        """领取任务：PENDING → ACTIVE"""
        pending_file = self.pending_dir / f"{task_id}.json"
        if not pending_file.exists():
            return None
        self.active_dir.mkdir(parents=True, exist_ok=True)
        active_file = self.active_dir / f"{task_id}.json"
        pending_file.rename(active_file)
        with open(active_file, 'r', encoding='utf-8') as f:
            task = json.load(f)
        task["status"] = "active"
        task["claimed"] = time.strftime("%Y-%m-%d %H:%M")
        with open(active_file, 'w', encoding='utf-8') as f:
            json.dump(task, f, ensure_ascii=False, indent=2)
        return task

    def complete_task(self, task_id: str, result: str = "", success: bool = True) -> bool:
        """完成任务：ACTIVE → DONE"""
        active_file = self.active_dir / f"{task_id}.json"
        if not active_file.exists():
            return False
        self.done_dir.mkdir(parents=True, exist_ok=True)
        done_file = self.done_dir / f"{task_id}.json"
        active_file.rename(done_file)
        with open(done_file, 'r', encoding='utf-8') as f:
            task = json.load(f)
        task["status"] = "done" if success else "failed"
        task["result"] = result
        task["completed"] = time.strftime("%Y-%m-%d %H:%M")
        with open(done_file, 'w', encoding='utf-8') as f:
            json.dump(task, f, ensure_ascii=False, indent=2)
        return True

    def status(self) -> Dict[str, Any]:
        """返回当前状态快照"""
        return {
            "pipeline": self.current_pipeline,
            "tools_loaded": len(self.registry.get("tools", {})),
            "pending": len(list(self.pending_dir.glob("*.json"))) if self.pending_dir.exists() else 0,
            "active": len(list(self.active_dir.glob("*.json"))) if self.active_dir.exists() else 0,
            "done_today": len(list(self.done_dir.glob("*.json"))) if self.done_dir.exists() else 0,
        }
