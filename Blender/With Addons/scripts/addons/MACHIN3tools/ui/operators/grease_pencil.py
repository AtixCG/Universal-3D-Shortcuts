import bpy
from ... utils.raycast import get_closest


class ShrinkwrapGreasePencil(bpy.types.Operator):
    bl_idname = "machin3.shrinkwrap_grease_pencil"
    bl_label = "MACHIN3: ShrinkWrap Grease Pencil"
    bl_description = "Shrinkwrap current Grease Pencil Layer to closest mesh surface based on Surface Offset value"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active = context.active_object
        if active and active.type == 'GPENCIL':
            return active.data.layers.active

    def execute(self, context):
        dg = context.evaluated_depsgraph_get()

        gp = context.active_object
        mx = gp.matrix_world
        offset = gp.data.zdepth_offset

        layer = gp.data.layers.active
        frame = layer.active_frame

        for stroke in frame.strokes:
            for idx, point in enumerate(stroke.points):
                closest, _, co, no, _, _ = get_closest(mx @ point.co, depsgraph=dg, debug=False)

                if closest:
                    point.co = mx.inverted_safe() @ (co + no * offset)

        return {'FINISHED'}
