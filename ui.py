import bpy
from .utils import *
from .i18n import translations
from . import bl_info
from .operators import NODE_OT_mouse_pos_tracker

# --- UI Panel ---


class NODE_PT_material_debugger_tool(bpy.types.Panel):
    """Material Debugger Tool 面板"""

    bl_label = "Material Debugger"
    bl_idname = "NODE_PT_material_debugger_tool"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Mat Debug Tool"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == "NODE_EDITOR" and space.shader_type == "OBJECT"

    def draw(self, context):
        layout = self.layout

        addon_props = context.scene.mat_debug_tool_properties
        col = layout.column(align=True)
        col.operator("view3d.test_operator", text="Test Operator")
        col.prop(addon_props, "open_debug", text="Open Debug", icon="RESTRICT_VIEW_OFF" if addon_props.open_debug else "RESTRICT_VIEW_ON")

        target_node = get_compositor_node(context)

        if not target_node:
            return
        # 遍历所有输入端口
        prop = context.scene.mat_debug_tool_properties.node_properties
        col.operator("node.mouse_pos_tracker", text="pointer_mode", depress=NODE_OT_mouse_pos_tracker._running, icon="CURSOR" if NODE_OT_mouse_pos_tracker._running else "MOUSE_LMB")
        if not prop.pointer_mode:
            box = col.box()
            col = box.column(align=True)
            col.label(text="Show Model:")
            col.prop(prop, "show_model", text="")
            col.prop(prop, "show_frame", text="Show Frame", icon="RESTRICT_VIEW_OFF" if prop.show_frame else "RESTRICT_VIEW_ON")
            col.prop(prop, "show_base_color", text="Show Base Color", icon="RESTRICT_VIEW_OFF" if prop.show_base_color else "RESTRICT_VIEW_ON")
            self.draw_socket_prop(col, target_node, 2)  # 缩放
            self.draw_socket_prop(col, target_node, 3)  # 缩放x
            self.draw_socket_prop(col, target_node, 4)  # 缩放y
            self.draw_socket_prop(col, target_node, 5)  # 数字x缩放
            self.draw_socket_prop(col, target_node, 6)  # 数字y缩放
        else:
            box = col.box()
            col = box.column(align=True)
            col.label(text="Show Model:")
            col.prop(prop, "show_model", text="")
            self.draw_socket_prop(col, target_node, 5)  # 数字x缩放
            self.draw_socket_prop(col, target_node, 6)  # 数字y缩放
            self.draw_socket_prop(col, target_node, 14)  # 指针大小
            self.draw_socket_prop(col, target_node, 15)  # 指针中间缩放
            self.draw_socket_prop(col, target_node, 16)  # 指针文字缩放
            self.draw_socket_prop(col, target_node, 17)  # 指针文字X
            self.draw_socket_prop(col, target_node, 18)  # 指针文字Y

    def draw_socket_prop(self, layout, node, index, text=None, icon="NONE", as_bool=False):
        if index < 0 or index >= len(node.inputs):
            layout.label(text=f"索引错误: {index}", icon="ERROR")
            return

        socket = node.inputs[index]

        if not socket.enabled:
            return

        if socket.is_linked:
            layout.label(text=text if text else socket.name, icon="LINKED")
            return

        display_text = text if text is not None else socket.name
        row = layout.row(align=True)
        if icon != "NONE":
            row.label(icon=icon)
        row.prop(socket, "default_value", text=display_text)


cls = [
    NODE_PT_material_debugger_tool,
]


def register():
    for c in cls:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(cls):
        bpy.utils.unregister_class(c)
