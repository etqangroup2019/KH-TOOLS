bl_info = {
    "name": "KH-Top View & Filter",
    "author": "Khaled Alnwesary",
    "version": (1, 47),
    "blender": (3, 00, 0),
    "location": "OUTLINER > HT",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "KH",
}

import bpy
import os
from bpy.utils import previews
from bpy.utils import register_class, unregister_class

class SelectCollectionObjects(bpy.types.Operator):
    bl_idname = "object.select_collection_objects"
    bl_label = ""
    collection_name : bpy.props.StringProperty(name="Collection Name")
    def execute(self, context):
        bpy.ops.outliner.collection_objects_select()            
        return {'FINISHED'}
        
def toggle_top_view(self, context):
    space = context.space_data
    if self.top_view:
        #if space.shading.type != 'WIREFRAME':
            # Change the display interface to be of type 'TOP'
        space.shading.type = 'WIREFRAME'
        bpy.ops.view3d.view_axis(type='TOP')
        # Enable Lock View for the view (region_3d)
        space.region_3d.lock_rotation = True
    else:
        space.shading.type = 'SOLID'
        space.region_3d.lock_rotation = False
        bpy.ops.view3d.view_persportho()
        
        
        
#def draw_lock_camera_option(self, context):
    #layout = self.layout
    #space_data = context.space_data
    
    #layout.prop(space_data, "lock_camera", text="Lock", icon='OUTLINER_OB_CAMERA')


        
# إنشاء أوبريتر مخصص لوظيفة SMART UV مع تطبيق Scale وRotation
class SmartUVOperator(bpy.types.Operator):
    bl_idname = "object.smart_uv"
    bl_label = "S-UV"
    @classmethod
    def poll(cls, context):
        return not bpy.context.mode == 'EDIT_MESH'

    def execute(self, context):
        # الحصول على جميع الكائنات المحددة من نوع MESH
        selected_mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected_mesh_objects:
            # إذا لم يكن هناك كائنات محددة، استخدم الكائن النشط
            obj = context.object
            if obj and obj.type == 'MESH':
                selected_mesh_objects = [obj]

        if selected_mesh_objects:
            # إلغاء تحديد جميع الكائنات أولاً
            bpy.ops.object.select_all(action='DESELECT')

            for obj in selected_mesh_objects:
                # تعيين الكائن كنشط ومحدد
                context.view_layer.objects.active = obj
                obj.select_set(True)

                # التحقق من وجود mesh data مشترك مع كائنات أخرى
                if obj.data.users > 1:
                    # جعل الـ mesh data منفصل لهذا الكائن
                    try:
                        bpy.ops.object.make_single_user(object=False, obdata=True, material=False, animation=False)
                        print(f"تم فصل mesh data للكائن: {obj.name}")
                    except RuntimeError as e:
                        print(f"خطأ في فصل mesh data للكائن {obj.name}: {e}")

                # تطبيق Scale وRotation على الكائن
                try:
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                    print(f"تم تطبيق التحويلات على الكائن: {obj.name}")
                except RuntimeError as e:
                    print(f"خطأ في تطبيق التحويلات على {obj.name}: {e}")

                # تطبيق Smart UV mapping
                try:
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.uv.smart_project()
                    bpy.ops.object.editmode_toggle()
                    print(f"تم تطبيق Smart UV mapping على الكائن: {obj.name}")
                except RuntimeError as e:
                    print(f"خطأ في تطبيق Smart UV mapping على {obj.name}: {e}")
                    # التأكد من العودة إلى Object mode في حالة حدوث خطأ
                    if context.mode == 'EDIT_MESH':
                        bpy.ops.object.editmode_toggle()

                # إلغاء تحديد الكائن الحالي قبل الانتقال للتالي
                obj.select_set(False)

        return {'FINISHED'}

