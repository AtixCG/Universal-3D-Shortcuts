import bpy
import textwrap
import rna_keymap_ui
from .ot_keymap import me_keyboard_keymap, me_mouse_keymap, ob_keyboard_keymap, ob_mouse_keymap, \
    toggles_keymap
from .ot_keymap import toggle_me_keyboard_keymap, toggle_me_mouse_keymap, toggle_ob_keyboard_keymap, \
    toggle_ob_mouse_keymap, toggle_toggles_keymap
from .tools_keymap import populate_preferences_keymaps_of_tools, update_keymaps_of_tools
from .preferences import get_preferences


class XRAYSELToolKmiPG(bpy.types.PropertyGroup):
    # name = StringProperty() -> Instantiated by default
    description: bpy.props.StringProperty(name="Description")
    icon: bpy.props.StringProperty(name="Icon")
    active: bpy.props.BoolProperty(
        name="Active",
        description="Enable or disable key modifier",
        update=update_keymaps_of_tools,
        default=True)
    shift: bpy.props.BoolProperty(
        name="Shift",
        description="Shift key pressed",
        update=update_keymaps_of_tools,
        default=False
    )
    ctrl: bpy.props.BoolProperty(
        name="Ctrl",
        description="Ctrl key pressed",
        update=update_keymaps_of_tools,
        default=False
    )
    alt: bpy.props.BoolProperty(
        name="Alt",
        description="Alt key pressed",
        update=update_keymaps_of_tools,
        default=False
    )


class XRAYSELToolKeymapPG(bpy.types.PropertyGroup):
    # name = StringProperty() -> Instantiated by default
    kmis: bpy.props.CollectionProperty(name="KMIS", type=XRAYSELToolKmiPG)


# noinspection PyTypeChecker
class XRAYSELToolMeDirectionProps(bpy.types.PropertyGroup):
    # name = StringProperty() -> Instantiated by default
    select_through: bpy.props.BoolProperty(
        name="Select Through",
        description="Select verts, faces and edges laying underneath",
        default=True
    )
    default_color: bpy.props.FloatVectorProperty(
        name="Default Color",
        description="Tool color when selection through is disabled",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0)
    )
    select_through_color: bpy.props.FloatVectorProperty(
        name="Select Through Color",
        description="Tool color when selection through is disabled",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0)
    )
    show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable x-ray shading during selection",
        default=True
    )
    select_all_edges: bpy.props.BoolProperty(
        name="Select All Edges",
        description="Additionally select edges that are partially inside the selection borders, "
                    "not just the ones completely inside the selection borders. Works only "
                    "in select through mode",
        default=False
    )
    select_all_faces: bpy.props.BoolProperty(
        name="Select All Faces",
        description="Additionally select faces that are partially inside the selection borders, "
                    "not just the ones with centers inside the selection borders. Works only "
                    "in select through mode",
        default=False
    )


