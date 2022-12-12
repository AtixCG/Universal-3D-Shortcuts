from typing import Optional
import c4d
from c4d.modules import snap

doc: c4d.documents.BaseDocument  # The active document
op: Optional[c4d.BaseObject]  # The active object, None if unselected

def main() -> None:
    bc = doc.GetSettingsInstance(c4d.DOCUMENTSETTINGS_MODELING)

    point=c4d.IsCommandChecked((c4d.SNAPMODE_POINT))

    edge=c4d.IsCommandChecked((c4d.SNAPMODE_EDGE))

    polygon=c4d.IsCommandChecked((c4d.SNAPMODE_POLYGON))

    spline=c4d.IsCommandChecked((c4d.SNAPMODE_SPLINE))

    axis=c4d.IsCommandChecked((c4d.SNAPMODE_AXIS))

    inter=c4d.IsCommandChecked((c4d.SNAPMODE_INTERSECTION))

    midpoint=c4d.IsCommandChecked((c4d.SNAPMODE_MIDPOINT))

    workplane=c4d.IsCommandChecked((c4d.SNAPMODE_WORKPLANE))

    guide=c4d.IsCommandChecked((c4d.SNAPMODE_GUIDE))

    data = c4d.BaseContainer()
    en = data[c4d.SNAP_SETTINGS_ENABLED]
    if edge == 1:
        if en == 0:
            data[c4d.SNAP_SETTINGS_ENABLED] = 1
        else:
            data[c4d.SNAPMODE_EDGE] = 0
            if point == 0 and polygon == 0 and spline == 0 and axis == 0 and inter == 0 and midpoint==0 and workplane == 0 and guide == 0:
                data[c4d.SNAP_SETTINGS_ENABLED] = 0
    else:
        data[c4d.SNAP_SETTINGS_ENABLED] = 1
        data[c4d.SNAPMODE_EDGE]=1

    snap.SetSnapSettings(doc, data)
    c4d.EventAdd()

if __name__ == '__main__':
    main()