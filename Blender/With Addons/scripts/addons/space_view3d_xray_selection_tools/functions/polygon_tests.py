import numpy as np


def circle_bbox(center, radius):
    """Return a bounding box of a circle."""
    xmin = center[0] - radius
    xmax = center[0] + radius
    ymin = center[1] - radius
    ymax = center[1] + radius
    return xmin, xmax, ymin, ymax


def polygon_bbox(poly):
    """Return a bounding box of a polygon."""
    np_poly = np.array(poly, "f")
    xmin = np.amin(np_poly[:, 0])
    xmax = np.amax(np_poly[:, 0])
    ymin = np.amin(np_poly[:, 1])
    ymax = np.amax(np_poly[:, 1])
    return xmin, xmax, ymin, ymax


def point_inside_rectangles(co, xmin, xmax, ymin, ymax):
    """Return a boolean mask of rectangles that have a single given point inside their area."""
    x, y = co
    with np.errstate(invalid="ignore"):
        return (xmin < x) & (x < xmax) & (ymin < y) & (y < ymax)


def points_inside_rectangle(co, xmin, xmax, ymin, ymax):
    """Return a boolean mask of points that lie inside a border of a given rectangle."""
    x = co[:, 0]
    y = co[:, 1]
    with np.errstate(invalid="ignore"):
        return (xmin < x) & (x < xmax) & (ymin < y) & (y < ymax)


def segments_completely_outside_rectangle(segments, xmin, xmax, ymin, ymax):
    """Return a boolean mask of segments that lie completely outside rectangle"""
    v1x = segments[:, 0, 0]
    v1y = segments[:, 0, 1]
    v2x = segments[:, 1, 0]
    v2y = segments[:, 1, 1]

    with np.errstate(invalid="ignore"):
        return (
            np.isnan(v1x) | np.isnan(v2x)
            | (v1x < xmin) & (v2x < xmin)
            | (v1x > xmax) & (v2x > xmax)
            | (v1y < ymin) & (v2y < ymin)
            | (v1y > ymax) & (v2y > ymax)
        )


def segments_intersect_rectangle(segment_co, xmin, xmax, ymin, ymax, prefilter=False):
    """Return a boolean mask of segments that intersect rectangle."""

    # Limit search.
    all_segments_mask_isect = segments_mask_prefilter = None
    if prefilter:
        all_segments_mask_isect = np.full(segment_co.shape[0], False, "?")
        segments_mask_prefilter = ~segments_completely_outside_rectangle(segment_co, xmin, xmax, ymin, ymax)
        if np.any(segments_mask_prefilter):
            segment_co = segment_co[segments_mask_prefilter]
        else:
            return all_segments_mask_isect

    # https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/editors/space_view3d/view3d_select.c#L477 # noqa
    v1x = segment_co[:, 0, 0]
    v1y = segment_co[:, 0, 1]
    v2x = segment_co[:, 1, 0]
    v2y = segment_co[:, 1, 1]

    dx0 = v2x - v1x
    dy0 = v1y - v2y

    dx1 = v1x - xmin
    dx2 = v1x - xmax
    dy1 = v1y - ymin
    dy2 = v1y - ymax

    d1 = dy0 * dx1 + dx0 * dy1
    d2 = dy0 * dx1 + dx0 * dy2
    d3 = dy0 * dx2 + dx0 * dy2
    d4 = dy0 * dx2 + dx0 * dy1

    # Need to be used with prefiltering segments outside rectangle.
    with np.errstate(invalid="ignore"):
        segments_mask_not_isect = (
            np.isnan(v1x) | np.isnan(v2x)
            | ((d1 < 0) & (d2 < 0) & (d3 < 0) & (d4 < 0))
            | ((d1 > 0) & (d2 > 0) & (d3 > 0) & (d4 > 0))
        )

    if prefilter:
        all_segments_mask_isect[segments_mask_prefilter] = ~segments_mask_not_isect
        return all_segments_mask_isect

    return ~segments_mask_not_isect


def points_inside_circle(co, center, radius):
    with np.errstate(invalid="ignore"):
        return ((co[:, 0] - center[0]) ** 2 + (co[:, 1] - center[1]) ** 2) ** 0.5 <= radius


