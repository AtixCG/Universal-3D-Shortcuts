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


# Currently supports versions:
#   2.83.x LTS
#   2.93.1
#   3.2 (as of June 2022)

import bpy
from ctypes import c_int, c_float, c_void_p, c_short, c_char, c_char_p, \
    c_uint, Structure, Union, POINTER
from typing import List


bl_info = {
    "name": "Toggle Hide",
    "location": "3D View / Outliner, (Hotkey J)",
    "version": (0, 2, 0),
    "blender": (3, 2, 0),
    "description": "Toggle object visibility of outliner selection",
    "author": "kaio",
    "category": "Object",
}


# Blender major/sub version
blender_version = bpy.app.version[:2]
_as_pointer = bpy.types.Struct.as_pointer


def idcode(id):
    """
    Little endian version of 'MAKE_ID2' from 'DNA_ID_enums.h'
    """
    return sum(j << 8 * i for i, j in enumerate(id.encode()))


def fproperty(funcs, property=property):
    return property(*funcs())


# source/blender/makesdna/DNA_ID_enums.h
# We only care about types which can have their visibility toggled,
# which is currently Object and LayerCollection instances.

ID_LAYERCOLL = 0
ID_OB = idcode("OB")  # bpy.types.Object


# TreeStoreElem.flag
TSE_CLOSED   = 1
TSE_SELECTED = 2


class ListBase(Structure):
    _cache = {}
    _fields_ = (("first", c_void_p), ("last",  c_void_p))
    def __new__(cls, c_type=None):
        if c_type in cls._cache: return cls._cache[c_type]
        elif c_type is None: ListBase_ = cls
        else:
            class ListBase_(Structure):
                __name__ = __qualname__ = f"ListBase{cls.__qualname__}"
                _fields_ = (("first", POINTER(c_type)),
                            ("last",  POINTER(c_type)))
                __iter__ = cls.__iter__
                __bool__ = cls.__bool__
        return cls._cache.setdefault(c_type, ListBase_)

    def __iter__(self):
        links_p = []
        elem_n = self.first or self.last
        elem_p = elem_n and elem_n.contents.prev
        if elem_p:
            while elem_p:
                links_p.append(elem_p.contents)
                elem_p = elem_p.contents.prev
            yield from reversed(links_p)
        while elem_n:
            yield elem_n.contents
            elem_n = elem_n.contents.next

    def __bool__(self):
        return bool(self.first or self.last)


class StructBase(Structure):
    _subclasses = []
    __annotations__ = {}
    def __init__(self, *_): pass
    def __init_subclass__(cls): cls._subclasses.append(cls)
    def __new__(cls, srna=None):
        try: return cls.from_address(_as_pointer(srna))
        except TypeError: return super().__new__(cls)  # Not a StructRNA instance

    @staticmethod
    def _init_structs():
        """
        Initialize subclasses, converting annotations to fields.
        """
        functype = type(lambda: None)

        for cls in StructBase._subclasses:
            fields = []
            anons = []
            for field, value in cls.__annotations__.items():
                if isinstance(value, functype):
                    value = value()
                elif isinstance(value, Union):
                    anons.append(field)
                fields.append((field, value))

            if anons:
                cls._anonynous_ = anons

            # Base classes might not have _fields_. Don't set anything.
            if fields:
                cls._fields_ = fields
            cls.__annotations__.clear()

        StructBase._subclasses.clear()
        ListBase._cache.clear()


# source/blender/makesdna/DNA_view2d_types.h
class View2D(StructBase):
    tot:        c_float * 4
    cur:        c_float * 4
    vert:       c_int * 4
    hor:        c_int * 4
    mask:       c_int * 4
    min:        c_float * 2
    max:        c_float * 2
    minzoom:    c_float
    maxzoom:    c_float
    scroll:     c_short
    scroll_ui:  c_short
    keeptot:    c_short
    keepzoom:   c_short
    keepofs:    c_short
    flag:       c_short
    align:      c_short
    winx:       c_short
    winy:       c_short
    oldwinx:    c_short
    oldwiny:    c_short
    around:     c_short

    if blender_version == (2, 83):
        tab_offset: POINTER(c_float)
        tab_num:    c_int
        tab_cur:    c_int

    alpha_vert:     c_char
    alpha_hor:      c_char

    if blender_version > (2, 83):
        _pad:       c_char * 6
    
    sms:            c_void_p
    smooth_timer:   c_void_p


# source/blender/makesdna/DNA_outliner_types.h
class TreeStoreElem(StructBase):
    type:   c_short
    nr:     c_short
    flag:   c_short

    if blender_version >= (3, 2):  # TODO: Check lowest version.
        used:   c_short

    id: lambda: POINTER(ID)


