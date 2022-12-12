from typing import Optional
import c4d

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:

    bd = doc.GetActiveBaseDraw()
    cam=bd.GetSceneCamera(doc)
    cam[c4d.CAMERA_FOCUS]=cam[c4d.CAMERAOBJECT_APERTURE]
    c4d.EventAdd()

if __name__ == '__main__':
    main()