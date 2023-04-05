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


bl_info = {
    "name": "X-Ray Selection Tools",
    "author": "MarshmallowCirno",
    "version": (4, 3, 2),
    "blender": (3, 4, 0),
    "location": "Toolbar > Selection Tools",
    "description": "Box, lasso and circle selection tools with x-ray",
    "warning": "",
    "category": "3D View",
    "doc_url": "https://gumroad.com/l/DaLdj",
    "tracker_url": "https://blenderartists.org/t/x-ray-selection-tools/1212316",
}


reloadable_modules = (
    "view3d",
    "timer",
    "polygon_tests",
    "selection",
    "mesh_intersect",
    "mesh_modal",
    "object_intersect",
    "object_intersect_box",
    "object_intersect_circle",
    "object_intersect_lasso",
    "object_modal",
    "mesh_ot",
    "mesh_ot_box",
    "mesh_ot_circle",
    "mesh_ot_lasso",
    "object_ot_box",
    "object_ot_circle",
    "object_ot_lasso",
    "help",
    "ot_keymap",
    "tools",
    "tools_dummy",
    "tools_keymap",
    "ui_preferences",
)

# when bpy is already in local, we know this is not the initial import...
if "bpy" in locals():
    # ...so we need to reload our submodule(s) using importlib
    import importlib

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])
else:
    from .functions import (
        mesh_intersect,
        mesh_modal,
        object_intersect,
        object_intersect_box,
        object_intersect_circle,
        object_intersect_lasso,
        object_modal,
        polygon_tests,
        selection,
        timer,
        view3d,
    )
    from .mesh_ot import mesh_ot_box, mesh_ot_circle, mesh_ot_lasso, mesh_ot
    from .object_ot import object_ot_box, object_ot_circle, object_ot_lasso
    from . import help, ot_keymap, tools, tools_dummy, ui_preferences


import bpy


def register():
    mesh_ot_box.register()
    mesh_ot_circle.register()
    mesh_ot_lasso.register()
    mesh_ot.register()
    object_ot_box.register()
    object_ot_circle.register()
    object_ot_lasso.register()
    help.register()
    ui_preferences.register()
    ot_keymap.register()
    tools.register()
    tools_dummy.register()


def unregister():
    mesh_ot_box.unregister()
    mesh_ot_circle.unregister()
    mesh_ot_lasso.unregister()
    mesh_ot.unregister()
    object_ot_box.unregister()
    object_ot_circle.unregister()
    object_ot_lasso.unregister()
    help.unregister()
    ui_preferences.unregister()
    ot_keymap.unregister()
    tools.reset_active_tool()
    tools.unregister()
    tools_dummy.unregister()
