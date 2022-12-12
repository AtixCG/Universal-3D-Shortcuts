# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import mathutils
import time
import numpy
import math
import random

bl_info = {
    "name": "Drop It",
    "author": "Andreas Aust",
    "version": (1, 2),
    "blender": (2, 80, 0),
    "location": "View3D > Object Mode > Object Context Menu (W / Right Click on Object)",
    "description": "Drop Objects to Ground or Surface",
    "warning": "",
    "doc_url": "",
    "tracker_url": "https://blenderartists.org/t/drop-it-free-addon/1244259",
    "category": "Object",
}


dgraph = None


class DROPIT_OT_drop_it(bpy.types.Operator):
    """Drop to Ground or Surface"""
    bl_idname = "object.drop_it"
    bl_label = "Drop It"
    bl_options = {'REGISTER', 'UNDO'}

    drop_by: bpy.props.EnumProperty(
        name="",
        description="Drop by lowest Vertex or Origin",
        items=[
            ("lw_vertex", "Lowest Vertex", ""),
            ("origin", "Origin", "")]
    )

    col_in_sel: bpy.props.BoolProperty(
        name="Collision in Selection",
        description="Collision for selected Objects",
        default=True
    )

    affect_parenting: bpy.props.BoolProperty(
        name="Parenting Settings",
        description="Affect Parent and Child Connection",
        default=False
    )

    affect_only_parents: bpy.props.BoolProperty(
        name="Affect Only Parents",
        description="Affect the Parents, leaving the Children in Place",
        default=False
    )

    affect_sel_childs: bpy.props.BoolProperty(
        name="Affect Selected Children",
        description="Affect Selected Children",
        default=False
    )

    bpy.types.WindowManager.surf_align = bpy.props.BoolProperty(
        default=True)

    rand_zrot: bpy.props.IntProperty(
        name="Rotation:",
        description="Random Local Z Angle, between -Z  and +Z",
        default=0,
        min=0,
        max=360,
        subtype='ANGLE'
    )

    rand_loc: bpy.props.FloatProperty(
        name="Location:",
        description="Random Radius for XY Local Location",
        default=0,
        min=0,
        max=100,
        subtype='DISTANCE'
    )

    offset_z: bpy.props.FloatProperty(
        name="Offset Z Location:",
        description="Offset Local Z Location",
        default=0,
        min=-10,
        max=10,
        subtype='DISTANCE'
    )

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and context.mode == 'OBJECT' and context.area.type == 'VIEW_3D'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        col.label(text="Drop By:")
        row = layout.row()
        row.prop(self, "drop_by")
        row.prop(self, "col_in_sel")
        for i in range(10):
            layout.column()

        col = layout.column(align=True)
        col.label(text="Random:")
        row = layout.row()
        row.prop(self, "rand_zrot")
        row.prop(self, "rand_loc")
        layout.prop(self, "offset_z")

        layout.column()
        layout.column()
        layout.prop(self, "affect_parenting", icon='LINKED')

        if self.affect_parenting:
            col = layout.column(align=True)
            col.prop(self, "affect_only_parents")
            col.prop(self, "affect_sel_childs")

            if self.affect_only_parents:
                self.affect_sel_childs = False

        wm = context.window_manager
        if wm.surf_align:
            label = "Align To Surface"
            ic = 'GIZMO'
        else:
            label = "No Align"
            ic = 'ORIENTATION_VIEW'
        layout.prop(wm, 'surf_align', text=label, toggle=True, icon=ic)

    def execute(self, context):
        time_start = time.time()
        objs = context.selected_objects
        view_layer = context.view_layer

        # CHECK RAYCAST APP VERSION
        global dgraph
        dgraph = context.view_layer
        if bpy.app.version >= (2, 91, 0):
            dgraph = dgraph.depsgraph

        if len(objs) > 1:
            # HIDE ALL SELECTED TO IGNORE SELF HIT
            if not self.col_in_sel:
                for obj in objs:
                    obj.hide_set(True)
            else:
                # SORT SELECTION BY LOC Z TO START HIT FROM BOTTOM TO TOP
                objs_sorted = [(obj, obj.location.z) for obj in objs]
                objs_sorted = sorted(objs_sorted, key=lambda os: os[1])
                objs = [obj[0] for obj in objs_sorted]

        for obj in objs:
            if obj.type == 'MESH' or obj.type == 'EMPTY':

                parent = None
                children = []
                hidden_objs = []
                obj_rot_z = obj.rotation_euler[2]

                # IGNORE SELECTED CHILDREN IF ENABLED
                if not self.affect_sel_childs and obj.parent:
                    continue

                # AFFECT ONLY PARENTS IF ENABLED
                if self.affect_only_parents:
                    if obj.children:
                        children = obj.children
                        for child in children:
                            unparent(child)
                    else:
                        continue

                # AFFECT ONLY SElECTED CHILDS IF ENABLED
                if self.affect_sel_childs:
                    if obj.children:
                        for child in obj.children:
                            if child in objs:
                                children.append(child)
                                unparent(child)

                # IF IS CHILD UNPARENT FOR CORRECT TRANSFORMATION
                if obj.parent:
                    parent = obj.parent
                    unparent(obj)

                # RESET ROTATION FOR CORRECT ALIGN
                if context.window_manager.surf_align:
                    obj.rotation_euler = mathutils.Euler()

                # RANDOM LOCATION RADIUS
                if self.rand_loc > 0:
                    x = random.uniform(-self.rand_loc, self.rand_loc)
                    y = random.uniform(-self.rand_loc, self.rand_loc)
                    obj.location.x += x
                    obj.location.y += y

                # UPDATE MATRIX
                view_layer.update()

                # GET LOWEST VERTICES OR ORIGIN
                if self.drop_by == "lw_vertex":
                    # DROP BY LOWEST VERTEX
                    lowest_verts = get_lowest_verts(obj)
                else:
                    lowest_verts = [obj.location]

                hidden_objs.append(obj)
                obj.hide_set(True)

                # IGNORE RAYCAST FOR OWN CHILDS
                if obj.children:
                    for child in obj.children:
                        if not child.hide_get():
                            hidden_objs.append(child)
                            child.hide_set(True)

                hit_info = {}

                # LINE CAST FROM LOW VERTS
                for co in lowest_verts:
                    cast = raycast(context, co.copy())
                    if cast is not None:
                        hit_info.update(cast)
                #print("hit_info", hit_info)
                # SET LOCATION Z BY DIST FROM HIT
                dist = 0
                hitloc_nrm = (0, 0)
                if len(hit_info) == 0:
                    dist = lowest_verts[0][2]
                    hitloc_nrm = (lowest_verts[0], mathutils.Vector((0, 0, 1)))
                else:
                    # GET MIN HIT DIST AND NRM
                    dist = min(hit_info.keys())
                    hitloc_nrm = hit_info.get(dist)

                obj.location.z -= (dist)
                view_layer.update()

                # ROTATE TO HIT NORMAL
                if context.window_manager.surf_align:
                    rotate_object(obj, hitloc_nrm[0], hitloc_nrm[1])
                    obj.rotation_euler.rotate_axis('Z', obj_rot_z)
                    # view_layer.update()

                # RANDOM Z ROTATION
                if self.rand_zrot > 0:
                    obj.rotation_euler.rotate_axis(
                        'Z', math.radians(random.randrange(-self.rand_zrot, self.rand_zrot)))
                    # view_layer.update()

                # ADD LOCAl Z OFFSET LOCATION
                if self.offset_z != 0:
                    vec = mathutils.Vector((0.0, 0.0, self.offset_z))
                    local_loc = vec @ obj.matrix_world.inverted()
                    obj.location += local_loc
                    # view_layer.update()

                # SET PARENT IF AVAILABLE
                if parent:
                    set_parent(parent, obj)
                    # view_layer.update()

                # SET CHILDS IF AVAILABLE
                if children:
                    for child in children:
                        set_parent(obj, child)
                    # view_layer.update()

                # RESET VISIBILITY FOR HIDDEN CHILDS
                if hidden_objs:
                    for o in hidden_objs:
                        o.hide_set(False)
                        o.select_set(True)

                view_layer.update()

        if not self.col_in_sel:
            for obj in objs:
                obj.hide_set(False)
                obj.select_set(True)

        print("Drop It, calculation time: ",
              str(time.time() - time_start))

        return {'FINISHED'}


