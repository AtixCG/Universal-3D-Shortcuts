import bpy
from . registration import get_addon


def get_groups_collection(scene):
    mcol = scene.collection

    gpcol = bpy.data.collections.get("Groups")

    if gpcol:
        if gpcol.name not in mcol.children:
            mcol.children.link(gpcol)

    else:
        gpcol = bpy.data.collections.new(name="Groups")
        mcol.children.link(gpcol)

    return gpcol


def get_scene_collections(scene, ignore_decals=True):
    decalmachine, _, _, _ = get_addon("DECALmachine")
    mcol = scene.collection

    scenecols = []
    seen = list(mcol.children)

    while seen:
        col = seen.pop(0)
        if col not in scenecols:
            if not (ignore_decals and decalmachine and (col.DM.isdecaltypecol or col.DM.isdecalparentcol)):
                scenecols.append(col)
        seen.extend(list(col.children))

    return scenecols


def get_collection_depth(self, collections, depth=0, init=False):
    if init or depth > self.depth:
        self.depth = depth

    for col in collections:
        if col.children:
            get_collection_depth(self, col.children, depth + 1, init=False)

    return self.depth
