import bpy
from bpy.props import EnumProperty, BoolProperty
from .. utils.object import parent, unparent
from .. utils.group import group, ungroup, get_group_matrix, select_group_children, get_child_depth, clean_up_groups, fade_group_sizes
from .. utils.collection import get_collection_depth
from .. utils.registration import get_prefs
from .. utils.modifier import get_mods_as_dict, add_mods_from_dict
from .. utils.object import compensate_children
from .. items import group_location_items



class Group(bpy.types.Operator):
    bl_idname = "machin3.group"
    bl_label = "MACHIN3: Group"
    bl_description = "Group Objects by Parenting them to an Empty"
    bl_options = {'REGISTER', 'UNDO'}

    location: EnumProperty(name="Location", items=group_location_items, default='AVERAGE')
    rotation: EnumProperty(name="Rotation", items=group_location_items, default='WORLD')

    @classmethod
    def poll(cls, context):

        if context.mode == 'OBJECT':
            sel = [obj for obj in context.selected_objects]
            if len(sel) == 1:
                obj = sel[0]
                parent = obj.parent

                if parent:
                    booleans = [mod for mod in parent.modifiers if mod.type == 'BOOLEAN' and mod.object == obj]
                    if booleans:
                        return False
            return True

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row()
        row.label(text="Location")
        row.prop(self, 'location', expand=True)

        row = column.row()
        row.label(text="Rotation")
        row.prop(self, 'rotation', expand=True)

    def invoke(self, context, event):
        self.coords = (event.mouse_region_x, event.mouse_region_y)

        return self.execute(context)

    def execute(self, context):
        sel = {obj for obj in context.selected_objects if (obj.parent and obj.parent.M3.is_group_empty) or not obj.parent}

        if sel:
            self.group(context, sel)

            return {'FINISHED'}
        return {'CANCELLED'}

    def group(self, context, sel):
        debug = False

        grouped = {obj for obj in sel if obj.parent and obj.parent.M3.is_group_empty}

        selected_empties = {obj for obj in sel if obj.M3.is_group_empty}

        if debug:
            print()
            print("               sel", [obj.name for obj in sel])
            print("           grouped", [obj.name for obj in grouped])
            print("  selected empties", [obj.name for obj in selected_empties])

        if grouped == sel:

            unselected_empties = {obj.parent for obj in sel if obj not in selected_empties and obj.parent and obj.parent.M3.is_group_empty and obj.parent not in selected_empties}

            top_level = {obj for obj in selected_empties | unselected_empties if obj.parent not in selected_empties | unselected_empties}

            if debug:
                print("unselected empties", [obj.name for obj in unselected_empties])
                print("         top level", [obj.name for obj in top_level])


            if len(top_level) == 1:
                new_parent = top_level.pop()

            else:
                parent_groups = {obj.parent for obj in top_level}

                if debug:
                    print("     parent_groups", [obj.name if obj else None for obj in parent_groups])

                new_parent = parent_groups.pop() if len(parent_groups) == 1 else None


        else:
            new_parent = None

        if debug:
            print("        new parent", new_parent.name if new_parent else None)
            print(20 * "-")


        ungrouped = {obj for obj in sel - grouped if obj not in selected_empties}

        top_level = {obj for obj in selected_empties if obj.parent not in selected_empties}

        grouped = {obj for obj in grouped if obj not in selected_empties and obj.parent not in selected_empties}

        if len(top_level) == 1 and new_parent in top_level:
            new_parent = list(top_level)[0].parent

            if debug:
                print("updated parent", new_parent.name)

        if debug:
            print("     top level", [obj.name for obj in top_level])
            print("       grouped", [obj.name for obj in grouped])
            print("     ungrouped", [obj.name for obj in ungrouped])

        for obj in top_level | grouped:
            unparent(obj)

        empty = group(context, top_level | grouped | ungrouped, location=self.location, rotation=self.rotation)

        if new_parent:
            parent(empty, new_parent)
            empty.M3.is_group_object = True


        clean_up_groups(context)

        if get_prefs().group_fade_sizes:
            fade_group_sizes(context, init=True)

        bpy.ops.machin3.draw_label(text=f"{'Sub' if new_parent else 'Root'}: {empty.name}", coords=self.coords, color=(0.5, 1, 0.5) if new_parent else (1, 1, 1), time=get_prefs().HUD_fade_group, alpha=0.75)


