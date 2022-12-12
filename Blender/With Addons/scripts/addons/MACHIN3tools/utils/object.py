import bpy
import bmesh
from mathutils import Matrix, Vector
from . math import flatten_matrix


def parent(obj, parentobj):
    if obj.parent:
        unparent(obj)

    obj.parent = parentobj
    obj.matrix_parent_inverse = parentobj.matrix_world.inverted_safe()


def unparent(obj):
    if obj.parent:
        omx = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = omx


def unparent_children(obj):
    children = []

    for c in obj.children:
        unparent(c)
        children.append(c)

    return children


def compensate_children(obj, oldmx, newmx):

    deltamx = newmx.inverted_safe() @ oldmx
    children = [c for c in obj.children]

    for c in children:
        pmx = c.matrix_parent_inverse
        c.matrix_parent_inverse = deltamx @ pmx


def flatten(obj, depsgraph=None):
    if not depsgraph:
        depsgraph = bpy.context.evaluated_depsgraph_get()

    oldmesh = obj.data

    obj.data = bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))
    obj.modifiers.clear()

    bpy.data.meshes.remove(oldmesh, do_unlink=True)


def add_vgroup(obj, name="", ids=[], weight=1, debug=False):
    vgroup = obj.vertex_groups.new(name=name)

    if debug:
        print(" » Created new vertex group: %s" % (name))

    if ids:
        vgroup.add(ids, weight, "ADD")

    else:
        obj.vertex_groups.active_index = vgroup.index
        bpy.ops.object.vertex_group_assign()

    return vgroup


def add_facemap(obj, name="", ids=[]):
    fmap = obj.face_maps.new(name=name)

    if ids:
        fmap.add(ids)

    return fmap


def set_obj_origin(obj, mx, bm=None, decalmachine=False, meshmachine=False):

    omx = obj.matrix_world.copy()

    children = [c for c in obj.children]
    compensate_children(obj, omx, mx)

    deltamx = mx.inverted_safe() @ obj.matrix_world

    obj.matrix_world = mx

    if bm:
        bmesh.ops.transform(bm, verts=bm.verts, matrix=deltamx)
        bmesh.update_edit_mesh(obj.data)
    else:
        obj.data.transform(deltamx)

    if obj.type == 'MESH':
        obj.data.update()

    if decalmachine and children:

        for c in [c for c in children if c.DM.isdecal and c.DM.decalbackup]:
            backup = c.DM.decalbackup
            backup.DM.backupmx = flatten_matrix(deltamx @ backup.DM.backupmx)

    if meshmachine:

        for stash in obj.MM.stashes:

            if getattr(stash, 'version', False) and float('.'.join([v for v in stash.version.split('.')[:2]])) >= 0.7:
                stashdeltamx = stash.obj.MM.stashdeltamx

                if stash.self_stash:
                    if stash.obj.users > 2:
                        print(f"INFO: Duplicating {stash.name}'s stashobj {stash.obj.name} as it's used by multiple stashes")

                        dup = stash.obj.copy()
                        dup.data = stash.obj.data.copy()
                        stash.obj = dup

                stash.obj.MM.stashdeltamx = flatten_matrix(deltamx @ stashdeltamx)
                stash.obj.MM.stashorphanmx = flatten_matrix(mx)



                stash.self_stash = False

            else:
                stashdeltamx = stash.obj.MM.stashtargetmx.inverted_safe() @ stash.obj.MM.stashmx

                stash.obj.MM.stashmx = flatten_matrix(omx @ stashdeltamx)
                stash.obj.MM.stashtargetmx = flatten_matrix(mx)

            stash.obj.data.transform(deltamx)
            stash.obj.matrix_world = mx


def get_eval_bbox(obj):
    return [Vector(co) for co in obj.bound_box]
