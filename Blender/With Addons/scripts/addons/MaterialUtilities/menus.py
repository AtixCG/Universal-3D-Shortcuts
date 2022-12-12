import bpy

from .functions import *
from .operators import *
from .preferences import *

# -----------------------------------------------------------------------------
# menu classes

class VIEW3D_MT_materialutilities_assign_material(bpy.types.Menu):
    """Menu for choosing which material should be assigned to current selection"""
    # The menu is filled programmatically with available materials

    bl_idname = "VIEW3D_MT_materialutilities_assign_material"
    bl_label = "Assign Material"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        edit_mode = False

        materials = bpy.data.materials.items()

        bl_id = VIEW3D_OT_materialutilities_assign_material_object.bl_idname
        obj = context.object
        mu_prefs = materialutilities_get_preferences(context)

        if (not obj is None) and obj.mode == 'EDIT':
            bl_id = VIEW3D_OT_materialutilities_assign_material_edit.bl_idname
            edit_mode = True

        if len(materials) > mu_prefs.search_show_limit:
            op = layout.operator(bl_id,
                            text = 'Search',
                            icon = 'VIEWZOOM')
            op.material_name = ""
            op.new_material = False
            op.show_dialog = True
            if not edit_mode:
                op.override_type = mu_prefs.override_type

        op = layout.operator(bl_id,
                text = "Add New Material",
                icon = 'ADD')
        op.material_name = mu_new_material_name(mu_prefs.new_material_name)
        op.new_material = True
        op.show_dialog = True
        if not edit_mode:
            op.override_type = mu_prefs.override_type

        layout.separator()

        mat_count = 0

        for material_name, material in materials:
            # If Theres a limit, and we reached it, stop!
            if (mu_prefs.material_show_limit > 0) and (mat_count >= mu_prefs.material_show_limit):
                break

            # Should we show Grease Pencil materials?
            if not mu_prefs.include_gp_materials:
                if material.is_grease_pencil:
                    continue

            # New materials don't have .preview set (until the preview is generated)
            #  So, if the material has a preview, use that
            if (type(material.preview) is bpy.types.ImagePreview):
                op = layout.operator(bl_id,
                        text = material_name,
                        icon_value = material.preview.icon_id)
            # If the material does not have a preview, use standard material icon
            else:
                op = layout.operator(bl_id,
                        text = material_name,
                        icon = 'MATERIAL_DATA')

            op.material_name = material_name
            op.new_material = False
            op.show_dialog = False
            if not edit_mode:
                op.override_type = mu_prefs.override_type

            mat_count += 1

        # If there's enough number of materials, add a Search option at the end of the list
        if mat_count > mu_prefs.search_show_btm_limit:
            layout.separator()
            layout.operator(bl_id,
                            text = 'Search',
                            icon = 'VIEWZOOM'
                            ).show_dialog = True

            op = layout.operator(bl_id,
                    text = "Add New Material",
                    icon = 'ADD')
            op.material_name = mu_new_material_name(mu_prefs.new_material_name)
            op.new_material = True
            op.show_dialog = True
            if not edit_mode:
                op.override_type = mu_prefs.override_type


class VIEW3D_MT_materialutilities_clean_slots(bpy.types.Menu):
    """Menu for cleaning up the material slots"""

    bl_idname = "VIEW3D_MT_materialutilities_clean_slots"
    bl_label = "Clean Slots"

    def draw(self, context):
        layout = self.layout

        layout.label
        layout.operator(VIEW3D_OT_materialutilities_clean_material_slots.bl_idname,
                        text = "Clean Material Slots",
                        icon = 'X')
        layout.separator()
        layout.operator(VIEW3D_OT_materialutilities_remove_material_slot.bl_idname,
                        text = "Remove Active Material Slot",
                        icon = 'REMOVE')
        layout.operator(VIEW3D_OT_materialutilities_remove_all_material_slots.bl_idname,
                        text = "Remove All Material Slots",
                        icon = 'CANCEL')


