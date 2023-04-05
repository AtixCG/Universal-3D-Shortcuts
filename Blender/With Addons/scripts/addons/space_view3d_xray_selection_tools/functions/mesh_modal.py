from ..preferences import get_preferences


def gather_overlays(context):
    overlays = {
        "show_xray": context.space_data.shading.show_xray,
        "xray_alpha": context.space_data.shading.xray_alpha,
        "show_xray_wireframe": bool(context.space_data.shading.show_xray_wireframe),
        "xray_alpha_wireframe": bool(context.space_data.shading.xray_alpha_wireframe),
        "backwire_opacity": context.space_data.overlay.backwire_opacity,
    }
    return overlays


def gather_modifiers(self, context):
    mods = []
    mods_to_hide = []

    if self.hide_mirror:
        mods_to_hide.append('MIRROR')
    if self.hide_solidify:
        mods_to_hide.append('SOLIDIFY')

    sel_obs = context.selected_objects if context.selected_objects else [context.object]
    for ob in sel_obs:
        mods.extend([(m, m.show_in_editmode) for m in ob.modifiers if m.type in mods_to_hide])
    return mods


def set_properties_from_preferences(self, tool):
    dirs_props = get_preferences().me_direction_properties

    if not self.override_global_props:
        if self.directional:  # for initial shading before direction is determined
            self.select_through = dirs_props[0].select_through and dirs_props[1].select_through
            self.show_xray = dirs_props[0].show_xray and dirs_props[1].show_xray and self.select_through
        else:
            self.select_through = get_preferences().me_select_through
            self.default_color = get_preferences().me_default_color
            self.select_through_color = get_preferences().me_select_through_color
            self.show_xray = get_preferences().me_show_xray
            self.select_all_edges = get_preferences().me_select_all_edges
            self.select_all_faces = get_preferences().me_select_all_faces

        self.select_through_toggle_key = get_preferences().me_select_through_toggle_key
        self.select_through_toggle_type = get_preferences().me_select_through_toggle_type
        self.hide_mirror = get_preferences().me_hide_mirror
        self.hide_solidify = get_preferences().me_hide_solidify
        match tool:
            case 'BOX':
                self.show_crosshair = get_preferences().me_show_crosshair
            case 'LASSO':
                self.show_lasso_icon = get_preferences().me_show_lasso_icon


def initialize_shading_from_properties(self, context):
    shading = context.space_data.shading
    overlay = context.space_data.overlay

    if self.directional:
        # If both directions have prop to show xray turned on
        # enable xray shading for wait for input stage.
        dir_props = get_preferences().me_direction_properties
        if (
            dir_props[0].select_through
            and dir_props[1].select_through
            and dir_props[0].show_xray
            and dir_props[1].show_xray
        ):
            shading.show_xray = True
            shading.show_xray_wireframe = True
    else:
        if self.select_through:
            # Default xray shading should be turned on.
            if self.show_xray:
                shading.show_xray = True
                shading.show_xray_wireframe = True
            # Hidden xray shading should be turned on to select through if default xray shading is off.
            if not self.override_intersect_tests:
                if (
                    shading.type in {'SOLID', 'MATERIAL', 'RENDERED'}
                    and not shading.show_xray
                    or shading.type == 'WIREFRAME'
                    and not shading.show_xray_wireframe
                ):
                    shading.show_xray = True
                    shading.show_xray_wireframe = True
                    shading.xray_alpha = 1  # .5
                    shading.xray_alpha_wireframe = 1  # 0
                    overlay.backwire_opacity = 0  # .5


def set_properties_from_direction(self, direction):
    dir_props = get_preferences().me_direction_properties[direction]
    self.select_through = dir_props.select_through
    self.default_color = dir_props.default_color
    self.select_through_color = dir_props.select_through_color
    self.show_xray = dir_props.show_xray
    self.select_all_edges = dir_props.select_all_edges
    self.select_all_faces = dir_props.select_all_faces


