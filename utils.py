import bpy
import os

# 配置信息
NODE_GROUP_NAME = "MaterialDebuggerTool"  # 节点组名称
ASSET_RELATIVE_PATH = ("assets", "assets.blend")  # 资产文件路径
AOV_NAME = "MaterialDebuggerToolViewAOV"  # AOV输出名称
AOV_SCREENUV_NAME = "MaterialDebuggerToolScreenUVAOV"  # 屏幕UVAOV输出名称
AOV_NODE_LABEL = "Debugger"  # aov节点名称


def import_node_group():
    """核心函数：从插件目录导入节点组并设为保护"""

    # 1. 检查当前文件是否已经存在该节点组
    if NODE_GROUP_NAME in bpy.data.node_groups:
        # 如果已存在，确保开启保护（Fake User）
        bpy.data.node_groups[NODE_GROUP_NAME].use_fake_user = True
        return

    # 2. 构造资源文件的绝对路径
    addon_dir = os.path.dirname(__file__)
    filepath = os.path.join(addon_dir, *ASSET_RELATIVE_PATH)

    # 检查文件是否存在
    if not os.path.exists(filepath):
        print(f"警告: 插件资源文件不存在 -> {filepath}")
        return

    # 3. 从 .blend 文件中追加 (Append) 节点组
    try:
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            if NODE_GROUP_NAME in data_from.node_groups:
                data_to.node_groups = [NODE_GROUP_NAME]
            else:
                print(f"错误: 在 assets.blend 中未找到名为 '{NODE_GROUP_NAME}' 的节点组")
                return

        # 4. 导入后设置 Fake User
        # 注意：只有在 with 语句结束后，data_to 中的内容才会真正加载进当前 bpy.data
        new_group = bpy.data.node_groups.get(NODE_GROUP_NAME)
        if new_group:
            new_group.use_fake_user = True
            print(f"成功导入并保护节点组: {NODE_GROUP_NAME}")

    except Exception as e:
        print(f"导入节点组时发生错误: {e}")


def open_debug_update(self, context):
    pass
