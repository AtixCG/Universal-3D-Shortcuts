def register_tool_fallback(tool_cls, *, after=None, separator=False, group=False):
    """
    Register a tool in the toolbar.

    :arg tool: A tool subclass.
    :type tool: :class:`bpy.types.WorkSpaceTool` subclass.
    :arg space_type: Space type identifier.
    :type space_type: string
    :arg after: Optional identifiers this tool will be added after.
    :type after: collection of strings or None.
    :arg separator: When true, add a separator before this tool.
    :type separator: bool
    :arg group: When true, add a new nested group of tools.
    :type group: bool
    """
    space_type = tool_cls.bl_space_type
    context_mode = tool_cls.bl_context_mode

    from bl_ui.space_toolsystem_common import (
        ToolSelectPanelHelper,
        ToolDef,
    )

    cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
    if cls is None:
        raise Exception("Space type %r has no toolbar" % space_type)
    tools = cls._tools[context_mode]

    # First sanity check
    from bpy.types import WorkSpaceTool
    tools_id = {
        item.idname for item in ToolSelectPanelHelper._tools_flatten(tools)
        if item is not None
    }
    if not issubclass(tool_cls, WorkSpaceTool):
        raise Exception("Expected WorkSpaceTool subclass, not %r" % type(tool_cls))
    if tool_cls.bl_idname in tools_id:
        raise Exception("Tool %r already exists!" % tool_cls.bl_idname)
    del tools_id, WorkSpaceTool

    # Convert the class into a ToolDef.
    def tool_from_class(tool_cls):
        # Convert class to tuple, store in the class for removal.
        tool_def = ToolDef.from_dict({
            "idname": tool_cls.bl_idname,
            "label": tool_cls.bl_label,
            "description": getattr(tool_cls, "bl_description", tool_cls.__doc__),
            "icon": getattr(tool_cls, "bl_icon", None),
            "cursor": getattr(tool_cls, "bl_cursor", None),
            "options": getattr(tool_cls, "bl_options", None),
            "widget": getattr(tool_cls, "bl_widget", None),
            "widget_properties": getattr(tool_cls, "bl_widget_properties", None),
            "keymap": getattr(tool_cls, "bl_keymap", None),
            "keymap_fallback": getattr(tool_cls, "bl_keymap_fallback", None),
            "data_block": getattr(tool_cls, "bl_data_block", None),
            "operator": getattr(tool_cls, "bl_operator", None),
            "draw_settings": getattr(tool_cls, "draw_settings", None),
            "draw_cursor": getattr(tool_cls, "draw_cursor", None),
        })
        tool_cls._bl_tool = tool_def

        keymap_data = tool_def.keymap
        if keymap_data is not None:
            if context_mode is None:
                context_descr = "All"
            else:
                context_descr = context_mode.replace("_", " ").title()
            from bpy import context
            wm = context.window_manager
            keyconfigs = wm.keyconfigs
            kc_default = keyconfigs.default
            # Note that Blender's default tools use the default key-config for both.
            # We need to use the add-ons for 3rd party tools so reloading the key-map doesn't clear them.
            kc = keyconfigs.addon
            if callable(keymap_data[0]):
                cls._km_action_simple(kc_default, kc, context_descr, tool_def.label, keymap_data)
        return tool_def

    tool_converted = tool_from_class(tool_cls)

    if group:
        # Create a new group
        tool_converted = (tool_converted,)

    tool_def_insert = (
        (None, tool_converted) if separator else
        (tool_converted,)
    )

    def skip_to_end_of_group(seq, i):
        i_prev = i
        while i < len(seq) and seq[i] is not None:
            i_prev = i
            i += 1
        return i_prev

    changed = False
    if after is not None:
        for i, item in enumerate(tools):
            if item is None:
                pass
            elif isinstance(item, ToolDef):
                if item.idname in after:
                    i = skip_to_end_of_group(item, i)
                    tools[i + 1:i + 1] = tool_def_insert
                    changed = True
                    break
            elif isinstance(item, tuple):
                for j, sub_item in enumerate(item, 1):
                    if isinstance(sub_item, ToolDef):
                        if sub_item.idname in after:
                            if group:
                                # Can't add a group within a group,
                                # add a new group after this group.
                                i = skip_to_end_of_group(tools, i)
                                tools[i + 1:i + 1] = tool_def_insert
                            else:
                                j = skip_to_end_of_group(item, j)
                                item = item[:j + 1] + tool_def_insert + item[j + 1:]
                                tools[i] = item
                            changed = True
                            break
                if changed:
                    break

        if not changed:
            print("bpy.utils.register_tool: could not find 'after'", after)
    if not changed:
        tools.extend(tool_def_insert)


def unregister_tool_fallback(tool_cls):
    space_type = tool_cls.bl_space_type
    context_mode = tool_cls.bl_context_mode

    from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
    cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
    if cls is None:
        raise Exception("Space type %r has no toolbar" % space_type)
    tools = cls._tools[context_mode]

    tool_def = tool_cls._bl_tool
    try:
        i = tools.index(tool_def)
    except ValueError:
        i = -1

    def tool_list_clean(tool_list):
        # Trim separators.
        while tool_list and tool_list[-1] is None:
            del tool_list[-1]
        while tool_list and tool_list[0] is None:
            del tool_list[0]
        # Remove duplicate separators.
        for i in range(len(tool_list) - 1, -1, -1):
            is_none = tool_list[i] is None
            if is_none and prev_is_none:
                del tool_list[i]
            prev_is_none = is_none

    changed = False
    if i != -1:
        del tools[i]
        tool_list_clean(tools)
        changed = True

    if not changed:
        for i, item in enumerate(tools):
            if isinstance(item, tuple):
                try:
                    j = item.index(tool_def)
                except ValueError:
                    j = -1

                if j != -1:
                    item_clean = list(item)
                    del item_clean[j]
                    tool_list_clean(item_clean)
                    if item_clean:
                        tools[i] = tuple(item_clean)
                    else:
                        del tools[i]
                        tool_list_clean(tools)
                    del item_clean

                    # tuple(sub_item for sub_item in items if sub_item is not tool_def)
                    changed = True
                    break

    if not changed:
        raise Exception("Unable to remove %r" % tool_cls)
    del tool_cls._bl_tool

    keymap_data = tool_def.keymap
    if keymap_data is not None:
        from bpy import context
        wm = context.window_manager
        keyconfigs = wm.keyconfigs
        for kc in (keyconfigs.default, keyconfigs.addon):
            km = kc.keymaps.get(keymap_data[0])
            if km is None:
                print("Warning keymap %r not found in %r!" % (keymap_data[0], kc.name))
            else:
                kc.keymaps.remove(km)