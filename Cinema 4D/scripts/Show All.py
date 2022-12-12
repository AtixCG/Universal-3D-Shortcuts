from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    # Called when the plugin is selected by the user. Similar to CommandData.Execute.
    obj = doc.GetObjects()
    for bo in obj:
        bo[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = 2
    c4d.EventAdd()

"""
def state():
    # Defines the state of the command in a menu. Similar to CommandData.GetState.
    return c4d.CMD_ENABLED
"""

if __name__ == '__main__':
    main()