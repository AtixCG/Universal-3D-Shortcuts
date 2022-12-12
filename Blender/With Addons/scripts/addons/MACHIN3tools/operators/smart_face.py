import bpy
from bpy.props import BoolProperty
import bmesh
from .. utils.view import update_local_view
from .. utils.registration import get_prefs


class SmartFace(bpy.types.Operator):
    bl_idname = "machin3.smart_face"
    bl_label = "MACHIN3: Smart Face"
    bl_options = {'REGISTER', 'UNDO'}

    automerge: BoolProperty(name="Merge to closeby Vert", default=True)
    use_focus: BoolProperty(name="Focus on new Object", default=False)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        if self.mode[0] or self.mode[1]:
            if len(self.verts) == 1:
                column.prop(self, "automerge")

        elif self.mode[2] and get_prefs().activate_focus:
            column.prop(self, "use_focus", text="Use Focus", toggle=True)

    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH':
            mode = tuple(context.scene.tool_settings.mesh_select_mode)
            return any(mode == m for m in [(True, False, False), (False, True, False), (False, False, True)])

    def execute(self, context):
        active = context.active_object
        ts = context.scene.tool_settings

        self.mode = tuple(ts.mesh_select_mode)

        bm = bmesh.from_edit_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        if self.mode[0] or self.mode[1]:
            self.verts = [v for v in bm.verts if v.select]

            if self.verts:

                if len(self.verts) < 3:
                    self.f3(active, bm)

                else:
                    bpy.ops.mesh.edge_face_add()

                return {'FINISHED'}

        elif self.mode[2]:
            faces = [f for f in bm.faces if f.select]

            if faces:
                bpy.ops.mesh.duplicate()
                bpy.ops.mesh.separate(type='SELECTED')

                bpy.ops.object.mode_set(mode='OBJECT')

                objs = [obj for obj in context.selected_objects if obj != active]

                if objs:
                    obj = objs[0]

                    active.select_set(False)
                    obj.select_set(True)
                    context.view_layer.objects.active = obj

                    if get_prefs().activate_focus and self.use_focus:
                        self.focus(context)

                    bpy.ops.object.mode_set(mode='EDIT')

                return {'FINISHED'}
        return {'CANCELLED'}

    def focus(self, context):
        view = context.space_data
        history = context.scene.M3.focus_history

        vis = context.visible_objects
        hidden = [obj for obj in vis if obj != context.active_object]

        if view.local_view:
            update_local_view(view, [(obj, False) for obj in hidden])

        else:
            if history:
                history.clear()

            bpy.ops.view3d.localview(frame_selected=False)

        epoch = history.add()
        epoch.name = "Epoch %d" % (len(history) - 1)

        for obj in hidden:
            entry = epoch.objects.add()
            entry.obj = obj
            entry.name = obj.name

    def f3(self, active, bm):
        verts = self.verts

        if len(verts) == 1:
            vs = verts[0]

            faces = vs.link_faces
            open_edges = [e for e in vs.link_edges if not e.is_manifold]

            if faces and len(open_edges) == 2:

                e1 = open_edges[0]
                e2 = open_edges[1]

                v1_other = e1.other_vert(vs)
                v2_other = e2.other_vert(vs)

                v1_dir = v1_other.co - vs.co
                v2_dir = v2_other.co - vs.co

                v_new = bm.verts.new()
                v_new.co = vs.co + v1_dir + v2_dir

                f = bm.faces.new([vs, v2_other, v_new, v1_other])
                f.smooth = any([f.smooth for f in faces])

                bmesh.ops.recalc_face_normals(bm, faces=[f])

                if self.automerge:
                    nonmanifoldverts = [v for v in bm.verts if any([not e.is_manifold for e in v.link_edges]) and v not in [vs, v_new, v1_other, v2_other]]

                    if nonmanifoldverts:
                        distance = min([((v_new.co - v.co).length, v) for v in nonmanifoldverts], key=lambda x: x[0])
                        threshold = min([(v_new.co - v.co).length * 0.5 for v in [v1_other, v2_other]])

                        if distance[0] < threshold:
                            v_closest = distance[1]

                            bmesh.ops.pointmerge(bm, verts=[v_new, v_closest], merge_co=v_closest.co)


                if any([len(v1_other.link_edges) == 4, len(v2_other.link_edges) == 4]):
                    if len(v1_other.link_edges) == 4 and any([not e.is_manifold for e in v1_other.link_edges]):
                        vs.select = False
                        v1_other.select = True
                        vs = v1_other

                    elif len(v2_other.link_edges) == 4 and any([not e.is_manifold for e in v2_other.link_edges]):
                        vs.select = False
                        v2_other.select = True
                        vs = v2_other
                    else:
                        vs.select = False
                        bm.select_flush(False)

                    bm.select_flush(False)

                    second_vs = [e.other_vert(vs) for e in vs.link_edges if not e.is_manifold and len(e.other_vert(vs).link_edges) == 4 and sum([not e.is_manifold for e in e.other_vert(vs).link_edges]) == 2]

                    if second_vs:
                        second_v = second_vs[0]
                        second_v.select = True

                        bm.select_flush(True)

                else:
                    vs.select = False

                    bm.select_flush(False)


        if len(verts) == 2:
            v1 = verts[0]
            v2 = verts[1]
            e12 = bm.edges.get([v1, v2])

            faces = [f for v in [v1, v2] for f in v.link_faces]

            v1_edges = [e for e in v1.link_edges if e != e12 and not e.is_manifold]
            v2_edges = [e for e in v2.link_edges if e != e12 and not e.is_manifold]

            if v1_edges and v2_edges:
                v1_other = v1_edges[0].other_vert(v1)
                v2_other = v2_edges[0].other_vert(v2)

                if v1_other == v2_other:
                    f = bm.faces.new([v1, v1_other, v2])
                else:
                    f = bm.faces.new([v1, v1_other, v2_other, v2])

                f.smooth = any([f.smooth for f in faces])

                bmesh.ops.recalc_face_normals(bm, faces=[f])

                v1.select = False
                v2.select = False

                if len(v1_other.link_edges) == 4 and any([not e.is_manifold for e in v1_other.link_edges]):
                    v1_other.select = True

                if len(v2_other.link_edges) == 4 and any([not e.is_manifold for e in v2_other.link_edges]):
                    v2_other.select = True

                bm.select_flush(False)

                if v1_other.select and not v2_other.select:
                    v1 = v1_other
                    v2 = v2_other

                    second_vs = [e.other_vert(v1) for e in v1.link_edges if not e.is_manifold and e.other_vert(v1) != v2 and len(e.other_vert(v1).link_edges) == 4]
                    if second_vs:
                        second_v = second_vs[0]
                        second_v.select = True

                elif v2_other.select and not v1_other.select:
                    v1 = v1_other
                    v2 = v2_other

                    second_vs = [e.other_vert(v2) for e in v2.link_edges if not e.is_manifold and e.other_vert(v2) != v1 and len(e.other_vert(v2).link_edges) == 4]
                    if second_vs:
                        second_v = second_vs[0]
                        second_v.select = True

                bm.select_flush(True)


        bmesh.update_edit_mesh(active.data)
