import bpy
from bpy.props import BoolProperty
import os
import time
from ... utils.registration import get_addon
from ... utils.system import add_path_to_recent_files, get_incremented_paths
from ... utils.ui import popup_message, get_icon
from ... colors import green


class New(bpy.types.Operator):
    bl_idname = "machin3.new"
    bl_label = "Current file is unsaved. Start a new file anyway?"
    bl_description = "Start new .blend file"
    bl_options = {'REGISTER'}

    def execute(self, context):

        bpy.ops.wm.read_homefile(load_ui=True)

        return {'FINISHED'}

    def invoke(self, context, event):
        if bpy.data.is_dirty:
            return context.window_manager.invoke_confirm(self, event)
        else:
            bpy.ops.wm.read_homefile(load_ui=True)
            return {'FINISHED'}



class Save(bpy.types.Operator):
    bl_idname = "machin3.save"
    bl_label = "Save"
    bl_options = {'REGISTER'}

    @classmethod
    def description(cls, context, properties):
        currentblend = bpy.data.filepath

        if currentblend:
            return f"Save {currentblend}"
        return "Save unsaved file as..."

    def execute(self, context):
        currentblend = bpy.data.filepath

        if currentblend:
            bpy.ops.wm.save_mainfile()

            t = time.time()
            localt = time.strftime('%H:%M:%S', time.localtime(t))
            print("%s | Saved blend: %s" % (localt, currentblend))
            self.report({'INFO'}, 'Saved "%s"' % (os.path.basename(currentblend)))

        else:
            bpy.ops.wm.save_mainfile('INVOKE_DEFAULT')

        return {'FINISHED'}


class SaveAs(bpy.types.Operator):
    bl_idname = "machin3.save_as"
    bl_label = "MACHIN3: Save As"
    bl_description = "Save the current file in the desired location\nALT: Save as Copy\nCTRL: Save as Asset"
    bl_options = {'REGISTER', 'UNDO'}

    copy: BoolProperty(name="Save as Copy", default=False)
    asset: BoolProperty(name="Save as Asset", default=False)

    def draw(self, context):
        layout = self.layout
        column = layout.column()

    def invoke(self, context, event):
        self.asset = event.ctrl
        self.copy = event.alt
        return self.execute(context)

    def execute(self, context):
        assets = [obj for obj in bpy.data.objects if obj.asset_data]

        if self.asset and assets:
            print(f"\nINFO: Saving as Asset!")
            print(f"      Found {len(assets)} root Object/Assembly Assets in the current file")

            keep = set()
            self.get_asset_objects_recursively(assets, keep)



            remove = [obj for obj in bpy.data.objects if obj not in keep]


            for obj in remove:
                print(f"WARNING: Removing {obj.name}")
                bpy.data.objects.remove(obj, do_unlink=True)

            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

            bpy.ops.wm.save_as_mainfile('INVOKE_DEFAULT', copy=True)

        elif self.copy:
            print("\nINFO: Saving as Copy")
            bpy.ops.wm.save_as_mainfile('INVOKE_DEFAULT', copy=True)

        else:
            bpy.ops.wm.save_as_mainfile('INVOKE_DEFAULT')

        return {'FINISHED'}

    def get_asset_objects_recursively(self, assets, keep, depth=0):

        for obj in assets:
            keep.add(obj)

            if obj.type == 'EMPTY' and obj.instance_type == 'COLLECTION' and obj.instance_collection:
                self.get_asset_objects_recursively(obj.instance_collection.objects, keep, depth + 1)


