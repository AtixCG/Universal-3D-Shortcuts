import bpy
from bpy.props import EnumProperty, BoolProperty, IntProperty
from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d, region_2d_to_location_3d
import bmesh
from mathutils import Vector
from mathutils.geometry import intersect_point_line, intersect_line_line, intersect_line_plane
from .. utils.graph import get_shortest_path
from .. utils.ui import popup_message, init_status, finish_status
from .. utils.draw import draw_line, draw_lines, draw_point, draw_tris, draw_vector
from .. utils.snap import Snap
from .. utils.math import average_locations, get_center_between_verts, get_face_center
from .. utils.selection import get_edges_vert_sequences, get_selection_islands
from .. utils.registration import get_addon
from .. utils.system import printd
from .. utils.property import step_enum
from .. items import smartvert_mode_items, smartvert_merge_type_items, smartvert_path_type_items, ctrl, alt

from .. colors import yellow, white, green


hypercursor = None


def draw_slide_status(op):
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)

        text = f"Slide Extend Snap to {op.snap_element.capitalize()}" if op.snap_element else "Slide Extend"
        row.label(text=text)

        row.label(text="", icon='MOUSE_LMB')
        row.label(text="Confirm")

        row.label(text="", icon='MOUSE_RMB')
        row.label(text="Cancel")

        row.separator(factor=10)

        if op.can_flatten:
            row.label(text="", icon='EVENT_F')
            row.label(text=f"Flatten: {op.flatten}")

        if not op.is_snapping:
            row.label(text="", icon='EVENT_CTRL')
            row.label(text="Snap")

        if op.is_snapping and op.snap_element == 'EDGE' and not op.is_diverging:
            row.label(text="", icon='EVENT_ALT')
            row.label(text="Diverge")

    return draw


