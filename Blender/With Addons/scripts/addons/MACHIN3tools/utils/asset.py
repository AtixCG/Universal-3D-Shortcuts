import bpy
import os
from . system import printd
from . registration import get_prefs


def get_catalogs_from_asset_libraries(context, debug=False):

    asset_libraries = context.preferences.filepaths.asset_libraries
    all_catalogs = []

    for lib in asset_libraries:
        name = lib.name
        path = lib.path

        cat_path = os.path.join(path, 'blender_assets.cats.txt')

        if os.path.exists(cat_path):
            if debug:
                print(name, cat_path)

            with open(cat_path) as f:
                lines = f.readlines()

            for line in lines:
                if line != '\n' and not any([line.startswith(skip) for skip in ['#', 'VERSION']]) and len(line.split(':')) == 3:
                    all_catalogs.append(line[:-1])

    catalogs = {}

    for cat in all_catalogs:
        uuid, catalog, simple_name = cat.split(':')

        if catalog not in catalogs:
            catalogs[catalog] = {'uuid': uuid,
                                 'simple_name': simple_name}

    if debug:
        printd(catalogs)

    return catalogs


def update_asset_catalogs(self, context):
    self.catalogs = get_catalogs_from_asset_libraries(context, debug=False)

    items = [('NONE', 'None', '')]

    for catalog in self.catalogs:
        items.append((catalog, catalog, ""))

    default = get_prefs().preferred_default_catalog if get_prefs().preferred_default_catalog in self.catalogs else 'NONE'
    bpy.types.WindowManager.M3_asset_catalogs = bpy.props.EnumProperty(name="Asset Categories", items=items, default=default)
