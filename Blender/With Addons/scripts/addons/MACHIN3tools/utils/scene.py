import bpy
from mathutils import Vector, Quaternion


def set_cursor(matrix=None, location=Vector(), rotation=Quaternion()):

    cursor = bpy.context.scene.cursor

    if matrix:
        cursor.location = matrix.to_translation()
        cursor.rotation_quaternion = matrix.to_quaternion()
        cursor.rotation_mode = 'QUATERNION'

    else:
        cursor.location = location

        if cursor.rotation_mode == 'QUATERNION':
            cursor.rotation_quaternion = rotation

        elif cursor.rotation_mode == 'AXIS_ANGLE':
            cursor.rotation_axis_angle = rotation.to_axis_angle()

        else:
            cursor.rotation_euler = rotation.to_euler(cursor.rotation_mode)