class UnGroup(bpy.types.Operator):
    bl_idname = "machin3.ungroup"
    bl_label = "MACHIN3: Un-Group"
    bl_options = {'REGISTER', 'UNDO'}

    ungroup_all_selected: BoolProperty(name="Un-Group all Selected Groups", default=False)
    ungroup_entire_hierarchy: BoolProperty(name="Un-Group entire Hierarchy down", default=False)

    @classmethod
    def description(cls, context, properties):
        if context.scene.M3.group_recursive_select and context.scene.M3.group_select:
            return "Un-Group selected top-level Groups\nALT: Un-Group all selected Groups"
        else:
            return "Un-Group selected top-level Groups\nALT: Un-Group all selected Groups\nCTRL: Un-Group entire Hierarchy down"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        row = column.row(align=True)
        row.label(text="Un-Group")
        row.prop(self, 'ungroup_all_selected', text='All Selected', toggle=True)
        row.prop(self, 'ungroup_entire_hierarchy', text='Entire Hierarchy', toggle=True)

    def invoke(self, context, event):
        self.ungroup_all_selected = event.alt
        self.ungroup_entire_hierarchy = event.ctrl

        return self.execute(context)

    def execute(self, context):
        empties, all_empties = self.get_group_empties(context)

        if empties:
            self.ungroup(empties, all_empties)

            clean_up_groups(context)

            if get_prefs().group_fade_sizes:
                fade_group_sizes(context, init=True)

            return {'FINISHED'}
        return {'CANCELLED'}

    def get_group_empties(self, context):
        all_empties = [obj for obj in context.selected_objects if obj.M3.is_group_empty]

        if self.ungroup_all_selected:
            empties = all_empties
        else:
            empties = [e for e in all_empties if e.parent not in all_empties]

        return empties, all_empties

    def collect_entire_hierarchy(self, empties):
        for e in empties:
            children = [obj for obj in e.children if obj.M3.is_group_empty]

            for c in children:
                self.empties.append(c)
                self.collect_entire_hierarchy([c])

    def ungroup(self, empties, all_empties):
        if self.ungroup_entire_hierarchy:
            self.empties = empties
            self.collect_entire_hierarchy(empties)
            empties = set(self.empties)

        for empty in empties:
            ungroup(empty)


class Groupify(bpy.types.Operator):
    bl_idname = "machin3.groupify"
    bl_label = "MACHIN3: Groupify"
    bl_description = "Turn any Empty Hirearchy into Group"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return [obj for obj in context.selected_objects if obj.type == 'EMPTY' and not obj.M3.is_group_empty and obj.children]

    def execute(self, context):
        all_empties = [obj for obj in context.selected_objects if obj.type == 'EMPTY' and not obj.M3.is_group_empty and obj.children]

        empties = [e for e in all_empties if e.parent not in all_empties]

        self.groupify(empties)

        if get_prefs().group_fade_sizes:
            fade_group_sizes(context, init=True)

        return {'FINISHED'}

    def groupify(self, objects):
        for obj in objects:
            if obj.type == 'EMPTY' and not obj.M3.is_group_empty and obj.children:
                obj.M3.is_group_empty = True
                obj.M3.is_group_object = True if obj.parent and obj.parent.M3.is_group_empty else False
                obj.show_in_front = True
                obj.empty_display_type = 'CUBE'
                obj.empty_display_size = get_prefs().group_size
                obj.show_name = True

                if not any([s in obj.name.lower() for s in ['grp', 'group']]):
                    obj.name = f"{obj.name}_GROUP"

                self.groupify(obj.children)

            else:
                obj.M3.is_group_object = True



class Select(bpy.types.Operator):
    bl_idname = "machin3.select_group"
    bl_label = "MACHIN3: Select Group"
    bl_description = "Select Group\nCTRL: Select entire Group Hierarchy down"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        if context.scene.M3.group_recursive_select:
            return "Select entire Group Hierarchies down"
        else:
            return "Select Top Level Groups\nCTRL: Select entire Group Hierarchy down"

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return [obj for obj in context.selected_objects if obj.M3.is_group_empty or obj.M3.is_group_object]

    def invoke(self, context, event):
        clean_up_groups(context)

        empties = {obj for obj in context.selected_objects if obj.M3.is_group_empty}
        objects = [obj for obj in context.selected_objects if obj.M3.is_group_object and obj not in empties]

        for obj in objects:
            if obj.parent and obj.parent.M3.is_group_empty:
                empties.add(obj.parent)


        for e in empties:
            if e.visible_get():
                e.select_set(True)

                if len(empties) == 1:
                    context.view_layer.objects.active = e

            select_group_children(context.view_layer, e, recursive=event.ctrl or context.scene.M3.group_recursive_select)

        if get_prefs().group_fade_sizes:
            fade_group_sizes(context, init=True)

        return {'FINISHED'}