# إنشاء أوبريتر مخصص لوظيفة CUBE UV مع تطبيق Scale وRotation
class CubeUVOperator(bpy.types.Operator):
    bl_idname = "object.cube_uv"
    bl_label = "C-UV"
    @classmethod
    def poll(cls, context):
        return not bpy.context.mode == 'EDIT_MESH'

    def execute(self, context):
        # الحصول على جميع الكائنات المحددة من نوع MESH
        selected_mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected_mesh_objects:
            # إذا لم يكن هناك كائنات محددة، استخدم الكائن النشط
            obj = context.object
            if obj and obj.type == 'MESH':
                selected_mesh_objects = [obj]

        if selected_mesh_objects:
            # إلغاء تحديد جميع الكائنات أولاً
            bpy.ops.object.select_all(action='DESELECT')

            for obj in selected_mesh_objects:
                # تعيين الكائن كنشط ومحدد
                context.view_layer.objects.active = obj
                obj.select_set(True)

                # التحقق من وجود mesh data مشترك مع كائنات أخرى
                if obj.data.users > 1:
                    # جعل الـ mesh data منفصل لهذا الكائن
                    try:
                        bpy.ops.object.make_single_user(object=False, obdata=True, material=False, animation=False)
                        print(f"تم فصل mesh data للكائن: {obj.name}")
                    except RuntimeError as e:
                        print(f"خطأ في فصل mesh data للكائن {obj.name}: {e}")

                # تطبيق Scale وRotation على الكائن
                try:
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                    print(f"تم تطبيق التحويلات على الكائن: {obj.name}")
                except RuntimeError as e:
                    print(f"خطأ في تطبيق التحويلات على {obj.name}: {e}")

                # تطبيق UV mapping
                try:
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.uv.cube_project(cube_size=3)
                    bpy.ops.object.editmode_toggle()
                    print(f"تم تطبيق UV mapping على الكائن: {obj.name}")
                except RuntimeError as e:
                    print(f"خطأ في تطبيق UV mapping على {obj.name}: {e}")
                    # التأكد من العودة إلى Object mode في حالة حدوث خطأ
                    if context.mode == 'EDIT_MESH':
                        bpy.ops.object.editmode_toggle()

                # إلغاء تحديد الكائن الحالي قبل الانتقال للتالي
                obj.select_set(False)

        return {'FINISHED'}




# Create custom operator for CUBE UV function
class FullscreenOperator(bpy.types.Operator):
    bl_idname = "object.fullscreen"
    bl_label = "full"
    def execute(self, context):
        bpy.ops.wm.window_fullscreen_toggle()
        bpy.ops.screen.screen_full_area()
        return {'FINISHED'}
    
# ASSETS
class AssetOperator(bpy.types.Operator):
    bl_idname = "object.asset"
    bl_label = "Asset"
    def execute(self, context):
        bpy.ops.wm.window_new()
        bpy.context.area.ui_type = 'ASSETS'
        bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5, cursor=(0, 0))

        bpy.context.area.ui_type = 'UV'
        bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.1, cursor=(0, 0))

        bpy.context.area.ui_type = 'ShaderNodeTree'
        bpy.context.space_data.show_region_ui = False
        bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5, cursor=(0, 0))
        

        bpy.context.area.ui_type = 'PROPERTIES'
        bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.5, cursor=(0, 0))
        bpy.context.area.ui_type = 'OUTLINER'
        bpy.context.space_data.show_restrict_column_render = True
        bpy.context.space_data.show_restrict_column_viewport = True
        bpy.context.space_data.show_restrict_column_select = True
        bpy.context.space_data.show_restrict_column_enable = False


        


        
        
        return {'FINISHED'}
    


        
# Realtime
script_dir = os.path.dirname(os.path.abspath(__file__))
my_icons_dir = os.path.join(script_dir, "icons")
preview_collection4 = bpy.utils.previews.new()
preview_collection4.load("w.png", os.path.join(my_icons_dir, "w.png"), 'IMAGE')
class Realtime(bpy.types.Operator):
    bl_idname = "object.realtime"
    bl_label = "Realtime"
    bl_description = "Realtime VIEW 3D"
    def execute(self, context):
        if bpy.context.scene.camera is not None:
            bpy.ops.wm.window_new()
            bpy.context.area.ui_type = 'VIEW_3D'
            bpy.ops.screen.screen_full_area(use_hide_panels=True)
            bpy.context.space_data.shading.type = 'RENDERED'
            bpy.context.space_data.overlay.show_overlays = False
            bpy.context.space_data.show_gizmo_context = False

            #bpy.context.space_data.show_gizmo = False
            bpy.context.space_data.show_gizmo_tool = False
            bpy.context.space_data.show_region_ui = False
            bpy.context.scene.camera.select_set(True)
            bpy.context.view_layer.objects.active = bpy.context.scene.camera
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.spaces.active.region_3d.view_perspective = 'CAMERA'
                    break
            space = context.space_data
            space.region_3d.lock_rotation = True
        return {'FINISHED'}

class VIEW3D_OT_view_all_operator(bpy.types.Operator):
    bl_idname = "view3d.view_all_operator"
    bl_label = "View All Image"

    def execute(self, context):
        bpy.ops.image.view_all(fit_view=True)
        return {'FINISHED'}
    


preview_collection = bpy.utils.previews.new()
preview_collection.load("26.png", os.path.join(my_icons_dir, "26.png"), 'IMAGE')

