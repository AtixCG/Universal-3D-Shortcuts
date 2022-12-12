<img width="1009" alt="Universal 3D Shortcuts" src="https://user-images.githubusercontent.com/112505578/207167305-13273872-59d7-4095-b2d2-735ed4c38b28.png">




Universal 3D Shortcuts are designed to unify the experience with 3D programs and allow you to focus on solving a problem without the distraction of changing programs. No matter which one you use, you'll have the same navigation and keyboard shortcuts. Where possible, the original hotkeys have not been changed. For each program 200-300 keyboard shortcuts have been considered/changed.

>⚡️Currently supported: Blender, Maya, Cinema 4D

## Command Reference

The document containing the list of keyboard shortcuts can be used as a Command Reference to find the same command between 3D programs.

## Download

S

## Possible Issues

This project was made and tested by me alone, so mistakes are possible. The most complex and problematic integration of hotkeys was in Blender, so the probability of problems there is the highest. 

The keyboard shortcuts are tested on the following program versions:
* Maya 2023.2
* Cinema 4D 2023
* Blender 3.4

## Installation

### Maya
1. Copy the files in the "Marking Menus" folder and paste them to `Documents\maya\YOUR MAYA VERSION\prefs\markingMenus`
2. In Maya go to: Windows -> Settings/Preferences -> Hotkey Editor
3. Click on ![setting](https://user-images.githubusercontent.com/112505578/207167397-4e52a0c5-6911-41f6-9bcc-382b6932c21c.png)
 icon and then "Import"
4. Select "Universal.mhk" in downloaded folder

### Cinema 4D
1. Copy all files in downloaded Scripts folder and paste them to: 
`%AppData%\Maxon\YOUR CINEMA 4D VERSION\library\scripts`
2. (Optional) Install [Drop to Floor](https://www.alphapixel.net/drop-to-floor/) by Alpha Pixel
3. In Cinema4D go to: Windows -> Command Manager -> File -> Load
4. Select "Universal.res" in downloaded folder

### Blender (With Addons)
In this case, the missing functionality of Blender is augmented with the help of the third-party addons. 

1. Copy the files in the "With Addons" folder and paste them to: 
`%USERPROFILE%\AppData\Roaming\Blender Foundation\Blender\YOUR BLENDER VERSION`

> :warning: **WARNING. This method will overwrite your Blender preferences. And restarting some addons may break shortcuts associated with the addon. You might want to create a backup before replacing files.**

### Blender (Without Addons)
In this case, no addons will be used for installation.

1. In Blender go to: Blender Preferences -> Keymap -> Import
2. Select "Universal_WO_Addons.py" in downloaded folder


## With Addons vs Without Addons
### With Addons
The version with addons contains the following addons:
* Align Tools (Built-In)
* Pie Menus (Built-In)
* [AutoDelete](https://blenderartists.org/t/auto-delete/678815/1) by Darcvizer 
* [Drop It](https://andreasaust.gumroad.com/l/drop_it) by AndreasAustPMX
* [MACHIN3tools](https://machin3.gumroad.com/l/MACHIN3tools) by machin3
* [MaterialUtilities](https://github.com/ChrisHinde/MaterialUtilities) by ChrisHinde 
* [Merge Tool](https://github.com/Stromberg90/Scripts/tree/master/Blender) by Stromberg90 
* Separate Objects by Me
* [Toggle Hide](https://github.com/K-410/blender-scripts/blob/master/2.8/toggle_hide.py) by K-410
* [X-Ray Selection](https://blenderartists.org/t/x-ray-selection-tools/1212316) Tools by Cirno 

> Note: If you are the developer of any of these addons and do not want it to be used, please contact me.
#### Updating Addons
You can install updates for addons, but you will probably need to configure the associated hotkeys.

### Without Addons
**:x: The following commands and keyboard shortcuts are missing in the version without addons:**
Command|Shortcut
----|----
Assign New Material|Alt-A
Group|Ctrl-G
Ungroup|Shift-G
Drop It|Ctrl-Alt-Shift-Z
Assign Default Material|Ctrl-Alt-Shift-L
Set Pivot to Bottom|Ctrl-Shift-C
Mirror|Alt-Shift-M
Merge Tool|Ctrl-W
Sculpting menu (Sculpt Mode)|W

**:recycle:	These shortcuts hanged to built-in commands:**
Command|Shortcut
----|----
Select|D
Delete|X
Hide|H
Clean Up|Shift-Alt-D
Separate|Ctrl-Alt-Shift-S
