import bpy
from bpy.props import BoolProperty
import bmesh
from math import degrees
from .. utils.mesh import unhide_deselect, join
from .. utils.object import flatten
from .. utils.ui import popup_message


class MeshCut(bpy.types.Operator):
    bl_idname = "machin3.mesh_cut"
    bl_label = "MACHIN3: Mesh Cut"
    bl_description = "Cut a Mesh Object, using another Object.\nALT: Flatten Target Object's Modifier Stack\nSHIFT: Mark Seams"
    bl_options = {'REGISTER', 'UNDO'}

    flatten_target: BoolProperty(name="Flatte Target's Modifier Stack", default=False)
    mark_seams: BoolProperty(name="Mark Seams", default=False)

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return context.active_object and context.active_object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        row = column.row(align=True)
        row.prop(self, 'flatten_target', text="Flatten Target", toggle=True)
        row.prop(self, 'mark_seams', toggle=True)

    def invoke(self, context, event):
        self.flatten_target = event.alt
        self.mark_seams = event.shift
        return self.execute(context)

    def execute(self, context):
        target = context.active_object
        cutters = [obj for obj in context.selected_objects if obj != target]

        if cutters:
            cutter = cutters[0]

            unhide_deselect(target.data)
            unhide_deselect(cutter.data)

            dg = context.evaluated_depsgraph_get()

            flatten(cutter, dg)

            if self.flatten_target:
                flatten(target, dg)

            cutter.data.materials.clear()

            join(target, [cutter], select=[1])

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.intersect(separate_mode='ALL')
            bpy.ops.object.mode_set(mode='OBJECT')

            bm = bmesh.new()
            bm.from_mesh(target.data)
            bm.normal_update()
            bm.verts.ensure_lookup_table()

            select_layer = bm.faces.layers.int.get('Machin3FaceSelect')

            meshcut_layer = bm.edges.layers.int.get('Machin3EdgeMeshCut')

            if not meshcut_layer:
                meshcut_layer = bm.edges.layers.int.new('Machin3EdgeMeshCut')

            cutter_faces = [f for f in bm.faces if f[select_layer] > 0]
            bmesh.ops.delete(bm, geom=cutter_faces, context='FACES')

            non_manifold = [e for e in bm.edges if not e.is_manifold]

            verts = set()

            for e in non_manifold:
                e[meshcut_layer] = 1

                if self.mark_seams:
                    e.seam = True

                verts.update(e.verts)

            bmesh.ops.remove_doubles(bm, verts=list({v for e in non_manifold for v in e.verts}), dist=0.0001)

            straight_edged = []

            for v in verts:
                if v.is_valid and len(v.link_edges) == 2:
                    e1 = v.link_edges[0]
                    e2 = v.link_edges[1]

                    vector1 = e1.other_vert(v).co - v.co
                    vector2 = e2.other_vert(v).co - v.co

                    angle = degrees(vector1.angle(vector2))

                    if 179 <= angle <= 181:
                        straight_edged.append(v)

            bmesh.ops.dissolve_verts(bm, verts=straight_edged)

            bm.faces.layers.int.remove(select_layer)

            bm.to_mesh(target.data)
            bm.free()

            return {'FINISHED'}
        else:
            popup_message("Select one object first, then select the object to be cut last!", title="Illegal Sellection")
            return {'CANCELLED'}
