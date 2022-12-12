from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    bd = doc.GetActiveBaseDraw()
    old = bd[c4d.BASEDRAW_HUD_DRAW_STATISTICS]
    if old == 0:
        bd[c4d.BASEDRAW_HUD_DRAW_STATISTICS] = 1
    else:
        bd[c4d.BASEDRAW_HUD_DRAW_STATISTICS] = 0
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()