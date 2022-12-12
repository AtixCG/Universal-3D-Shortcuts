import bpy
import bmesh
from bpy.props import FloatProperty, IntProperty, EnumProperty, BoolProperty
from math import radians
from mathutils.geometry import intersect_point_line
from .. utils.math import average_locations, average_normals
from .. utils.draw import draw_point, draw_vector
from .. items import axis_vector_mappings, axis_items, cursor_spin_angle_preset_items
from .. colors import yellow, blue, red


class PunchItALittle(bpy.types.Operator):
    bl_idname = "machin3.punch_it_a_little"
    bl_label = "MACHIN3: Punch It (a little)"
    bl_description = "Manifold Extruding that works, somewhat"
    bl_options = {'REGISTER', 'UNDO'}

    amount: FloatProperty(name="Amount", description="Extrusion Depth", default=0.1, min=0, precision=4, step=0.1)

    def execute(self, context):
        if self.amount:
            active = context.active_object

            bpy.ops.mesh.duplicate()

            bm = bmesh.from_edit_mesh(active.data)
            bm.normal_update()

            original_verts = [v for v in bm.verts if v.select]
            original_faces = [f for f in bm.faces if f.select]

            geo = bmesh.ops.extrude_face_region(bm, geom=original_faces, use_normal_flip=False)
            extruded_verts = [v for v in geo['geom'] if isinstance(v, bmesh.types.BMVert)]

            normal = original_faces[0].normal

            for v in original_verts:
                v.co += normal * self.amount

            for v in extruded_verts:
                v.select_set(True)

            bm.select_flush(True)

            all_faces = [f for f in bm.faces if f.select]

            bmesh.ops.recalc_face_normals(bm, faces=all_faces)

            bmesh.update_edit_mesh(active.data)

            bpy.ops.mesh.intersect_boolean(use_self=True)
        return {'FINISHED'}


class CursorSpin(bpy.types.Operator):
    bl_idname = "machin3.cursor_spin"
    bl_label = "MACHIN3: Cursor Spin"
    bl_description = "Cursor Spin"
    bl_options = {'REGISTER', 'UNDO'}

    def update_angle(self, context):
        if self.angle_preset != 'None' and self.angle != int(self.angle_preset):
            self.avoid_update = True
            self.angle_preset = 'None'

    def update_angle_preset(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        if self.angle_preset != 'None':
            self.angle = int(self.angle_preset)

    def update_offset_reset(self, context):
        if self.avoid_update:
            self.avoid_update = False
            return

        self.offset = 0

        self.avoid_update = True
        self.offset_reset = False

    angle: FloatProperty(name='Angle', default=45, min=0, update=update_angle)
    angle_preset: EnumProperty(name='Angle Preset', items=cursor_spin_angle_preset_items, default='45', update=update_angle_preset)
    angle_invert: BoolProperty(name='Invert', default=False)

    steps: IntProperty(name='Steps', default=4, min=1)
    adaptive: BoolProperty(name="Adaptive Steps", default=True)
    adaptive_factor: FloatProperty(name="Adaptive Factor", default=0.1, step=0.05)

    axis: EnumProperty(name='Axis', description='Cursor Axis', items=axis_items, default='Y')

    offset: FloatProperty(name='Offset', default=0, step=0.1)
    offset_reset: BoolProperty(name='Offset Reset', default=False, update=update_offset_reset)

    avoid_update: BoolProperty()

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)

        row = column.row(align=True)
        r = row.row(align=True)
        r.scale_y = 1.2
        r.prop(self, 'angle_preset', expand=True)
        row.prop(self, 'angle_invert', toggle=True)

        row = column.split(factor=0.4, align=True)
        row.prop(self, 'angle')

        r = row.split(factor=0.6, align=True)

        if self.adaptive:
            r.prop(self, 'adaptive_factor', text='Factor')
        else:
            r.prop(self, 'steps')

        r.prop(self, 'adaptive', text='Adaptive', toggle=True)

        column.separator()

        row = column.split(factor=0.5, align=True)

        r = row.row(align=True)
        r.prop(self, 'axis', expand=True)

        r = row.row(align=True)
        r.prop(self, 'offset')
        r.prop(self, 'offset_reset', text='', icon='LOOP_BACK', toggle=True)

    def execute(self, context):
        debug = False

        if self.angle:
            cmx = context.scene.cursor.matrix
            mx = context.active_object.matrix_world

            angle = radians(-self.angle if self.angle_invert else self.angle)

            axis = cmx.to_quaternion() @ axis_vector_mappings[self.axis]

            center = cmx.to_translation()

            bm = bmesh.from_edit_mesh(context.active_object.data)
            verts = [v for v in bm.verts if v.select]

            if verts:
                center_sel = mx @ average_locations([v.co for v in verts])
                if debug:
                    draw_point(center_sel, modal=False)

                i = intersect_point_line(center_sel, center, center + axis)

                if i:
                    closest_on_axis = i[0]
                    if debug:
                        draw_point(closest_on_axis, color=yellow, modal=False)

                    offset_vector = (closest_on_axis - center_sel).normalized()
                    if debug:
                        draw_vector(offset_vector, closest_on_axis, color=yellow, modal=False)

                    center = center + offset_vector * self.offset
                    if debug:
                        draw_point(center, color=blue, modal=False)

                    faces = [f for f in bm.faces if f.select]

                    avg_normal = average_normals([f.normal for f in faces])

                    cross = offset_vector.cross(avg_normal)
                    if debug:
                        draw_vector(cross, origin=center, color=red, modal=False)

                    dot = cross.dot(axis)

                    if dot < 0:
                        angle = -angle

                if debug:
                    context.area.tag_redraw()

            if self.adaptive:
                steps = max([int(self.angle * self.adaptive_factor), 1])

            else:
                steps = self.steps

            bpy.ops.mesh.spin(angle=angle, steps=steps, center=center, axis=axis)
        return {'FINISHED'}
