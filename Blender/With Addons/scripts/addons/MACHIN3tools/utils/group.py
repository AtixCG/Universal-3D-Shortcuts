import bpy
from mathutils import Vector, Quaternion
from . object import parent, unparent
from . math import average_locations, get_loc_matrix, get_rot_matrix
from . import registration as r



def group(context, sel, location='AVERAGE', rotation='WORLD'):
    col = get_group_collection(context, sel)

    empty = bpy.data.objects.new(name=get_base_group_name(), object_data=None)
    empty.M3.is_group_empty = True
    empty.matrix_world = get_group_matrix(context, sel, location, rotation)
    col.objects.link(empty)

    context.view_layer.objects.active = empty
    empty.select_set(True)
    empty.show_in_front = True
    empty.empty_display_type = 'CUBE'

    empty.show_name = True
    empty.empty_display_size = r.get_prefs().group_size

    empty.M3.group_size = r.get_prefs().group_size

    for obj in sel:
        parent(obj, empty)
        obj.M3.is_group_object = True

    return empty


def ungroup(empty):
    for obj in empty.children:
        unparent(obj)
        obj.M3.is_group_object = False

    bpy.data.objects.remove(empty, do_unlink=True)


def clean_up_groups(context):
    for obj in context.scene.objects:

        if obj.M3.is_group_empty and not obj.children:
            print("INFO: Removing empty Group", obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)

        elif obj.M3.is_group_object:
            if obj.parent:

                if not obj.parent.M3.is_group_empty:
                    obj.M3.is_group_object = False
                    print(f"INFO: {obj.name} is no longer a group object, because it's parent {obj.parent.name} is not a group empty")

            else:
                obj.M3.is_group_object = False
                print(f"INFO: {obj.name} is no longer a group object, because it doesn't have any parent")

        elif not obj.M3.is_group_object and obj.parent and obj.parent.M3.is_group_empty:
            obj.M3.is_group_object = True
            print(f"INFO: {obj.name} is now a group object, because it was manually parented to {obj.parent.name}")



def get_group_polls(context):
    active_group = context.active_object if context.active_object and context.active_object.M3.is_group_empty and context.active_object.select_get() else None
    active_child = context.active_object if context.active_object and context.active_object.parent and context.active_object.M3.is_group_object and context.active_object.select_get() else None

    group_empties = bool([obj for obj in context.visible_objects if obj.M3.is_group_empty])
    groupable = bool([obj for obj in context.selected_objects if (obj.parent and obj.parent.M3.is_group_empty) or not obj.parent])
    ungroupable = bool([obj for obj in context.selected_objects if obj.M3.is_group_empty]) if group_empties else False

    addable = bool([obj for obj in context.selected_objects if obj != (active_group if active_group else active_child.parent) and obj not in (active_group.children if active_group else active_child.parent.children) and (not obj.parent or (obj.parent and obj.parent.M3.is_group_empty and not obj.parent.select_get()))]) if active_group or active_child else False

    removable = bool([obj for obj in context.selected_objects if obj.M3.is_group_object])
    selectable = bool([obj for obj in context.selected_objects if obj.M3.is_group_empty or obj.M3.is_group_object])
    duplicatable = bool([obj for obj in context.selected_objects if obj.M3.is_group_empty])
    groupifyable = bool([obj for obj in context.selected_objects if obj.type == 'EMPTY' and not obj.M3.is_group_empty and obj.children])

    return bool(active_group), bool(active_child), group_empties, groupable, ungroupable, addable, removable, selectable, duplicatable, groupifyable


def get_group_collection(context, sel):

    collections = set(col for obj in sel for col in obj.users_collection)

    if len(collections) == 1:
        return collections.pop()

    else:
        return context.scene.collection


def get_group_matrix(context, objects, location_type='AVERAGE', rotation_type='WORLD'):


    if location_type == 'AVERAGE':
        location = average_locations([obj.matrix_world.to_translation() for obj in objects])

    elif location_type == 'ACTIVE':
        if context.active_object:
            location = context.active_object.matrix_world.to_translation()

        else:
            location = average_locations([obj.matrix_world.to_translation() for obj in objects])

    elif location_type == 'CURSOR':
        location = context.scene.cursor.location

    elif location_type == 'WORLD':
        location = Vector()



    if rotation_type == 'AVERAGE':
        rotation = Quaternion(average_locations([obj.matrix_world.to_quaternion().to_exponential_map() for obj in objects]))

    elif rotation_type == 'ACTIVE':
        if context.active_object:
            rotation = context.active_object.matrix_world.to_quaternion()

        else:
            rotation = Quaternion(average_locations([obj.matrix_world.to_quaternion().to_exponential_map() for obj in objects]))

    elif rotation_type == 'CURSOR':
        rotation = context.scene.cursor.matrix.to_quaternion()

    elif rotation_type == 'WORLD':
        rotation = Quaternion()

    return get_loc_matrix(location) @ get_rot_matrix(rotation)



def select_group_children(view_layer, empty, recursive=False):

    children = [c for c in empty.children if c.M3.is_group_object and c.name in view_layer.objects]

    if empty.hide_get():
        empty.hide_set(False)

        if empty.visible_get(view_layer=view_layer):
            empty.select_set(True)

    for obj in children:
        if obj.visible_get(view_layer=view_layer):
            obj.select_set(True)

        if obj.M3.is_group_empty and recursive:
            select_group_children(view_layer, obj, recursive=True)


def get_child_depth(self, children, depth=0, init=False):
    if init or depth > self.depth:
        self.depth = depth

    for child in children:
        if child.children:
            get_child_depth(self, child.children, depth + 1, init=False)

    return self.depth


def fade_group_sizes(context, size=None, groups=[], init=False):
    if init:
        groups = [obj for obj in context.scene.objects if obj.M3.is_group_empty and not obj.parent]

    for group in groups:
        if size:
            factor = r.get_prefs().group_fade_factor

            group.empty_display_size = factor * size
            group.M3.group_size = group.empty_display_size

        sub_groups = [c for c in group.children if c.M3.is_group_empty]

        if sub_groups:
            fade_group_sizes(context, size=group.M3.group_size, groups=sub_groups, init=False)



def get_base_group_name():
    p = r.get_prefs()

    if r.get_prefs().group_auto_name:
        name = f"{p.group_prefix}{p.group_basename + '_001'}{p.group_suffix}"

        c = 0
        while name in bpy.data.objects:
            c += 1
            name = f"{p.group_prefix}{p.group_basename + '_' + str(c).zfill(3)}{p.group_suffix}"

        return name

    else:
        name = f"{p.group_basename}_001"

        c = 0
        while name in bpy.data.objects:
            c += 1
            name = f"{p.group_basename + '_' + str(c).zfill(3)}"

        return name


def update_group_name(group):
    p = r.get_prefs()
    prefix = p.group_prefix
    suffix = p.group_suffix

    name = group.name
    newname = name

    if not name.startswith(prefix):
        newname = prefix + newname

    if not name.endswith(suffix):
        newname = newname + suffix

    if name == newname:
        return

    c = 0
    while newname in bpy.data.objects:
        c += 1
        newname = f"{p.group_prefix}{name + '_' + str(c).zfill(3)}{p.group_suffix}"

    group.name = newname
