from mathutils import Matrix, Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d


def set_xray(context):
    x = (context.scene.M3.pass_through, context.scene.M3.show_edit_mesh_wire)
    shading = context.space_data.shading

    shading.show_xray = True if any(x) else False

    if context.scene.M3.show_edit_mesh_wire:
        shading.xray_alpha = 0.1

    elif context.scene.M3.pass_through:
        shading.xray_alpha = 1 if context.active_object and context.active_object.type == "MESH" else 0.5


def reset_xray(context):
    shading = context.space_data.shading

    shading.show_xray = False
    shading.xray_alpha = 0.5


def update_local_view(space_data, states):
    if space_data.local_view:
        for obj, local in states:
            obj.local_view_set(space_data, local)


def reset_viewport(context, disable_toolbar=False):
    for screen in context.workspace.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        r3d = space.region_3d

                        r3d.view_distance = 10
                        r3d.view_matrix = Matrix(((1, 0, 0, 0),
                                                  (0, 0.2, 1, -1),
                                                  (0, -1, 0.2, -10),
                                                  (0, 0, 0, 1)))

                        if disable_toolbar:
                            space.show_region_toolbar = False


def sync_light_visibility(scene):


    for view_layer in scene.view_layers:
        lights = [obj for obj in view_layer.objects if obj.type == 'LIGHT']

        for light in lights:
            hidden = light.hide_get(view_layer=view_layer)

            if light.hide_render != hidden:
                light.hide_render = hidden


def get_loc_2d(context, loc):

    loc_2d = location_3d_to_region_2d(context.region, context.region_data, loc)
    return loc_2d if loc_2d else Vector((-1000, -1000))
