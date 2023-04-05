from struct import pack

import bpy
import gpu
import numpy as np
from bgl import glEnable, glDisable, GL_BLEND
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from ..functions.mesh_intersect import select_mesh_elems
from ..functions.mesh_modal import *


FILL_VERTEX_SHADER = '''
    in vec2 pos;

    uniform mat4 u_ViewProjectionMatrix;
    uniform float u_X;
    uniform float u_Y;

    void main()
    {
        gl_Position = u_ViewProjectionMatrix * vec4(pos.x + u_X, pos.y + u_Y, 0.0f, 1.0f);
    }
'''
FILL_FRAGMENT_SHADER = '''
    out vec4 fragColor;

    uniform vec4 u_FillColor;

    void main()
    {
        fragColor = u_FillColor;
    }
'''
BORDER_VERTEX_SHADER = '''
    in vec2 pos;
    in float len;
    out float v_Len;

    uniform mat4 u_ViewProjectionMatrix;
    uniform float u_X;
    uniform float u_Y;

    void main()
    {
        v_Len = len;
        gl_Position = u_ViewProjectionMatrix * vec4(pos.x + u_X, pos.y + u_Y, 0.0f, 1.0f);
    }
'''
BORDER_FRAGMENT_SHADER = '''
    in float v_Len;
    out vec4 fragColor;

    uniform vec4 u_SegmentColor;
    uniform vec4 u_GapColor;

    float dash_size = 2;
    float gap_size = 2;
    vec4 col = u_SegmentColor;

    void main()
    {
        if (fract(v_Len/(dash_size + gap_size)) > dash_size/(dash_size + gap_size)) 
            col = u_GapColor;

        fragColor = col;
    }
'''
fill_shader = gpu.types.GPUShader(FILL_VERTEX_SHADER, FILL_FRAGMENT_SHADER)  # noqa
border_shader = gpu.types.GPUShader(BORDER_VERTEX_SHADER, BORDER_FRAGMENT_SHADER)  # noqa


