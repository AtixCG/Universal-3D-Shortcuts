import bpy
import rna_keymap_ui
bl_info = {
    "name": "Auto Delete :)",
    "location": "View3D > Add > Mesh > Auto Delete,",
    "description": "Auto detect a delete elements",
    "author": "Vladislav Kindushov",
    "version": (0, 3),
    "blender": (2, 80, 0),
    "category": "Mesh",
}

addon_keymaps = []

def find_connected_verts(me, found_index):
    edges = me.edges
    connecting_edges = [i for i in edges if found_index in i.vertices[:]]
    return len(connecting_edges)


class VIEW3D_OT_auto_delete(bpy.types.Operator):
    """ Dissolves mesh elements based on context instead
    of forcing the user to select from a menu what
    it should dissolve.
    """
    bl_idname = "view3d.auto_delete"
    bl_label = "Auto Delete"
    bl_options = {'UNDO'}

    use_verts = bpy.props.BoolProperty(name="Use Verts", default=False)

    @classmethod
    def poll(cls, context):
        return context.mode in ['EDIT_CURVE', 'OBJECT', 'EDIT_MESH']

    def execute(self, context):
        if bpy.context.mode == 'OBJECT':
            sel = bpy.context.selected_objects

            bpy.ops.object.delete(use_global=True)

        elif bpy.context.mode == 'EDIT_MESH':
            select_mode = context.tool_settings.mesh_select_mode
            me = context.object.data
            if select_mode[0]:
                vertex = me.vertices

                bpy.ops.mesh.dissolve_verts()

                if vertex == me.vertices:
                    bpy.ops.mesh.delete(type='VERT')


            elif select_mode[1] and not select_mode[2]:
                edges1 = me.edges

                bpy.ops.mesh.dissolve_edges(use_verts=True, use_face_split=False)
                if edges1 == me.edges:
                    bpy.ops.mesh.delete(type='EDGE')

                bpy.ops.mesh.select_mode(type='EDGE')

                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='EDIT')
                vs = [v.index for v in me.vertices if v.select]
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')

                for v in vs:
                    vv = find_connected_verts(me, v)
                    if vv == 2:
                        me.vertices[v].select = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.dissolve_verts()
                bpy.ops.mesh.select_all(action='DESELECT')

                for v in vs:
                    me.vertices[v].select = True


            elif select_mode[2] and not select_mode[1]:
                bpy.ops.mesh.delete(type='FACE')
            else:
                bpy.ops.mesh.dissolve_verts()

        elif bpy.context.mode == 'EDIT_CURVE':
            bpy.ops.curve.delete(type='VERT')
        return {'FINISHED'}

def FindConflict(box):
    find = bpy.context.window_manager.keyconfigs.user.keymaps['3D View'].keymap_items.get('view3d.auto_delete')
    ku = bpy.context.window_manager.keyconfigs.user
    km = ['3D View','3D View Generic','Object Mode', 'Mesh','Curve']
    for km_n in km: 
        for i in bpy.context.window_manager.keyconfigs.user.keymaps[km_n].keymap_items:
            if find.type == i.type and find.ctrl == i.ctrl and find.alt == i.alt and find.shift == i.shift and find.name != i.name:
                col = box.column()
                col.label(text='Conflict hotkey: ' + '3D View -> ' + km_n + ' -> ' + i.name + " : ")
                col.prop(i, 'active')

class auto_delete_pref(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        box = layout.row().box()
        FindConflict(box)
        box = layout.row().box()

        ku = bpy.context.window_manager.keyconfigs.user
        km = ku.keymaps.get('3D View')

        kmi = km.keymap_items.get('view3d.auto_delete')
        rna_keymap_ui.draw_kmi([], ku, km, kmi, box, 0)

classes = (VIEW3D_OT_auto_delete, auto_delete_pref)



def register():
    for c in classes:
        bpy.utils.register_class(c)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.auto_delete', 'X', 'PRESS', ctrl=False, shift=False)
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()

    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()