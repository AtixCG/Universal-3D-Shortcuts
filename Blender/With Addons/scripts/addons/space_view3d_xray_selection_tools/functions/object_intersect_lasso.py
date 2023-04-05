from itertools import compress

import numpy as np

from .object_intersect import (
    partition,
    get_ob_2dbboxes,
    get_vert_co_2d,
    get_edge_vert_co_2d,
    get_face_vert_co_2d,
    get_ob_loc_co_2d,
    do_selection,
)
from .polygon_tests import (
    point_inside_rectangles,
    point_inside_polygons,
    points_inside_polygon,
    segments_intersect_polygon,
)


def get_obs_mask_overlap_lasso(obs, obs_mask_check, depsgraph, region, rv3d, lasso_poly, check_faces=False):
    list_of_obs_to_check = compress(obs, obs_mask_check)
    bool_list = []

    for ob in list_of_obs_to_check:
        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh(preserve_all_data_layers=False, depsgraph=None)
        vert_co_2d = get_vert_co_2d(me, ob_eval, region, rv3d)
        verts_mask_in_lasso = points_inside_polygon(vert_co_2d, lasso_poly, prefilter=True)
        if np.any(verts_mask_in_lasso):
            bool_list.append(True)
        else:
            edge_vert_co_2d = get_edge_vert_co_2d(me, vert_co_2d)
            edges_mask_isect_lasso = segments_intersect_polygon(edge_vert_co_2d, lasso_poly, prefilter=True)
            if np.any(edges_mask_isect_lasso):
                bool_list.append(True)
            else:
                if check_faces:
                    face_vert_co_2d, face_cell_starts, face_cell_ends, face_loop_totals = get_face_vert_co_2d(
                        me, vert_co_2d
                    )
                    if face_loop_totals.size > 0:
                        faces_mask_cursor_in = point_inside_polygons(
                            lasso_poly[0],
                            face_vert_co_2d,
                            face_cell_starts,
                            face_cell_ends,
                            face_loop_totals,
                            prefilter=True,
                        )
                        bool_list.append(np.any(faces_mask_cursor_in))
                    else:
                        bool_list.append(False)
                else:
                    bool_list.append(False)
        ob_eval.to_mesh_clear()

    bools = np.fromiter(bool_list, "?", len(bool_list))
    return bools


def get_obs_mask_in_lasso(obs, obs_mask_check, depsgraph, region, rv3d, lasso_poly):
    list_of_obs_to_check = compress(obs, obs_mask_check)
    bool_list = []

    for ob in list_of_obs_to_check:
        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh(preserve_all_data_layers=False, depsgraph=None)
        vert_co_2d = get_vert_co_2d(me, ob_eval, region, rv3d)
        verts_mask_in_lasso = points_inside_polygon(vert_co_2d, lasso_poly, prefilter=True)
        if np.all(verts_mask_in_lasso):
            bool_list.append(True)
        else:
            bool_list.append(False)
        ob_eval.to_mesh_clear()

    bools = np.fromiter(bool_list, "?", len(bool_list))
    return bools


def select_obs_in_lasso(context, mode, lasso_poly, behavior):
    region = context.region
    rv3d = context.region_data
    depsgraph = context.evaluated_depsgraph_get()

    selectable_obs = context.selectable_objects
    mesh_obs, nonmesh_obs = partition(selectable_obs, lambda o: o.type in {'MESH', 'CURVE', 'FONT'})
    mesh_ob_count = len(mesh_obs)

    # Get coordinates of 2d bounding boxes of objects.
    (
        ob_2dbbox_xmin,
        ob_2dbbox_xmax,
        ob_2dbbox_ymin,
        ob_2dbbox_ymax,
        ob_2dbbox_points,
        ob_2dbbox_segments,
        obs_mask_2dbbox_entire_clip,
    ) = get_ob_2dbboxes(mesh_obs, mesh_ob_count, region, rv3d)

    # Check for bounding boxes intersections with lasso.
    # Speed up finding overlaps or intersections by doing polygon tests on bounding boxes.

    # Ob bbox intersects lasso.
    segment_bools = segments_intersect_polygon(ob_2dbbox_segments, lasso_poly)
    segment_bools.shape = (mesh_ob_count, 4)
    obs_mask_2dbbox_isect_lasso = np.any(segment_bools, axis=1)

    # Ob bbox entirely inside lasso.
    point_bools = points_inside_polygon(ob_2dbbox_points, lasso_poly)
    point_bools.shape = (mesh_ob_count, 4)
    obs_mask_2dbbox_entire_in_lasso = np.all(point_bools, axis=1)

    # Cursor is inside ob bbox.
    obs_mask_cursor_in_2dbbox = point_inside_rectangles(
        lasso_poly[0], ob_2dbbox_xmin, ob_2dbbox_xmax, ob_2dbbox_ymin, ob_2dbbox_ymax
    )

    obs_mask_dont_check = obs_mask_2dbbox_entire_in_lasso | obs_mask_2dbbox_entire_clip

    if behavior == 'OVERLAP':
        obs_mask_check_verts_edges = obs_mask_2dbbox_isect_lasso & ~obs_mask_dont_check
        obs_mask_check_faces = obs_mask_cursor_in_2dbbox & ~obs_mask_2dbbox_isect_lasso & ~obs_mask_dont_check

        mesh_obs_mask_in_lasso = obs_mask_2dbbox_entire_in_lasso
        mesh_obs_mask_in_lasso[obs_mask_check_verts_edges] = get_obs_mask_overlap_lasso(
            mesh_obs, obs_mask_check_verts_edges, depsgraph, region, rv3d, lasso_poly
        )
        mesh_obs_mask_in_lasso[obs_mask_check_faces] = get_obs_mask_overlap_lasso(
            mesh_obs, obs_mask_check_faces, depsgraph, region, rv3d, lasso_poly, check_faces=True
        )
        do_selection(mesh_obs_mask_in_lasso, mesh_obs, mode)

    else:
        obs_mask_check = (
            obs_mask_2dbbox_isect_lasso | (obs_mask_cursor_in_2dbbox & ~obs_mask_2dbbox_isect_lasso)
        ) & ~obs_mask_dont_check

        mesh_obs_mask_in_lasso = obs_mask_2dbbox_entire_in_lasso
        mesh_obs_mask_in_lasso[obs_mask_check] = get_obs_mask_in_lasso(
            mesh_obs, obs_mask_check, depsgraph, region, rv3d, lasso_poly
        )
        do_selection(mesh_obs_mask_in_lasso, mesh_obs, mode)

    nonmesh_ob_co_2d = get_ob_loc_co_2d(nonmesh_obs, region, rv3d)
    nonmesh_obs_mask_in_lasso = points_inside_polygon(nonmesh_ob_co_2d, lasso_poly)
    do_selection(nonmesh_obs_mask_in_lasso, nonmesh_obs, mode)
