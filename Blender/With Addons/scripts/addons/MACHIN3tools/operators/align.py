import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty
from mathutils import Matrix, Vector, Euler, Quaternion
from math import radians
from .. utils.math import get_loc_matrix, get_rot_matrix, get_sca_matrix, average_locations
from .. utils.object import compensate_children, parent, unparent
from .. utils.draw import draw_mesh_wire, draw_label, update_HUD_location
from .. utils.mesh import get_coords
from .. utils.ui import init_cursor, init_status, finish_status
from .. utils.system import printd
from .. items import obj_align_mode_items
from .. colors import green, blue


class Align(bpy.types.Operator):
    bl_idname = 'machin3.align'
    bl_label = 'MACHIN3: Align'
    bl_options = {'REGISTER', 'UNDO'}

    inbetween: BoolProperty(name="Align in between", default=False)
    is_inbetween: BoolProperty(name="Draw in between", default=True)
    inbetween_flip: BoolProperty(name="Flip", default=False)

    mode: EnumProperty(name='Mode', items=obj_align_mode_items, default='ACTIVE')

    location: BoolProperty(name='Align Location', default=True)
    rotation: BoolProperty(name='Align Rotation', default=True)
    scale: BoolProperty(name='Align Scale', default=False)

    loc_x: BoolProperty(name='X', default=True)
    loc_y: BoolProperty(name='Y', default=True)
    loc_z: BoolProperty(name='Z', default=True)

    rot_x: BoolProperty(name='X', default=True)
    rot_y: BoolProperty(name='Y', default=True)
    rot_z: BoolProperty(name='Z', default=True)

    sca_x: BoolProperty(name='X', default=True)
    sca_y: BoolProperty(name='Y', default=True)
    sca_z: BoolProperty(name='Z', default=True)

    parent_to_bone: BoolProperty(name='Parent to Bone', default=True)
    align_z_to_y: BoolProperty(name='Align Z to Y', default=True)
    roll: BoolProperty(name='Roll', default=False)
    roll_amount: FloatProperty(name='Roll Amount in Degrees', default=90)

    def draw(self, context):
        layout = self.layout

        column = layout.column()

        if not self.inbetween or not self.is_inbetween:
            row = column.split(factor=0.3)
            row.label(text='Align to', icon='BONE_DATA' if self.mode == 'ACTIVE' and context.active_bone else 'BLANK1')
            r = row.row()
            r.prop(self, 'mode', expand=True)

            if self.mode == 'ACTIVE' and context.active_bone:
                row = column.split(factor=0.3)
                row.label(text='Parent to Bone')
                row.prop(self, 'parent_to_bone', text='True' if self.parent_to_bone else 'False', toggle=True)

                row = column.split(factor=0.3)
                row.label(text='Align Z to Y')
                row.prop(self, 'align_z_to_y', text='True' if self.align_z_to_y else 'False', toggle=True)

                row = column.split(factor=0.3)
                row.prop(self, 'roll', text='Roll')

                r = row.row(align=True)
                r.active = self.roll
                r.prop(self, 'roll_amount', text='')

            else:
                if self.mode in ['ORIGIN', 'CURSOR', 'ACTIVE']:
                    row = column.split(factor=0.3)
                    row.prop(self, 'location', text='Location')

                    r = row.row(align=True)
                    r.active = self.location
                    r.prop(self, 'loc_x', toggle=True)
                    r.prop(self, 'loc_y', toggle=True)
                    r.prop(self, 'loc_z', toggle=True)

                if self.mode in ['CURSOR', 'ACTIVE']:
                    row = column.split(factor=0.3)
                    row.prop(self, 'rotation', text='Rotation')

                    r = row.row(align=True)
                    r.active = self.rotation
                    r.prop(self, 'rot_x', toggle=True)
                    r.prop(self, 'rot_y', toggle=True)
                    r.prop(self, 'rot_z', toggle=True)

                if self.mode == 'ACTIVE':
                    row = column.split(factor=0.3)
                    row.prop(self, 'scale', text='Scale')

                    r = row.row(align=True)
                    r.active = self.scale
                    r.prop(self, 'sca_x', toggle=True)
                    r.prop(self, 'sca_y', toggle=True)
                    r.prop(self, 'sca_z', toggle=True)


        if self.is_inbetween:
            row = column.split(factor=0.3)
            row.label(text='Align in between')
            r = row.row(align=True)
            r.prop(self, 'inbetween', toggle=True)

            if self.inbetween:
                r.prop(self, 'inbetween_flip', toggle=True)


    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.mode in ['OBJECT', 'POSE']

    def execute(self, context):
        active = context.active_object
        sel = context.selected_objects

        self.is_inbetween = len(sel) == 3 and active and active in sel

        if self.is_inbetween and self.inbetween:
            self.align_in_between(context, active, [obj for obj in context.selected_objects if obj != active])
            return {'FINISHED'}

        if self.mode in ['ORIGIN', 'CURSOR', 'FLOOR']:

            if active and active.M3.is_group_empty and active.children:
                sel = [active]

        elif self.mode in 'ACTIVE':
            all_empties = [obj for obj in sel if obj.M3.is_group_empty and obj != active]
            top_level = [obj for obj in all_empties if obj.parent not in all_empties]

            if top_level:
                sel = top_level

        if self.mode == 'ORIGIN':
            self.align_to_origin(context, sel)

        elif self.mode == 'CURSOR':
            self.align_to_cursor(context, sel)

        elif self.mode == 'ACTIVE':
            if context.active_bone:
                self.align_to_active_bone(active, context.active_bone.name, [obj for obj in sel if obj != active])

            else:
                self.align_to_active_object(context, active, [obj for obj in sel if obj != active])

        elif self.mode == 'FLOOR':
            context.evaluated_depsgraph_get()
            self.drop_to_floor(context, sel)

        return {'FINISHED'}

    def align_to_origin(self, context, sel):
        for obj in sel:
            omx = obj.matrix_world
            oloc, orot, osca = omx.decompose()

            olocx, olocy, olocz = oloc
            orotx, oroty, orotz = orot.to_euler('XYZ')
            oscax, oscay, oscaz = osca


            if self.location:
                locx = 0 if self.loc_x else olocx
                locy = 0 if self.loc_y else olocy
                locz = 0 if self.loc_z else olocz

                loc = get_loc_matrix(Vector((locx, locy, locz)))

            else:
                loc = get_loc_matrix(oloc)



            rot = orot.to_matrix().to_4x4()



            sca = get_sca_matrix(osca)

            if obj.children and context.scene.tool_settings.use_transform_skip_children:
                compensate_children(obj, omx, loc @ rot @ sca)

            obj.matrix_world = loc @ rot @ sca

    def align_to_cursor(self, context, sel):
        cursor = context.scene.cursor
        cursor.rotation_mode = 'XYZ'

        for obj in sel:
            omx = obj.matrix_world
            oloc, orot, osca = omx.decompose()

            olocx, olocy, olocz = oloc
            orotx, oroty, orotz = orot.to_euler('XYZ')
            oscax, oscay, oscaz = osca


            if self.location:
                locx = cursor.location.x if self.loc_x else olocx
                locy = cursor.location.y if self.loc_y else olocy
                locz = cursor.location.z if self.loc_z else olocz

                loc = get_loc_matrix(Vector((locx, locy, locz)))

            else:
                loc = get_loc_matrix(oloc)



            if self.rotation:
                rotx = cursor.rotation_euler.x if self.rot_x else orotx
                roty = cursor.rotation_euler.y if self.rot_y else oroty
                rotz = cursor.rotation_euler.z if self.rot_z else orotz

                rot = get_rot_matrix(Euler((rotx, roty, rotz), 'XYZ'))

            else:
                rot = get_rot_matrix(orot)



            sca = get_sca_matrix(osca)

            if obj.children and context.scene.tool_settings.use_transform_skip_children:
                compensate_children(obj, omx, loc @ rot @ sca)

            obj.matrix_world = loc @ rot @ sca

    def align_to_active_object(self, context, active, sel):
        amx = active.matrix_world
        aloc, arot, asca = amx.decompose()

        alocx, alocy, alocz = aloc
        arotx, aroty, arotz = arot.to_euler('XYZ')
        ascax, ascay, ascaz = asca

        for obj in sel:
            omx = obj.matrix_world
            oloc, orot, osca = omx.decompose()

            olocx, olocy, olocz = oloc
            orotx, oroty, orotz = orot.to_euler('XYZ')
            oscax, oscay, oscaz = osca


            if self.location:
                locx = alocx if self.loc_x else olocx
                locy = alocy if self.loc_y else olocy
                locz = alocz if self.loc_z else olocz

                loc = get_loc_matrix(Vector((locx, locy, locz)))

            else:
                loc = get_loc_matrix(oloc)



            if self.rotation:
                rotx = arotx if self.rot_x else orotx
                roty = aroty if self.rot_y else oroty
                rotz = arotz if self.rot_z else orotz

                rot = get_rot_matrix(Euler((rotx, roty, rotz), 'XYZ'))

            else:
                rot = get_rot_matrix(orot)



            if self.scale:
                scax = ascax if self.sca_x else oscax
                scay = ascay if self.sca_y else oscay
                scaz = ascaz if self.sca_z else oscaz

                sca = get_sca_matrix(Vector((scax, scay, scaz)))

            else:
                sca = get_sca_matrix(osca)

            if obj.children and context.scene.tool_settings.use_transform_skip_children:
                compensate_children(obj, omx, loc @ rot @ sca)

            obj.matrix_world = loc @ rot @ sca

    def align_to_active_bone(self, armature, bonename, sel):
        bone = armature.pose.bones[bonename]

        for obj in sel:
            if self.parent_to_bone:
                obj.parent = armature
                obj.parent_type = 'BONE'
                obj.parent_bone = bonename

            if self.align_z_to_y:
                obj.matrix_world = armature.matrix_world @ bone.matrix @ Matrix.Rotation(radians(-90), 4, 'X') @ Matrix.Rotation(radians(self.roll_amount if self.roll else 0), 4, 'Z')
            else:
                obj.matrix_world = armature.matrix_world @ bone.matrix @ Matrix.Rotation(radians(self.roll_amount if self.roll else 0), 4, 'Y')

    def drop_to_floor(self, context, selection):
        for obj in selection:
            mx = obj.matrix_world
            oldmx = mx.copy()

            if obj.type == 'MESH':
                minz = min((mx @ v.co)[2] for v in obj.data.vertices)
                mx.translation.z -= minz

            elif obj.type == 'EMPTY':
                mx.translation.z -= obj.location.z

            if obj.children and context.scene.tool_settings.use_transform_skip_children:
                compensate_children(obj, oldmx, mx)


    def align_in_between(self, context, active, sel):

        oldmx = active.matrix_world.copy()

        _, rot, sca = oldmx.decompose()
        locations = [obj.matrix_world.to_translation() for obj in sel]

        active_up = rot @ Vector((0, 0, 1))
        sel_up = locations[0] - locations[1]
        mx = get_loc_matrix(average_locations(locations)) @ get_rot_matrix(active_up.rotation_difference(sel_up) @ rot @ Quaternion((1, 0, 0), radians(180 if self.inbetween_flip else 0))) @ get_sca_matrix(sca)

        active.matrix_world = mx

        if active.children and context.scene.tool_settings.use_transform_skip_children:
            compensate_children(active, oldmx, mx)


