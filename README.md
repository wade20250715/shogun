# Shogun 将军

> 将军家老足轻 — 轻量级多Agent文件系统协作调度器

两个独立部署的AI Agent，一个Python一个Node.js，没有共享内存，没有消息队列——就靠JSON文件和约定协作了好几个月。

这就是Shogun的实战验证。

## 为什么需要Shogun

多Agent框架很多（LangGraph、CrewAI、AutoGen），但它们都假设Agent在同一个进程里，或通过同一套API通信。

实际场景是：你有一个跑在飞书上的Python Agent（Hermes），一个跑在微信上的Node.js Agent（OpenClaw），两个都无法直接调对方的代码。你需要一套**零依赖、纯文件系统、任何语言都能用**的协作协议。

Shogun就是干这个的。

## 三层模型

```
将军层 → 人类 + 主Agent（决策/验收/放任务）
  ↓ 文件系统
家老层 → 辅助Agent（领任务/调工具/交活）
  ↓ 子进程
足轻层 → 脚本/CrewAI/API（重体力活）
```

## 核心能力

- 启动自检：读共享上下文 → 读武器库 → 扫描待领任务
- 管线路由：输入"地黄饮子PPI网络图"，自动匹配pharma管线14个工具
- 任务队列：PENDING→ACTIVE→DONE 状态机，全程文件追踪
- 工具注册：JSON驱动，新工具加一行自动感知，5条管线50个工具已验证

## 安装

```bash
pip install shogun-agent
```

## 三分钟上手

```python
from shogun import Shogun

sg = Shogun(root_dir="./workspace")
sg.startup()

# 创建任务
task_id = sg.create_task(
    title="调整PPI网络图配色",
    description="地黄饮子PPI网络图的节点颜色太暗，换Nature配色",
    assigned_to="openclaw"
)
# → 自动匹配pharma管线，附带14个可用工具

# Agent领取
task = sg.claim_task(task_id)

# Agent完成
sg.complete_task(task_id, result="已用matplotlib重绘，300DPI，Nature配色")
```

## 跟其他框架的区别

| 特性 | Shogun | LangGraph | CrewAI |
|------|--------|-----------|--------|
| 通信方式 | JSON文件 | Python对象 | 进程内 |
| 跨语言 | ✅ 任意 | ❌ Python only | ❌ Python only |
| 零依赖 | ✅ stdlib | ❌ | ❌ |
| 管线路由 | ✅ 关键词匹配 | 手动 | 手动 |
| 状态机 | PENDING→ACTIVE→DONE | 自定义 | 内置 |
| 生产验证 | ✅ 双Agent 2个月 | ✅ | ✅ |

## 设计哲学

控制工程的闭环反馈：

- 传感器层 → Hook检测（文件变化、定时扫描）
- 控制器层 → 决策逻辑（管线路由、工具匹配）
- 执行器层 → 工具调用（50工具5管线）
- 反馈层 → 审计追踪（任务队列+白板留言）

## License

MIT
