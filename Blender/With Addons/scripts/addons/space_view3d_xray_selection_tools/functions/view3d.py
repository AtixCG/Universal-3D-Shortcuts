import numpy as np


def get_co_world_of_ob(ob, co_local):
    """Get global coordinates of points in object space."""
    mat_world = np.array(ob.matrix_world)
    mat = mat_world[:3, :3].T  # rotates backwards without T
    loc = mat_world[:3, 3]
    co_world = co_local @ mat + loc
    return co_world


def get_co_world_of_mats(mat_world, co_local):
    """Get global coordinates of points in multiple object spaces."""
    mat = mat_world[:, :3, :3]
    mat = mat.transpose((0, 2, 1))  # rotates backwards without T
    loc = mat_world[:, :3, 3]
    co_world = co_local @ mat + loc[:, None]
    co_world.shape = (-1, 3)
    return co_world


def get_co_2d(region, rv3d, co_world, get_clipped=False):
    """Get 2D coordinates of points."""
    # https://blender.stackexchange.com/questions/6155/how-to-convert-coordinates-from-vertex-to-world-space
    # \scripts\modules\bpy_extras\view3d_utils.py location_3d_to_region_2d

    # Get projection.
    rv3d_mat = np.array(rv3d.perspective_matrix)
    c = co_world.shape[0]
    co_world_4d = np.column_stack([co_world, np.ones((c, 1), "f")])
    prj = (rv3d_mat @ co_world_4d.T).T

    # Get 2d co.
    width_half = region.width / 2.0
    height_half = region.height / 2.0
    prj_w = prj[:, 3]  # negative if coord is behind the origin of a perspective view

    if get_clipped:
        mask_clip = prj_w <= 0
        prj_w = np.abs(prj_w)
        co_2d = np.empty((c, 2), "f")
        co_2d[:, 0] = width_half * (1 + (prj[:, 0] / prj_w))
        co_2d[:, 1] = height_half * (1 + (prj[:, 1] / prj_w))
        return co_2d, mask_clip
    else:
        co_2d = np.empty((c, 2), "f")
        co_2d[:, 0] = width_half * (1 + (prj[:, 0] / prj_w))
        co_2d[:, 1] = height_half * (1 + (prj[:, 1] / prj_w))
        co_2d[prj_w <= 0] = np.nan
        return co_2d
