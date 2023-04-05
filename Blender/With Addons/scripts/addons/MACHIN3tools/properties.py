import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty, CollectionProperty, PointerProperty, EnumProperty, FloatProperty, FloatVectorProperty
from mathutils import Matrix
import bmesh
from . utils.math import flatten_matrix
from . utils.world import get_world_output
from . utils.system import abspath
from . utils.registration import get_prefs, get_addon_prefs
from . utils.tools import get_active_tool
from . utils.light import adjust_lights_for_rendering, get_area_light_poll
from . utils.view import sync_light_visibility
from . items import eevee_preset_items, align_mode_items, render_engine_items, cycles_device_items, driver_limit_items, axis_items, driver_transform_items, driver_space_items, bc_orientation_items, shading_light_items




class HistoryObjectsCollection(bpy.types.PropertyGroup):
    name: StringProperty()
    obj: PointerProperty(name="History Object", type=bpy.types.Object)


class HistoryUnmirroredCollection(bpy.types.PropertyGroup):
    name: StringProperty()
    obj: PointerProperty(name="History Unmirror", type=bpy.types.Object)


class HistoryEpochCollection(bpy.types.PropertyGroup):
    name: StringProperty()
    objects: CollectionProperty(type=HistoryObjectsCollection)
    unmirrored: CollectionProperty(type=HistoryUnmirroredCollection)



selected = []