class import_skp(bpy.types.Operator):
    bl_idname = "view3d.import_skp"
    bl_label = "SKP"

    def execute(self, context):
        # لم يعد هناك حاجة لهذا الكلاس - تم نقل الوظيفة إلى sketchup_script()
        # يتم الآن التعامل مع الاستيراد تلقائياً عبر timer
        print("SKP | Import is now handled automatically")
        return {'FINISHED'}
    
preview_collection2 = bpy.utils.previews.new()
preview_collection2.load("7.png", os.path.join(my_icons_dir, "7.png"), 'IMAGE')

class import_setup(bpy.types.Operator):
    bl_idname = "view3d.import_setup"
    bl_label = "Setup"

    def execute(self, context):
        bpy.ops.object.skp_addonn()
        return {'FINISHED'}
    

preview_collection1 = bpy.utils.previews.new()
preview_collection1.load("27.png", os.path.join(my_icons_dir, "27.png"), 'IMAGE')

class update_skp(bpy.types.Operator):
    bl_idname = "view3d.update_skp"
    bl_label = "SKP"

    def execute(self, context):
        # لم يعد هناك حاجة لهذا الكلاس - تم نقل الوظيفة إلى update_script()
        # يتم الآن التعامل مع التحديث تلقائياً عبر timer
        print("SKP | Update is now handled automatically")
        return {'FINISHED'}
    
preview_collection3 = bpy.utils.previews.new()
preview_collection3.load("10.png", os.path.join(my_icons_dir, "10.png"), 'IMAGE')

class update_setup(bpy.types.Operator):
    bl_idname = "view3d.update_setup"
    bl_label = "Update"

    def execute(self, context):
        bpy.ops.object.skp_update_file()
        return {'FINISHED'}
    
    
    

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print("تم حذف الملف بنجاح")
    else:
        print("الملف غير موجود")
def main():
    # تحديث اسم الملف الجديد
    file_path = os.path.join(os.path.expanduser("~"), "Documents", "sketchup_import_data.txt")
    delete_file(file_path)

def main1():
    # تحديث اسم الملف الجديد
    file_path = os.path.join(os.path.expanduser("~"), "Documents", "sketchup_update_data.txt")
    delete_file(file_path)
    

def draw_callback_px1(self, context):
    KH = context.preferences.addons['KH-Tools'].preferences.KH_TopView == True
    if KH :
        layout = self.layout
        box = layout.box()
        box.prop(context.window_manager, "enable_filter", text="H-Filter")
        if context.window_manager.enable_filter:
            bpy.context.space_data.filter_state = 'VISIBLE'
            bpy.context.space_data.filter_invert = True
        else:
            bpy.context.space_data.filter_state = 'ALL'
    return KH


def draw_top_view(self, context):
    KH = context.preferences.addons['KH-Tools'].preferences.KH_TopView == True
    if KH :
        layout = self.layout
        space = context.space_data
        layout.prop(context.scene, "top_view", text="Top", icon='RESTRICT_VIEW_OFF' if space.region_3d.lock_rotation == True else 'RESTRICT_VIEW_ON')
    return KH

# Add custom icons to 3DVIEWPORT HEADER
def draw_callback_smart(self, context):
    # البحث عن الإضافة في المسارات المختلفة
    try:
        KH = context.preferences.addons['KH-Tools'].preferences.KH_TopView == True
    except KeyError:
        try:
            KH = context.preferences.addons['kh_tools'].preferences.KH_TopView == True
        except KeyError:
            try:
                KH = False
                for addon_name in context.preferences.addons.keys():
                    if 'kh' in addon_name.lower() or 'tools' in addon_name.lower():
                        addon = context.preferences.addons[addon_name]
                        if hasattr(addon.preferences, 'KH_TopView'):
                            KH = addon.preferences.KH_TopView == True
                            break
            except:
                KH = True
    if KH :
        layout = self.layout
        layout.operator("object.smart_uv", icon='TEXTURE')
        layout.operator("object.cube_uv", icon='FACE_MAPS')
        layout.operator("object.asset", icon='ASSET_MANAGER')
        file_path = os.path.join(os.path.expanduser("~"), "Documents", "sketchup_import_data.txt")
        if os.path.exists(file_path):
            layout.operator("view3d.import_skp",icon_value=preview_collection['26.png'].icon_id)
            
        
        skp_old_exists = False
        for collection in bpy.data.collections:
            if collection.name == "SKP Master":
                skp_old_exists = True
                break   
        file_path1 = os.path.join(os.path.expanduser("~"), "Documents", "sketchup_update_data.txt")
        if os.path.exists(file_path1):
            if skp_old_exists:
                layout.operator("view3d.update_skp",icon_value=preview_collection1['27.png'].icon_id)

        skp_old_exists = False
        for collection in bpy.data.collections:
            if collection.name == "skp":
                skp_old_exists = True
                break
        if skp_old_exists:
            layout.operator("view3d.import_setup",icon_value=preview_collection2['7.png'].icon_id)
            layout.prop(context.scene, "loading_progress", text="Loading", slider=True) 
        skp_old_exists = False
        for collection in bpy.data.collections:
            if collection.name == "skp_old":
                skp_old_exists = True
                break
        if skp_old_exists:
            layout.operator("view3d.update_setup",icon_value=preview_collection3['10.png'].icon_id)
            layout.prop(context.scene, "loading_progress", text="Loading", slider=True) 
    return KH