# source/blender/editors/space_outliner/outliner_intern.h
class TreeElement(StructBase):
    next:       lambda: POINTER(TreeElement)
    prev:       lambda: POINTER(TreeElement)
    parent:     lambda: POINTER(TreeElement)

    if blender_version > (2, 91):
        abstract_element:   c_void_p  # outliner::AbstractTreeElement
    
    subtree:    lambda: ListBase(TreeElement)
    xs:         c_int
    ys:         c_int
    store_elem: POINTER(TreeStoreElem)
    flag:       c_short
    index:      c_short
    idcode:     c_short
    xend:       c_short
    name:       c_char_p
    directdata: c_void_p

    if blender_version < (3, 2):
        rnaptr:     c_void_p * 3

    _treeid = None

    @fproperty
    def select():
        def getter(self): return bool(self.store_elem.contents.flag & 2)
        def setter(self, state):
            if state: self.store_elem.contents.flag |= TSE_SELECTED
            else: self.store_elem.contents.flag &= ~TSE_SELECTED
        return getter, setter

    @fproperty
    def expand():
        def getter(self): return not bool(self.tseflag & TSE_CLOSED)
        def setter(self, state):
            if state: self.store_elem.contents.flag &= ~TSE_CLOSED
            else: self.store_elem.contents.flag |= TSE_CLOSED
        return getter, setter

    @property
    def treeid(self):
        """
        Internal use.
        """
        if self._treeid is None:
            self._treeid = hash(
                tuple((t.name.decode(), t.idcode) for t in self._resolve()))
        return self._treeid

    def _resolve(self):
        """
        Return a reversed sequence of the hierarchy, excluding the root tree.
        Internal use.
        """
        link = [self]
        parent = self.parent
        while parent:
            link.append(parent.contents)
            parent = parent.contents.parent
        return tuple(reversed(link))[1:]

    def as_object(self, root):
        """
        Return the bpy.types.Object or LayerCollection instance.
        """

        view_layer = bpy.context.view_layer
        objects = view_layer.objects

        for t in subtrees_get(root):
            if t.treeid != self.treeid:
                continue

            name = t.name.decode()
            idcode = t.idcode

            # Is a bpy.types.LayerCollection subtree
            if idcode == ID_LAYERCOLL:
                # Layer collections can be nested resolve the hierarchy.
                layer_coll = view_layer.layer_collection
                for p in [t.name.decode() for t in self._resolve()]:
                    layer_coll = layer_coll.children[p]
                return layer_coll

            # Is a bpy.types.Object subtree
            elif idcode == ID_OB:
                return objects[name]

            # Could handle other types, eg. meshes.
            else:
                pass

        return None

    @staticmethod
    def from_outliner(space: bpy.types.SpaceOutliner):
        if not isinstance(space, bpy.types.SpaceOutliner):
            raise TypeError("Expected a bpy.types.SpaceOutliner instance.")
        return SpaceOutliner(space).tree.first


# source/blender/makesdna/DNA_space_types.h
class SpaceOutliner(StructBase):
    next: c_void_p
    prev: c_void_p
    regionbase: ListBase
    spacetype: c_char
    link_flag: c_char
    pad0: c_char * 6
    v2d: View2D  # DNA_DEPRECATED
    tree: ListBase(TreeElement)
    treestore: c_void_p
    search_string: c_char * 64
    search_tse: TreeStoreElem

    flag: c_short
    outlinevis: c_short

    if blender_version > (2, 93):
        lib_override_view_mode: c_short

    storeflag: c_short

    if blender_version < (3, 2):
        search_flags: c_char
    else:
        _pad: c_char * 6

    sync_select_dirty: c_char
    # ... (cont)

    @classmethod
    def get_tree(cls, so: bpy.types.SpaceOutliner) -> TreeElement:
        return cls.from_address(so.as_pointer()).tree.first


# source/blender/makesdna/DNA_ID.h
class ID(StructBase):
    next: c_void_p
    prev: c_void_p
    newid: c_void_p
    lib: c_void_p

    if blender_version > (2, 83):
        asset_data: c_void_p

    name: c_char * 66
    flag: c_short
    tag: c_int
    us: c_int
    icon_id: c_int
    recalc: c_int
    recalc_up_to_undo_push: c_int
    recalc_after_undo_push: c_int
    session_uuid: c_uint
    properties: c_void_p
    override_library: c_void_p
    orig_id: c_void_p
    py_instance: c_void_p

    if blender_version > (2, 83) and blender_version < (3, 2):
        _pad1: c_void_p

    if blender_version >= (2, 93):
        library_weak_reference: c_void_p

        class ID_Runtime(StructBase):
            class ID_Runtime_Remap(StructBase):
                status: c_int
                skipped_refcounter: c_int
                skipped_direct: c_int
                skipped_indirect: c_int
            remap: ID_Runtime_Remap
        runtime: ID_Runtime
    

