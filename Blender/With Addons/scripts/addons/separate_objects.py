bl_info = {
    "name": "Separate Objects",
    "author": "Atix",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "View3D > Object Mode > Object Context Menu / Object Menu",
    "description": "Separates Selected Objects in Object Mode",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

import bpy

class SeparateObjetcsOperator(bpy.types.Operator):
    """Separate Objects"""
    bl_idname = "object.separate_objetcs"
    bl_label = "Separate Objetcs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objs = context.selected_objects
        for obj in objs:
            if obj.type == 'MESH':
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.separate(type='LOOSE')
                bpy.ops.object.editmode_toggle()

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        return {'FINISHED'}


def draw_inmenu(self, context):
    self.layout.operator("object.separate_objetcs", text="Separate")


addon_keymaps = []


def register():
    bpy.utils.register_class(SeparateObjetcsOperator)
    bpy.types.VIEW3D_MT_object_context_menu.append(draw_inmenu)
    bpy.types.VIEW3D_MT_object.append(draw_inmenu)

    # KEYMAP
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(
        name='Object Mode', space_type='VIEW_3D')
    kmi = km.keymap_items.new("object.separate_objetcs", 'S', 'PRESS', ctrl=True, shift=True, alt = True)
    addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(SeparateObjetcsOperator)
    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_inmenu)
    bpy.types.VIEW3D_MT_object.remove(draw_inmenu)
    # KEYMAP
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()