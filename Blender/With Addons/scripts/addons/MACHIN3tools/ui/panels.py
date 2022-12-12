import bpy
from .. utils.registration import get_prefs
from .. utils.group import get_group_polls
from .. utils.ui import get_icon
from .. import bl_info


class PanelMACHIN3tools(bpy.types.Panel):
    bl_idname = "MACHIN3_PT_machin3_tools"
    bl_label = "MACHIN3tools %s" % ('.'.join([str(v) for v in bl_info['version']]))
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MACHIN3"
    bl_order = 20

    @classmethod
    def poll(cls, context):
        p = get_prefs()

        if p.show_sidebar_panel:
            if context.mode == 'OBJECT':
                return p.activate_smart_drive or p.activate_unity or p.activate_group or p.activate_assetbrowser_tools
            elif context.mode == 'EDIT_MESH':
                return p.activate_extrude

    def draw(self, context):
        layout = self.layout

        m3 = context.scene.M3
        p = get_prefs()

        if context.mode == 'OBJECT':

            if p.activate_smart_drive:
                box = layout.box()
                box.prop(m3, "show_smart_drive", text="Smart Drive", icon='TRIA_DOWN' if m3.show_smart_drive else 'TRIA_RIGHT', emboss=False)

                if m3.show_smart_drive:
                    self.draw_smart_drive(m3, box)

            if p.activate_unity:
                box = layout.box()

                box.prop(m3, "show_unity", text="Unity", icon='TRIA_DOWN' if m3.show_unity else 'TRIA_RIGHT', emboss=False)

                if m3.show_unity:
                    self.draw_unity(context, m3, box)

            if p.activate_group:
                box = layout.box()

                box.prop(m3, "show_group", text="Group", icon='TRIA_DOWN' if m3.show_group else 'TRIA_RIGHT', emboss=False)

                if m3.show_group:
                    self.draw_group(context, m3, box)

            if p.activate_assetbrowser_tools:
                box = layout.box()

                box.prop(m3, "show_assetbrowser_tools", text="Assetbrowser Tools", icon='TRIA_DOWN' if m3.show_assetbrowser_tools else 'TRIA_RIGHT', emboss=False)

                if m3.show_assetbrowser_tools:
                    self.draw_assetbrowser_tools(context, box)

        elif context.mode == 'EDIT_MESH':

            if p.activate_extrude:
                box = layout.box()

                box.prop(m3, "show_extrude", text="Extrude", icon='TRIA_DOWN' if m3.show_extrude else 'TRIA_RIGHT', emboss=False)

                if m3.show_extrude:
                    self.draw_extrude(context, m3, box)

    def draw_smart_drive(self, m3, layout):
        column = layout.column()

        b = column.box()
        b.label(text="Driver")

        col = b.column(align=True)

        row = col.split(factor=0.25, align=True)
        row.label(text="Values")
        r = row.row(align=True)
        op = r.operator("machin3.set_driver_value", text='', icon='SORT_ASC')
        op.mode = 'DRIVER'
        op.value = 'START'
        r.prop(m3, 'driver_start', text='')
        r.operator("machin3.switch_driver_values", text='', icon='ARROW_LEFTRIGHT').mode = 'DRIVER'
        r.prop(m3, 'driver_end', text='')
        op = r.operator("machin3.set_driver_value", text='', icon='SORT_ASC')
        op.mode = 'DRIVER'
        op.value = 'END'

        row = col.split(factor=0.25, align=True)
        row.label(text="Transform")
        r = row.row(align=True)
        r.prop(m3, 'driver_transform', expand=True)

        row = col.split(factor=0.25, align=True)
        row.scale_y = 0.9
        row.label(text="Axis")
        r = row.row(align=True)
        r.prop(m3, 'driver_axis', expand=True)

        row = col.split(factor=0.25, align=True)
        row.label(text="Space")
        r = row.row(align=True)
        r.prop(m3, 'driver_space', expand=True)


        b = column.box()
        b.label(text="Driven")

        col = b.column(align=True)

        row = col.split(factor=0.25, align=True)
        row.label(text="Values")
        r = row.row(align=True)
        op = r.operator("machin3.set_driver_value", text='', icon='SORT_ASC')
        op.mode = 'DRIVEN'
        op.value = 'START'
        r.prop(m3, 'driven_start', text='')
        r.operator("machin3.switch_driver_values", text='', icon='ARROW_LEFTRIGHT').mode = 'DRIVEN'
        r.prop(m3, 'driven_end', text='')
        op = r.operator("machin3.set_driver_value", text='', icon='SORT_ASC')
        op.mode = 'DRIVEN'
        op.value = 'END'

        row = col.split(factor=0.25, align=True)
        row.label(text="Transform")
        r = row.row(align=True)
        r.prop(m3, 'driven_transform', expand=True)

        row = col.split(factor=0.25, align=True)
        row.scale_y = 0.9
        row.label(text="Axis")
        r = row.row(align=True)
        r.prop(m3, 'driven_axis', expand=True)

        row = col.split(factor=0.25, align=True)
        row.label(text="Limit")
        r = row.row(align=True)
        r.prop(m3, 'driven_limit', expand=True)

        r = column.row()
        r.scale_y = 1.2
        r.operator("machin3.smart_drive", text='Drive it!', icon='AUTO')

    def draw_unity(self, context, m3, layout):
        all_prepared = True if context.selected_objects and all([obj.M3.unity_exported for obj in context.selected_objects]) else False

        column = layout.column(align=True)

        row = column.split(factor=0.3)
        row.label(text="Export")
        row.prop(m3, 'unity_export', text='True' if m3.unity_export else 'False', toggle=True)

        row = column.split(factor=0.3)
        row.label(text="Triangulate")
        row.prop(m3, 'unity_triangulate', text='True' if m3.unity_triangulate else 'False', toggle=True)

        column.separator()

        if m3.unity_export:
            column.prop(m3, 'unity_export_path', text='')

            if all_prepared:
                row = column.row(align=True)
                row.scale_y = 1.5

                if m3.unity_export_path:
                    row.operator_context = 'EXEC_DEFAULT'

                op = row.operator("export_scene.fbx", text='Export')
                op.use_selection = True
                op.apply_scale_options = 'FBX_SCALE_ALL'

                if m3.unity_export_path:
                    op.filepath = m3.unity_export_path

        if not m3.unity_export or not all_prepared:
            row = column.row(align=True)
            row.scale_y = 1.5
            row.operator("machin3.prepare_unity_export", text="Prepare + Export %s" % ('Selected' if context.selected_objects else 'Visible') if m3.unity_export else "Prepare %s" % ('Selected' if context.selected_objects else 'Visible')).prepare_only = False

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("machin3.restore_unity_export", text="Restore Transformations")

    def draw_group(self, context, m3, layout):
        column = layout.column(align=True)
        p = get_prefs()

        active_group, active_child, group_empties, groupable, ungroupable, addable, removable, selectable, duplicatable, groupifyable = get_group_polls(context)



        row = column.row()
        row = column.split(factor=0.3, align=True)
        row.active = active_group or m3.affect_only_group_origin
        row.label(text="Group Origin")

        if active_group or m3.affect_only_group_origin:

            if m3.affect_only_group_origin:
                row.prop(m3, "affect_only_group_origin", text="Disable, when done!", toggle=True, icon_value=get_icon('error'))
            else:
                row.prop(m3, "affect_only_group_origin", text="Adjust", toggle=True, icon='OBJECT_ORIGIN')

        else:
            r = row.split(factor=0.4)
            r.separator()
            r.label(text="None")

        column.separator()



        row = column.split(factor=0.3, align=True)
        row.label(text="Auto Select")
        r = row.row(align=True)
        if not p.use_group_sub_menu:
            r.prop(m3, 'show_group_select', text='', icon='HIDE_OFF' if m3.show_group_select else 'HIDE_ON')
        r.prop(m3, 'group_select', text='True' if m3.group_select else 'False', toggle=True)

        row = column.split(factor=0.3, align=True)
        row.label(text="Recursive")
        r = row.row(align=True)
        if not p.use_group_sub_menu:
            r.prop(m3, 'show_group_recursive_select', text='', icon='HIDE_OFF' if m3.show_group_recursive_select else 'HIDE_ON')
        r.prop(m3, 'group_recursive_select', text='True' if m3.group_recursive_select else 'False', toggle=True)

        row = column.split(factor=0.3, align=True)
        row.label(text="Hide Empties")
        r = row.row(align=True)
        if not p.use_group_sub_menu:
            r.prop(m3, 'show_group_hide', text='', icon='HIDE_OFF' if m3.show_group_hide else 'HIDE_ON')
        r.prop(m3, 'group_hide', text='True' if m3.group_hide else 'False', toggle=True)



        column = layout.column(align=True)

        row = column.row(align=True)
        row.scale_y = 1.2
        r = row.row(align=True)
        r.active = groupable
        r.operator("machin3.group", text="Group")
        r = row.row(align=True)
        r.active = ungroupable
        r.operator("machin3.ungroup", text="Un-Group")
        r = row.row(align=True)

        row = column.row(align=True)
        row.scale_y = 1
        r.active = groupifyable
        row.operator("machin3.groupify", text="Groupify")



        column = layout.column(align=True)

        row = column.row(align=True)
        row.scale_y = 1.2
        r = row.row(align=True)
        r.active = selectable
        r.operator("machin3.select_group", text="Select Group")
        r = row.row(align=True)
        r.active = duplicatable
        r.operator("machin3.duplicate_group", text="Duplicate Group")



        column = layout.column(align=True)

        row = column.row(align=True)
        row.scale_y = 1.2
        r = row.row(align=True)
        r.active = addable and (active_group or active_child)
        r.operator("machin3.add_to_group", text="Add to Group")
        r = row.row(align=True)
        r.active = removable
        r.operator("machin3.remove_from_group", text="Remove from Group")

    def draw_extrude(self, context, m3, layout):
        column = layout.column(align=True)

        row = column.row(align=True)
        row.scale_y = 1.2
        row.operator("machin3.cursor_spin", text='Cursor Spin')
        row.operator("machin3.punch_it_a_little", text='Punch It (a little)', icon_value=get_icon('fist'))

    def draw_assetbrowser_tools(self, context, layout):
        column = layout.column(align=True)
        column.scale_y = 1.2

        column.operator("machin3.create_assembly_asset", text='Create Assembly Asset', icon='ASSET_MANAGER')
        column.operator("machin3.assemble_instance_collection", text='Assemble Instance Collection', icon='NETWORK_DRIVE')