def segments_inside_or_intersect_circle(segment_co, center, radius, prefilter=False):
    """Return a boolean mask of segments that intersect circle or fully inside circle."""

    # Limit search to circle bounding box.
    all_segments_mask_isect = segments_mask_prefilter = None
    if prefilter:
        all_segments_mask_isect = np.full(segment_co.shape[0], False, "?")
        xmin, xmax, ymin, ymax = circle_bbox(center, radius)
        segments_mask_prefilter = ~segments_completely_outside_rectangle(segment_co, xmin, xmax, ymin, ymax)
        if np.any(segments_mask_prefilter):
            segment_co = segment_co[segments_mask_prefilter]
        else:
            return all_segments_mask_isect

    # https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/editors/space_view3d/view3d_select.c#L2595
    # https://github.com/dfelinto/blender/blob/c4ef90f5a0b1d05b16187eb6e32323defe6461c0/source/blender/blenlib/intern/math_geom.c#L338
    # https://github.com/dfelinto/blender/blob/c4ef90f5a0b1d05b16187eb6e32323defe6461c0/source/blender/blenlib/intern/math_geom.c#L3364
    # https://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment/6853926#6853926
    x1 = segment_co[:, 0, 0]
    y1 = segment_co[:, 0, 1]
    x2 = segment_co[:, 1, 0]
    y2 = segment_co[:, 1, 1]
    cx, cy = center

    # closest_to_line
    # Find the closest point to circle center on line through x,y and find param
    # where (0 <= param <= 1) when cp is in the line segment x-y.
    ux = x2 - x1
    uy = y2 - y1
    hx = cx - x1
    hy = cy - y1
    dot = ux * hx + uy * hy
    len_sq = ux**2 + uy**2
    # len_sq == 0 case of 0 length line
    param = np.divide(dot, len_sq, out=np.full_like(dot, -1), where=len_sq != 0)
    param[np.isnan(param)] = -1

    cp_x = x1 + ux * param
    cp_y = y1 + uy * param

    # closest_to_line_segment
    # Point closest to circle center on line segment x-y.
    bound1 = param < 0
    bound2 = param > 1
    cp_x[bound1] = x1[bound1]
    cp_y[bound1] = y1[bound1]
    cp_x[bound2] = x2[bound2]
    cp_y[bound2] = y2[bound2]

    # dist_squared_to_line_segment
    # Distance circle center to line-piece x-y.
    dx = cx - cp_x
    dy = cy - cp_y
    len_squared = dx**2 + dy**2

    # Segments intersect circle.
    with np.errstate(invalid="ignore"):
        segments_mask_isect = len_squared < radius**2

    if prefilter:
        all_segments_mask_isect[segments_mask_prefilter] = segments_mask_isect
        return all_segments_mask_isect

    return segments_mask_isect


def point_inside_polygons(co, poly_vert_co, poly_cell_starts, poly_cell_ends, poly_loop_totals, prefilter=False):
    """Return a boolean mask of polygons that have a single given point inside their area."""

    # Limit search to poly bounding box.
    all_polys_mask_under = polys_mask_prefilter = None
    if prefilter:
        all_polys_mask_under = np.full(poly_loop_totals.size, False, "?")
        # Polygon bboxes.
        # If polygon has nan vert than bbox is composed of nan.
        poly_vert_co_x = poly_vert_co[:, 0]
        poly_vert_co_y = poly_vert_co[:, 1]
        xmin = np.minimum.reduceat(poly_vert_co_x, poly_cell_starts)
        xmax = np.maximum.reduceat(poly_vert_co_x, poly_cell_starts)
        ymin = np.minimum.reduceat(poly_vert_co_y, poly_cell_starts)
        ymax = np.maximum.reduceat(poly_vert_co_y, poly_cell_starts)
        # Mask of polygons that have point in their bbox.
        polys_mask_prefilter = point_inside_rectangles(co, xmin, xmax, ymin, ymax)

        if np.any(polys_mask_prefilter):
            # Number of verts of each prefiltered polygon.
            prefilter_poly_loop_totals = poly_loop_totals[polys_mask_prefilter]
            # Mask of prefiltered verts of polygons.
            poly_verts_mask_prefilter = np.repeat(polys_mask_prefilter, poly_loop_totals)

            poly_vert_co = poly_vert_co[poly_verts_mask_prefilter]
            # Index of first and last polygon vertex in polygon verts sequence.
            cumsum = prefilter_poly_loop_totals.cumsum()
            poly_cell_starts = np.insert(cumsum[:-1], 0, 0)
            poly_cell_ends = np.subtract(cumsum, 1)
        else:
            return all_polys_mask_under

    # Get coordinates of verts to calculate intersections
    # [0, 1, 2, 3], [0, 1, 2, 3, 4], [0, 1, 2] polygons example
    # [0, 1, 2, 3, 0, 1, 2, 3, 4, 0, 1, 2] first vertex indices example
    # [0, 1, 2, 4, 0, 1, 2, 3, 2, 0, 1, 3] second vertex indices example after replacing
    # [3, 0, 1, 2, 4, 0, 1, 2, 3, 2, 0, 1] second vertex indices example after roll
    # Replacing example:
    # p2[3] = p1[8]
    # p2[8] = p1[11]
    # p2[11] = p1[3]
    # Then roll

    mask1 = poly_cell_ends
    mask2 = np.roll(mask1, 1)

    p1 = poly_vert_co
    p2 = p1.copy()
    p2[mask2] = p1[mask1]
    p2 = np.roll(p2, 1, axis=0)

    x, y = co
    p1x = p1[:, 0]
    p1y = p1[:, 1]
    p2x = p2[:, 0]
    p2y = p2[:, 1]

    # https://en.wikipedia.org/wiki/Even–odd_rule
    # https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html
    # https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/blenlib/intern/math_geom.c#L1541
    with np.errstate(invalid="ignore", divide="ignore"):
        vert_odd_even = ((p1y > y) != (p2y > y)) & (x < (p2x - p1x) * (y - p1y) / (p2y - p1y) + p1x)
    poly_odd_even = np.add.reduceat(vert_odd_even, poly_cell_starts)
    polys_mask_under = poly_odd_even % 2 == 1

    if prefilter:
        all_polys_mask_under[polys_mask_prefilter] = polys_mask_under
        return all_polys_mask_under

    return polys_mask_under


