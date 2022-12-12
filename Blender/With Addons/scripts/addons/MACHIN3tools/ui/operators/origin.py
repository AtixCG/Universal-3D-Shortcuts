import bpy
import bmesh
from ... utils.math import get_loc_matrix, get_rot_matrix, get_sca_matrix, create_rotation_matrix_from_vertex, create_rotation_matrix_from_edge, get_center_between_verts, create_rotation_matrix_from_face
from ... utils.math import average_locations
from ... utils.ui import popup_message
from ... utils.object import set_obj_origin
from ... utils.registration import get_addon


decalmachine = None
meshmachine = None


class OriginToActive(bpy.types.Operator):
    bl_idname = "machin3.origin_to_active"
    bl_label = "MACHIN3: Origin to Active"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        if context.mode == 'OBJECT':
            return "Set Selected Objects' Origin to Active Object\nALT: only set Origin Location\nCTRL: only set Origin Rotation"
        elif context.mode == 'EDIT_MESH':
            return "Set Mesh Object's Origin to Active Vert/Edge/Face\nALT: only set Origin Location\nCTRL: only set Origin Rotation"

    @classmethod
    def poll(cls, context):
        active = context.active_object

        if active:
            if context.mode == 'OBJECT':
                return [obj for obj in context.selected_objects if obj != active and obj.type not in ['EMPTY', 'FONT']]

            elif context.mode == 'EDIT_MESH' and tuple(context.scene.tool_settings.mesh_select_mode) in [(True, False, False), (False, True, False), (False, False, True)]:
                bm = bmesh.from_edit_mesh(active.data)
                return [v for v in bm.verts if v.select]

    def invoke(self, context, event):
        if event.alt and event.ctrl:
            popup_message("Hold down ATL, CTRL or neither, not both!", title="Invalid Modifier Keys")
            return {'CANCELLED'}

        global decalmachine, meshmachine

        if decalmachine is None:
            decalmachine = get_addon('DECALmachine')[0]

        if meshmachine is None:
            meshmachine = get_addon('MESHmachine')[0]

        active = context.active_object

        if context.mode == 'OBJECT':
            self.origin_to_active_object(context, only_location=event.alt, only_rotation=event.ctrl, decalmachine=decalmachine, meshmachine=meshmachine)

        elif context.mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.ed.undo_push(message="Flush Edit Mode Changes")
            bpy.ops.object.mode_set(mode='EDIT')

            self.origin_to_editmesh(active, only_location=event.alt, only_rotation=event.ctrl, decalmachine=decalmachine, meshmachine=meshmachine)

        return {'FINISHED'}

    def origin_to_editmesh(self, active, only_location, only_rotation, decalmachine, meshmachine):
        mx = active.matrix_world.copy()

        bm = bmesh.from_edit_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):
            verts = [v for v in bm.verts if v.select]
            co = average_locations([v.co for v in verts])

            loc = get_loc_matrix(mx @ co)

            v = bm.select_history[-1] if bm.select_history else verts[0]
            rot = create_rotation_matrix_from_vertex(active, v)

        elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, True, False):
            edges = [e for e in bm.edges if e.select]
            center = average_locations([get_center_between_verts(*e.verts) for e in edges])

            loc = get_loc_matrix(mx @ center)

            e = bm.select_history[-1] if bm.select_history else edges[0]
            rot = create_rotation_matrix_from_edge(active, e)

        elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
            faces = [f for f in bm.faces if f.select]
            center = average_locations([f.calc_center_median_weighted() for f in faces])

            loc = get_loc_matrix(mx @ center)

            f = bm.faces.active if bm.faces.active and bm.faces.active in faces else faces[0]
            rot = create_rotation_matrix_from_face(mx, f)

        if only_location:
            rot = get_rot_matrix(mx.to_quaternion())

        if only_rotation:
            loc = get_loc_matrix(mx.to_translation())

        sca = get_sca_matrix(mx.to_scale())
        selmx = loc @ rot @ sca

        set_obj_origin(active, selmx, bm=bm, decalmachine=decalmachine, meshmachine=meshmachine)

    def origin_to_active_object(self, context, only_location, only_rotation, decalmachine, meshmachine):
        sel = [obj for obj in context.selected_objects if obj != context.active_object and obj.type not in ['EMPTY', 'FONT']]

        aloc, arot, asca = context.active_object.matrix_world.decompose()

        for obj in sel:

            oloc, orot, osca = obj.matrix_world.decompose()

            if only_location:
                mx = get_loc_matrix(aloc) @ get_rot_matrix(orot) @ get_sca_matrix(osca)

            elif only_rotation:
                mx = get_loc_matrix(oloc) @ get_rot_matrix(arot) @ get_sca_matrix(osca)

            else:
                mx = context.active_object.matrix_world

            set_obj_origin(obj, mx, decalmachine=decalmachine, meshmachine=meshmachine)


