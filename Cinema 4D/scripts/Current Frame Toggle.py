from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    bd = doc.GetActiveBaseDraw()
    old = bd[c4d.BASEDRAW_HUD_FRAME]
    if old == 0:
        bd[c4d.BASEDRAW_HUD_FRAME] = 1
    else:
        bd[c4d.BASEDRAW_HUD_FRAME] = 0
    c4d.EventAdd()

if __name__ == '__main__':
    main()