def draw_align_relative_status(op):
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)

        row.label(text="Align Relative")

        row.separator(factor=2)
        row.label(text="", icon='EVENT_SPACEKEY')
        row.label(text="Confirm")

        row.label(text="", icon='MOUSE_RMB')
        row.label(text="Cancel")

        row.separator(factor=10)
        row.label(text="", icon='MOUSE_LMB')
        row.label(text="Select Single")

        row.separator(factor=2)
        row.label(text="", icon='EVENT_SHIFT')
        row.label(text="", icon='MOUSE_LMB')
        row.label(text="Select Multiple")

        row.separator(factor=2)
        row.label(text="", icon='MOUSE_MMB')
        row.label(text=f"Instance: {op.instance}")

    return draw


class AlignRelative(bpy.types.Operator):
    bl_idname = "machin3.align_relative"
    bl_label = "MACHIN3: Align Relative"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    instance: BoolProperty(name="Instance", default=False)

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            active = context.active_object
            return active and [obj for obj in context.selected_objects if obj != active]

    def draw_VIEW3D(self):
        for obj in self.targets:
            for batch in self.batches[obj]:
                draw_mesh_wire(batch, color=green if self.instance else blue, alpha=0.5)

    def draw_HUD(self, args):
        context, event = args

        draw_label(context, title='Instance' if self.instance else 'Duplicate', coords=Vector((self.HUD_x, self.HUD_y)), center=False, color=green if self.instance else blue)

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            update_HUD_location(self, event, offsetx=10, offsety=10)

        self.targets = [obj for obj in context.selected_objects if obj not in self.orig_sel]

        for obj in self.targets:
            if obj not in self.batches:
                self.batches[obj] = [get_coords(aligner.data, obj.matrix_world @ self.deltamx[aligner], indices=True) for aligner in self.aligners if aligner.data]

        events = ['MOUSEMOVE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE']

        if event.type in events:

            if event.type == 'MOUSEMOVE':
                self.mousepos = Vector((event.mouse_region_x, event.mouse_region_y))
                update_HUD_location(self, event, offsetx=10, offsety=10)

            elif event.type in ['WHEELUPMOUSE', 'WHEELDOWNMOUSE']:
                self.instance = not self.instance
                context.active_object.select_set(True)



        if event.type == 'LEFTMOUSE':
            return {'PASS_THROUGH'}



        elif event.type == 'MIDDLEMOUSE':
            return {'PASS_THROUGH'}



        if event.type == 'SPACE':
            self.finish()


            for target in self.targets:
                self.target_map[target] = {'dups': [],
                                           'map': {}}

                for aligner in self.aligners:
                    dup = aligner.copy()

                    self.target_map[target]['dups'].append(dup)
                    self.target_map[target]['map'][aligner] = dup

                    if aligner.data:
                        dup.data = aligner.data if self.instance else aligner.data.copy()

                    dup.matrix_world = target.matrix_world @ self.deltamx[aligner]

                    for col in aligner.users_collection:
                        col.objects.link(dup)


            if self.debug:
                printd(self.target_map, name='target map')

            for target, dup_data in self.target_map.items():
                if self.debug:
                    print(target.name)

                for dup in dup_data['dups']:
                    if self.debug:
                        print("", dup.name, " > ", dup_data['map'][dup].name)

                    self.reparent(dup_data, target, dup, debug=self.debug)

                    self.remirror(dup_data, target, dup, debug=self.debug)

                    self.regroup(dup_data, target, dup, debug=self.debug)


            bpy.ops.object.select_all(action='DESELECT')

            for target, dup_data in self.target_map.items():
                for dup in dup_data['dups']:
                    dup.select_set(True)
                    context.view_layer.objects.active = dup

            return {'FINISHED'}

        elif event.type in ['RIGHTMOUSE', 'ESC']:
            self.finish()

            bpy.ops.object.select_all(action='DESELECT')

            for obj in self.orig_sel:
                obj.select_set(True)

                if obj == self.active:
                    context.view_layer.objects.active = obj

            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def finish(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
        bpy.types.SpaceView3D.draw_handler_remove(self.HUD, 'WINDOW')

        finish_status(self)

    def invoke(self, context, event):
        self.debug = True
        self.debug = False

        self.active = context.active_object
        self.aligners = [obj for obj in context.selected_objects if obj != self.active]

        if self.debug:
            print("reference:", self.active.name)
            print(" aligners:", [obj.name for obj in self.aligners])

        self.orig_sel = [self.active] + self.aligners
        self.targets = []
        self.batches = {}
        self.target_map = {}

        self.deltamx = {obj: self.active.matrix_world.inverted_safe() @ obj.matrix_world for obj in self.aligners}

        init_cursor(self, event)

        init_status(self, context, func=draw_align_relative_status(self))
        self.active.select_set(True)


        args = (context, event)
        self.HUD = bpy.types.SpaceView3D.draw_handler_add(self.draw_HUD, (args, ), 'WINDOW', 'POST_PIXEL')
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (), 'WINDOW', 'POST_VIEW')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def reparent(self, dup_data, target, dup, debug=False):

        if dup.parent and dup.parent in self.orig_sel:
            if dup.parent == self.active:
                pobj = target

                if debug:
                    print("  duplicate is parented to reference", dup.parent.name)

            else:
                pobj = dup_data['map'][dup.parent]
                if debug:
                    print("  duplicate is parented to another aligner", dup.parent.name)

            unparent(dup)
            parent(dup, pobj)

    def remirror(self, dup_data, target, dup, debug=False):

        mirrors = [mod for mod in dup.modifiers if mod.type == 'MIRROR' and mod.mirror_object in self.orig_sel]

        for mod in mirrors:
            if mod.mirror_object == self.active:
                mobj = target
                if debug:
                    print("  duplicate is mirrored accross reference", mod.mirror_object.name)

            else:
                mobj = dup_data['map'][mod.mirror_object]
                if debug:
                    print("  duplicate is mirrored accross another aligner", mod.mirror_object.name)

            mod.mirror_object = mobj

    def regroup(self, dup_data, target, dup, debug=False):

        if target.M3.is_group_object and target.parent and target.parent.M3.is_group_empty:
            if (dup.M3.is_group_object and self.active.M3.is_group_object) and (dup.parent and self.active.parent) and (dup.parent.M3.is_group_empty and self.active.parent.M3.is_group_empty) and (dup.parent == self.active.parent):
                if debug:
                    print("  regrouping to", target.name)

                unparent(dup)
                parent(dup, target.parent)
