import bpy
import bmesh
from mathutils import Vector, Quaternion
from ... utils.math import get_center_between_verts, average_locations, create_rotation_matrix_from_vertex, create_rotation_matrix_from_edge, create_rotation_matrix_from_face
from ... utils.math import get_loc_matrix, get_rot_matrix, get_sca_matrix
from ... utils.scene import set_cursor
from ... utils.ui import popup_message
from ... utils.registration import get_prefs
from ... utils.object import compensate_children


cursor = None


class CursorToOrigin(bpy.types.Operator):
    bl_idname = "machin3.cursor_to_origin"
    bl_label = "MACHIN3: Cursor to Origin"
    bl_description = "Reset Cursor to World Origin\nALT: Only reset Cursor Location\nCTRL: Only reset Cursor Rotation"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        if event.alt and event.ctrl:
            popup_message("Hold down ATL, CTRL or neither, not both!", title="Invalid Modifier Keys")
            return {'CANCELLED'}

        if not context.space_data.overlay.show_cursor and not context.scene.M3.draw_cursor_axes:
            context.space_data.overlay.show_cursor = True

        cmx = context.scene.cursor.matrix

        set_cursor(location=cmx.to_translation() if event.ctrl else Vector(), rotation=cmx.to_quaternion() if event.alt else Quaternion())

        if get_prefs().cursor_set_transform_preset:
            global cursor

            if cursor is not None:
                bpy.ops.machin3.set_transform_preset(pivot=cursor[0], orientation=cursor[1])
                cursor = None

        return {'FINISHED'}


class CursorToSelected(bpy.types.Operator):
    bl_idname = "machin3.cursor_to_selected"
    bl_label = "MACHIN3: Cursor to Selected"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        if context.mode == 'OBJECT':
            return "Align Cursor with Selected Object(s)\nALT: Only set Cursor Location\nCTRL: Only set Cursor Rotation"

        elif context.mode == 'EDIT_MESH':
            return "Align Cursor with Vert/Edge/Face\nALT: Only set Cursor Location\nCTRL: Only set Cursor Rotation"

    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH' and tuple(context.scene.tool_settings.mesh_select_mode) in [(True, False, False), (False, True, False), (False, False, True)]:
            bm = bmesh.from_edit_mesh(context.active_object.data)
            return [v for v in bm.verts if v.select]
        return context.active_object or context.selected_objects

    def invoke(self, context, event):

        if not context.space_data.overlay.show_cursor and not context.scene.M3.draw_cursor_axes:
            context.space_data.overlay.show_cursor = True

        active = context.active_object
        sel = [obj for obj in context.selected_objects if obj != active]
        cmx = context.scene.cursor.matrix

        if sel and not active:
            context.view_layer.objects.active = sel[0]
            sel.remove(active)

        if event.alt and event.ctrl:
            popup_message("Hold down ATL, CTRL or neither, not both!", title="Invalid Modifier Keys")
            return {'CANCELLED'}

        if context.mode == 'OBJECT' and active and (not sel or active.M3.is_group_empty):
            self.cursor_to_active_object(active, cmx, only_location=event.alt, only_rotation=event.ctrl)

            if get_prefs().activate_transform_pie and get_prefs().cursor_set_transform_preset:
                self.set_cursor_transform_preset(context)

            return {'FINISHED'}

        elif context.mode == 'EDIT_MESH':
            self.cursor_to_editmesh(context, active, cmx, only_location=event.alt, only_rotation=event.ctrl)

            if get_prefs().activate_transform_pie and get_prefs().cursor_set_transform_preset:
                self.set_cursor_transform_preset(context)

            return {'FINISHED'}

        bpy.ops.view3d.snap_cursor_to_selected()

        return {'FINISHED'}

    def set_cursor_transform_preset(self, context):
        global cursor

        pivot = context.scene.tool_settings.transform_pivot_point
        orientation = context.scene.transform_orientation_slots[0].type

        if pivot != 'CURSOR' and orientation != 'CURSOR':
            cursor = (context.scene.tool_settings.transform_pivot_point, context.scene.transform_orientation_slots[0].type)

        bpy.ops.machin3.set_transform_preset(pivot='CURSOR', orientation='CURSOR')

    def cursor_to_editmesh(self, context, active, cmx, only_location, only_rotation):
        bm = bmesh.from_edit_mesh(active.data)
        mx = active.matrix_world

        if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):
            verts = [v for v in bm.verts if v.select]

            co = average_locations([v.co for v in verts])

            loc = mx @ co

            v = bm.select_history[-1] if bm.select_history else verts[0]
            rot = create_rotation_matrix_from_vertex(active, v)

        elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, True, False):
            edges = [e for e in bm.edges if e.select]
            center = average_locations([get_center_between_verts(*e.verts) for e in edges])

            loc = mx @ center

            e = bm.select_history[-1] if bm.select_history else edges[0]
            rot = create_rotation_matrix_from_edge(active, e)

        elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
            faces = [f for f in bm.faces if f.select]

            center = average_locations([f.calc_center_median_weighted() for f in faces])

            loc = mx @ center

            f = bm.faces.active if bm.faces.active and bm.faces.active in faces else faces[0]
            rot = create_rotation_matrix_from_face(mx, f)

        set_cursor(location=cmx.to_translation() if only_rotation else loc, rotation=cmx.to_quaternion() if only_location else rot.to_quaternion())

    def cursor_to_active_object(self, active, cmx, only_location, only_rotation):
        mx = active.matrix_world
        loc, rot, _ = mx.decompose()

        set_cursor(location=cmx.to_translation() if only_rotation else loc, rotation=cmx.to_quaternion() if only_location else rot)


class SelectedToCursor(bpy.types.Operator):
    bl_idname = "machin3.selected_to_cursor"
    bl_label = "MACHIN3: Selected To Cursor"
    bl_description = "Transform Selected Objects to Cursor\nALT: Only set Location\nCTRL: Only set Rotation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return context.selected_objects or context.active_object

    def invoke(self, context, event):
        sel = context.selected_objects

        if context.active_object and context.active_object.M3.is_group_empty and context.active_object.children:
            sel = [context.active_object]

        elif context.active_object and context.active_object not in sel:
            sel.append(context.active_object)


        cmx = context.scene.cursor.matrix

        for obj in sel:
            loc, rot, sca = obj.matrix_world.decompose()

            if event.alt:
                mx = get_loc_matrix(cmx.to_translation()) @ get_rot_matrix(rot) @ get_sca_matrix(sca)

            elif event.ctrl:
                mx = get_loc_matrix(loc) @ get_rot_matrix(cmx.to_quaternion()) @ get_sca_matrix(sca)

            else:
                mx = get_loc_matrix(cmx.to_translation()) @ get_rot_matrix(cmx.to_quaternion()) @ get_sca_matrix(sca)

            if obj.children and context.scene.tool_settings.use_transform_skip_children:
                compensate_children(obj, obj.matrix_world, mx)

            obj.matrix_world = mx

        return {'FINISHED'}
