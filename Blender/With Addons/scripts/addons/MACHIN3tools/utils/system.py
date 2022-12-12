import bpy
import os
import sys
import re
from pprint import pprint


enc = sys.getfilesystemencoding()


def abspath(path):
    return os.path.abspath(bpy.path.abspath(path))


def quotepath(path):
    if " " in path:
        path = '"%s"' % (path)
    return path


def add_path_to_recent_files(path):

    try:
        recent_path = bpy.utils.user_resource('CONFIG', path="recent-files.txt")
        with open(recent_path, "r+", encoding=enc) as f:
            content = f.read()
            f.seek(0, 0)
            f.write(path.rstrip('\r\n') + '\n' + content)

    except (IOError, OSError, FileNotFoundError):
        pass


def open_folder(path):
    import platform
    import subprocess

    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        os.system('xdg-open "%s" %s &' % (path, "> /dev/null 2> /dev/null"))  # > sends stdout,  2> sends stderr


def makedir(pathstring):
    if not os.path.exists(pathstring):
        os.makedirs(pathstring)
    return pathstring


def printd(d, name=''):
    print(f"\n{name}")
    pprint(d, sort_dicts=False)


def get_incremented_paths(currentblend):
    path = os.path.dirname(currentblend)
    filename = os.path.basename(currentblend)

    filenameRegex = re.compile(r"(.+)\.blend\d*$")

    mo = filenameRegex.match(filename)

    if mo:
        name = mo.group(1)
        numberendRegex = re.compile(r"(.*?)(\d+)$")

        mo = numberendRegex.match(name)

        if mo:
            basename = mo.group(1)
            numberstr = mo.group(2)
        else:
            basename = name + "_"
            numberstr = "000"

        number = int(numberstr)

        incr = number + 1
        incrstr = str(incr).zfill(len(numberstr))

        incrname = basename + incrstr + ".blend"

        return os.path.join(path, incrname), os.path.join(path, name + '_01.blend')
