import bpy
from bpy.props import StringProperty, BoolProperty


class SetSnappingPreset(bpy.types.Operator):
    bl_idname = "machin3.set_snapping_preset"
    bl_label = "MACHIN3: Set Snapping Preset"
    bl_description = "Set Snapping Preset"
    bl_options = {'REGISTER', 'UNDO'}

    element: StringProperty(name="Snap Element")
    target: StringProperty(name="Snap Target")
    align_rotation: BoolProperty(name="Align Rotation")

    def draw(self, context):
        layout = self.layout
        column = layout.column()

    @classmethod
    def description(cls, context, properties):

        if properties.element == 'VERTEX':
            return "Snap to Vertices"

        elif properties.element == 'EDGE':
            return "Snap to Edges"

        elif properties.element == 'FACE' and properties.align_rotation:
            return "Snap to Faces and Align the Rotation"

        elif properties.element == 'INCREMENT':
            return "Snap to Absolute Grid Points"

        elif properties.element == 'VOLUME':
            return "Snap to Volumes"

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D'

    def execute(self, context):
        ts = context.scene.tool_settings

        ts.snap_elements = {self.element}

        if self.element == 'INCREMENT':
            ts.use_snap_grid_absolute = True

        elif self.element == 'VOLUME':
            pass

        else:
            ts.snap_target = self.target
            ts.use_snap_align_rotation = self.align_rotation

        return {'FINISHED'}
