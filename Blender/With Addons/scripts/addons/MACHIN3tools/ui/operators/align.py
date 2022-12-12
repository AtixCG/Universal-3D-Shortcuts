import bpy
from bpy.props import EnumProperty, BoolProperty
import bmesh
from mathutils import Vector, Matrix, geometry
from ... utils.math import get_center_between_verts, create_rotation_difference_matrix_from_quat, get_loc_matrix, create_selection_bbox, get_right_and_up_axes
from ... items import axis_items, align_type_items, axis_mapping_dict, align_direction_items, align_space_items, align_mode_items
from ... utils.selection import get_selected_vert_sequences, get_selection_islands
from ... utils.ui import popup_message


class AlignEditMesh(bpy.types.Operator):
    bl_idname = "machin3.align_editmesh"
    bl_label = "MACHIN3: Align (Edit Mesh)"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Local Space Align\nALT: World Space Align\nCTRL: Cursor Space Align"

    mode: EnumProperty(name="Mode", items=align_mode_items, default="VIEW")
    type: EnumProperty(name="Type", items=align_type_items, description="Align to Min or Max, Average, Zero or Cursor", default="MIN")

    axis: EnumProperty(name="Axis", items=axis_items, description="Align on the X, Y or Z Axis", default="X")
    direction: EnumProperty(name="Direction", items=align_direction_items, default="LEFT")

    space: EnumProperty(name="Space", items=align_space_items, description="Align in Local, World or Cursor Space", default="LOCAL")

    align_each: BoolProperty(name="Align Each Island independently", default=False)
    draw_each: BoolProperty()

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_MESH":
            active = context.active_object
            bm = bmesh.from_edit_mesh(active.data)
            return [v for v in bm.verts if v.select]

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)

        split = column.split(factor=0.15, align=True)
        split.label(text='Space')
        row = split.row(align=True)
        row.prop(self, 'space', expand=True)

        split = column.split(factor=0.15, align=True)
        split.label(text='Axis')
        row = split.row(align=True)
        row.prop(self, 'axis', expand=True)

        split = column.split(factor=0.15, align=True)
        split.label(text='Type')
        row = split.row(align=True)
        row.prop(self, 'type', expand=True)

        if self.draw_each:
            split = column.split(factor=0.15, align=True)
            split.label(text='Each')
            row = split.row(align=True)
            row.prop(self, 'align_each', text='True' if self.align_each else 'False', toggle=True)

    def invoke(self, context, event):

        self.space = 'WORLD' if event.alt else 'CURSOR' if event.ctrl else 'LOCAL'

        if self.mode == 'VIEW':
            axis_right, axis_up, flip_right, flip_up = get_right_and_up_axes(context, mx=self.get_matrix(context))

            if self.type in ['ZERO', 'AVERAGE', 'CURSOR'] and self.direction in ['HORIZONTAL', 'VERTICAL']:
                axis = axis_right if self.direction == "HORIZONTAL" else axis_up

            elif self.direction in ['LEFT', 'RIGHT', 'TOP', 'BOTTOM']:
                axis = axis_right if self.direction in ['RIGHT', 'LEFT'] else axis_up

                if self.direction == 'RIGHT':
                    self.type = 'MIN' if flip_right else 'MAX'

                elif self.direction == 'LEFT':
                    self.type = 'MAX' if flip_right else 'MIN'

                elif self.direction == 'TOP':
                    self.type = 'MIN' if flip_up else 'MAX'

                elif self.direction == 'BOTTOM':
                    self.type = 'MAX' if flip_up else 'MIN'

            else:
                popup_message(f"You can't combine {self.type} with {self.direction}!", title="Invalid Property Combination")
                return {'CANCELLED'}

            self.axis = 'X' if axis == 0 else 'Y' if axis == 1 else 'Z'

        return self.execute(context)

    def execute(self, context):
        self.align(context, self.type, axis_mapping_dict[self.axis], self.space)
        return {'FINISHED'}

    def align(self, context, type, axis, space):
        active = context.active_object
        mx = self.get_matrix(context)

        bm = bmesh.from_edit_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        all_verts = []
        verts = [v for v in bm.verts if v.select]

        if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False) or type in ['ZERO', 'CURSOR']:
            all_verts.append(verts)
            self.draw_each = False

        elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, True, False):
            sequences = get_selected_vert_sequences(verts.copy(), debug=False)
            eachable = len(sequences) > 1

            if eachable:
                self.draw_each = True

            if eachable and self.align_each:
                for verts, _ in sequences:
                    all_verts.append(verts)

            else:
                all_verts.append(verts)

        elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
            islands = get_selection_islands([f for f in bm.faces if f.select], debug=False)
            eachable = len(islands) > 1

            if eachable:
                self.draw_each = True

            if eachable and self.align_each:
                for verts, _, _ in islands:
                    all_verts.append(verts)
            else:
                all_verts.append(verts)

        for verts in all_verts:


            if space == 'LOCAL':
                axiscoords = [v.co[axis] for v in verts]

            elif space == 'WORLD':
                axiscoords = [(active.matrix_world @ v.co)[axis] for v in verts]

            elif space == 'CURSOR':
                axiscoords = [(mx.inverted_safe() @ active.matrix_world @ v.co)[axis] for v in verts]



            if self.type == "MIN":
                target = min(axiscoords)

            elif self.type == "MAX":
                target = max(axiscoords)

            elif self.type == "ZERO":
                target = 0

            elif self.type == "AVERAGE":
                target = sum(axiscoords) / len(axiscoords)

            elif type == "CURSOR":
                if space == 'LOCAL':
                    c_world = context.scene.cursor.location
                    c_local = mx.inverted_safe() @ c_world
                    target = c_local[axis]

                elif space == 'WORLD':
                    target = context.scene.cursor.location[axis]

                elif space == 'CURSOR':
                    target = 0



            for v in verts:
                if space == 'LOCAL':
                    v.co[axis] = target

                elif space == 'WORLD':
                    world_co = active.matrix_world @ v.co

                    world_co[axis] = target

                    v.co = active.matrix_world.inverted_safe() @ world_co

                elif space == 'CURSOR':
                    cursor_co = mx.inverted_safe() @ active.matrix_world @ v.co

                    cursor_co[axis] = target

                    v.co = active.matrix_world.inverted_safe() @ mx @ cursor_co

        bm.normal_update()
        bmesh.update_edit_mesh(active.data)

    def get_matrix(self, context):
        mx = context.active_object.matrix_world if self.space == 'LOCAL' else context.scene.cursor.matrix if self.space == 'CURSOR' else Matrix()
        return mx


