import bpy
from mathutils import Vector, Matrix
import gpu
from gpu_extras.batch import batch_for_shader
from gpu_extras.presets import draw_circle_2d
import blf
from . wm import get_last_operators
from . registration import get_prefs, get_addon
from . ui import require_header_offset, get_zoom_factor
from . tools import get_active_tool
from .. colors import red, green, blue, black, white


hypercursor = None

def draw_axes_HUD(context, objects):
    global hypercursor
    
    if not hypercursor:
        hypercursor = get_addon('HyperCursor')[0]


    if context.space_data.overlay.show_overlays:
        m3 = context.scene.M3

        size = m3.draw_axes_size
        alpha = m3.draw_axes_alpha - 0.001
        screenspace = m3.draw_axes_screenspace
        ui_scale = context.preferences.view.ui_scale

        show_cursor = context.space_data.overlay.show_cursor
        show_hyper_cursor = hypercursor and get_active_tool(context).idname in ['machin3.tool_hyper_cursor', 'machin3.tool_hyper_cursor_simple'] and context.scene.HC.show_gizmos

        axes = [(Vector((1, 0, 0)), red), (Vector((0, 1, 0)), green), (Vector((0, 0, 1)), blue)]

        for axis, color in axes:
            coords = []

            for obj in objects:


                if obj == 'CURSOR':

                    if not show_hyper_cursor:
                        mx = context.scene.cursor.matrix
                        origin = mx.decompose()[0]

                        factor = get_zoom_factor(context, origin, scale=300, ignore_obj_scale=True) if screenspace else 1

                        if show_cursor and screenspace:
                            coords.append(origin + (mx.to_3x3() @ axis).normalized() * 0.1 * ui_scale * factor * 0.8)
                            coords.append(origin + (mx.to_3x3() @ axis).normalized() * 0.1 * ui_scale * factor * 1.2)

                        else:
                            coords.append(origin + (mx.to_3x3() @ axis).normalized() * size * ui_scale * factor * 0.9)
                            coords.append(origin + (mx.to_3x3() @ axis).normalized() * size * ui_scale * factor)

                            coords.append(origin + (mx.to_3x3() @ axis).normalized() * size * ui_scale * factor * 0.1)
                            coords.append(origin + (mx.to_3x3() @ axis).normalized() * size * ui_scale * factor * 0.7)


                elif str(obj) != '<bpy_struct, Object invalid>':
                    mx = obj.matrix_world
                    origin = mx.decompose()[0]

                    factor = get_zoom_factor(context, origin, scale=300, ignore_obj_scale=True) if screenspace else 1

                    coords.append(origin + (mx.to_3x3() @ axis).normalized() * size * ui_scale * factor * 0.1)
                    coords.append(origin + (mx.to_3x3() @ axis).normalized() * size * ui_scale * factor)


            if coords:
                indices = [(i, i + 1) for i in range(0, len(coords), 2)]

                shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
                shader.bind()
                shader.uniform_float("color", (*color, alpha))

                gpu.state.depth_test_set('NONE')
                gpu.state.blend_set('ALPHA' if alpha < 1 else 'NONE')
                gpu.state.line_width_set(2)

                use_legacy_line_smoothing(alpha, 2)

                batch = batch_for_shader(shader, 'LINES', {"pos": coords}, indices=indices)
                batch.draw(shader)


def draw_focus_HUD(context, color=(1, 1, 1), alpha=1, width=2):
    if context.space_data.overlay.show_overlays:
        region = context.region
        view = context.space_data

        if view.local_view:


            coords = [(width, width), (region.width - width, width), (region.width - width, region.height - width), (width, region.height - width)]
            indices =[(0, 1), (1, 2), (2, 3), (3, 0)]

            shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
            shader.bind()
            shader.uniform_float("color", (*color, alpha / 4))

            gpu.state.depth_test_set('NONE')
            gpu.state.blend_set('ALPHA' if (alpha / 4) < 1 else 'NONE')
            gpu.state.line_width_set(width)

            batch = batch_for_shader(shader, 'LINES', {"pos": coords}, indices=indices)
            batch.draw(shader)


            scale = context.preferences.view.ui_scale * get_prefs().HUD_scale
            offset = 4

            if require_header_offset(context, top=True):
                offset += int(25)

            title = "Focus Level: %d" % len(context.scene.M3.focus_history)

            stashes = True if context.active_object and getattr(context.active_object, 'MM', False) and getattr(context.active_object.MM, 'stashes') else False
            center = (region.width / 2) + (scale * 100) if stashes else region.width / 2

            font = 1
            fontsize = int(12 * scale)

            blf.size(font, fontsize, 72)
            blf.color(font, *color, alpha)
            blf.position(font, center - int(60 * scale), region.height - offset - int(fontsize), 0)

            blf.draw(font, title)


