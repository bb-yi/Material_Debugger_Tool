import bpy
from bpy.props import *
from .i18n import translations
from .utils import *


class MatDebugToolNodeProperties(bpy.types.PropertyGroup):
    show_frame: BoolProperty(name="Show Frame", default=False, update=show_frame_update)
    show_base_color: BoolProperty(name="Show Base Color", default=False, update=show_base_color_update)
    show_model: EnumProperty(name="Show Model", items=[("AUTO", "Auto", ""), ("GRAY", "Gray", ""), ("RGB", "RGB", ""), ("HSV", "HSV", "")], default="AUTO", update=show_model_update)
    pointer_mode: BoolProperty(name="Pointer Mode", default=False, update=pointer_mode_update)
    pointer_pos: FloatVectorProperty(name="Pointer Position", size=2, default=(0.5, 0.5))


class MatDebugToolProperties(bpy.types.PropertyGroup):
    open_debug: BoolProperty(name=translations("Open Debug"), default=False, update=open_debug_update)
    use_compositor: StringProperty(name="Viewport Composite State", default="DISABLED")
    compositor_use_nodes: BoolProperty(name="Compositor Use Nodes", default=False)
    view_node_link_socket: StringProperty(name="View Node Link Socket", default="")

    node_properties: PointerProperty(type=MatDebugToolNodeProperties)


def register():
    bpy.utils.register_class(MatDebugToolNodeProperties)
    bpy.utils.register_class(MatDebugToolProperties)
    bpy.types.Scene.mat_debug_tool_properties = PointerProperty(type=MatDebugToolProperties)


def unregister():
    bpy.utils.unregister_class(MatDebugToolNodeProperties)
    bpy.utils.unregister_class(MatDebugToolProperties)
    del bpy.types.Scene.mat_debug_tool_properties
