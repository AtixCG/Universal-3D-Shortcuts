from . tools import prettify_tool_name
from . system import printd
from . registration import get_addon_operator_idnames


addons = None

addon_abbr_mapping = {'MACHIN3tools': 'M3',
                      'DECALmachine': 'DM',
                      'MESHmachine': 'MM',
                      'HyperCursor': 'HC',
                      'PUNCHit': 'PI'}


def get_last_operators(context, debug=False):
    def get_parent_addon(idname):
        if idname.startswith('hops.'):
            return 'HO'
        elif idname.startswith('bc.'):
            return 'BC'

        for name, idnames in addons.items():
            if idname in idnames:
                return addon_abbr_mapping[name]
        return None

    global addons

    if addons is None:
        addons = {}

        for addon in ['MACHIN3tools', 'DECALmachine', 'MESHmachine', 'HyperCursor', 'PUNCHit']:
            addons[addon] = get_addon_operator_idnames(addon)

        if debug:
            printd(addons)

    operators = []

    for op in context.window_manager.operators:
        idname = op.bl_idname.replace('_OT_', '.').lower()
        label = op.bl_label.replace('MACHIN3: ', '').replace('Macro', '').strip()
        addon = get_parent_addon(idname)
        prop = ''


        if idname.startswith('machin3.call_'):
            continue



        elif idname == 'machin3.set_tool_by_name':
            prop = prettify_tool_name(op.properties.get('name', ''))

        elif idname == 'machin3.switch_workspace':
            prop = op.properties.get('name', '')

        elif idname == 'machin3.switch_shading':
            toggled_overlays = getattr(op, 'toggled_overlays', False)
            prop = op.properties.get('shading_type', '').capitalize()

            if toggled_overlays:
                label = f"{toggled_overlays} Overlays"

        elif idname == 'machin3.edit_mode':
            toggled_object = getattr(op, 'toggled_object', False)
            label = 'Object Mode' if toggled_object else 'Edit Mesh Mode'

        elif idname == 'machin3.mesh_mode':
            mode = op.properties.get('mode', '')
            label = f"{mode.capitalize()} Mode"

        elif idname == 'machin3.smart_vert':
            if op.properties.get('slideoverride', ''):
                prop = 'SideExtend'

            elif op.properties.get('vertbevel', False):
                prop = 'VertBevel'

            else:
                modeint = op.properties.get('mode')
                mergetypeint = op.properties.get('mergetype')
                mousemerge = getattr(op, 'mousemerge', False)

                mode = 'Merge' if modeint== 0 else 'Connect'
                mergetype = 'AtMouse' if mousemerge else 'AtLast' if mergetypeint == 0 else 'AtCenter' if mergetypeint == 1 else 'Paths'

                if mode == 'Merge':
                    prop = mode + mergetype
                else:
                    pathtype = getattr(op, 'pathtype', False)
                    prop = mode + 'Pathsby' + pathtype.title()


        elif idname == 'machin3.smart_edge':
            if op.properties.get('is_knife_project', False):
                prop = 'KnifeProject'

            elif op.properties.get('sharp', False):
                mode = getattr(op, 'sharp_mode')

                if mode == 'SHARPEN':
                    prop = 'ToggleSharp'
                elif mode == 'CHAMFER':
                    prop = 'ToggleChamfer'
                elif mode == 'KOREAN':
                    prop = 'ToggleKoreanBevel'

            elif op.properties.get('offset', False):
                prop = 'KoreanBevel'

            elif getattr(op, 'draw_bridge_props'):
                prop = 'Bridge'

            elif getattr(op, 'is_knife'):
                prop = 'Knife'

            elif getattr(op, 'is_connect'):
                prop = 'Connect'

            elif getattr(op, 'is_starconnect'):
                prop = 'StarConnect'

            elif getattr(op, 'is_select'):
                mode = getattr(op, 'select_mode')

                if getattr(op, 'is_region'):
                    prop = 'SelectRegion'
                else:
                    prop = f'Select{mode.title()}'

            elif getattr(op, 'is_loop_cut'):
                prop = 'LoopCut'

            elif getattr(op, 'is_turn'):
                prop = 'Turn'

        elif idname == 'machin3.smart_face':
            mode = getattr(op, 'mode')

            if mode[0]:
                prop = "FaceFromVert"
            if mode[1]:
                prop = "FaceFromEdge"
            elif mode[2]:
                prop = "MeshFromFaces"

        elif idname == 'machin3.focus':
            if op.properties.get('method', 0) == 1:
                prop = 'LocalView'

        elif idname == 'machin3.mirror':
            removeall = getattr(op, 'removeall')

            if removeall:
                label = "Remove All Mirrors"

            else:
                axis = getattr(op, 'axis')
                remove = getattr(op, 'remove')

                if remove:
                    label = "Remove Mirror"

                    across = getattr(op, 'removeacross')
                    cursor = getattr(op, 'removecursor')

                else:
                    cursor = getattr(op, 'cursor')
                    across = getattr(op, 'across')

                if cursor:
                    prop = f'Cursor {axis}'
                elif across:
                    prop = f'Object {axis}'
                else:
                    prop = f'Local {axis}'

        elif idname == 'machin3.shade':
            mode = getattr(op, 'mode')

            label = f"Shade {mode.title()}"

            incl_children = getattr(op, 'include_children')
            incl_boolean = getattr(op, 'include_boolean_objs')

            if mode == 'SMOOTH':
                sharpen = getattr(op, 'sharpen')

                if sharpen:
                    prop += '+Sharpen'

            elif mode == 'FLAT':
                clear = getattr(op, 'clear')

                if clear:
                    prop += '+Clear'

            if incl_children:
                prop += ' +incl Children'

            if incl_boolean:
                prop += ' +incl. Boolean'

            prop = prop.strip()

        elif idname == 'machin3.purge_orphans':
            recursive = getattr(op, 'recursive')
            label = 'Purge Orphans Recursively' if recursive else 'Purge Orphans'



        elif idname == 'machin3.decal_library_visibility_preset':
            label = f"{label} {op.properties.get('name')}"
            prop = 'Store' if op.properties.get('store') else 'Recall'



        elif idname == 'machin3.select':
            if getattr(op, 'vgroup', False):
                prop = 'VertexGroup'
            elif getattr(op, 'faceloop', False):
                prop = 'FaceLoop'
            else:
                prop = 'Loop' if op.properties.get('loop', False) else 'Sharp'

        elif idname == 'machin3.boolean':
            prop = getattr(op, 'method', False).capitalize()

        elif idname == 'machin3.symmetrize':

            if getattr(op, 'remove'):
                prop = 'Remove'

            if getattr(op, 'partial'):
                label = 'Selected ' + label



        elif idname == 'machin3.add_object_at_cursor':
            is_pipe_init = getattr(op, 'is_pipe_init', False)

            if is_pipe_init:
                label = 'Initiate Pipe Creation'

            else:
                objtype = getattr(op, 'type', False)
                label = f"Add {objtype.title()} at Cursor"


        elif idname == 'machin3.transform_cursor':
            mode = getattr(op, 'mode', False).capitalize()
            is_array = getattr(op, 'is_array', False)
            is_macro = getattr(op, 'is_macro', False)
            is_duplicate = getattr(op, 'is_duplicate', False)

            if is_macro:
                geo = 'Mesh Selection' if context.mode == 'EDIT_MESH' else 'Object Selection'

                if is_duplicate:
                    label = f"Duplicate {mode} {geo}"

                else:
                    label = f"{mode} {geo}"

            elif is_array:

                if mode == 'Translate':
                    label = f"Linear Array"
                elif mode == 'Rotate':
                    label = f"Radial Array"

            else:
                label = f"{mode} Cursor"

        elif idname == 'machin3.pick_hyper_bevel':
            mirror = getattr(op, 'mirror')

            if mirror:
                label = 'Mirror Hyper Bevel'
            else:
                label = 'Remove Hyper Bevel'

        elif idname == 'machin3.point_cursor':
            align_y_axis = getattr(op, 'align_y_axis')
            label = 'Point Cursor'
            prop = 'Y' if align_y_axis else 'Z'

        elif idname == 'machin3.hyper_cursor_object':
            hide_all = getattr(op, 'hide_all_visible_wire_objs')
            toggle_wire_children = getattr(op, 'toggle_wire_children')
            sort_modifiers = getattr(op, 'sort_modifiers')

            if hide_all:
                label = "Hide All Visible Wire Objects"
            elif toggle_wire_children:
                label = "Toggle Wire Objects in Object Tree"
            elif sort_modifiers:
                label = "Sort Modifiers + Force Gizmo Update"


        operators.append((addon, label, idname, prop))

    if not operators:
        operators.append((None, 'Undo', 'ed.undo', ''))

    if debug:
        for addon, label, idname, prop in operators:
            print(addon, label, f"({idname})", prop)

    return operators