# noinspection PyTypeChecker
class XRAYSELPreferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    tabs: bpy.props.EnumProperty(
        name="Tabs",
        items=[('MESH_TOOLS', "Mesh Tools", ""),
               ('OBJECT_TOOLS', "Object Tools", ""),
               ('KEYMAP', "Advanced Keymap", "")
               ],
        default='MESH_TOOLS',
        options={'SKIP_SAVE'}
    )
    me_directional_box: bpy.props.BoolProperty(
        name="Directional Box Behavior",
        description="Configure behavior separately for dragging directions",
        default=False
    )
    me_directional_lasso: bpy.props.BoolProperty(
        name="Directional Lasso Behavior",
        description="Configure behavior separately for dragging directions",
        default=False
    )
    me_select_through: bpy.props.BoolProperty(
        name="Select Through",
        description="Select verts, faces and edges laying underneath",
        default=True
    )
    me_select_through_toggle_key: bpy.props.EnumProperty(
        name="Selection Through Toggle Key",
        description="Toggle selection through by holding this key",
        items=[('CTRL', "CTRL", ""),
               ('ALT', "ALT", ""),
               ('SHIFT', "SHIFT", ""),
               ('DISABLED', "DISABLED", "")
               ],
        default='DISABLED'
    )
    me_select_through_toggle_type: bpy.props.EnumProperty(
        name="Toggle Selection Through by Press or Hold",
        description="Toggle selection through by holding or by pressing key",
        items=[('HOLD', "Holding", ""),
               ('PRESS', "Pressing", "")
               ],
        default='HOLD'
    )
    me_default_color: bpy.props.FloatVectorProperty(
        name="Default Color",
        description="Tool color when selection through is disabled",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0)
    )
    me_select_through_color: bpy.props.FloatVectorProperty(
        name="Select Through Color",
        description="Tool color when selection through is disabled",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0)
    )
    me_show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable x-ray shading during selection",
        default=True
    )
    me_select_all_edges: bpy.props.BoolProperty(
        name="Select All Edges",
        description="Additionally select edges that are partially inside the selection borders, "
                    "not just the ones completely inside the selection borders. Works only "
                    "in select through mode",
        default=False
    )
    me_select_all_faces: bpy.props.BoolProperty(
        name="Select All Faces",
        description="Additionally select faces that are partially inside the selection borders, "
                    "not just the ones with centers inside the selection borders. Works only "
                    "in select through mode",
        default=False
    )
    me_hide_mirror: bpy.props.BoolProperty(
        name="Hide Mirror",
        description="Hide mirror modifiers during selection",
        default=True
    )
    me_hide_solidify: bpy.props.BoolProperty(
        name="Hide Solidify",
        description="Hide solidify modifiers during selection",
        default=True
    )
    me_show_crosshair: bpy.props.BoolProperty(
        name="Show Crosshair",
        description="Show crosshair when wait_for_input is enabled",
        default=True
    )
    me_show_lasso_icon: bpy.props.BoolProperty(
        name="Show Lasso Cursor",
        description="Show lasso cursor icon when wait_for_input is enabled",
        default=True
    )

    ob_show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable x-ray shading during selection",
        default=True
    )
    ob_xray_toggle_key: bpy.props.EnumProperty(
        name="X-Ray Toggle Key",
        description="Toggle x-ray by holding this key",
        items=[('CTRL', "CTRL", ""),
               ('ALT', "ALT", ""),
               ('SHIFT', "SHIFT", ""),
               ('DISABLED', "DISABLED", "")
               ],
        default='DISABLED'
    )
    ob_xray_toggle_type: bpy.props.EnumProperty(
        name="Toggle X-Ray by Press or Hold",
        description="Toggle x-ray by holding or by pressing key",
        items=[('HOLD', "Holding", ""),
               ('PRESS', "Pressing", "")
               ],
        default='HOLD'
    )
    ob_show_crosshair: bpy.props.BoolProperty(
        name="Show Crosshair",
        description="Show crosshair when wait_for_input is enabled",
        default=True
    )
    ob_show_lasso_icon: bpy.props.BoolProperty(
        name="Show Lasso Cursor",
        description="Show lasso cursor icon when wait_for_input is enabled",
        default=True
    )
    ob_box_select_behavior: bpy.props.EnumProperty(
        name="Box Select Behavior",
        description="Selection behavior",
        items=[('ORIGIN', "Origin", "Select objects by origins", 'DOT', 1),
               ('CONTAIN', "Contain", "Select only the objects fully contained in box", 'STICKY_UVS_LOC', 2),
               ('OVERLAP', "Overlap (Default)", "Select objects overlapping box", 'SELECT_SUBTRACT', 3),
               ('DIRECTIONAL', "Directional", "Dragging left to right select contained, right to left select "
                                              "overlapped", 'UV_SYNC_SELECT', 4)
               ],
        default='OVERLAP'
    )
    ob_circle_select_behavior: bpy.props.EnumProperty(
        name="Circle Select Behavior",
        description="Selection behavior",
        items=[('ORIGIN', "Origin (Default)", "Select objects by origins", 'DOT', 1),
               ('CONTAIN', "Contain", "Select only the objects fully contained in circle", 'STICKY_UVS_LOC', 2),
               ('OVERLAP', "Overlap", "Select objects overlapping circle", 'SELECT_SUBTRACT', 3)
               ],
        default='ORIGIN'
    )
    ob_lasso_select_behavior: bpy.props.EnumProperty(
        name="Lasso Select Behavior",
        description="Selection behavior",
        items=[('ORIGIN', "Origin (Default)", "Select objects by origins", 'DOT', 1),
               ('CONTAIN', "Contain", "Select only the objects fully contained in lasso", 'STICKY_UVS_LOC', 2),
               ('OVERLAP', "Overlap", "Select objects overlapping lasso", 'SELECT_SUBTRACT', 3),
               ('DIRECTIONAL', "Directional", "Dragging left to right select contained, right to left select "
                                              "overlapped", 'UV_SYNC_SELECT', 4)
               ],
        default='ORIGIN'
    )

    enable_me_keyboard_keymap: bpy.props.BoolProperty(
        name="Mesh Mode Keyboard Shortcuts",
        description="Activate to add shortcuts to blender keymap, deactivate to remove "
                    "shortcuts from blender keymap",
        update=toggle_me_keyboard_keymap,
        default=True
    )
    enable_me_mouse_keymap: bpy.props.BoolProperty(
        name="Mesh Mode Mouse Shortcuts",
        description="Activate to add shortcuts to blender keymap, deactivate to remove "
                    "shortcuts from blender keymap",
        update=toggle_me_mouse_keymap,
        default=False
    )
    enable_ob_keyboard_keymap: bpy.props.BoolProperty(
        name="Object Mode Keyboard Shortcuts",
        description="Activate to add shortcuts to blender keymap, deactivate to remove "
                    "shortcuts from blender keymap",
        update=toggle_ob_keyboard_keymap,
        default=True
    )
    enable_ob_mouse_keymap: bpy.props.BoolProperty(
        name="Object Mode Mouse Shortcuts",
        description="Activate to add shortcuts to blender keymap, deactivate to remove "
                    "shortcuts from blender keymap",
        update=toggle_ob_mouse_keymap,
        default=False
    )
    enable_toggles_keymap: bpy.props.BoolProperty(
        name="Preferences Toggles Shortcuts",
        description="Activate to add shortcuts to blender keymap, deactivate to remove "
                    "shortcuts from blender keymap",
        update=toggle_toggles_keymap,
        default=False
    )

    keymaps_of_tools: bpy.props.CollectionProperty(type=XRAYSELToolKeymapPG, name="Keymaps of Tools")
    me_direction_properties: bpy.props.CollectionProperty(type=XRAYSELToolMeDirectionProps, name="Mesh Direction Props")

    select_mouse: bpy.props.EnumProperty(
        description="Last value of property, since keyconfig.preferences isn't available at blender startup",
        items=[
            ('LEFT', "", ""),
            ('RIGHT', "", ""),
        ],
        default='LEFT',
    )

    rmb_action: bpy.props.EnumProperty(
        description="Last value of property, since keyconfig.preferences isn't available at blender startup",
        items=[
            ('TWEAK', "", ""),
            ('FALLBACK_TOOL', "", ""),
        ],
        default='TWEAK',
    )

    tool_keymap_tabs: bpy.props.EnumProperty(
        name="Tool Selection Modifier Keys",
        items=[('BOX', "Box Tool", ""),
               ('CIRCLE', "Circle Tool", ""),
               ('LASSO', "Lasso Tool", "")
               ],
        default='BOX',
        options={'SKIP_SAVE'}
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(self, "tabs", expand=True)
        box = col.box()

        if self.tabs == 'MESH_TOOLS':
            self.draw_mesh_tools_preferences(box)
        elif self.tabs == 'OBJECT_TOOLS':
            self.draw_object_tools_preferences(box)
        elif self.tabs == 'KEYMAP':
            self.draw_adv_keymap(box)

    @staticmethod
    def draw_flow_vertical_separator(flow):
        row = flow.row()
        row.scale_y = .7
        row.label(text="")
        row = flow.row()
        row.scale_y = .7
        row.label(text="")

    def draw_mesh_tools_preferences(self, box):
        if self.enable_me_keyboard_keymap:
            box.label(text="Change shortcuts here or disable them by unchecking")
            col = box.column()
            self.draw_keymap_items(col, "Mesh", me_keyboard_keymap, {'KEYBOARD'}, False)
            box.separator(factor=1.7)

        if self.me_directional_box | self.me_directional_lasso:
            flow = box.grid_flow(columns=2, row_major=True, align=True)

            flow.label(text="Toggle select through during selection with a key")
            split = flow.split(align=True)
            sub = split.row(align=True)
            sub.active = self.me_select_through_toggle_key != 'DISABLED'
            sub.prop(self, "me_select_through_toggle_type", text="")
            split.prop(self, "me_select_through_toggle_key", text="")

            self.draw_flow_vertical_separator(flow)

            dir_tools = []
            def_tools = ["Circle"]
            if self.me_directional_box:
                dir_tools.append("Box")
            else:
                def_tools.append("Box")
            if self.me_directional_lasso:
                dir_tools.append("Lasso")
            else:
                def_tools.append("Lasso")

            rtl_props = self.me_direction_properties["RIGHT_TO_LEFT"]
            ltr_props = self.me_direction_properties["LEFT_TO_RIGHT"]

            flow.label(text="Tool")
            split = flow.split(align=True)
            row = split.row()
            row.label(text="", icon='BLANK1')
            sub = row.row()
            sub.alignment = 'CENTER'
            sub.label(text=" and ".join(dir_tools))
            row = split.row()
            row.label(text="", icon='BLANK1')
            sub = row.row()
            sub.alignment = 'CENTER'
            sub.label(text=" and ".join(dir_tools))
            row = split.row()
            row.label(text="", icon='BLANK1')
            sub = row.row()
            sub.alignment = 'CENTER'
            sub.label(text=" and ".join(def_tools))
            # split.label(text=" and ".join(dir_tools), icon='BLANK1')
            # split.label(text=" and ".join(dir_tools), icon='BLANK1')
            # split.label(text=" and ".join(def_tools), icon='BLANK1')
            # split.prop(self, "blank", text=" and ".join(dir_tools), icon='BLANK1', emboss=False)
            # split.prop(self, "blank", text=" and ".join(dir_tools), icon='BLANK1', emboss=False)
            # split.prop(self, "blank", text=" and ".join(def_tools), icon='BLANK1', emboss=False)

            flow.label(text="Direction")
            split = flow.split(align=True)
            row = split.row()
            row.label(text="", icon='BACK')
            sub = row.row()
            sub.alignment = 'CENTER'
            sub.label(text="Right to Left")
            row = split.row()
            row.label(text="", icon='FORWARD')
            sub = row.row()
            sub.alignment = 'CENTER'
            sub.label(text="Left to Right")
            row = split.row()
            row.label(text="", icon='ARROW_LEFTRIGHT')
            sub = row.row()
            sub.alignment = 'CENTER'
            sub.label(text="Any")
            # split.label(text="Right to Left", icon='BACK')
            # split.label(text="Left to Right", icon='FORWARD')
            # split.label(text="Any", icon='ARROW_LEFTRIGHT')
            # split.prop(self, "blank", text="Right to Left", icon='BACK', emboss=False)
            # split.prop(self, "blank", text="Left to Right", icon='FORWARD', emboss=False)
            # split.prop(self, "blank", text="Any", icon='ARROW_LEFTRIGHT', emboss=False)

            flow.label(text="Start selection with enabled selection through")
            split = flow.split(align=True)
            split.prop(rtl_props, "select_through", text="Select Through", icon='MOD_WIREFRAME')
            split.prop(ltr_props, "select_through", text="Select Through", icon='MOD_WIREFRAME')
            split.prop(self, "me_select_through", text="Select Through", icon='MOD_WIREFRAME')

            rtl_st_available = rtl_props.select_through or self.me_select_through_toggle_key != 'DISABLED'
            ltr_st_available = ltr_props.select_through or self.me_select_through_toggle_key != 'DISABLED'
            def_st_available = self.me_select_through or self.me_select_through_toggle_key != 'DISABLED'

            flow.label(text="Selection frame color when selection through is disabled")
            split = flow.split(align=True)
            split.prop(rtl_props, "default_color", text="")
            split.prop(ltr_props, "default_color", text="")
            split.prop(self, "me_default_color", text="")

            flow.label(text="Selection frame color when selection through is enabled")
            split = flow.split(align=True)
            split.prop(rtl_props, "select_through_color", text="")
            split.prop(ltr_props, "select_through_color", text="")
            split.prop(self, "me_select_through_color", text="")

            flow.label(text="Show x-ray shading during selection through")
            split = flow.split(align=True)
            row = split.row(align=True)
            row.active = rtl_st_available
            row.prop(rtl_props, "show_xray", text="Show X-Ray", icon='XRAY')
            row = split.row(align=True)
            row.active = ltr_st_available
            row.prop(ltr_props, "show_xray", text="Show X-Ray", icon='XRAY')
            row = split.row(align=True)
            row.active = def_st_available
            row.prop(self, "me_show_xray", text="Show X-Ray", icon='XRAY')

            row = flow.row(align=True)
            row.label(text="Select all edges touched by selection region")
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_all_edges"
            split = flow.split(align=True)
            row = split.row(align=True)
            row.active = rtl_st_available
            row.prop(rtl_props, "select_all_edges", text="Select All Edges", icon='EDGESEL')
            row = split.row(align=True)
            row.active = ltr_st_available
            row.prop(ltr_props, "select_all_edges", text="Select All Edges", icon='EDGESEL')
            row = split.row(align=True)
            row.active = def_st_available
            row.prop(self, "me_select_all_edges", text="Select All Edges", icon='EDGESEL')

            row = flow.row(align=True)
            row.label(text="Select all faces touched by selection region")
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_all_faces"
            split = flow.split(align=True)
            row = split.row(align=True)
            row.active = rtl_st_available
            row.prop(rtl_props, "select_all_faces", text="Select All Faces", icon='FACESEL')
            row = split.row(align=True)
            row.active = ltr_st_available
            row.prop(ltr_props, "select_all_faces", text="Select All Faces", icon='FACESEL')
            row = split.row(align=True)
            row.active = def_st_available
            row.prop(self, "me_select_all_faces", text="Select All Faces", icon='FACESEL')

            self.draw_flow_vertical_separator(flow)

            flow.label(text="Configure tool settings separately for drag directions")
            split = flow.split(align=True)
            split.prop(self, "me_directional_box", text="Directional Box", icon='UV_SYNC_SELECT')
            row = split.row(align=True)
            row.prop(self, "me_directional_lasso", text="Directional Lasso", icon='UV_SYNC_SELECT')
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_drag_direction"

            self.draw_flow_vertical_separator(flow)

            flow.label(text="Temporary hide this modifiers during selection through")
            split = flow.split(align=True)
            split.active = rtl_st_available or ltr_st_available or def_st_available
            split.prop(self, "me_hide_mirror", text="Mirror", icon='MOD_MIRROR')
            row = split.row(align=True)
            row.prop(self, "me_hide_solidify", text="Solidify", icon='MOD_SOLIDIFY')
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_hide_modifiers"

            self.draw_flow_vertical_separator(flow)

            flow.label(text="Show box tool crosshair or lasso tool icon")
            split = flow.split(align=True)
            split.prop(self, "me_show_crosshair", text="Show Crosshair", icon='RESTRICT_SELECT_OFF')
            row = split.row(align=True)
            row.prop(self, "me_show_lasso_icon", text="Show Lasso Icon", icon='RESTRICT_SELECT_OFF')
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "wait_for_input_cursor"

        else:
            flow = box.grid_flow(columns=2, row_major=True, align=True)

            flow.label(text="Start selection with enabled selection through")
            flow.prop(self, "me_select_through", text="Select Through", icon='MOD_WIREFRAME')

            flow.label(text="Toggle select through during selection with a key")
            split = flow.split(align=True)
            sub = split.row(align=True)
            sub.active = self.me_select_through_toggle_key != 'DISABLED'
            sub.prop(self, "me_select_through_toggle_type", text="")
            split.prop(self, "me_select_through_toggle_key", text="")

            self.draw_flow_vertical_separator(flow)

            flow.label(text="Selection frame color when selection through is disabled")
            flow.prop(self, "me_default_color", text="")

            st_available = self.me_select_through or self.me_select_through_toggle_key != 'DISABLED'

            flow.label(text="Selection frame color when selection through is enabled")
            flow.prop(self, "me_select_through_color", text="")

            self.draw_flow_vertical_separator(flow)

            flow.label(text="Show x-ray shading during selection through")
            row = flow.row()
            row.active = st_available
            row.prop(self, "me_show_xray", text="Show X-Ray", icon='XRAY')

            self.draw_flow_vertical_separator(flow)

            flow.label(text="Select all edges touched by selection region")
            row = flow.row(align=True)
            row.active = st_available
            row.prop(self, "me_select_all_edges", text="Select All Edges", icon='EDGESEL')
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_all_edges"

            flow.label(text="Select all faces touched by selection region")
            row = flow.row(align=True)
            row.active = st_available
            row.prop(self, "me_select_all_faces", text="Select All Faces", icon='FACESEL')
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_all_faces"

            self.draw_flow_vertical_separator(flow)

            flow.label(text="Configure tool settings separately for drag directions")
            split = flow.split(align=True)
            split.prop(self, "me_directional_box", text="Directional Box", icon='UV_SYNC_SELECT')
            row = split.row(align=True)
            row.prop(self, "me_directional_lasso", text="Directional Lasso", icon='UV_SYNC_SELECT')
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_drag_direction"

            self.draw_flow_vertical_separator(flow)

            flow.label(text="Temporary hide this modifiers during selection through")
            split = flow.split(align=True)
            split.active = st_available
            split.prop(self, "me_hide_mirror", text="Mirror", icon='MOD_MIRROR')
            row = split.row(align=True)
            row.prop(self, "me_hide_solidify", text="Solidify", icon='MOD_SOLIDIFY')
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_hide_modifiers"

            self.draw_flow_vertical_separator(flow)

            flow.label(text="Show box tool crosshair or lasso tool icon")
            split = flow.split(align=True)
            split.prop(self, "me_show_crosshair", text="Show Crosshair", icon='RESTRICT_SELECT_OFF')
            row = split.row(align=True)
            row.prop(self, "me_show_lasso_icon", text="Show Lasso Icon", icon='RESTRICT_SELECT_OFF')
            row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "wait_for_input_cursor"

    def draw_object_tools_preferences(self, box):
        if self.enable_ob_keyboard_keymap:
            box.label(text="Change shortcuts here or disable them by unchecking")
            col = box.column()
            self.draw_keymap_items(col, "Object Mode", ob_keyboard_keymap, {'KEYBOARD'}, False)
            box.separator(factor=1.7)

        flow = box.grid_flow(columns=2, row_major=True, align=True)

        flow.label(text="Start selection with enabled x-ray shading")
        flow.prop(self, "ob_show_xray", text="Show X-Ray", icon='XRAY')

        flow.label(text="Toggle x-ray shading during selection with a key")
        split = flow.split(align=True)
        sub = split.row(align=True)
        sub.active = self.ob_xray_toggle_key != 'DISABLED'
        sub.prop(self, "ob_xray_toggle_type", text="")
        split.prop(self, "ob_xray_toggle_key", text="")

        self.draw_flow_vertical_separator(flow)

        flow.label(text="Box tool behavior")
        row = flow.row(align=True)
        row.prop(self, "ob_box_select_behavior", text="")
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "ob_selection_behavior"

        flow.label(text="Circle tool behavior")
        row = flow.row(align=True)
        row.prop(self, "ob_circle_select_behavior", text="")
        row.label(text="", icon='BLANK1')

        flow.label(text="Lasso tool behavior")
        row = flow.row(align=True)
        row.prop(self, "ob_lasso_select_behavior", text="")
        row.label(text="", icon='BLANK1')

        self.draw_flow_vertical_separator(flow)

        flow.label(text="Show box tool crosshair or lasso tool icon")
        split = flow.split(align=True)
        split.prop(self, "ob_show_crosshair", text="Show Crosshair", icon='RESTRICT_SELECT_OFF')
        row = split.row(align=True)
        row.prop(self, "ob_show_lasso_icon", text="Show Lasso Icon", icon='RESTRICT_SELECT_OFF')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "wait_for_input_cursor"

    def draw_adv_keymap(self, box):

        # Object and Mesh Mode Keymap
        col = box.column()
        row = col.row(align=True)
        row.label(text="Shortcuts for starting tools and changing preferences")
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "tool_keymaps"

        col = box.column()

        km_col = col.column(align=True)
        icon = 'CHECKBOX_HLT' if self.enable_me_keyboard_keymap else 'CHECKBOX_DEHLT'
        km_col.prop(self, "enable_me_keyboard_keymap", text="Mesh Mode Tools: Keyboard Shortcuts",
                    icon=icon)
        if self.enable_me_keyboard_keymap:
            sub_box = km_col.box()
            kmi_col = sub_box.column(align=True)
            self.draw_keymap_items(kmi_col, "Mesh", me_keyboard_keymap, {'KEYBOARD'}, True)

        km_col = col.column(align=True)
        icon = 'CHECKBOX_HLT' if self.enable_ob_keyboard_keymap else 'CHECKBOX_DEHLT'
        km_col.prop(self, "enable_ob_keyboard_keymap", text="Object Mode Tools: Keyboard Shortcuts",
                    icon=icon)
        if self.enable_ob_keyboard_keymap:
            sub_box = km_col.box()
            kmi_col = sub_box.column(align=True)
            self.draw_keymap_items(kmi_col, "Object Mode", ob_keyboard_keymap, {'KEYBOARD'}, True)

        km_col = col.column(align=True)
        icon = 'CHECKBOX_HLT' if self.enable_me_mouse_keymap else 'CHECKBOX_DEHLT'
        km_col.prop(self, "enable_me_mouse_keymap", text="Mesh Mode Tools: Mouse Shortcuts", icon=icon)
        if self.enable_me_mouse_keymap:
            sub_box = km_col.box()
            kmi_col = sub_box.column(align=True)
            self.draw_keymap_items(kmi_col, "Mesh", me_mouse_keymap, {'MOUSE', 'TWEAK'}, True)

        km_col = col.column(align=True)
        icon = 'CHECKBOX_HLT' if self.enable_ob_mouse_keymap else 'CHECKBOX_DEHLT'
        km_col.prop(self, "enable_ob_mouse_keymap", text="Object Mode Tools: Mouse Shortcuts", icon=icon)
        if self.enable_ob_mouse_keymap:
            sub = km_col.box()
            kmi_col = sub.column(align=True)
            self.draw_keymap_items(kmi_col, "Object Mode", ob_mouse_keymap, {'MOUSE', 'TWEAK'}, True)

        km_col = col.column(align=True)
        icon = 'CHECKBOX_HLT' if self.enable_toggles_keymap else 'CHECKBOX_DEHLT'
        km_col.prop(self, "enable_toggles_keymap", text="Preferences Toggle Shortcuts", icon=icon)
        if self.enable_toggles_keymap:
            sub_box = km_col.box()
            kmi_col = sub_box.column(align=True)
            self.draw_keymap_items(kmi_col, "Mesh", toggles_keymap, {'MOUSE', 'TWEAK', 'KEYBOARD'}, True)

        # Tool Selection Mode Keymap
        box.separator()
        row = box.row(align=True)
        row.label(text="Shortcuts for toolbar tool selection modes")
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "tool_selection_mode_keymaps"

        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(self, "tool_keymap_tabs", expand=True)

        tool = self.tool_keymap_tabs
        keymap = self.keymaps_of_tools[tool]
        kmis = keymap.kmis
        for mode in kmis.keys():
            row = col.row(align=True)
            description = kmis[mode].description
            icon = kmis[mode].icon
            row.prop(kmis[mode], "active", text=description, icon=icon)

            sub = row.row(align=True)
            sub.active = kmis[mode].active
            sub.prop(kmis[mode], "shift", text="Shift", toggle=True)
            sub.prop(kmis[mode], "ctrl", text="Ctrl", toggle=True)
            sub.prop(kmis[mode], "alt", text="Alt", toggle=True)

    @staticmethod
    def draw_keymap_items(col, km_name, keymap, map_type, allow_remove):
        kc = bpy.context.window_manager.keyconfigs.user
        km = kc.keymaps.get(km_name)
        kmi_idnames = [km_tuple[1].idname for km_tuple in keymap]
        if allow_remove:
            col.context_pointer_set("keymap", km)

        kmis = [kmi for kmi in km.keymap_items if
                kmi.idname in kmi_idnames and kmi.map_type in map_type]
        for kmi in kmis:
            rna_keymap_ui.draw_kmi(['ADDON', 'USER', 'DEFAULT'], kc, km, kmi, col, 0)


def populate_preferences_direction_properties():
    left = get_preferences().me_direction_properties.add()
    left.name = "RIGHT_TO_LEFT"
    left = get_preferences().me_direction_properties.add()
    left.name = "LEFT_TO_RIGHT"


classes = (
    XRAYSELToolMeDirectionProps,
    XRAYSELToolKmiPG,
    XRAYSELToolKeymapPG,
    XRAYSELPreferences
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    populate_preferences_keymaps_of_tools()
    populate_preferences_direction_properties()


def unregister():
    get_preferences().me_direction_properties.clear()
    get_preferences().keymaps_of_tools.clear()

    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
