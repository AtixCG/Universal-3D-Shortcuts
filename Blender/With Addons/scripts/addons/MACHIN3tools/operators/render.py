import bpy
from bpy.props import BoolProperty
from .. utils.registration import get_prefs
from .. utils.system import makedir, printd
from .. utils.math import dynamic_format
import os
import datetime
import time
import platform


class Render(bpy.types.Operator):
    bl_idname = "machin3.render"
    bl_label = "MACHIN3: Render"
    bl_options = {'REGISTER', 'UNDO'}

    quarter_qual: BoolProperty(name="Quarter Quality", default=False)
    half_qual: BoolProperty(name="Half Quality", default=False)
    double_qual: BoolProperty(name="Double Quality", default=False)
    quad_qual: BoolProperty(name="Quadruple Quality", default=False)

    seed: BoolProperty(name="Seed Render", default=False)
    final: BoolProperty(name="Final Render", default=False)

    def draw(self, context):
        layout = self.layout
        column = layout.column()

    @classmethod
    def description(cls, context, properties):
        currentblend = bpy.data.filepath
        currentfolder = os.path.dirname(currentblend)
        outpath = makedir(os.path.join(currentfolder, get_prefs().render_folder_name))

        if properties.seed:
            desc = f"Render {get_prefs().render_seed_count} seeds, combine all, and save to {outpath + os.sep}"
        else:
            desc = f"Render and save to {outpath + os.sep}"

        if properties.final:
            desc += "\nAdditionally force EXR, render Cryptomatte, and set up the Compositor"

        desc += f"\n\nALT: Half Quality\nSHIFT: Double Quality\nALT + CTRL: Quarter Quality\nSHIFT + CTRL: Quadruple Quality"

        return desc

    @classmethod
    def poll(cls, context):
        return context.scene.camera

    def invoke(self, context, event):
        self.half_qual = event.alt
        self.double_qual = event.shift
        self.quarter_qual = event.alt and event.ctrl
        self.quad_qual = event.shift and event.ctrl

        self.settings = {'scene': context.scene,
                         'render': context.scene.render,
                         'cycles': context.scene.cycles,
                         'view_layer': context.view_layer,

                         'resolution': (context.scene.render.resolution_x, context.scene.render.resolution_y),
                         'samples': context.scene.cycles.samples,
                         'threshold': context.scene.cycles.adaptive_threshold,
                         'format': context.scene.render.image_settings.file_format,
                         'depth': context.scene.render.image_settings.color_depth,
                         'seed': context.scene.cycles.seed,
                         'seed_count': get_prefs().render_seed_count,

                         'tree': None,
                         'use_nodes': context.scene.use_nodes,
                         'use_compositing': context.scene.render.use_compositing,

                         'outpath': None,
                         'blendname': None,
                         'ext': None,
                         }

        self.strings = {'quality': ' (Quarter Quality)' if self.quarter_qual else ' (Half Quality)' if self.half_qual else ' (Double Quality)' if self.double_qual else ' (Quadruple Quality)' if self.quad_qual else '',

                        'resolution_terminal': None,
                        'samples_terminal': None,
                        'threshold_terminal': None,

                        'resolution_file': None,
                        'samples_file': None,
                        'threshold_file': None,
                        }

        return self.execute(context)

    def execute(self, context):

        starttime = time.time()

        self.set_render_settings()

        self.get_output_path()

        self.get_strings()

        self.prepare_rendering()

        if self.seed:

            self.clear_out_compositor()

            seedpaths, matte_path = self.seed_render()

            images = self.load_seed_renderings(seedpaths)

            basename = self.get_save_path(suffix='seed')
            self.setup_compositor_for_firefly_removal(images, basename)

            bpy.ops.render.render(animation=False, write_still=False, use_viewport=False, layer='', scene='')

            save_path = self.rename_file_output(basename)

            if not get_prefs().render_keep_seed_renderings:
                for _, path in seedpaths:
                    os.remove(path)

                if not self.final:
                    self.clear_out_compositor()

        else:

            if self.final:

                basename = self.get_save_path(suffix='clownmatte' if get_prefs().render_use_clownmatte_naming else 'cryptomatte')
                self.setup_compositor_for_cryptomatte_export(basename)

            bpy.ops.render.render(animation=False, write_still=False, use_viewport=False, layer='', scene='')

            save_path = self.get_save_path()

            if self.final:
                matte_path = self.rename_file_output(basename)

            img = bpy.data.images.get('Render Result')
            img.save_render(filepath=save_path)

        rendertime = datetime.timedelta(seconds=int(time.time() - starttime))
        print(f"\nRendering finished after {rendertime}")
        print(f"          saved to {save_path}")

        self.reset_render_settings()

        if self.final:
            self.setup_compositor_for_final_composing(save_path, matte_path)

        return {'FINISHED'}



    def set_render_settings(self):

        render = self.settings['render']
        cycles = self.settings['cycles']

        if self.quarter_qual:
            render.resolution_x = round(render.resolution_x / 4)
            render.resolution_y = round(render.resolution_y / 4)

            if render.engine == 'CYCLES':
                cycles.samples = round(cycles.samples / 4)

                if cycles.use_adaptive_sampling:
                    cycles.adaptive_threshold = cycles.adaptive_threshold * 4

        elif self.half_qual:
            render.resolution_x = round(render.resolution_x / 2)
            render.resolution_y = round(render.resolution_y / 2)

            if render.engine == 'CYCLES':
                cycles.samples = round(cycles.samples / 2)

                if cycles.use_adaptive_sampling:
                    cycles.adaptive_threshold = cycles.adaptive_threshold * 2

        elif self.double_qual:
            render.resolution_x *= 2
            render.resolution_y *= 2

        elif self.quad_qual:
            render.resolution_x *= 4
            render.resolution_y *= 4

        if self.final:
            render.image_settings.file_format = 'OPEN_EXR'

    def get_output_path(self):

        currentblend = bpy.data.filepath
        currentfolder = os.path.dirname(currentblend)

        render = self.settings['render']
        fileformat = render.image_settings.file_format

        if fileformat == 'TIFF':
            ext = 'tif'
        elif fileformat in ['TARGA', 'TARGA_RAW']:
            ext = 'tga'
        elif fileformat in ['OPEN_EXR', 'OPEN_EXR_MULTILAYER']:
            ext = 'exr'
        elif fileformat == 'JPEG':
            ext = 'jpg'
        elif fileformat == 'JPEG2000':
            ext = 'jp2' if render.image_settings.jpeg2k_codec == 'JP2' else 'j2c'
        else:
            ext = fileformat.lower()

        self.settings['outpath'] = makedir(os.path.join(currentfolder, get_prefs().render_folder_name))
        self.settings['blendname'] = os.path.basename(currentblend).split('.')[0]
        self.settings['ext'] = ext

    def get_strings(self):

        render = self.settings['render']
        cycles = self.settings['cycles']

        resolution = self.settings['resolution']
        samples = self.settings['samples']
        threshold = self.settings['threshold']

        if any([self.quarter_qual, self.half_qual, self.double_qual, self.quad_qual]):
            self.strings['resolution_terminal'] = f"{render.resolution_x}x{render.resolution_y} ({resolution[0]}x{resolution[1]})"
            self.strings['samples_terminal'] = f"{cycles.samples} ({samples})"
            self.strings['threshold_terminal'] = f" and a noise threshold of {dynamic_format(cycles.adaptive_threshold)} ({dynamic_format(threshold)})" if cycles.use_adaptive_sampling else ''

        else:
            self.strings['resolution_terminal'] = f"{render.resolution_x}x{render.resolution_y}"
            self.strings['samples_terminal'] = str(cycles.samples)
            self.strings['threshold_terminal'] = f" and a noise threshold of {dynamic_format(cycles.adaptive_threshold)}" if cycles.use_adaptive_sampling else ''

        self.strings['resolution_file'] = f"{render.resolution_x}x{render.resolution_y}"
        self.strings['samples_file'] = str(cycles.samples)
        self.strings['threshold_file'] = dynamic_format(cycles.adaptive_threshold)

    def prepare_rendering(self):

        self.settings['render'].use_compositing = False

        prefix = "\n"

        if self.final:
            prefix += 'Final'

            if self.seed:
                prefix += ' Seed'
        else:
            if self.seed:
                prefix += 'Seed'
            else:
                prefix += 'Quick'

        quality = self.strings['quality']
        resolution = self.strings['resolution_terminal']
        samples = self.strings['samples_terminal']
        threshold = self.strings['threshold_terminal']

        ext = self.settings['ext']

        if self.seed:
            count = self.settings['seed_count']

            print(f"{prefix} Rendering{quality} {count} times at {resolution} with {samples} samples{threshold} to .{ext}")

        else:
            print(f"{prefix} Rendering{quality} at {resolution} with {samples} samples{threshold} to .{ext}")

        bpy.ops.render.view_show('INVOKE_DEFAULT')

    def clear_out_compositor(self):

        scene = self.settings['scene']

        scene.use_nodes = True
        tree = scene.node_tree

        for node in tree.nodes:

            if node.type == 'IMAGE' and node.image:
                if "Render Seed " in node.image.name or node.image.name in ['Render', 'Seed Render']:
                    bpy.data.images.remove(node.image)

            elif node.type == 'CRYPTOMATTE_V2':
                if node.image.name in ['Clownmatte', 'Cryptomatte']:
                    bpy.data.images.remove(node.image)

            tree.nodes.remove(node)

        self.settings['tree'] = tree

    def get_save_path(self, seed=None, suffix=None):

        cycles = self.settings['cycles']

        outpath = self.settings['outpath']
        blendname = self.settings['blendname']
        ext = self.settings['ext']

        resolution = self.strings['resolution_file']
        samples = self.strings['samples_file']
        threshold = self.strings['threshold_file']


        now = 'DATETIME' if suffix else datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        if platform.system() == "Windows":
            now = now.replace(':', '-')

        basename = f"{blendname}_{now}_{resolution}_{samples}"

        if cycles.use_adaptive_sampling:
            basename += f"_{threshold}"

        if seed is not None:
            basename += f"_seed_{seed}"

        if suffix:
            basename += "_" + suffix
            return basename

        return os.path.join(outpath, f"{basename}.{ext}")

    def reset_render_settings(self):

        scene = self.settings['scene']
        render = self.settings['render']
        cycles = self.settings['cycles']

        if any([self.quarter_qual, self.half_qual, self.double_qual, self.quad_qual]):
            render.resolution_x = self.settings['resolution'][0]
            render.resolution_y = self.settings['resolution'][1]

            cycles.samples = self.settings['samples']

            if cycles.use_adaptive_sampling:
                cycles.adaptive_threshold = self.settings['threshold']

        render.image_settings.file_format = self.settings['format']
        render.image_settings.color_depth = self.settings['depth']

        if self.seed:
            cycles.seed = self.settings['seed']

        scene.use_nodes = self.settings['use_nodes']
        render.use_compositing = self.settings['use_compositing']

        if get_prefs().render_keep_seed_renderings and self.seed and not self.final and not scene.use_nodes:
            scene.use_nodes = True

    def rename_file_output(self, basename):

        scene = self.settings['scene']

        outpath = self.settings['outpath']
        ext = self.settings['ext']

        comp_path = os.path.join(outpath, f"{basename}{str(scene.frame_current).zfill(4)}.{ext}")

        time.sleep(1)
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        if platform.system() == "Windows":
            now = now.replace(':', '-')

        basename = basename.replace('DATETIME', now)

        save_path = os.path.join(outpath, f"{basename}.{ext}")
        os.rename(comp_path, save_path)

        return save_path



    def seed_render(self):

        count = self.settings['seed_count']
        cycles = self.settings['cycles']

        matte_path = None

        seedpaths = []

        for i in range(count):
            cycles.seed = i

            if i == count - 1 and self.final:
                basename = self.get_save_path(suffix='clownmatte' if get_prefs().render_use_clownmatte_naming else 'cryptomatte')
                self.setup_compositor_for_cryptomatte_export(basename)

            print(" Seed:", cycles.seed)
            bpy.ops.render.render(animation=False, write_still=False, use_viewport=False, layer='', scene='')

            save_path = self.get_save_path(seed=i)

            if i == count - 1 and self.final:
                matte_path = self.rename_file_output(basename)

                self.clear_out_compositor()

            img = bpy.data.images.get('Render Result')
            img.save_render(filepath=save_path)
            seedpaths.append((i, save_path))

            img.name = f"Render Seed {i} ({i + 1}/{count})"
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            img.name = f"Render Result"

        return seedpaths, matte_path

    def load_seed_renderings(self, seedpaths):

        count = self.settings['seed_count']

        images = []

        for idx, (seed, path) in enumerate(seedpaths):
            loadimg = bpy.data.images.load(filepath=path)
            loadimg.name = f"Render Seed {seed} ({idx + 1}/{count})"

            images.append(loadimg)

        return images

    def setup_compositor_for_firefly_removal(self, images, basename):

        count = self.settings['seed_count']
        scene = self.settings['scene']
        render = self.settings['render']
        tree = self.settings['tree']
        outpath = self.settings['outpath']

        print(f"\nCompositing {count} Renders")

        scene.render.use_compositing = True

        imgnodes = []
        mixnodes = []

        for idx, img in enumerate(images):
            imgnode = tree.nodes.new('CompositorNodeImage')
            imgnode.image = img
            imgnodes.append(imgnode)

            imgnode.location.x = idx * 200

            if idx < count - 1:
                mixnode = tree.nodes.new('CompositorNodeMixRGB')
                mixnode.blend_type = 'DARKEN'
                mixnodes.append(mixnode)

                mixnode.location.x = 400 + idx * 200
                mixnode.location.y = 300

            if idx == 0:
                tree.links.new(imgnode.outputs[0], mixnode.inputs[1])
            else:
                tree.links.new(imgnode.outputs[0], mixnodes[idx - 1].inputs[2])

                if idx < count - 1:
                    tree.links.new(mixnodes[idx - 1].outputs[0], mixnodes[idx].inputs[1])

            if idx == count - 1:
                compnode = tree.nodes.new('CompositorNodeComposite')

                compnode.location.x = imgnode.location.x + 500
                compnode.location.y = 150

                viewnode = tree.nodes.new('CompositorNodeViewer')
                viewnode.location.x = imgnode.location.x + 500
                viewnode.location.y = 300

                tree.links.new(mixnodes[-1].outputs[0], compnode.inputs[0])
                tree.links.new(mixnodes[-1].outputs[0], viewnode.inputs[0])


        outputnode = tree.nodes.new('CompositorNodeOutputFile')
        outputnode.location.x = compnode.location.x

        tree.links.new(mixnodes[-1].outputs[0], outputnode.inputs[0])

        if render.image_settings.file_format == 'OPEN_EXR_MULTILAYER':
            outputnode.base_path = os.path.join(outpath, basename)
        else:
            outputnode.base_path = outpath

        output = outputnode.file_slots[0]
        output.path = basename
        output.save_as_render = False



    def setup_compositor_for_cryptomatte_export(self, basename):

        scene = self.settings['scene']
        view_layer = self.settings['view_layer']
        outpath = self.settings['outpath']

        self.clear_out_compositor()

        tree = self.settings['tree']

        scene.render.use_compositing = True

        view_layer.use_pass_cryptomatte_object = True
        view_layer.use_pass_cryptomatte_material = True
        view_layer.use_pass_cryptomatte_asset = True

        rndrnode = tree.nodes.new('CompositorNodeRLayers')

        compnode = tree.nodes.new('CompositorNodeComposite')
        compnode.location.x = 400

        tree.links.new(rndrnode.outputs[0], compnode.inputs[0])

        outputnode = tree.nodes.new('CompositorNodeOutputFile')
        outputnode.format.file_format = 'OPEN_EXR_MULTILAYER'

        Imageslot = outputnode.inputs.get('Image')
        outputnode.layer_slots.remove(Imageslot)

        for name in ['CryptoObject00', 'CryptoObject01', 'CryptoObject02', 'CryptoMaterial00', 'CryptoMaterial01', 'CryptoMaterial02', 'CryptoAsset00', 'CryptoAsset01', 'CryptoAsset02']:
            inputname = name.replace('Crypto', 'Clown') if get_prefs().render_use_clownmatte_naming else name

            outputnode.layer_slots.new(inputname)
            tree.links.new(rndrnode.outputs[name], outputnode.inputs[inputname])

        outputnode.location.x = 400
        outputnode.location.y = -200

        outputnode.base_path = os.path.join(outpath, basename)

    def setup_compositor_for_final_composing(self, img_path, matte_path):

        self.clear_out_compositor()

        render = self.settings['render']
        tree = self.settings['tree']

        render.use_compositing = True

        imgname = 'Seed Render' if self.seed else 'Render'
        mattename = 'Clownmatte' if get_prefs().render_use_clownmatte_naming else 'Cryptomatte'

        img = bpy.data.images.load(img_path)
        img.name = imgname

        matte = bpy.data.images.load(matte_path)
        matte.name = mattename

        imgnode = tree.nodes.new('CompositorNodeImage')
        imgnode.image = img

        imgnode.name = imgname
        imgnode.label = imgname

        mattenode = tree.nodes.new('CompositorNodeCryptomatteV2')
        mattenode.source = 'IMAGE'
        mattenode.image = matte
        mattenode.layer_name = 'ClownObject' if get_prefs().render_use_clownmatte_naming else 'CryptoObject'

        mattenode.name = mattename
        mattenode.label = mattename

        mattenode.location.x = 300
        mattenode.location.y = -150

        tree.links.new(imgnode.outputs[0], mattenode.inputs[0])

        viewernode = tree.nodes.new('CompositorNodeViewer')
        viewernode.location.x = 600

        tree.links.new(imgnode.outputs[0], viewernode.inputs[0])


class DuplicateNodes(bpy.types.Operator):
    bl_idname = "machin3.duplicate_nodes"
    bl_label = "MACHIN3: Duplicate Nodes"
    bl_description = "Duplicate Nodes normaly, except for Cryptomatte V2 nodes, in that case keep the inputs and clear out the matte ids"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'NODE_EDITOR' and context.scene.use_nodes

    def execute(self, context):
        active = context.scene.node_tree.nodes.active

        if active and active.type == 'CRYPTOMATTE_V2':
            bpy.ops.node.duplicate_move_keep_inputs('INVOKE_DEFAULT')
            context.scene.node_tree.nodes.active.matte_id = ''
            return {'FINISHED'}
        return {'PASS_THROUGH'}
