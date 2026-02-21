import bpy
from .utils import *
from .i18n import translations
from . import bl_info
from .operators import NODE_OT_mouse_pos_tracker
import rna_keymap_ui


class MatDebugToolPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text=translations("Material Debugger Tool"), icon="SHADERFX")
        row.label(text=f"Version: {bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}")
        row.label(text="BY : LEDingQ", icon="FUND")
        layout.label(text="快捷键设置 (Keymap Settings):", icon="KEYINGSET")
        wm = context.window_manager
        kc = wm.keyconfigs.user
        if kc:
            km = kc.keymaps.get("Node Editor")
            if km:
                for kmi in km.keymap_items:
                    if kmi.idname == "node.connect_to_aov":
                        layout.context_pointer_set("keymap", km)
                        rna_keymap_ui.draw_kmi([], kc, km, kmi, layout, 0)
                        break


class NODE_PT_material_debugger_tool(bpy.types.Panel):
    """Material Debugger Tool 面板"""

    bl_label = "Material Debugger Tool"
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
        if context.scene.render.engine != "BLENDER_EEVEE_NEXT":
            col = layout.column(align=True)
            col.alert = True
            col.label(text="Only supported in EEVEE NEXT", icon="ERROR")
            return

        addon_props = context.scene.mat_debug_tool_properties
        col = layout.column(align=True)
        # col.operator("view3d.test_operator", text="Test Operator")
        box = col.box()
        row = box.row(align=True)
        row.label(text=translations("Shift + Alt + LMB on node to preview"), icon="INFO")
        row.operator("wm.open_github_page", text="", icon="URL")
        # col1 = col.row(align=True)
        # col1.alert = True
        # active_node = context.active_node
        # if not active_node.select:
        #     col1.label(text=translations("Please select a node"), icon="ERROR")
        if not addon_props.open_debug:
            return
        col.prop(addon_props, "open_debug", text=translations("Open Debug"), icon="SHADERFX")
        target_node = get_compositor_node(context)

        if not target_node:
            return
        # 遍历所有输入端口
        prop = context.scene.mat_debug_tool_properties.node_properties
        col.operator("node.mouse_pos_tracker", text=translations("Pointer Mode"), depress=NODE_OT_mouse_pos_tracker._running, icon="CURSOR")
        if not prop.pointer_mode:
            box = col.box()
            col = box.column(align=True)
            # col.label(text="Show Model:")
            col.prop(prop, "show_model", text="")
            col.prop(prop, "show_frame", text=translations("Show Frame"), icon="META_PLANE")
            col.prop(prop, "show_base_color", text=translations("Show Base Color"), icon="NODE_MATERIAL")
            self.draw_socket_prop(col, target_node, 2, text=translations("Scale"))  # 缩放
            self.draw_socket_prop(col, target_node, 3, text=translations("Scale X"))  # 缩放x
            self.draw_socket_prop(col, target_node, 4, text=translations("Scale Y"))  # 缩放y
            self.draw_socket_prop(col, target_node, 5, text=translations("Number X Scale"))  # 数字x缩放
            self.draw_socket_prop(col, target_node, 6, text=translations("Number Y Scale"))  # 数字y缩放
        else:
            box = col.box()
            col = box.column(align=True)
            # col.label(text="Show Model:")
            col.prop(prop, "show_model", text="")
            self.draw_socket_prop(col, target_node, 14, text=translations("Pointer Size"))  # 指针大小
            self.draw_socket_prop(col, target_node, 15, text=translations("Internal Scaling"))  # 指针中间缩放
            self.draw_socket_prop(col, target_node, 16, text=translations("Text Scale"))  # 指针文字缩放
            self.draw_socket_prop(col, target_node, 5, text=translations("Number X Scale"))  # 数字x缩放
            self.draw_socket_prop(col, target_node, 6, text=translations("Number Y Scale"))  # 数字y缩放
            self.draw_socket_prop(col, target_node, 17, text=translations("Number X Offset"))  # 指针文字X
            self.draw_socket_prop(col, target_node, 18, text=translations("Number Y Offset"))  # 指针文字Y

    def draw_socket_prop(self, layout, node, index, text=None, icon="NONE", as_bool=False):
        if index < 0 or index >= len(node.inputs):
            layout.label(text=f"index out of range: {index}", icon="ERROR")
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


def draw_shader_header_buttons(self, context):
    if context.space_data.tree_type != "ShaderNodeTree":
        return

    layout = self.layout

    # layout.separator()

    row = layout.row(align=True)
    addon_props = context.scene.mat_debug_tool_properties
    row.prop(addon_props, "open_debug", text="", icon="SHADERFX")
    row.operator("node.mouse_pos_tracker", text="", depress=NODE_OT_mouse_pos_tracker._running, icon="CURSOR")


cls = [
    MatDebugToolPreferences,
    NODE_PT_material_debugger_tool,
]


def register():
    for c in cls:
        bpy.utils.register_class(c)
    bpy.types.NODE_HT_header.append(draw_shader_header_buttons)


def unregister():
    for c in reversed(cls):
        bpy.utils.unregister_class(c)
    bpy.types.NODE_HT_header.remove(draw_shader_header_buttons)
