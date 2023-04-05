import bpy
from bpy.props import IntProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty
import os
from . utils.ui import get_icon, draw_keymap_items, get_keymap_item
from . utils.registration import activate, get_path, get_name, get_addon
from . items import preferences_tabs, matcap_background_type_items


decalmachine = None
meshmachine = None
punchit = None

has_sidebar = ['OT_smart_drive',
               'OT_group',
               'OT_create_assembly_asset',
               'OT_prepare_unity_export']

draws_lines = ['OT_smart_vert',
               'OT_punch_it']

has_hud = ['OT_material_picker',
           'OT_surface_slide',
           'OT_clean_up',
           'OT_clipping_toggle',
           'OT_group',
           'OT_transform_edge_constrained',
           'OT_focus',
           'MT_tools_pie',
           'OT_mirror']

is_fading = ['OT_material_picker',
             'OT_clean_up',
             'OT_clipping_toggle',
             'OT_group',
             'MT_tools_pie']

has_settings = has_sidebar + draws_lines + has_hud + ['OT_smart_vert',
                                                      'OT_clean_up',
                                                      'OT_punch_it',
                                                      'OT_transform_edge_constrained',
                                                      'OT_focus',
                                                      'OT_group',
                                                      'OT_render',
                                                      'OT_create_assembly_asset',
                                                      'OT_clipping_toggle',
                                                      'OT_surface_slide',
                                                      'OT_material_picker',
                                                      'OT_clipping_toggle',
                                                      'OT_customize',

                                                      'MT_modes_pie',
                                                      'MT_save_pie',
                                                      'MT_shading_pie',
                                                      'MT_cursor_pie',
                                                      'MT_snapping_pie',
                                                      'MT_viewport_pie',
                                                      'MT_tools_pie']


