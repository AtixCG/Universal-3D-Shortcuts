import bpy

from .preferences import get_preferences


fallback_keymap_dict = {
    "3D View Tool: Object, Select Box X-Ray (fallback)": ("object.select_box_xray", "BOX"),
    "3D View Tool: Object, Select Circle X-Ray (fallback)": ("object.select_circle_xray", "CIRCLE"),
    "3D View Tool: Object, Select Lasso X-Ray (fallback)": ("object.select_lasso_xray", "LASSO"),

    "3D View Tool: Edit Mesh, Select Box X-Ray (fallback)": ("mesh.select_box_xray", "BOX"),
    "3D View Tool: Edit Mesh, Select Circle X-Ray (fallback)": ("mesh.select_circle_xray", "CIRCLE"),
    "3D View Tool: Edit Mesh, Select Lasso X-Ray (fallback)": ("mesh.select_lasso_xray", "LASSO"),
}

dummy_fallback_keymap_dict = {
    "3D View Tool: Edit Curve, Select Box X-Ray (fallback)": ("view3d.select_box", "BOX"),
    "3D View Tool: Edit Curve, Select Circle X-Ray (fallback)": ("view3d.select_circle", "CIRCLE"),
    "3D View Tool: Edit Curve, Select Lasso X-Ray (fallback)": ("view3d.select_lasso", "LASSO"),

    "3D View Tool: Edit Armature, Select Box X-Ray (fallback)": ("view3d.select_box", "BOX"),
    "3D View Tool: Edit Armature, Select Circle X-Ray (fallback)": ("view3d.select_circle", "CIRCLE"),
    "3D View Tool: Edit Armature, Select Lasso X-Ray (fallback)": ("view3d.select_lasso", "LASSO"),

    "3D View Tool: Edit Metaball, Select Box X-Ray (fallback)": ("view3d.select_box", "BOX"),
    "3D View Tool: Edit Metaball, Select Circle X-Ray (fallback)": ("view3d.select_circle", "CIRCLE"),
    "3D View Tool: Edit Metaball, Select Lasso X-Ray (fallback)": ("view3d.select_lasso", "LASSO"),

    "3D View Tool: Edit Lattice, Select Box X-Ray (fallback)": ("view3d.select_box", "BOX"),
    "3D View Tool: Edit Lattice, Select Circle X-Ray (fallback)": ("view3d.select_circle", "CIRCLE"),
    "3D View Tool: Edit Lattice, Select Lasso X-Ray (fallback)": ("view3d.select_lasso", "LASSO"),

    "3D View Tool: Pose, Select Box X-Ray (fallback)": ("view3d.select_box", "BOX"),
    "3D View Tool: Pose, Select Circle X-Ray (fallback)": ("view3d.select_circle", "CIRCLE"),
    "3D View Tool: Pose, Select Lasso X-Ray (fallback)": ("view3d.select_lasso", "LASSO"),
}


def add_fallback_keymap(keymap_dict: dict) -> None:
    """Create empty fallback keymap for every tool."""
    # https://developer.blender.org/rBc9d9bfa84ad
    kc = bpy.context.window_manager.keyconfigs.default
    for keymap_name in keymap_dict.keys():
        kc.keymaps.new(name=keymap_name, space_type='VIEW_3D', region_type='WINDOW', tool=True)


def add_fallback_keymap_items(keymap_dict: dict) -> None:
    """Fill tool fallback keymaps with keymap items from addon preferences."""
    kc = bpy.context.window_manager.keyconfigs.active
    # keyconfig.preferences isn't available at blender startup
    if kc.preferences is not None:
        select_mouse = get_preferences().select_mouse = kc.preferences.select_mouse
        rmb_action = get_preferences().rmb_action = kc.preferences.rmb_action
    else:
        select_mouse = get_preferences().select_mouse
        rmb_action = get_preferences().rmb_action

    kc = bpy.context.window_manager.keyconfigs.addon
    addon_prefs_keymaps = get_preferences().keymaps_of_tools

    if select_mouse == 'RIGHT' and rmb_action == 'FALLBACK_TOOL':
        event_type = 'RIGHTMOUSE'
    else:
        event_type = 'LEFTMOUSE'

    for keymap_name, (keymap_item_idname, tool) in keymap_dict.items():
        km = kc.keymaps.new(name=keymap_name, space_type='VIEW_3D', region_type='WINDOW', tool=True)
        addon_prefs_keymap = addon_prefs_keymaps[tool]
        addon_prefs_keymap_items = addon_prefs_keymap.kmis

        for key, values in reversed(addon_prefs_keymap_items.items()):
            if values["active"]:
                kmi = km.keymap_items.new(
                    keymap_item_idname,
                    event_type,
                    'CLICK_DRAG',
                    ctrl=values["ctrl"],
                    shift=values["shift"],
                    alt=values["alt"],
                )
                if values["name"] != 'DEF':
                    kmi.properties.mode = values["name"]

                if keymap_item_idname in {"mesh.select_circle_xray",
                                          "object.select_circle_xray",
                                          "view3d.select_circle"}:
                    kmi.properties.wait_for_input = False


