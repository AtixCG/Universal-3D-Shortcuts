import bpy
from .. items import mirror_props



def add_triangulate(obj):
    mod = obj.modifiers.new(name="Triangulate", type="TRIANGULATE")
    mod.keep_custom_normals = True
    mod.quad_method = 'FIXED'
    mod.show_expanded = True
    return mod


def add_shrinkwrap(obj, target):
    mod = obj.modifiers.new(name="Shrinkwrap", type="SHRINKWRAP")

    mod.target = target
    mod.show_on_cage = True
    mod.show_expanded = False
    return mod


def add_mods_from_dict(obj, modsdict):
    for name, props in modsdict.items():
        mod = obj.modifiers.new(name=name, type=props['type'])

        for pname, pvalue in props.items():
            if pname != 'type':
                setattr(mod, pname, pvalue)


def add_bevel(obj, method='WEIGHT'):
    mod = obj.modifiers.new(name='Bevel', type='BEVEL')
    mod.limit_method = method

    mod.show_expanded = False
    return mod



def remove_mod(modname, objtype='MESH', context=None, object=None):

    if context and object:
        with context.temp_override(object=object):
            if objtype == 'GPENCIL':
                bpy.ops.object.gpencil_modifier_remove(modifier=modname)
            else:
                bpy.ops.object.modifier_remove(modifier=modname)

    else:
        if objtype == 'GPENCIL':
            bpy.ops.object.gpencil_modifier_remove(modifier=modname)
        else:
            bpy.ops.object.modifier_remove(modifier=modname)


def remove_triangulate(obj):
    lastmod = obj.modifiers[-1] if obj.modifiers else None

    if lastmod and lastmod.type == 'TRIANGULATE':
        obj.modifiers.remove(lastmod)
        return True



def get_mod_as_dict(mod, skip_show_expanded=False):
    d = {}

    if mod.type == 'MIRROR':
        for prop in mirror_props:
            if skip_show_expanded and prop == 'show_expanded':
                continue

            if prop in ['use_axis', 'use_bisect_axis', 'use_bisect_flip_axis']:
                d[prop] = tuple(getattr(mod, prop))
            else:
                d[prop] = getattr(mod, prop)

    return d


def get_mods_as_dict(obj, types=[], skip_show_expanded=False):
    mods = []

    for mod in obj.modifiers:
        if types:
            if mod.type in types:
                mods.append(mod)

        else:
            mods.append(mod)

    modsdict = {}

    for mod in mods:
        modsdict[mod.name] = get_mod_as_dict(mod, skip_show_expanded=skip_show_expanded)

    return modsdict



def apply_mod(modname):
    bpy.ops.object.modifier_apply(modifier=modname)



def get_mod_obj(mod):
    if mod.type in ['BOOLEAN', 'HOOK', 'LATTICE', 'DATA_TRANSFER', 'GP_MIRROR']:
        return mod.object
    elif mod.type == 'MIRROR':
        return mod.mirror_object
    elif mod.type == 'ARRAY':
        return mod.offset_object
