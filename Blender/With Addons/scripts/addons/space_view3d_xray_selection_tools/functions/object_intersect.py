from itertools import chain
from operator import attrgetter, methodcaller

import numpy as np

from .view3d import get_co_world_of_ob, get_co_world_of_mats, get_co_2d
from .selection import get_ob_selection_mask


def partition(items, predicate=bool):
    # https://nedbatchelder.com/blog/201306/filter_a_list_into_two_parts.html
    a, b = [], []
    for item in items:
        (a if predicate(item) else b).append(item)
    return a, b


def get_ob_2dbboxes(mesh_obs, mesh_ob_count, region, rv3d):
    ob_3dbbox_list = map(attrgetter("bound_box"), mesh_obs)
    ob_3dbbox_flat_list = chain.from_iterable(chain.from_iterable(ob_3dbbox_list))
    ob_3dbbox_co_local = np.fromiter(ob_3dbbox_flat_list, "f", mesh_ob_count * 24).reshape((mesh_ob_count, 8, 3))

    # Get object matrices.
    ob_mat_list = map(attrgetter("matrix_world"), mesh_obs)
    ob_mat_flat_list = chain.from_iterable(chain.from_iterable(ob_mat_list))
    ob_mats = np.fromiter(ob_mat_flat_list, "f", mesh_ob_count * 16).reshape((mesh_ob_count, 4, 4))

    # Get world space coordinates of 3d bboxes of objects.
    ob_3dbbox_co_world = get_co_world_of_mats(ob_mats, ob_3dbbox_co_local)

    # Get 2d coordinates of 3d bboxes of objects.
    ob_3dbbox_co_2d, ob_3dbbox_co_2d_mask_clip = get_co_2d(region, rv3d, ob_3dbbox_co_world, get_clipped=True)
    ob_3dbbox_co_2d.shape = (mesh_ob_count, 8, 2)
    ob_3dbbox_co_2d_mask_clip.shape = (mesh_ob_count, 8)

    # Get min max 2d coordinates.
    x = ob_3dbbox_co_2d[:, :, 0]
    y = ob_3dbbox_co_2d[:, :, 1]
    ob_2dbbox_xmin = np.amin(x, axis=1)
    ob_2dbbox_xmax = np.amax(x, axis=1)
    ob_2dbbox_ymin = np.amin(y, axis=1)
    ob_2dbbox_ymax = np.amax(y, axis=1)

    # Create 2d bboxes of objects.
    ob_2dbbox_points = np.column_stack(
        (
            ob_2dbbox_xmin,
            ob_2dbbox_ymin,
            ob_2dbbox_xmin,
            ob_2dbbox_ymax,
            ob_2dbbox_xmax,
            ob_2dbbox_ymax,
            ob_2dbbox_xmax,
            ob_2dbbox_ymin,
        )
    ).reshape((mesh_ob_count * 4, 2))

    # Create segments of object 2d bboxes.
    ob_2dbbox_segments = np.column_stack(
        (
            ob_2dbbox_xmin,
            ob_2dbbox_ymin,
            ob_2dbbox_xmin,
            ob_2dbbox_ymax,
            ob_2dbbox_xmin,
            ob_2dbbox_ymax,
            ob_2dbbox_xmax,
            ob_2dbbox_ymax,
            ob_2dbbox_xmax,
            ob_2dbbox_ymax,
            ob_2dbbox_xmax,
            ob_2dbbox_ymin,
            ob_2dbbox_xmax,
            ob_2dbbox_ymin,
            ob_2dbbox_xmin,
            ob_2dbbox_ymin,
        )
    ).reshape((mesh_ob_count * 4, 2, 2))

    # Get mask of entirely clipped bboxes.
    obs_mask_2dbbox_entire_clip = np.all(ob_3dbbox_co_2d_mask_clip, axis=1)

    return (
        ob_2dbbox_xmin,
        ob_2dbbox_xmax,
        ob_2dbbox_ymin,
        ob_2dbbox_ymax,
        ob_2dbbox_points,
        ob_2dbbox_segments,
        obs_mask_2dbbox_entire_clip,
    )


def get_vert_co_2d(me, ob, region, rv3d):
    """Look for verts inside the selection polygon path."""
    verts = me.vertices
    vert_count = len(verts)

    # Get local coordinates of vertices.
    vert_co_local = np.empty(vert_count * 3, "f")
    verts.foreach_get("co", vert_co_local)
    vert_co_local.shape = (vert_count, 3)

    # Get 2d coordinates of vertices.
    vert_co_world = get_co_world_of_ob(ob, vert_co_local)
    vert_co_2d = get_co_2d(region, rv3d, vert_co_world)
    return vert_co_2d


def get_edge_vert_co_2d(me, vert_co_2d):
    """Look for edges that intersect the selection polygon path."""
    edges = me.edges
    edge_count = len(edges)

    # For each edge get 2 indices of its vertices.
    edge_vert_indices = np.empty(edge_count * 2, "i")
    edges.foreach_get("vertices", edge_vert_indices)
    edge_vert_indices.shape = (edge_count, 2)

    # For each edge get 2 coordinates of its vertices.
    edge_vert_co_2d = vert_co_2d[edge_vert_indices]
    return edge_vert_co_2d


def get_face_vert_co_2d(me, vert_co_2d):
    """Look for faces."""
    faces = me.polygons
    face_count = len(faces)

    # Loops - edges that forms face polygons, sorted by polygon indices.
    loops = me.loops
    loop_count = len(loops)

    # Number of vertices for each face.
    face_loop_totals = np.empty(face_count, "i")
    faces.foreach_get("loop_total", face_loop_totals)

    # Sequence of vertices of all faces.
    face_vert_indices = np.zeros(loop_count, "i")
    faces.foreach_get("vertices", face_vert_indices)

    # Coordinates of vertices of faces.
    face_vert_co_2d = vert_co_2d[face_vert_indices]
    # Index of first face vert in face verts sequence.
    cumsum = face_loop_totals.cumsum()
    face_cell_starts = np.insert(cumsum[:-1], 0, 0)
    # Index of last face vert in face verts sequence.
    face_cell_ends = np.subtract(cumsum, 1)
    return face_vert_co_2d, face_cell_starts, face_cell_ends, face_loop_totals


def get_ob_loc_co_2d(obs, region, rv3d):
    """Get 2D coordinates of object location."""
    ob_co_world = map(attrgetter("location"), obs)
    ob_co_world = chain.from_iterable(ob_co_world)
    c = len(obs)
    ob_co_world = np.fromiter(ob_co_world, "f", c * 3).reshape((c, 3))
    ob_co_2d = get_co_2d(region, rv3d, ob_co_world)
    return ob_co_2d


def do_selection(mask_of_obs_to_select, obs_to_select, mode):
    obs_mask_selected = map(methodcaller("select_get"), obs_to_select)
    obs_mask_selected = np.fromiter(obs_mask_selected, "?")
    select = get_ob_selection_mask(obs_mask_selected, mask_of_obs_to_select, mode).tolist()
    for ob, sel in zip(obs_to_select, select):
        ob.select_set(sel)
