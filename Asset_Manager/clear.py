import bpy
import os
from .utilities import *
from .base_operator_class import kh_BaseBulkOperator

class kh_OT_ClearOperator(kh_BaseBulkOperator):
    """Bulk Clear Asset"""
    bl_idname = "asset.kh_bulk_clear_asset"
    bl_label = "Clear"
    bl_options = {"REGISTER"}

    def draw(self, context):
        num = len(bpy.context.selected_assets)
        self.layout.label(icon='ERROR', text="This will clear " +
                          str(num)+" assets with NO UNDO. ")
        self.layout.label(text="Press ESC to cancel")

    def main(self, context):
        directory = kh_get_catalog_directory(context)
        for f in bpy.context.selected_assets:
            if f.local_id == None:
                path = f.full_library_path
                type_out = kh_id_type_to_type_name(f.id_type)
                if path not in self.commands.keys():
                    self.commands[path] = []
                self.commands[path].append(
                    "bpy.data."+type_out+"['"+f.name+"'].asset_clear();")
            else:
                f.local_id.asset_clear()


def kh_MT_clear_menu_func(self, context):
    KH = context.preferences.addons['KH-Tools'].preferences.Asset_Maker == True
    if KH :
        layout=self.layout
        row=layout.row(align=True)
        row.operator('asset.kh_bulk_clear_asset',text='Clear',icon='TRASH')
        # self.layout.operator_context = 'INVOKE_DEFAULT'
        # self.layout.operator(ASSET_OT_ClearOperator.bl_idname,text=ASSET_OT_ClearOperator.bl_label)
