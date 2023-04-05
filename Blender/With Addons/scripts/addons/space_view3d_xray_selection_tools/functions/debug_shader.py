import gpu
import bpy
from gpu_extras.batch import batch_for_shader
from bgl import glEnable, glDisable, GL_BLEND


def redraw_point_shader(context, points):
    dns = bpy.app.driver_namespace
    handler = dns.get("draw_xray_points_debug")
    if handler:
        context.space_data.draw_handler_remove(handler, 'WINDOW')
        del bpy.app.driver_namespace['draw_xray_points_debug']

    point_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    point_batch = batch_for_shader(point_shader, 'POINTS', {"pos": points})

    handler = context.space_data.draw_handler_add(draw_point_shader, (point_shader, point_batch,), 'WINDOW',
                                                  'POST_PIXEL')
    dns['draw_xray_points_debug'] = handler
    context.area.tag_redraw()


def draw_point_shader(point_shader, point_batch):
    point_shader.bind()
    point_shader.uniform_float("color", (1.0, 0.0, 0.0, 1.0))
    point_batch.draw(point_shader)


def redraw_segment_shader(context, points, indices):
    dns = bpy.app.driver_namespace
    handler = dns.get("draw_xray_segment_debug")
    if handler:
        context.space_data.draw_handler_remove(handler, 'WINDOW')
        del bpy.app.driver_namespace['draw_xray_segment_debug']

    segment_shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    segment_batch = batch_for_shader(segment_shader, 'LINES', {"pos": points}, indices=indices)

    handler = context.space_data.draw_handler_add(draw_segment_shader, (segment_shader, segment_batch,), 'WINDOW',
                                                  'POST_PIXEL')
    dns['draw_xray_segment_debug'] = handler
    context.area.tag_redraw()


def draw_segment_shader(segment_shader, segment_batch):
    glEnable(GL_BLEND)
    segment_shader.bind()
    segment_shader.uniform_float("color", (0.0, 1.0, 0.0, 0.2))
    segment_batch.draw(segment_shader)
    glDisable(GL_BLEND)

    # points = ob_2dbboxes.reshape((-1, 2)).tolist()
    # redraw_point_shader(context, points)

    # points = ob_2dbbox_segments.reshape((-1, 2)).tolist()
    # indices = np.arange(ob_2dbbox_segments.size, dtype="i").reshape((-1, 2))
    # redraw_segment_shader(context, points, indices)
