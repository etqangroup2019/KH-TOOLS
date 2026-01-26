import bpy
import bpy.types
from bpy.utils import register_class, unregister_class
from .rename import *
from .move import *
from .clear import *
from .settings import *
from .preview import *

bl_info = {
    "name": "Asset Tools",
    "author": "Johnny Matthews",
    "location": "Asset Viewer - Right Click Menu",
    "version": (1, 7),
    "blender": (4, 0, 0),
    "description": "A set of tools for managing multiple assets at the same time",
    "doc_url": "",
    "category": "Assets"
}


classes = (
    khAssetToolsPreferences,
    kh_OT_MoveOperator,
    kh_OT_RenameOperator,
    kh_OT_ClearOperator,
    kh_OT_PreviewOperator,

)
             
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(kh_MT_move_menu_func)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(kh_MT_rename_menu_func)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(kh_MT_clear_menu_func)
    


def unregister():
    for cls in (classes):
        bpy.utils.unregister_class(cls)
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(kh_MT_move_menu_func)
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(kh_MT_rename_menu_func)
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(kh_MT_clear_menu_func)

    

if __name__ == "__main__":
    register()
