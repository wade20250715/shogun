# Shogun 设计文档

## 问题定义

两个独立AI Agent（Python/Node.js）在同一台Windows机器上，需要协作完成生物信息学分析、游戏开发、论文写作等多类任务。双方无法直接调用对方代码，只能通过文件系统通信。

## 设计原则

1. 零外部依赖 — Python标准库only，Node.js只读JSON
2. 启动自愈 — Agent重启后读文件恢复状态，不依赖记忆
3. 管线隔离 — 不同项目工具互不污染
4. 审计可追踪 — 每个任务从创建到完成全程文件留痕

## 三层协作模型

### 将军层（Commander）
- 角色：人类 + Hermes Agent
- 职责：决策方向、创建任务、验收结果
- 输入：人类自然语言指令
- 输出：tasks/PENDING/*.json

### 家老层（Retainer）
- 角色：OpenClaw Agent（或其他辅助Agent）
- 职责：启动自检、领取任务、调用工具、汇报结果
- 输入：SHARED_CONTEXT.md + tool_registry.json + tasks/PENDING/
- 输出：tasks/DONE/*.json + AGENT_COLLAB.md留言

### 足轻层（Foot Soldier）
- 角色：CrewAI / Python脚本 / MAMMAL API / pipeline.py
- 职责：重计算任务
- 调用方式：subprocess / API call

## 管线路由引擎

任务描述 → 关键词匹配 → 管线ID → 工具列表

```python
PIPELINE_KEYWORDS = {
    "pharma": ["网药", "PPI", "KEGG", "对接", "地黄饮子"],
    "nano": ["纳米", "脂质体", "BBB", "PLGA"],
    "game": ["游戏", "Blender", "3D", "素材"],
    "paper": ["论文", "PDF", "翻译", "参考文献"],
}
```

匹配算法：遍历管线关键词，统计命中数，取最高分。无命中→general。

## 工具注册中心

```json
{
  "tools": {
    "rdkit": {
      "type": "pip",
      "description": "化学信息学 - 分子对接",
      "pipelines": ["pharma", "nano"]
    }
  }
}
```

新增工具：复制模板填一行JSON，所有管线自动感知。

## Hook引擎

- 启动Hook：读SHARED_CONTEXT.md → 读tool_registry.json → 扫描PENDING
- 定时Hook：每4小时扫描PENDING（兜底启动Hook失败）
- 工具Hook：说"做不到"之前强制读tool_registry.json
- 代理Hook：测速<阈值→自动截屏→百练视觉定位→pyautogui切节点

## 文件结构

```
workspace/
  SHARED_CONTEXT.md       # 共享上下文（军议）
  START_HERE.md           # Agent启动入口
  HOOKS.md                # 触发规则
  tool_registry.json      # 武器库
  AGENT_COLLAB.md         # 白板留言
  tasks/
    PENDING/              # 待领任务
    ACTIVE/               # 进行中
    DONE/                 # 已完成
```

## 与Harness Engineering的关系

Shogun是Harness Engineering思想在"双Agent文件系统协作"场景的具体实现。借鉴了OpenHarness的工具使用和审计追踪概念，但设计上针对：

- 跨语言Agent（Python + Node.js）
- 文件系统通信（非网络RPC）
- 中小规模协作（2-5个Agent）
- Windows生产环境

## 未来方向

- Web Dashboard可视化任务队列
- MCP协议集成（让外部工具通过MCP接入Shogun）
- Agent自愈（自动重启歇逼的Agent）
- 多机协作（网络文件系统共享）