class VIEW3D_MT_materialutilities_select_by_material(bpy.types.Menu):
    """Menu for choosing which material should be used for selection"""
    # The menu is filled programmatically with available materials

    bl_idname = "VIEW3D_MT_materialutilities_select_by_material"
    bl_label = "Select by Material"

    def draw(self, context):
        layout = self.layout

        bl_id = VIEW3D_OT_materialutilities_select_by_material_name.bl_idname
        obj = context.object
        mu_prefs = materialutilities_get_preferences(context)

        layout.label

        mat_count = 0

        if obj is None or obj.mode == 'OBJECT':
            materials = bpy.data.materials.items()

            if len(materials) > mu_prefs.search_show_limit:
                layout.operator(bl_id,
                                text = 'Search',
                                icon = 'VIEWZOOM'
                                ).show_dialog = True

                layout.separator()

            # Show all used materials in entire blend file
            for material_name, material in materials:
                # If Theres a limit, and we reached it, stop!
                if (mu_prefs.material_show_limit > 0) and (mat_count >= mu_prefs.material_show_limit):
                    break

                # Should we show Grease Pencil materials?
                if not mu_prefs.include_gp_materials:
                    if material.is_grease_pencil:
                        continue

                # There's no point in showing materials with 0 users
                #  (It will still show materials with fake user though)
                if material.users > 0:
                    # New materials don't have .preview set (until the preview is generated)
                    #  So, if the material has a preview, use that
                    if (type(material.preview) is bpy.types.ImagePreview):
                        op = layout.operator(bl_id,
                                text = material_name,
                                icon_value = material.preview.icon_id)
                    # If the material does not have a preview, use standard material icon
                    else:
                        op = layout.operator(bl_id,
                                text = material_name,
                                icon = 'MATERIAL_DATA')
                    op.material_name = material_name
                    op.show_dialog = False

                mat_count += 1

        elif obj.mode == 'EDIT':
            objects = context.selected_editable_objects
            materials_added = []

            # There can be an active object (that is in Edit mode), but not actually "selected"
            #  (so it isn't listed in selected_objects)
            if len(objects) == 0:
                objects = [obj]

            for obj in objects:
                #show only the materials on this object
                material_slots = obj.material_slots
                for material_slot in material_slots:
                    material = material_slot.material

                    # Don't add a material that's already in the menu
                    if material.name in materials_added:
                        continue

                    # New materials don't have .preview set (until the preview is generated)
                    #  So, if the material has a preview, use that
                    if (type(material.preview) is bpy.types.ImagePreview):
                        op = layout.operator(bl_id,
                                text = material.name,
                                icon_value = material.preview.icon_id)
                    # If the material does not have a preview, use standard material icon
                    else:
                        op = layout.operator(bl_id,
                                text = material.name,
                                icon = 'MATERIAL_DATA')
                    op.material_name = material.name
                    op.show_dialog = False

                    materials_added.append(material.name)

                    mat_count += 1

        if mat_count > mu_prefs.search_show_btm_limit:
            layout.separator()
            layout.operator(bl_id,
                            text = 'Search',
                            icon = 'VIEWZOOM'
                            ).show_dialog = True

class VIEW3D_MT_materialutilities_specials(bpy.types.Menu):
    """Specials menu for Material Utilities"""

    bl_idname = "VIEW3D_MT_materialutilities_specials"
    bl_label = "Specials"

    def draw(self, context):
        mu_prefs = materialutilities_get_preferences(context)
        layout = self.layout

        layout.operator(MATERIAL_OT_materialutilities_merge_base_names.bl_idname,
                        text = "Merge Base Names",
                        icon = "GREASEPENCIL")

        layout.operator(MATERIAL_OT_materialutilities_join_objects.bl_idname,
                        text = "Join by material",
                        icon = "OBJECT_DATAMODE")

        layout.separator()

        op = layout.operator(MATERIAL_OT_materialutilities_remove_unused_materials.bl_idname,
                        text = "Remove unused materials",
                        icon = "TRASH")

        layout.separator()

        op = layout.operator(MATERIAL_OT_materialutilities_auto_smooth_angle.bl_idname,
                        text = "Set Auto Smooth",
                        icon = "SHADING_SOLID")
        op.affect = mu_prefs.set_smooth_affect
        op.angle = mu_prefs.auto_smooth_angle

