# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Material Debugger Tool",
    "author": "LEDingQ",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}


import bpy
from . import operators
from . import ui
from .i18n import translations_dict
from . import property
from .utils import import_node_group, _draw_handler
from bpy.app.handlers import persistent
from .operators import NODE_OT_connect_to_aov


@persistent
def load_post_handler(dummy):
    """当新建文件或打开文件后运行"""
    bpy.app.timers.register(import_node_group, first_interval=0.1)


addon_keymaps = []


def register():
    print("Registering Material Debugger Tool")
    try:
        bpy.app.translations.register(__name__, translations_dict)
    except:
        pass
    property.register()
    operators.register()
    ui.register()
    # 添加快捷键配置
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Node Editor", space_type="NODE_EDITOR")

        # 配置: Shift + Alt + 左键
        kmi = km.keymap_items.new(NODE_OT_connect_to_aov.bl_idname, type="LEFTMOUSE", value="PRESS", shift=True, alt=True)
        addon_keymaps.append((km, kmi))
    bpy.app.timers.register(import_node_group, first_interval=0.1)
    # 注册文件加载钩子
    if load_post_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_post_handler)


def unregister():
    try:
        bpy.app.translations.unregister(__name__)
    except:
        pass
    property.unregister()
    operators.unregister()
    ui.unregister()
    # 移除快捷键
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    global _draw_handler
    if _draw_handler is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handler, "WINDOW")
        _draw_handler = None
    if load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_handler)
