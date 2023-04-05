from itertools import compress

import numpy as np

from .object_intersect import partition, get_ob_2dbboxes, get_vert_co_2d, get_ob_loc_co_2d, do_selection
from .polygon_tests import point_inside_rectangles, points_inside_rectangle, segments_intersect_rectangle


def get_obs_mask_in_selbox(obs, obs_mask_check, depsgraph, region, rv3d, xmin, xmax, ymin, ymax):
    list_of_obs_to_check = compress(obs, obs_mask_check)
    bool_list = []

    for ob in list_of_obs_to_check:
        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh(preserve_all_data_layers=False, depsgraph=None)
        vert_co_2d = get_vert_co_2d(me, ob_eval, region, rv3d)
        verts_mask_in_selbox = points_inside_rectangle(vert_co_2d, xmin, xmax, ymin, ymax)
        if np.all(verts_mask_in_selbox):
            bool_list.append(True)
        else:
            bool_list.append(False)
        ob_eval.to_mesh_clear()

    bools = np.fromiter(bool_list, "?", len(bool_list))
    return bools


def select_obs_in_box(context, mode, xmin, xmax, ymin, ymax, behavior):
    region = context.region
    rv3d = context.region_data
    depsgraph = context.evaluated_depsgraph_get()

    selectable_obs = context.selectable_objects

    if behavior == 'CONTAIN':
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

        # Check for bounding boxes intersections with selection box.
        # Speed up finding overlaps or intersections by doing polygon tests on bounding boxes.

        # Ob bbox intersects selection box.
        segment_bools = segments_intersect_rectangle(ob_2dbbox_segments, xmin, xmax, ymin, ymax, prefilter=True)
        segment_bools.shape = (mesh_ob_count, 4)
        obs_mask_2dbbox_isect_selbox = np.any(segment_bools, axis=1)

        # Ob bbox bbox entirely inside selection box.
        point_bools = points_inside_rectangle(ob_2dbbox_points, xmin, xmax, ymin, ymax)
        point_bools.shape = (mesh_ob_count, 4)
        obs_mask_2dbbox_entire_in_selbox = np.all(point_bools, axis=1)

        # Cursor is inside ob bbox.
        obs_mask_cursor_in_2dbbox = point_inside_rectangles(
            (xmin, ymin), ob_2dbbox_xmin, ob_2dbbox_xmax, ob_2dbbox_ymin, ob_2dbbox_ymax
        )

        obs_mask_dont_check = obs_mask_2dbbox_entire_in_selbox | obs_mask_2dbbox_entire_clip
        obs_mask_check = (
            obs_mask_2dbbox_isect_selbox | (obs_mask_cursor_in_2dbbox & ~obs_mask_2dbbox_isect_selbox)
        ) & ~obs_mask_dont_check

        mesh_obs_mask_in_selbox = obs_mask_2dbbox_entire_in_selbox
        mesh_obs_mask_in_selbox[obs_mask_check] = get_obs_mask_in_selbox(
            mesh_obs, obs_mask_check, depsgraph, region, rv3d, xmin, xmax, ymin, ymax
        )
        do_selection(mesh_obs_mask_in_selbox, mesh_obs, mode)

        nonmesh_ob_co_2d = get_ob_loc_co_2d(nonmesh_obs, region, rv3d)
        nonmesh_obs_mask_in_selbox = points_inside_rectangle(nonmesh_ob_co_2d, xmin, xmax, ymin, ymax)
        do_selection(nonmesh_obs_mask_in_selbox, nonmesh_obs, mode)

    if behavior == 'ORIGIN':
        ob_co_2d = get_ob_loc_co_2d(selectable_obs, region, rv3d)
        obs_mask_in_selbox = points_inside_rectangle(ob_co_2d, xmin, xmax, ymin, ymax)
        do_selection(obs_mask_in_selbox, selectable_obs, mode)
