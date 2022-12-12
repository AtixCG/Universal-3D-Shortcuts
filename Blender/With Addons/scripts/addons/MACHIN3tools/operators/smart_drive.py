import bpy
from bpy.props import StringProperty
from math import radians, degrees
from .. items import axis_mapping_dict


class SmartDrive(bpy.types.Operator):
    bl_idname = 'machin3.smart_drive'
    bl_label = 'MACHIN3: Smart Drive'
    bl_description = 'Drive one Object using another'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        m3 = context.scene.M3

        driver_start = m3.driver_start
        driver_end = m3.driver_end

        driven_start = m3.driven_start
        driven_end = m3.driven_end

        if driver_start != driver_end and driven_start != driven_end and context.active_object:
            driven = context.active_object
            sel = [obj for obj in context.selected_objects if obj != driven]

            return len(sel) == 1

    def execute(self, context):
        m3 = context.scene.M3

        driver_start = m3.driver_start
        driver_end = m3.driver_end
        driver_transform = m3.driver_transform
        driver_axis = m3.driver_axis
        driver_space = m3.driver_space

        driven_start = m3.driven_start
        driven_end = m3.driven_end
        driven_transform = m3.driven_transform
        driven_axis = m3.driven_axis
        driven_limit = m3.driven_limit

        path = driven_transform.lower()
        index = axis_mapping_dict[driven_axis]

        driven = context.active_object
        driver = [obj for obj in context.selected_objects if obj != driven][0]

        if driven.animation_data:
            for d in driven.animation_data.drivers:
                if d.data_path == path and d.array_index == index:
                    driven.animation_data.drivers.remove(d)

        fcurve = driven.driver_add(path, index)

        drv = fcurve.driver
        drv.type = 'SCRIPTED'

        var = drv.variables.new()
        var.name = path[:3]
        var.type = 'TRANSFORMS'

        target = var.targets[0]
        target.id = driver
        target.transform_type = '%s_%s' % (driver_transform[:3], driver_axis)

        if driver_space == 'AUTO':
            target.transform_space = 'LOCAL_SPACE' if driver.parent else 'WORLD_SPACE'
        else:
            target.transform_space = driver_space

        if driver_transform == 'ROTATION_EULER':
            driver_start = radians(driver_start)
            driver_end = radians(driver_end)

        if driven_transform == 'ROTATION_EULER':
            driven_start = radians(driven_start)
            driven_end = radians(driven_end)

        drv.expression = self.get_expression(driver_start, driver_end, driven_start, driven_end, driven_limit, var.name)

        return {'FINISHED'}

    def get_expression(self, driver_start, driver_end, driven_start, driven_end, driven_limit, varname):

        range_driver = abs(driver_end - driver_start)
        range_driven = abs(driven_end - driven_start)

        if driver_end > driver_start:
            expr = f'((({varname} - {driver_start}) / {range_driver}) * {range_driven})'

        else:
            expr = f'((({driver_start} - {varname}) / {range_driver}) * {range_driven})'

        if driven_end > driven_start:
            expr = f'{expr} + {driven_start}'

            if driven_limit == 'START':
                expr = f'max({driven_start}, {expr})'

            elif driven_limit == 'END':
                expr = f'min({driven_end}, {expr})'

            elif driven_limit == 'BOTH':
                expr = f'max({driven_start}, min({driven_end}, {expr}))'


        else:
            expr = f'{driven_start} - {expr}'

            if driven_limit == 'START':
                expr = f'min({driven_start}, {expr})'

            elif driven_limit == 'END':
                expr = f'max({driven_end}, {expr})'

            elif driven_limit == 'BOTH':
                expr = f'min({driven_start}, max({driven_end}, {expr}))'

        return expr


class SwitchValues(bpy.types.Operator):
    bl_idname = 'machin3.switch_driver_values'
    bl_label = 'MACHIN3: Switch Driver Values'
    bl_options = {'REGISTER', 'UNDO'}

    mode: StringProperty(name='Mode', default='DRIVER')

    @classmethod
    def description(cls, context, properties):
        return 'Switch Start and End %s Values' % (properties.mode.capitalize())

    def execute(self, context):
        m3 = context.scene.M3

        if self.mode == 'DRIVER':
            m3.driver_start, m3.driver_end = m3.driver_end, m3.driver_start

        elif self.mode == 'DRIVEN':
            m3.driven_start, m3.driven_end = m3.driven_end, m3.driven_start

        return {'FINISHED'}


class SetValue(bpy.types.Operator):
    bl_idname = 'machin3.set_driver_value'
    bl_label = 'MACHIN3: set_driver_value'
    bl_options = {'REGISTER', 'UNDO'}

    mode: StringProperty(name='Mode', default='DRIVER')
    value: StringProperty(name='Value', default='START')


    @classmethod
    def description(cls, context, properties):
        return 'Set %s %s Value' % (properties.mode.capitalize(), properties.value.capitalize())

    @classmethod
    def poll(cls, context):
        return context.active_object and context.selected_objects == [context.active_object]

    def execute(self, context):
        active = context.active_object

        value = self.value.lower()
        mode = self.mode.lower()

        m3 = context.scene.M3

        axis = getattr(m3, f'{mode}_axis')
        transform = getattr(m3, f'{mode}_transform').lower()

        val = getattr(active, transform)[axis_mapping_dict[axis]]

        if transform == 'rotation_euler':
            val = degrees(val)

        setattr(m3, f'{mode}_{value}', val)

        return {'FINISHED'}