def points_inside_polygon(co, poly, prefilter=False):
    """Return a boolean mask of points that lie within a single given polygon, ray casting method."""
    # https://stackoverflow.com/questions/36399381/whats-the-fastest-way-of-checking-if-a-point-is-inside-a-polygon-in-python # noqa
    # http://geospatialpython.com/2011/01/point-in-polygon.html
    # https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/blenlib/intern/math_geom.c#L1542

    # Limit poly search to points within poly bounding box.
    all_points_mask_in = points_mask_prefilter = None
    if prefilter:
        all_points_mask_in = np.full(co.shape[0], False, "?")
        xmin, xmax, ymin, ymax = polygon_bbox(poly)
        points_mask_prefilter = points_inside_rectangle(co, xmin, xmax, ymin, ymax)
        if np.any(points_mask_prefilter):
            co = co[points_mask_prefilter]
        else:
            return all_points_mask_in

    x = co[:, 0]
    y = co[:, 1]

    np_poly = np.array(poly, "f")
    poly1 = np_poly
    poly2 = np.roll(np_poly, 2)

    points_mask_in = np.full(co.shape[0], False, "?")

    def loop(p1x, p1y, p2x, p2y):
        xints = 0.0

        with np.errstate(invalid="ignore"):
            idx = np.nonzero((y > min(p1y, p2y)) & (y <= max(p1y, p2y)) & (x <= max(p1x, p2x)))[0]

        if idx.size > 0:
            if p1y != p2y:
                xints = (y[idx] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x:
                points_mask_in[idx] = ~points_mask_in[idx]
            else:
                idxx = idx[x[idx] <= xints]
                points_mask_in[idxx] = ~points_mask_in[idxx]

    np.frompyfunc(loop, 4, 1)(poly1[:, 0], poly1[:, 1], poly2[:, 0], poly2[:, 1])

    if prefilter:
        all_points_mask_in[points_mask_prefilter] = points_mask_in
        return all_points_mask_in

    return points_mask_in


def segments_intersect_polygon(segment_co, poly, prefilter=False):
    """Return a boolean mask of segments that intersect polygon."""

    # Limit search to poly bounding box.
    full_segments_mask_isect = segments_mask_prefilter = None
    if prefilter:
        full_segments_mask_isect = np.full(segment_co.shape[0], False, "?")
        xmin, xmax, ymin, ymax = polygon_bbox(poly)
        segments_mask_prefilter = ~segments_completely_outside_rectangle(segment_co, xmin, xmax, ymin, ymax)
        if np.any(segments_mask_prefilter):
            segment_co = segment_co[segments_mask_prefilter]
        else:
            return full_segments_mask_isect

    s1x = segment_co[:, 0, 0]
    s1y = segment_co[:, 0, 1]
    s2x = segment_co[:, 1, 0]
    s2y = segment_co[:, 1, 1]

    poly_sides = len(poly)
    np_poly = np.array(poly, "f")
    poly1 = np_poly
    poly2 = np.roll(np_poly, 2)

    def loop(p1x, p1y, p2x, p2y):
        # https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/blenlib/intern/lasso_2d.c#L69  # noqa
        # https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/blenlib/intern/math_geom.c#L1105  # noqa

        dx0 = s1x - p1x
        dy0 = s1y - p1y
        dx1 = s2x - s1x
        dy1 = s2y - s1y
        dx2 = p2x - p1x
        dy2 = p2y - p1y

        div = dx1 * dy2 - dy1 * dx2
        with np.errstate(invalid="ignore", divide="ignore"):
            param = (dy0 * dx2 - dx0 * dy2) / div
        with np.errstate(invalid="ignore", divide="ignore"):
            mu = (dy0 * dx1 - dx0 * dy1) / div
        with np.errstate(invalid="ignore"):
            poly_segments_mask_isect_segment = (0.0 <= param) & (param <= 1.0) & (0.0 <= mu) & (mu <= 1.0)

        return poly_segments_mask_isect_segment

    poly_segments_mask_isect_segments = np.frompyfunc(loop, 4, 1)(poly1[:, 0], poly1[:, 1], poly2[:, 0], poly2[:, 1])
    poly_segments_mask_isect_segments = np.hstack(poly_segments_mask_isect_segments)
    poly_segments_mask_isect_segments.shape = (poly_sides, segment_co.shape[0])
    segments_mask_isect = np.any(poly_segments_mask_isect_segments, axis=0)

    if prefilter:
        full_segments_mask_isect[segments_mask_prefilter] = segments_mask_isect
        return full_segments_mask_isect

    return segments_mask_isect