class Duplicate(bpy.types.Operator):
    bl_idname = "machin3.duplicate_group"
    bl_label = "MACHIN3: duplicate_group"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        if context.scene.M3.group_recursive_select:
            return "Duplicate entire Group Hierarchies down\nALT: Create Instances"
        else:
            return "Duplicate Top Level Groups\nALT: Create Instances\nCTRL: Duplicate entire Group Hierarchies down"

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return [obj for obj in context.selected_objects if obj.M3.is_group_empty]

    def invoke(self, context, event):
        empties = [obj for obj in context.selected_objects if obj.M3.is_group_empty]

        bpy.ops.object.select_all(action='DESELECT')

        for e in empties:
            e.select_set(True)
            select_group_children(context.view_layer, e, recursive=event.ctrl or context.scene.M3.group_recursive_select)

        if get_prefs().group_fade_sizes:
            fade_group_sizes(context, init=True)

        bpy.ops.object.duplicate_move_linked('INVOKE_DEFAULT') if event.alt else bpy.ops.object.duplicate_move('INVOKE_DEFAULT')

        return {'FINISHED'}



class Add(bpy.types.Operator):
    bl_idname = "machin3.add_to_group"
    bl_label = "MACHIN3: Add to Group"
    bl_description = "Add Selection to Group"
    bl_options = {'REGISTER', 'UNDO'}

    realign_group_empty: BoolProperty(name="Re-Align Group Empty", default=False)
    location: EnumProperty(name="Location", items=group_location_items, default='AVERAGE')
    rotation: EnumProperty(name="Rotation", items=group_location_items, default='WORLD')

    add_mirror: BoolProperty(name="Add Mirror Modifiers, if there are common ones among the existing Group's objects, that are missing from the new Objects", default=True)
    is_mirror: BoolProperty()

    add_color: BoolProperty(name="Add Object Color, from Group's Empty", default=True)
    is_color: BoolProperty()

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, 'realign_group_empty', toggle=True)

        row = column.row()
        row.active = self.realign_group_empty
        row.prop(self, 'location', expand=True)

        row = column.row()
        row.active = self.realign_group_empty
        row.prop(self, 'rotation', expand=True)

        row = column.row(align=True)

        if self.is_color:
            row.prop(self, 'add_color', text="Add Color", toggle=True)

        if self.is_mirror:
            row.prop(self, 'add_mirror', text="Add Mirror", toggle=True)

    def execute(self, context):
        debug = False

        active_group = context.active_object if context.active_object and context.active_object.M3.is_group_empty and context.active_object.select_get() else None

        if not active_group:

            active_group = context.active_object.parent if context.active_object and context.active_object.M3.is_group_object and context.active_object.select_get() else None

            if not active_group:
                return {'CANCELLED'}

        objects = [obj for obj in context.selected_objects if obj != active_group and obj not in active_group.children and (not obj.parent or (obj.parent and obj.parent.M3.is_group_empty and not obj.parent.select_get()))]

        if debug:
            print("active group", active_group.name)
            print("     addable", [obj.name for obj in objects])

        if objects:

            children = [c for c in active_group.children if c.M3.is_group_object and c.type == 'MESH' and c.name in context.view_layer.objects]

            self.is_mirror = any(obj for obj in children for mod in obj.modifiers if mod.type == 'MIRROR')

            self.is_color = any(obj.type == 'MESH' for obj in objects)

            for obj in objects:
                if obj.parent:
                    unparent(obj)

                parent(obj, active_group)

                obj.M3.is_group_object = True

                if obj.type == 'MESH':

                    if children and self.add_mirror:
                        self.mirror(obj, active_group, children)

                    if self.add_color:
                        obj.color = active_group.color

            if self.realign_group_empty:

                gmx = get_group_matrix(context, [c for c in active_group.children], self.location, self.rotation)

                compensate_children(active_group, active_group.matrix_world, gmx)

                active_group.matrix_world = gmx


            clean_up_groups(context)

            if get_prefs().group_fade_sizes:
                fade_group_sizes(context, init=True)

            return {'FINISHED'}
        return {'CANCELLED'}

    def mirror(self, obj, active_group, children):

        all_mirrors = {}

        for c in children:
            if c.M3.is_group_object and not c.M3.is_group_empty and c.type == 'MESH':
                mirrors = get_mods_as_dict(c, types=['MIRROR'], skip_show_expanded=True)

                if mirrors:
                    all_mirrors[c] = mirrors

        if all_mirrors and len(all_mirrors) == len(children):


            obj_props = [props for props in get_mods_as_dict(obj, types=['MIRROR'], skip_show_expanded=True).values()]

            if len(all_mirrors) == 1:

                common_props = [props for props in next(iter(all_mirrors.values())).values() if props not in obj_props]

            else:
                common_props = []

                for c, mirrors in all_mirrors.items():
                    others = [obj for obj in all_mirrors if obj != c]

                    for name, props in mirrors.items():
                        if all(props in all_mirrors[o].values() for o in others) and props not in common_props:
                            if props not in obj_props:
                                common_props.append(props)


            if common_props:
                common_mirrors = {f"Mirror{'.' + str(idx).zfill(3) if idx else ''}": props for idx, props in enumerate(common_props)}

                add_mods_from_dict(obj, common_mirrors)


