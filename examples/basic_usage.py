"""
Shogun 使用示例

运行前确保目录下有 SHARED_CONTEXT.md 和 tool_registry.json
"""

from shogun import Shogun

# 1. 初始化
sg = Shogun(root_dir="./workspace")

# 2. 启动自检
status = sg.startup()
print(f"注册工具: {status['registry_loaded']}")
print(f"待领任务: {status['pending_tasks']}")

# 3. 管线路由
pipeline = sg.route_pipeline("帮我分析地黄饮子对阿尔茨海默病的PPI网络")
print(f"匹配管线: {pipeline}")
print(f"可用工具: {sg.get_tools()}")

# 4. 创建任务
task_id = sg.create_task(
    title="跑地黄饮子×AD全流程",
    description="用pipeline.py --full --herbs 熟地黄,山茱萸,肉苁蓉,巴戟天,附子,肉桂,石斛,麦冬,五味子,石菖蒲,远志,茯苓,薄荷,生姜,大枣 --disease Alzheimer --db data/herb_db_v2_pipeline.json",
    assigned_to="hermes"
)
print(f"任务已创建: {task_id}")

# 5. 查看状态
print(sg.status())