# source/blender/makesdna/DNA_windowmanager_types.h
class wmWindowManager(StructBase):
    id: ID
    windrawable: c_void_p
    winactive: c_void_p
    windows: ListBase
    initialized: c_short
    file_saved: c_short
    op_undo_depth: c_short
    outliner_sync_select_dirty: c_short



def subtrees_get(tree) -> List[TreeElement]:
    """
    Given a tree, retrieve all its sub tree elements.
    """
    trees = []
    pool = [tree]
    while pool:
        t = pool.pop().contents
        trees.append(t)
        child = t.subtree.first
        while child:
            pool.append(child)
            child = child.contents.next
    return trees[1:]


def get_any_space_outliner() -> bpy.types.SpaceOutliner | None:
    """
    Try to get the outliner space data from context, otherwise
    find and return the first one.
    """
    space = getattr(bpy.context, "space_data", None)

    if not isinstance(space, bpy.types.SpaceOutliner):
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'OUTLINER':
                    return area.spaces.active
    return space


class OUTLINER_OT_toggle_hide(bpy.types.Operator):
    """Toggle the visibility of current outliner selection"""
    bl_idname = "outliner.toggle_hide"
    bl_label = "Toggle Hide"
    bl_options = {'REGISTER', 'UNDO'}

    _keymaps = []

    # Toggling only works when an outliner area is present. When two or more
    # outliners exist, the active outliner is used for purpose of selection.
    @classmethod
    def poll(cls, context):
        space = getattr(context, "space_data", None)
        if isinstance(space, bpy.types.SpaceOutliner):
            return True

        return get_any_space_outliner() is not None

    def execute(self, context):
        space = get_any_space_outliner()
        if space is None:
            return {'CANCELLED'}

        # Represents "Scene Collection" ie. the topmost tree element.
        root = TreeElement.from_outliner(space)
        wmstruct = wmWindowManager.from_address(context.window_manager.as_pointer())

        # Track processed objects to prevent those that appear in multiple
        # collections from being processed again.
        walked = set()

        outliner_types = {ID_OB, ID_LAYERCOLL}
        WM_OUTLINER_SYNC_SELECT_FROM_OBJECT = 1

        for tree in subtrees_get(root):
            if tree.idcode not in outliner_types or not tree.select:
                continue

            obj = tree.as_object(root)
            if obj in walked:
                continue

            # Is a layer collection
            elif isinstance(obj, bpy.types.LayerCollection):
                obj.hide_viewport ^= True

            # Is a bpy.types.Object instance
            elif isinstance(obj, bpy.types.Object):
                if obj.hide_get():
                    obj.hide_set(False)
                    obj.select_set(True)
                    # Prevent outliner selection sync from object mode specifically.
                    wmstruct.outliner_sync_select_dirty &= ~WM_OUTLINER_SYNC_SELECT_FROM_OBJECT

                # Is a visible object instance. Hide it.
                else:
                    obj.hide_set(True)

            # Traversed objects are tracked to prevent multiple instances from
            # toggling eachother.
            walked.add(obj)

        # Redraw to show any changes.
        if blender_version < (3, 2):
            for ar in space.id_data.areas:
                if ar.spaces.active == space:
                    ar.tag_redraw()
                    break

        return {'FINISHED'}

    @classmethod
    def register(cls):
        # Register keymaps
        kc = bpy.context.window_manager.keyconfigs.addon.keymaps

        km = kc.get("Object Mode") or kc.new("Object Mode")
        kmi = km.keymap_items.new(cls.bl_idname, 'J', 'PRESS')
        cls._keymaps.append((km, kmi))

        km = kc.get("Outliner") or kc.new("Outliner", space_type='OUTLINER')
        kmi = km.keymap_items.new("outliner.toggle_hide", 'J', 'PRESS')
        cls._keymaps.append((km, kmi))

    @classmethod
    def unregister(cls):
        for km, kmi in cls._keymaps:
            km.keymap_items.remove(kmi)
        cls._keymaps.clear()


def register():
    if blender_version < (2, 83):
        raise AssertionError("Minimum Blender version 2.83 required")
    bpy.utils.register_class(OUTLINER_OT_toggle_hide)
    StructBase._init_structs()


def unregister():
    bpy.utils.unregister_class(OUTLINER_OT_toggle_hide)