# def draw_callback_px(self, context):
#     KH = context.preferences.addons['KH-Tools'].preferences.KH_TopView == True
#     if KH :
#         layout = self.layout
#         layout.operator("object.select_collection_objects", icon='RESTRICT_SELECT_OFF')
#     return KH

def draw_func(self, context):
    KH = context.preferences.addons['KH-Tools'].preferences.KH_TopView == True
    if KH :
        layout = self.layout
        layout.operator("view3d.view_all_operator", text="View All", icon="FULLSCREEN_ENTER")
    return KH

def draw_callback_realtime(self, context):
    # البحث عن الإضافة في المسارات المختلفة
    try:
        KH = context.preferences.addons['KH-Tools'].preferences.KH_TopView == True
    except KeyError:
        try:
            KH = context.preferences.addons['kh_tools'].preferences.KH_TopView == True
        except KeyError:
            try:
                KH = False
                for addon_name in context.preferences.addons.keys():
                    if 'kh' in addon_name.lower() or 'tools' in addon_name.lower():
                        addon = context.preferences.addons[addon_name]
                        if hasattr(addon.preferences, 'KH_TopView'):
                            KH = addon.preferences.KH_TopView == True
                            break
            except:
                KH = True
    if KH :
        layout = self.layout
        layout.operator("object.fullscreen", text="" ,icon='FULLSCREEN_ENTER')
        layout.operator("object.realtime",icon_value=preview_collection4['w.png'].icon_id,text="CAM")
    return KH
 
 

classes = ( ## KH-Top View////////////////////////////////////////////////////////////////////////
            SelectCollectionObjects,
            SmartUVOperator,
            CubeUVOperator,
            FullscreenOperator,
            AssetOperator,
            VIEW3D_OT_view_all_operator,
            import_skp,
            import_setup,
            update_skp,
            update_setup,
            Realtime,           
                )

def register():
    for i in classes:
        register_class(i)
    ## KH-Top View////////////////////////////////////////////////////////////////////////
   
    #bpy.types.OUTLINER_HT_header.append(draw_callback_px)
    bpy.types.WindowManager.enable_filter = bpy.props.BoolProperty(default=False)
    bpy.types.OUTLINER_HT_header.append(draw_callback_px1)
    bpy.types.Scene.top_view = bpy.props.BoolProperty(default=False, update=toggle_top_view)
    bpy.types.VIEW3D_MT_editor_menus.append(draw_top_view)
    #bpy.types.VIEW3D_MT_editor_menus.append(draw_lock_camera_option) 
    bpy.types.VIEW3D_MT_editor_menus.append(draw_callback_smart)
    bpy.types.IMAGE_HT_header.prepend(draw_func)
    bpy.types.VIEW3D_HT_header.append(draw_callback_realtime)
        


def unregister():
    for i in classes:
        unregister_class(i)
    ## KH-Top View////////////////////////////////////////////////////////////////////////
    # التحقق من وجود الخصائص قبل حذفها لتجنب الأخطاء
    #bpy.types.OUTLINER_HT_header.remove(draw_callback_px)
    if hasattr(bpy.types.WindowManager, 'enable_filter'):
        del bpy.types.WindowManager.enable_filter
    bpy.types.OUTLINER_HT_header.remove(draw_callback_px1)
    if hasattr(bpy.types.Scene, 'top_view'):
        del bpy.types.Scene.top_view
    bpy.types.VIEW3D_MT_editor_menus.remove(draw_top_view)
    #bpy.types.VIEW3D_MT_editor_menus.remove(draw_lock_camera_option)
    bpy.types.VIEW3D_MT_editor_menus.remove(draw_callback_smart)
    bpy.types.IMAGE_HT_header.remove(draw_func)
    bpy.types.VIEW3D_HT_header.remove(draw_callback_realtime)



if __name__ == "__main__":
    try:
        register()
    except:
        pass
    unregister() 
