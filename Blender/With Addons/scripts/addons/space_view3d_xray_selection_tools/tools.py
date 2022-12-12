import os

import bpy

from .preferences import get_preferences
from .tools_keymap import add_fallback_keymap
from .tools_keymap import add_fallback_keymap_items
from .tools_keymap import fallback_keymap_dict
from .tools_keymap import get_keymap_of_tool_from_preferences
from .tools_keymap import remove_fallback_keymap_items


icon_dir = os.path.join(os.path.dirname(__file__), "icon")


class ToolSelectBoxXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection with x-ray"
    bl_icon = os.path.join(icon_dir, "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "mesh.select_box_xray"
    bl_keymap = (
        (
            "mesh.select_box_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "mesh.select_box_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "mesh.select_box_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "mesh.select_box_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
            {})
    )

    def draw_settings(context, layout, tool):
        tool_props = tool.operator_properties("mesh.select_box_xray")
        global_props = get_preferences()

        row = layout.row()
        row.use_property_split = False
        row.prop(tool_props, "mode", text="", expand=True, icon_only=True)
        row.prop(global_props, "me_select_through", icon='XRAY', toggle=True)


class ToolSelectBoxXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection with x-ray"
    bl_icon = os.path.join(icon_dir, "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "object.select_box_xray"
    bl_keymap = (
        (
            "object.select_box_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "object.select_box_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "object.select_box_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "object.select_box_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
            {})
    )

    def draw_settings(context, layout, tool):
        tool_props = tool.operator_properties("object.select_box_xray")

        row = layout.row()
        row.use_property_split = False
        row.prop(tool_props, "mode", text="", expand=True, icon_only=True)


class ToolSelectCircleXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection with x-ray"
    bl_icon = os.path.join(icon_dir, "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "mesh.select_lasso_xray"
    bl_keymap = (
        (
            "mesh.select_circle_xray",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
            {"properties": [("mode", 'SUB'), ("wait_for_input", False)]}),
        (
            "mesh.select_circle_xray",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
            {"properties": [("mode", 'ADD'), ("wait_for_input", False)]}),
        (
            "mesh.select_circle_xray",
            {"type": 'LEFTMOUSE', "value": 'PRESS'},
            {"properties": [("wait_for_input", False)]})
    )

    def draw_cursor(context, tool, xy):
        from gpu_extras.presets import draw_circle_2d
        props = tool.operator_properties("mesh.select_circle_xray")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, segments=32)

    def draw_settings(context, layout, tool):
        tool_props = tool.operator_properties("mesh.select_circle_xray")
        global_props = get_preferences()

        row = layout.row()
        row.use_property_split = False
        row.prop(tool_props, "mode", text="", expand=True, icon_only=True)
        row.prop(global_props, "me_select_through", icon='XRAY', toggle=True)

        layout.prop(tool_props, "radius")


class ToolSelectCircleXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection with x-ray"
    bl_icon = os.path.join(icon_dir, "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "object.select_circle_xray"
    bl_keymap = (
        (
            "object.select_circle_xray",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
            {"properties": [("mode", 'SUB'), ("wait_for_input", False)]}),
        (
            "object.select_circle_xray",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
            {"properties": [("mode", 'ADD'), ("wait_for_input", False)]}),
        (
            "object.select_circle_xray",
            {"type": 'LEFTMOUSE', "value": 'PRESS'},
            {"properties": [("wait_for_input", False)]})
    )

    def draw_cursor(context, tool, xy):
        from gpu_extras.presets import draw_circle_2d
        props = tool.operator_properties("object.select_circle_xray")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, segments=32)

    def draw_settings(context, layout, tool):
        tool_props = tool.operator_properties("object.select_circle_xray")

        row = layout.row()
        row.use_property_split = False
        row.prop(tool_props, "mode", text="", expand=True, icon_only=True)

        layout.prop(tool_props, "radius")


class ToolSelectLassoXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection with x-ray"
    bl_icon = os.path.join(icon_dir, "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "mesh.select_lasso_xray"
    bl_keymap = (
        (
            "mesh.select_lasso_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "mesh.select_lasso_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "mesh.select_lasso_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "mesh.select_lasso_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
            {})
    )

    def draw_settings(context, layout, tool):
        tool_props = tool.operator_properties("mesh.select_lasso_xray")
        global_props = get_preferences()

        row = layout.row()
        row.use_property_split = False
        row.prop(tool_props, "mode", text="", expand=True, icon_only=True)
        row.prop(global_props, "me_select_through", icon='XRAY', toggle=True)


class ToolSelectLassoXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection with x-ray"
    bl_icon = os.path.join(icon_dir, "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "object.select_lasso_xray"
    bl_keymap = (
        (
            "object.select_lasso_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "object.select_lasso_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "object.select_lasso_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "object.select_lasso_xray",
            {"type": 'LEFTMOUSE', "value": 'CLICK_DRAG'},
            {})
    )

    def draw_settings(context, layout, tool):
        tool_props = tool.operator_properties("object.select_lasso_xray")

        row = layout.row()
        row.use_property_split = False
        row.prop(tool_props, "mode", text="", expand=True, icon_only=True)


box_tools = (
    ToolSelectBoxXrayMesh,
    ToolSelectBoxXrayObject
)
circle_tools = (
    ToolSelectCircleXrayMesh,
    ToolSelectCircleXrayObject
)
lasso_tools = (
    ToolSelectLassoXrayMesh,
    ToolSelectLassoXrayObject
)


def reset_active_tool() -> None:
    for workspace in bpy.data.workspaces:
        for screen in workspace.screens:
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    override = {"screen": screen, "area": area, "space_data": area.spaces[0]}
                    bpy.ops.wm.tool_set_by_id(override, name="builtin.select_box")

    from bl_ui.space_toolsystem_common import ToolSelectPanelHelper

    cls = ToolSelectPanelHelper._tool_class_from_space_type('VIEW_3D')
    cls._tool_group_active = {"bultin.select": 1}


def register() -> None:
    ToolSelectBoxXrayMesh.bl_keymap = get_keymap_of_tool_from_preferences("mesh.select_box_xray")
    ToolSelectBoxXrayObject.bl_keymap = get_keymap_of_tool_from_preferences("object.select_box_xray")

    ToolSelectCircleXrayMesh.bl_keymap = get_keymap_of_tool_from_preferences("mesh.select_circle_xray")
    ToolSelectCircleXrayObject.bl_keymap = get_keymap_of_tool_from_preferences("object.select_circle_xray")

    ToolSelectLassoXrayMesh.bl_keymap = get_keymap_of_tool_from_preferences("mesh.select_lasso_xray")
    ToolSelectLassoXrayObject.bl_keymap = get_keymap_of_tool_from_preferences("object.select_lasso_xray")

    for tool in box_tools:
        bpy.utils.register_tool(tool, after={"builtin.select_box"}, separator=False, group=False)
    for tool in circle_tools:
        bpy.utils.register_tool(tool, after={"builtin.select_circle"}, separator=False, group=False)
    for tool in lasso_tools:
        bpy.utils.register_tool(tool, after={"builtin.select_lasso"}, separator=False, group=False)

    add_fallback_keymap(fallback_keymap_dict)
    add_fallback_keymap_items(fallback_keymap_dict)


def unregister() -> None:
    import itertools

    remove_fallback_keymap_items(fallback_keymap_dict)

    for tool in itertools.chain(box_tools, circle_tools, lasso_tools):
        bpy.utils.unregister_tool(tool)
