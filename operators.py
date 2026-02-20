import bpy
from .utils import *
from .i18n import translations


class VIEW3D_OT_TestOperator(bpy.types.Operator):
    """Test Operator"""

    bl_idname = "view3d.test_operator"
    bl_label = "Test Operator"

    def execute(self, context):
        state = bpy.data.materials["Material"].node_tree.nodes["Texture Coordinate"].type
        props = context.scene.mat_debug_tool_properties
        # for area in context.screen.areas:
        #     if area.type == "VIEW_3D":
        #         for space in area.spaces:
        #             if space.type == "VIEW_3D":
        #                 props.viewport_composite_state = space.shading.use_compositor
        # print(props.viewport_composite_state)
        print(state)
        return {"FINISHED"}


class NODE_OT_connect_to_aov(bpy.types.Operator):
    """Shift+Alt+Click: 循环连接节点输出到 AOV"""

    bl_idname = "node.connect_to_aov"
    bl_label = "Connect to AOV"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        # 1. 必须是节点编辑器
        # 2. 必须是着色器节点树 (ShaderNodeTree)
        # 3. 必须已经加载了节点树 (即编辑器不是空的)
        return space.type == "NODE_EDITOR" and space.tree_type == "ShaderNodeTree" and space.node_tree is not None and space.shader_type == "OBJECT"

    def invoke(self, context, event):
        # 1. 尝试选中鼠标下的节点
        try:
            bpy.ops.node.select(location=(event.mouse_region_x, event.mouse_region_y), extend=False)
        except RuntimeError:
            # 如果没点到节点，直接取消
            return {"CANCELLED"}

        return self.execute(context)

    def execute(self, context):
        print("执行")
        tree = context.space_data.node_tree
        active_node = context.active_node
        if not active_node:
            return {"CANCELLED"}
        if not active_node.select:
            return {"CANCELLED"}
        props = context.scene.mat_debug_tool_properties
        if not props.open_debug:
            props.open_debug = True
        # 创建视图层AOV
        self.ensure_view_layer_aov(context)
        # 创建屏幕UV AOV
        self.ensure_view_layer_screenUV_aov(context)

        # 创建AOV节点
        aov_node = self.get_or_create_aov_node(tree)
        screenUV_node = self.get_or_create_screenUV_aov_node(tree)
        # 设置合成器
        self.setup_compositor(context)
        # 3.1 获取当前已连接的端口索引（如果已连接）
        current_index = -1

        # 遍历所有连线，看是否有线是从 active_node 连到 aov_node 的
        for link in tree.links:
            if link.to_node == aov_node and link.from_node == active_node:
                # 找到了现有的连接，获取它在 active_node 输出列表中的索引
                # 注意：我们要找的是“输出插槽”的索引
                for i, socket in enumerate(active_node.outputs):
                    if socket == link.from_socket:
                        current_index = i
                        break
                # 找到一个就可以退出了（假设只连了一根线）
                if current_index != -1:
                    break

        # 3.2 寻找下一个有效的插槽
        # 我们从 current_index + 1 开始找，如果超出了长度就取模回到 0
        num_outputs = len(active_node.outputs)
        if num_outputs == 0:
            self.report({"WARNING"}, "节点没有输出端口")
            return {"CANCELLED"}

        target_socket = None

        # 最多尝试遍历一圈 (num_outputs 次)
        for i in range(1, num_outputs + 1):
            # 计算下一个索引 (循环)
            check_index = (current_index + i) % num_outputs
            socket = active_node.outputs[check_index]

            # 过滤条件：
            # 1. 插槽必须启用 (enabled)
            # 2. 插槽不能是 BSDF/Shader 类型 (AOV 只能接数据，不能接 Shader)
            if socket.enabled and socket.type != "SHADER":
                target_socket = socket
                break

        if not target_socket:
            self.report({"WARNING"}, "不支持shader类型节点")
            return {"CANCELLED"}

        # 创建连接
        tree.links.new(target_socket, aov_node.inputs[0])

        # self.report({"INFO"}, f"已连接: {active_node.name} -> [{target_socket.name}]")

        return {"FINISHED"}

    def get_or_create_aov_node(self, tree):
        """寻找现有的 AOV 节点，如果没有则创建"""
        # 优先按标签(Label)或名称查找，防止重复创建
        for node in tree.nodes:
            if node.type == "OUTPUT_AOV" and (node.label == AOV_NODE_LABEL or node.aov_name == AOV_NAME):
                return node

        # 创建新的
        node = tree.nodes.new(type="ShaderNodeOutputAOV")
        node.name = "AOV_Auto_Node"
        node.label = AOV_NODE_LABEL
        node.aov_name = AOV_NAME

        # 放在视口右侧一点的位置（简单处理）
        node.location = (200, 0)
        # 如果有 active node，放在 active node 右边
        if tree.nodes.active:
            node.location = (tree.nodes.active.location.x + 300, tree.nodes.active.location.y)

        return node

    def get_or_create_screenUV_aov_node(self, tree):
        """寻找现有的 ScreenUV AOV 节点，如果没有则创建"""
        screenUV_AOVnode = None
        for node in tree.nodes:
            if node.type == "OUTPUT_AOV" and (node.label == AOV_NODE_LABEL + "_ScreenUV" or node.aov_name == AOV_SCREENUV_NAME):
                screenUV_AOVnode = node
                break
        if screenUV_AOVnode is None:
            # 创建新的
            screenUV_AOVnode = tree.nodes.new(type="ShaderNodeOutputAOV")
            screenUV_AOVnode.name = "AOV_ScreenUV_Node"
            screenUV_AOVnode.label = AOV_NODE_LABEL + "_ScreenUV"
            screenUV_AOVnode.aov_name = AOV_SCREENUV_NAME

        view_node = None
        for node in tree.nodes:
            if node.type == "OUTPUT_AOV" and (node.label == AOV_NODE_LABEL or node.aov_name == AOV_NAME):
                view_node = node
                break

        screenUV_AOVnode.location = (view_node.location.x, view_node.location.y - 100) if view_node else (200, -200)
        if not screenUV_AOVnode.inputs[0].is_linked:
            screenUV_node = tree.nodes.new(type="ShaderNodeTexCoord")
            screenUV_node.name = "ScreenUV"
            screenUV_node.label = "ScreenUV"
            screenUV_node.location = (screenUV_AOVnode.location.x - 150, screenUV_AOVnode.location.y - 50)
            tree.links.new(screenUV_node.outputs["Window"], screenUV_AOVnode.inputs[0])
            screenUV_node.hide = True
            screenUV_node.select = False
        screenUV_AOVnode.select = False
        return screenUV_AOVnode

    def ensure_view_layer_aov(self, context):
        aov_name = AOV_NAME
        view_layer = context.view_layer

        aov = view_layer.aovs.get(aov_name)

        if aov:
            return aov
        new_aov = view_layer.aovs.add()
        new_aov.name = aov_name
        new_aov.type = "COLOR"

    def ensure_view_layer_screenUV_aov(self, context):
        aov_name = AOV_SCREENUV_NAME
        view_layer = context.view_layer

        aov = view_layer.aovs.get(aov_name)

        if aov:
            return aov
        new_aov = view_layer.aovs.add()
        new_aov.name = aov_name
        new_aov.type = "COLOR"

    def setup_compositor(self, context):
        """
        子函数：配置合成器
        1. 开启实时合成器
        2. 记录原始连接状态
        3. 链接 AOV -> MaterialDebuggerTool -> Composite
        """
        scene = context.scene

        # 1. 确保启用合成节点
        if not scene.use_nodes:
            scene.use_nodes = True

        tree = scene.node_tree

        rl_node = None  # 渲染层节点
        view_node = None  # 预览器节点
        tool_node = None  # MaterialDebuggerTool

        TOOL_GROUP_NAME = NODE_GROUP_NAME

        # 查找现有节点
        for node in tree.nodes:
            if node.type == "R_LAYERS":
                rl_node = node
            elif node.type == "VIEWER":
                view_node = node
            elif node.type == "GROUP" and node.node_tree and node.node_tree.name == TOOL_GROUP_NAME:
                tool_node = node

        # 错误检查
        if not rl_node:
            rl_node = tree.nodes.new(type="CompositorNodeRLayers")
            rl_node.location = (-100, 0)

        if not view_node:
            # 如果没有预览器节点，创建一个
            view_node = tree.nodes.new("CompositorNodeViewer")
            view_node.location = (400, 0)
        if not tool_node:
            # 创建工具节点组
            tool_node = tree.nodes.new(type="CompositorNodeGroup")
            node_group = bpy.data.node_groups.get(TOOL_GROUP_NAME)
            if not node_group:
                import_node_group()
                node_group = bpy.data.node_groups.get(TOOL_GROUP_NAME)
            if not node_group:
                print("无法导入节点组：节点组不存在")
                return

            tool_node.node_tree = node_group
            tool_node.name = "MaterialDebuggerTool"
            tool_node.label = "Material Debugger Tool"
            tool_node.location = (200, 0)
        # 创建连接
        view_aov_socket = rl_node.outputs.get(AOV_NAME)
        if not view_aov_socket:
            self.ensure_view_layer_aov(context)
            view_aov_socket = rl_node.outputs.get(AOV_NAME)
        if not view_aov_socket:
            self.report({"WARNING"}, f"渲染层节点未找到 AOV 通道 '{AOV_NAME}'")
            return

        view_screenuv_socket = rl_node.outputs.get(AOV_SCREENUV_NAME)
        if not view_screenuv_socket:
            self.ensure_view_layer_screenUV_aov(context)
            view_screenuv_socket = rl_node.outputs.get(AOV_SCREENUV_NAME)
        if not view_screenuv_socket:
            self.report({"WARNING"}, f"渲染层节点未找到 AOV 通道 '{AOV_SCREENUV_NAME}'")

        tool_node_val_socket = tool_node.inputs.get(tool_node.inputs[0].name)
        tool_node_uv_socket = tool_node.inputs.get(tool_node.inputs[1].name)
        tool_node_output_socket = tool_node.outputs.get(tool_node.outputs[0].name)
        if not tool_node_val_socket or not tool_node_uv_socket or not tool_node_output_socket:
            self.report({"WARNING"}, "资产错误")
            return
        # 创建连接,判断原本是否已经连接,尽量降低合成器刷新
        if not tool_node_val_socket.is_linked or tool_node_val_socket.links[0].from_socket != view_aov_socket:
            tree.links.new(view_aov_socket, tool_node.inputs[0])
        if not tool_node_uv_socket.is_linked or tool_node_uv_socket.links[0].from_socket != view_screenuv_socket:
            tree.links.new(view_screenuv_socket, tool_node.inputs[1])
        if not tool_node_output_socket.is_linked or tool_node_output_socket.links[0].to_node.inputs[0] != view_node.inputs[0]:
            for link in list(tool_node_output_socket.links):
                tree.links.remove(link)
            tree.links.new(tool_node.outputs[0], view_node.inputs[0])
        return

    def view_settings(self, context):
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.shading.type = "RENDERED"
                        space.shading.use_compositor = "ALWAYS"


