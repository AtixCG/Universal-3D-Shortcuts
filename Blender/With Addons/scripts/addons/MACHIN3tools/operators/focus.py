import bpy
import bmesh
from bpy.props import BoolProperty, EnumProperty, IntProperty
from .. utils.registration import get_prefs, get_addon
from .. utils.view import update_local_view
from .. items import focus_method_items, focus_levels_items


class Focus(bpy.types.Operator):
    bl_idname = "machin3.focus"
    bl_label = "MACHIN3: Focus"
    bl_options = {'REGISTER', 'UNDO'}

    method: EnumProperty(name="Method", items=focus_method_items, default='VIEW_SELECTED')

    levels: EnumProperty(name="Levels", items=focus_levels_items, description="Switch between single-level Blender native Local View and multi-level MACHIN3 Focus", default="MULTIPLE")
    unmirror: BoolProperty(name="Un-Mirror", default=True)
    ignore_mirrors: BoolProperty(name="Ignore Mirrors", default=True)

    invert: BoolProperty(name="Inverted Focus", default=False)

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='View Selected' if self.method == 'VIEW_SELECTED' else 'Local View')
        column = box.column()

        if self.method == 'VIEW_SELECTED':
            column.prop(self, "ignore_mirrors", toggle=True)

        elif self.method == 'LOCAL_VIEW':
            row = column.row()
            row.label(text="Levels")
            row.prop(self, "levels", expand=True)

            column.prop(self, "unmirror", toggle=True)

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'VIEW_3D' and context.region.type == 'WINDOW'

    def execute(self, context):
        if self.method == 'VIEW_SELECTED':
            self.view_selected(context)

        elif self.method == 'LOCAL_VIEW':
            self.local_view(context)

        return {'FINISHED'}

    def view_selected(self, context):
        mirrors = []

        nothing_selected = False

        mode = context.mode

        if mode == 'OBJECT':
            sel = context.selected_objects

            if not sel:
                bpy.ops.view3d.view_all('INVOKE_DEFAULT') if get_prefs().focus_view_transition else bpy.ops.view3d.view_all()
                return

            if self.ignore_mirrors:
                mirrors = [mod for obj in sel for mod in obj.modifiers if mod.type == 'MIRROR' and mod.show_viewport]

                for mod in mirrors:
                    mod.show_viewport = False

        elif mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(context.active_object.data)
            bm.normal_update()

            nothing_selected = not [v for v in bm.verts if v.select]

            if nothing_selected:
                for v in bm.verts:
                    v.select_set(True)

                bm.select_flush(True)

        bpy.ops.view3d.view_selected('INVOKE_DEFAULT') if get_prefs().focus_view_transition else bpy.ops.view3d.view_selected()

        for mod in mirrors:
            mod.show_viewport = True

        if nothing_selected:
            if mode == 'OBJECT':
                for obj in context.visible_objects:
                    obj.select_set(False)

            elif mode == 'EDIT_MESH':
                for f in bm.faces:
                    f.select_set(False)

                bm.select_flush(False)

    def local_view(self, context, debug=False):
        def focus(context, view, sel, history, init=False, invert=False, lights=[]):
            vis = context.visible_objects
            hidden = [obj for obj in vis if obj not in sel]

            for obj in lights:
                if obj in hidden:
                    hidden.remove(obj)


            if hidden:
                if init:

                    if lights:
                        for obj in lights:
                            obj.select_set(True)

                    bpy.ops.view3d.localview(frame_selected=False)

                    if lights:
                        for obj in lights:
                            obj.select_set(False)

                else:
                    update_local_view(view, [(obj, False) for obj in hidden])

                epoch = history.add()
                epoch.name = "Epoch %d" % (len(history) - 1)

                for obj in hidden:
                    entry = epoch.objects.add()
                    entry.obj = obj
                    entry.name = obj.name

                if self.unmirror:
                    mirrored = [(obj, mod) for obj in sel for mod in obj.modifiers if mod.type == "MIRROR"]

                    for obj, mod in mirrored:
                        if mod.show_viewport:
                            mod.show_viewport = False

                            entry = epoch.unmirrored.add()
                            entry.obj = obj
                            entry.name = obj.name

                if invert:
                    for obj in sel:
                        obj.select_set(False)

                else:
                    sel[0].select_set(True)

        def unfocus(context, view, history):
            last_epoch = history[-1]

            obj = last_epoch.objects[0].obj

            if len(history) == 1:
                bpy.ops.view3d.localview(frame_selected=False)

            else:
                update_local_view(view, [(entry.obj, True) for entry in last_epoch.objects])

            for entry in last_epoch.unmirrored:
                for mod in entry.obj.modifiers:
                    if mod.type == "MIRROR":
                        mod.show_viewport = True

            idx = history.keys().index(last_epoch.name)
            history.remove(idx)

            obj.select_set(False)

        view = context.space_data

        sel = context.selected_objects
        vis = context.visible_objects

        if self.invert:
            for obj in vis:
                obj.select_set(not obj.select_get())

            sel = context.selected_objects

        lights = [obj for obj in vis if obj.type == 'LIGHT' and obj not in sel] if get_prefs().focus_lights else []


        if self.levels == "SINGLE":
            if self.unmirror:
                if view.local_view:
                    mirrored = [(obj, mod) for obj in vis for mod in obj.modifiers if mod.type == "MIRROR"]

                else:
                    mirrored = [(obj, mod) for obj in sel for mod in obj.modifiers if mod.type == "MIRROR"]

                for obj, mod in mirrored:
                    mod.show_viewport = True if view.local_view else False



            if lights:
                for obj in lights:
                    obj.select_set(True)

            bpy.ops.view3d.localview(frame_selected=False)

            if lights:
                for obj in lights:
                    obj.select_set(False)


        else:
            history = context.scene.M3.focus_history

            if view.local_view:

                if context.selected_objects and not vis == sel:
                    focus(context, view, sel, history, invert=self.invert, lights=lights)

                else:
                    if history:
                        unfocus(context, view, history)

                    else:
                        bpy.ops.view3d.localview(frame_selected=False)

            elif context.selected_objects:

                if history:
                    history.clear()

                focus(context, view, sel, history, init=True, invert=self.invert, lights=lights)

            if debug:
                for epoch in history:
                    print(epoch.name, ", hidden: ", [obj.name for obj in epoch.objects], ", unmirrored: ", [obj.name for obj in epoch.unmirrored])