class SmartVert(bpy.types.Operator):
    bl_idname = "machin3.smart_vert"
    bl_label = "MACHIN3: Smart Vert"
    bl_options = {'REGISTER', 'UNDO'}

    mode: EnumProperty(name="Mode", items=smartvert_mode_items, default="MERGE")
    mergetype: EnumProperty(name="Merge Type", items=smartvert_merge_type_items, default="LAST")
    merge_center_paths: BoolProperty(name="Merge Paths in center", default=False)
    pathtype: EnumProperty(name="Path Type", items=smartvert_path_type_items, default="TOPO")

    slideoverride: BoolProperty(name="Slide Override", default=False)
    vertbevel: BoolProperty(name="Single Vertex Bevelling", default=False)

    index: IntProperty(name="Index of Edge accociated with HyperCursor Gizmo, that is to be removed")
    can_flatten: BoolProperty(name="Can Flatten", default=False)
    flatten: BoolProperty(name="Flatten End Face", default=False)

    snapping = False
    passthrough = False
    mousemerge = False

    @classmethod
    def poll(cls, context):
        if context.active_object:
            if context.mode == 'EDIT_MESH':
                bm = bmesh.from_edit_mesh(context.active_object.data)
                return [v for v in bm.verts if v.select]
            return context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        if self.slideoverride:
            row = column.split(factor=0.3)
            row.label(text="Mode")
            r = row.row()
            r.label(text='Slide Extend')

        else:
            row = column.split(factor=0.3)
            row.label(text="Mode")
            r = row.row()
            r.prop(self, "mode", expand=True)

            if self.mode == "MERGE":
                row = column.split(factor=0.3)
                row.label(text="Merge")
                r = row.row(align=True)
                r.prop(self, "mergetype", expand=True)

                if self.mergetype == 'PATHS':
                    r.prop(self, "merge_center_paths", text='in Center', toggle=True)

            if self.mode == "CONNECT" or (self.mode == "MERGE" and self.mergetype == "PATHS"):
                row = column.split(factor=0.3)
                row.label(text="Shortest Path")
                r = row.row()
                r.prop(self, "pathtype", expand=True)

    def draw_VIEW3D(self):

        if self.coords:
            draw_lines(self.coords, mx=self.mx, color=(0.5, 1, 0.5), width=2, alpha=0.5)

        if self.is_snapping:
            if self.snap_element == 'EDGE':
                if self.snap_coords:
                    draw_lines(self.snap_coords, color=(1, 0, 0), width=3, alpha=0.75)

                if self.snap_proximity_coords:
                    draw_lines(self.snap_proximity_coords, mx=self.mx, color=(1, 0, 0), width=1, alpha=0.3)

                if self.snap_ortho_coords:
                    draw_lines(self.snap_ortho_coords, mx=self.mx, color=(1, 0.7, 0), width=1, alpha=0.3)

            elif self.snap_element == 'FACE':
                if self.snap_tri_coords:
                    draw_tris(self.snap_tri_coords, color=(1, 0, 0), alpha=0.1)

                if self.snap_ortho_coords:
                    draw_lines(self.snap_ortho_coords, mx=self.mx, color=(1, 0.7, 0), width=1, alpha=0.3)

    def modal(self, context, event):
        context.area.tag_redraw()

        self.mousepos = Vector((event.mouse_region_x, event.mouse_region_y))

        self.is_snapping = event.ctrl
        self.is_diverging = self.is_snapping and event.alt

        if not self.is_snapping:
            self.snap_coords = []
            self.snap_tri_coords = []
            self.snap_proximity_coords = []
            self.snap_ortho_coords = []
            self.snap_element = None

        events = ['MOUSEMOVE', *ctrl, *alt]

        if self.can_flatten:
            events.append('F')

        if event.type in events:

            if event.type == 'F' and event.value == 'PRESS':
                self.flatten = not self.flatten

            if self.passthrough:
                self.passthrough = False

                self.loc = self.get_slide_vector_intersection(context)
                self.init_loc = self.init_loc + self.loc - self.offset_loc

            elif event.ctrl:
                self.S.get_hit(self.mousepos)

                if self.S.hit:
                    self.slide_snap(context)

                else:
                    self.snap_coords = []
                    self.snap_tri_coords = []
                    self.snap_proximity_coords = []
                    self.snap_ortho_coords = []
                    self.snap_element = None

                    self.loc = self.get_slide_vector_intersection(context)

                    self.slide(context)

            else:
                self.is_snapping = False
                self.loc = self.get_slide_vector_intersection(context)

                self.slide(context)




        if event.type in {'MIDDLEMOUSE'}:
            self.offset_loc = self.get_slide_vector_intersection(context)

            self.passthrough = True
            return {'PASS_THROUGH'}


        elif event.type in {'LEFTMOUSE', 'SPACE'} and event.value == 'PRESS':

            if self.is_snapping:

                avg_dist = sum((v.co - data['co']).length for v, data in self.verts.items()) / len(self.verts)

                bmesh.ops.dissolve_degenerate(self.bm, edges=self.bm.edges, dist=avg_dist / 100)
                self.bm.normal_update()

                if context.mode == 'EDIT_MESH':
                    bmesh.update_edit_mesh(self.active.data)
                else:
                    self.bm.to_mesh(self.active.data)

            if context.mode == 'OBJECT':
                from HyperCursor.utils.select import clear_hyper_edge_selection
                clear_hyper_edge_selection(context.active_object)

            self.finish(context)

            return {'FINISHED'}


        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel_modal(context)

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def cancel_modal(self, context):

        for v, data in self.verts.items():
            v.co = data['co']

        if self.can_flatten:
            for v, vdict in self.flatten_dict['other_verts'].items():
                v.co = vdict['co']

        self.bm.normal_update()

        if context.mode == 'EDIT_MESH':
            bmesh.update_edit_mesh(self.active.data)
        else:
            self.bm.to_mesh(self.active.data)

        self.finish(context)

    def finish(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')

        finish_status(self)

        self.S.finish()

        if context.mode == 'OBJECT':
            context.active_object.HC.show_geometry_gizmos = True

            context.active_object.select_set(True)


    def invoke(self, context, event):

        if context.mode == 'OBJECT':
            global hypercursor

            if hypercursor is None:
                hypercursor = get_addon('HyperCursor')[0]

            if self.slideoverride and hypercursor:
                context.active_object.HC.show_geometry_gizmos = False

                from HyperCursor.utils.select import get_selected_edges

            else:
                return {'CANCELLED'}

        self.mousepos = Vector((event.mouse_region_x, event.mouse_region_y))

        if self.slideoverride:
            if context.mode == 'EDIT_MESH' and tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
                return {'CANCELLED'}

            self.active = context.active_object
            self.mx = self.active.matrix_world

            if context.mode == 'EDIT_MESH':
                self.bm = bmesh.from_edit_mesh(self.active.data)
                self.bm.normal_update()


                if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):

                    selected = [v for v in self.bm.verts if v.select]
                    history = list(self.bm.select_history)

                    if len(selected) == 1:
                        popup_message("Select more than 1 vertex.")
                        return {'CANCELLED'}

                    elif not history:
                        popup_message("Select the last vertex without Box or Circle Select.")
                        return {'CANCELLED'}

                    else:


                        if len(selected) > 3 and len(selected) % 2 == 0 and set(history) == set(selected):
                            self.verts = {history[i]: {'co': history[i].co.copy(), 'target': history[i + 1]} for i in range(0, len(history), 2)}

                        else:
                            last = history[-1]
                            self.verts = {v: {'co': v.co.copy(), 'target': last} for v in selected if v != last}


                elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, True, False):

                    selected = [e for e in self.bm.edges if e.select]
                    self.verts = {}

                    for edge in selected:
                        edge_center = average_locations([self.mx @ v.co for v in edge.verts])

                        mouse_3d = region_2d_to_location_3d(context.region, context.region_data, self.mousepos, edge_center)
                        mouse_3d_local = self.mx.inverted_safe() @ mouse_3d

                        closest = min([(v, (v.co - mouse_3d_local).length) for v in edge.verts], key=lambda x: x[1])[0]

                        self.verts[closest] = {'co': closest.co.copy(), 'target': edge.other_vert(closest)}

            else:
                wm = context.window_manager
                context.window.cursor_warp(int(wm.hyper_mousepos[0]), int(wm.hyper_mousepos[1]))
                self.mousepos = Vector(wm.hyper_mousepos_region)

                self.bm = bmesh.new()
                self.bm.from_mesh(self.active.data)
                self.bm.normal_update()
                self.bm.edges.ensure_lookup_table()

                selected = get_selected_edges(self.bm, index=self.index)
                self.verts = {}

                for edge in selected:
                    edge_center = average_locations([self.mx @ v.co for v in edge.verts])

                    mouse_3d = region_2d_to_location_3d(context.region, context.region_data, self.mousepos, edge_center)
                    mouse_3d_local = self.mx.inverted_safe() @ mouse_3d

                    closest = min([(v, (v.co - mouse_3d_local).length) for v in edge.verts], key=lambda x: x[1])[0]

                    self.verts[closest] = {'co': closest.co.copy(), 'target': edge.other_vert(closest)}



            self.can_flatten = False
            self.flatten_dict = {}

            if len(self.verts) == 1:

                vert = next(iter(self.verts))

                planar_edges = [e for e in vert.link_edges if not e.other_vert(vert) == self.verts[vert]['target']]

                if len(planar_edges) == 2:
                    end_faces = [f for f in planar_edges[0].link_faces if f in planar_edges[1].link_faces]

                    if len(end_faces) == 1:
                        end_face = end_faces[0]

                        if len(end_face.verts) > 3:
                            self.can_flatten = True

                            tri_verts = set(v for e in planar_edges for v in e.verts)
                            self.flatten_dict = {'tri_verts': list(tri_verts),
                                                 'other_verts': {}}

                            other_verts = [v for v in end_face.verts if v not in tri_verts]

                            for v in other_verts:
                                slide_edges = [e for e in v.link_edges if e not in end_face.edges]

                                if slide_edges:
                                    line = [slide_edges[0].verts[0].co.copy(), slide_edges[0].verts[1].co.copy()]
                                    self.flatten_dict['other_verts'][v] = {'co': v.co.copy(),
                                                                           'line': line}


            self.target_avg = self.mx @ average_locations([data['target'].co for _, data in self.verts.items()])
            self.origin = self.mx @ average_locations([v.co for v, _ in self.verts.items()])

            if self.target_avg == self.origin:
                if context.mode == 'OBJECT':
                    context.active_object.HC.show_geometry_gizmos = True

                popup_message("Try to position the view and mouse in a way, that clearly indicates the direction you want to slide towards", title='Ambigious Direction')
                return {'CANCELLED'}

            self.init_loc = self.get_slide_vector_intersection(context)

            if self.init_loc:

                self.loc = self.init_loc
                self.offset_loc = self.init_loc
                self.distance = 0
                self.coords = []

                self.S = Snap(context, alternative=[self.active], debug=False)

                self.is_snapping = False
                self.is_diverging = False
                self.snap_element = None
                self.snap_coords = []
                self.snap_tri_coords = []
                self.snap_proximity_coords = []
                self.snap_ortho_coords = []

                init_status(self, context, func=draw_slide_status(self))

                self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (), 'WINDOW', 'POST_VIEW')

                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}

            return {'CANCELLED'}

        else:
            self.vertbevel = False
            self.mousemerge = False
            ret = False

            if self.mode == 'MERGE' and self.mergetype in ['LAST', 'CENTER']:
                ret = self.smart_vert(context)

            elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):
                ret = self.smart_vert(context)

            if ret:
                return {'FINISHED'}

        return {'CANCELLED'}

    def execute(self, context):
        self.smart_vert(context)
        return {'FINISHED'}

    def smart_vert(self, context):
        active = context.active_object
        topo = True if self.pathtype == "TOPO" else False

        bm = bmesh.from_edit_mesh(active.data)
        bm.normal_update()
        bm.verts.ensure_lookup_table()

        verts = [v for v in bm.verts if v.select]
        edges = [e for e in bm.edges if e.select]
        faces = [f for f in bm.faces if f.select]



        if len(verts) == 1 and tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):
            bpy.ops.mesh.bevel('INVOKE_DEFAULT', affect='VERTICES')
            self.vertbevel = True
            return True



        elif self.mode == "MERGE":

            if self.mergetype == "LAST":

                if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True):
                    self.mouse_merge(context, active, bm, verts, faces=faces)

                elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, True, False) and edges:
                    self.mouse_merge(context, active, bm, verts, edges=edges)

                elif len(verts) >= 2:
                    if self.validate_history(active, bm, lazy=True):
                        bpy.ops.mesh.merge(type='LAST')

                    else:
                        self.mouse_merge(context, active, bm, verts=verts, edges=None)

                return True

            elif self.mergetype == "CENTER":
                if tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, False, True) and faces:
                    self.center_merge(active, bm, verts, faces=faces)

                elif tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (False, True, False) and edges:
                    self.center_merge(active, bm, verts, edges=edges)

                elif len(verts) >= 2:
                    bpy.ops.mesh.merge(type='CENTER')

                return True


            elif self.mergetype == "PATHS" and tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):
                if len(verts) == 4:
                    history = self.validate_history(active, bm)

                    if history:
                        path1, path2 = self.get_paths(bm, history, topo)
                        self.merge_paths(active, bm, path1, path2)
                        return True



        elif self.mode == "CONNECT" and tuple(bpy.context.scene.tool_settings.mesh_select_mode) == (True, False, False):
            if len(verts) == 4:
                history = self.validate_history(active, bm)

                if history:
                    path1, path2 = self.get_paths(bm, history, topo)

                    self.connect(active, bm, path1, path2)
                    return True

    def validate_history(self, active, bm, lazy=False):
        verts = [v for v in bm.verts if v.select]
        history = list(bm.select_history)

        if lazy:
            return history

        if len(verts) == len(history):
            return history
        return None

    def get_paths(self, bm, history, topo):
        pair1 = history[0:2]
        pair2 = history[2:4]
        pair2.reverse()

        path1 = get_shortest_path(bm, *pair1, topo=topo, select=True)
        path2 = get_shortest_path(bm, *pair2, topo=topo, select=True)

        is_any_in_both = any(v in path2 for v in path1)

        if is_any_in_both:
            path1 = get_shortest_path(bm, *pair1, topo=not topo, select=True)
            path2 = get_shortest_path(bm, *pair2, topo=not topo, select=True)

            self.pathtype = step_enum(self.pathtype, smartvert_path_type_items, step=1, loop=True)

        return path1, path2

    def merge_paths(self, active, bm, path1, path2):
        targetmap = {}

        for v1, v2 in zip(path1, path2):
            targetmap[v1] = v2

            if self.merge_center_paths:
                v2.co = average_locations([v1.co, v2.co])

        bmesh.ops.weld_verts(bm, targetmap=targetmap)
        bmesh.update_edit_mesh(active.data)

    def center_merge(self, active, bm, verts, edges=None, faces=None):

        if faces:
            islands = get_selection_islands(faces, debug=False)

            seen_verts = []

            for verts, _, _ in islands:
                merge_verts = [v for v in verts if v not in seen_verts]
                seen_verts.extend(merge_verts)

                bmesh.ops.pointmerge(bm, verts=merge_verts, merge_co=average_locations([v.co for v in merge_verts]))

        elif edges:
            all_verts = verts.copy()

            try:
                sequences = get_edges_vert_sequences(verts, edges, debug=False)

            except:
                sequences = [(all_verts, False)]

            for verts, _ in sequences:
                bmesh.ops.pointmerge(bm, verts=verts, merge_co=average_locations([v.co for v in verts]))

        for el in list(bm.verts) + list(bm.edges):
            el.select_set(False)

        bmesh.update_edit_mesh(active.data)

    def mouse_merge(self, context, active, bm, verts, edges=None, faces=None):

        def get_merge_co_from_mouse(verts, debug=False):
            distances = []

            for v in verts:
                mouse_3d = region_2d_to_location_3d(context.region, context.region_data, self.mousepos, mx @ v.co)
                mouse_3d_local = mx.inverted_safe() @ mouse_3d

                if debug:
                    draw_point(mouse_3d_local, mx=mx, color=white, modal=False)

                distances.append((v.co, (v.co - mouse_3d_local).length))

            return min(distances, key=lambda x: x[1])[0]

        mx = active.matrix_world

        if faces:
            islands = get_selection_islands(faces, debug=False)

            seen_verts = []

            for verts, _, _ in islands:
                merge_verts = [v for v in verts if v not in seen_verts]
                seen_verts.extend(merge_verts)

                merge_co = get_merge_co_from_mouse(merge_verts)
                bmesh.ops.pointmerge(bm, verts=merge_verts, merge_co=merge_co)

        elif edges:
            all_verts = verts.copy()

            try:
                sequences = get_edges_vert_sequences(verts, edges, debug=False)

            except:
                sequences = [(all_verts, False)]

            for seq, _ in sequences:
                merge_co = merge_co=get_merge_co_from_mouse(seq)
                bmesh.ops.pointmerge(bm, verts=seq, merge_co=merge_co)

        else:
            merge_co = get_merge_co_from_mouse(verts)
            bmesh.ops.pointmerge(bm, verts=verts, merge_co=merge_co)

        bmesh.update_edit_mesh(active.data)
        self.mousemerge = True

    def connect(self, active, bm, path1, path2):
        for verts in zip(path1, path2):
            if not bm.edges.get(verts):
                bmesh.ops.connect_vert_pair(bm, verts=verts)

        bmesh.update_edit_mesh(active.data)

    def get_slide_vector_intersection(self, context):
        view_origin = region_2d_to_origin_3d(context.region, context.region_data, self.mousepos)
        view_dir = region_2d_to_vector_3d(context.region, context.region_data, self.mousepos)

        i = intersect_line_line(view_origin, view_origin + view_dir, self.origin, self.target_avg)

        return i[1]

    def slide(self, context):
        origin_dir = (self.target_avg - self.origin).normalized()
        move_dir = (self.loc - self.init_loc).normalized()

        self.distance = (self.mx.to_3x3().inverted_safe() @ (self.init_loc - self.loc)).length * origin_dir.dot(move_dir)

        self.coords = []

        for v, data in self.verts.items():
            init_co = data['co']
            target = data['target']

            slidedir = (target.co - init_co).normalized()
            v.co = init_co + slidedir * self.distance

            self.coords.extend([v.co, target.co])

        if self.can_flatten:

            if self.flatten:
                self.flatten_verts()

            else:
                for v, vdict in self.flatten_dict['other_verts'].items():
                    v.co = vdict['co']

        self.bm.normal_update()

        if context.mode == 'EDIT_MESH':
            bmesh.update_edit_mesh(self.active.data)
        else:
            self.bm.to_mesh(self.active.data)

    def slide_snap(self, context):

        hitmx = self.S.hitmx
        hit_co = hitmx.inverted_safe() @ self.S.hitlocation

        hitface = self.S.hitface
        tri_coords = self.S.cache.tri_coords[self.S.hitobj.name][self.S.hitindex]


        face_weight = 25
        edge_weight = 1

        face_distance = (hitface, (hit_co - hitface.calc_center_median_weighted()).length / face_weight)

        edge = min([(e, (hit_co - intersect_point_line(hit_co, e.verts[0].co, e.verts[1].co)[0]).length, (hit_co - get_center_between_verts(*e.verts)).length) for e in hitface.edges if e.calc_length()], key=lambda x: (x[1] * x[2]) / x[0].calc_length())
        edge_distance = (edge[0], ((edge[1] * edge[2]) / edge[0].calc_length()) / edge_weight)

        closest = min([face_distance, edge_distance], key=lambda x: x[1])

        self.snap_coords = []
        self.snap_tri_coords = []
        self.snap_proximity_coords = []
        self.snap_ortho_coords = []

        if isinstance(closest[0], bmesh.types.BMEdge):
            self.snap_element = 'EDGE'

            self.snap_coords = [hitmx @ v.co for v in closest[0].verts]

            snap_coords = [self.mx.inverted_safe() @ co for co in self.snap_coords]

            self.snap_proximity_coords = []
            self.snap_ortho_coords = []

            for v, data in self.verts.items():
                init_co = data['co']
                target = data['target']

                snap_dir = (snap_coords[0] - snap_coords[1]).normalized()
                slide_dir = (init_co - target.co).normalized()

                if abs(slide_dir.dot(snap_dir)) > 0.999:
                    v.co = init_co

                else:
                    i = intersect_line_line(init_co, target.co, *snap_coords)

                    v.co = i[1 if self.is_diverging else 0] if i else init_co

                    if v.co != target.co:
                        self.coords.extend([v.co, target.co])

                    if i[1] != snap_coords[0]:
                        self.snap_proximity_coords.extend([i[1], snap_coords[0]])

                    if v.co != i[1]:
                        self.snap_ortho_coords.extend([v.co, i[1]])

        elif isinstance(closest[0], bmesh.types.BMFace):
            self.snap_element = 'FACE'

            foundintersection = False

            co = self.mx.inverted_safe() @ hitmx @ get_face_center(closest[0])
            no = self.mx.inverted_safe().to_3x3() @ hitmx.to_3x3() @ closest[0].normal

            for v, data in self.verts.items():
                init_co = data['co']
                target = data['target']

                i = intersect_line_plane(init_co, target.co, co, no)

                if i:
                    foundintersection = True
                    v.co = i

                    self.snap_ortho_coords.extend([i, co])

            if foundintersection:
                self.snap_tri_coords = tri_coords

        if self.can_flatten:

            if self.flatten:
                self.flatten_verts()

            else:
                for v, vdict in self.flatten_dict['other_verts'].items():
                    v.co = vdict['co']

        self.bm.normal_update()

        if context.mode == 'EDIT_MESH':
            bmesh.update_edit_mesh(self.active.data)
        else:
            self.bm.to_mesh(self.active.data)

    def flatten_verts(self):

        tri_verts = self.flatten_dict['tri_verts']

        tri_dir1 = (tri_verts[0].co - tri_verts[1].co).normalized()
        tri_dir2 = (tri_verts[2].co - tri_verts[1].co).normalized()

        plane_no = tri_dir1.cross(tri_dir2)
        plane_co = tri_verts[1].co

        for v, vdict in self.flatten_dict['other_verts'].items():

            i = intersect_line_plane(*vdict['line'], plane_co, plane_no)

            if i:
                v.co = i
