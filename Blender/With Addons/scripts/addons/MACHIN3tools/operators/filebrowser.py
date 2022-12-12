import bpy
from bpy.props import StringProperty, BoolProperty
import os
from .. utils.system import abspath, open_folder
from .. utils.property import step_list


class Open(bpy.types.Operator):
    bl_idname = "machin3.filebrowser_open"
    bl_label = "MACHIN3: Open in System's filebrowser"
    bl_description = "Open the current location in the System's own filebrowser\nALT: Open .blend file"

    path: StringProperty(name="Path")
    blend_file: BoolProperty(name="Open .blend file")

    @classmethod
    def poll(cls, context):
        return context.area.type == 'FILE_BROWSER'

    def execute(self, context):
        params = context.space_data.params
        directory = abspath(params.directory.decode())

        if self.blend_file:
            active_file = context.active_file

            if active_file.asset_data:
                bpy.ops.asset.open_containing_blend_file()

            else:
                path = os.path.join(directory, active_file.relative_path)
                bpy.ops.machin3.open_library_blend(blendpath=path)

        else:
            open_folder(directory)

        return {'FINISHED'}


class Toggle(bpy.types.Operator):
    bl_idname = "machin3.filebrowser_toggle"
    bl_label = "MACHIN3: Toggle Filebrowser"
    bl_description = ""

    type: StringProperty()

    @classmethod
    def poll(cls, context):
        return context.area.type == 'FILE_BROWSER'

    def execute(self, context):
        if self.type == 'DISPLAY_TYPE':
            if context.area.ui_type == 'FILES':
                if context.space_data.params.display_type == 'LIST_VERTICAL':
                    context.space_data.params.display_type = 'THUMBNAIL'

                else:
                    context.space_data.params.display_type = 'LIST_VERTICAL'

            elif context.area.ui_type == 'ASSETS':
                if context.space_data.params.asset_library_ref == 'Library':
                    context.space_data.params.asset_library_ref = 'LOCAL'
                elif context.space_data.params.asset_library_ref == 'LOCAL':
                    context.space_data.params.asset_library_ref = 'Library'

        elif self.type == 'SORT':
            if context.area.ui_type == 'FILES':
                if context.space_data.params.sort_method == 'FILE_SORT_ALPHA':
                    context.space_data.params.sort_method = 'FILE_SORT_TIME'

                else:
                    context.space_data.params.sort_method = 'FILE_SORT_ALPHA'

            elif context.area.ui_type == 'ASSETS':
                import_types = ['LINK', 'APPEND', 'APPEND_REUSE']

                bpy.context.space_data.params.import_type = step_list(context.space_data.params.import_type, import_types, 1)

        elif self.type == 'HIDDEN':
            if context.area.ui_type == 'FILES':
                context.space_data.params.show_hidden = not context.space_data.params.show_hidden

        return {'FINISHED'}


class CycleThumbs(bpy.types.Operator):
    bl_idname = "machin3.filebrowser_cycle_thumbnail_size"
    bl_label = "MACHIN3: Cycle Thumbnail Size"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    reverse: BoolProperty(name="Reverse Cycle Diretion")

    @classmethod
    def poll(cls, context):
        return context.area.type == 'FILE_BROWSER' and context.space_data.params.display_type == 'THUMBNAIL'

    def execute(self, context):
        sizes = ['TINY', 'SMALL', 'NORMAL', 'LARGE']
        size = bpy.context.space_data.params.display_size
        bpy.context.space_data.params.display_size = step_list(size, sizes, -1 if self.reverse else 1, loop=True)

        return {'FINISHED'}
