import bpy

translations_dict = {
    "zh_CN": {
        # UI & Properties
        ("*", "Material Debugger Tool"): "材质调试工具",
        ("*", "Open Debug"): "关闭调试",
        ("*", "Viewport Composite State"): "视图合成状态",
        ("*", "Compositor Use Nodes"): "合成器使用节点",
        ("*", "View Node Link Socket"): "预览节点链接端口",
        ("*", "Show Frame"): "显示边框",
        ("*", "Show Base Color"): "显示底色",
        ("*", "Show Model"): "显示模式",
        ("*", "Pointer Mode"): "指针模式",
        ("*", "Pointer Position"): "指针位置",
        ("*", "Keymap Settings:"): "快捷键设置:",
        ("*", "Only supported in EEVEE NEXT"): "仅支持在EEVEE NEXT中使用",
        ("*", "Index Error:"): "索引错误:",
        # Operators & Tooltips
        ("*", "Connect to AOV"): "连接到AOV",
        ("*", "Track Mouse Position"): "追踪鼠标位置",
        ("*", "Shift+Alt+Click: Cycle connect node output to AOV"): "Shift+Alt+左键: 循环连接节点输出到 AOV",
        # Warnings & Reports
        ("*", "Node has no output sockets"): "节点没有输出端口",
        ("*", "Shader type nodes are not supported"): "不支持Shader类型节点",
        ("*", "Render layer node AOV pass not found: "): "渲染层节点未找到 AOV 通道: ",
        ("*", "Asset error"): "资产错误",
        # Node Parameters (节点参数)
        ("*", "Scale"): "缩放",
        ("*", "Scale X"): "缩放X",
        ("*", "Scale Y"): "缩放Y",
        ("*", "Number X Scale"): "数字X缩放",
        ("*", "Number Y Scale"): "数字Y缩放",
        ("*", "Pointer Size"): "指针大小",
        ("*", "Internal Scaling"): "内部缩放",
        ("*", "Text Scale"): "文字缩放",
        ("*", "Number X Offset"): "数字X偏移",
        ("*", "Number Y Offset"): "数字Y偏移",
        ("*", "Shift + Alt + LMB on node to preview"): "Shift + Alt + 左键点击节点预览",
        ("*", "Please select a node"): "请选择一个节点",
    },
}


def translations(text):
    return bpy.app.translations.pgettext(text)
