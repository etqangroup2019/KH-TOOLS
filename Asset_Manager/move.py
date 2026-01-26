import bpy
import os
from .utilities import *
from .base_operator_class import kh_BaseBulkOperator

class kh_OT_MoveOperator(kh_BaseBulkOperator):
    """Move Assets to a Catalog"""
    bl_idname = "asset.kh_bulk_asset_mover"
    bl_label = "Asset Mover"
    bl_options = {"REGISTER"}

    catalog: bpy.props.EnumProperty(
        name="Destination Catalog", items=kh_item_callback)

    def main(self, context):
        directory = kh_get_catalog_directory(context)
        dest_rel_dir = kh_catalog_id_to_rel_path(directory, self.catalog)
        dest_root_dir = kh_ensure_dir(directory, dest_rel_dir)

        for f in bpy.context.selected_assets:
            # Determine source info
            if f.local_id is None:
                source_blend_path = f.full_library_path
                id_type_plural = kh_id_type_to_type_name(f.id_type)
                asset_name = f.name

                if source_blend_path not in self.commands.keys():
                    self.commands[source_blend_path] = []

                # Build destination .blend file path (per-asset file under dest directory)
                dest_blend_path = os.path.join(dest_root_dir, asset_name + ".blend")
                dest_blend_path_bpy = kh_path_for_blender(dest_blend_path)

                # Python expr to run in child Blender:
                # - open a new temp file
                # - append the asset from source_blend_path
                # - set catalog
                # - save to dest_blend_path
                # - remove from source and save source
                src_path_bpy = kh_path_for_blender(source_blend_path)

                cmd = (
                    "import bpy; import os; "
                    f"src='{kh_py_string_literal(src_path_bpy)}'; "
                    f"dst='{kh_py_string_literal(dest_blend_path_bpy)}'; "
                    f"id_type='{kh_py_string_literal(id_type_plural)}'; "
                    f"name='{kh_py_string_literal(asset_name)}'; "
                    f"cat='{kh_py_string_literal(self.catalog)}'; "
                    # Append into an empty file and save
                    "bpy.ops.wm.read_homefile(use_empty=True); "
                    "lib=bpy.data.libraries.load(src, link=False); df,dt=lib.__enter__(); setattr(dt, id_type, [name]); lib.__exit__(None,None,None); "
                    "obj = getattr(bpy.data, id_type).get(name); "
                    "(obj and getattr(obj, 'asset_data', None)) and setattr(obj.asset_data, 'catalog_id', cat); "
                    "bpy.ops.wm.save_as_mainfile(filepath=dst); "
                    # Now open source, remove, and save
                    "bpy.ops.wm.open_mainfile(filepath=src); "
                    "db = getattr(bpy.data, id_type); tmp=db.get(name); tmp and db.remove(tmp); "
                    "bpy.ops.wm.save_mainfile(); "
                )

                self.commands[source_blend_path].append(cmd)
            else:
                # Local asset in current file: create new file and move
                id_type_plural = kh_id_type_to_type_name(f.id_type)
                asset_name = f.name
                dest_blend_path = os.path.join(dest_root_dir, asset_name + ".blend")
                dest_blend_path_bpy = kh_path_for_blender(dest_blend_path)

                # Save current to temp path for loading
                current_path = bpy.data.filepath
                if current_path == "":
                    # Skip unsaved current files
                    continue

                src_path_bpy = kh_path_for_blender(current_path)

                if current_path not in self.commands.keys():
                    self.commands[current_path] = []

                cmd = (
                    "import bpy; "
                    f"src='{kh_py_string_literal(src_path_bpy)}'; "
                    f"dst='{kh_py_string_literal(dest_blend_path_bpy)}'; "
                    f"id_type='{kh_py_string_literal(id_type_plural)}'; "
                    f"name='{kh_py_string_literal(asset_name)}'; "
                    f"cat='{kh_py_string_literal(self.catalog)}'; "
                    "bpy.ops.wm.read_homefile(use_empty=True); "
                    "lib=bpy.data.libraries.load(src, link=False); df,dt=lib.__enter__(); setattr(dt, id_type, [name]); lib.__exit__(None,None,None); "
                    "obj = getattr(bpy.data, id_type).get(name); "
                    "(obj and getattr(obj, 'asset_data', None)) and setattr(obj.asset_data, 'catalog_id', cat); "
                    "bpy.ops.wm.save_as_mainfile(filepath=dst); "
                    "bpy.ops.wm.open_mainfile(filepath=src); "
                    "db = getattr(bpy.data, id_type); tmp=db.get(name); tmp and db.remove(tmp); "
                    "bpy.ops.wm.save_mainfile(); "
                )

                self.commands[current_path].append(cmd)

# def ASSET_MT_move_menu_func(self, context):
#     self.layout.operator_context = 'INVOKE_DEFAULT'
#     self.layout.operator(ASSET_OT_MoveOperator.bl_idname,text=ASSET_OT_MoveOperator.bl_label)
    
def kh_MT_move_menu_func(self, context):
    KH = context.preferences.addons['KH-Tools'].preferences.Asset_Maker == True
    if KH :
        layout=self.layout
        row=layout.row(align=True)
        row.operator('asset.kh_bulk_asset_mover',text='Move',icon='ASSET_MANAGER')
        row = layout.row(align=True)
        op = row.operator('asset.kh_bulk_preview_generate', text='Preview', icon='FILE_IMAGE')
        op.use_image_render = True