def draw_surface_slide_HUD(context, color=(1, 1, 1), alpha=1, width=2):
    if context.space_data.overlay.show_overlays:
        region = context.region

        scale = context.preferences.view.ui_scale * get_prefs().HUD_scale
        offset = 0

        if require_header_offset(context, top=False):
            offset += int(20)

        title = "Surface Sliding"

        font = 1
        fontsize = int(12 * scale)

        blf.size(font, fontsize, 72)
        blf.color(font, *color, alpha)
        blf.position(font, (region.width / 2) - int(60 * scale), 0 + offset + int(fontsize), 0)

        blf.draw(font, title)


def draw_screen_cast_HUD(context):
    p = get_prefs()
    operators = get_last_operators(context, debug=False)[-p.screencast_operator_count:]

    font = 0
    scale = context.preferences.view.ui_scale * get_prefs().HUD_scale

    tools = [r for r in context.area.regions if r.type == 'TOOLS']
    offset_x = tools[0].width if tools else 0

    offset_x += 7 if p.screencast_show_addon else 15

    redo = [r for r in context.area.regions if r.type == 'HUD']
    offset_y = redo[0].height + 50 if redo else 50

    emphasize = 1.25

    if p.screencast_show_addon:
        blf.size(font, round(p.screencast_fontsize * scale * emphasize), 72)
        addon_offset_x = blf.dimensions(font, 'MM')[0]
    else:
        addon_offset_x = 0

    y = 0
    hgap = 10

    for idx, (addon, label, idname, prop) in enumerate(reversed(operators)):
        size = round(p.screencast_fontsize * scale * (emphasize if idx == 0 else 1))
        vgap = round(size / 2)

        color = green if idname.startswith('machin3.') and p.screencast_highlight_machin3 else white
        alpha = (len(operators) - idx) / len(operators)

        if idx == 0:
            blf.enable(font, blf.SHADOW)

            blf.shadow_offset(font, 3, -3)
            blf.shadow(font, 5, *black, 1.0)



        text = f"{label}: {prop}" if prop else label

        x = offset_x + addon_offset_x
        y = offset_y * scale if idx == 0 else y + (blf.dimensions(font, text)[1] + vgap)

        blf.size(font, size, 72)
        blf.color(font, *color, alpha)
        blf.position(font, x, y, 0)

        blf.draw(font, text)



        if p.screencast_show_idname:
            x += blf.dimensions(font, text)[0] + hgap

            blf.size(font, size - 2, 72)
            blf.color(font, *color, alpha * 0.3)
            blf.position(font, x, y, 0)

            blf.draw(font, f"{idname}")

            blf.size(font, size, 72)


        if idx == 0:
            blf.disable(font, blf.SHADOW)



        if addon and p.screencast_show_addon:
            blf.size(font, size, 72)

            x = offset_x + addon_offset_x - blf.dimensions(font, addon)[0] - (hgap / 2)

            blf.color(font, *white, alpha * 0.3)
            blf.position(font, x, y, 0)

            blf.draw(font, addon)

        if idx == 0:
            y += blf.dimensions(font, text)[1]



def update_HUD_location(self, event, offsetx=20, offsety=20):

    self.HUD_x = event.mouse_x - self.region_offset_x + offsetx
    self.HUD_y = event.mouse_y - self.region_offset_y + offsety


def draw_label(context, title='', coords=None, center=True, color=(1, 1, 1), alpha=1):

    if not coords:
        region = context.region
        width = region.width / 2
        height = region.height / 2
    else:
        width, height = coords

    scale = context.preferences.view.ui_scale * get_prefs().HUD_scale

    font = 1
    fontsize = int(12 * scale)

    blf.size(font, fontsize, 72)
    blf.color(font, *color, alpha)

    if center:
        blf.position(font, width - (int(len(title) * scale * 7) / 2), height + int(fontsize), 0)
    else:
        blf.position(font, *(coords), 1)


    blf.draw(font, title)



def use_legacy_line_smoothing(alpha, width):

    if get_prefs().use_legacy_line_smoothing and alpha < 1:
        try:
            import bgl

            bgl.glEnable(bgl.GL_BLEND)
            bgl.glLineWidth(width)
            bgl.glEnable(bgl.GL_LINE_SMOOTH)
        except:
            pass


def draw_point(co, mx=Matrix(), color=(1, 1, 1), size=6, alpha=1, xray=True, modal=True):
    def draw():
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set('NONE' if xray else 'LESS_EQUAL')
        gpu.state.blend_set('ALPHA' if alpha < 1 else 'NONE')
        gpu.state.point_size_set(size)

        batch = batch_for_shader(shader, 'POINTS', {"pos": [mx @ co]})
        batch.draw(shader)

    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')