class SaveIncremental(bpy.types.Operator):
    bl_idname = "machin3.save_incremental"
    bl_label = "Incremental Save"
    bl_options = {'REGISTER'}

    @classmethod
    def description(cls, context, properties):
        currentblend = bpy.data.filepath

        if currentblend:
            incrpaths = get_incremented_paths(currentblend)

            if incrpaths:
                return f"Save {currentblend} incrementally to {os.path.basename(incrpaths[0])}\nALT: Save to {os.path.basename(incrpaths[1])}"

        return "Save unsaved file as..."

    def invoke(self, context, event):
        currentblend = bpy.data.filepath

        if currentblend:
            incrpaths = get_incremented_paths(currentblend)
            savepath = incrpaths[1] if event.alt else incrpaths[0]

            if os.path.exists(savepath):
                self.report({'ERROR'}, "File '%s' exists already!\nBlend has NOT been saved incrementally!" % (savepath))
                return {'CANCELLED'}

            else:

                add_path_to_recent_files(savepath)

                bpy.ops.wm.save_as_mainfile(filepath=savepath)

                t = time.time()
                localt = time.strftime('%H:%M:%S', time.localtime(t))
                print(f"{localt} | Saved {os.path.basename(currentblend)} incrementally to {savepath}")
                self.report({'INFO'}, f"Incrementally saved to {os.path.basename(savepath)}")

        else:
            bpy.ops.wm.save_mainfile('INVOKE_DEFAULT')

        return {'FINISHED'}


class SaveVersionedStartupFile(bpy.types.Operator):
    bl_idname = "machin3.save_versioned_startup_file"
    bl_label = "Save Versioned Startup File"
    bl_options = {'REGISTER'}

    def execute(self, context):
        config_path = bpy.utils.user_resource('CONFIG')
        startup_path = os.path.join(config_path, 'startup.blend')

        if os.path.exists(startup_path):
            indices = [int(f.replace('startup.blend', '')) for f in os.listdir(bpy.utils.user_resource('CONFIG')) if 'startup.blend' in f and f != 'startup.blend']
            biggest_idx = max(indices) if indices else 0

            os.rename(startup_path, os.path.join(config_path, f'startup.blend{biggest_idx + 1}'))

            bpy.ops.wm.save_homefile()

            self.report({'INFO'}, f'Versioned Startup File saved: {biggest_idx + 1}')

        else:
            bpy.ops.wm.save_homefile()

            self.report({'INFO'}, f'Initial Startup File saved')

        return {'FINISHED'}


class LoadMostRecent(bpy.types.Operator):
    bl_idname = "machin3.load_most_recent"
    bl_label = "Load Most Recent"
    bl_description = "Load most recently used .blend file"
    bl_options = {"REGISTER"}

    def execute(self, context):
        recent_path = bpy.utils.user_resource('CONFIG', path="recent-files.txt")

        try:
            with open(recent_path) as file:
                recent_files = file.read().splitlines()
        except (IOError, OSError, FileNotFoundError):
            recent_files = []

        if recent_files:
            most_recent = recent_files[0]

            if os.path.exists(most_recent):
                bpy.ops.wm.open_mainfile(filepath=most_recent, load_ui=True)
                self.report({'INFO'}, 'Loaded most recent "%s"' % (os.path.basename(most_recent)))

            else:
                popup_message("File %s does not exist" % (most_recent), title="File not found")

        return {'FINISHED'}


class LoadPrevious(bpy.types.Operator):
    bl_idname = "machin3.load_previous"
    bl_label = "Current file is unsaved. Load previous blend in folder anyway?"
    bl_description = "Load Previous Blend File in Current Folder\nALT: Don't load ui"
    bl_options = {'REGISTER'}

    load_ui: BoolProperty()

    @classmethod
    def poll(cls, context):
        return bpy.data.filepath

    def invoke(self, context, event):
        self.load_ui = not event.alt

        if bpy.data.filepath:
            path, _, idx = self.get_data(bpy.data.filepath)

            if idx >= 0:
                if bpy.data.is_dirty:
                    return context.window_manager.invoke_confirm(self, event)

                else:
                    self.execute(context)

            else:
                popup_message("You've reached the first file in the current foler: %s." % (path), title="Info")

        return {'FINISHED'}

    def execute(self, context):
        path, files, idx = self.get_data(bpy.data.filepath)

        loadpath = os.path.join(path, files[idx])

        add_path_to_recent_files(loadpath)

        bpy.ops.wm.open_mainfile(filepath=loadpath, load_ui=self.load_ui)
        self.report({'INFO'}, 'Loaded previous file "%s" (%d/%d)' % (os.path.basename(loadpath), idx + 1, len(files)))

        return {'FINISHED'}

    def get_data(self, filepath):
        currentpath = os.path.dirname(filepath)
        currentblend = os.path.basename(filepath)

        blendfiles = [f for f in sorted(os.listdir(currentpath)) if f.endswith(".blend")]
        index = blendfiles.index(currentblend)
        previousidx = index - 1

        return currentpath, blendfiles, previousidx


