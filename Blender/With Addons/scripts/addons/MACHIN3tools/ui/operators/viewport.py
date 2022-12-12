import bpy
import bmesh
from bpy.props import EnumProperty, BoolProperty
from ... utils.view import reset_viewport
from ... utils.math import average_locations
from ... items import view_axis_items


class ViewAxis(bpy.types.Operator):
    bl_idname = "machin3.view_axis"
    bl_label = "View Axis"
    bl_options = {'REGISTER'}

    axis: EnumProperty(name="Axis", items=view_axis_items, default="FRONT")

    @classmethod
    def description(cls, context, properties):
        m3 = context.scene.M3

        if context.mode == 'OBJECT':
            selection = 'Object'
        elif context.mode == 'EDIT_MESH':
            selection = 'Verts' if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False) else 'Edges' if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, True, False) else 'Faces' if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True) else 'Elements'
        else:
            selection = 'Elements'

        if m3.custom_views_local:
            return "Align Custom View to Active Object\nALT: Align View to Active %s" % (selection)
        if m3.custom_views_cursor:
            return "Align Custom View to Cursor\nALT: Align View to Active %s" % (selection)
        else:
            return "Align View to World\nALT: Align View to Active to Active %s" % (selection)

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

    def invoke(self, context, event):
        m3 = context.scene.M3
        r3d = context.space_data.region_3d

        if event.alt:
            bpy.ops.view3d.view_axis(type=self.axis, align_active=True)

            r3d.view_perspective = 'ORTHO'

        elif m3.custom_views_local or m3.custom_views_cursor:
            mx = context.scene.cursor.matrix if m3.custom_views_cursor else context.active_object.matrix_world if m3.custom_views_local and context.active_object else None

            if not mx:
                context.scene.M3.custom_views_local = False
                bpy.ops.view3d.view_axis(type=self.axis, align_active=False)
                return {'FINISHED'}

            loc, rot, _ = mx.decompose()
            rot = self.create_view_rotation(rot, self.axis)

            if context.mode == 'EDIT_MESH':
                bm = bmesh.from_edit_mesh(context.active_object.data)

                verts = [v for v in bm.verts if v.select]

                if verts:
                    loc = context.active_object.matrix_world @ average_locations([v.co for v in verts])

            r3d.view_location = loc
            r3d.view_rotation = rot

            r3d.view_perspective = 'ORTHO'

        else:
            bpy.ops.view3d.view_axis(type=self.axis, align_active=False)

        return {'FINISHED'}

    def create_view_rotation(self, rot, axis):

        if self.axis == 'FRONT':
            rmx = rot.to_matrix()
            rotated = rot.to_matrix()

            rotated.col[1] = rmx.col[2]
            rotated.col[2] = -rmx.col[1]

            rot = rotated.to_quaternion()

        elif self.axis == 'BACK':
            rmx = rot.to_matrix()
            rotated = rot.to_matrix()

            rotated.col[0] = -rmx.col[0]
            rotated.col[1] = rmx.col[2]
            rotated.col[2] = rmx.col[1]

            rot = rotated.to_quaternion()

        elif self.axis == 'RIGHT':
            rmx = rot.to_matrix()
            rotated = rot.to_matrix()

            rotated.col[0] = rmx.col[1]
            rotated.col[1] = rmx.col[2]
            rotated.col[2] = rmx.col[0]

            rot = rotated.to_quaternion()

        elif self.axis == 'LEFT':
            rmx = rot.to_matrix()
            rotated = rot.to_matrix()

            rotated.col[0] = -rmx.col[1]
            rotated.col[1] = rmx.col[2]
            rotated.col[2] = -rmx.col[0]

            rot = rotated.to_quaternion()

        elif self.axis == 'BOTTOM':
            rmx = rot.to_matrix()
            rotated = rot.to_matrix()

            rotated.col[1] = -rmx.col[1]
            rotated.col[2] = -rmx.col[2]

            rot = rotated.to_quaternion()

        return rot


class MakeCamActive(bpy.types.Operator):
    bl_idname = "machin3.make_cam_active"
    bl_label = "Make Active"
    bl_description = "Make selected Camera active."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active = context.active_object
        if active:
            return active.type == "CAMERA"

    def execute(self, context):
        context.scene.camera = context.active_object

        return {'FINISHED'}


