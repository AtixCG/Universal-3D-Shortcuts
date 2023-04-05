import bpy
from bpy.props import EnumProperty, BoolProperty
from mathutils import Vector


axis_items = [("0", "X", ""),
              ("1", "Y", ""),
              ("2", "Z", "")]



class SelectCenterObjects(bpy.types.Operator):
    bl_idname = "machin3.select_center_objects"
    bl_label = "MACHIN3: Select Center Objects"
    bl_description = "Selects Objects in the Center, objects, that have verts on both sides of the X, Y or Z axis."
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(name="Axis", items=axis_items, default="0")

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row()
        row.prop(self, "axis", expand=True)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        visible = [obj for obj in context.visible_objects if obj.type == "MESH"]

        if visible:

            bpy.ops.object.select_all(action='DESELECT')

            for obj in visible:
                mx = obj.matrix_world

                coords = [(mx @ Vector(co))[int(self.axis)] for co in obj.bound_box]

                if min(coords) < 0 and max(coords) > 0:
                    obj.select_set(True)

        return {'FINISHED'}


class SelectWireObjects(bpy.types.Operator):
    bl_idname = "machin3.select_wire_objects"
    bl_label = "MACHIN3: Select Wire Objects"
    bl_description = "Select Objects set to WIRE display type\nALT: Hide Objects\nCLTR: Include Empties"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return [obj for obj in context.visible_objects if obj.display_type in ['WIRE', 'BOUNDS'] or obj.type == 'EMPTY']

    def invoke(self, context, event):
        bpy.ops.object.select_all(action='DESELECT')

        for obj in context.visible_objects:
            if obj.display_type == '':
                obj.display_type = 'WIRE'


        if event.ctrl:
            objects = [obj for obj in context.visible_objects if obj.display_type in ['WIRE', 'BOUNDS'] or obj.type == 'EMPTY']
        else:
            objects = [obj for obj in context.visible_objects if obj.display_type in ['WIRE', 'BOUNDS']]

        for obj in objects:
            if event.alt:
                obj.hide_set(True)
            else:
                obj.select_set(True)

        return {'FINISHED'}


class SelectHierarchy(bpy.types.Operator):
    bl_idname = "machin3.select_hierarchy"
    bl_label = "MACHIN3: Select Hierarchy"
    bl_description = "Select Hierarchy Down"
    bl_options = {'REGISTER', 'UNDO'}

    include_parent: BoolProperty(name="Include Parent", description="Include the Parent in the Selection", default=False)

    recursive: BoolProperty(name="Select Recursive Children", description="Select Children Recursively", default=True)
    unhide: BoolProperty(name="Select Hidden Children", description="Unhide and Select Hidden Children", default=False)

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(self, 'include_parent', toggle=True)

        row = column.row(align=True)
        row.prop(self, 'recursive', text="Recursive", toggle=True)
        row.prop(self, 'unhide', text="Unhide", toggle=True)

    def invoke(self, context, event):

        return self.execute(context)

    def execute(self, context):
        view = context.space_data
        sel = context.selected_objects

        for obj in sel:
            if self.recursive:
                children = [(c, c.visible_get()) for c in obj.children_recursive if c.name in context.view_layer.objects]
            else:
                children = [(c, c.visible_get()) for c in obj.children if c.name in context.view_layer.objects]

            for c, vis in children:
                if self.unhide and not vis:
                    if view.local_view and not c.local_view_get(view):
                        c.local_view_set(view, True)

                    c.hide_set(False)

                c.select_set(True)

            obj.select_set(self.include_parent)


        return {'FINISHED'}
