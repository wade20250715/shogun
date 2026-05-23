"""
Shogun usage example.

Prerequisites: create a workspace directory with a tool_registry.json inside.
See README for the registry format.
"""

from shogun import Shogun

# 1. Initialize — point to your workspace
sg = Shogun(root_dir="./example-workspace")

# 2. Boot self-check
status = sg.startup()
print(f"Registry loaded: {status['registry_loaded']}")
print(f"Pending tasks:   {status['pending_tasks']}")

# 3. Pipeline routing (keywords come from YOUR tool_registry.json)
desc = "resize all product images to 800x600 and convert to webp"
pipeline = sg.route_pipeline(desc)
print(f"Matched pipeline: {pipeline}")
print(f"Available tools:  {sg.get_tools()}")

# 4. Create a task
task_id = sg.create_task(
    title="Batch resize product images",
    description=desc,
    assigned_to="image-worker"
)
print(f"Task created: {task_id}")

# 5. Worker claims the task
task = sg.claim_task(task_id)
if task:
    print(f"Claimed: {task['title']}")

# 6. Worker completes it
sg.complete_task(task_id, result="47 images processed, 800x600 webp.")

# 7. Check status
print(sg.status())

# 8. Leave a note on the whiteboard
sg.write_note("Image batch complete. Ready for next step.", author="example-script")

# 9. Read recent whiteboard entries
print("\n--- Whiteboard ---")
print(sg.read_board())
