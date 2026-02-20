import bpy
from bpy.props import *
from .i18n import translations


class MatDebugToolProperties(bpy.types.PropertyGroup):
    open_debug: BoolProperty(name=translations("Open Debug"), default=False)
    viewport_composite_state: StringProperty(name="Viewport Composite State", default="DISABLED")


def register():
    bpy.utils.register_class(MatDebugToolProperties)
    bpy.types.Scene.mat_debug_tool_properties = PointerProperty(type=MatDebugToolProperties)


def unregister():
    bpy.utils.unregister_class(MatDebugToolProperties)
    del bpy.types.Scene.mat_debug_tool_properties
