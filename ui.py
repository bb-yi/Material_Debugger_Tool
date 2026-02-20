import bpy
from .utils import *
from .i18n import translations
from . import bl_info

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

        layout.operator("view3d.test_operator", text="Test Operator")

        layout.prop(addon_props, "open_debug", text="Open Debug", icon="RESTRICT_VIEW_OFF" if addon_props.open_debug else "RESTRICT_VIEW_ON")


cls = [
    NODE_PT_material_debugger_tool,
]


def register():
    for c in cls:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(cls):
        bpy.utils.unregister_class(c)