class OriginToCursor(bpy.types.Operator):
    bl_idname = "machin3.origin_to_cursor"
    bl_label = "MACHIN3: Origin to Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        if context.mode == 'OBJECT':
            return "Set Selected Objects' Origin to Cursor\nALT: only set Origin Location\nCTRL: only set Origin Rotation"
        elif context.mode == 'EDIT_MESH':
            return "Set Mesh Object's Origin to Cursor\nALT: only set Origin Location\nCTRL: only set Origin Rotation"

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return [obj for obj in context.selected_objects if obj.type not in ['EMPTY', 'FONT']]
        else:
            return context.mode == 'EDIT_MESH'

    def invoke(self, context, event):
        if event.alt and event.ctrl:
            popup_message("Hold down ATL, CTRL or neither, not both!", title="Invalid Modifier Keys")
            return {'CANCELLED'}

        global decalmachine, meshmachine

        if decalmachine is None:
            decalmachine = get_addon('DECALmachine')[0]

        if meshmachine is None:
            meshmachine = get_addon('MESHmachine')[0]

        if context.mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.ed.undo_push(message="Flush Edit Mode Changes")
            bpy.ops.object.mode_set(mode='EDIT')

        self.origin_to_cursor(context, only_location=event.alt, only_rotation=event.ctrl, decalmachine=decalmachine, meshmachine=meshmachine)
        return {'FINISHED'}

    def origin_to_cursor(self, context, only_location=False, only_rotation=False, decalmachine=False, meshmachine=False):
        cmx = context.scene.cursor.matrix

        if context.mode == 'OBJECT':
            for obj in [obj for obj in context.selected_objects if obj.type not in ['EMPTY', 'FONT']]:
                loc, rot, sca = obj.matrix_world.decompose()

                omx = obj.matrix_world

                if only_location:
                    mx = get_loc_matrix(cmx.to_translation()) @ get_rot_matrix(omx.to_quaternion()) @ get_sca_matrix(omx.to_scale())

                elif only_rotation:
                    mx = get_loc_matrix(omx.to_translation()) @ get_rot_matrix(cmx.to_quaternion()) @ get_sca_matrix(omx.to_scale())

                else:
                    mx = cmx

                set_obj_origin(obj, mx, decalmachine=decalmachine, meshmachine=meshmachine)

        elif context.mode == 'EDIT_MESH':
            active = context.active_object

            amx = active.matrix_world

            bm = bmesh.from_edit_mesh(active.data)
            bm.normal_update()

            if only_location:
                mx = get_loc_matrix(cmx.to_translation()) @ get_rot_matrix(amx.to_quaternion()) @ get_sca_matrix(amx.to_scale())

            elif only_rotation:
                mx = get_loc_matrix(omx.to_translation()) @ get_rot_matrix(amx.to_quaternion()) @ get_sca_matrix(amx.to_scale())

            else:
                mx = cmx

            set_obj_origin(active, mx, bm=bm, decalmachine=decalmachine, meshmachine=meshmachine)