def get_max_3d_region(context):
    """获取当前屏幕上面积最大的 3D 视图的绘制区域 (WINDOW)"""
    target_area = None
    max_size = 0

    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            size = area.width * area.height
            if size > max_size:
                max_size = size
                target_area = area

    if target_area:
        # 遍历该 Area 的所有子 Region，找到真正用于显示 3D 画面的 WINDOW 区域
        for region in target_area.regions:
            if region.type == "WINDOW":
                return region
    return None


class NODE_OT_mouse_pos_tracker(bpy.types.Operator):
    """实时追踪鼠标位置并传给合成器节点"""

    bl_idname = "node.mouse_pos_tracker"
    bl_label = "Track Mouse Position"

    _running = False

    def modal(self, context, event):
        props = context.scene.mat_debug_tool_properties
        if not NODE_OT_mouse_pos_tracker._running or not props.open_debug:
            self.cancel(context)
            return {"FINISHED"}
        if event.type == "MOUSEMOVE":
            self.update_node_position(context, event)

        return {"PASS_THROUGH"}

    def update_node_position(self, context, event):
        # 1. 获取最大的 3D 视图绘制区域
        target_region = get_max_3d_region(context)
        if not target_region:
            return

        # 2. 将全局鼠标坐标转换为相对于该 3D 视图的局部坐标
        # event.mouse_x/y 是相对于整个 Blender 软件窗口的绝对坐标
        # target_region.x/y 是该 3D 视图在整个软件窗口中的起点坐标
        rel_x = event.mouse_x - target_region.x
        rel_y = event.mouse_y - target_region.y

        # 3. 计算归一化比例 (0.0 到 1.0)
        norm_x = rel_x / target_region.width
        norm_y = rel_y / target_region.height

        # 4. 限制在 0-1 之间（如果鼠标移出了 3D 视图范围，将其锁定在边缘）
        norm_x = max(0.0, min(1.0, norm_x))
        norm_y = max(0.0, min(1.0, norm_y))

        # --- 在这里添加你的写入节点的逻辑 ---
        node = get_compositor_node(context)
        node.inputs[12].default_value = norm_x
        node.inputs[13].default_value = norm_y
        # print(f"3D View Normalized Pos: ({norm_x:.3f}, {norm_y:.3f})")

    def invoke(self, context, event):
        props = context.scene.mat_debug_tool_properties.node_properties
        if NODE_OT_mouse_pos_tracker._running:
            NODE_OT_mouse_pos_tracker._running = False
            props.pointer_mode = False
            if context.area:
                context.area.tag_redraw()
            return {"FINISHED"}

        NODE_OT_mouse_pos_tracker._running = True
        props.pointer_mode = True
        context.window_manager.modal_handler_add(self)

        if context.area:
            context.area.tag_redraw()

        # print("鼠标追踪已启动")
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        NODE_OT_mouse_pos_tracker._running = False
        if context.area:
            context.area.tag_redraw()
        # print("鼠标追踪已关闭")


classes = [
    VIEW3D_OT_TestOperator,
    NODE_OT_connect_to_aov,
    NODE_OT_mouse_pos_tracker,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