class Remove(bpy.types.Operator):
    bl_idname = "machin3.remove_from_group"
    bl_label = "MACHIN3: Remove from Group"
    bl_description = "Remove Selection from Group"
    bl_options = {'REGISTER', 'UNDO'}

    realign_group_empty: BoolProperty(name="Re-Align Group Empty", default=False)
    location: EnumProperty(name="Location", items=group_location_items, default='AVERAGE')
    rotation: EnumProperty(name="Rotation", items=group_location_items, default='WORLD')

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            return True

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        column.prop(self, 'realign_group_empty', toggle=True)

        row = column.row()
        row.active = self.realign_group_empty
        row.prop(self, 'location', expand=True)

        row = column.row()
        row.active = self.realign_group_empty
        row.prop(self, 'rotation', expand=True)

    def execute(self, context):
        debug = False

        all_group_objects = [obj for obj in context.selected_objects if obj.M3.is_group_object]

        group_objects = [obj for obj in all_group_objects if obj.parent not in all_group_objects]

        if debug:
            print()
            print("all group objects", [obj.name for obj in all_group_objects])
            print("    group objects", [obj.name for obj in group_objects])

        if group_objects:

            empties = set()

            for obj in group_objects:
                empties.add(obj.parent)

                unparent(obj)
                obj.M3.is_group_object = False

            if self.realign_group_empty:
                for e in empties:
                    children = [c for c in e.children]

                    if children:
                        gmx = get_group_matrix(context, children, self.location, self.rotation)

                        compensate_children(e, e.matrix_world, gmx)

                        e.matrix_world = gmx

            clean_up_groups(context)

            return {'FINISHED'}
        return {'CANCELLED'}



class ToggleChildren(bpy.types.Operator):
    bl_idname = "machin3.toggle_outliner_children"
    bl_label = "MACHIN3: Toggle Outliner Children"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'OUTLINER'

    def execute(self, context):
        area = context.area
        space = area.spaces[0]

        space.use_filter_children = not space.use_filter_children

        return {'FINISHED'}


class ToggleGroupMode(bpy.types.Operator):
    bl_idname = "machin3.toggle_outliner_group_mode"
    bl_label = "MACHIN3: Toggle Outliner Group Mode"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'OUTLINER'

    def execute(self, context):
        area = context.area
        space = area.spaces[0]

        if space.use_filter_object_mesh:
            space.use_filter_collection = False
            space.use_filter_object_mesh = False
            space.use_filter_object_content = False
            space.use_filter_object_armature = False
            space.use_filter_object_light = False
            space.use_filter_object_camera = False
            space.use_filter_object_others = False
            space.use_filter_children = True

        else:
            space.use_filter_collection = True
            space.use_filter_object_mesh = True
            space.use_filter_object_content = True
            space.use_filter_object_armature = True
            space.use_filter_object_light = True
            space.use_filter_object_camera = True
            space.use_filter_object_others = True

        return {'FINISHED'}


class CollapseOutliner(bpy.types.Operator):
    bl_idname = "machin3.collapse_outliner"
    bl_label = "MACHIN3: Collapse Outliner"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'OUTLINER'

    def execute(self, context):

        col_depth = get_collection_depth(self, [context.scene.collection], init=True)

        child_depth = get_child_depth(self, [obj for obj in context.scene.objects if obj.children], init=True)

        for i in range(max(col_depth, child_depth) + 1):
            bpy.ops.outliner.show_one_level(open=False)

        return {'FINISHED'}


class ExpandOutliner(bpy.types.Operator):
    bl_idname = "machin3.expand_outliner"
    bl_label = "MACHIN3: Expand Outliner"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'OUTLINER'

    def execute(self, context):

        bpy.ops.outliner.show_hierarchy()

        depth = get_collection_depth(self, [context.scene.collection], init=True)

        for i in range(depth):
            bpy.ops.outliner.show_one_level(open=True)

        return {'FINISHED'}