def draw_points(coords, indices=None, mx=Matrix(), color=(1, 1, 1), size=6, alpha=1, xray=True, modal=True):
    def draw():
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set('NONE' if xray else 'LESS_EQUAL')
        gpu.state.blend_set('ALPHA' if alpha < 1 else 'NONE')
        gpu.state.point_size_set(size)

        if indices:
            if mx != Matrix():
                batch = batch_for_shader(shader, 'POINTS', {"pos": [mx @ co for co in coords]}, indices=indices)
            else:
                batch = batch_for_shader(shader, 'POINTS', {"pos": coords}, indices=indices)

        else:
            if mx != Matrix():
                batch = batch_for_shader(shader, 'POINTS', {"pos": [mx @ co for co in coords]})
            else:
                batch = batch_for_shader(shader, 'POINTS', {"pos": coords})

        batch.draw(shader)


    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')


def draw_line(coords, indices=None, mx=Matrix(), color=(1, 1, 1), width=1, alpha=1, xray=True, modal=True):
    def draw():
        nonlocal indices

        if not indices:
            indices = [(i, i + 1) for i in range(0, len(coords)) if i < len(coords) - 1]

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set('NONE' if xray else 'LESS_EQUAL')
        gpu.state.blend_set('ALPHA' if alpha < 1 else 'NONE')
        gpu.state.line_width_set(width)

        use_legacy_line_smoothing(alpha, width)

        batch = batch_for_shader(shader, 'LINES', {"pos": [mx @ co for co in coords]}, indices=indices)
        batch.draw(shader)

    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')


def draw_lines(coords, indices=None, mx=Matrix(), color=(1, 1, 1), width=1, alpha=1, xray=True, modal=True):
    def draw():
        nonlocal indices

        if not indices:
            indices = [(i, i + 1) for i in range(0, len(coords), 2)]

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set('NONE' if xray else 'LESS_EQUAL')
        gpu.state.blend_set('ALPHA' if alpha < 1 else 'NONE')
        gpu.state.line_width_set(width)

        use_legacy_line_smoothing(alpha, width)

        if mx != Matrix():
            batch = batch_for_shader(shader, 'LINES', {"pos": [mx @ co for co in coords]}, indices=indices)

        else:
            batch = batch_for_shader(shader, 'LINES', {"pos": coords}, indices=indices)

        batch.draw(shader)

    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')


def draw_vector(vector, origin=Vector((0, 0, 0)), mx=Matrix(), color=(1, 1, 1), width=1, alpha=1, xray=True, modal=True):
    def draw():
        coords = [mx @ origin, mx @ origin + mx.to_3x3() @ vector]

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set('NONE' if xray else 'LESS_EQUAL')
        gpu.state.blend_set('ALPHA' if alpha < 1 else 'NONE')
        gpu.state.line_width_set(width)

        use_legacy_line_smoothing(alpha, width)

        batch = batch_for_shader(shader, 'LINES', {"pos": coords})
        batch.draw(shader)


    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')


def draw_vectors(vectors, origins, mx=Matrix(), color=(1, 1, 1), width=1, alpha=1, xray=True, modal=True):
    def draw():
        coords = []

        for v, o in zip(vectors, origins):
            coords.append(mx @ o)
            coords.append(mx @ o + mx.to_3x3() @ v)

        indices = [(i, i + 1) for i in range(0, len(coords), 2)]

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set('NONE' if xray else 'LESS_EQUAL')
        gpu.state.blend_set('ALPHA' if alpha < 1 else 'NONE')
        gpu.state.line_width_set(width)

        use_legacy_line_smoothing(alpha, width)

        batch = batch_for_shader(shader, 'LINES', {"pos": coords}, indices=indices)
        batch.draw(shader)


    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')


def draw_circle(coords, size=10, width=1, segments=64, color=(1, 1, 1), alpha=1, xray=True, modal=True):
    def draw():
        gpu.state.depth_test_set('NONE' if xray else 'LESS_EQUAL')
        gpu.state.blend_set('ALPHA' if alpha < 1 else 'NONE')
        gpu.state.line_width_set(width)

        use_legacy_line_smoothing(alpha, width)

        draw_circle_2d(coords, (*color, alpha), size, segments=segments)

    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')


def draw_mesh_wire(batch, color=(1, 1, 1), width=1, alpha=1, xray=True, modal=True):
    def draw():
        nonlocal batch
        coords, indices = batch

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set('NONE' if xray else 'LESS_EQUAL')
        gpu.state.blend_set('ALPHA' if alpha < 1 else 'NONE')
        gpu.state.line_width_set(width)

        use_legacy_line_smoothing(alpha, width)

        b = batch_for_shader(shader, 'LINES', {"pos": coords}, indices=indices)
        b.draw(shader)

        del shader
        del b

    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')


