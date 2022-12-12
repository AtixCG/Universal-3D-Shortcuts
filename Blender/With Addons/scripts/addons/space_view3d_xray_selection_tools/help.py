import bpy
import textwrap


def draw_me_select_all_edges_info_popup(self, context):
    layout = self.layout
    text = \
        "By default, in selection through mode tools select only edges, both vertices of which are inside a " \
        "selection region. Enable this option if you want to select all edges, that overlap a selection region " \
        "(this is slower than the default selection on meshes with a lot of geometry)."
    lines = textwrap.wrap(text, 120)
    col = layout.column(align=True)
    for n in lines:
        col.label(text=n)


def draw_me_select_all_faces_info_popup(self, context):
    layout = self.layout
    text = \
        "By default, in selection through mode tools select only faces whose center dots are inside a selection " \
        "region. Enable this option if you want to select all faces, that overlap a selection region " \
        "(this is slower than the default selection on meshes with a lot of geometry)."
    lines = textwrap.wrap(text, 120)
    col = layout.column(align=True)
    for n in lines:
        col.label(text=n)


def draw_me_drag_direction_info_popup(self, context):
    layout = self.layout
    text = \
        "For example you can set up selection through for right-to-left drag direction and disable it for " \
        "left-to-right drag direction."
    lines = textwrap.wrap(text, 120)
    col = layout.column(align=True)
    for n in lines:
        col.label(text=n)


def draw_me_hide_modifiers_info_popup(self, context):
    layout = self.layout
    text = \
        "Hide mirror modifier or solidify modifier during selection through and re-enable them after finishing " \
        "selection. This can be useful on dense mesh, making it easier to see real geometry in x-ray shading."
    lines = textwrap.wrap(text, 120)
    col = layout.column(align=True)
    for n in lines:
        col.label(text=n)


def draw_wait_for_input_cursor_info_popup(self, context):
    layout = self.layout
    text = \
        "Show crosshair of box tool or lasso icon of lasso tool next to cursor when tool is started with " \
        "a keyboard shortcut."
    lines = textwrap.wrap(text, 120)
    col = layout.column(align=True)
    for n in lines:
        col.label(text=n)


def draw_ob_select_behavior_info_popup(self, context):
    layout = self.layout
    texts = \
        ("• In Origin mode you select only objects with origins within the selection region.",
         "• In Contain mode you select only objects entirely enclosed in the selection region.",
         "• In Overlap mode you select all objects within the selection region, plus any objects "
         "crossing boundaries of the selection region.",
         "• In Direction mode you automatically switch between Overlap and Contain selection "
         "based on cursor movement direction.",
         "    ○ Drag from left to right to select all objects crossing or within the selection region (Overlap).",
         "    ○ Drag from right to left to select all objects entirely enclosed in the selection region (Contain).",
         "Note that every mode is slower than the default one on objects with a lot of geometry."
         )
    for text in texts:
        lines = textwrap.wrap(text, 120)
        col = layout.column(align=True)
        for n in lines:
            col.label(text=n)


def draw_tool_keymaps_info_popup(self, context):
    layout = self.layout
    texts = \
        ("Change, disable or enable shortcuts here. To edit shortcut properties independently of global addon "
         "settings, expand key item and check Override Global Properties.",
         "Deactivating header here will remove shortcuts below it from blender keyconfig.",
         )
    for text in texts:
        lines = textwrap.wrap(text, 120)
        col = layout.column(align=True)
        for n in lines:
            col.label(text=n)


def draw_tool_selection_mode_keymaps_info_popup(self, context):
    layout = self.layout
    texts = \
        ("Keys that change selection mode when held down before using a box, lasso or circle xray tool in the "
         "toolbar.",
         "Deactivating selection mode here will remove its shortcut from xray selection tool.",
         "Active Mode corresponds to active selection mode button in blender header or Active Tool tab in "
         "blender properties area."
         )
    for text in texts:
        lines = textwrap.wrap(text, 120)
        col = layout.column(align=True)
        for n in lines:
            col.label(text=n)


class XRAYSEL_OT_show_info_popup(bpy.types.Operator):
    """Show description"""
    bl_idname = "xraysel.show_info_popup"
    bl_label = "Select X-Ray"

    button: bpy.props.StringProperty()

    def invoke(self, context, event):
        if self.button == "me_select_all_edges":
            context.window_manager.popover(draw_me_select_all_edges_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
        elif self.button == "me_select_all_faces":
            context.window_manager.popover(draw_me_select_all_faces_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
        elif self.button == "me_drag_direction":
            context.window_manager.popover(draw_me_drag_direction_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
        elif self.button == "me_hide_modifiers":
            context.window_manager.popover(draw_me_hide_modifiers_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
        elif self.button == "ob_selection_behavior":
            context.window_manager.popover(draw_ob_select_behavior_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
        elif self.button == "wait_for_input_cursor":
            context.window_manager.popover(draw_wait_for_input_cursor_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
        elif self.button == "tool_keymaps":
            context.window_manager.popover(draw_tool_keymaps_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
        elif self.button == "tool_selection_mode_keymaps":
            context.window_manager.popover(draw_tool_selection_mode_keymaps_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
        return {'FINISHED'}


classes = (
    XRAYSEL_OT_show_info_popup,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
