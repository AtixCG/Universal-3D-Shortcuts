import bpy
from bpy.props import FloatProperty, EnumProperty, BoolProperty
import random
from ... utils.registration import get_addon
from ... utils.material import get_last_node, lighten_color
from ... colors import group_colors



class ColorizeMaterials(bpy.types.Operator):
    bl_idname = "machin3.colorize_materials"
    bl_label = "MACHIN3: Colorize Materials"
    bl_description = "Set Material Viewport Colors from last Node in Material"
    bl_options = {'REGISTER', 'UNDO'}

    lighten_amount: FloatProperty(name="Lighten", default=0.05, min=0, max=1)

    @classmethod
    def poll(cls, context):
        return bpy.data.materials

    def execute(self, context):
        for mat in bpy.data.materials:
            node = get_last_node(mat)

            if node:
                color = node.inputs.get("Base Color")

                if not color:
                    color = node.inputs.get("Color")

                if color:
                    mat.diffuse_color = lighten_color(color=color.default_value, amount=self.lighten_amount)

        return {'FINISHED'}


class ColorizeObjectsFromMaterials(bpy.types.Operator):
    bl_idname = "machin3.colorize_objects_from_materials"
    bl_label = "MACHIN3: Colorize Objects from Materials"
    bl_description = "Set Object Viewport Colors of selected Objects from their active Materials"
    bl_options = {'REGISTER', 'UNDO'}

    lighten_amount: FloatProperty(name="Lighten", default=0.05, min=0, max=1)

    @classmethod
    def poll(cls, context):
        return [obj for obj in context.selected_objects if obj.type != 'EMPTY']

    def execute(self, context):
        objects = [obj for obj in context.selected_objects if obj.type != 'EMPTY']

        for obj in objects:
            mat = obj.active_material

            if mat:
                node = get_last_node(mat)

                if node:
                    color = node.inputs.get("Base Color")

                    if not color:
                        color = node.inputs.get("Color")

                    if color:
                        obj.color = lighten_color(color=color.default_value, amount=self.lighten_amount)

        return {'FINISHED'}


class ColorizeObjectsFromActive(bpy.types.Operator):
    bl_idname = "machin3.colorize_objects_from_active"
    bl_label = "MACHIN3: Colorize Objects from Active"
    bl_description = "Set Object Viewport Colors from Active Object"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.selected_objects

    def execute(self, context):
        active = context.active_object

        for obj in context.selected_objects:
            obj.color = active.color

        return {'FINISHED'}


multi_collection_items = [("LEAST", "Least", ""),
                          ("MOST", "Most", "")]


decal_collection_items = [("TYPE", "Type", ""),
                          ("PARENT", "Parent", ""),
                          ("IGNORE", "Ignore", "")]



class ColorizeObjectsFromCollections(bpy.types.Operator):
    bl_idname = "machin3.colorize_objects_from_collections"
    bl_label = "MACHIN3: Colorize Objects from Collections"
    bl_description = "Set Object Viewport Colors of selected Objects based on Collections"
    bl_options = {'REGISTER', 'UNDO'}

    multiple: EnumProperty(name="Multiple Collections", items=multi_collection_items, default="MOST")

    decalmachine: EnumProperty(name="DECALmachine Collections", items=decal_collection_items, default="TYPE")


    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.split(factor=0.5)
        row.label(text="Multi-Collection Objects")
        r = row.row()
        r.prop(self, "multiple", expand=True)

        if self.dm:
            row = column.split(factor=0.5)
            row.label(text="Decal Collections")
            r = row.row()
            r.prop(self, "decalmachine", expand=True)

        column.label(text=self.msg, icon='INFO')


    @classmethod
    def poll(cls, context):
        return context.selected_objects


    def execute(self, context):
        self.dm, _, _, _ = get_addon("DECALmachine")


        collectiondict = {}

        for obj in context.selected_objects:
            cols = sorted([col for col in obj.users_collection], key=lambda c: len(c.objects), reverse=True if self.multiple == "MOST" else False)

            if self.dm:
                if obj.DM.isdecal:
                    if self.decalmachine == "TYPE":
                        cols = [col for col in cols if col.DM.isdecaltypecol]

                    if self.decalmachine == "PARENT":
                        cols = [col for col in cols if col.DM.isdecalparentcol]

                    if self.decalmachine == "IGNORE" and obj.parent:
                        cols = sorted([col for col in obj.parent.users_collection], key=lambda c: len(c.objects), reverse=True if self.multiple == "MOST" else False)


            if cols:
                col = cols[0]
            else:
                col = context.scene.collection


            if col in collectiondict:
                collectiondict[col]["objects"].append(obj)

            else:
                collectiondict[col] = {}
                collectiondict[col]["objects"] = [obj]
                collectiondict[col]["color"] = (random.random(), random.random(), random.random(), 1)


        for col in collectiondict:
            objects = collectiondict[col]["objects"]
            color = collectiondict[col]["color"]


            for obj in objects:
                obj.color = color

        self.msg = "Assigned %d unique colors." % (len(collectiondict))


        return {'FINISHED'}


class ColorizeObjectsFromGroups(bpy.types.Operator):
    bl_idname = "machin3.colorize_objects_from_groups"
    bl_label = "MACHIN3: Colorize Objects from Groups"
    bl_options = {'REGISTER', 'UNDO'}

    random_color: BoolProperty(name="Random Color", default=True)
    active_only: BoolProperty(name="Active Group Only", default=False)

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return [obj for obj in context.selected_objects if obj.M3.is_group_empty]

    @classmethod
    def description(cls, context, properties):
        if context.active_object and context.active_object.M3.is_group_empty:
            return "Recursively Set Random Object Viewport Colors for Group Objects based on Group Membership\nALT: Set Group Member Colors based on existing Group Empy Colors\nCTRL: Only Colorize the Active Group"
        else:
            return "Recursively Set Random Object Viewport Colors for Group Objects based on Group Membership\nALT: Set Group Member Colors based on existing Group Empy Colors"

    def draw(self, context):
        layout = self.layout

        column = layout.column()
        row = column.row(align=True)
        row.prop(self, 'random_color', toggle=True)

        if context.active_object and context.active_object.M3.is_group_empty:
            row.prop(self, 'active_only', toggle=True)

    def invoke(self, context, event):
        self.random_color = not event.alt
        self.active_only = event.ctrl
        return self.execute(context)

    def execute(self, context):
        self.colors = group_colors.copy()
        active_group = context.active_object if context.active_object and context.active_object.M3.is_group_empty else None

        if active_group and self.active_only:
            self.colorize_group(active_group, recursive=False)

        else:
            all_empties = [obj for obj in context.selected_objects if obj.M3.is_group_empty]
            top_level = [obj for obj in all_empties if obj.parent not in all_empties]

            for group in top_level:
                self.colorize_group(group, recursive=True)

        return {'FINISHED'}

    def colorize_group(self, empty, recursive=False):
        children = [c for c in empty.children if c.M3.is_group_object]

        color = self.get_random_color() if self.random_color else empty.color

        if self.random_color:
            empty.color = color

        for c in children:
            if c.M3.is_group_empty:
                if recursive:
                    self.colorize_group(c, recursive=recursive)
            else:
                c.color = color

    def get_random_color(self):

        if self.colors:
            random_color = self.colors.pop(random.randint(0, len(self.colors) - 1))
        else:
            random_color = (random.random(), random.random(), random.random())

        return tuple(list(random_color) + [1])
