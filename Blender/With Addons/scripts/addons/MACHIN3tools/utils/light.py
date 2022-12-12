import bpy


def adjust_lights_for_rendering(mode='DECREASE'):
    divider = bpy.context.scene.M3.adjust_lights_on_render_divider

    for light in bpy.data.lights:
        if light.type == 'AREA':
            print("", light.name, light.energy, ' > ', light.energy / divider)

            if mode == 'DECREASE':
                light.energy /= divider

            elif mode == 'INCREASE':
                light.energy *= divider


def get_area_light_poll():
    return [obj for obj in bpy.data.objects if obj.type == 'LIGHT' and obj.data.type == 'AREA']
