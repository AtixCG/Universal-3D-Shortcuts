import bpy
from bpy.props import BoolProperty
from mathutils import Vector, Quaternion
from .. utils.registration import get_addon
from .. utils.math import flatten_matrix, get_loc_matrix, get_rot_matrix, get_sca_matrix




class Apply(bpy.types.Operator):
    bl_idname = "machin3.apply_transformations"
    bl_label = "MACHIN3: Apply Transformations"
    bl_description = "Apply Transformations while keeping the bevel width as well as the child transformations unchanged."
    bl_options = {'REGISTER', 'UNDO'}

    scale: BoolProperty(name="Scale", default=True)
    rotation: BoolProperty(name="Rotation", default=False)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row(align=True)
        row.prop(self, "scale", toggle=True)
        row.prop(self, "rotation", toggle=True)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.selected_objects

    def execute(self, context):
        if any([self.rotation, self.scale]):
            decalmachine, _, _, _ = get_addon("DECALmachine")

            apply_objs = [obj for obj in context.selected_objects if not obj.parent]

            for obj in apply_objs:

                children = [(child, child.matrix_world) for child in obj.children]

                mx = obj.matrix_world
                loc, rot, sca = mx.decompose()

                if self.rotation and self.scale:
                    meshmx = get_rot_matrix(rot) @ get_sca_matrix(sca)
                elif self.rotation:
                    meshmx = get_rot_matrix(rot)
                elif self.scale:
                    meshmx = get_sca_matrix(sca)

                obj.data.transform(meshmx)

                if self.rotation and self.scale:
                    applymx = get_loc_matrix(loc) @ get_rot_matrix(Quaternion()) @ get_sca_matrix(Vector.Fill(3, 1))
                elif self.rotation:
                    applymx = get_loc_matrix(loc) @ get_rot_matrix(Quaternion()) @ get_sca_matrix(sca)
                elif self.scale:
                    applymx = get_loc_matrix(loc) @ get_rot_matrix(rot) @ get_sca_matrix(Vector.Fill(3, 1))

                obj.matrix_world = applymx


                if self.scale:
                    mods = [mod for mod in obj.modifiers if mod.type == "BEVEL"]

                    for mod in mods:
                        vwidth = get_sca_matrix(sca) @ Vector((0, 0, mod.width))
                        mod.width = vwidth[2]


                for obj, mxw in children:
                    obj.matrix_world = mxw

                    if decalmachine and obj.DM.decalbackup:
                        backup = obj.DM.decalbackup
                        backup.DM.backupmx = flatten_matrix(meshmx @ backup.DM.backupmx)

        return {'FINISHED'}
