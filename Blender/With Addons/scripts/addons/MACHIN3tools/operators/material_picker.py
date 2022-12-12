import bpy
from bpy.props import BoolProperty
from bl_ui.space_statusbar import STATUSBAR_HT_header as statusbar
from mathutils import Vector
from .. utils.raycast import cast_obj_ray_from_mouse, cast_bvh_ray_from_mouse
from .. utils.draw import draw_label
from .. utils.registration import get_prefs
from .. items import alt


def draw_material_pick_status(self, context):
    layout = self.layout

    row = layout.row(align=True)
    row.label(text=f"Material Picker")

    row.label(text="", icon='MOUSE_LMB')
    row.label(text="Pick Material")

    row.label(text="", icon='MOUSE_MMB')
    row.label(text="Viewport")

    row.label(text="", icon='MOUSE_RMB')
    row.label(text="Cancel")

    row.separator(factor=10)

    row.label(text="", icon='EVENT_ALT')
    row.label(text="Assign Material")


class MaterialPicker(bpy.types.Operator):
    bl_idname = "machin3.material_picker"
    bl_label = "MACHIN3: Material Picker"
    bl_description = "Pick a Material from the 3D View\nALT: Assign it to the Selection too"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def draw_HUD(self, args):
        context, event = args

        draw_label(context, title="Assign" if self.is_assign else "Pick", coords=self.mousepos + Vector((20, 10)), center=False)

    def modal(self, context, event):
        context.area.tag_redraw()

        self.mousepos = Vector((event.mouse_region_x, event.mouse_region_y))
        self.is_assign = event.alt

        if event.type == 'LEFTMOUSE':
            if context.mode == 'OBJECT':
                hitobj, hitobj_eval, _, _, hitindex, _ = cast_obj_ray_from_mouse(self.mousepos, depsgraph=self.dg, debug=False)

            elif context.mode == 'EDIT_MESH':
                hitobj, _, _, hitindex, _, _ = cast_bvh_ray_from_mouse(self.mousepos, candidates=[obj for obj in context.visible_objects if obj.mode == 'EDIT'])

            if hitobj:
                if context.mode == 'OBJECT':
                    matindex = hitobj_eval.data.polygons[hitindex].material_index
                elif context.mode == 'EDIT_MESH':
                    matindex = hitobj.data.polygons[hitindex].material_index

                context.view_layer.objects.active = hitobj
                hitobj.active_material_index = matindex

                if hitobj.material_slots and hitobj.material_slots[matindex].material:
                    mat = hitobj.material_slots[matindex].material

                    if self.is_assign:
                        sel = [obj for obj in context.selected_objects if obj != hitobj and obj.data]

                        for obj in sel:
                            if not obj.material_slots:
                                obj.data.materials.append(mat)

                            else:
                                obj.material_slots[obj.active_material_index].material = mat


                    bpy.ops.machin3.draw_label(text=mat.name, coords=self.mousepos, alpha=1, time=get_prefs().HUD_fade_material_picker)

                else:
                    bpy.ops.machin3.draw_label(text="Empty", coords=self.mousepos, color=(0.5, 0.5, 0.5), alpha=1, time=get_prefs().HUD_fade_material_picker + 0.2)

            else:
                bpy.ops.machin3.draw_label(text="None", coords=self.mousepos, color=(1, 0, 0), alpha=1, time=get_prefs().HUD_fade_material_picker + 0.2)

            self.finish(context)
            return {'FINISHED'}

        elif event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'}

        elif event.type in ['RIGHTMOUSE', 'ESC']:
            self.finish(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def finish(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

        context.window.cursor_set("DEFAULT")

        statusbar.draw = self.bar_orig

        if context.visible_objects:
            context.visible_objects[0].select_set(context.visible_objects[0].select_get())

    def invoke(self, context, event):

        self.is_assign = False 

        context.window.cursor_set("EYEDROPPER")
        self.mousepos = Vector((event.mouse_region_x, event.mouse_region_y))

        self.dg = context.evaluated_depsgraph_get()

        self.bar_orig = statusbar.draw
        statusbar.draw = draw_material_pick_status

        if context.visible_objects:
            context.visible_objects[0].select_set(context.visible_objects[0].select_get())

        args = (context, event)
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