def set_parent(parent, child):
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def unparent(obj):
    mxw_obj = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_world = mxw_obj


def rotate_object(obj, loc, normal):
    up = mathutils.Vector((0, 0, 1))
    angle = normal.angle(up)
    direction = up.cross(normal)

    R = mathutils.Matrix.Rotation(angle, 4, direction)
    T = mathutils.Matrix.Translation(loc)
    M = T @ R @ T.inverted()

    obj.location = M @ obj.location
    obj.rotation_euler.rotate(M)


def get_lowest_verts(obj):
    verts = obj.data.vertices
    count = len(verts)
    co = numpy.zeros(count * 3, dtype=numpy.float32)
    verts.foreach_get("co", co)
    co.shape = (count, 3)

    mtxw = numpy.array(obj.matrix_world)
    mtxw2 = mtxw[: 3, : 3].T
    loc = mtxw[: 3, 3]
    co_world = co @ mtxw2 + loc

    co_z_all = co_world[:, 2]
    co_z_min = co_z_all.min()
    co_z_all_idx = numpy.where(co_world == co_z_min)
    co_low_all = co_world[co_z_all_idx[0]]

    # RETURN LOWEST Z LOC
    count = len(co_low_all)
    if count == -1:
        return co_low_all

    # GET CENTER OF SAME Z LEVEL VERTS
    # APPEND TO ARRAY
    else:
        x = co_low_all[:, 0]
        x = x.sum() / len(x)
        y = co_low_all[:, 1]
        y = y.sum() / len(y)

        low_center = mathutils.Vector((x, y, co_z_min))
        co_low_all = numpy.append(co_low_all, low_center)
        co_low_all.shape = (count + 1, 3)

        return co_low_all


def raycast(context, origin):
    _origin = origin
    _origin[2] -= 0  # 0.0001

    cast = context.scene.ray_cast(dgraph, _origin, (0, 0, -1), distance=1000)

    if cast[0] == False:
        return None

    hitloc = cast[1]
    nrm = cast[2]
    dist = origin[2] - hitloc[2]
    return {dist: (hitloc, nrm)}


classes = [
    DROPIT_OT_drop_it
]


def draw_inmenu(self, context):
    self.layout.operator("object.drop_it", text="Drop It", icon='SORT_ASC')


addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.append(draw_inmenu)

    # KEYMAP
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new("object.drop_it", 'V', 'PRESS')
    addon_keymaps.append((km, kmi))


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_inmenu)

    # KEYMAP
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