def set_shading_from_properties(self, context):
    """For toggling overlays by hotkey or by changing dragging direction."""
    shading = context.space_data.shading
    overlay = context.space_data.overlay

    # In general avoiding here turning off xray shading and selecting through if xray shading is already enabled.
    if not (self.directional and not self.direction):  # skip toggling until direction is determined
        # Enable xray shading when it is enabled in props.
        if self.show_xray:
            shading.show_xray = True
            shading.show_xray_wireframe = True
        # Return initial xray shading when xray is off in props (don't hide xray when it is already enabled).
        else:
            shading.show_xray = self.init_overlays["show_xray"]
            shading.show_xray_wireframe = self.init_overlays["show_xray_wireframe"]

        # If select through is toggled on in props by direction or by key and intersect tests won't be used
        # enabled hidden xray shading to select through
        # don't use hidden xray shading if default xray shading is already enabled.
        if (
            (
                self.select_through
                and not self.invert_select_through
                or not self.select_through
                and self.invert_select_through
            )
            and not self.override_intersect_tests
            and (
                shading.type in {'SOLID', 'MATERIAL', 'RENDERED'}
                and not shading.show_xray
                or shading.type == 'WIREFRAME'
                and not shading.show_xray_wireframe
            )
        ):
            shading.show_xray = True
            shading.show_xray_wireframe = True
            shading.xray_alpha = 1  # .5
            shading.xray_alpha_wireframe = 1  # 0
            overlay.backwire_opacity = 0  # .5
        else:
            # If hidden xray shading should be off, restore initial overlay opacity.
            shading.xray_alpha = self.init_overlays["xray_alpha"]
            shading.xray_alpha_wireframe = self.init_overlays["xray_alpha_wireframe"]
            overlay.backwire_opacity = self.init_overlays["backwire_opacity"]

        # If select through is toggled off in props by direction or by key
        # return initial xray shading.
        if (not self.select_through and not self.invert_select_through) or (
            self.select_through and self.invert_select_through
        ):
            shading.show_xray = self.init_overlays["show_xray"]
            shading.show_xray_wireframe = self.init_overlays["show_xray_wireframe"]


def set_modifiers_from_properties(self):
    """Hide modifiers in editmode or restore initial visibility."""
    if self.init_mods:
        if self.select_through:
            for mod, show_in_editmode in self.init_mods:
                if mod.show_in_editmode:
                    mod.show_in_editmode = False
        else:
            for mod, show_in_editmode in self.init_mods:
                if mod.show_in_editmode != show_in_editmode:
                    mod.show_in_editmode = show_in_editmode


def restore_overlays(self, context):
    if self.init_overlays:
        context.space_data.shading.show_xray = self.init_overlays["show_xray"]
        context.space_data.shading.xray_alpha = self.init_overlays["xray_alpha"]
        context.space_data.shading.show_xray_wireframe = self.init_overlays["show_xray_wireframe"]
        context.space_data.shading.xray_alpha_wireframe = self.init_overlays["xray_alpha_wireframe"]
        context.space_data.overlay.backwire_opacity = self.init_overlays["backwire_opacity"]


def restore_modifiers(self):
    if self.init_mods:
        for mod, show_in_editmode in self.init_mods:
            if mod.show_in_editmode != show_in_editmode:
                mod.show_in_editmode = show_in_editmode


def get_select_through_toggle_key_list():
    match get_preferences().me_select_through_toggle_key:
        case 'CTRL':
            return {'LEFT_CTRL', 'RIGHT_CTRL'}
        case 'ALT':
            return {'LEFT_ALT', 'RIGHT_ALT'}
        case 'SHIFT':
            return {'LEFT_SHIFT', 'RIGHT_SHIFT'}
        case 'DISABLED':
            return {'DISABLED'}


def toggle_alt_mode(self, event):
    if (
        event.ctrl
        and self.alt_mode_toggle_key == 'CTRL'
        or event.alt
        and self.alt_mode_toggle_key == 'ALT'
        or event.shift
        and self.alt_mode_toggle_key == 'SHIFT'
    ):
        self.curr_mode = self.alt_mode
    else:
        self.curr_mode = self.mode


def update_shader_color(self, context):
    if self.select_through_color != self.default_color:
        context.region.tag_redraw()
