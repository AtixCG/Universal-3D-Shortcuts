from mathutils import Vector

axis_items = [('X', 'X', ''),
              ('Y', 'Y', ''),
              ('Z', 'Z', '')]

axis_index_mapping = {'X': 0,
                      'Y': 1,
                      'Z': 2}

axis_vector_mappings = {'X': Vector((1, 0, 0)),
                        'Y': Vector((0, 1, 0)),
                        'Z': Vector((0, 0, 1))}

uv_axis_items = [('U', 'U', ''),
                 ('V', 'V', '')]



ctrl = ['LEFT_CTRL', 'RIGHT_CTRL']
alt = ['LEFT_ALT', 'RIGHT_ALT']
shift = ['LEFT_SHIFT', 'RIGHT_SHIFT']



preferences_tabs = [("GENERAL", "General", ""),
                    ("KEYMAPS", "Keymaps", ""),
                    ("ABOUT", "About", "")]

matcap_background_type_items = [("THEME", "Theme", ""),
                                ("WORLD", "World", ""),
                                ("VIEWPORT", "Viewport", "")]




smartvert_mode_items = [("MERGE", "Merge", ""),
                        ("CONNECT", "Connect Paths", "")]


smartvert_merge_type_items = [("LAST", "Last", ""),
                              ("CENTER", "Center", ""),
                              ("PATHS", "Paths", "")]

smartvert_path_type_items = [("TOPO", "Topo", ""),
                             ("LENGTH", "Length", "")]


smartedge_sharp_mode_items = [('SHARPEN', 'Sharpen', ''),
                              ('CHAMFER', 'Chamfer', ''),
                              ('KOREAN', 'Korean Bevel', '')]

smartedge_select_mode_items = [('BOUNDS', 'Bounds/Region', ''),
                               ('ADJACENT', 'Adjacent', '')]

focus_method_items = [('VIEW_SELECTED', 'View Selected', ''),
                      ('LOCAL_VIEW', 'Local View', '')]

focus_levels_items = [('SINGLE', 'Single', ''),
                      ('MULTIPLE', 'Multiple', '')]

align_mode_items = [('VIEW', 'View', ''),
                    ('AXES', 'Axes', '')]

align_type_items = [('MIN', 'Min', ''),
                    ('MAX', 'Max', ''),
                    ('AVERAGE', 'Average', ''),
                    ('ZERO', 'Zero', ''),
                    ('CURSOR', 'Cursor', '')]

align_direction_items = [('LEFT', 'Left', ''),
                         ('RIGHT', 'Right', ''),
                         ('TOP', 'Top', ''),
                         ('BOTTOM', 'Bottom', ''),
                         ('HORIZONTAL', 'Horizontal', ''),
                         ('VERTICAL', 'Vertical', '')]

align_space_items = [('LOCAL', 'Local', ''),
                     ('WORLD', 'World', ''),
                     ('CURSOR', 'Cursor', '')]

obj_align_mode_items = [('ORIGIN', 'Origin', ''),
                        ('CURSOR', 'Cursor', ''),
                        ('ACTIVE', 'Active', ''),
                        ('FLOOR', 'Floor', '')]

cleanup_select_items = [("NON-MANIFOLD", "Non-Manifold", ""),
                        ("NON-PLANAR", "Non-Planar", ""),
                        ("TRIS", "Tris", ""),
                        ("NGONS", "Ngons", "")]

driver_limit_items = [('NONE', 'None', ''),
                      ('START', 'Start', ''),
                      ('END', 'End', ''),
                      ('BOTH', 'Both', '')]

driver_transform_items = [('LOCATION', 'Location', ''),
                          ('ROTATION_EULER', 'Rotation', '')]

driver_space_items = [('AUTO', 'Auto', 'Choose Local or World space based on whether driver object is parented'),
                      ('LOCAL_SPACE', 'Local', ''),
                      ('WORLD_SPACE', 'World', '')]

axis_mapping_dict = {'X': 0, 'Y': 1, 'Z': 2}

uv_align_axis_mapping_dict = {'U': 0, 'V': 1}

bridge_interpolation_items = [('LINEAR', 'Linear', ''),
                              ('PATH', 'Path', ''),
                              ('SURFACE', 'Surface', '')]

view_axis_items = [("FRONT", "Front", ""),
                   ("BACK", "Back", ""),
                   ("LEFT", "Left", ""),
                   ("RIGHT", "Right", ""),
                   ("TOP", "Top", ""),
                   ("BOTTOM", "Bottom", "")]

group_location_items = [('AVERAGE', 'Average', ''),
                        ('ACTIVE', 'Active', ''),
                        ('CURSOR', 'Cursor', ''),
                        ('WORLD', 'World', '')]

cursor_spin_angle_preset_items = [('None', 'None', ''),
                                  ('30', '30', ''),
                                  ('45', '45', ''),
                                  ('60', '60', ''),
                                  ('90', '90', ''),
                                  ('135', '135', ''),
                                  ('180', '180', '')]


create_assembly_asset_empty_location_items = [('AVG', 'Average', ''),
                                              ('AVGFLOOR', 'Average Floor', ''),
                                              ('WORLDORIGIN', 'World Origin', '')]

create_assembly_asset_empty_collection_items = [('SCENECOL', 'Add to Scene Collection', ''),
                                                ('OBJCOLS', 'Add to Object Collections', '')]


shade_mode_items = [('SMOOTH', 'Smooth', ''),
                    ('FLAT', 'Flat', '')]




eevee_preset_items = [('NONE', 'None', ''),
                      ('LOW', 'Low', 'Use Scene Lights, Ambient Occlusion and Screen Space Reflections'),
                      ('HIGH', 'High', 'Use Bloom and Screen Space Refractions'),
                      ('ULTRA', 'Ultra', 'Use Scene World and Volumetrics.\nCreate Principled Volume node if necessary')]

render_engine_items = [('BLENDER_EEVEE', 'Eevee', ''),
                       ('CYCLES', 'Cycles', '')]


shading_light_items = [('STUDIO', 'Studio', ''),
                       ('MATCAP', 'Matcap', ''),
                       ('FLAT', 'Flat', '')]


cycles_device_items = [('CPU', 'CPU', ''),
                       ('GPU', 'GPU', '')]


bc_orientation_items = [('LOCAL', 'Local', ''),
                        ('NEAREST', 'Nearest', ''),
                        ('LONGEST', 'Longest', '')]


tool_name_mapping_dict = {'BC': 'BoxCutter',
                          'Hops': 'HardOps',
                          'builtin.select_box': 'Select Box',
                          'machin3.tool_hyper_cursor': 'Hyper Cursor',
                          'machin3.tool_hyper_cursor_simple': 'Simple Hyper Cursor'}



mirror_props = ['type',
                'merge_threshold',
                'mirror_object',
                'mirror_offset_u',
                'mirror_offset_v',
                'offset_u',
                'offset_v',
                'show_expanded',
                'show_in_editmode',
                'show_on_cage',
                'show_render',
                'show_viewport',
                'use_axis',
                'use_bisect_axis',
                'use_bisect_flip_axis',
                'use_clip',
                'use_mirror_merge',
                'use_mirror_u',
                'use_mirror_v',
                'use_mirror_vertex_groups']
