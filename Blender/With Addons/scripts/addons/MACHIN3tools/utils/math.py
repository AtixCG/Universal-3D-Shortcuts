from mathutils import Matrix, Vector
from math import log10, floor



def dynamic_format(value, decimal_offset=0):
    if round(value, 6) == 0:
        return '0'

    l10 = log10(abs(value))
    f = floor(abs(l10))

    if l10 < 0:
        precision = f + 1 + decimal_offset

    else:
        precision = decimal_offset
    return f"{'-' if value < 0 else ''}{abs(value):.{precision}f}"



def get_center_between_points(point1, point2, center=0.5):
    return point1 + (point2 - point1) * center


def get_center_between_verts(vert1, vert2, center=0.5):
    return get_center_between_points(vert1.co, vert2.co, center=center)


def get_edge_normal(edge):
    return average_normals([f.normal for f in edge.link_faces])


def get_face_center(face, method='MEDIAN_WEIGHTED'):
    if method == 'BOUNDS':
        return face.calc_center_bounds()
    elif method == 'MEDIAN':
        return face.calc_center_median()
    elif method == 'MEDIAN_WEIGHTED':
        return face.calc_center_median_weighted()


def average_locations(locationslist, size=3):
    avg = Vector.Fill(size)

    for n in locationslist:
        avg += n

    return avg / len(locationslist)


def average_normals(normalslist):
    avg = Vector()

    for n in normalslist:
        avg += n

    return avg.normalized()



def flatten_matrix(mx):
    dimension = len(mx)
    return [mx[j][i] for i in range(dimension) for j in range(dimension)]


def compare_matrix(mx1, mx2, precision=4):

    round1 = [round(i, precision) for i in flatten_matrix(mx1)]
    round2 = [round(i, precision) for i in flatten_matrix(mx2)]
    return round1 == round2


def get_loc_matrix(location):
    return Matrix.Translation(location)


def get_rot_matrix(rotation):
    return rotation.to_matrix().to_4x4()


def get_sca_matrix(scale):
    scale_mx = Matrix()
    for i in range(3):
        scale_mx[i][i] = scale[i]
    return scale_mx


def create_rotation_matrix_from_vertex(obj, vert):
    mx = obj.matrix_world

    normal = mx.to_3x3() @ vert.normal

    if vert.link_edges:
        longest_edge = max([e for e in vert.link_edges], key=lambda x: x.calc_length())
        binormal = (mx.to_3x3() @ (longest_edge.other_vert(vert).co - vert.co)).normalized()

        tangent = binormal.cross(normal).normalized()

        binormal = normal.cross(tangent).normalized()

    else:
        objup = (mx.to_3x3() @ Vector((0, 0, 1))).normalized()

        dot = normal.dot(objup)
        if abs(round(dot, 6)) == 1:
            objup = (mx.to_3x3() @ Vector((1, 0, 0))).normalized()

        tangent = normal.cross(objup).normalized()
        binormal = normal.cross(tangent).normalized()

    rot = Matrix()
    rot[0].xyz = tangent
    rot[1].xyz = binormal
    rot[2].xyz = normal

    return rot.transposed()


def create_rotation_matrix_from_edge(obj, edge):
    mx = obj.matrix_world

    binormal = (mx.to_3x3() @ (edge.verts[1].co - edge.verts[0].co)).normalized()

    if edge.link_faces:
        normal = (mx.to_3x3() @ get_edge_normal(edge)).normalized()
        tangent = binormal.cross(normal).normalized()

        normal = tangent.cross(binormal).normalized()

    else:
        objup = (mx.to_3x3() @ Vector((0, 0, 1))).normalized()

        dot = binormal.dot(objup)
        if abs(round(dot, 6)) == 1:
            objup = (mx.to_3x3() @ Vector((1, 0, 0))).normalized()

        tangent = (binormal.cross(objup)).normalized()
        normal = tangent.cross(binormal)

    rotmx = Matrix()
    rotmx[0].xyz = tangent
    rotmx[1].xyz = binormal
    rotmx[2].xyz = normal

    return rotmx.transposed()


def create_rotation_matrix_from_face(mx, face):

    normal = (mx.to_3x3() @ face.normal).normalized()

    tangent = (mx.to_3x3() @ face.calc_tangent_edge_pair()).normalized()

    binormal = normal.cross(tangent)

    rot = Matrix()
    rot[0].xyz = tangent
    rot[1].xyz = binormal
    rot[2].xyz = normal

    return rot.transposed()


def create_rotation_difference_matrix_from_quat(v1, v2):
    q = v1.rotation_difference(v2)
    return q.to_matrix().to_4x4()


def create_selection_bbox(coords):
    minx = min(coords, key=lambda x: x[0])
    maxx = max(coords, key=lambda x: x[0])

    miny = min(coords, key=lambda x: x[1])
    maxy = max(coords, key=lambda x: x[1])

    minz = min(coords, key=lambda x: x[2])
    maxz = max(coords, key=lambda x: x[2])

    midx = get_center_between_points(minx, maxx)
    midy = get_center_between_points(miny, maxy)
    midz = get_center_between_points(minz, maxz)

    mid = Vector((midx[0], midy[1], midz[2]))

    bbox = [Vector((minx.x, miny.y, minz.z)), Vector((maxx.x, miny.y, minz.z)),
            Vector((maxx.x, maxy.y, minz.z)), Vector((minx.x, maxy.y, minz.z)),
            Vector((minx.x, miny.y, maxz.z)), Vector((maxx.x, miny.y, maxz.z)),
            Vector((maxx.x, maxy.y, maxz.z)), Vector((minx.x, maxy.y, maxz.z))]

    return bbox, mid


def get_right_and_up_axes(context, mx):
    r3d = context.space_data.region_3d

    view_right = r3d.view_rotation @ Vector((1, 0, 0))
    view_up = r3d.view_rotation @ Vector((0, 1, 0))

    axes_right = []
    axes_up = []

    for idx, axis in enumerate([Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))]):
        dot = view_right.dot(mx.to_3x3() @ axis)
        axes_right.append((dot, idx))

        dot = view_up.dot(mx.to_3x3() @ axis)
        axes_up.append((dot, idx))

    axis_right = max(axes_right, key=lambda x: abs(x[0]))
    axis_up = max(axes_up, key=lambda x: abs(x[0]))

    flip_right = True if axis_right[0] < 0 else False
    flip_up = True if axis_up[0] < 0 else False

    return axis_right[1], axis_up[1], flip_right, flip_up