class M3SceneProperties(bpy.types.PropertyGroup):
    def update_xray(self, context):
        x = (self.pass_through, self.show_edit_mesh_wire)
        shading = context.space_data.shading

        shading.show_xray = True if any(x) else False

        if self.show_edit_mesh_wire:
            shading.xray_alpha = 0.1

        elif self.pass_through:
            shading.xray_alpha = 1 if context.active_object and context.active_object.type == "MESH" else 0.5

    def update_uv_sync_select(self, context):
        ts = context.scene.tool_settings
        ts.use_uv_select_sync = self.uv_sync_select

        global selected
        active = context.active_object

        if ts.use_uv_select_sync:
            bpy.ops.mesh.select_all(action='DESELECT')

            bm = bmesh.from_edit_mesh(active.data)
            bm.normal_update()
            bm.verts.ensure_lookup_table()

            if selected:
                for v in bm.verts:
                    if v.index in selected:
                        v.select_set(True)

            bm.select_flush(True)

            bmesh.update_edit_mesh(active.data)


        else:
            bm = bmesh.from_edit_mesh(active.data)
            bm.normal_update()
            bm.verts.ensure_lookup_table()

            selected = [v.index for v in bm.verts if v.select]

            bpy.ops.mesh.select_all(action="SELECT")

            mode = tuple(ts.mesh_select_mode)

            if mode == (False, True, False):
                ts.uv_select_mode = "EDGE"

            else:
                ts.uv_select_mode = "VERTEX"

    def update_show_cavity(self, context):
        t = (self.show_cavity, self.show_curvature)
        shading = context.space_data.shading

        shading.show_cavity = True if any(t) else False

        if t == (True, True):
            shading.cavity_type = "BOTH"

        elif t == (True, False):
            shading.cavity_type = "WORLD"

        elif t == (False, True):
            shading.cavity_type = "SCREEN"

    def update_grouppro_dotnames(self, context):
        gpcols = [col for col in bpy.data.collections if col.created_with_gp]

        for col in gpcols:
            if self.grouppro_dotnames:
                if not col.name.startswith("."):
                    col.name = ".%s" % col.name

            else:
                if col.name.startswith("."):
                    col.name = col.name[1:]

    pass_through: BoolProperty(name="Pass Through", default=False, update=update_xray)
    show_edit_mesh_wire: BoolProperty(name="Show Edit Mesh Wireframe", default=False, update=update_xray)
    uv_sync_select: BoolProperty(name="Synce Selection", default=False, update=update_uv_sync_select)

    show_cavity: BoolProperty(name="Cavity", default=True, update=update_show_cavity)
    show_curvature: BoolProperty(name="Curvature", default=False, update=update_show_cavity)

    focus_history: CollectionProperty(type=HistoryEpochCollection)

    grouppro_dotnames: BoolProperty(name=".dotname GroupPro collections", default=False, update=update_grouppro_dotnames)

    def update_eevee_preset(self, context):
        eevee = context.scene.eevee
        shading = context.space_data.shading

        if self.eevee_preset == 'NONE':
            eevee.use_ssr = False
            eevee.use_gtao = False
            eevee.use_bloom = False
            eevee.use_volumetric_lights = False

            if self.eevee_preset_set_use_scene_lights:
                shading.use_scene_lights = False

            if self.eevee_preset_set_use_scene_world:
                shading.use_scene_world = False

            if context.scene.render.engine == 'BLENDER_EEVEE':
                if self.eevee_preset_set_use_scene_lights:
                    shading.use_scene_lights_render = False

                if self.eevee_preset_set_use_scene_world:
                    shading.use_scene_world_render = False

        elif self.eevee_preset == 'LOW':
            eevee.use_ssr = True
            eevee.use_ssr_halfres = True
            eevee.use_ssr_refraction = False
            eevee.use_gtao = True
            eevee.use_bloom = False
            eevee.use_volumetric_lights = False

            if self.eevee_preset_set_use_scene_lights:
                shading.use_scene_lights = True

            if self.eevee_preset_set_use_scene_world:
                shading.use_scene_world = False

            if context.scene.render.engine == 'BLENDER_EEVEE':
                if self.eevee_preset_set_use_scene_lights:
                    shading.use_scene_lights_render = True

                if self.eevee_preset_set_use_scene_world:
                    shading.use_scene_world_render = False

        elif self.eevee_preset == 'HIGH':
            eevee.use_ssr = True
            eevee.use_ssr_halfres = False
            eevee.use_ssr_refraction = True
            eevee.use_gtao = True
            eevee.use_bloom = True
            eevee.use_volumetric_lights = False

            if self.eevee_preset_set_use_scene_lights:
                shading.use_scene_lights = True

            if self.eevee_preset_set_use_scene_world:
                shading.use_scene_world = False

            if context.scene.render.engine == 'BLENDER_EEVEE':
                if self.eevee_preset_set_use_scene_lights:
                    shading.use_scene_lights_render = True

                if self.eevee_preset_set_use_scene_world:
                    shading.use_scene_world_render = False

        elif self.eevee_preset == 'ULTRA':
            eevee.use_ssr = True
            eevee.use_ssr_halfres = False
            eevee.use_ssr_refraction = True
            eevee.use_gtao = True
            eevee.use_bloom = True
            eevee.use_volumetric_lights = True

            if self.eevee_preset_set_use_scene_lights:
                shading.use_scene_lights = True

            if context.scene.render.engine == 'BLENDER_EEVEE':
                if self.eevee_preset_set_use_scene_lights:
                    shading.use_scene_lights_render = True

            if self.eevee_preset_set_use_scene_lights:
                world = context.scene.world
                if world:
                    shading.use_scene_world = True

                    if context.scene.render.engine == 'BLENDER_EEVEE':
                        shading.use_scene_world_render = True

                    output = get_world_output(world)
                    links = output.inputs[1].links

                    if not links:
                        tree = world.node_tree

                        volume = tree.nodes.new('ShaderNodeVolumePrincipled')
                        tree.links.new(volume.outputs[0], output.inputs[1])

                        volume.inputs[2].default_value = 0.1
                        volume.location = (-200, 200)

    def update_eevee_gtao_factor(self, context):
        context.scene.eevee.gtao_factor = self.eevee_gtao_factor

    def update_eevee_bloom_intensity(self, context):
        context.scene.eevee.bloom_intensity = self.eevee_bloom_intensity

    def update_render_engine(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        context.scene.render.engine = self.render_engine

        if get_prefs().activate_render and get_prefs().activate_shading_pie and get_prefs().render_adjust_lights_on_render and get_area_light_poll() and self.adjust_lights_on_render:
            last = self.adjust_lights_on_render_last

            debug = False

            if last in ['NONE', 'INCREASE'] and self.render_engine == 'CYCLES':
                self.adjust_lights_on_render_last = 'DECREASE'

                if debug:
                    print("decreasing on switch to cycies engine")

                adjust_lights_for_rendering(mode='DECREASE')

            elif last == 'DECREASE' and self.render_engine == 'BLENDER_EEVEE':
                self.adjust_lights_on_render_last = 'INCREASE'

                if debug:
                    print("increasing on switch to eevee engine")

                adjust_lights_for_rendering(mode='INCREASE')

        if get_prefs().activate_render and get_prefs().render_sync_light_visibility:
            sync_light_visibility(context.scene)

    def update_cycles_device(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        context.scene.cycles.device = self.cycles_device

    def update_shading_light(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        shading = context.space_data.shading
        shading.light = self.shading_light

        if self.use_flat_shadows:
            shading.show_shadows = shading.light == 'FLAT'

    def update_use_flat_shadows(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        shading = context.space_data.shading

        if shading.light == 'FLAT':
            shading.show_shadows = self.use_flat_shadows

    def update_custom_views_local(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        if self.custom_views_local and self.custom_views_cursor:
            self.avoid_update = True
            self.custom_views_cursor = False

        context.space_data.overlay.show_ortho_grid = not self.custom_views_local

        if get_prefs().custom_views_use_trackball:
            context.preferences.inputs.view_rotate_method = 'TRACKBALL' if self.custom_views_local else 'TURNTABLE'

        if get_prefs().activate_transform_pie and get_prefs().custom_views_set_transform_preset:
            bpy.ops.machin3.set_transform_preset(pivot='MEDIAN_POINT', orientation='LOCAL' if self.custom_views_local else 'GLOBAL')

    def update_custom_views_cursor(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        if self.custom_views_cursor and self.custom_views_local:
            self.avoid_update = True
            self.custom_views_local = False

        context.space_data.overlay.show_ortho_grid = not self.custom_views_cursor

        if get_prefs().custom_views_use_trackball:
            context.preferences.inputs.view_rotate_method = 'TRACKBALL' if self.custom_views_cursor else 'TURNTABLE'

        if 'machin3.tool_hyper_cursor' not in get_active_tool(context).idname:

            if get_prefs().activate_transform_pie and get_prefs().custom_views_set_transform_preset:
                bpy.ops.machin3.set_transform_preset(pivot='CURSOR' if self.custom_views_cursor else 'MEDIAN_POINT', orientation='CURSOR' if self.custom_views_cursor else 'GLOBAL')

    def update_enforce_hide_render(self, context):
        from . ui.operators import shading

        for _, name in shading.render_visibility:
            obj = bpy.data.objects.get(name)

            if obj:
                obj.hide_set(obj.visible_get())
                


    eevee_preset: EnumProperty(name="Eevee Preset", description="Eevee Quality Presets", items=eevee_preset_items, default='NONE', update=update_eevee_preset)
    eevee_preset_set_use_scene_lights: BoolProperty(name="Set Use Scene Lights", description="Set Use Scene Lights when changing Eevee Preset", default=False)
    eevee_preset_set_use_scene_world: BoolProperty(name="Set Use Scene World", description="Set Use Scene World when changing Eevee Preset", default=False)

    eevee_gtao_factor: FloatProperty(name="Factor", default=1, min=0, step=0.1, update=update_eevee_gtao_factor)
    eevee_bloom_intensity: FloatProperty(name="Intensity", default=0.05, min=0, step=0.1, update=update_eevee_bloom_intensity)

    render_engine: EnumProperty(name="Render Engine", description="Render Engine", items=render_engine_items, default='BLENDER_EEVEE', update=update_render_engine)
    cycles_device: EnumProperty(name="Render Device", description="Render Device", items=cycles_device_items, default='CPU', update=update_cycles_device)

    shading_light: EnumProperty(name="Lighting Method", description="Lighting Method for Solid/Texture Viewport Shading", items=shading_light_items, default='MATCAP', update=update_shading_light)
    use_flat_shadows: BoolProperty(name="Use Flat Shadows", description="Use Shadows when in Flat Lighting", default=True, update=update_use_flat_shadows)

    draw_axes_size: FloatProperty(name="Draw_Axes Size", default=0.1, min=0)
    draw_axes_alpha: FloatProperty(name="Draw Axes Alpha", default=0.5, min=0, max=1)
    draw_axes_screenspace: BoolProperty(name="Draw Axes in Screen Space", default=True)

    draw_active_axes: BoolProperty(name="Draw Active Axes", description="Draw Active's Object Axes", default=False)
    draw_cursor_axes: BoolProperty(name="Draw Cursor Axes", description="Draw Cursor's Axes", default=False)

    adjust_lights_on_render: BoolProperty(name="Adjust Lights when Rendering", description="Adjust Lights Area Lights when Rendering, to better match Eevee and Cycles", default=False)
    adjust_lights_on_render_divider: FloatProperty(name="Divider used to calculate Cycles Light Strength from Eeeve Light Strength", default=4, min=1)
    adjust_lights_on_render_last: StringProperty(name="Last Light Adjustment", default='NONE')
    is_light_decreased_by_handler: BoolProperty(name="Have Lights been decreased by the init render handler?", default=False)

    enforce_hide_render: BoolProperty(name="Enforce hide_render setting when Viewport Rendering", description="Enfore hide_render setting for objects when Viewport Rendering", default=True, update=update_enforce_hide_render)



    custom_views_local: BoolProperty(name="Custom Local Views", description="Use Custom Views, based on the active object's orientation", default=False, update=update_custom_views_local)
    custom_views_cursor: BoolProperty(name="Custom Cursor Views", description="Use Custom Views, based on the cursor's orientation", default=False, update=update_custom_views_cursor)



    align_mode: EnumProperty(name="Align Mode", items=align_mode_items, default="VIEW")



    show_smart_drive: BoolProperty(name="Show Smart Drive")

    driver_start: FloatProperty(name="Driver Start Value", precision=3)
    driver_end: FloatProperty(name="Driver End Value", precision=3)
    driver_axis: EnumProperty(name="Driver Axis", items=axis_items, default='X')
    driver_transform: EnumProperty(name="Driver Transform", items=driver_transform_items, default='LOCATION')
    driver_space: EnumProperty(name="Driver Space", items=driver_space_items, default='AUTO')

    driven_start: FloatProperty(name="Driven Start Value", precision=3)
    driven_end: FloatProperty(name="Driven End Value", precision=3)
    driven_axis: EnumProperty(name="Driven Axis", items=axis_items, default='X')
    driven_transform: EnumProperty(name="Driven Transform", items=driver_transform_items, default='LOCATION')
    driven_limit: EnumProperty(name="Driven Lmit", items=driver_limit_items, default='BOTH')



    def update_unity_export_path(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        path = self.unity_export_path

        if path:
            if not path.endswith('.fbx'):
                path += '.fbx'

            self.avoid_update = True
            self.unity_export_path = abspath(path)

    show_unity: BoolProperty(name="Show Unity")

    unity_export: BoolProperty(name="Export to Unity", description="Enable to do the actual FBX export\nLeave it off to only prepare the Model")
    unity_export_path: StringProperty(name="Unity Export Path", subtype='FILE_PATH', update=update_unity_export_path)
    unity_triangulate: BoolProperty(name="Triangulate before exporting", description="Add Triangulate Modifier to the end of every object's stack", default=False)



    def update_bcorientation(self, context):
        bcprefs = get_addon_prefs('BoxCutter')

        if self.bcorientation == 'LOCAL':
            bcprefs.behavior.orient_method = 'LOCAL'
        elif self.bcorientation == 'NEAREST':
            bcprefs.behavior.orient_method = 'NEAREST'
        elif self.bcorientation == 'LONGEST':
            bcprefs.behavior.orient_method = 'TANGENT'

    bcorientation: EnumProperty(name="BoxCutter Orientation", items=bc_orientation_items, default='LOCAL', update=update_bcorientation)



    def update_group_select(self, context):

        if not self.group_select:
            all_empties = [obj for obj in context.selected_objects if obj.M3.is_group_empty]
            top_level = [obj for obj in all_empties if obj.parent not in all_empties]

            for obj in context.selected_objects:
                if obj not in top_level:
                    obj.select_set(False)

    def update_group_recursive_select(self, context):

        if not self.group_recursive_select:
            all_empties = [obj for obj in context.selected_objects if obj.M3.is_group_empty]
            top_level = [obj for obj in all_empties if obj.parent not in all_empties]

            for obj in context.selected_objects:
                if obj not in top_level:
                    obj.select_set(False)

    def update_group_hide(self, context):
        empties = [obj for obj in context.visible_objects if obj.M3.is_group_empty]

        for e in empties:
            if e == context.active_object or not context.scene.M3.group_hide:
                e.show_name = True
                e.empty_display_size = e.M3.group_size

            else:
                e.show_name = False

                if round(e.empty_display_size, 4) != 0.0001:
                    e.M3.group_size = e.empty_display_size

                e.empty_display_size = 0.0001

    def update_affect_only_group_origin(self, context):
        if self.affect_only_group_origin:
            context.scene.tool_settings.use_transform_skip_children = True
            self.group_select = False

        else:
            context.scene.tool_settings.use_transform_skip_children = False
            self.group_select = True

    show_group: BoolProperty(name="Show Group")

    group_select: BoolProperty(name="Auto Select Groups", description="Automatically select the entire Group, when its Empty is made active", default=True, update=update_group_select)
    group_recursive_select: BoolProperty(name="Recursively Select Groups", description="Recursively select entire Group Hierarchies down", default=True, update=update_group_recursive_select)
    group_hide: BoolProperty(name="Hide Group Empties in 3D View", description="Hide Group Empties in 3D View to avoid Clutter", default=True, update=update_group_hide)

    show_group_select: BoolProperty(name="Show Auto Select Toggle in main Object Context Menu", default=True)
    show_group_recursive_select: BoolProperty(name="Show Recursive Selection Toggle in main Object Context Menu", default=True)
    show_group_hide: BoolProperty(name="Show Group Hide Toggle in main Object Context Menu", default=True)

    affect_only_group_origin: BoolProperty(name="Transform only the Group Origin(Empty)", description='Transform the Group Origin(Empty) only, disable Group Auto-Select and enable "affect Parents only"', default=False, update=update_affect_only_group_origin)



    show_assetbrowser_tools: BoolProperty(name="Show Assetbrowser Tools")
    asset_collect_path: StringProperty(name="Collect Path", subtype="DIR_PATH", default="")


    show_extrude: BoolProperty(name="Show Extrude")



    avoid_update: BoolProperty()


class M3ObjectProperties(bpy.types.PropertyGroup):
    unity_exported: BoolProperty(name="Exported to Unity")

    pre_unity_export_mx: FloatVectorProperty(name="Pre-Unity-Export Matrix", subtype="MATRIX", size=16, default=flatten_matrix(Matrix()))
    pre_unity_export_mesh: PointerProperty(name="Pre-Unity-Export Mesh", type=bpy.types.Mesh)
    pre_unity_export_armature: PointerProperty(name="Pre-Unity-Export Armature", type=bpy.types.Armature)

    is_group_empty: BoolProperty()
    is_group_object: BoolProperty()
    group_size: FloatProperty(default=0.2)

    smooth_angle: FloatProperty(name="Smooth Angle", default=30)
    has_smoothed: BoolProperty(name="Has been smoothed", default=False)


    draw_axes: BoolProperty(name="Draw Axes", default=False)



    avoid_update: BoolProperty()