def draw_bbox(bbox, mx=Matrix(), color=(1, 1, 1), corners=0, width=1, alpha=1, xray=True, modal=True):

    def draw():
        if corners:
            length = corners

            coords = [bbox[0], bbox[0] + (bbox[1] - bbox[0]) * length, bbox[0] + (bbox[3] - bbox[0]) * length, bbox[0] + (bbox[4] - bbox[0]) * length,
                      bbox[1], bbox[1] + (bbox[0] - bbox[1]) * length, bbox[1] + (bbox[2] - bbox[1]) * length, bbox[1] + (bbox[5] - bbox[1]) * length,
                      bbox[2], bbox[2] + (bbox[1] - bbox[2]) * length, bbox[2] + (bbox[3] - bbox[2]) * length, bbox[2] + (bbox[6] - bbox[2]) * length,
                      bbox[3], bbox[3] + (bbox[0] - bbox[3]) * length, bbox[3] + (bbox[2] - bbox[3]) * length, bbox[3] + (bbox[7] - bbox[3]) * length,
                      bbox[4], bbox[4] + (bbox[0] - bbox[4]) * length, bbox[4] + (bbox[5] - bbox[4]) * length, bbox[4] + (bbox[7] - bbox[4]) * length,
                      bbox[5], bbox[5] + (bbox[1] - bbox[5]) * length, bbox[5] + (bbox[4] - bbox[5]) * length, bbox[5] + (bbox[6] - bbox[5]) * length,
                      bbox[6], bbox[6] + (bbox[2] - bbox[6]) * length, bbox[6] + (bbox[5] - bbox[6]) * length, bbox[6] + (bbox[7] - bbox[6]) * length,
                      bbox[7], bbox[7] + (bbox[3] - bbox[7]) * length, bbox[7] + (bbox[4] - bbox[7]) * length, bbox[7] + (bbox[6] - bbox[7]) * length]

            indices = [(0, 1), (0, 2), (0, 3),
                       (4, 5), (4, 6), (4, 7),
                       (8, 9), (8, 10), (8, 11),
                       (12, 13), (12, 14), (12, 15),
                       (16, 17), (16, 18), (16, 19),
                       (20, 21), (20, 22), (20, 23),
                       (24, 25), (24, 26), (24, 27),
                       (28, 29), (28, 30), (28, 31)]


        else:
            coords = bbox
            indices = [(0, 1), (1, 2), (2, 3), (3, 0),
                       (4, 5), (5, 6), (6, 7), (7, 4),
                       (0, 4), (1, 5), (2, 6), (3, 7)]

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set('NONE' if xray else 'LESS_EQUAL')
        gpu.state.blend_set('ALPHA' if alpha < 1 else 'NONE')
        gpu.state.line_width_set(width)

        use_legacy_line_smoothing(alpha, width)

        if mx != Matrix():
            batch = batch_for_shader(shader, 'LINES', {"pos": [mx @ co for co in coords]}, indices=indices)

        else:
            batch = batch_for_shader(shader, 'LINES', {"pos": coords}, indices=indices)

        batch.draw(shader)

    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')


def draw_cross_3d(co, mx=Matrix(), color=(1, 1, 1), width=1, length=1, alpha=1, xray=True, modal=True):
    def draw():

        x = Vector((1, 0, 0))
        y = Vector((0, 1, 0))
        z = Vector((0, 0, 1))

        coords = [(co - x) * length, (co + x) * length,
                  (co - y) * length, (co + y) * length,
                  (co - z) * length, (co + z) * length]

        indices = [(0, 1), (2, 3), (4, 5)]

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set('NONE' if xray else 'LESS_EQUAL')
        gpu.state.blend_set('ALPHA' if alpha < 1 else 'NONE')
        gpu.state.line_width_set(width)

        use_legacy_line_smoothing(alpha, width)

        if mx != Matrix():
            batch = batch_for_shader(shader, 'LINES', {"pos": [mx @ co for co in coords]}, indices=indices)

        else:
            batch = batch_for_shader(shader, 'LINES', {"pos": coords}, indices=indices)

        batch.draw(shader)

    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')



def draw_tris(coords, indices=None, mx=Matrix(), color=(1, 1, 1), width=1, alpha=1, xray=True, modal=True):
    def draw():
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        shader.bind()
        shader.uniform_float("color", (*color, alpha))

        gpu.state.depth_test_set('NONE' if xray else 'LESS_EQUAL')
        gpu.state.blend_set('ALPHA' if alpha < 1 else 'NONE')
        gpu.state.line_width_set(width)

        if mx != Matrix():
            batch = batch_for_shader(shader, 'TRIS', {"pos": [mx @ co for co in coords]}, indices=indices)

        else:
            batch = batch_for_shader(shader, 'TRIS', {"pos": coords}, indices=indices)

        batch.draw(shader)

    if modal:
        draw()

    else:
        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')
