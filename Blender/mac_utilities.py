import sys
def optimize_for_mac(keyconfig_data):
    # check platform
    if sys.platform == "darwin":
        for keyGroup in keyconfig_data:
            # get key binding items
            keyItems = keyGroup[2]["items"]
            for keyItem in keyItems:
                keyDef = keyItem[1]
                if "ctrl" in keyDef:
                    keyDef["oskey"] = keyDef.pop("ctrl")