def remove_fallback_keymap_items(keymap_dict: dict) -> None:
    """Remove tool fallback keymap items."""
    for keymap_name in keymap_dict.keys():
        kc = bpy.context.window_manager.keyconfigs.addon
        km = kc.keymaps.get(keymap_name)
        if km is not None:
            for kmi in km.keymap_items:
                km.keymap_items.remove(kmi)


def populate_preferences_keymaps_of_tools() -> None:
    """Fill preferences keymaps collection property from template"""
    addon_prefs_tool_keymaps = get_preferences().keymaps_of_tools
    default_addon_prefs_keymap_dict = {
        "DEF": {"description": "Active Mode", "icon": "PROPERTIES",
                "active": True, "shift": False, "ctrl": False, "alt": False},
        "SET": {"description": "Set", "icon": "SELECT_SET",
                "active": False, "shift": False, "ctrl": False, "alt": False},
        "ADD": {"description": "Extend", "icon": "SELECT_EXTEND",
                "active": True, "shift": True, "ctrl": False, "alt": False},
        "SUB": {"description": "Subtract", "icon": "SELECT_SUBTRACT",
                "active": True, "shift": False, "ctrl": True, "alt": False},
        "XOR": {"description": "Difference", "icon": "SELECT_DIFFERENCE",
                "active": False, "shift": False, "ctrl": False, "alt": True},
        "AND": {"description": "Intersect", "icon": "SELECT_INTERSECT",
                "active": True, "shift": True, "ctrl": True, "alt": False}
    }

    for tool in ("BOX", "LASSO", "CIRCLE"):
        addon_prefs_tool_keymap = addon_prefs_tool_keymaps.get(tool)
        if addon_prefs_tool_keymap is None:
            addon_prefs_tool_keymap = addon_prefs_tool_keymaps.add()
            addon_prefs_tool_keymap["name"] = tool

        keymap_dict = default_addon_prefs_keymap_dict
        # remove XOR and AND from circle tools
        if tool == "CIRCLE":
            keymap_dict.pop("XOR")
            keymap_dict.pop("AND")

        kmis = addon_prefs_tool_keymap.kmis
        for idname, values in keymap_dict.items():
            if idname not in kmis.keys():
                kmi = kmis.add()
                kmi["name"] = idname
                kmi["description"] = values["description"]
                kmi["icon"] = values["icon"]
                kmi["active"] = values["active"]
                kmi["shift"] = values["shift"]
                kmi["ctrl"] = values["ctrl"]
                kmi["alt"] = values["alt"]


def get_keymap_of_tool_from_preferences(bl_operator: str) -> tuple:
    """Get tool keymap items from addon preferences keymap collection property."""
    addon_prefs_tool_keymaps = get_preferences().keymaps_of_tools
    tool = {
        "mesh.select_box_xray": "BOX",
        "object.select_box_xray": "BOX",
        "view3d.select_box": "BOX",
        "mesh.select_circle_xray": "CIRCLE",
        "object.select_circle_xray": "CIRCLE",
        "view3d.select_circle": "CIRCLE",
        "mesh.select_lasso_xray": "LASSO",
        "object.select_lasso_xray": "LASSO",
        "view3d.select_lasso": "LASSO"
    }[bl_operator]
    addon_prefs_tool_keymap = addon_prefs_tool_keymaps[tool]
    addon_prefs_tool_keymap_items = addon_prefs_tool_keymap.kmis

    keyconfig_tool_keymap_items = []
    for idname, values in addon_prefs_tool_keymap_items.items():
        if values["active"]:
            kmi = (
                bl_operator,
                {
                    "type": 'LEFTMOUSE',
                    "value": 'CLICK_DRAG',
                    "shift": values["shift"],
                    "ctrl": values["ctrl"],
                    "alt": values["alt"]
                },
                {"properties": [("mode", idname)]}
            )
            if idname == "DEF":
                kmi[2]["properties"] = []

            if tool == "CIRCLE":
                kmi[2]["properties"].append(("wait_for_input", False))

            keyconfig_tool_keymap_items.append(kmi)

    keyconfig_tool_keymap_items.reverse()
    keyconfig_tool_keymap_items = tuple(keyconfig_tool_keymap_items)
    return keyconfig_tool_keymap_items


def update_keymaps_of_tools(self, context) -> None:
    """Apply changes of addon preferences keymap collection property to keyconfig tool keymaps."""
    from .tools import unregister as unregister_tools
    from .tools_dummy import unregister as unregister_tools_dummy
    from .tools import register as register_tools
    from .tools_dummy import register as register_tools_dummy

    unregister_tools()
    unregister_tools_dummy()

    register_tools()
    register_tools_dummy()