class VIEW3D_MT_materialutilities_main(bpy.types.Menu):
    """Main menu for Material Utilities"""

    bl_idname = "VIEW3D_MT_materialutilities_main"
    bl_label = "Material Utilities"

    def draw(self, context):
        obj = context.object
        mu_prefs = materialutilities_get_preferences(context)

        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.menu(VIEW3D_MT_materialutilities_assign_material.bl_idname,
                     icon = 'ADD')
        layout.menu(VIEW3D_MT_materialutilities_select_by_material.bl_idname,
                     icon = 'VIEWZOOM')
        layout.separator()

        active_object = bpy.context.active_object
        copy_lbl = 'Copy Material to Selected' if active_object.mode == 'EDIT' else 'Copy Materials to Selected'
        layout.operator(VIEW3D_OT_materialutilities_copy_material_to_others.bl_idname,
                         text = copy_lbl,
                         icon = 'COPY_ID')

        layout.separator()

        layout.menu(VIEW3D_MT_materialutilities_clean_slots.bl_idname,
                    icon = 'NODE_MATERIAL')

        layout.separator()

        layout.operator(VIEW3D_OT_materialutilities_replace_material.bl_idname,
                        text = 'Replace Material',
                        icon = 'OVERLAY')

        if mu_prefs.show_multiple_materials_replacement:
            layout.operator(VIEW3D_OT_materialutilities_replace_multiple_materials.bl_idname,
                            text = 'Replace Multiple Materials',
                            icon = 'OVERLAY')

        op = layout.operator(VIEW3D_OT_materialutilities_fake_user_set.bl_idname,
                       text = 'Set Fake User',
                       icon = 'FAKE_USER_OFF')
        op.fake_user = mu_prefs.fake_user
        op.affect = mu_prefs.fake_user_affect

        op = layout.operator(VIEW3D_OT_materialutilities_change_material_link.bl_idname,
                       text = 'Change Material Link',
                       icon = 'LINKED')
        op.link_to = mu_prefs.link_to
        op.affect = mu_prefs.link_to_affect
        layout.separator()

        layout.menu(VIEW3D_MT_materialutilities_specials.bl_idname,
                        icon = 'SOLO_ON')



def materialutilities_specials_menu(self, contxt):
    self.layout.separator()
    self.layout.menu(VIEW3D_MT_materialutilities_main.bl_idname)


def materialutilities_menu_move(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_REGION_WIN'

    layout.operator(MATERIAL_OT_materialutilities_material_slot_move.bl_idname,
                    icon = 'TRIA_UP_BAR',
                    text = 'Move Slot to the Top').movement = 'TOP'
    layout.operator(MATERIAL_OT_materialutilities_material_slot_move.bl_idname,
                    icon = 'TRIA_DOWN_BAR',
                    text = 'Move Slot to the Bottom').movement = 'BOTTOM'
    layout.separator()

def materialutilities_menu_functions(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_REGION_WIN'

    layout.separator()

    layout.menu(VIEW3D_MT_materialutilities_assign_material.bl_idname,
                 icon = 'ADD')
    layout.menu(VIEW3D_MT_materialutilities_select_by_material.bl_idname,
                 icon = 'VIEWZOOM')
    layout.separator()

    layout.operator(VIEW3D_OT_materialutilities_copy_material_to_others.bl_idname,
                     text = 'Copy Materials to Selected',
                     icon = 'COPY_ID')

    layout.separator()

    layout.menu(VIEW3D_MT_materialutilities_clean_slots.bl_idname,
                icon = 'NODE_MATERIAL')

    layout.separator()
    layout.operator(VIEW3D_OT_materialutilities_replace_material.bl_idname,
                    text = 'Replace Material',
                    icon = 'OVERLAY')

    layout.operator(VIEW3D_OT_materialutilities_fake_user_set.bl_idname,
                   text = 'Set Fake User',
                   icon = 'FAKE_USER_OFF')

    layout.operator(VIEW3D_OT_materialutilities_change_material_link.bl_idname,
                   text = 'Change Material Link',
                   icon = 'LINKED')
    layout.separator()

    layout.menu(VIEW3D_MT_materialutilities_specials.bl_idname,
                    icon = 'SOLO_ON')