class CenterEditMesh(bpy.types.Operator):
    bl_idname = "machin3.center_editmesh"
    bl_label = "MACHIN3: Center (Edit Mesh)"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Local Space Center\nALT: World Space Center\nCTRL: Cursor Space Center"

    axis: EnumProperty(name="Axis", items=axis_items, default="X")
    direction: EnumProperty(name="Axis", items=align_direction_items, default="HORIZONTAL")

    space: EnumProperty(name="Space", items=align_space_items, default="LOCAL")

    @classmethod
    def poll(cls, context):
        if context.mode == "EDIT_MESH":
            active = context.active_object
            bm = bmesh.from_edit_mesh(active.data)
            return [v for v in bm.verts if v.select]

    def invoke(self, context, event):
        if event.alt and event.ctrl:
            popup_message("Hold down ATL, CTRL or neither, not both!", title="Invalid Modifier Keys")
            return {'CANCELLED'}

        self.space = 'WORLD' if event.alt else 'CURSOR' if event.ctrl else 'LOCAL'

        self.center(context, axis_mapping_dict[self.axis], self.direction, self.space)
        return {'FINISHED'}

    def center(self, context, axis, direction, space):
        active = context.active_object
        mx = active.matrix_world if space == 'LOCAL' else context.scene.cursor.matrix if space == 'CURSOR' else Matrix()

        mode = context.scene.M3.align_mode

        if mode == 'VIEW':
            axis_right, axis_up, flip_right, flip_up = get_right_and_up_axes(context, mx=mx)

            axis = axis_right if direction == "HORIZONTAL" else axis_up

        bm = bmesh.from_edit_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]

        if len(verts) == 1:
            origin = verts[0].co

        elif len(verts) == 2:
            origin = get_center_between_verts(*verts)

        else:
            _, origin = create_selection_bbox([v.co for v in verts])

        if space == 'LOCAL':
            target = origin.copy()
            target[axis] = 0

            mxt = get_loc_matrix(target - origin)

        elif space == 'WORLD':
            origin = active.matrix_world @ origin
            target = origin.copy()
            target[axis] = 0

            mxt = get_loc_matrix(active.matrix_world.inverted_safe().to_3x3() @ (target - origin))

        elif space == 'CURSOR':
            origin = mx.inverted_safe() @ active.matrix_world @ origin
            target = origin.copy()
            target[axis] = 0

            mxt = get_loc_matrix(active.matrix_world.inverted_safe().to_3x3() @ mx.to_3x3() @ (target - origin))

        for v in verts:
            v.co = mxt @ v.co

        bmesh.update_edit_mesh(active.data)


