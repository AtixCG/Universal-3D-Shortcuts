import bpy
import bmesh
from math import degrees
from .. utils.mesh import unhide_deselect, join
from .. utils.object import flatten


class MeshCut(bpy.types.Operator):
    bl_idname = "machin3.mesh_cut"
    bl_label = "MACHIN3: Mesh Cut"
    bl_description = "Knife Intersect a mesh, using another object.\nALT: flatten target object's modifier stack\nSHIFT: Mark Seam"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and len(context.selected_objects) == 2 and context.active_object and context.active_object in context.selected_objects and all(obj.type == 'MESH' for obj in context.selected_objects)

    def invoke(self, context, event):
        target = context.active_object
        cutter = [obj for obj in context.selected_objects if obj != target][0]

        unhide_deselect(target.data)
        unhide_deselect(cutter.data)

        dg = context.evaluated_depsgraph_get()

        flatten(cutter, dg)

        if event.alt:
            flatten(target, dg)

        cutter.data.materials.clear()

        join(target, [cutter], select=[1])

        bpy.ops.object.mode_set(mode='EDIT')
        if event.shift:
            bpy.ops.mesh.intersect(separate_mode='ALL')
        else:
            bpy.ops.mesh.intersect(separate_mode='CUT')
        bpy.ops.object.mode_set(mode='OBJECT')

        bm = bmesh.new()
        bm.from_mesh(target.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        i = bm.faces.layers.int.verify()
        s = bm.edges.layers.string.verify()

        cutter_faces = [f for f in bm.faces if f[i] > 0]
        bmesh.ops.delete(bm, geom=cutter_faces, context='FACES')

        if event.shift:
            non_manifold = [e for e in bm.edges if not e.is_manifold]

            verts = set()

            for e in non_manifold:
                e.seam = True
                e[s] = 'MESHCUT'.encode()

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

        bm.faces.layers.int.remove(i)

        bm.to_mesh(target.data)
        bm.clear()

        return {'FINISHED'}