class MACHIN3toolsPreferences(bpy.types.AddonPreferences):
    path = get_path()
    bl_idname = get_name()



    def update_switchmatcap1(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        matcaps = [mc.name for mc in context.preferences.studio_lights if os.path.basename(os.path.dirname(mc.path)) == "matcap"]
        if self.switchmatcap1 not in matcaps:
            self.avoid_update = True
            self.switchmatcap1 = "NOT FOUND"

    def update_switchmatcap2(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        matcaps = [mc.name for mc in context.preferences.studio_lights if os.path.basename(os.path.dirname(mc.path)) == "matcap"]
        if self.switchmatcap2 not in matcaps:
            self.avoid_update = True
            self.switchmatcap2 = "NOT FOUND"

    def update_custom_preferences_keymap(self, context):
        if self.custom_preferences_keymap:
            kc = context.window_manager.keyconfigs.user

            for km in kc.keymaps:
                if km.is_user_modified:
                    self.custom_preferences_keymap = False
                    self.dirty_keymaps = True
                    return

            self.dirty_keymaps = False

    def update_auto_smooth_angle_presets(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        try:
            angles = [int(a) for a in self.auto_smooth_angle_presets.split(',')]
        except:
            self.avoid_update = True
            self.auto_smooth_angle_presets = "10, 20, 30, 60, 180"



    def update_activate_smart_vert(self, context):
        activate(self, register=self.activate_smart_vert, tool="smart_vert")

    def update_activate_smart_edge(self, context):
        activate(self, register=self.activate_smart_edge, tool="smart_edge")

    def update_activate_smart_face(self, context):
        activate(self, register=self.activate_smart_face, tool="smart_face")

    def update_activate_clean_up(self, context):
        activate(self, register=self.activate_clean_up, tool="clean_up")

    def update_activate_extrude(self, context):
        activate(self, register=self.activate_extrude, tool="extrude")

    def update_activate_focus(self, context):
        activate(self, register=self.activate_focus, tool="focus")

    def update_activate_mirror(self, context):
        activate(self, register=self.activate_mirror, tool="mirror")

    def update_activate_align(self, context):
        activate(self, register=self.activate_align, tool="align")

    def update_activate_group(self, context):
        activate(self, register=self.activate_group, tool="group")

    def update_activate_smart_drive(self, context):
        activate(self, register=self.activate_smart_drive, tool="smart_drive")

    def update_activate_assetbrowser_tools(self, context):
        activate(self, register=self.activate_assetbrowser_tools, tool="assetbrowser")

    def update_activate_filebrowser_tools(self, context):
        activate(self, register=self.activate_filebrowser_tools, tool="filebrowser")

    def update_activate_render(self, context):
        activate(self, register=self.activate_render, tool="render")

    def update_activate_smooth(self, context):
        activate(self, register=self.activate_smooth, tool="smooth")

    def update_activate_clipping_toggle(self, context):
        activate(self, register=self.activate_clipping_toggle, tool="clipping_toggle")

    def update_activate_surface_slide(self, context):
        activate(self, register=self.activate_surface_slide, tool="surface_slide")

    def update_activate_material_picker(self, context):
        activate(self, register=self.activate_material_picker, tool="material_picker")

    def update_activate_apply(self, context):
        activate(self, register=self.activate_apply, tool="apply")

    def update_activate_select(self, context):
        activate(self, register=self.activate_select, tool="select")

    def update_activate_mesh_cut(self, context):
        activate(self, register=self.activate_mesh_cut, tool="mesh_cut")

    def update_activate_thread(self, context):
        activate(self, register=self.activate_thread, tool="thread")

    def update_activate_unity(self, context):
        activate(self, register=self.activate_unity, tool="unity")

    def update_activate_customize(self, context):
        activate(self, register=self.activate_customize, tool="customize")



    def update_activate_modes_pie(self, context):
        activate(self, register=self.activate_modes_pie, tool="modes_pie")

    def update_activate_save_pie(self, context):
        activate(self, register=self.activate_save_pie, tool="save_pie")

    def update_activate_shading_pie(self, context):
        activate(self, register=self.activate_shading_pie, tool="shading_pie")

    def update_activate_views_pie(self, context):
        activate(self, register=self.activate_views_pie, tool="views_pie")

    def update_activate_align_pie(self, context):
        activate(self, register=self.activate_align_pie, tool="align_pie")

    def update_activate_cursor_pie(self, context):
        activate(self, register=self.activate_cursor_pie, tool="cursor_pie")

    def update_activate_transform_pie(self, context):
        activate(self, register=self.activate_transform_pie, tool="transform_pie")

    def update_activate_snapping_pie(self, context):
        activate(self, register=self.activate_snapping_pie, tool="snapping_pie")

    def update_activate_collections_pie(self, context):
        activate(self, register=self.activate_collections_pie, tool="collections_pie")

    def update_activate_workspace_pie(self, context):
        activate(self, register=self.activate_workspace_pie, tool="workspace_pie")

    def update_activate_tools_pie(self, context):
        activate(self, register=self.activate_tools_pie, tool="tools_pie")



    focus_show: BoolProperty(name="Show Focus Preferences", default=False)

    focus_view_transition: BoolProperty(name="Viewport Tweening", default=True)
    focus_lights: BoolProperty(name="Ignore Lights (keep them always visible)", default=False)



    group_show: BoolProperty(name="Show Group Preferences", default=False)

    group_auto_name: BoolProperty(name="Auto Name Groups", description="Automatically add a Prefix and/or Suffix to any user-set Group Name", default=True)
    group_basename: StringProperty(name="Group Basename", default="GROUP")
    group_prefix: StringProperty(name="Prefix to add to Group Names", default="_")
    group_suffix: StringProperty(name="Suffix to add to Group Names", default="_grp")
    group_size: FloatProperty(name="Group Empty Draw Size", description="Default Group Size", default=0.2)
    group_fade_sizes: BoolProperty(name="Fade Group Empty Sizes", description="Make Sub Group's Emtpies smaller than their Parents", default=True)
    group_fade_factor: FloatProperty(name="Fade Group Size Factor", description="Factor by which to decrease each Group Empty's Size", default=0.8, min=0.1, max=0.9)



    assetbrowser_show: BoolProperty(name="Show Assetbrowser Tools Preferences", default=False)

    preferred_default_catalog: StringProperty(name="Preferred Default Catalog", default="Model")
    preferred_assetbrowser_workspace_name: StringProperty(name="Preferred Workspace for Assembly Asset Creation", default="General.alt")
    show_assembly_asset_creation_in_save_pie: BoolProperty(name="Show Assembly Asset Creation in Save Pie", default=True)
    show_instance_collection_assembly_in_modes_pie: BoolProperty(name="Show Collection Instance Assembly in Modes Pie", default=True)
    hide_wire_objects_when_creating_assembly_asset: BoolProperty(name="Hide Wire Objects when creating Assembly Asset", default=True)
    hide_wire_objects_when_assembling_instance_collection: BoolProperty(name="Hide Wire Objects when assembling Collection Instance", default=True)



    render_show: BoolProperty(name="Show Render Preferences", default=False)

    render_folder_name: StringProperty(name="Render Folder Name", description="Folder used to stored rended images relative to the Location of the .blend file", default='out')
    render_seed_count: IntProperty(name="Seed Render Count", description="Set the Amount of Seed Renderings used to remove Fireflies", default=3, min=2, max=9)
    render_keep_seed_renderings: BoolProperty(name="Keep Individual Renderings", description="Keep the individual Seed Renderings, after they've been combined into a single Image", default=False)
    render_use_clownmatte_naming: BoolProperty(name="Use Clownmatte Name", description="""It's a better name than "Cryptomatte", believe me""", default=True)
    render_show_buttons_in_light_properties: BoolProperty(name="Show Render Buttons in Light Properties Panel", description="Show Render Buttons in Light Properties Panel", default=True)
    render_sync_light_visibility: BoolProperty(name="Sync Light visibility/renderability", description="Sync Light hide_render props based on hide_viewport props", default=True)
    render_adjust_lights_on_render: BoolProperty(name="Ajust Area Lights when Rendering in Cycles", description="Adjust Area Lights when Rendering, to better match Eevee and Cycles", default=True)
    render_enforce_hide_render: BoolProperty(name="Enforce hide_render setting when Viewport Rendering", description="Adjust Area Lights when Rendering, to better match Eevee and Cycles", default=True)



    matpick_show: BoolProperty(name="Show Material Picker Preferences", default=False)

    matpick_workspace_names: StringProperty(name="Workspaces the Material Picker should appear on", default="Shading, Material")
    matpick_spacing_obj: FloatProperty(name="Object Mode Spacing", min=0, default=20)
    matpick_spacing_edit: FloatProperty(name="Edit Mode Spacing", min=0, default=5)



    customize_show: BoolProperty(name="Show Cuatomize Preferences", default=False)

    custom_startup: BoolProperty(name="Startup Scene", default=False)
    custom_theme: BoolProperty(name="Theme", default=True)
    custom_matcaps: BoolProperty(name="Matcaps", default=True)
    custom_shading: BoolProperty(name="Shading", default=False)
    custom_overlays: BoolProperty(name="Overlays", default=False)
    custom_outliner: BoolProperty(name="Outliner", default=False)
    custom_preferences_interface: BoolProperty(name="Preferences: Interface", default=False)
    custom_preferences_viewport: BoolProperty(name="Preferences: Viewport", default=False)
    custom_preferences_navigation: BoolProperty(name="Preferences: Navigation", default=False)
    custom_preferences_keymap: BoolProperty(name="Preferences: Keymap", default=False, update=update_custom_preferences_keymap)
    custom_preferences_system: BoolProperty(name="Preferences: System", default=False)
    custom_preferences_save: BoolProperty(name="Preferences: Save & Load", default=False)



    modes_pie_show: BoolProperty(name="Show Modes Pie Preferences", default=False)

    toggle_cavity: BoolProperty(name="Toggle Cavity/Curvature OFF in Edit Mode, ON in Object Mode", default=True)
    toggle_xray: BoolProperty(name="Toggle X-Ray ON in Edit Mode, OFF in Object Mode, if Pass Through or Wireframe was enabled in Edit Mode", default=True)
    sync_tools: BoolProperty(name="Sync Tool if possible, when switching Modes", default=True)



    save_pie_versioned_show: BoolProperty(name="Show Save Pie: Versioned Startup File Preferences", default=False)
    save_pie_import_show: BoolProperty(name="Show Save Pie: Import/Export Preferences", default=False)
    save_pie_screencast_show: BoolProperty(name="Show Save Pie: ScreenCast Preferences", default=False)

    save_pie_show_obj_export: BoolProperty(name="Show .obj Export", default=True)
    save_pie_show_fbx_export: BoolProperty(name="Show .fbx Export", default=True)
    save_pie_show_usd_export: BoolProperty(name="Show .usd Export", default=True)

    fbx_export_apply_scale_all: BoolProperty(name="Use 'Fbx All' for Applying Scale", description="This is useful for Unity, but bad for Unreal Engine", default=False)

    show_screencast: BoolProperty(name="Show Screencast in Save Pie", description="Show Screencast in Save Pie", default=True)
    screencast_operator_count: IntProperty(name="Operator Count", description="Maximum number of Operators displayed when Screen Casting", default=12, min=1, max=100)
    screencast_fontsize: IntProperty(name="Font Size", default=12, min=2)
    screencast_highlight_machin3: BoolProperty(name="Highlight MACHIN3 operators", description="Highlight Operators from MACHIN3 addons", default=True)
    screencast_show_addon: BoolProperty(name="Display Operator's Addons", description="Display Operator's Addon", default=True)
    screencast_show_idname: BoolProperty(name="Display Operator's idnames", description="Display Operator's bl_idname properties", default=False)



    shading_pie_autosmooth_show: BoolProperty(name="Show Shading Pie: Autosmooth Preferences", default=False)
    shading_pie_matcap_show: BoolProperty(name="Show Shading Pie: Matcap Switch Preferences", default=False)

    switchmatcap1: StringProperty(name="Matcap 1", update=update_switchmatcap1)
    switchmatcap2: StringProperty(name="Matcap 2", update=update_switchmatcap2)
    matcap2_force_single: BoolProperty(name="Force Single Color Shading for Matcap 2", default=True)
    matcap2_disable_overlays: BoolProperty(name="Disable Overlays for Matcap 2", default=True)

    matcap_switch_background: BoolProperty(name="Switch Background too", default=False)
    matcap1_switch_background_type: EnumProperty(name="Matcap 1 Background Type", items=matcap_background_type_items, default="THEME")
    matcap1_switch_background_viewport_color: FloatVectorProperty(name="Matcap 1 Background Color", subtype='COLOR', default=[0.05, 0.05, 0.05], size=3, min=0, max=1)

    matcap2_switch_background_type: EnumProperty(name="Matcap 2 Background Type", items=matcap_background_type_items, default="THEME")
    matcap2_switch_background_viewport_color: FloatVectorProperty(name="Matcap 2 Background Color", subtype='COLOR', default=[0.05, 0.05, 0.05], size=3, min=0, max=1)

    auto_smooth_angle_presets: StringProperty(name="Autosmooth Angle Preset", default="10, 20, 30, 60, 180", update=update_auto_smooth_angle_presets)



    views_pie_show: BoolProperty(name="Show Views Pie Preferences", default=False)

    obj_mode_rotate_around_active: BoolProperty(name="Rotate Around Selection, but only in Object Mode", default=False)
    custom_views_use_trackball: BoolProperty(name="Force Trackball Navigation when using Custom Views", default=True)
    custom_views_set_transform_preset: BoolProperty(name="Set Transform Preset when using Custom Views", default=False)
    show_orbit_selection: BoolProperty(name="Show Orbit around Active", default=True)
    show_orbit_method: BoolProperty(name="Show Orbit Method Selection", default=True)



    cursor_pie_show: BoolProperty(name="Show Cursor and Origin Pie Preferences", default=False)

    cursor_show_to_grid: BoolProperty(name="Show Cursor and Selected to Grid", default=False)
    cursor_set_transform_preset: BoolProperty(name="Set Transform Preset when Setting Cursor", default=False)



    snapping_pie_show: BoolProperty(name="Show Snapping Pie Preferences", default=False)

    snap_show_absolute_grid: BoolProperty(name="Show Absolute Grid Snapping", default=False)
    snap_show_volume: BoolProperty(name="Show Volume Snapping", default=False)




    workspace_pie_show: BoolProperty(name="Show Workspace Pie Preferences", default=False)

    pie_workspace_left_name: StringProperty(name="Left Workspace Name", default="Layout")
    pie_workspace_left_text: StringProperty(name="Left Workspace Custom Label", default="MACHIN3")
    pie_workspace_left_icon: StringProperty(name="Left Workspace Icon", default="VIEW3D")

    pie_workspace_top_left_name: StringProperty(name="Top-Left Workspace Name", default="UV Editing")
    pie_workspace_top_left_text: StringProperty(name="Top-Left Workspace Custom Label", default="UVs")
    pie_workspace_top_left_icon: StringProperty(name="Top-Left Workspace Icon", default="GROUP_UVS")

    pie_workspace_top_name: StringProperty(name="Top Workspace Name", default="Shading")
    pie_workspace_top_text: StringProperty(name="Top Workspace Custom Label", default="Materials")
    pie_workspace_top_icon: StringProperty(name="Top Workspace Icon", default="MATERIAL_DATA")

    pie_workspace_top_right_name: StringProperty(name="Top-Right Workspace Name", default="")
    pie_workspace_top_right_text: StringProperty(name="Top-Right Workspace Custom Label", default="")
    pie_workspace_top_right_icon: StringProperty(name="Top-Right Workspace Icon", default="")

    pie_workspace_right_name: StringProperty(name="Right Workspace Name", default="Rendering")
    pie_workspace_right_text: StringProperty(name="Right Workspace Custom Label", default="")
    pie_workspace_right_icon: StringProperty(name="Right Workspace Icon", default="")

    pie_workspace_bottom_right_name: StringProperty(name="Bottom-Right Workspace Name", default="")
    pie_workspace_bottom_right_text: StringProperty(name="Bottom-Right Workspace Custom Label", default="")
    pie_workspace_bottom_right_icon: StringProperty(name="Bottom-Right Workspace Icon", default="")

    pie_workspace_bottom_name: StringProperty(name="Bottom Workspace Name", default="Scripting")
    pie_workspace_bottom_text: StringProperty(name="Bottom Workspace Custom Label", default="")
    pie_workspace_bottom_icon: StringProperty(name="Bottom Workspace Icon", default="CONSOLE")

    pie_workspace_bottom_left_name: StringProperty(name="Bottom-Left Workspace Name", default="")
    pie_workspace_bottom_left_text: StringProperty(name="Bottom-Left Workspace Custom Label", default="")
    pie_workspace_bottom_left_icon: StringProperty(name="Bottom-Left Workspace Icon", default="")



    tools_pie_show: BoolProperty(name="Show Tools Pie Preferences", default=False)

    tools_show_boxcutter_presets: BoolProperty(name="Show BoxCutter Presets", default=True)
    tools_show_hardops_menu: BoolProperty(name="Show Hard Ops Menu", default=True)
    tools_show_quick_favorites: BoolProperty(name="Show Quick Favorites", default=False)
    tools_show_tool_bar: BoolProperty(name="Show Tool Bar", default=False)



    activate_smart_vert: BoolProperty(name="Smart Vert", default=False, update=update_activate_smart_vert)
    activate_smart_edge: BoolProperty(name="Smart Edge", default=False, update=update_activate_smart_edge)
    activate_smart_face: BoolProperty(name="Smart Face", default=False, update=update_activate_smart_face)
    activate_clean_up: BoolProperty(name="Clean Up", default=False, update=update_activate_clean_up)
    activate_extrude: BoolProperty(name="Extrude", default=False, update=update_activate_extrude)
    activate_focus: BoolProperty(name="Focus", default=True, update=update_activate_focus)
    activate_mirror: BoolProperty(name="Mirror", default=False, update=update_activate_mirror)
    activate_align: BoolProperty(name="Align", default=False, update=update_activate_align)
    activate_group: BoolProperty(name="Group", default=False, update=update_activate_group)
    activate_smart_drive: BoolProperty(name="Smart Drive", default=False, update=update_activate_smart_drive)
    activate_assetbrowser_tools: BoolProperty(name="Assetbrowser Tools", default=False, update=update_activate_assetbrowser_tools)
    activate_filebrowser_tools: BoolProperty(name="Filebrowser Tools", default=False, update=update_activate_filebrowser_tools)
    activate_render: BoolProperty(name="Render", default=False, update=update_activate_render)
    activate_smooth: BoolProperty(name="Smooth", default=False, update=update_activate_smooth)
    activate_clipping_toggle: BoolProperty(name="Clipping Toggle", default=False, update=update_activate_clipping_toggle)
    activate_surface_slide: BoolProperty(name="Surface Slide", default=False, update=update_activate_surface_slide)
    activate_material_picker: BoolProperty(name="Material Picker", default=False, update=update_activate_material_picker)
    activate_apply: BoolProperty(name="Apply", default=False, update=update_activate_apply)
    activate_select: BoolProperty(name="Select", default=False, update=update_activate_select)
    activate_mesh_cut: BoolProperty(name="Mesh Cut", default=False, update=update_activate_mesh_cut)
    activate_thread: BoolProperty(name="Thread", default=False, update=update_activate_thread)
    activate_unity: BoolProperty(name="Unity", default=False, update=update_activate_unity)
    activate_customize: BoolProperty(name="Customize", default=False, update=update_activate_customize)



    activate_modes_pie: BoolProperty(name="Modes Pie", default=True, update=update_activate_modes_pie)
    activate_save_pie: BoolProperty(name="Save Pie", default=False, update=update_activate_save_pie)
    activate_shading_pie: BoolProperty(name="Shading Pie", default=False, update=update_activate_shading_pie)
    activate_views_pie: BoolProperty(name="Views Pie", default=False, update=update_activate_views_pie)
    activate_align_pie: BoolProperty(name="Align Pies", default=False, update=update_activate_align_pie)
    activate_cursor_pie: BoolProperty(name="Cursor and Origin Pie", default=False, update=update_activate_cursor_pie)
    activate_transform_pie: BoolProperty(name="Transform Pie", default=False, update=update_activate_transform_pie)
    activate_snapping_pie: BoolProperty(name="Snapping Pie", default=False, update=update_activate_snapping_pie)
    activate_collections_pie: BoolProperty(name="Collections Pie", default=False, update=update_activate_collections_pie)
    activate_workspace_pie: BoolProperty(name="Workspace Pie", default=False, update=update_activate_workspace_pie)
    activate_tools_pie: BoolProperty(name="Tools Pie", default=False, update=update_activate_tools_pie)



    use_group_sub_menu: BoolProperty(name="Use Group Sub-Menu", default=False)
    use_group_outliner_toggles: BoolProperty(name="Show Group Outliner Toggles", default=True)



    show_sidebar_panel: BoolProperty(name="Show Sidebar Panel", description="Show MACHIN3tools Panel in 3D View's Sidebar", default=True)
    use_legacy_line_smoothing: BoolProperty(name="Use Legacy Line Smoothing", description="Legacy Line Smoothing using the depreciated bgl module\nIf this is disabled, lines drawn by MACHIN3tools won't be anti aliased.", default=False)



    HUD_scale: FloatProperty(name="HUD Scale", description="Scale of HUD elements", default=1, min=0.1)
    HUD_fade_clean_up: FloatProperty(name="Clean Up HUD Fade Time (seconds)", default=1, min=0.1, max=3)
    HUD_fade_clipping_toggle: FloatProperty(name="Clipping Toggle HUD Fade Time (seconds)", default=1, min=0.1)
    HUD_fade_material_picker: FloatProperty(name="Material Picker HUD Fade Time (seconds)", default=0.5, min=0.1)
    HUD_fade_group: FloatProperty(name="Group HUD Fade Time (seconds)", default=1, min=0.1)
    HUD_fade_tools_pie: FloatProperty(name="Tools Pie HUD Fade Time (seconds)", default=0.75, min=0.1)

    mirror_flick_distance: IntProperty(name="Flick Distance", default=75, min=20, max=1000)



    tabs: EnumProperty(name="Tabs", items=preferences_tabs, default="GENERAL")
    avoid_update: BoolProperty(default=False)
    dirty_keymaps: BoolProperty(default=False)


    def draw(self, context):
        layout=self.layout



        column = layout.column(align=True)
        row = column.row()
        row.prop(self, "tabs", expand=True)

        box = column.box()

        if self.tabs == "GENERAL":
            self.draw_general(box)

        elif self.tabs == "KEYMAPS":
            self.draw_keymaps(box)

        elif self.tabs == "ABOUT":
            self.draw_about(box)

    def draw_general(self, box):
        split = box.split()


        b = split.box()
        b.label(text="Activate")



        bb = b.box()
        bb.label(text="Tools")

        column = bb.column(align=True)

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_smart_vert", toggle=True)
        row.label(text="Smart Vertex Merging, Connecting and Sliding.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_smart_edge", toggle=True)
        row.label(text="Smart Edge Creation, Manipulation, Projection and Selection Conversion.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_smart_face", toggle=True)
        row.label(text="Smart Face Creation and Object-from-Face Creation.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_clean_up", toggle=True)
        row.label(text="Quick Geometry Clean-up.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_extrude", toggle=True)
        row.label(text="Fixing Blender's Extrude Manifold and Spin Operators")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_focus", toggle=True)
        row.label(text="Object Focus and Multi-Level Isolation.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_mirror", toggle=True)
        row.label(text="Object Mirroring and Un-Mirroring.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_align", toggle=True)
        row.label(text="Object per-axis Location, Rotation and Scale Alignment, as well as Object Relative Alignments.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_group", toggle=True)
        row.label(text="Group Objects using Empties as Parents.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_smart_drive", toggle=True)
        row.label(text="Use one Object to drive another.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_assetbrowser_tools", toggle=True)
        row.label(text="Easy Assemly Asset Creation and Import via the Assetbrowser.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_filebrowser_tools", toggle=True)
        row.label(text="Additional Tools/Shortcuts for the Filebrowser.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_render", toggle=True)
        row.label(text="Tools for efficient, iterative rendering.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_smooth", toggle=True)
        row.label(text="Toggle Smoothing in Korean Bevel and SubD workflows.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_clipping_toggle", toggle=True)
        row.label(text="Viewport Clipping Plane Toggle.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_surface_slide", toggle=True)
        row.label(text="Easily modify Mesh Topology, while maintaining Form.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_material_picker", toggle=True)
        row.label(text="Pick Materials from the Material Workspace's 3D View.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_apply", toggle=True)
        row.label(text="Apply Transformations while keeping the Bevel Width as well as the Child Transformations unchanged.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_select", toggle=True)
        row.label(text="Select Center Objects or Wire Objects.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_mesh_cut", toggle=True)
        row.label(text="Knife Intersect a Mesh-Object, using another one.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_thread", toggle=True)
        row.label(text="Easily turn Cylinder Faces into Thread.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_unity", toggle=True)
        row.label(text="Unity related Tools.")

        column.separator()
        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_customize", toggle=True)
        row.label(text="Customize various Blender preferences, settings and keymaps.")



        bb = b.box()
        bb.label(text="Pie Menus")

        column = bb.column(align=True)

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_modes_pie", toggle=True)
        row.label(text="Quick mode changing.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_save_pie", toggle=True)
        row.label(text="Save, Open, Append and Link. Load Recent, Previous and Next. Purge and Clean Out. ScreenCast.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_shading_pie", toggle=True)
        row.label(text="Control shading, overlays, eevee and some object properties.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_views_pie", toggle=True)
        row.label(text="Control views. Create and manage cameras.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_align_pie", toggle=True)
        row.label(text="Edit mesh and UV alignments.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_cursor_pie", toggle=True)
        row.label(text="Cursor and Origin manipulation.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_transform_pie", toggle=True)
        row.label(text="Transform Orientations and Pivots.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_snapping_pie", toggle=True)
        row.label(text="Snapping.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_collections_pie", toggle=True)
        row.label(text="Collection management.")

        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_workspace_pie", toggle=True)
        r = row.split(factor=0.4)
        r.label(text="Switch Workplaces.")
        r.label(text="If enabled, customize it in ui/pies.py", icon="INFO")

        column.separator()
        row = column.split(factor=0.25, align=True)
        row.prop(self, "activate_tools_pie", toggle=True)
        row.label(text="Switch Tools, useful with BoxCutter/HardOps and HyperCursor.")



        b = split.box()
        b.label(text="Settings")



        if any([getattr(bpy.types, f'MACHIN3_{name}', False) for name in has_sidebar + draws_lines]):
            bb = b.box()
            bb.label(text="View 3D")

            if any([getattr(bpy.types, f'MACHIN3_{name}', False) for name in has_sidebar]):
                column = bb.column()
                column.prop(self, "show_sidebar_panel")

            if any([getattr(bpy.types, f'MACHIN3_{name}', False) for name in draws_lines]):
                column = bb.column()
                column.prop(self, "use_legacy_line_smoothing")


        if any([getattr(bpy.types, f'MACHIN3_{name}', False) for name in has_hud]):
            bb = b.box()
            bb.label(text="HUD")

            column = bb.column()
            row = column.row()
            r = row.split(factor=0.2)
            r.prop(self, "HUD_scale", text="")
            r.label(text="HUD Scale")

            if getattr(bpy.types, "MACHIN3_OT_mirror", False):
                r = row.split(factor=0.3)
                r.prop(self, "mirror_flick_distance", text="")
                r.label(text="Mirror Flick Distance")

            if any([getattr(bpy.types, f'MACHIN3_{name}', False) for name in is_fading]):
                column = bb.column()
                column.label(text="Fade time")

                column = bb.column()
                row = column.row(align=True)

                if getattr(bpy.types, "MACHIN3_OT_clean_up", False):
                    row.prop(self, "HUD_fade_clean_up", text="Clean Up")

                if getattr(bpy.types, "MACHIN3_OT_clipping_toggle", False):
                    row.prop(self, "HUD_fade_clipping_toggle", text="Clipping Toggle")

                if getattr(bpy.types, "MACHIN3_OT_material_picker", False):
                    row.prop(self, "HUD_fade_material_picker", text="Material Picker")

                if getattr(bpy.types, "MACHIN3_OT_group", False):
                    row.prop(self, "HUD_fade_group", text="Group")

                if getattr(bpy.types, "MACHIN3_MT_tools_pie", False):
                    row.prop(self, "HUD_fade_tools_pie", text="Tools Pie")



        if getattr(bpy.types, "MACHIN3_OT_focus", False):
            bb = b.box()
            bb.prop(self, 'focus_show', text="Focus", icon='TRIA_DOWN' if self.focus_show else 'TRIA_RIGHT', emboss=False)

            if self.focus_show:
                column = bb.column()
                column.prop(self, "focus_view_transition")

                column = bb.column()
                column.prop(self, "focus_lights")



        if getattr(bpy.types, "MACHIN3_OT_group", False):
            bb = b.box()
            bb.prop(self, 'group_show', text="Group", icon='TRIA_DOWN' if self.group_show else 'TRIA_RIGHT', emboss=False)

            if self.group_show:
                column = bb.column(align=True)

                row = column.split(factor=0.2, align=True)
                row.prop(self, "use_group_sub_menu", text='Sub Menu', toggle=True)
                row.label(text="Use Group Sub Menu in Object Context Menu.")

                row = column.split(factor=0.2, align=True)
                row.prop(self, "use_group_outliner_toggles", text='Outliner Toggles', toggle=True)
                row.label(text="Show Group Toggles in Outliner Header.")

                column.separator()

                row = column.row()
                r = row.split(factor=0.2)
                r.label(text="Basename")
                r.prop(self, "group_basename", text="")

                row = column.row()
                r = row.split(factor=0.2)
                r.prop(self, "group_auto_name", text='Auto Name', toggle=True)

                rr = r.row()
                rr.active = self.group_auto_name
                rr.prop(self, "group_prefix", text="Prefix")
                rr.prop(self, "group_suffix", text="Suffix")

                column.separator()

                row = column.row()
                r = row.split(factor=0.2)
                r.prop(self, "group_size", text="")
                r.label(text="Default Empty Draw Size")

                r.prop(self, "group_fade_sizes", text='Fade Sub Group Sizes')
                rr = r.row()
                rr.active = self.group_fade_sizes
                rr.prop(self, "group_fade_factor", text='Factor')



        if getattr(bpy.types, "MACHIN3_OT_assemble_instance_collection", False):
            bb = b.box()
            bb.prop(self, 'assetbrowser_show', text="Assetbrowser Tools", icon='TRIA_DOWN' if self.assetbrowser_show else 'TRIA_RIGHT', emboss=False)

            if self.assetbrowser_show:
                column = bb.column(align=True)
                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "preferred_default_catalog", text="")
                r.label(text="Preferred Default Catalog (must exist alredy)")

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "preferred_assetbrowser_workspace_name", text="")
                r.label(text="Preferred Workspace for Assembly Asset Creation")

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "hide_wire_objects_when_creating_assembly_asset", text="True" if self.hide_wire_objects_when_creating_assembly_asset else "False", toggle=True)
                r.label(text="Hide Wire Objects when creating Assembly Asset")

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "hide_wire_objects_when_assembling_instance_collection", text="True" if self.hide_wire_objects_when_assembling_instance_collection else "False", toggle=True)
                r.label(text="Hide Wire Objects when assembling Instance Collection")

                if getattr(bpy.types, "MACHIN3_MT_modes_pie", False):
                    row = column.row(align=True)
                    r = row.split(factor=0.2, align=True)
                    r.prop(self, "show_instance_collection_assembly_in_modes_pie", text="True" if self.show_instance_collection_assembly_in_modes_pie else "False", toggle=True)
                    r.label(text="Show Instance Collection Assembly in Modes Pie")

                if getattr(bpy.types, "MACHIN3_MT_save_pie", False):
                    row = column.row(align=True)
                    r = row.split(factor=0.2, align=True)
                    r.prop(self, "show_assembly_asset_creation_in_save_pie", text="True" if self.show_assembly_asset_creation_in_save_pie else "False", toggle=True)
                    r.label(text="Show Assembly Asset Creation in Save Pie")



        if getattr(bpy.types, "MACHIN3_OT_render", False):
            bb = b.box()
            bb.prop(self, 'render_show', text="Render", icon='TRIA_DOWN' if self.render_show else 'TRIA_RIGHT', emboss=False)

            if self.render_show:
                column = bb.column(align=True)
                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "render_folder_name", text="")
                r.label(text="Folder Name (relative to the .blend file)")

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "render_seed_count", text="")
                r.label(text="Seed Render Count")

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "render_keep_seed_renderings", text="True" if self.render_keep_seed_renderings else "False", toggle=True)
                r.label(text="Keep Individual Seed Renderings")

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "render_use_clownmatte_naming", text="True" if self.render_use_clownmatte_naming else "False", toggle=True)
                r.label(text="Use Clownmatte Naming")

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "render_show_buttons_in_light_properties", text="True" if self.render_show_buttons_in_light_properties else "False", toggle=True)
                r.label(text="Show Render Butttons in Light Properties Panel")

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "render_sync_light_visibility", text="True" if self.render_sync_light_visibility else "False", toggle=True)
                r.label(text="Sync Light visibility/renderability")

                column.separator()

                if self.activate_shading_pie:
                    row = column.row(align=True)
                    r = row.split(factor=0.2, align=True)
                    r.prop(self, "render_adjust_lights_on_render", text="True" if self.render_adjust_lights_on_render else "False", toggle=True)
                    r.label(text="Adjust Area Lights when Rendering in Cycles, controlled from the Shading Pie")#

                    row = column.row(align=True)
                    r = row.split(factor=0.2, align=True)
                    r.prop(self, "render_enforce_hide_render", text="True" if self.render_enforce_hide_render else "False", toggle=True)
                    r.label(text="Enforce hidde_render setting when Viewport Rendering, controlled from the Shading Pie")#

                else:
                    row = column.row(align=True)
                    row.separator()
                    row.label(text="Enable the Shading Pie for additional options", icon='INFO')



        if getattr(bpy.types, "MACHIN3_OT_material_picker", False):
            bb = b.box()
            bb.prop(self, 'matpick_show', text="Material Picker", icon='TRIA_DOWN' if self.matpick_show else 'TRIA_RIGHT', emboss=False)

            if self.matpick_show:
                column = bb.column(align=True)
                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "matpick_workspace_names", text="")
                r.label(text="Workspace Names")

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "matpick_spacing_obj", text="")
                r.label(text="Object Mode Spacing")

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "matpick_spacing_edit", text="")
                r.label(text="Edit Mode Spacing")




        if getattr(bpy.types, "MACHIN3_OT_customize", False):
            bb = b.box()
            bb.prop(self, 'customize_show', text="Customize", icon='TRIA_DOWN' if self.customize_show else 'TRIA_RIGHT', emboss=False)

            if self.customize_show:
                bbb = bb.box()
                column = bbb.column()

                row = column.row()
                row.prop(self, "custom_theme")
                row.prop(self, "custom_matcaps")
                row.prop(self, "custom_shading")

                row = column.row()
                row.prop(self, "custom_overlays")
                row.prop(self, "custom_outliner")
                row.prop(self, "custom_startup")

                bbb = bb.box()
                column = bbb.column()

                row = column.row()

                col = row.column()
                col.prop(self, "custom_preferences_interface")
                col.prop(self, "custom_preferences_keymap")

                col = row.column()
                col.prop(self, "custom_preferences_viewport")
                col.prop(self, "custom_preferences_system")

                col = row.column()
                col.prop(self, "custom_preferences_navigation")
                col.prop(self, "custom_preferences_save")

                if self.dirty_keymaps:
                    row = column.row()
                    row.label(text="Keymaps have been modified, restore them first.", icon="ERROR")
                    row.operator("machin3.restore_keymaps", text="Restore now")
                    row.label()

                column = bb.column()
                row = column.row()

                row.label()
                row.operator("machin3.customize", text="Customize")
                row.label()


        b.separator()



        if getattr(bpy.types, "MACHIN3_MT_modes_pie", False):
            bb = b.box()
            bb.prop(self, 'modes_pie_show', text="Modes Pie", icon='TRIA_DOWN' if self.modes_pie_show else 'TRIA_RIGHT', emboss=False)

            if self.modes_pie_show:
                column = bb.column(align=True)

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "toggle_cavity", text="True" if self.toggle_cavity else "False", toggle=True)
                r.label(text="Toggle Cavity/Curvature OFF in Edit Mode, ON in Object Mode")

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "toggle_xray", text="True" if self.toggle_xray else "False", toggle=True)
                r.label(text="Toggle X-Ray ON in Edit Mode, OFF in Object Mode, if Pass Through or Wireframe was enabled in Edit Mode")

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "sync_tools", text="True" if self.sync_tools else "False", toggle=True)
                r.label(text="Sync Tool if possible, when switching Modes")



        if getattr(bpy.types, "MACHIN3_MT_save_pie", False):


            kmi = get_keymap_item('Window', 'machin3.save_versioned_startup_file')

            if kmi:
                bb = b.box()
                bb.prop(self, 'save_pie_versioned_show', text="Save Pie: Versioned Startup File", icon='TRIA_DOWN' if self.save_pie_versioned_show else 'TRIA_RIGHT', emboss=False)

                if self.save_pie_versioned_show:
                    column = bb.column(align=True)
                    row = column.row(align=True)
                    r = row.split(factor=0.2, align=True)
                    r.prop(kmi, "active", text='Enabled' if kmi.active else 'Disabled')
                    r.label(text="Use CTRL + U keymap override")



            bb = b.box()
            bb.prop(self, 'save_pie_import_show', text="Save Pie: Import/Export", icon='TRIA_DOWN' if self.save_pie_import_show else 'TRIA_RIGHT', emboss=False)

            if self.save_pie_import_show:
                column = bb.column(align=True)


                row = column.row(align=True)
                split = row.split(factor=0.5, align=True)

                r = split.split(factor=0.42, align=True)
                r.prop(self, "save_pie_show_obj_export", text="True" if self.save_pie_show_obj_export else "False", toggle=True)
                r.label(text="Show .obj Import/Export")

                split.separator()


                row = column.row(align=True)
                split = row.split(factor=0.5, align=True)

                r = split.split(factor=0.42, align=True)
                r.prop(self, "save_pie_show_fbx_export", text="True" if self.save_pie_show_fbx_export else "False", toggle=True)
                r.label(text="Show .fbx Import/Export")

                if self.save_pie_show_fbx_export:
                    r = split.split(factor=0.42, align=True)
                    r.prop(self, "fbx_export_apply_scale_all", text="True" if self.fbx_export_apply_scale_all else "False", toggle=True)
                    r.label(text="Use 'Fbx All' for Applying Scale")

                else:
                    split.separator()


                row = column.row(align=True)
                split = row.split(factor=0.5, align=True)

                r = split.split(factor=0.42, align=True)
                r.prop(self, "save_pie_show_usd_export", text="True" if self.save_pie_show_usd_export else "False", toggle=True)
                r.label(text="Show .usd Import/Export")

                split.separator()



            bb = b.box()
            bb.prop(self, 'save_pie_screencast_show', text="Save Pie: Screen Cast", icon='TRIA_DOWN' if self.save_pie_screencast_show else 'TRIA_RIGHT', emboss=False)

            if self.save_pie_screencast_show:

                column = bb.column(align=True)
                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.prop(self, "show_screencast", text="True" if self.show_screencast else "False", toggle=True)
                r.label(text="Show Screencast in Save Pie")

                if self.show_screencast:
                    split = bb.split(factor=0.5)
                    col = split.column(align=True)

                    row = col.row(align=True)
                    r = row.split(factor=0.4, align=True)
                    r.prop(self, "screencast_operator_count", text="")
                    r.label(text="Operator Count")

                    row = col.row(align=True)
                    r = row.split(factor=0.4, align=True)
                    r.prop(self, "screencast_fontsize", text="")
                    r.label(text="Font Size")

                    col = split.column()
                    col.prop(self, "screencast_highlight_machin3")
                    col.prop(self, "screencast_show_addon")
                    col.prop(self, "screencast_show_idname")



        if getattr(bpy.types, "MACHIN3_MT_shading_pie", False):


            bb = b.box()
            bb.prop(self, 'shading_pie_autosmooth_show', text="Shading Pie: Autosmooth", icon='TRIA_DOWN' if self.shading_pie_autosmooth_show else 'TRIA_RIGHT', emboss=False)

            if self.shading_pie_autosmooth_show:
                column = bb.column(align=True)

                row = column.row(align=True)
                r = row.split(factor=0.2, align=True)
                r.label(text="Angle Presets")
                r.prop(self, "auto_smooth_angle_presets", text='')



            bb = b.box()
            bb.prop(self, 'shading_pie_matcap_show', text="Shading Pie: Matcap Switch", icon='TRIA_DOWN' if self.shading_pie_matcap_show else 'TRIA_RIGHT', emboss=False)

            if self.shading_pie_matcap_show:
                column = bb.column()

                row = column.row()
                row.prop(self, "switchmatcap1")
                row.prop(self, "switchmatcap2")

                row = column.split(factor=0.5)
                row.prop(self, "matcap_switch_background")

                col = row.column()
                col.prop(self, "matcap2_force_single")
                col.prop(self, "matcap2_disable_overlays")

                if self.matcap_switch_background:
                    row = column.row()
                    row.prop(self, "matcap1_switch_background_type", expand=True)
                    row.prop(self, "matcap2_switch_background_type", expand=True)

                    if any([bg == 'VIEWPORT' for bg in [self.matcap1_switch_background_type, self.matcap2_switch_background_type]]):
                        row = column.split(factor=0.5)

                        if self.matcap1_switch_background_type == 'VIEWPORT':
                            row.prop(self, "matcap1_switch_background_viewport_color", text='')

                        else:
                            row.separator()

                        if self.matcap2_switch_background_type == 'VIEWPORT':
                            row.prop(self, "matcap2_switch_background_viewport_color", text='')

                        else:
                            row.separator()



        if getattr(bpy.types, "MACHIN3_MT_viewport_pie", False):
            bb = b.box()
            bb.prop(self, 'views_pie_show', text="Views Pie", icon='TRIA_DOWN' if self.views_pie_show else 'TRIA_RIGHT', emboss=False)

            if self.views_pie_show:

                column = bb.column()
                column.prop(self, "custom_views_use_trackball")

                if self.activate_transform_pie:
                    column.prop(self, "custom_views_set_transform_preset")

                column.prop(self, "show_orbit_selection")
                column.prop(self, "show_orbit_method")



        if getattr(bpy.types, "MACHIN3_MT_cursor_pie", False):
            bb = b.box()
            bb.prop(self, 'cursor_pie_show', text="Cursor and Origin Pie", icon='TRIA_DOWN' if self.cursor_pie_show else 'TRIA_RIGHT', emboss=False)

            if self.cursor_pie_show:
                column = bb.column()
                column.prop(self, "cursor_show_to_grid")

                if self.activate_transform_pie or self.activate_shading_pie:
                        if self.activate_transform_pie:
                            column.prop(self, "cursor_set_transform_preset")



        if getattr(bpy.types, "MACHIN3_MT_snapping_pie", False):
            bb = b.box()
            bb.prop(self, 'snapping_pie_show', text="Snapping Pie", icon='TRIA_DOWN' if self.snapping_pie_show else 'TRIA_RIGHT', emboss=False)

            if self.snapping_pie_show:
                column = bb.column()

                column.prop(self, "snap_show_absolute_grid")
                column.prop(self, "snap_show_volume")



        if getattr(bpy.types, "MACHIN3_MT_workspace_pie", False):
            bb = b.box()
            bb.prop(self, 'workspace_pie_show', text="Workspace Pie", icon='TRIA_DOWN' if self.workspace_pie_show else 'TRIA_RIGHT', emboss=False)

            if self.workspace_pie_show:

                column = bb.column()
                column.label(text="It's your responsibility to pick workspace- and icon names that actually exist!", icon='ERROR')



                first = column.split(factor=0.2)
                first.separator()

                second = first.split(factor=0.25)
                second.separator()

                third = second.split(factor=0.33)

                col = third.column()
                col.label(text="Top")

                col.prop(self, 'pie_workspace_top_name', text="", icon='WORKSPACE')
                col.prop(self, 'pie_workspace_top_text', text="", icon='SMALL_CAPS')
                col.prop(self, 'pie_workspace_top_icon', text="", icon='IMAGE_DATA')

                fourth = third.split(factor=0.5)
                fourth.separator()

                fifth = fourth
                fifth.separator()



                first = column.split(factor=0.2)
                first.separator()

                second = first.split(factor=0.25)

                col = second.column()
                col.label(text="Top-Left")

                col.prop(self, 'pie_workspace_top_left_name', text="", icon='WORKSPACE')
                col.prop(self, 'pie_workspace_top_left_text', text="", icon='SMALL_CAPS')
                col.prop(self, 'pie_workspace_top_left_icon', text="", icon='IMAGE_DATA')

                third = second.split(factor=0.33)
                third.separator()

                fourth = third.split(factor=0.5)

                col = fourth.column()
                col.label(text="Top-Right")

                col.prop(self, 'pie_workspace_top_right_name', text="", icon='WORKSPACE')
                col.prop(self, 'pie_workspace_top_right_text', text="", icon='SMALL_CAPS')
                col.prop(self, 'pie_workspace_top_right_icon', text="", icon='IMAGE_DATA')

                fifth = fourth
                fifth.separator()



                first = column.split(factor=0.2)

                col = first.column()
                col.label(text="Left")

                col.prop(self, 'pie_workspace_left_name', text="", icon='WORKSPACE')
                col.prop(self, 'pie_workspace_left_text', text="", icon='SMALL_CAPS')
                col.prop(self, 'pie_workspace_left_icon', text="", icon='IMAGE_DATA')

                second = first.split(factor=0.25)
                second.separator()

                third = second.split(factor=0.33)

                col = third.column()
                col.label(text="")
                col.label(text="")
                col.operator('machin3.get_icon_name_help', text="Icon Names?", icon='INFO')

                fourth = third.split(factor=0.5)
                fourth.separator()

                fifth = fourth

                col = fifth.column()
                col.label(text="Right")

                col.prop(self, 'pie_workspace_right_name', text="", icon='WORKSPACE')
                col.prop(self, 'pie_workspace_right_text', text="", icon='SMALL_CAPS')
                col.prop(self, 'pie_workspace_right_icon', text="", icon='IMAGE_DATA')



                first = column.split(factor=0.2)
                first.separator()

                second = first.split(factor=0.25)

                col = second.column()
                col.label(text="Bottom-Left")

                col.prop(self, 'pie_workspace_bottom_left_name', text="", icon='WORKSPACE')
                col.prop(self, 'pie_workspace_bottom_left_text', text="", icon='SMALL_CAPS')
                col.prop(self, 'pie_workspace_bottom_left_icon', text="", icon='IMAGE_DATA')

                third = second.split(factor=0.33)
                third.separator()

                fourth = third.split(factor=0.5)

                col = fourth.column()
                col.label(text="Bottom-Right")

                col.prop(self, 'pie_workspace_bottom_right_name', text="", icon='WORKSPACE')
                col.prop(self, 'pie_workspace_bottom_right_text', text="", icon='SMALL_CAPS')
                col.prop(self, 'pie_workspace_bottom_right_icon', text="", icon='IMAGE_DATA')

                fifth = fourth
                fifth.separator()



                first = column.split(factor=0.2)
                first.separator()

                second = first.split(factor=0.25)
                second.separator()

                third = second.split(factor=0.33)

                col = third.column()
                col.label(text="Bottom")

                col.prop(self, 'pie_workspace_bottom_name', text="", icon='WORKSPACE')
                col.prop(self, 'pie_workspace_bottom_text', text="", icon='SMALL_CAPS')
                col.prop(self, 'pie_workspace_bottom_icon', text="", icon='IMAGE_DATA')

                fourth = third.split(factor=0.5)
                fourth.separator()

                fifth = fourth
                fifth.separator()



        if getattr(bpy.types, "MACHIN3_MT_tools_pie", False):
            bb = b.box()
            bb.prop(self, 'tools_pie_show', text="Tools Pie", icon='TRIA_DOWN' if self.tools_pie_show else 'TRIA_RIGHT', emboss=False)

            if self.tools_pie_show:
                split = bb.split(factor=0.5)

                col = split.column()
                col.prop(self, "tools_show_boxcutter_presets")
                col.prop(self, "tools_show_hardops_menu")

                col = split.column()
                col.prop(self, "tools_show_quick_favorites")
                col.prop(self, "tools_show_tool_bar")



        if not any([getattr(bpy.types, f'MACHIN3_{name}', False) for name in has_settings]):
            b.label(text="No tools or pie menus with settings have been activated.")

    def draw_keymaps(self, box):
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        from . registration import keys

        split = box.split()

        b = split.box()
        b.label(text="Tools")

        if not self.draw_tool_keymaps(kc, keys, b):
            b.label(text="No keymappings available, because none of the tools have been activated.")


        b = split.box()
        b.label(text="Pie Menus")

        if not self.draw_pie_keymaps(kc, keys, b):
            b.label(text="No keymappings created, because none of the pies have been activated.")

    def draw_about(self, box):
        global decalmachine, meshmachine, punchit

        if decalmachine is None:
            decalmachine = get_addon('DECALmachine')[0]

        if meshmachine is None:
            meshmachine = get_addon('MESHmachine')[0]

        if punchit is None:
            punchit = get_addon('PUNCHit')[0]

        column = box.column(align=True)

        row = column.row(align=True)

        row.scale_y = 1.5
        row.operator("wm.url_open", text='MACHIN3tools', icon='INFO').url = 'https://machin3.io/MACHIN3tools/'
        row.operator("wm.url_open", text='MACHINƎ.io', icon='WORLD').url = 'https://machin3.io'
        row.operator("wm.url_open", text='blenderartists', icon_value=get_icon('blenderartists')).url = 'https://blenderartists.org/t/machin3tools/1135716/'

        row = column.row(align=True)
        row.scale_y = 1.5
        row.operator("wm.url_open", text='Patreon', icon_value=get_icon('patreon')).url = 'https://patreon.com/machin3'
        row.operator("wm.url_open", text='Twitter', icon_value=get_icon('twitter')).url = 'https://twitter.com/machin3io'
        row.operator("wm.url_open", text='Youtube', icon_value=get_icon('youtube')).url = 'https://www.youtube.com/c/MACHIN3/'
        row.operator("wm.url_open", text='Artstation', icon_value=get_icon('artstation')).url = 'https://www.artstation.com/machin3'

        column.separator()

        row = column.row(align=True)
        row.scale_y = 1.5
        row.operator("wm.url_open", text='DECALmachine', icon_value=get_icon('save' if decalmachine else 'cancel_grey')).url = 'https://decal.machin3.io'
        row.operator("wm.url_open", text='MESHmachine', icon_value=get_icon('save' if meshmachine else 'cancel_grey')).url = 'https://mesh.machin3.io'
        row.operator("wm.url_open", text='PUNCHit', icon_value=get_icon('save' if punchit else 'cancel_grey')).url = 'https://machin3.io/PUNCHit'

    def draw_tool_keymaps(self, kc, keysdict, layout):
        drawn = False

        for name in keysdict:
            if "PIE" not in name:
                keylist = keysdict.get(name)

                if draw_keymap_items(kc, name, keylist, layout):
                    drawn = True

        return drawn

    def draw_pie_keymaps(self, kc, keysdict, layout):
        drawn = False

        for name in keysdict:
            if "PIE" in name:
                keylist = keysdict.get(name)

                if draw_keymap_items(kc, name, keylist, layout):
                    drawn = True

        return drawn