class AlignObjectToEdge(bpy.types.Operator):
    bl_idname = "machin3.align_object_to_edge"
    bl_label = "MACHIN3: Align Object to Edge"
    bl_description = "Align one or more objects to edge in active object\nALT: Snap objects to edge by proximity\nCTRL: Snap objects to edge by midpoint"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH':
            active = context.active_object
            sel = [obj for obj in context.selected_objects if obj != active]

            if active and sel:
                for obj in [active] + sel:
                    bm = bmesh.from_edit_mesh(obj.data)

                    if len([e for e in bm.edges if e.select]) != 1:
                        return False
                return True

    def invoke(self, context, event):
        target = context.active_object
        objs = [obj for obj in context.selected_objects if obj != target]

        for obj in objs:

            v_obj, v_target, mid, coords = self.get_vectors_from_alignment_edges(obj, target)

            if v_obj and v_target:
                loc, _, _ = obj.matrix_world.decompose()

                rmx = create_rotation_difference_matrix_from_quat(v_obj, v_target)

                obj.matrix_world = get_loc_matrix(loc) @ rmx @ get_loc_matrix(-loc) @ obj.matrix_world

                if event.alt or event.ctrl:
                    mid_world = obj.matrix_world @ mid

                    co, _ = geometry.intersect_point_line(mid_world, *coords)

                    if co:
                        obj.matrix_world = Matrix.Translation(co - mid_world) @ obj.matrix_world

                        if event.ctrl:
                            mid_target = (coords[0] + coords[1]) / 2
                            mid_obj = obj.matrix_world @ mid

                            mxt = Matrix.Translation(mid_target - mid_obj)

                            obj.matrix_world = mxt @ obj.matrix_world

        return {'FINISHED'}

    def get_vectors_from_alignment_edges(self, obj, target):

        bm = bmesh.from_edit_mesh(obj.data)
        edges = [e for e in bm.edges if e.select]

        v_obj = (obj.matrix_world.to_3x3() @ Vector(edges[0].verts[0].co - edges[0].verts[1].co)).normalized() if len(edges) == 1 else None
        mid = get_center_between_verts(*edges[0].verts) if edges else None

        bm = bmesh.from_edit_mesh(target.data)
        edges = [e for e in bm.edges if e.select]

        v_target = (target.matrix_world.to_3x3() @ Vector(edges[0].verts[0].co - edges[0].verts[1].co)).normalized() if len(edges) == 1 else None
        coords = [target.matrix_world @ v.co for v in edges[0].verts] if edges else None

        if v_obj and v_target:

            dot = v_obj.dot(v_target)

            if dot < 0:
                v_obj.negate()

            return v_obj, v_target, mid, coords
        return None, None, None, None


class AlignObjectToVert(bpy.types.Operator):
    bl_idname = "machin3.align_object_to_vert"
    bl_label = "MACHIN3: Align Object to Vert"
    bl_description = "Align one or more objects to vertice in active object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH':
            active = context.active_object
            sel = [obj for obj in context.selected_objects if obj != active]

            if active and sel:
                for obj in [active] + sel:
                    bm = bmesh.from_edit_mesh(obj.data)

                    if len([v for v in bm.verts if v.select]) != 1:
                        return False
                return True

    def invoke(self, context, event):
        target = context.active_object
        objs = [obj for obj in context.selected_objects if obj != target]

        mx_target = target.matrix_world
        bm_target = bmesh.from_edit_mesh(target.data)
        v_target = [v for v in bm_target.verts if v.select][0]

        for obj in objs:
            mx_obj = obj.matrix_world
            bm_obj = bmesh.from_edit_mesh(obj.data)
            v_obj = [v for v in bm_obj.verts if v.select][0]

            obj.matrix_world = Matrix.Translation(mx_target @ v_target.co - mx_obj @ v_obj.co) @ obj.matrix_world
        return {'FINISHED'}


class Straighten(bpy.types.Operator):
    bl_idname = "machin3.straighten"
    bl_label = "MACHIN3: Straighten"
    bl_description = "Straighten verts or edges"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(context.active_object.data)
            return len([v for v in bm.verts if v.select]) > 2 and not [f for f in bm.faces if f.select]

    def execute(self, context):
        active = context.active_object

        bm = bmesh.from_edit_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]

        if context.scene.tool_settings.mesh_select_mode[1]:
            sequences = get_selected_vert_sequences(verts.copy(), ensure_seq_len=True, debug=False)

            if sequences:
                vert_lists = [seq for seq, cyclic in sequences if len(seq) > 2 and not cyclic]

                if vert_lists:
                    for verts in vert_lists:
                        v_start = verts[0]
                        v_end = verts[-1]

                        self.straighten(bm, verts, v_start, v_end)

                    bmesh.update_edit_mesh(active.data)

                    return {'FINISHED'}

        v_start, v_end = self.get_start_and_end_from_history(bm)

        if not v_start:
            v_start, v_end = self.get_start_and_end_from_distance(verts)

        self.straighten(bm, verts, v_start, v_end)

        bmesh.update_edit_mesh(active.data)

        return {'FINISHED'}

    def straighten(self, bm, verts, v_start, v_end):
        verts.remove(v_start)
        verts.remove(v_end)

        for v in verts:
            co, _ = geometry.intersect_point_line(v.co, v_start.co, v_end.co)
            v.co = co

        bm.normal_update()

    def get_start_and_end_from_distance(self, verts):
        pairs = {frozenset([v, v2]) for v in verts for v2 in verts if v2 != v}

        distances = [((v2.co - v.co).length, (v, v2)) for v, v2 in pairs]

        return max(distances, key=lambda x: x[0])[1]

    def get_start_and_end_from_history(self, bm):
        history = list(bm.select_history)

        if len(history) >= 2 and all([isinstance(h, bmesh.types.BMVert) for h in history]):
            return history[0], history[-1]
        return None, None
