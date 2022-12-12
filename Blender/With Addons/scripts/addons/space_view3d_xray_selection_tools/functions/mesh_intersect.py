import bmesh
import numpy as np
from .polygon_tests import circle_bbox, polygon_bbox, \
    points_inside_rectangle, segments_completely_outside_rectangle, segments_intersect_rectangle, \
    points_inside_circle, segments_inside_or_intersect_circle, \
    points_inside_polygon, point_inside_polygons, segments_intersect_polygon
from .view3d import get_co_world_of_ob, get_co_2d
from .selection import get_mesh_selection_mask


def lookup_isin(array, lut):
    # https://stackoverflow.com/questions/67391617/faster-membership-test-numpy-isin-too-slow/67393797#67393797
    # size of lookup table
    bound = lut.size

    # pre-filter the invalid ranges and locate the value to check further
    mask = array < bound
    idx = np.where(mask)

    # correct the mask by using the very fast LUT
    mask[idx] = lut[array[idx]]
    return mask


def select_mesh_elems(context, mode, tool, tool_co, select_all_edges, select_all_faces):
    box_xmin = box_xmax = box_ymin = box_ymax = center = radius = lasso = None
    vert_co = verts_mask_visin = vis_edges_mask_in = edge_count = edges_mask_visin = None

    if tool == 0:
        box_xmin, box_xmax, box_ymin, box_ymax = tool_co
    elif tool == 1:
        center, radius = tool_co
    else:  # shape == 2:
        lasso = tool_co

    region = context.region
    rv3d = context.region_data

    sel_obs = context.selected_objects if context.selected_objects else [context.object]
    for ob in sel_obs:
        if ob.type == 'MESH':
            mesh_select_mode = context.tool_settings.mesh_select_mode

            ob.update_from_editmode()
            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            # VERT PASS ####
            if mesh_select_mode[0] or mesh_select_mode[1] or mesh_select_mode[2] and select_all_faces:

                verts = me.vertices
                vert_count = len(verts)

                # local coordinates of vertices
                vert_co_local = np.empty(vert_count * 3, "f")
                verts.foreach_get("co", vert_co_local)
                vert_co_local.shape = (vert_count, 3)

                # mask of visible vertices
                verts_mask_vis = np.empty(vert_count, "?")
                verts.foreach_get("hide", verts_mask_vis)
                verts_mask_vis = ~verts_mask_vis

                # local coordinates of visible vertices
                vis_vert_co_local = vert_co_local[verts_mask_vis]

                # world coordinates of visible vertices
                vis_vert_co_world = get_co_world_of_ob(ob, vis_vert_co_local)

                # 2d coordinates of visible vertices
                vert_co = np.empty((vert_count, 2), "f")
                vert_co[verts_mask_vis] = vis_vert_co = get_co_2d(region, rv3d, vis_vert_co_world)

                # mask of vertices inside the selection polygon from visible vertices
                # box select
                if tool == 0:
                    vis_verts_mask_in = points_inside_rectangle(vis_vert_co, box_xmin, box_xmax, box_ymin, box_ymax)
                # circle select
                elif tool == 1:
                    vis_verts_mask_in = points_inside_circle(vis_vert_co, center, radius)
                # lasso select
                else:
                    vis_verts_mask_in = points_inside_polygon(vis_vert_co, lasso, prefilter=True)

                # mask of visible vertices inside the selection polygon from all vertices
                verts_mask_visin = np.full(vert_count, False, "?")
                verts_mask_visin[verts_mask_vis] = vis_verts_mask_in

                # do selection
                if mesh_select_mode[0]:
                    select = get_mesh_selection_mask(verts, vert_count, verts_mask_visin, mode)

                    select_list = select.tolist()
                    for i, v in enumerate(bm.verts):
                        v.select = select_list[i]

            # EDGE PASS ####
            if mesh_select_mode[1] or mesh_select_mode[2] and select_all_faces:
                edges = me.edges
                edge_count = len(edges)

                # for each edge get 2 indices of its vertices
                edge_vert_indices = np.empty(edge_count * 2, "i")
                edges.foreach_get("vertices", edge_vert_indices)
                edge_vert_indices.shape = (edge_count, 2)

                # mask of visible edges
                edges_mask_vis = np.empty(edge_count, "?")
                edges.foreach_get("hide", edges_mask_vis)
                edges_mask_vis = ~edges_mask_vis

                # for each visible edge get 2 vertex indices
                vis_edge_vert_indices = edge_vert_indices[edges_mask_vis]

                # for each visible edge get mask of vertices in the selection polygon
                vis_edge_verts_mask_in = verts_mask_visin[vis_edge_vert_indices]

                # try to select edges that are completely inside the selection polygon
                if not select_all_edges:
                    # mask of edges inside the selection polygon from visible edges
                    vis_edges_mask_in = vis_edge_verts_mask_in[:, 0] & vis_edge_verts_mask_in[:, 1]

                # if select_all_edges enabled or no inner edges found
                # then select edges that intersect the selection polygon
                if select_all_edges or (not select_all_edges and not np.any(vis_edges_mask_in)) or \
                        (mesh_select_mode[2] and select_all_faces):

                    # coordinates of vertices of visible edges
                    vis_edge_vert_co = vert_co[vis_edge_vert_indices]

                    # mask of edges from visible edges that have vertex inside the selection polygon and
                    # should be selected
                    vis_edges_mask_vert_in = vis_edge_verts_mask_in[:, 0] | vis_edge_verts_mask_in[:, 1]

                    # selection polygon bbox
                    # box select
                    if tool == 0:
                        xmin, xmax, ymin, ymax = box_xmin, box_xmax, box_ymin, box_ymax
                    # circle select
                    elif tool == 1:
                        xmin, xmax, ymin, ymax = circle_bbox(center, radius)
                    # lasso select
                    else:
                        xmin, xmax, ymin, ymax = polygon_bbox(lasso)

                    # mask of edges from visible edges that have verts both laying outside of one of sides
                    # of selection polygon bbox, so they can't intersect the selection polygon and
                    # shouldn't be selected
                    vis_edges_mask_cant_isect = segments_completely_outside_rectangle(
                        vis_edge_vert_co, xmin, xmax, ymin, ymax)

                    # mask of edges from visible edges that may intersect selection polygon and
                    # should be tested for intersection
                    vis_edges_mask_may_isect = ~vis_edges_mask_vert_in & ~vis_edges_mask_cant_isect

                    # skip if there is no edges that need to be tested for intersection
                    if np.any(vis_edges_mask_may_isect):
                        # get coordinates of verts of visible edges that may intersect the selection polygon
                        may_isect_vis_edge_co = vis_edge_vert_co[vis_edges_mask_may_isect]

                        # mask of edges that intersect the selection polygon from edges that may intersect it
                        # box select
                        if tool == 0:
                            may_isect_vis_edges_mask_isect = segments_intersect_rectangle(
                                may_isect_vis_edge_co, box_xmin, box_xmax, box_ymin, box_ymax)
                        # circle select
                        elif tool == 1:
                            may_isect_vis_edges_mask_isect = segments_inside_or_intersect_circle(
                                may_isect_vis_edge_co, center, radius)
                        # lasso select
                        else:
                            may_isect_vis_edges_mask_isect = segments_intersect_polygon(may_isect_vis_edge_co, lasso)

                        # mask of edges that intersect the selection polygon from visible edges
                        vis_edges_mask_in = vis_edges_mask_vert_in
                        vis_edges_mask_in[vis_edges_mask_may_isect] = may_isect_vis_edges_mask_isect
                    else:
                        vis_edges_mask_in = vis_edges_mask_vert_in

                # mask of visible edges inside the selection polygon from all edges
                edges_mask_visin = np.full(edge_count, False, "?")
                edges_mask_visin[edges_mask_vis] = vis_edges_mask_in

                # do selection
                if mesh_select_mode[1]:
                    select = get_mesh_selection_mask(edges, edge_count, edges_mask_visin, mode)

                    select_list = select.tolist()
                    for i, e in enumerate(bm.edges):
                        e.select = select_list[i]

            # FACE PASS #####
            if mesh_select_mode[2]:
                faces = me.polygons
                face_count = len(faces)

                # get mask of visible faces
                faces_mask_vis = np.empty(face_count, "?")
                faces.foreach_get("hide", faces_mask_vis)
                faces_mask_vis = ~faces_mask_vis

                # select faces which centers are inside the selection rectangle
                if not select_all_faces:
                    # local coordinates of face centers
                    face_center_co_local = np.empty(face_count * 3, "f")
                    faces.foreach_get("center", face_center_co_local)
                    face_center_co_local.shape = (face_count, 3)

                    # local coordinates of visible face centers
                    vis_face_center_co_local = face_center_co_local[faces_mask_vis]

                    # world coordinates of visible face centers
                    vis_vert_co_world = get_co_world_of_ob(ob, vis_face_center_co_local)

                    # 2d coordinates of visible face centers
                    vis_face_center_co = get_co_2d(region, rv3d, vis_vert_co_world)

                    # mask of face centers inside the selection polygon from visible faces
                    # box select
                    if tool == 0:
                        vis_faces_mask_in = points_inside_rectangle(
                            vis_face_center_co, box_xmin, box_xmax, box_ymin, box_ymax)
                    # circle select
                    elif tool == 1:
                        vis_faces_mask_in = points_inside_circle(
                            vis_face_center_co, center, radius)
                    # lasso select
                    else:
                        vis_faces_mask_in = points_inside_polygon(
                            vis_face_center_co, lasso, prefilter=True)

                    # mask of visible faces inside the selection polygon from all faces
                    faces_mask_visin = np.full(face_count, False, "?")
                    faces_mask_visin[faces_mask_vis] = vis_faces_mask_in
                else:
                    # mesh loops - edges that forms face polygons, sorted by face indices
                    loops = me.loops
                    loop_count = len(loops)

                    # number of vertices for each face
                    face_loop_totals = np.empty(face_count, "i")
                    faces.foreach_get("loop_total", face_loop_totals)

                    # skip getting faces from edges if there is no edges inside selection border
                    in_edge_count = np.count_nonzero(edges_mask_visin)
                    if in_edge_count:
                        # getting faces from bmesh is faster when a low number of faces need to be
                        # selected from a large number of total faces, otherwise numpy is faster
                        ratio = edge_count / in_edge_count

                        if ratio > 20:
                            # bmesh pass
                            visin_edge_indices = tuple(np.nonzero(edges_mask_visin)[0])
                            in_face_indices = [[face.index for face in bm.edges[index].link_faces]
                                               for index in visin_edge_indices]

                            from itertools import chain
                            in_face_indices = set(chain.from_iterable(in_face_indices))
                            c = len(in_face_indices)
                            in_face_indices = np.fromiter(in_face_indices, "i", c)
                        else:
                            # numpy pass
                            # indices of face edges
                            loop_edge_indices = np.empty(loop_count, "i")
                            loops.foreach_get("edge_index", loop_edge_indices)

                            # index of face for each edge in mesh loop
                            face_indices = np.arange(face_count)
                            loop_face_indices = np.repeat(face_indices, face_loop_totals)

                            # mask of visible edges in the selection polygon that are in mesh loops,
                            # therefore forming face polygons in the selection border
                            loop_edges_mask_visin = lookup_isin(loop_edge_indices, edges_mask_visin)

                            # indices of faces inside the selection polygon
                            in_face_indices = np.unique(loop_face_indices[loop_edges_mask_visin])

                        # mask of all faces in the selection polygon
                        faces_mask_in = np.full(face_count, False, "?")
                        faces_mask_in[in_face_indices] = np.True_
                        # mask of visible faces in the selection polygon
                        faces_mask_visin = faces_mask_vis & faces_mask_in
                    else:
                        faces_mask_in = faces_mask_visin = np.full(face_count, False, "?")

                    # FACE POLY PASS ####
                    # select faces under cursor (faces that have the selection polygon inside their area)

                    # visible faces not in the selection polygon
                    faces_mask_visnoin = ~faces_mask_in & faces_mask_vis

                    # number of vertices of each visible face not in the selection polygon
                    visnoin_face_loop_totals = face_loop_totals[faces_mask_visnoin]

                    # skip if all faces are already selected
                    if visnoin_face_loop_totals.size > 0:
                        # box select
                        if tool == 0:
                            cursor_co = (box_xmax, box_ymin)  # bottom right box corner
                        # circle select
                        elif tool == 1:
                            cursor_co = center
                        # lasso select
                        else:
                            cursor_co = lasso[0]

                        # indices of vertices of all faces
                        face_vert_indices = np.empty(loop_count, "i")
                        faces.foreach_get("vertices", face_vert_indices)

                        # mask of vertices not in the selection polygon from face vertices
                        face_verts_mask_visnoin = np.repeat(faces_mask_visnoin, face_loop_totals)
                        # indices of vertices of visible faces not in the selection polygon
                        visnoin_face_vert_indices = face_vert_indices[face_verts_mask_visnoin]
                        # coordinates of vertices of visible faces not in the selection polygon
                        visnoin_face_vert_co = vert_co[visnoin_face_vert_indices]
                        # index of first face vertex in face vertex sequence
                        visnoin_face_cell_starts = np.insert(visnoin_face_loop_totals[:-1].cumsum(), 0, 0)

                        # mask of faces that have cursor inside their polygon area
                        # from visible faces not in the selection polygon
                        visnoin_faces_mask_under = point_inside_polygons(
                            cursor_co, visnoin_face_vert_co, visnoin_face_cell_starts, None,
                            visnoin_face_loop_totals, prefilter=True)

                        # mask of visible faces under cursor from all faces
                        faces_mask_visunder = np.full(face_count, False, "?")
                        faces_mask_visunder[faces_mask_visnoin] = visnoin_faces_mask_under

                        # mask of visible faces in the selection polygon and under cursor
                        faces_mask_visin[faces_mask_visunder] = np.True_

                # do selection
                select = get_mesh_selection_mask(faces, face_count, faces_mask_visin, mode)

                select_list = select.tolist()
                for i, f in enumerate(bm.faces):
                    f.select = select_list[i]

            # flush face selection after selecting/deselecting edges and vertices
            bm.select_flush_mode()

            bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)
