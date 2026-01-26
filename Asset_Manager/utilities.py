import bpy
import os
from .settings import *

# UI Functions


def kh_tag_callback(self, context):
    tags = {}
    for f in bpy.context.selected_asset_files:
        for tag in f.asset_data.tags:
            tags[tag.name] = True
    output = []
    i = 0
    for tag in tags.keys():
        output.append((tag, tag, "", i))
        i += 1
    return output


def kh_item_callback(self, context):
    if not context or not hasattr(context, "space_data") or not context.space_data or not hasattr(context.space_data, "params"):
        return [("", "Catalog", "", 0)]
    
    directory = context.space_data.params.directory
    d = str(directory).split('\'')
    directory = d[1]
    cat = open(os.path.join(str(directory), "blender_assets.cats.txt"))
    cats = cat.readlines()
    cat.close()

    output = [("", "Catalog", "", 0),
              ("00000000-0000-0000-0000-000000000000", "Unassigned", "", 0)]
    i = 1
    for line in cats:
        if line[0:1] == "#":
            continue
        if line.strip() == "":
            continue
        if line[0:7] == "VERSION":
            continue
        data = line.split(":")
        output.append((data[0], data[1], "", i))
        i += 1
    return output


# Utility Functions

def kh_get_catalog_directory(context):
    if not context or not hasattr(context, "space_data") or not context.space_data or not hasattr(context.space_data, "params"):
        return ""
    catalog = context.space_data.params.catalog_id
    directory = context.space_data.params.directory
    if directory == "b''":
        return ""
    d = str(directory).split('\'')
    return d[1]


def kh_get_file_path(relative_path, directory):
    p = relative_path.split(".blend\\")
    p[0] = p[0]+".blend"
    return os.path.join(directory, p[0])


def kh_id_type_to_type_name(id_type):
    type_out = id_type.lower()+"s"
    if id_type == "NODETREE":
        type_out = "node_groups"
    return type_out


def kh_run_command(path, commands):
    import subprocess
    commandlist = "".join(commands)
    try:
        expr = "import bpy; "+commandlist + \
            " bpy.ops.wm.save_mainfile(); bpy.ops.wm.quit_blender();"
        list = [bpy.app.binary_path]
        if bpy.context.preferences.addons['KH-Tools'].preferences.background == True:
            list.append("-b")
        list.append(path)
        list.append("--python-expr")
        list.append(expr)
        subprocess.run(list)
    except:
        print("Error on the new Blender instance")


# Catalog utilities for mapping catalog IDs to folder paths
def kh_read_catalog_map(directory):
    cats_path = os.path.join(str(directory), "blender_assets.cats.txt")
    mapping = {}
    try:
        with open(cats_path, 'r', encoding='utf-8', errors='ignore') as cat:
            for line in cat.readlines():
                if not line or line.startswith('#'):
                    continue
                line = line.strip()
                if not line or line.startswith('VERSION'):
                    continue
                data = line.split(":")
                if len(data) < 2:
                    continue
                mapping[data[0]] = data[1]
    except Exception:
        pass
    return mapping


def kh_catalog_id_to_rel_path(directory, catalog_id):
    mapping = kh_read_catalog_map(directory)
    label_path = mapping.get(catalog_id, "Unassigned")
    label_path = label_path.strip()
    if label_path == "":
        return ""
    # Normalize to OS-specific separators
    rel_dir = label_path.replace("\\", "/").strip("/").replace("/", os.sep)
    return rel_dir


def kh_ensure_dir(root_dir, rel_dir):
    target_dir = os.path.join(root_dir, rel_dir) if rel_dir else str(root_dir)
    try:
        os.makedirs(target_dir, exist_ok=True)
    except Exception:
        pass
    return target_dir


def kh_path_for_blender(path):
    # Use forward slashes so Blender on Windows reads paths without escaping
    return str(path).replace("\\", "/")


def kh_py_string_literal(value):
    s = str(value)
    s = s.replace('\\', r'\\')
    s = s.replace("'", r"\'")
    return s