class LoadNext(bpy.types.Operator):
    bl_idname = "machin3.load_next"
    bl_label = "Current file is unsaved. Load next blend in folder anyway?"
    bl_description = "Load Next Blend File in Current Folder\nALT: Don't load ui"
    bl_options = {'REGISTER'}

    load_ui: BoolProperty()

    @classmethod
    def poll(cls, context):
        return bpy.data.filepath

    def invoke(self, context, event):
        self.load_ui = not event.alt

        if bpy.data.filepath:
            path, files, idx = self.get_data(bpy.data.filepath)

            if idx < len(files):
                if bpy.data.is_dirty:
                    return context.window_manager.invoke_confirm(self, event)

                else:
                    self.execute(context)
            else:
                popup_message("You've reached the last file in the current foler: %s." % (path), title="Info")

        return {'FINISHED'}

    def execute(self, context):
        path, files, idx = self.get_data(bpy.data.filepath)

        loadpath = os.path.join(path, files[idx])

        add_path_to_recent_files(loadpath)

        bpy.ops.wm.open_mainfile(filepath=loadpath, load_ui=self.load_ui)
        self.report({'INFO'}, 'Loaded next file "%s" (%d/%d)' % (os.path.basename(loadpath), idx + 1, len(files)))

        return {'FINISHED'}

    def get_data(self, filepath):
        currentpath = os.path.dirname(filepath)
        currentblend = os.path.basename(filepath)

        blendfiles = [f for f in sorted(os.listdir(currentpath)) if f.endswith(".blend")]
        index = blendfiles.index(currentblend)
        previousidx = index + 1

        return currentpath, blendfiles, previousidx


decalmachine = None

class Purge(bpy.types.Operator):
    bl_idname = "machin3.purge_orphans"
    bl_label = "MACHIN3: Purge Orphans"
    bl_options = {'REGISTER', 'UNDO'}

    recursive: BoolProperty(name="Recursive Purge", default=False)

    @classmethod
    def description(cls, context, properties):
        return "Purge Orphans\nALT: Purge Orphans Recursively"

    def invoke(self, context, event):
        global decalmachine
        
        if decalmachine is None:
            decalmachine = get_addon('DECALmachine')[0]

        self.recursive = event.alt

        before_meshes_count = len(bpy.data.meshes)
        before_curves_count = len(bpy.data.curves)
        before_objects_count = len(bpy.data.objects)
        before_materials_count = len(bpy.data.materials)
        before_images_count = len(bpy.data.images)
        before_nodegroups_count = len(bpy.data.node_groups)
        before_collections_count = len(bpy.data.collections)
        before_scenes_count = len(bpy.data.scenes)
        before_worlds_count = len(bpy.data.worlds)

        if decalmachine:
            bpy.ops.machin3.remove_decal_orphans()

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=self.recursive)

        after_meshes_count = len(bpy.data.meshes)
        after_curves_count = len(bpy.data.curves)
        after_objects_count = len(bpy.data.objects)
        after_materials_count = len(bpy.data.materials)
        after_images_count = len(bpy.data.images)
        after_nodegroups_count = len(bpy.data.node_groups)
        after_collections_count = len(bpy.data.collections)
        after_scenes_count = len(bpy.data.scenes)
        after_worlds_count = len(bpy.data.worlds)

        meshes_count = before_meshes_count - after_meshes_count
        curves_count = before_curves_count - after_curves_count
        objects_count = before_objects_count - after_objects_count
        materials_count = before_materials_count - after_materials_count
        images_count = before_images_count - after_images_count
        nodegroups_count = before_nodegroups_count - after_nodegroups_count
        collections_count = before_collections_count - after_collections_count
        scenes_count = before_scenes_count - after_scenes_count
        worlds_count = before_worlds_count - after_worlds_count


        if any([meshes_count, curves_count, objects_count, materials_count, images_count, nodegroups_count, collections_count, scenes_count, worlds_count]):
            total_count = meshes_count + curves_count + objects_count + materials_count + images_count + nodegroups_count + collections_count + scenes_count + worlds_count

            msg = [f"Removed {total_count} data blocks!"]

            if meshes_count:
                msg.append(f" • {meshes_count} meshes")

            if curves_count:
                msg.append(f" • {curves_count} curves")

            if objects_count:
                msg.append(f" • {objects_count} objects")

            if materials_count:
                msg.append(f" • {materials_count} materials")

            if images_count:
                msg.append(f" • {images_count} images")

            if nodegroups_count:
                msg.append(f" • {nodegroups_count} node groups")

            if scenes_count:
                msg.append(f" • {scenes_count} scenes")

            if worlds_count:
                msg.append(f" • {worlds_count} worlds")

            popup_message(msg, title="Recursive Purge" if event.alt else "Purge")

        else:
            bpy.ops.machin3.draw_label(text="Nothing to purge.", coords=(context.region.width / 2, 200), color=green)

        return {'FINISHED'}


