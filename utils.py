import bpy
import os
import json
import time

# 配置信息
NODE_GROUP_NAME = "MaterialDebuggerTool"  # 节点组名称
ASSET_RELATIVE_PATH = ("assets", "assets.blend")  # 资产文件路径
AOV_NAME = "MaterialDebuggerToolViewAOV"  # AOV输出名称
AOV_SCREENUV_NAME = "MaterialDebuggerToolScreenUVAOV"  # 屏幕UVAOV输出名称
AOV_NODE_LABEL = "Debugger"  # aov节点名称

_last_dimensions = (0, 0)  # 上一次的宽高比
_draw_handler = None


def import_node_group():
    """从插件目录导入节点组并设为保护"""

    if NODE_GROUP_NAME in bpy.data.node_groups:
        bpy.data.node_groups[NODE_GROUP_NAME].use_fake_user = True
        return

    addon_dir = os.path.dirname(__file__)
    filepath = os.path.join(addon_dir, *ASSET_RELATIVE_PATH)

    if not os.path.exists(filepath):
        print(f"警告: 插件资源文件不存在 -> {filepath}")
        return

    # 从 .blend 文件中追加 (Append) 节点组
    try:
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            if NODE_GROUP_NAME in data_from.node_groups:
                data_to.node_groups = [NODE_GROUP_NAME]
            else:
                print(f"错误: 在 assets.blend 中未找到名为 '{NODE_GROUP_NAME}' 的节点组")
                return

        new_group = bpy.data.node_groups.get(NODE_GROUP_NAME)
        if new_group:
            new_group.use_fake_user = True
            print(f"成功导入并保护节点组: {NODE_GROUP_NAME}")

    except Exception as e:
        print(f"导入节点组时发生错误: {e}")


def save_settings(context):
    # print("保存设置")
    props = context.scene.mat_debug_tool_properties
    # 保存视图实时合成器开启状态
    area = get_max_area()
    if not area:
        return
    for space in area.spaces:
        if space.type == "VIEW_3D":
            props.use_compositor = space.shading.use_compositor
            break
        break
    # 保存合成器节点树使用状态
    props.compositor_use_nodes = context.scene.use_nodes
    # 保存预览节点链接状态
    view_node_state = {}
    if props.use_compositor and context.scene.node_tree:
        tree = context.scene.node_tree
        view_node = None
        for node in tree.nodes:
            if node.type == "VIEWER":
                view_node = node
                break
        if view_node:
            view_node_state["image"] = view_node.inputs[0].links[0].from_node.name if view_node.inputs[0].is_linked else ""
            view_node_state["image_from_socket"] = view_node.inputs[0].links[0].from_socket.name if view_node.inputs[0].is_linked else ""
            view_node_state["alpha"] = view_node.inputs[1].links[0].from_node.name if view_node.inputs[1].is_linked else ""
            view_node_state["alpha_from_socket"] = view_node.inputs[1].links[0].from_socket.name if view_node.inputs[1].is_linked else ""
    props.view_node_link_socket = json.dumps(view_node_state, ensure_ascii=False, indent=None)
    # print("保存的视图节点状态:", props.view_node_link_socket)
    pass


def recovery_settings(context):
    # print("恢复设置")
    props = context.scene.mat_debug_tool_properties
    # 恢复视图实时合成器开启状态
    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.use_compositor = props.use_compositor
                    break
                break
    # 恢复合成器节点树使用状态
    context.scene.use_nodes = props.compositor_use_nodes
    # 恢复预览节点链接状态
    view_node_state = json.loads(props.view_node_link_socket)
    if context.scene.use_nodes:
        tree = context.scene.node_tree
        view_node = None
        for node in tree.nodes:
            if node.type == "VIEWER":
                view_node = node
                break
        if view_node:
            if view_node_state["image"]:
                for node in tree.nodes:
                    if node.name == view_node_state["image"]:
                        tree.links.new(view_node.inputs[0], node.outputs[view_node_state["image_from_socket"]])
                        break
            if view_node_state["alpha"]:
                for node in tree.nodes:
                    if node.name == view_node_state["alpha"]:
                        tree.links.new(view_node.inputs[1], node.outputs[view_node_state["alpha_from_socket"]])
                        break
    pass


def view_settings(context):
    area = get_max_area()
    if not area:
        return
    for space in area.spaces:
        if space.type == "VIEW_3D":
            # space.shading.type = "RENDERED"
            space.shading.use_compositor = "ALWAYS"


def open_debug_update(self, context):
    global _draw_handler
    if self.open_debug:
        save_settings(context)
        view_settings(context)
        bpy.ops.node.connect_to_aov()
        if _draw_handler is None:
            _draw_handler = bpy.types.SpaceView3D.draw_handler_add(monitor_resize_handler, (), "WINDOW", "POST_PIXEL")
    else:
        recovery_settings(context)
        if _draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handler, "WINDOW")
            _draw_handler = None
        pass


def get_compositor_node(context):
    addon_props = context.scene.mat_debug_tool_properties
    scene = context.scene
    if not addon_props.open_debug:
        return None
    if not scene.use_nodes:
        return None
    cmp_tree = scene.node_tree
    if not cmp_tree:
        return None
    target_node = None
    for node in cmp_tree.nodes:
        if node.type == "GROUP" and node.node_tree and node.node_tree.name == NODE_GROUP_NAME:
            target_node = node
            break
    if not target_node:
        return None
    return target_node


def show_frame_update(self, context):
    node = get_compositor_node(context)
    if not node:
        return
    node.inputs[7].default_value = 1.0 if self.show_frame else 0.0


def show_base_color_update(self, context):
    node = get_compositor_node(context)
    if not node:
        return
    node.inputs[8].default_value = 1.0 if self.show_base_color else 0.0


def show_model_update(self, context):
    node = get_compositor_node(context)
    if not node:
        return
    node.inputs[9].default_value = {"AUTO": 0, "GRAY": 1, "RGB": 2, "HSV": 3}.get(self.show_model, 0.0)


def pointer_mode_update(self, context):
    node = get_compositor_node(context)
    if not node:
        return
    node.inputs[11].default_value = 1.0 if self.pointer_mode else 0.0


def monitor_resize_handler():
    global _last_dimensions
    target_area = get_max_area()
    if not target_area:
        return
    # 获取当前尺寸
    current_dims = (target_area.width, target_area.height)
    if current_dims != _last_dimensions:
        _last_dimensions = current_dims
        bpy.app.timers.register(lambda: update_aspect_ratio(current_dims[0], current_dims[1]), first_interval=0.0)


def update_aspect_ratio(width, height):
    node = get_compositor_node(bpy.context)
    if not node:
        return
    node.inputs[10].default_value = width / height
    # print(f"检测到尺寸变化，新的宽高比: {width}x{height}")


def get_max_area():
    context = bpy.context
    target_area = None
    max_size = 0

    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            size = area.width * area.height
            if size > max_size:
                max_size = size
                target_area = area

    return target_area
