"""
SketchUp Drag & Drop Import Module for KH-Tools
Enables drag and drop functionality for .skp files in Blender
"""

import bpy
import os

class SKP_Drop_Importer(bpy.types.Operator):
    """Import SketchUp files via drag and drop with settings dialog"""
    bl_idname = "wm.skp_drop_importer"
    bl_label = "Import SKP via KH TOOLS"
    bl_description = "Import SketchUp (.skp) files using KH-Tools importer"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Path to the SketchUp file",
        subtype="FILE_PATH"
    )

    def execute(self, context):
        # التحقق من وجود KH TOOLS import operator
        if not hasattr(bpy.ops.import_scene, 'skp_k'):
            self.report({'ERROR'}, "KH TOOLS SketchUp importer is not available! Make sure KH-Tools addon is enabled.")
            return {'CANCELLED'}

        # التحقق من صحة الملف
        if not os.path.exists(self.filepath):
            self.report({'ERROR'}, f"File does not exist: {self.filepath}")
            return {'CANCELLED'}

        if not self.filepath.lower().endswith('.skp'):
            self.report({'ERROR'}, "File is not a SketchUp (.skp) file!")
            return {'CANCELLED'}

        # استدعاء مستورد KH-Tools مع نافذة الإعدادات
        try:
            # استدعاء الأوبيراتور مع 'INVOKE_DEFAULT' لإظهار نافذة الإعدادات
            bpy.ops.import_scene.skp_k('INVOKE_DEFAULT', filepath=self.filepath)

            filename = os.path.basename(self.filepath)
            self.report({'INFO'}, f"Import dialog opened for: {filename}")

        except Exception as e:
            self.report({'ERROR'}, f"Failed to open import dialog: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}


class SKP_FileDropHandler(bpy.types.FileHandler):
    """File handler for SketchUp files drag and drop"""
    bl_idname = "SKP_FH_import"
    bl_label = "Import SketchUp"
    bl_import_operator = "wm.skp_drop_importer"
    bl_file_extensions = ".skp"

    @classmethod
    def poll_drop(cls, context):
        """Check if we can handle the dropped files"""
        return (context.area and 
                context.area.type in {'VIEW_3D', 'OUTLINER', 'PROPERTIES'})


class SKP_DragDropPanel(bpy.types.Panel):
    """Panel to show drag & drop status"""
    bl_label = "Drag & Drop"
    bl_idname = "VIEW3D_PT_skp_drag_drop"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KH-Tools"
    bl_parent_id = "OBJECT_PT_copy_name_material"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        # إظهار البانل فقط عندما يكون SketchUp Manager مفعل
        # البحث عن الإضافة في المسارات المختلفة
        try:
            KH = context.preferences.addons['KH-Tools'].preferences.KH_Sketchup == True
        except KeyError:
            try:
                KH = context.preferences.addons['kh_tools'].preferences.KH_Sketchup == True
            except KeyError:
                try:
                    KH = False
                    for addon_name in context.preferences.addons.keys():
                        if 'kh' in addon_name.lower() or 'tools' in addon_name.lower():
                            addon = context.preferences.addons[addon_name]
                            if hasattr(addon.preferences, 'KH_Sketchup'):
                                KH = addon.preferences.KH_Sketchup == True
                                break
                except:
                    KH = True
        return KH

    def draw_header(self, context):
        self.layout.label(text="", icon='IMPORT')

    def draw(self, context):
        layout = self.layout

        # حالة السحب والإفلات
        box = layout.box()
        row = box.row()
        if hasattr(bpy.ops.import_scene, 'skp_k'):
            row.label(text="Ready for .skp files", icon='CHECKMARK')
        else:
            row.label(text="KH-Tools importer not found", icon='ERROR')

        # تعليمات الاستخدام
        col = layout.column(align=True)
        col.label(text="How to use:")
        col.label(text="1. Drag .skp file from file explorer")
        col.label(text="2. Drop it on 3D Viewport")
        col.label(text="3. Import settings dialog will open")
        col.label(text="4. Configure settings and click Import")

        # المناطق المدعومة
        layout.separator()
        row = layout.row()
        row.label(text="Drop Zones:", icon='INFO')
        col = layout.column(align=True)
        col.label(text="• 3D Viewport")
        col.label(text="• Outliner")
        col.label(text="• Properties Panel")


# Classes to register
classes = (
    SKP_Drop_Importer,
    SKP_FileDropHandler,
    SKP_DragDropPanel,
)

def register():
    """Register all classes and handlers"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("SketchUp Drag & Drop handler registered successfully")

def unregister():
    """Unregister all classes and handlers"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("SketchUp Drag & Drop handler unregistered")

if __name__ == "__main__":
    register()