class Clean(bpy.types.Operator):
    bl_idname = "machin3.clean_out_blend_file"
    bl_label = "Clean out entire .blend file!"
    bl_description = "Clean out entire .blend file"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.data.objects or bpy.data.materials or bpy.data.images

    def draw(self, context):
        layout = self.layout

        column = layout.column()
        column.label(text='This will remove everything in the current .blend file!', icon_value=get_icon('error'))

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

        for mat in bpy.data.materials:
            bpy.data.materials.remove(mat, do_unlink=True)

        for img in bpy.data.images:
            bpy.data.images.remove(img, do_unlink=True)

        for col in bpy.data.collections:
            bpy.data.collections.remove(col, do_unlink=True)

        for i in range(5):
            bpy.ops.outliner.orphans_purge()

        if context.space_data.local_view:
            bpy.ops.view3d.localview(frame_selected=False)

        return {'FINISHED'}


class ReloadLinkedLibraries(bpy.types.Operator):
    bl_idname = "machin3.reload_linked_libraries"
    bl_label = "MACHIN3: Reload Linked Liraries"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.data.libraries

    def execute(self, context):
        reloaded = []

        for lib in bpy.data.libraries:
            lib.reload()
            reloaded.append(lib.name)
            print(f"Reloaded Library: {lib.name}")

        self.report({'INFO'}, f"Reloaded {'Library' if len(reloaded) == 1 else f'{len(reloaded)} Libraries'}: {', '.join(reloaded)}")

        return {'FINISHED'}


class ScreenCast(bpy.types.Operator):
    bl_idname = "machin3.screen_cast"
    bl_label = "MACHIN3: Screen Cast"
    bl_description = "Screen Cast Operators"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        screencast_keys = get_addon('Screencast Keys')[0]

        if screencast_keys:
            return "Screen Cast recent Operators and Keys"
        return "Screen Cast Recent Operators"

    def execute(self, context):

        wm = context.window_manager
        setattr(wm, 'M3_screen_cast', not getattr(wm, 'M3_screen_cast', False))

        screencast_keys = get_addon('Screencast Keys')[0]

        if screencast_keys:


            current = context.workspace
            other = [ws for ws in bpy.data.workspaces if ws != current]

            if other:
                context.window.workspace = other[0]
                context.window.workspace = current

            bpy.ops.wm.sk_screencast_keys('INVOKE_DEFAULT')

        if context.visible_objects:
            context.visible_objects[0].select_set(context.visible_objects[0].select_get())

        return {'FINISHED'}
