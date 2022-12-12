import bpy
from .. utils.modifier import add_shrinkwrap
from .. utils.object import parent




class SurfaceSlide(bpy.types.Operator):
    bl_idname = "machin3.surface_slide"
    bl_label = "MACHIN3: Surface Slide"
    bl_description = "Start Surface Sliding: modifify the topology while keeping the inital form intact"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode == 'EDIT_MESH':
            return not [mod for mod in context.active_object.modifiers if mod.type == 'SHRINKWRAP' and 'SurfaceSlide' in mod.name]

    def execute(self, context):
        active = context.active_object
        active.update_from_editmode()

        surface = bpy.data.objects.new(name=f"{active.name}_SURFACE", object_data=active.data.copy())
        surface.data.name = '%s_SURFACE' % (active.data.name)
        surface.use_fake_user = True
        surface.matrix_world = active.matrix_world

        shrinkwrap = add_shrinkwrap(active, surface)
        shrinkwrap.name = 'SurfaceSlide'

        if active.modifiers[0] != shrinkwrap:
            bpy.ops.object.modifier_move_to_index(modifier=shrinkwrap.name, index=0)

        parent(surface, active)

        return {'FINISHED'}


class FinishSurfaceSlide(bpy.types.Operator):
    bl_idname = "machin3.finish_surface_slide"
    bl_label = "MACHIN3: Finish Surface Slide"
    bl_description = "Stop Surface Sliding"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active = context.active_object if context.active_object else None
        if active:
            return [mod for mod in context.active_object.modifiers if mod.type == 'SHRINKWRAP' and 'SurfaceSlide' in mod.name]

    def execute(self, context):
        active = context.active_object

        surfaceslide = self.get_surface_slide(active)
        surface = surfaceslide.target

        editmode = context.mode == 'EDIT_MESH'

        if editmode:
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.modifier_apply(modifier=surfaceslide.name)

        if editmode:
            bpy.ops.object.mode_set(mode='EDIT')

        if surface:
            bpy.data.meshes.remove(surface.data, do_unlink=True)

        return {'FINISHED'}

    def get_surface_slide(self, obj):
        surfaceslide = obj.modifiers.get('SurfaceSlide')

        if not surfaceslide:
            surfaceslide = [mod for mod in obj.modifiers if mod.type == 'SHRINKWRAP' and 'SurfaceSlide' in mod.name][0]

        return surfaceslide