# noinspection PyTypeChecker
class MESH_OT_select_circle_xray(bpy.types.Operator):
    """Select items using circle selection with x-ray"""
    bl_idname = "mesh.select_circle_xray"
    bl_label = "Circle Select X-Ray"
    bl_options = {'REGISTER', 'GRAB_CURSOR'}

    mode: bpy.props.EnumProperty(
        name="Mode",
        description="Default selection mode",
        items=[
            ('SET', "Set", "Set a new selection", 'SELECT_SET', 1),
            ('ADD', "Extend", "Extend existing selection", 'SELECT_EXTEND', 2),
            ('SUB', "Subtract", "Subtract existing selection", 'SELECT_SUBTRACT', 3),
        ],
        default='SET',
        options={'SKIP_SAVE'},
    )
    alt_mode: bpy.props.EnumProperty(
        name="Alternate Mode",
        description="Alternate selection mode",
        items=[
            ('SET', "Select", "Set a new selection", 'SELECT_SET', 1),
            ('ADD', "Extend Selection", "Extend existing selection", 'SELECT_EXTEND', 2),
            ('SUB', "Deselect", "Subtract existing selection", 'SELECT_SUBTRACT', 3),
        ],
        default='SUB',
        options={'SKIP_SAVE'},
    )
    alt_mode_toggle_key: bpy.props.EnumProperty(
        name="Alternate Mode Toggle Key",
        description="Toggle selection mode by holding this key",
        items=[
            ('CTRL', "CTRL", ""),
            ('ALT', "ALT", ""),
            ('SHIFT', "SHIFT", ""),
        ],
        default='SHIFT',
        options={'SKIP_SAVE'},
    )
    radius: bpy.props.IntProperty(
        name="Radius",
        description="Radius",
        default=25,
        min=1,
    )
    wait_for_input: bpy.props.BoolProperty(
        name="Wait for Input",
        description="Wait for mouse input or initialize circle selection immediately (usually you "
                    "should enable it when you assign the operator to a keyboard key)",
        default=False,
        options={'SKIP_SAVE'},
    )
    override_global_props: bpy.props.BoolProperty(
        name="Override Global Properties",
        description="Use properties in this keymaps item instead of properties in the global addon settings",
        default=False,
        options={'SKIP_SAVE'},
    )
    select_through: bpy.props.BoolProperty(
        name="Select Through",
        description="Select verts, faces and edges laying underneath",
        default=True,
        options={'SKIP_SAVE'},
    )
    select_through_toggle_key: bpy.props.EnumProperty(
        name="Selection Through Toggle Key",
        description="Toggle selection through by holding this key",
        items=[
            ('CTRL', "CTRL", ""),
            ('ALT', "ALT", ""),
            ('SHIFT', "SHIFT", ""),
            ('DISABLED', "DISABLED", ""),
        ],
        default='DISABLED',
        options={'SKIP_SAVE'},
    )
    select_through_toggle_type: bpy.props.EnumProperty(
        name="Selection Through Toggle Press / Hold",
        description="Toggle selection through by holding or by pressing key",
        items=[
            ('HOLD', "Holding", ""),
            ('PRESS', "Pressing", ""),
        ],
        default='HOLD',
        options={'SKIP_SAVE'},
    )
    default_color: bpy.props.FloatVectorProperty(
        name="Default Color",
        description="Tool color when disabled selection through",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0),
        options={'SKIP_SAVE'},
    )
    select_through_color: bpy.props.FloatVectorProperty(
        name="Select Through Color",
        description="Tool color when enabled selection through",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0),
        options={'SKIP_SAVE'},
    )
    show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable x-ray shading during selection",
        default=True,
        options={'SKIP_SAVE'},
    )
    select_all_edges: bpy.props.BoolProperty(
        name="Select All Edges",
        description="Additionally select edges that are partially inside the selection circle, "
                    "not just the ones completely inside the selection circle. Works only in "
                    "select through mode",
        default=False,
        options={'SKIP_SAVE'},
    )
    select_all_faces: bpy.props.BoolProperty(
        name="Select All Faces",
        description="Additionally select faces that are partially inside the selection circle, "
                    "not just the ones with centers inside the selection circle. Works only in "
                    "select through mode",
        default=False,
        options={'SKIP_SAVE'},
    )
    hide_mirror: bpy.props.BoolProperty(
        name="Hide Mirror",
        description="Hide mirror modifiers during selection",
        default=True,
        options={'SKIP_SAVE'},
    )
    hide_solidify: bpy.props.BoolProperty(
        name="Hide Solidify",
        description="Hide solidify modifiers during selection",
        default=True,
        options={'SKIP_SAVE'},
    )

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'EDIT_MESH'

    def __init__(self):
        self.stage = None
        self.curr_mode = self.mode
        self.directional = False
        self.direction = None

        self.last_mouse_region_x = 0
        self.last_mouse_region_y = 0

        self.init_mods = None
        self.init_overlays = None

        self.override_modal = False
        self.override_intersect_tests = False

        self.invert_select_through = False
        self.select_through_toggle_key_list = get_select_through_toggle_key_list()

        self.handler = None
        self.border_batch = None
        self.fill_batch = None
        self.unif_segment_color = None
        self.unif_gap_color = None
        self.unif_fill_color = None
        self.circle_verts_orig = None

    def invoke(self, context, event):
        # Set operator properties from addon preferences.
        set_properties_from_preferences(self, tool='CIRCLE')

        self.override_intersect_tests = (
            self.select_all_faces
            and context.tool_settings.mesh_select_mode[2]
            or self.select_all_edges
            and context.tool_settings.mesh_select_mode[1]
        )

        self.override_modal = (
            self.select_through_toggle_key != 'DISABLED'
            or self.alt_mode_toggle_key != 'SHIFT'
            or self.alt_mode != 'SUB'
            or not self.select_through
            and self.default_color[:] != (1.0, 1.0, 1.0)
            or self.select_through
            and self.select_through_color[:] != (1.0, 1.0, 1.0)
            or self.override_intersect_tests
        )

        self.init_mods = gather_modifiers(self, context)  # save initial modifier states
        self.init_overlays = gather_overlays(context)  # save initial x-ray overlay states

        # Set x-ray overlays and modifiers.
        initialize_shading_from_properties(self, context)
        set_modifiers_from_properties(self)

        context.window_manager.modal_handler_add(self)

        # Jump to.
        if self.override_modal:
            self.show_custom_ui(context, event)
            if self.wait_for_input:
                self.stage = 'CUSTOM_WAIT_FOR_INPUT'
            else:
                self.stage = 'CUSTOM_SELECTION'
        else:
            self.invoke_inbuilt_circle_select()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if self.stage == 'CUSTOM_WAIT_FOR_INPUT':
            # Update shader.
            if event.type == 'MOUSEMOVE':
                self.update_shader_position(context, event)

            # Toggle modifiers and overlays.
            if event.type in self.select_through_toggle_key_list:
                if (
                    event.value in {'PRESS', 'RELEASE'}
                    and self.select_through_toggle_type == 'HOLD'
                    or event.value == 'PRESS'
                    and self.select_through_toggle_type == 'PRESS'
                ):
                    self.invert_select_through = not self.invert_select_through
                    set_shading_from_properties(self, context)
                    update_shader_color(self, context)

            # Change radius.
            if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'NUMPAD_MINUS', 'NUMPAD_PLUS'}:
                self.update_radius(context, event)

            # Finish stage.
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                self.stage = 'CUSTOM_SELECTION'
                toggle_alt_mode(self, event)
                if self.override_intersect_tests and (
                    self.select_through
                    and not self.invert_select_through
                    or not self.select_through
                    and self.invert_select_through
                ):
                    self.begin_custom_intersect_tests(context)
                else:
                    self.exec_inbuilt_circle_select()

        if self.stage == 'CUSTOM_SELECTION':
            # Update shader.
            if event.type == 'MOUSEMOVE':
                self.update_shader_position(context, event)
                if self.override_intersect_tests and self.select_through:
                    self.begin_custom_intersect_tests(context)
                else:
                    self.exec_inbuilt_circle_select()

            # Toggle modifiers and overlays.
            if event.type in self.select_through_toggle_key_list:
                if (
                    event.value in {'PRESS', 'RELEASE'}
                    and self.select_through_toggle_type == 'HOLD'
                    or event.value == 'PRESS'
                    and self.select_through_toggle_type == 'PRESS'
                ):
                    self.invert_select_through = not self.invert_select_through
                    set_shading_from_properties(self, context)
                    update_shader_color(self, context)

            # Change radius.
            if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'NUMPAD_MINUS', 'NUMPAD_PLUS'}:
                self.update_radius(context, event)

            # Finish stage.
            if event.value == 'RELEASE' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                if self.wait_for_input:
                    self.stage = 'CUSTOM_WAIT_FOR_INPUT'
                else:
                    self.remove_custom_ui(context)
                    self.finish_modal(context)
                    bpy.ops.ed.undo_push(message="Circle Select")
                    return {'FINISHED'}

        # Finish modal.
        if event.value == 'PRESS' and event.type == 'ENTER':
            if self.stage in {'CUSTOM_WAIT_FOR_INPUT', 'CUSTOM_SELECTION'}:
                self.remove_custom_ui(context)
            self.finish_modal(context)
            return {'FINISHED'}

        if self.stage == 'INBUILT_OP':
            # Inbuilt op was finished, now finish modal.
            if event.type == 'MOUSEMOVE':
                self.radius = context.window_manager.operator_properties_last("view3d.select_circle").radius
                self.finish_modal(context)
                return {'FINISHED'}

        # Cancel modal.
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            if self.stage in {'CUSTOM_WAIT_FOR_INPUT', 'CUSTOM_SELECTION'}:
                self.remove_custom_ui(context)
                bpy.ops.ed.undo_push(message="Circle Select")
            self.finish_modal(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def show_custom_ui(self, context, event):
        """Set status text, draw shader."""
        enum_items = self.properties.bl_rna.properties["mode"].enum_items
        curr_mode_name = enum_items[self.curr_mode].name
        enum_items = self.properties.bl_rna.properties["alt_mode"].enum_items
        alt_mode_name = enum_items[self.alt_mode].name

        if self.wait_for_input:
            status_text = (
                "RMB, ESC: Cancel  |  ENTER: Confirm  |  WhDown/Pad+: Add  |  WhUp/Pad-: Subtract  |  "
                f"LMB: {curr_mode_name}  |  {self.alt_mode_toggle_key}+LMB: {alt_mode_name}"
            )
        else:
            status_text = "RMB, ESC: Cancel  |  WhDown/Pad+: Add  |  WhUp/Pad-: Subtract"
        if self.select_through_toggle_key != 'DISABLED':
            status_text += f"  |  {self.select_through_toggle_key}: Toggle Select Through"
        context.workspace.status_text_set(text=status_text)

        self.build_circle_shader()
        self.handler = context.space_data.draw_handler_add(self.draw_circle_shader, (), 'WINDOW', 'POST_PIXEL')
        self.update_shader_position(context, event)

    def update_radius(self, context, event):
        if event.type in {'WHEELUPMOUSE', 'NUMPAD_MINUS'}:
            self.radius -= 10
        elif event.type in {'WHEELDOWNMOUSE', 'NUMPAD_PLUS'}:
            self.radius += 10
        self.build_circle_shader()
        context.region.tag_redraw()

    def remove_custom_ui(self, context):
        """Restore cursor and status text, remove shader."""
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.region.tag_redraw()

    def invoke_inbuilt_circle_select(self):
        self.stage = 'INBUILT_OP'
        bpy.ops.view3d.select_circle(
            'INVOKE_DEFAULT', mode=self.curr_mode, wait_for_input=self.wait_for_input, radius=self.radius
        )

    def exec_inbuilt_circle_select(self):
        bpy.ops.view3d.select_circle(
            x=self.last_mouse_region_x,
            y=self.last_mouse_region_y,
            mode=self.curr_mode,
            wait_for_input=False,
            radius=self.radius,
        )

    def begin_custom_intersect_tests(self, context):
        center = (self.last_mouse_region_x, self.last_mouse_region_y)
        circle = (center, self.radius)
        select_mesh_elems(
            context,
            mode=self.curr_mode,
            tool='CIRCLE',
            tool_co=circle,
            select_all_edges=self.select_all_edges,
            select_all_faces=self.select_all_faces,
        )
        if self.curr_mode == 'SET':
            self.curr_mode = 'ADD'

    def finish_modal(self, context):
        restore_overlays(self, context)
        restore_modifiers(self)
        context.window_manager.operator_properties_last("mesh.select_circle_xray").radius = self.radius

    def update_shader_position(self, context, event):
        self.last_mouse_region_x = event.mouse_region_x
        self.last_mouse_region_y = event.mouse_region_y
        context.region.tag_redraw()

    @staticmethod
    def get_circle_verts_orig(radius):
        sides = 31
        # https://stackoverflow.com/questions/17258546/opengl-creating-a-circle-change-radius
        counts = np.arange(1, sides + 1, dtype="f")
        angles = np.multiply(counts, 2 * np.pi / sides)
        vert_x = np.multiply(np.sin(angles), radius)
        vert_y = np.multiply(np.cos(angles), radius)
        vert_co = np.vstack((vert_x, vert_y)).T
        vert_co.shape = (sides, 2)
        vertices = vert_co.tolist()
        vertices.append(vertices[0])
        return vertices

    def build_circle_shader(self):
        vertices = self.get_circle_verts_orig(self.radius)
        segment = (Vector(vertices[0]) - Vector(vertices[1])).length
        lengths = [segment * i for i in range(32)]

        self.unif_segment_color = border_shader.uniform_from_name("u_SegmentColor")
        self.unif_gap_color = border_shader.uniform_from_name("u_GapColor")
        self.border_batch = batch_for_shader(border_shader, 'LINE_STRIP', {"pos": vertices, "len": lengths})

        vertices.append(vertices[0])  # ending triangle
        vertices.insert(0, (0, 0))  # starting vert of triangle fan
        self.unif_fill_color = fill_shader.uniform_from_name("u_FillColor")
        self.fill_batch = batch_for_shader(fill_shader, 'TRI_FAN', {"pos": vertices})

    def draw_circle_shader(self):
        matrix = gpu.matrix.get_projection_matrix()
        if (
            self.select_through
            and not self.invert_select_through
            or not self.select_through
            and self.invert_select_through
        ):
            segment_color = (*self.select_through_color, 1)
            fill_color = (*self.select_through_color, 0.04)
        else:
            segment_color = (*self.default_color, 1)
            fill_color = (*self.default_color, 0.04)
        gap_color = (0.0, 0.0, 0.0, 1.0)

        glEnable(GL_BLEND)
        fill_shader.bind()
        fill_shader.uniform_float("u_ViewProjectionMatrix", matrix)
        fill_shader.uniform_float("u_X", self.last_mouse_region_x)
        fill_shader.uniform_float("u_Y", self.last_mouse_region_y)
        fill_shader.uniform_vector_float(self.unif_fill_color, pack("4f", *fill_color), 4, 1)
        self.fill_batch.draw(fill_shader)
        glDisable(GL_BLEND)

        border_shader.bind()
        border_shader.uniform_float("u_ViewProjectionMatrix", matrix)
        border_shader.uniform_float("u_X", self.last_mouse_region_x)
        border_shader.uniform_float("u_Y", self.last_mouse_region_y)
        border_shader.uniform_vector_float(self.unif_segment_color, pack("4f", *segment_color), 4, 1)
        border_shader.uniform_vector_float(self.unif_gap_color, pack("4f", *gap_color), 4, 1)
        self.border_batch.draw(border_shader)


classes = (MESH_OT_select_circle_xray,)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in classes:
        unregister_class(cls)
