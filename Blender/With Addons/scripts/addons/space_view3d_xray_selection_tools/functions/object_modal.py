from ..preferences import get_preferences


def gather_overlays(context):
    overlays = {
        "show_xray": context.space_data.shading.show_xray,
        "show_xray_wireframe": context.space_data.shading.show_xray_wireframe,
    }
    return overlays


def set_properties(self, tool):
    if not self.override_global_props:
        self.show_xray = get_preferences().ob_show_xray
        self.xray_toggle_key = get_preferences().ob_xray_toggle_key
        self.xray_toggle_type = get_preferences().ob_xray_toggle_type
        match tool:
            case 'BOX':
                self.show_crosshair = get_preferences().ob_show_crosshair
                self.behavior = self.curr_behavior = get_preferences().ob_box_select_behavior
            case 'CIRCLE':
                self.behavior = self.curr_behavior = get_preferences().ob_circle_select_behavior
            case 'LASSO':
                self.show_lasso_icon = get_preferences().ob_show_lasso_icon
                self.behavior = self.curr_behavior = get_preferences().ob_lasso_select_behavior


def sync_properties(self, context):
    """Sync operator parameters to current context shading. So if xray already enabled
    make sure it would be possible to toggle it regardless of operator parameters."""
    if (
        context.space_data.shading.type in {'SOLID', 'MATERIAL', 'RENDERED'}
        and context.space_data.shading.show_xray
        or context.space_data.shading.type == 'WIREFRAME'
        and context.space_data.shading.show_xray_wireframe
    ):
        self.show_xray = True


def toggle_overlays(self, context):
    if context.space_data.shading.type in {'SOLID', 'MATERIAL', 'RENDERED'}:
        context.space_data.shading.show_xray = self.show_xray
    elif context.space_data.shading.type == 'WIREFRAME':
        context.space_data.shading.show_xray_wireframe = self.show_xray


def restore_overlays(self, context):
    if self.init_overlays:
        context.space_data.shading.show_xray = self.init_overlays["show_xray"]
        context.space_data.shading.show_xray_wireframe = self.init_overlays["show_xray_wireframe"]


def get_xray_toggle_key_list():
    match get_preferences().ob_xray_toggle_key:
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
        event.ctrl and self.alt_mode_toggle_key == 'CTRL'
        or event.alt and self.alt_mode_toggle_key == 'ALT'
        or event.shift and self.alt_mode_toggle_key == 'SHIFT'
    ):
        self.curr_mode = self.alt_mode
    else:
        self.curr_mode = self.mode
