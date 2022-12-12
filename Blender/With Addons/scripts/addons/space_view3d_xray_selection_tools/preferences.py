import os
import bpy


def get_addon_name():
    return os.path.basename(os.path.dirname(os.path.realpath(__file__)))


def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences
