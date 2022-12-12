import bpy
from .preferences import get_preferences


me_keyboard_keymap = []
me_mouse_keymap = []
ob_keyboard_keymap = []
ob_mouse_keymap = []
toggles_keymap = []


def register_me_keyboard_keymap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Mesh", space_type='EMPTY')

        kmi = km.keymap_items.new("mesh.select_lasso_xray", 'L', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        me_keyboard_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_circle_xray", 'C', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        me_keyboard_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_box_xray", 'B', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        me_keyboard_keymap.append((km, kmi))


def register_me_mouse_keymap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Mesh", space_type='EMPTY')

        kmi = km.keymap_items.new("mesh.select_lasso_xray", 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True, shift=True)
        kmi.properties.mode = 'SUB'
        me_mouse_keymap.append((km, kmi))
        
        kmi = km.keymap_items.new("mesh.select_lasso_xray", 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True)
        kmi.properties.mode = 'ADD'
        me_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_box_xray", 'RIGHTMOUSE', 'CLICK_DRAG', ctrl=True)
        kmi.properties.mode = 'SUB'
        me_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_box_xray", 'RIGHTMOUSE', 'CLICK_DRAG', shift=True)
        kmi.properties.mode = 'ADD'
        me_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_box_xray", 'RIGHTMOUSE', 'CLICK_DRAG')
        kmi.properties.mode = 'SET'
        me_mouse_keymap.append((km, kmi))


def register_ob_keyboard_keymap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Object Mode", space_type='EMPTY')

        kmi = km.keymap_items.new("object.select_lasso_xray", 'L', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        ob_keyboard_keymap.append((km, kmi))
        
        kmi = km.keymap_items.new("object.select_circle_xray", 'C', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        ob_keyboard_keymap.append((km, kmi))
        
        kmi = km.keymap_items.new("object.select_box_xray", 'B', 'PRESS')
        kmi.properties.mode = 'ADD'
        kmi.properties.wait_for_input = True
        ob_keyboard_keymap.append((km, kmi))


def register_ob_mouse_keymap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Object Mode", space_type='EMPTY')

        kmi = km.keymap_items.new("object.select_lasso_xray", 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True, shift=True)
        kmi.properties.mode = 'SUB'
        ob_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("object.select_lasso_xray", 'LEFTMOUSE', 'CLICK_DRAG', ctrl=True)
        kmi.properties.mode = 'ADD'
        ob_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("object.select_box_xray", 'RIGHTMOUSE', 'CLICK_DRAG', ctrl=True)
        kmi.properties.mode = 'SUB'
        ob_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("object.select_box_xray", 'RIGHTMOUSE', 'CLICK_DRAG', shift=True)
        kmi.properties.mode = 'ADD'
        ob_mouse_keymap.append((km, kmi))

        kmi = km.keymap_items.new("object.select_box_xray", 'RIGHTMOUSE', 'CLICK_DRAG')
        kmi.properties.mode = 'SET'
        ob_mouse_keymap.append((km, kmi))


def register_toggles_keymap():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Mesh", space_type='EMPTY')

        kmi = km.keymap_items.new("mesh.select_tools_xray_toggle_mesh_behavior", 'X', 'PRESS', ctrl=True, shift=True)
        toggles_keymap.append((km, kmi))

        kmi = km.keymap_items.new("mesh.select_tools_xray_toggle_select_through", 'X', 'PRESS', ctrl=True, alt=True)
        toggles_keymap.append((km, kmi))


def unregister_me_keyboard_keymap():
    for km, kmi in me_keyboard_keymap:
        km.keymap_items.remove(kmi)
    me_keyboard_keymap.clear()


def unregister_me_mouse_keymap():
    for km, kmi in me_mouse_keymap:
        km.keymap_items.remove(kmi)
    me_mouse_keymap.clear()


def unregister_ob_keyboard_keymap():
    for km, kmi in ob_keyboard_keymap:
        km.keymap_items.remove(kmi)
    ob_keyboard_keymap.clear()


def unregister_ob_mouse_keymap():
    for km, kmi in ob_mouse_keymap:
        km.keymap_items.remove(kmi)
    ob_mouse_keymap.clear()


def unregister_toggles_keymap():
    for km, kmi in toggles_keymap:
        km.keymap_items.remove(kmi)
    toggles_keymap.clear()


def toggle_me_keyboard_keymap(self, context):
    if get_preferences().enable_me_keyboard_keymap:
        register_me_keyboard_keymap()
    else:
        unregister_me_keyboard_keymap()


def toggle_me_mouse_keymap(self, context):
    if get_preferences().enable_me_mouse_keymap:
        register_me_mouse_keymap()
    else:
        unregister_me_mouse_keymap()


def toggle_ob_keyboard_keymap(self, context):
    if get_preferences().enable_ob_keyboard_keymap:
        register_ob_keyboard_keymap()
    else:
        unregister_ob_keyboard_keymap()


def toggle_ob_mouse_keymap(self, context):
    if get_preferences().enable_ob_mouse_keymap:
        register_ob_mouse_keymap()
    else:
        unregister_ob_mouse_keymap()


def toggle_toggles_keymap(self, context):
    if get_preferences().enable_toggles_keymap:
        register_toggles_keymap()
    else:
        unregister_toggles_keymap()


def register():
    if get_preferences().enable_me_mouse_keymap:
        register_me_mouse_keymap()
    if get_preferences().enable_me_keyboard_keymap:
        register_me_keyboard_keymap()
    if get_preferences().enable_ob_mouse_keymap:
        register_ob_mouse_keymap()
    if get_preferences().enable_ob_keyboard_keymap:
        register_ob_keyboard_keymap()
    if get_preferences().enable_toggles_keymap:
        register_toggles_keymap()


def unregister():
    unregister_me_mouse_keymap()
    unregister_me_keyboard_keymap()
    unregister_ob_mouse_keymap()
    unregister_ob_keyboard_keymap()
    unregister_toggles_keymap()