class SmartViewCam(bpy.types.Operator):
    bl_idname = "machin3.smart_view_cam"
    bl_label = "Smart View Cam"
    bl_description = "Default: View Active Scene Camera\nNo Camera in the Scene: Create Camera from View\nCamera Selected: Make Selected Camera active and view it.\nAlt + Click: Create Camera from current View."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

    def invoke(self, context, event):
        cams = [obj for obj in context.scene.objects if obj.type == "CAMERA"]
        view = context.space_data

        if not cams or event.alt:
            bpy.ops.object.camera_add()
            context.scene.camera = context.active_object
            bpy.ops.view3d.camera_to_view()

        else:
            active = context.active_object

            if active:
                if active in context.selected_objects and active.type == "CAMERA":
                    context.scene.camera = active

            if view.region_3d.view_perspective == 'CAMERA':
                bpy.ops.view3d.view_persportho()
                bpy.ops.view3d.view_persportho()

            bpy.ops.view3d.view_camera()
            bpy.ops.view3d.view_center_camera()

        return {'FINISHED'}


class NextCam(bpy.types.Operator):
    bl_idname = "machin3.next_cam"
    bl_label = "MACHIN3: Next Cam"
    bl_options = {'REGISTER', 'UNDO'}

    previous: BoolProperty(name="Previous", default=False)

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D' and context.space_data.region_3d.view_perspective == 'CAMERA'

    def execute(self, context):
        cams = sorted([obj for obj in context.scene.objects if obj.type == "CAMERA"], key=lambda x: x.name)

        if len(cams) > 1:
            active = context.scene.camera


            idx = cams.index(active)

            if not self.previous:
                idx = 0 if idx == len(cams) - 1 else idx + 1

            else:
                idx = len(cams) - 1 if idx == 0 else idx - 1


            newcam = cams[idx]

            context.scene.camera = newcam

            bpy.ops.view3d.view_center_camera()


        return {'FINISHED'}


class ToggleCamPerspOrtho(bpy.types.Operator):
    bl_idname = "machin3.toggle_cam_persportho"
    bl_label = "MACHIN3: Toggle Camera Perspective/Ortho"
    bl_description = "Toggle Active Scene Camera Perspective/Ortho"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.camera

    def execute(self, context):
        cam = context.scene.camera

        if cam.data.type == "PERSP":
            cam.data.type = "ORTHO"
        else:
            cam.data.type = "PERSP"

        return {'FINISHED'}


toggledprefs = False


class ToggleViewPerspOrtho(bpy.types.Operator):
    bl_idname = "machin3.toggle_view_persportho"
    bl_label = "MACHIN3: Toggle View Perspective/Ortho"
    bl_description = "Toggle Viewport Perspective/Ortho"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global toggledprefs

        view = context.space_data
        viewtype = view.region_3d.view_perspective
        prefs = context.preferences.inputs

        if viewtype == "PERSP" and prefs.use_auto_perspective:
            prefs.use_auto_perspective = False
            toggledprefs = True

        if viewtype == "ORTHO" and toggledprefs:
            prefs.use_auto_perspective = True

        bpy.ops.view3d.view_persportho()

        return {'FINISHED'}


class ToggleOrbitMethod(bpy.types.Operator):
    bl_idname = "machin3.toggle_orbit_method"
    bl_label = "MACHIN3: Toggle Orbit Method"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        if context.preferences.inputs.view_rotate_method == 'TURNTABLE':
            return "Change Orbit Method from Turntable to Trackball"
        return "Change Orbit Method from Trackball to Turntable"

    def execute(self, context):
        if context.preferences.inputs.view_rotate_method == 'TURNTABLE':
            context.preferences.inputs.view_rotate_method = 'TRACKBALL'
        else:
            context.preferences.inputs.view_rotate_method = 'TURNTABLE'

        return {'FINISHED'}


class ToggleOrbitSelection(bpy.types.Operator):
    bl_idname = "machin3.toggle_orbit_selection"
    bl_label = "MACHIN3: Toggle Orbit Selection"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        if context.preferences.inputs.use_rotate_around_active:
            return "Disable Orbit around Selection"
        return "Enable Orbit around Selection"

    def execute(self, context):
        context.preferences.inputs.use_rotate_around_active = not context.preferences.inputs.use_rotate_around_active
        return {'FINISHED'}


class ResetViewport(bpy.types.Operator):
    bl_idname = "machin3.reset_viewport"
    bl_label = "MACHIN3: Reset Viewport"
    bl_description = "Perfectly align the viewport with the Y axis, looking into Y+"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

    def execute(self, context):
        context.space_data.region_3d.is_orthographic_side_view = False
        context.space_data.region_3d.view_perspective = 'PERSP'

        reset_viewport(context)

        return {'FINISHED'}
