#this is a free addon, you can use, edit and share this addon as you please! If you have any suggestions for the code, please let me know


bl_info = {
    "name" : "KH-ASSET",
    "author" : "",
    "description" : "Place objects, with some randomization",
    "blender" : (2, 81, 0),
    "version" : (1, 2,),
    "location" : "",
    "warning" : "",
    "category" : "KH"
}


#from Asset_Maker import make_asset
import bpy
import random
from bpy_extras import view3d_utils
from mathutils import Vector
from mathutils import Matrix, Vector
import numpy as np
from bpy.utils import previews

from bpy.types import WindowManager

#from .Asset import *

from tabnanny import check
import bpy
import json
import os
import addon_utils
from bpy.types import Operator
from .presets import khModifiers
from bpy.props import StringProperty,EnumProperty,BoolProperty
#from random import random
import time
import subprocess
from pathlib import Path

from .make_asset import *

# دالة مساعدة للبحث عن إعدادات الإضافة
def get_addon_preferences_safe(context):
    """
    البحث عن إعدادات الإضافة في المسارات المختلفة
    """
    try:
        return context.preferences.addons['KH-Tools'].preferences
    except KeyError:
        try:
            return context.preferences.addons['kh_tools'].preferences
        except KeyError:
            try:
                for addon_name in context.preferences.addons.keys():
                    if 'kh' in addon_name.lower() or 'tools' in addon_name.lower():
                        addon = context.preferences.addons[addon_name]
                        if hasattr(addon, 'preferences'):
                            return addon.preferences
            except:
                pass
    return None


def generate_preview_for_saved_material(blend_file_path):
    """
    دالة مساعدة لإنشاء البريفيو للمادة بعد حفظها
    يتم استدعاؤها بشكل منفصل لتجنب تجميد البرنامج
    
    ملاحظة: هذه الدالة اختيارية - Blender سيقوم بإنشاء البريفيو
    تلقائياً عند فتح Asset Browser لأول مرة
    """
    try:
        # فتح الملف المحفوظ
        with bpy.data.libraries.load(str(blend_file_path)) as (data_from, data_to):
            # تحميل المادة
            data_to.materials = data_from.materials
        
        # إنشاء البريفيو للمادة المحملة
        for mat in data_to.materials:
            if mat:
                mat.asset_mark()
                mat.asset_generate_preview()
                
        return True
    except Exception as e:
        print(f"Failed to generate preview: {e}")
        return False


def origin_to_bottom(ob, matrix=Matrix(), use_verts=False):
    """
    moves the origin of the object to the bottom of it's bounding box. This code was shared by the user batFINGER on Blender StackExchange in the post named "Set origin to bottom center of multiple objects"
    """
    me = ob.data
    mw = ob.matrix_world
    if use_verts:
        data = (v.co for v in me.vertices)
    else:
        data = (Vector(v) for v in ob.bound_box)

    coords = np.array([matrix @ v for v in data])
    z = coords.T[2]
    mins = np.take(coords, np.where(z == z.min())[0], axis=0)
    o = Vector(np.mean(mins, axis=0))
    o = matrix.inverted() @ o
    me.transform(Matrix.Translation(-o))
    mw.translation = mw @ o    




def trs():
    selected_objects = bpy.context.selected_objects
    if selected_objects:
        for obj in selected_objects:
            if obj.type == 'MESH':
                if obj.data.users > 1:
                    obj.select_set(False)
                try:
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, isolate_users=False)
                except RuntimeError as e:
                    print("An error occurred:", e)


def trs2():
    if bpy.context.active_object is not None:
        obj = bpy.context.active_object
        if obj.type == 'MESH':
            if obj.data.users > 1:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, isolate_users=True)


class transform_apply(bpy.types.Operator):
    """
    transform apply
    """
    bl_idname = "kh.transform_apply"
    bl_label = "Transform Apply"
    bl_description = "transform applys"
    
    def execute(self, context):    
        try:
            for obj in bpy.context.selected_objects:
                trs()
                trs2()
        #return warning when no objects were selected
        except:
            self.report({'WARNING'}, "No object selected")
        return {'FINISHED'} 
    
    
    
class KH_ORIGIN(bpy.types.Operator):
    """
    moves origin of objects to the bottom of their bounding box
    """
    bl_idname = "kh.origin"
    bl_label = "CLICKR Origin"
    bl_description = "Move origins to bottom of objects"
    
    def execute(self, context):    
        try:
            for obj in bpy.context.selected_objects:
                origin_to_bottom(obj)
        #return warning when no objects were selected
        except:
            self.report({'WARNING'}, "No object selected")
        return {'FINISHED'} 
    


#استيراد مجلد بلندر

class IMPORT_OT_blend_files_operator(bpy.types.Operator):
    bl_idname = "import_blend_files.operator"
    bl_label = "Import Blend Files Operator"

    directory: bpy.props.StringProperty(
        name="Directory",
        description="Directory to import blend files from",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    def execute(self, context):
        directory = self.directory
        if not os.path.isdir(directory):
            self.report({'ERROR'}, "Invalid directory")
            return {'CANCELLED'}

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".blend"):
                    blend_file_path = os.path.join(root, file)
                    self.import_blend_file(blend_file_path)

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def import_blend_file(self, blend_file_path):
        # Use the filename without extension as the collection name
        collection_name = os.path.splitext(os.path.basename(blend_file_path))[0]
        # Create a new collection
        new_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(new_collection)
        
        # Append all objects from the blend file to the new collection
        with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects

        for obj in data_to.objects:
            if obj is not None:
                new_collection.objects.link(obj)
    
# تم نقل Car Motion Blur إلى قائمة Asset الرئيسية
        
        
class kh_ASSET_PANEL(bpy.types.Panel):
    bl_idname = "OBJECT_PT_kh_asset"
    bl_label = "Asset Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "KH-Tools" 
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        pref = get_addon_preferences_safe(context)
        if pref and hasattr(pref, 'Asset_Maker'):
            return pref.Asset_Maker == True
        return True
    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon='ASSET_MANAGER')
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.operator("object.kh_copy_object", text="Copy Object", icon='DUPLICATE')
        row = box.row()
        row.operator("object.bounds_type", text="Low Display" , icon='MESH_ICOSPHERE')
        row.operator("object.textured_display", text="", icon='TRASH')
        box = layout.box()
        row = box.row()
        row.operator("kh.add_curtain", text="Add Curtain", icon='MESH_PLANE')
        #row = box.row()
        row.prop(context.scene, "kh_use_curtain_collection", text="Use Collection")

        # إضافة Car Motion Blur إلى قائمة Asset
        box = layout.box()
        row = box.row()
        row.label(text="Car Motion Blur:", icon='AUTO')
        row = box.row()
        row.operator("object.start_frame", icon='AUTO')
        if context.active_object is not None:
            obj = context.active_object
            if obj.animation_data is not None:
                for fcurve in obj.animation_data.action.fcurves:
                    if fcurve.data_path == "location":
                        row.operator("object.delete_location_keyframes",text="", icon='TRASH')
                        break
        row = box.row()
        row.prop(context.scene, "start_x",text="X")
        row.prop(context.scene, "start_y",text="Y")
        row = box.row()
        row.prop(context.scene.render, "use_motion_blur", text="Motion Blur",icon= "SETTINGS", toggle=True)
        if bpy.context.scene.render.use_motion_blur == True:
            row = box.row()
            row.prop(context.scene.render, "motion_blur_shutter", text="Motion Blur", toggle=True)

        # إضافة High Poly إلى قائمة Asset
        box = layout.box()
        row = box.row()
        row.label(text="High Poly:", icon='MESH_ICOSPHERE')
        row = box.row()
        row.operator("object.high_poly", text="Select High Poly", icon = 'RESTRICT_SELECT_OFF')
        row = box.row()
        row.operator("object.cleanup_segmentation", text="Cleanup", icon = 'BRUSH_DATA')


# قائمة Asset Browser منفصلة
class kh_ASSET_BROWSER_PANEL(bpy.types.Panel):
    bl_idname = "OBJECT_PT_kh_asset_browser"
    bl_label = "Asset Maker"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "KH-Tools"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        pref = get_addon_preferences_safe(context)
        if pref and hasattr(pref, 'Asset_Maker'):
            return pref.Asset_Maker == True
        return True

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon='BLENDER')
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.operator("kh.transform_apply", icon='CHECKMARK')
        row = box.row()
        row.operator("kh.origin", text="Origins to Bottom", icon='DOT')
        row = box.row()
        pref = get_addon_preferences_safe(context)
        if pref.asset_type:
             row.operator("bagapie.kh_saveasset", text= 'Assets Object', icon ='ASSET_MANAGER')
        else:
            row.operator("kh.batch_coll_preview", text= 'Assets Collection')
            row.operator("bagapie.kh_saveasset", text="", icon='EXPORT')
        row = box.row()
        row.operator("KH.savematerial", text="Save Material", icon='ASSET_MANAGER')
        row = box.row()
        row.operator("kh.make_materials_assets", text=" material as Assets", icon='PLUS')
        row.operator("kh.update_materials_list", text="", icon='FILE_REFRESH')

        # قائمة المواد المحددة
        if hasattr(context.scene, 'kh_selected_materials') and len(context.scene.kh_selected_materials) > 0:
            materials_box = layout.box()
            materials_row = materials_box.row()
            materials_row.label(text=f"Materials from Selected Objects ({len(context.scene.kh_selected_materials)}):", icon='MATERIAL')

            # قائمة المواد
            materials_box.template_list(
                "KH_UL_selected_materials_list", "",
                context.scene, "kh_selected_materials",
                context.scene, "kh_selected_materials_index"
            )

        # row = box.row()
        # row.operator("Asset_blend_category.operator", text="Asset Category", icon='GREASEPENCIL')
        row = box.row()
        row.operator("import_blend_files.operator", text="Import Blend Folder", icon='FILE_FOLDER')
        # row.operator("kh.proxy", icon='MESH_ICOSPHERE')
        
#فتح برنامج التصنيف
# class AssetBlendCategoryOperator(bpy.types.Operator):
#     bl_idname = "asset_blend_category.operator"
#     bl_label = "Add Asset Category"
#     bl_description = "Open Blend Asset Category application"
    
#     def execute(self, context):
#         script_dir = os.path.dirname(os.path.realpath(__file__))  # الحصول على مسار السكربت الحالي
#         exe_path = os.path.join(script_dir, "Blend Asset category.exe")  # تحديد مسار التطبيق
        
#         if os.path.exists(exe_path):  # التحقق من وجود التطبيق
#             subprocess.Popen(exe_path, shell=True)  # تشغيل التطبيق
#             self.report({'INFO'}, "Application opened successfully")
#         else:
#             self.report({'ERROR'}, "Blend Asset category.exe not found!")

#         return {'FINISHED'}



def set_font_size(font_id, size, dpi=72):
    import blf
    try:
        # Blender < 4.0 (تقبل 3 وسائط)
        blf.size(font_id, size, dpi)
    except TypeError:
        # Blender >= 4.0 (تقبل وساطين فقط)
        blf.size(font_id, size)

# عامل إضافة الستائر مع النقر على الأسطح
class KH_AddCurtain(bpy.types.Operator):
    """إضافة ستائر بالنقر على الأسطح مع التدوير التلقائي"""
    bl_idname = "kh.add_curtain"
    bl_label = "Add Curtain"
    bl_options = {'REGISTER', 'UNDO'}

    # متغيرات للتحكم في العملية
    _handle = None
    _timer = None
    is_active = False
    master_curtain = None  # الستارة الأساسية للنسخ منها
    last_curtain = None  # آخر ستارة تم إضافتها
    current_rotation = 0.0  # التدوير الحالي بالراديان

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type in {'RIGHTMOUSE', 'ESC'}:
            # إنهاء العملية
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # النقر لإضافة ستارة
            self.add_curtain_at_cursor(context, event)
            # بدء تحويل مباشر عند الحاجة
            try:
                if self.last_curtain is not None:
                    if event.shift:  # تحريك الستارة مباشرة بعد الإضافة
                        self.invoke_transform(context, 'TRANSLATE')
                    elif event.ctrl:  # تغيير الحجم مباشرة بعد الإضافة
                        self.invoke_transform(context, 'RESIZE')
            except Exception as _:
                pass
            return {'RUNNING_MODAL'}

        if event.type == 'LEFT_ALT' and event.value == 'PRESS':
            # تدوير الستارة الأخيرة بـ 90 درجة
            self.rotate_last_curtain()
            return {'RUNNING_MODAL'}

        # اختصارات التحويل القياسية
        if event.value == 'PRESS':
            if event.type == 'G':
                self.invoke_transform(context, 'TRANSLATE')
                return {'RUNNING_MODAL'}
            if event.type == 'S':
                self.invoke_transform(context, 'RESIZE')
                return {'RUNNING_MODAL'}
            if event.type == 'R':
                self.invoke_transform(context, 'ROTATE')
                return {'RUNNING_MODAL'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            # بدء العملية التفاعلية
            self.is_active = True
            context.window_manager.modal_handler_add(self)

            # إضافة مؤشر مرئي
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                self.draw_callback_px, args, 'WINDOW', 'POST_PIXEL'
            )

            self.report({'INFO'}, "انقر لإضافة ستارة، Alt لتدوير الأخيرة، ESC للإنهاء")
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "يجب تشغيل هذا الأمر في 3D Viewport")
            return {'CANCELLED'}

    def cancel(self, context):
        # تنظيف العملية
        if self._handle:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self._handle = None

        # حذف الستارة الأساسية إذا كانت موجودة (لا تترك Master_Curtain في نقطة الأصل)
        if self.master_curtain is not None:
            try:
                ob = self.master_curtain
                # إزالة الكائن من البيانات ومن كل المجموعات المرتبطة
                bpy.data.objects.remove(ob, do_unlink=True)
            except Exception as _:
                # في حال فشل الحذف لأي سبب، فقط تجاهل بدون تعطيل الخروج
                pass
            finally:
                self.master_curtain = None

        self.is_active = False
        context.area.tag_redraw()

    def get_target_collection(self, context):
        """الحصول على الكولكشن المناسب لوضع الستائر"""
        if context.scene.kh_use_curtain_collection:
            # البحث عن كولكشن Curtains أو إنشاؤه
            curtain_collection = bpy.data.collections.get("Curtains")
            if curtain_collection is None:
                # إنشاء كولكشن جديد
                curtain_collection = bpy.data.collections.new("Curtains")
                context.scene.collection.children.link(curtain_collection)
            return curtain_collection
        else:
            # استخدام الكولكشن النشط الحالي
            return context.collection

    def rotate_last_curtain(self):
        """تدوير الستارة الأخيرة بـ 90 درجة"""
        if self.last_curtain is not None:
            import math

            # إضافة 90 درجة للتدوير الحالي
            self.current_rotation += math.pi / 2  # 90 درجة بالراديان

            # تطبيق التدوير على الستارة الأخيرة
            current_rotation = list(self.last_curtain.rotation_euler)
            current_rotation[2] = self.current_rotation  # Z rotation
            self.last_curtain.rotation_euler = current_rotation

            # تحديث المشهد
            bpy.context.view_layer.update()

            # عرض رسالة
            rotation_degrees = int(self.current_rotation * 180 / math.pi) % 360
            print(f"تم تدوير الستارة إلى: {rotation_degrees}°")


    

    def draw_callback_px(self, op, context):
        # رسم مؤشر أو نص توضيحي
        import blf
        import gpu
        from gpu_extras.batch import batch_for_shader

        # إعداد النص
        font_id = 0
        blf.position(font_id, 15, 50, 0)
        #blf.size(font_id, 20, 72)
        set_font_size(font_id, 20)
        blf.color(font_id, 1.0, 1.0, 1.0, 1.0)  # أبيض
        blf.draw(font_id, "Click to add curtain - Alt to rotate - ESC to exit")

        # نص إضافي
        blf.position(font_id, 15, 30, 0)
        #blf.size(font_id, 16, 72)
        set_font_size(font_id, 16)
        blf.color(font_id, 0.8, 0.8, 0.8, 1.0)  # رمادي فاتح
        blf.draw(font_id, "انقر لإضافة ستارة - Alt لتدوير - ESC للإنهاء")

        # تعليمات إضافية للتحكم
        blf.position(font_id, 15, 70, 0)
        set_font_size(font_id, 14)
        blf.color(font_id, 0.9, 0.9, 0.6, 1.0)
        blf.draw(font_id, "G: Move | S: Scale | R: Rotate | Shift+Click: Move | Ctrl+Click: Scale")

        # عرض التدوير الحالي
        blf.position(font_id, 15, 10, 0)
        #blf.size(font_id, 14, 72)
        set_font_size(font_id, 14)
        blf.color(font_id, 0.6, 0.8, 1.0, 1.0)  # أزرق فاتح
        rotation_degrees = int(self.current_rotation * 180 / 3.14159)
        blf.draw(font_id, f"Current rotation: {rotation_degrees}°")

    def add_curtain_at_cursor(self, context, event):
        """إضافة ستارة في موقع النقر مع التدوير التلقائي"""

        # الحصول على موقع النقر في العالم ثلاثي الأبعاد
        region = context.region
        rv3d = context.region_data
        coord = event.mouse_region_x, event.mouse_region_y

        # تحويل إحداثيات الماوس إلى شعاع في الفضاء ثلاثي الأبعاد
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        # إجراء ray casting للعثور على السطح
        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, object, matrix = context.scene.ray_cast(
            depsgraph, ray_origin, view_vector
        )

        if result:
            # تم العثور على سطح، إضافة الستارة
            if self.master_curtain is None:
                # إنشاء الستارة الأساسية للمرة الأولى
                self.create_master_curtain(context)

            if self.master_curtain is not None:
                # إنشاء نسخة من الستارة الأساسية
                self.place_curtain_copy(context, location, normal, object)
        else:
            self.report({'WARNING'}, "لم يتم العثور على سطح في هذا الموقع")

    def ensure_last_active(self):
        """تحديد وتفعيل آخر ستارة لبدء التحويلات"""
        if self.last_curtain is not None:
            try:
                for o in bpy.context.selected_objects:
                    o.select_set(False)
            except Exception:
                pass
            self.last_curtain.select_set(True)
            bpy.context.view_layer.objects.active = self.last_curtain

    def invoke_transform(self, context, mode: str):
        """تشغيل أوبراتور التحويل القياسي على آخر ستارة"""
        if self.last_curtain is None:
            return
        # تأكد أن آخر ستارة محددة وفعّالة
        self.ensure_last_active()
        try:
            if mode == 'TRANSLATE':
                bpy.ops.transform.translate('INVOKE_DEFAULT')
            elif mode == 'RESIZE':
                bpy.ops.transform.resize('INVOKE_DEFAULT')
            elif mode == 'ROTATE':
                bpy.ops.transform.rotate('INVOKE_DEFAULT')
        except RuntimeError as _:
            # قد يفشل إذا لم يكن السياق صحيحاً؛ نتجاهل بصمت
            pass

    def create_master_curtain(self, context):
        """إنشاء الستارة الأساسية للمرة الأولى"""
        # مسار ملف الستارة
        script_dir = os.path.dirname(os.path.realpath(__file__))
        curtain_file = os.path.join(script_dir, "Curtain.blend")

        if not os.path.exists(curtain_file):
            self.report({'ERROR'}, f"ملف الستارة غير موجود: {curtain_file}")
            return

        try:
            # استيراد الستارة من الملف
            with bpy.data.libraries.load(curtain_file, link=False) as (data_from, data_to):
                # البحث عن كائن الستارة (أول كائن في الملف)
                if data_from.objects:
                    data_to.objects = [data_from.objects[0]]  # أخذ أول كائن فقط
                else:
                    self.report({'ERROR'}, "لا يوجد كائنات في ملف الستارة")
                    return

            # إضافة الكائن المستورد إلى المشهد
            if data_to.objects:
                self.master_curtain = data_to.objects[0]
                target_collection = self.get_target_collection(context)
                target_collection.objects.link(self.master_curtain)

                # إخفاء الستارة الأساسية
                self.master_curtain.hide_set(True)
                self.master_curtain.name = "Master_Curtain"

                self.report({'INFO'}, "تم إنشاء الستارة الأساسية")
            else:
                self.report({'ERROR'}, "فشل في استيراد كائن الستارة")

        except Exception as e:
            self.report({'ERROR'}, f"خطأ في استيراد الستارة: {str(e)}")

    def place_curtain_copy(self, context, location, normal, hit_object):
        """إنشاء نسخة مرتبطة من الستارة الأساسية ووضعها"""
        try:
            # إنشاء نسخة مرتبطة (Linked Duplicate) مثل Alt+D
            curtain_copy = self.master_curtain.copy()
            # لا ننسخ البيانات للحصول على linked duplicate
            target_collection = self.get_target_collection(context)
            target_collection.objects.link(curtain_copy)

            # جعل النسخة نشطة ومحددة
            bpy.context.view_layer.objects.active = curtain_copy
            curtain_copy.select_set(True)

            # إظهار النسخة
            curtain_copy.hide_set(False)

            # وضع الستارة بحيث يلمس مركزها السطح
            offset_distance = 0.05  # مسافة صغيرة لتجنب التداخل
            curtain_copy.location = location + (normal * offset_distance)

            # تطبيق التدوير الحالي (بدون تدوير تلقائي)
            curtain_copy.rotation_euler = (0, 0, self.current_rotation)

            # تحديث آخر ستارة تم إضافتها
            self.last_curtain = curtain_copy

            # تطبيق التحويلات لضمان الاستقرار
            bpy.context.view_layer.update()

            self.report({'INFO'}, f"تم إضافة ستارة في الموقع: {location}")

        except Exception as e:
            self.report({'ERROR'}, f"خطأ في إنشاء نسخة الستارة: {str(e)}")


class OBJECT_OT_StartFrame(bpy.types.Operator):
    bl_idname = "object.start_frame"
    bl_label = "Car Motion Blur"

    def execute(self, context):
        active_object = bpy.context.active_object
        if active_object is None:
            self.report({'ERROR'}, "No active object found.")
            return {'CANCELLED'}
        selected_obj = bpy.context.selected_objects
        if selected_obj is not None:
            for obj in selected_obj:
                if obj.type == 'MESH':
                    frame_set()
                    start_frame()
                    end_frame()
        if not bpy.context.scene.render.use_motion_blur == True:
            bpy.context.scene.render.use_motion_blur = True
        return {'FINISHED'}
    
class DeleteLocationKeyframesOperator(bpy.types.Operator):
    bl_idname = "object.delete_location_keyframes"
    bl_label = "Delete Motion Blur"

    def execute(self, context):
        bpy.context.scene.frame_set(100)
        selected_obj = bpy.context.selected_objects
        if selected_obj is not None:
            for obj in selected_obj:
                if obj.type == 'MESH':
                    if context.active_object is not None:
                        if obj.animation_data is not None:
                            for fcurve in obj.animation_data.action.fcurves:
                                if fcurve.data_path == "location":
                                    obj.animation_data.action.fcurves.remove(fcurve)
                            self.report({'INFO'}, "Delete Motion Blur")

        return {'FINISHED'}

def frame_set():
    selected_obj = bpy.context.selected_objects
    
    if selected_obj is not None:
        for obj in selected_obj:
            if obj.type == 'MESH':
                target_frame = 100
                bpy.context.scene.frame_set(target_frame)
                obj.keyframe_insert(data_path="location", frame=target_frame)  

def start_frame():
    selected_obj = bpy.context.selected_objects
    if selected_obj is not None:
        for obj in selected_obj:
            if obj.type == 'MESH':
                obj.location.x -= bpy.context.scene.start_x
                obj.location.y -= bpy.context.scene.start_y
                obj.keyframe_insert(data_path="location", frame=0)


def end_frame():
    selected_obj = bpy.context.selected_objects
    if selected_obj is not None:
        for obj in selected_obj:
            if obj.type == 'MESH':
                obj.location.x += bpy.context.scene.start_x + bpy.context.scene.start_x
                obj.location.y += bpy.context.scene.start_y + bpy.context.scene.start_y
                obj.keyframe_insert(data_path="location", frame=200)
                target_frame = 100
                bpy.context.scene.frame_set(target_frame)
                  
bpy.types.Scene.start_x = bpy.props.FloatProperty(name="Start X", default=20, min=-30, max=30)
bpy.types.Scene.start_y = bpy.props.FloatProperty(name="Start Y", default=0.0, min=-30, max=30)



#Copy Objects\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class kh_copy_object(bpy.types.Operator):
    bl_idname = "object.kh_copy_object"
    bl_label = "Copy Objects"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance", default=1.0, min=0.01)
    num_copies: bpy.props.IntProperty(name="Number of Copies", default=1, min=1)
    #random_rotation: bpy.props.FloatProperty(name="Random Rotation (Z)", default=0.0, min=0.0, max=360.0)
    #random_scale: bpy.props.FloatProperty(name="Random Scale", default=0, min=0, max=2)
    axis: bpy.props.EnumProperty(name="Axis", items=[('X', "X", ""), ('-X', "-X", ""), ('Y', "Y", ""), ('-Y', "-Y", ""), ('Z', "Z", ""), ('-Z', "-Z", "")])

    def execute(self, context):
        active_object = bpy.context.active_object
        if active_object is None:
            self.report({'ERROR'}, "No active object found.")
            return {'CANCELLED'}

        for i in range(self.num_copies):
            new_obj = active_object.copy()
            bpy.context.collection.objects.link(new_obj)

            if self.axis == 'X':
                new_obj.location.x += self.distance * (i + 1)
            elif self.axis == '-X':
                new_obj.location.x -= self.distance * (i + 1)
            elif self.axis == 'Y':
                new_obj.location.y += self.distance * (i + 1)
            elif self.axis == '-Y':
                new_obj.location.y -= self.distance * (i + 1)
            elif self.axis == 'Z':
                new_obj.location.z += self.distance * (i + 1)            
            else:
                new_obj.location.z -= self.distance * (i + 1)

            #random_angle = random.uniform(0, self.random_rotation)
            #new_obj.rotation_euler.rotate_axis('Z', random_angle)

            #scale_factor = 1.0 + random.uniform(-self.random_scale, self.random_scale)
           
            #new_obj.scale *= scale_factor

        return {'FINISHED'}
    


import itertools

from pathlib import Path
import time
import gc

class KH_OT_saveasset(Operator):
    """Save as asset the selected object (preview generation may fail)"""
    bl_idname = 'bagapie.kh_saveasset'
    bl_label = 'Export ASSET'
    bl_options = {'REGISTER', 'UNDO'}

    rewrite: bpy.props.BoolProperty(default=False)
    check_file: bpy.props.BoolProperty(default=False)
    already_exist: bpy.props.BoolProperty(default=False)
    new_name: bpy.props.StringProperty(default="None")
    category: bpy.props.StringProperty(default="", description="Select category for the asset")
    
    def get_category_items(self, context):
        """Get list of categories for the ComboBox"""
        items = [('NONE', 'No Category', 'Save in main library folder', 'FOLDER_REDIRECT', 0)]
        
        try:
            # الحصول على المكتبة المحددة
            if hasattr(bpy.context.scene, 'get') and 'Use_library' in bpy.context.scene:
                prefs = bpy.context.preferences
                filepaths = prefs.filepaths
                asset_libraries = filepaths.asset_libraries
                
                selected_library = None
                for lib in asset_libraries:
                    if lib.name == bpy.context.scene['Use_library']:
                        selected_library = lib
                        break
                
                if selected_library:
                    categories = KH_OT_saveasset.get_categories_from_library(selected_library.path)
                    for i, cat in enumerate(categories):
                        items.append((cat, cat, f"Save in {cat} folder", 'FILE_FOLDER', i + 1))
        except Exception as e:
            print(f"Error getting category items: {e}")
        
        return items
    
    category_enum: bpy.props.EnumProperty(
        name="Category",
        description="Select category folder for the asset",
        items=get_category_items,
        default=None
    )

    @classmethod
    def poll(cls, context):
        o = context.object
        l = ['MESH','CURVE']
        return (
            o is not None and 
            o.type in l
        )

    def invoke(self, context, event):
        bpy.ops.kh.batch_preview()
        wm = context.window_manager
        ob = bpy.context.active_object

        prefs = bpy.context.preferences
        filepaths = prefs.filepaths
        asset_libraries = filepaths.asset_libraries

        try:
            print("Default library : "+ asset_libraries[0].name)
        except:
            Warning("Create Library. Preferences > File Paths > Asset Libraries", "INFO", 'ERROR') 
            return {'FINISHED'}

        self.rewrite = False
        self.check_file = False
        self.already_exist = False
        self.new_name = ob.name
        self.category = ""
        self.category_enum = 'NONE'

        #ob.asset_mark()
        #ob.asset_generate_preview()
        time.sleep(0.1)
        bpy.context.scene['Use_library'] = asset_libraries[0]
         # تنظيف الذاكرة قبل فتح النافذة
        gc.collect()
        return wm.invoke_props_dialog(self)
    
    @staticmethod
    def get_categories_from_library(library_path):
        """Get list of categories (folders) from the selected library"""
        categories = []
        try:
            library_dir = Path(library_path)
            if library_dir.exists() and library_dir.is_dir():
                for item in library_dir.iterdir():
                    if item.is_dir():
                        categories.append(item.name)
        except Exception as e:
            print(f"Error reading library categories: {e}")
        return categories
    
    def find_or_create_catalog(self, library_path, category_name):
        """
        البحث عن Catalog ID للفئة المحددة أو إنشاؤه في ملف blender_assets.cats.txt
        
        Args:
            library_path: مسار مكتبة الأصول
            category_name: اسم الفئة/الكاتالوج
            
        Returns:
            str: UUID للكاتالوج أو None في حالة الفشل
        """
        import uuid
        
        try:
            catalog_file = Path(library_path) / "blender_assets.cats.txt"
            
            # قراءة الملف الموجود أو إنشاء محتوى جديد
            existing_catalogs = {}
            catalog_lines = []
            
            if catalog_file.exists():
                with open(catalog_file, 'r', encoding='utf-8') as f:
                    catalog_lines = f.readlines()
                    
                # تحليل الكاتالوجات الموجودة
                for line in catalog_lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('VERSION'):
                        parts = line.split(':')
                        if len(parts) >= 2:
                            catalog_uuid = parts[0].strip()
                            catalog_path = parts[1].strip()
                            # استخراج اسم الكاتالوج من المسار
                            catalog_name = catalog_path.split('/')[-1] if '/' in catalog_path else catalog_path
                            existing_catalogs[catalog_name] = catalog_uuid
            
            # التحقق من وجود الكاتالوج
            if category_name in existing_catalogs:
                print(f"✅ Found existing catalog: {category_name} -> {existing_catalogs[category_name]}")
                return existing_catalogs[category_name]
            
            # إنشاء كاتالوج جديد
            new_uuid = str(uuid.uuid4())
            catalog_path = category_name  # يمكن استخدام مسار متداخل مثل "Furniture/Chairs"
            simple_name = category_name
            
            # إضافة السطر الجديد
            new_catalog_line = f"{new_uuid}:{catalog_path}:{simple_name}\n"
            
            # كتابة الملف
            with open(catalog_file, 'a', encoding='utf-8') as f:
                # إضافة رأس الملف إذا كان الملف جديداً
                if not catalog_file.exists() or len(catalog_lines) == 0:
                    f.write("# This is an Asset Catalog Definition file for Blender.\n")
                    f.write("#\n")
                    f.write("# Empty lines and lines starting with `#` will be ignored.\n")
                    f.write("# The first non-ignored line must be the version indicator.\n")
                    f.write("#\n")
                    f.write("# Columns are separated by `:` (colon).\n")
                    f.write("# The first column is the catalog UUID.\n")
                    f.write("# The second column is the catalog path.\n")
                    f.write("# The third column is the catalog simple name.\n")
                    f.write("\n")
                    f.write("VERSION 1\n")
                    f.write("\n")
                
                f.write(new_catalog_line)
            
            print(f"✅ Created new catalog: {category_name} -> {new_uuid}")
            return new_uuid
            
        except Exception as e:
            print(f"❌ Error in find_or_create_catalog: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def draw(self, context):
        layout = self.layout
        ob = bpy.context.active_object



        prefs = bpy.context.preferences
        filepaths = prefs.filepaths
        asset_libraries = filepaths.asset_libraries
        
        layout.label(text = "Select Library")
        for i in range(len(asset_libraries)):
            if asset_libraries[i].name == bpy.context.scene['Use_library']:
                statut = True
            else :
                statut = False

            layout.operator('use.kh_library', text=asset_libraries[i].name,  depress = statut).index = i

        # إظهار قائمة الفئات عند اختيار مكتبة
        if bpy.context.scene['Use_library']:
            selected_library = None
            for lib in asset_libraries:
                if lib.name == bpy.context.scene['Use_library']:
                    selected_library = lib
                    break
            
            if selected_library:
                categories = KH_OT_saveasset.get_categories_from_library(selected_library.path)
                
                if categories:
                    layout.separator()
                    layout.label(text="Select Category (Optional)")
                    
                    # استخدام ComboBox لاختيار الفئة
                    row = layout.row()
                    row.prop(self, 'category_enum', text="Category")
                    
                    # تحديث self.category من الاختيار في ComboBox
                    if self.category_enum and self.category_enum != 'NONE':
                        self.category = self.category_enum
                    else:
                        self.category = ""
                    
                    # إظهار معلومات الفئة المختارة
                    if self.category:
                        box = layout.box()
                        box.label(text=f"Selected Category: {self.category}", icon='FILE_FOLDER')
                        box.label(text=f"Assets will be saved in: {self.category}/ folder")
                else:
                    layout.separator()
                    layout.label(text="No categories found in this library", icon='INFO')
                    layout.label(text="Assets will be saved in the main library folder")

        if self.check_file == False:
            self.already_exist = False
            for asset_library in asset_libraries:
                # تعديل مسار الملف ليشمل الفئة إذا تم اختيارها
                if self.category and self.category.strip():
                    path_to_file = "{path}\\{category}\\{name}.blend".format(
                        path = asset_library.path, 
                        category = self.category,
                        name = ob.name
                    )
                else:
                    path_to_file = "{path}\\{name}.blend".format(path = asset_library.path, name = ob.name)
                path = Path(path_to_file)
                
                idx = 1
                if path.is_file() == True:
                    self.already_exist = True
                    if self.rewrite == False:
                        name=ob.name
                        while path.is_file() == True:
                            if self.category and self.category.strip():
                                path_to_file = "{path}\\{category}\\{name}.blend".format(
                                    path = asset_library.path, 
                                    category = self.category,
                                    name = ob.name + '_' + str(idx)
                                )
                            else:
                                path_to_file = "{path}\\{name}.blend".format(path = asset_library.path, name = ob.name + '_' + str(idx))
                            path = Path(path_to_file)
                            name = ob.name + '_' + str(idx)
                            idx += 1
                    else:
                        name = ob.name
                else:
                    name = ob.name

            self.new_name = name

        self.check_file = True

        if self.already_exist:
            box = layout.box()
            col = box.column(align=True)
            col.label(text = "Object with the same name already exist.")
            if self.rewrite == False:
                col.prop(self, 'new_name', text = "New name")
                for asset_library in asset_libraries:
                    if self.category and self.category.strip():
                        check_path = "{path}\\{category}\\{name}.blend".format(
                            path = asset_library.path, 
                            category = self.category,
                            name = self.new_name
                        )
                    else:
                        check_path = "{path}\\{name}.blend".format(path = asset_library.path, name = self.new_name)
                    
                    if Path(check_path).is_file():
                        col.label(text = "This name already exist.", icon ='ERROR')
                        col.label(text = "This asset will replace the existing one.", icon ='ERROR')
                col.label(text = "Current name : "+ob.name)

            col.prop(self, 'rewrite', text = "Replace existing asset.")
            col = box.column(align=True)
            col.scale_y = 0.8
            col.label(text = "If replace is enabled,")
            col.label(text = "and if an asset of the same name already exists,")
            col.label(text = "it will be replaced by this new asset.")

    def execute(self, context):
            
        prefs = bpy.context.preferences
        filepaths = prefs.filepaths
        asset_libraries = filepaths.asset_libraries

        if bpy.context.scene['Use_library'] == "":
            Warning("No library selected", "INFO", 'ERROR') 
            return {'FINISHED'}
        
        try:
            print(bpy.context.scene['Use_library'][0])
        except:
            Warning("No library selected", "INFO", 'ERROR') 
            return {'FINISHED'}

        for asset_library in asset_libraries:
            print(asset_library.path)

            selected_objects = bpy.context.selected_objects
            
            for ob in selected_objects:
                # إنشاء مجلد الفئة إذا لم يكن موجوداً
                if self.category and self.category.strip():
                    category_path = Path(asset_library.path) / self.category
                    category_path.mkdir(exist_ok=True)
                    
                    path_to_file = "{path}\\{category}\\{name}.blend".format(
                        path = asset_library.path, 
                        category = self.category,
                        name = ob.name
                    )
                else:
                    path_to_file = "{path}\\{name}.blend".format(path = asset_library.path, name = ob.name)
                
                path = Path(path_to_file)
                
                if path.is_file():
                    if not self.rewrite:
                        name = self.new_name
                        ob.name = self.new_name
                    else:
                        name = ob.name
                else:
                    name = ob.name
                
                if asset_library.name in bpy.context.scene['Use_library']:
                    # تحديد الكائن كـ Asset
                    ob.asset_mark()
                    
                    # تعيين الفئة (Category/Catalog) للـ Asset
                    if self.category and self.category.strip():
                        try:
                            # البحث عن الـ Catalog المطابق للفئة المختارة
                            catalog_id = self.find_or_create_catalog(asset_library.path, self.category)
                            
                            if catalog_id:
                                # تعيين الـ Catalog ID للـ Asset
                                ob.asset_data.catalog_id = catalog_id
                                print(f"✅ Asset '{ob.name}' assigned to catalog: {self.category} (ID: {catalog_id})")
                            else:
                                print(f"⚠️ Could not find or create catalog for: {self.category}")
                        except Exception as e:
                            print(f"⚠️ Error assigning catalog: {e}")
                    
                    # حفظ الملف
                    time.sleep(5)
                    bpy.data.libraries.write(path_to_file, {ob}, fake_user=True)
                    ob.asset_clear()  # هنا يتم تطبيق الطريقة asset_clear() على كل كائن بشكل منفصل
        
        del bpy.context.scene['Use_library']

        return {'FINISHED'}





class KH_OT_savematerial(Operator):
    """Save all active materials from all selected objects (preview generation may fail)"""
    bl_idname = 'kh.savematerial'
    bl_label = "Save Materials from Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    rewrite: bpy.props.BoolProperty(default=True)  # تفعيل الكتابة فوق الملفات الموجودة
    check_file: bpy.props.BoolProperty(default=False)
    already_exist: bpy.props.BoolProperty(default=False)
    new_name: bpy.props.StringProperty(default="None")
    mat_index: bpy.props.IntProperty(default=0)
    category: bpy.props.StringProperty(default="", description="Select category for the material")
    
    def get_category_items(self, context):
        """Get list of categories for the ComboBox"""
        items = [('NONE', 'No Category', 'Save in main library folder', 'FOLDER_REDIRECT', 0)]
        
        try:
            # الحصول على المكتبة المحددة
            if hasattr(bpy.context.scene, 'get') and 'Use_library' in bpy.context.scene:
                prefs = bpy.context.preferences
                filepaths = prefs.filepaths
                asset_libraries = filepaths.asset_libraries
                
                selected_library = None
                for lib in asset_libraries:
                    if lib.name == bpy.context.scene['Use_library']:
                        selected_library = lib
                        break
                
                if selected_library:
                    categories = KH_OT_saveasset.get_categories_from_library(selected_library.path)
                    for i, cat in enumerate(categories):
                        items.append((cat, cat, f"Save in {cat} folder", 'FILE_FOLDER', i + 1))
        except Exception as e:
            print(f"Error getting category items: {e}")
        
        return items
    
    category_enum: bpy.props.EnumProperty(
        name="Category",
        description="Select category folder for the material",
        items=get_category_items,
        default=None
    )


    @classmethod
    def poll(cls, context):
        # Check if there are any selected mesh or curve objects with materials
        if not context.selected_objects:
            return False

        selected_objects = [obj for obj in context.selected_objects if obj.type in ['MESH', 'CURVE']]
        if not selected_objects:
            return False

        # Check if any selected object has materials
        for obj in selected_objects:
            if obj.material_slots:
                for slot in obj.material_slots:
                    if slot.material:
                        return True
        return False

    def invoke(self, context, event):
        wm = context.window_manager
        obj = bpy.context.active_object
        idx = obj.active_material_index

        try:
            mat = obj.material_slots[idx].material
        except:
            Warning("No material on selected object", "INFO", 'ERROR') 
            return {'FINISHED'}

        prefs = bpy.context.preferences
        filepaths = prefs.filepaths
        asset_libraries = filepaths.asset_libraries

        try:
            print("Default library : "+ asset_libraries[0].name)
        except:
            Warning("Create Library. Preferences > File Paths > Asset Libraries", "INFO", 'ERROR') 
            return {'FINISHED'}

        self.rewrite = False
        self.check_file = False
        self.already_exist = False
        self.new_name = obj.name
        self.mat_index = idx
            
        mat = obj.material_slots[idx].material
        mat.asset_mark()
        # تم تعطيل asset_generate_preview() لتجنب التجميد
        # البريفيو سيتم إنشاؤه تلقائياً في Asset Browser

        bpy.context.scene['Use_library'] = asset_libraries[0]
        
        # تنظيف الذاكرة قبل فتح النافذة
        gc.collect()
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        idx = obj.active_material_index
        mat = obj.material_slots[idx].material

        layout.template_list("BAGAPIE_UL_saveasset_list", "", obj, "material_slots", obj, "active_material_index")

        prefs = bpy.context.preferences
        filepaths = prefs.filepaths
        asset_libraries = filepaths.asset_libraries
        
        layout.label(text = "Select Library")

        for i in range(len(asset_libraries)):

                if asset_libraries[i].name == bpy.context.scene['Use_library']:
                    statut = True
                else :
                    statut = False
            
                layout.operator('use.kh_library', text=asset_libraries[i].name,  depress = statut).index = i

        # إظهار قائمة الفئات عند اختيار مكتبة
        if bpy.context.scene['Use_library']:
            selected_library = None
            for lib in asset_libraries:
                if lib.name == bpy.context.scene['Use_library']:
                    selected_library = lib
                    break
            
            if selected_library:
                categories = KH_OT_saveasset.get_categories_from_library(selected_library.path)
                
                if categories:
                    layout.separator()
                    layout.label(text="Select Category (Optional)")
                    
                    # استخدام ComboBox لاختيار الفئة
                    row = layout.row()
                    row.prop(self, 'category_enum', text="Category")
                    
                    # تحديث self.category من الاختيار في ComboBox
                    if self.category_enum and self.category_enum != 'NONE':
                        self.category = self.category_enum
                    else:
                        self.category = ""
                    
                    # إظهار معلومات الفئة المختارة
                    if self.category:
                        box = layout.box()
                        box.label(text=f"Selected Category: {self.category}", icon='FILE_FOLDER')
                        box.label(text=f"Materials will be saved in: {self.category}/ folder")
                else:
                    layout.separator()
                    layout.label(text="No categories found in this library", icon='INFO')
                    layout.label(text="Materials will be saved in the main library folder")
              

        if self.mat_index != idx:
            self.mat_index = idx
            self.check_file = False

        if self.check_file == False:
            self.already_exist = False
            for asset_library in asset_libraries:
                # تعديل مسار الملف ليشمل الفئة إذا تم اختيارها
                if self.category and self.category.strip():
                    path_to_file = "{path}\\{category}\\{name}.blend".format(
                        path = asset_library.path, 
                        category = self.category,
                        name = mat.name
                    )
                else:
                    path_to_file = "{path}\\{name}.blend".format(path = asset_library.path, name=mat.name)
                path = Path(path_to_file)
                
                idx = 1
                if path.is_file() == True:
                    self.already_exist = True
                    if self.rewrite == False:
                        while path.is_file() == True:
                            if self.category and self.category.strip():
                                path_to_file = "{path}\\{category}\\{name}.blend".format(
                                    path = asset_library.path, 
                                    category = self.category,
                                    name = mat.name + '_' + str(idx)
                                )
                            else:
                                path_to_file = "{path}\\{name}.blend".format(path = asset_library.path, name=mat.name + '_' + str(idx))
                            path = Path(path_to_file)
                            name = mat.name + '_' + str(idx)
                            idx += 1
                    else:
                        name = mat.name

                else:
                    name = mat.name

            self.new_name = name
        self.check_file = True

        if self.already_exist:
            box = layout.box()
            col = box.column(align=True)
            col.label(text = "Material with the same name already exist.")
            if self.rewrite == False:
                col.prop(self, 'new_name', text = "New Name")
                for asset_library in asset_libraries:
                    if self.category and self.category.strip():
                        check_path = "{path}\\{category}\\{name}.blend".format(
                            path = asset_library.path, 
                            category = self.category,
                            name = self.new_name
                        )
                    else:
                        check_path = "{path}\\{name}.blend".format(path = asset_library.path, name=self.new_name)
                    
                    if Path(check_path).is_file():
                        col.label(text = "This name already exist.", icon ='ERROR')
                        col.label(text = "This asset will replace the existing one.", icon ='ERROR')
                col.label(text = "Current name : "+mat.name)
            col.prop(self, 'rewrite', text = "Replace existing asset.")
            col = box.column(align=True)
            col.scale_y = 0.8
            col.label(text = "If replace is enabled,")
            col.label(text = "and if an asset of the same name already exists,")
            col.label(text = "it will be replaced by this new asset.")
            
    def execute(self, context):

        print("\n" + "="*60)
        print("🔥 KH BATCH MATERIAL SAVE - COMPREHENSIVE ANALYSIS 🔥")
        print("="*60)

        # استيراد المكتبات المطلوبة
        from pathlib import Path
        import time

        # التحقق من إعدادات المكتبة
        prefs = bpy.context.preferences
        filepaths = prefs.filepaths
        asset_libraries = filepaths.asset_libraries

        print(f"📚 Available asset libraries: {len(asset_libraries)}")
        for lib in asset_libraries:
            print(f"   - {lib.name}: {lib.path}")

        use_library = bpy.context.scene.get('Use_library', None)
        if use_library is None:
            print("❌ ERROR: No library selected in scene")
            self.report({'ERROR'}, "No library selected")
            return {'FINISHED'}

        print(f"✅ Selected library setting: {use_library}")

        # الحصول على الكائنات المحددة بطرق متعددة للتأكد
        print(f"\n🎯 OBJECT SELECTION ANALYSIS:")

        # الطريقة الأولى: من context
        context_selected = list(context.selected_objects)
        print(f"   Context selected objects: {len(context_selected)}")

        # الطريقة الثانية: من bpy.context مباشرة
        bpy_selected = list(bpy.context.selected_objects)
        print(f"   Bpy.context selected objects: {len(bpy_selected)}")

        # الطريقة الثالثة: من scene
        scene_selected = [obj for obj in bpy.context.scene.objects if obj.select_get()]
        print(f"   Scene selected objects: {len(scene_selected)}")

        # استخدام أكبر قائمة
        all_selected = context_selected if len(context_selected) >= len(bpy_selected) else bpy_selected
        if len(scene_selected) > len(all_selected):
            all_selected = scene_selected

        print(f"   Using largest list: {len(all_selected)} objects")

        # طباعة تفاصيل كل كائن محدد
        for i, obj in enumerate(all_selected):
            print(f"   {i+1}. {obj.name} (Type: {obj.type})")

        # فلترة الكائنات للحصول على MESH فقط
        mesh_objects = [obj for obj in all_selected if obj.type == 'MESH']
        print(f"\n🧊 MESH OBJECTS: {len(mesh_objects)} found")

        if not mesh_objects:
            print("❌ ERROR: No mesh objects selected")
            self.report({'ERROR'}, "No mesh objects selected")
            return {'FINISHED'}

        # تحليل شامل للمواد
        print(f"\n🎨 MATERIAL ANALYSIS:")
        all_materials = []
        material_names = set()

        total_slots = 0
        total_materials_found = 0

        for obj_idx, obj in enumerate(mesh_objects):
            print(f"\n   Object {obj_idx+1}: {obj.name}")
            print(f"      Material slots: {len(obj.material_slots)}")
            total_slots += len(obj.material_slots)

            obj_materials = 0
            for slot_idx, slot in enumerate(obj.material_slots):
                if slot.material:
                    mat = slot.material
                    mat_name = mat.name
                    obj_materials += 1
                    total_materials_found += 1

                    print(f"         Slot {slot_idx}: '{mat_name}' (Users: {mat.users})")

                    if mat_name not in material_names:
                        all_materials.append(mat)
                        material_names.add(mat_name)
                        print(f"            ✅ ADDED to save queue")
                    else:
                        print(f"            ⚠️  DUPLICATE (already in queue)")
                else:
                    print(f"         Slot {slot_idx}: EMPTY")

            print(f"      Materials in this object: {obj_materials}")

        print(f"\n📊 COLLECTION SUMMARY:")
        print(f"   Total objects processed: {len(mesh_objects)}")
        print(f"   Total material slots: {total_slots}")
        print(f"   Total materials found: {total_materials_found}")
        print(f"   Unique materials to save: {len(all_materials)}")

        print(f"\n📝 MATERIALS QUEUE:")
        for i, mat in enumerate(all_materials):
            print(f"   {i+1}. '{mat.name}' (Type: {type(mat).__name__})")

        if not all_materials:
            print("❌ ERROR: No materials found in selected objects")
            self.report({'ERROR'}, "No materials found in selected objects")
            return {'FINISHED'}

        # بدء عملية الحفظ المجمع
        print(f"\n" + "="*50)
        print("💾 BATCH SAVING PROCESS - DETAILED ANALYSIS")
        print("="*50)

        saved_count = 0
        failed_count = 0
        skipped_count = 0
        skipped_materials = []  # قائمة المواد المتخطاة

        # التحقق من المكتبات المتاحة
        active_libraries = []
        for lib in asset_libraries:
            if lib.name in bpy.context.scene['Use_library']:
                active_libraries.append(lib)
                print(f"✅ Active library: {lib.name} -> {lib.path}")
            else:
                print(f"⚠️  Inactive library: {lib.name}")

        if not active_libraries:
            print("❌ ERROR: No active libraries found")
            self.report({'ERROR'}, "No active asset libraries")
            return {'FINISHED'}

        print(f"\n🎯 SAVING {len(all_materials)} MATERIALS TO {len(active_libraries)} LIBRARIES:")

        # حفظ كل مادة في كل مكتبة نشطة
        for lib_idx, library in enumerate(active_libraries):
            print(f"\n📚 LIBRARY {lib_idx+1}: {library.name}")
            print(f"   Path: {library.path}")

            # التحقق من وجود مجلد المكتبة
            lib_path = Path(library.path)
            if not lib_path.exists():
                print(f"   ❌ Library path does not exist: {lib_path}")
                continue

            print(f"   ✅ Library path exists")

            # حفظ كل مادة
            for mat_idx, material in enumerate(all_materials):
                print(f"\n   🎨 MATERIAL {mat_idx+1}/{len(all_materials)}: {material.name}")

                try:
                    # إنشاء مجلد الفئة إذا لم يكن موجوداً
                    if self.category and self.category.strip():
                        category_path = lib_path / self.category
                        category_path.mkdir(exist_ok=True)
                        file_path = category_path / f"{material.name}.blend"
                        print(f"      Target (with category): {file_path}")
                    else:
                        file_path = lib_path / f"{material.name}.blend"
                        print(f"      Target: {file_path}")

                    # التحقق من وجود الملف والتعامل معه
                    if file_path.exists():
                        print(f"      📁 File already exists: {file_path.name}")
                        if self.rewrite:
                            print(f"      🔄 Overwrite enabled - will replace existing file")
                            try:
                                # حذف الملف الموجود أولاً
                                file_path.unlink()
                                print(f"      🗑️  Old file deleted successfully")
                            except Exception as del_error:
                                print(f"      ⚠️  Could not delete old file: {del_error}")
                                # المتابعة بالكتابة فوق الملف
                        else:
                            print(f"      ⚠️  File exists - adding to skipped list")
                            # إضافة المادة لقائمة المتخطاة
                            skipped_materials.append({
                                'original_name': material.name,
                                'suggested_name': f"{material.name}_v2",
                                'material': material,
                                'file_path': str(file_path)
                            })
                            skipped_count += 1
                            continue
                    else:
                        print(f"      ✨ New file will be created")

                    # التحقق من صحة المادة
                    if not material or not hasattr(material, 'name'):
                        print(f"      ❌ Invalid material object")
                        failed_count += 1
                        continue

                    print(f"      📝 Material validation passed")
                    print(f"         Name: {material.name}")
                    print(f"         Type: {type(material).__name__}")
                    print(f"         Users: {material.users}")

                    # تحديد المادة كأصل
                    print(f"      🏷️  Marking as asset...")
                    material.asset_mark()
                    
                    # تعيين الفئة (Category/Catalog) للمادة
                    if self.category and self.category.strip():
                        try:
                            # البحث عن الـ Catalog المطابق للفئة المختارة
                            catalog_id = KH_OT_saveasset.find_or_create_catalog(
                                KH_OT_saveasset(), library.path, self.category
                            )
                            
                            if catalog_id:
                                # تعيين الـ Catalog ID للمادة
                                material.asset_data.catalog_id = catalog_id
                                print(f"      ✅ Material '{material.name}' assigned to catalog: {self.category} (ID: {catalog_id})")
                            else:
                                print(f"      ⚠️ Could not find or create catalog for: {self.category}")
                        except Exception as e:
                            print(f"      ⚠️ Error assigning catalog: {e}")
                    
                    # ملاحظة: تم تعطيل asset_generate_preview() لأنه يسبب تجميد
                    # سيتم إنشاء البريفيو تلقائياً عند فتح Asset Browser
                    print(f"      ℹ️  Preview will be generated automatically by Asset Browser")

                    # حفظ المادة
                    print(f"      💾 Writing to file...")
                    bpy.data.libraries.write(str(file_path), {material}, fake_user=True)

                    # إزالة تحديد الأصل
                    print(f"      🧹 Clearing asset mark...")
                    material.asset_clear()

                    saved_count += 1
                    print(f"      ✅ SUCCESS: {material.name} saved to {library.name}")

                except Exception as e:
                    failed_count += 1
                    print(f"      ❌ FAILED: {material.name}")
                    print(f"         Error: {str(e)}")
                    print(f"         Type: {type(e).__name__}")

                    # طباعة تفاصيل الخطأ
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"         Details: {error_details}")

                    # محاولة تنظيف المادة في حالة الخطأ
                    try:
                        if hasattr(material, 'asset_clear'):
                            material.asset_clear()
                    except:
                        pass

        # تنظيف - لكن فقط إذا لم تكن هناك مواد متخطاة
        if not skipped_materials and 'Use_library' in bpy.context.scene:
            del bpy.context.scene['Use_library']

        # النتائج النهائية
        print(f"\n" + "="*50)
        print("📊 FINAL COMPREHENSIVE RESULTS")
        print("="*50)
        print(f"🎯 Objects processed: {len(mesh_objects)}")
        print(f"🎨 Unique materials found: {len(all_materials)}")
        print(f"📚 Active libraries: {len(active_libraries)}")
        print(f"✅ Materials saved: {saved_count}")
        print(f"⚠️  Materials skipped: {skipped_count}")
        print(f"❌ Materials failed: {failed_count}")
        print(f"📈 Success rate: {(saved_count/(saved_count+failed_count)*100):.1f}%" if (saved_count+failed_count) > 0 else "N/A")

        # التعامل مع المواد المتخطاة
        if skipped_materials:
            print(f"\n⚠️  Found {len(skipped_materials)} skipped materials - showing rename dialog")

            # تحضير قائمة المواد المتخطاة مباشرة في Scene
            context.scene.kh_skipped_materials.clear()
            for item_data in skipped_materials:
                item = context.scene.kh_skipped_materials.add()
                item.original_name = item_data['original_name']
                item.new_name = item_data['suggested_name']
                item.material = item_data['material']
                item.file_path = item_data['file_path']

            # إظهار نافذة إعادة التسمية
            bpy.ops.kh.skipped_materials_dialog('INVOKE_DEFAULT')

            # رسالة للمستخدم
            self.report({'WARNING'}, f"⚠️ {skipped_count} materials skipped due to name conflicts - rename dialog opened")

        # رسالة مفصلة للمستخدم
        if saved_count > 0:
            message = f"✅ Batch save completed! {saved_count} materials saved from {len(mesh_objects)} objects"
            if failed_count > 0:
                message += f" ({failed_count} failed)"
            if not skipped_materials:  # فقط إذا لم تكن هناك مواد متخطاة
                self.report({'INFO'}, message)
        elif skipped_count > 0 and not skipped_materials:
            self.report({'WARNING'}, f"⚠️ All {skipped_count} materials were skipped")
        elif not skipped_materials:
            self.report({'ERROR'}, f"❌ Batch save failed! {failed_count} materials failed to save")

        return {'FINISHED'}


# خصائص للمواد المتخطاة
class KH_SkippedMaterialItem(bpy.types.PropertyGroup):
    original_name: bpy.props.StringProperty(name="Original Name")
    new_name: bpy.props.StringProperty(name="New Name")
    material: bpy.props.PointerProperty(type=bpy.types.Material)
    file_path: bpy.props.StringProperty(name="File Path")

class KH_UL_skipped_materials_list(bpy.types.UIList):
    """قائمة UI للمواد المتخطاة"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # اسم المادة الأصلي
            layout.label(text=item.original_name, icon='MATERIAL')

            # حقل تعديل الاسم الجديد
            layout.prop(item, "new_name", text="")

            # أيقونة تحذير
            layout.label(text="", icon='ERROR')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='MATERIAL')

class KH_OT_skipped_materials_dialog(Operator):
    """نافذة حوار للمواد المتخطاة مع إمكانية تغيير الأسماء"""
    bl_idname = 'kh.skipped_materials_dialog'
    bl_label = "Materials Skipped - Rename Required"
    bl_options = {'REGISTER', 'UNDO'}

    # خصائص النافذة
    width: bpy.props.IntProperty(default=600)
    height: bpy.props.IntProperty(default=400)

    # خاصية لتحديد المكتبة كـ ComboBox
    def get_library_items(self, context):
        """الحصول على قائمة مكتبات الأصول للـ ComboBox"""
        items = []

        prefs = bpy.context.preferences
        filepaths = prefs.filepaths
        asset_libraries = filepaths.asset_libraries

        if asset_libraries:
            for i, lib in enumerate(asset_libraries):
                # (identifier, name, description, icon, number)
                items.append((lib.name, lib.name, f"Path: {lib.path}", 'ASSET_MANAGER', i))
        else:
            items.append(('NONE', 'No Libraries Found', 'No asset libraries configured', 'ERROR', 0))

        return items

    def update_selected_library(self, context):
        """تحديث إعدادات Scene عند تغيير المكتبة المحددة"""
        if self.selected_library and self.selected_library != 'NONE':
            context.scene['Use_library'] = [self.selected_library]
            print(f"📚 Library updated to: {self.selected_library}")

    selected_library: bpy.props.EnumProperty(
        name="Target Library",
        description="Select the asset library to save materials to",
        items=get_library_items,
        update=update_selected_library,
        default=None
    )

    def execute(self, context):
        # حفظ المواد بالأسماء الجديدة
        return self.save_materials_with_new_names(context)

    def invoke(self, context, event):
        # تحضير قائمة المواد المتخطاة
        self.prepare_skipped_materials(context)

        # تحديد المكتبة الافتراضية من الإعدادات الحالية
        prefs = bpy.context.preferences
        filepaths = prefs.filepaths
        asset_libraries = filepaths.asset_libraries

        if not asset_libraries:
            self.report({'ERROR'}, "No asset libraries configured")
            return {'CANCELLED'}

        # البحث عن المكتبة المحددة مسبقاً
        use_library = context.scene.get('Use_library', None)
        default_library = None

        if use_library:
            if isinstance(use_library, list) and use_library:
                default_library = use_library[0]
            elif isinstance(use_library, str):
                default_library = use_library

        # التحقق من وجود المكتبة في القائمة المتاحة
        if default_library:
            library_names = [lib.name for lib in asset_libraries]
            if default_library in library_names:
                self.selected_library = default_library
                print(f"✅ Using previously selected library: {default_library}")
            else:
                # المكتبة المحددة مسبقاً غير موجودة، استخدم الأولى
                self.selected_library = asset_libraries[0].name
                print(f"⚠️  Previously selected library not found, using: {self.selected_library}")
        else:
            # لا توجد مكتبة محددة مسبقاً، استخدم الأولى
            self.selected_library = asset_libraries[0].name
            print(f"ℹ️  No previous selection, using first library: {self.selected_library}")

        # تحديث إعدادات Scene
        context.scene['Use_library'] = [self.selected_library]

        return context.window_manager.invoke_props_dialog(self, width=self.width)

    def prepare_skipped_materials(self, context):
        """تحضير قائمة المواد المتخطاة"""
        # القائمة تم تحضيرها مسبقاً من العامل الرئيسي
        # لا حاجة لمعالجة إضافية هنا
        pass

    def draw(self, context):
        layout = self.layout

        # عنوان النافذة
        title_box = layout.box()
        title_row = title_box.row()
        title_row.label(text="⚠️ Materials Skipped Due to Name Conflicts", icon='ERROR')

        # شرح المشكلة
        info_box = layout.box()
        info_col = info_box.column()
        info_col.label(text="The following materials were skipped because files with the same names already exist:")
        info_col.label(text="Please provide new names for these materials to save them.")

        # اختيار المكتبة باستخدام ComboBox
        library_box = layout.box()
        library_col = library_box.column()

        # عنوان القسم
        header_row = library_col.row()
        header_row.label(text="📚 Target Library", icon='ASSET_MANAGER')

        # ComboBox لاختيار المكتبة
        combo_row = library_col.row()
        combo_row.prop(self, "selected_library", text="")

        # عرض مسار المكتبة المحددة
        if self.selected_library and self.selected_library != 'NONE':
            prefs = bpy.context.preferences
            filepaths = prefs.filepaths
            asset_libraries = filepaths.asset_libraries

            selected_lib_path = None
            for lib in asset_libraries:
                if lib.name == self.selected_library:
                    selected_lib_path = lib.path
                    break

            if selected_lib_path:
                info_row = library_col.row()
                info_row.label(text=f"Path: {selected_lib_path}", icon='FOLDER_REDIRECT')
            else:
                info_row = library_col.row()
                info_row.label(text="Library path not found!", icon='ERROR')

        # قائمة المواد المتخطاة
        if len(context.scene.kh_skipped_materials) > 0:
            materials_box = layout.box()
            materials_row = materials_box.row()
            materials_row.label(text=f"Skipped Materials ({len(context.scene.kh_skipped_materials)}):", icon='MATERIAL')

            # قائمة المواد مع إمكانية التعديل
            materials_box.template_list(
                "KH_UL_skipped_materials_list", "",
                context.scene, "kh_skipped_materials",
                context.scene, "kh_skipped_materials_index",
                rows=min(8, len(context.scene.kh_skipped_materials))
            )

            # أزرار مساعدة
            buttons_row = materials_box.row()
            buttons_row.operator("kh.auto_rename_skipped", text="Auto Rename All", icon='FILE_REFRESH')
            buttons_row.operator("kh.reset_skipped_names", text="Reset Names", icon='LOOP_BACK')
        else:
            layout.label(text="No skipped materials found.", icon='INFO')

        # معلومات إضافية
        layout.separator()
        help_box = layout.box()
        help_col = help_box.column()
        help_col.label(text="💡 Tips:", icon='INFO')
        help_col.label(text="• Auto Rename will add '_v2', '_v3', etc. to duplicate names")
        help_col.label(text="• Empty names will use the original name with a suffix")
        help_col.label(text="• Click OK to save materials with new names")

    def save_materials_with_new_names(self, context):
        """حفظ المواد بالأسماء الجديدة"""

        print(f"\n🔄 SAVING SKIPPED MATERIALS WITH NEW NAMES")
        print("="*50)

        saved_count = 0
        failed_count = 0

        # الحصول على مكتبات الأصول
        prefs = bpy.context.preferences
        filepaths = prefs.filepaths
        asset_libraries = filepaths.asset_libraries

        # استخدام المكتبة المحددة من ComboBox
        if not self.selected_library or self.selected_library == 'NONE':
            self.report({'ERROR'}, "No library selected in ComboBox")
            return {'FINISHED'}

        use_library = [self.selected_library]
        print(f"📚 Using library for saving: {self.selected_library}")

        for item in context.scene.kh_skipped_materials:
            material = item.material
            new_name = item.new_name.strip()

            # استخدام الاسم الأصلي إذا كان الاسم الجديد فارغ
            if not new_name:
                new_name = item.original_name + "_v2"

            print(f"\n🎨 Processing: {item.original_name} -> {new_name}")

            # تغيير اسم المادة مؤقتاً
            original_name = material.name
            material.name = new_name

            try:
                # حفظ المادة في المكتبات النشطة
                for asset_library in asset_libraries:
                    if asset_library.name in use_library:
                        from pathlib import Path
                        import time

                        file_path = Path(asset_library.path) / f"{new_name}.blend"
                        print(f"   Saving to: {file_path}")

                        # حفظ المادة
                        material.asset_mark()
                        # تم تعطيل asset_generate_preview() لتجنب التجميد
                        bpy.data.libraries.write(str(file_path), {material}, fake_user=True)
                        material.asset_clear()

                        saved_count += 1
                        print(f"   ✅ SUCCESS: {new_name}")
                        break

            except Exception as e:
                # استرجاع الاسم الأصلي في حالة الفشل
                material.name = original_name
                failed_count += 1
                print(f"   ❌ FAILED: {str(e)}")

        # تنظيف
        context.scene.kh_skipped_materials.clear()

        # رسالة النتيجة
        if saved_count > 0:
            message = f"✅ Saved {saved_count} materials with new names"
            if failed_count > 0:
                message += f" ({failed_count} failed)"
            self.report({'INFO'}, message)
        else:
            self.report({'ERROR'}, f"❌ Failed to save materials ({failed_count} failed)")

        return {'FINISHED'}


class KH_OT_auto_rename_skipped(Operator):
    """إعادة تسمية تلقائية للمواد المتخطاة"""
    bl_idname = 'kh.auto_rename_skipped'
    bl_label = "Auto Rename Skipped Materials"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for item in context.scene.kh_skipped_materials:
            # إنشاء اسم جديد تلقائياً
            base_name = item.original_name
            counter = 2

            # البحث عن اسم غير مستخدم
            while True:
                new_name = f"{base_name}_v{counter}"

                # التحقق من عدم وجود مادة بهذا الاسم
                if new_name not in bpy.data.materials:
                    # التحقق من عدم وجود ملف بهذا الاسم
                    from pathlib import Path
                    prefs = bpy.context.preferences
                    filepaths = prefs.filepaths
                    asset_libraries = filepaths.asset_libraries

                    file_exists = False
                    for lib in asset_libraries:
                        file_path = Path(lib.path) / f"{new_name}.blend"
                        if file_path.exists():
                            file_exists = True
                            break

                    if not file_exists:
                        item.new_name = new_name
                        break

                counter += 1
                if counter > 100:  # حماية من الحلقة اللانهائية
                    item.new_name = f"{base_name}_{bpy.context.scene.frame_current}"
                    break

        self.report({'INFO'}, f"Auto-renamed {len(context.scene.kh_skipped_materials)} materials")
        return {'FINISHED'}

class KH_OT_reset_skipped_names(Operator):
    """إعادة تعيين أسماء المواد المتخطاة للأسماء الأصلية"""
    bl_idname = 'kh.reset_skipped_names'
    bl_label = "Reset Skipped Material Names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for item in context.scene.kh_skipped_materials:
            item.new_name = item.original_name

        self.report({'INFO'}, "Reset all names to original")
        return {'FINISHED'}



class KH_OT_make_materials_assets(Operator):
    """Make all materials from selected objects as assets in current file"""
    bl_idname = 'kh.make_materials_assets'
    bl_label = "Make Materials as Assets"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Check if there are any selected mesh or curve objects with materials
        if not context.selected_objects:
            return False

        selected_objects = [obj for obj in context.selected_objects if obj.type in ['MESH', 'CURVE']]
        if not selected_objects:
            return False

        # Check if any selected object has materials
        for obj in selected_objects:
            if obj.material_slots:
                for slot in obj.material_slots:
                    if slot.material:
                        return True
        return False

    def execute(self, context):

        print("\n" + "="*60)
        print("🏷️ MAKE MATERIALS AS ASSETS - CURRENT FILE")
        print("="*60)

        # الحصول على الكائنات المحددة
        selected_objects = [obj for obj in context.selected_objects if obj.type in ['MESH', 'CURVE']]
        print(f"📦 Processing {len(selected_objects)} selected objects")

        # جمع جميع المواد الفريدة
        all_materials = []
        material_names = set()

        for obj in selected_objects:
            print(f"\n🧊 Object: {obj.name}")
            print(f"   Material slots: {len(obj.material_slots)}")

            for slot_idx, slot in enumerate(obj.material_slots):
                if slot.material:
                    mat = slot.material
                    mat_name = mat.name
                    print(f"      Slot {slot_idx}: {mat_name}")

                    if mat_name not in material_names:
                        all_materials.append(mat)
                        material_names.add(mat_name)
                        print(f"         ✅ Added to asset queue")
                    else:
                        print(f"         ⚠️  Duplicate (already in queue)")

        print(f"\n📊 SUMMARY:")
        print(f"   Objects processed: {len(selected_objects)}")
        print(f"   Unique materials found: {len(all_materials)}")

        if not all_materials:
            self.report({'ERROR'}, "No materials found in selected objects")
            return {'FINISHED'}

        # تحويل المواد إلى أصول
        print(f"\n🏷️ CONVERTING TO ASSETS:")
        success_count = 0
        failed_count = 0
        already_asset_count = 0

        for mat in all_materials:
            print(f"\n   🎨 Material: {mat.name}")

            try:
                # التحقق من كون المادة أصل مسبقاً
                if mat.asset_data:
                    print(f"      ℹ️  Already an asset")
                    already_asset_count += 1
                    continue

                # تحويل إلى أصل
                mat.asset_mark()
                # تم تعطيل asset_generate_preview() لتجنب التجميد
                print(f"      ✅ Marked as asset")

                # إضافة fake user للحفاظ على المادة
                mat.use_fake_user = True
                print(f"      🔒 Fake user enabled")

                success_count += 1

            except Exception as e:
                print(f"      ❌ Failed: {str(e)}")
                failed_count += 1

        # النتائج النهائية
        print(f"\n📊 FINAL RESULTS:")
        print(f"   ✅ Successfully converted: {success_count}")
        print(f"   ℹ️  Already assets: {already_asset_count}")
        print(f"   ❌ Failed: {failed_count}")

        # تحديث قائمة المواد في الواجهة
        if hasattr(context.scene, 'kh_selected_materials'):
            context.scene.kh_selected_materials.clear()
            for mat in all_materials:
                item = context.scene.kh_selected_materials.add()
                item.name = mat.name
                item.material = mat

        # رسالة للمستخدم
        total_processed = success_count + already_asset_count
        if total_processed > 0:
            message = f"✅ {total_processed} materials are now assets in current file"
            if failed_count > 0:
                message += f" ({failed_count} failed)"
            self.report({'INFO'}, message)
        else:
            self.report({'ERROR'}, f"❌ Failed to convert materials to assets")

        return {'FINISHED'}


# خصائص لتخزين قائمة المواد المحددة
class KH_MaterialItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Material Name")
    material: bpy.props.PointerProperty(type=bpy.types.Material)
    is_asset: bpy.props.BoolProperty(name="Is Asset", default=False)

class KH_UL_selected_materials_list(bpy.types.UIList):
    """قائمة UI لعرض المواد المحددة من الكائنات"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.material:
                # أيقونة المادة
                mat_icon = 'MATERIAL' if not item.material.asset_data else 'ASSET_MANAGER'

                # اسم المادة
                layout.prop(item.material, "name", text="", emboss=False, icon=mat_icon)

                # حالة الأصل
                if item.material.asset_data:
                    layout.label(text="Asset", icon='CHECKMARK')
                else:
                    layout.label(text="", icon='BLANK1')
            else:
                layout.label(text="No Material", icon='ERROR')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='MATERIAL')

class KH_UL_saveasset_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        slot = item
        ma = slot.material
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if ma:
                layout.prop(ma, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="", translate=False, icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class KH_OT_update_materials_list(Operator):
    """Update the list of materials from selected objects"""
    bl_idname = 'kh.update_materials_list'
    bl_label = "Update Materials List"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # مسح القائمة الحالية
        context.scene.kh_selected_materials.clear()

        # جمع المواد من الكائنات المحددة
        selected_objects = [obj for obj in context.selected_objects if obj.type in ['MESH', 'CURVE']]
        material_names = set()

        for obj in selected_objects:
            for slot in obj.material_slots:
                if slot.material and slot.material.name not in material_names:
                    item = context.scene.kh_selected_materials.add()
                    item.name = slot.material.name
                    item.material = slot.material
                    item.is_asset = bool(slot.material.asset_data)
                    material_names.add(slot.material.name)

        self.report({'INFO'}, f"Updated list: {len(context.scene.kh_selected_materials)} materials found")
        return {'FINISHED'}


class KHLibrary(Operator):
    """Enable/Disable Library"""
    bl_idname = "use.kh_library"
    bl_label = "Use Library"

    index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        obj = context.object
        
        prefs = bpy.context.preferences
        filepaths = prefs.filepaths
        asset_libraries = filepaths.asset_libraries
        
        if asset_libraries[self.index].name in bpy.context.scene['Use_library']:
            bpy.context.scene['Use_library'] = bpy.context.scene['Use_library'].replace(asset_libraries[self.index].name, "", 1)
        else :
            bpy.context.scene['Use_library'] = asset_libraries[self.index].name

        return {'FINISHED'}


def Warning(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    

def enum_previews_from_directory_items1(self, context):
    enum_items = []

    if context is None:
        return enum_items
    directory = os.path.join(os.path.dirname(__file__), "cycles_preview")

    pcoll = preview_collections1["main"]

    if directory == pcoll.scene_previews_dir:
        return pcoll.scene_previews1

    if directory and os.path.exists(directory):
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.scene_previews1 = enum_items
    pcoll.scene_previews_dir = directory
    return pcoll.scene_previews1



#saveassets///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def check_moulah_version():
    
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_name = 'kh_saveassets.py'
    file_path = os.path.join(current_directory, file_name)

    return(os.path.isfile(file_path))


if check_moulah_version():
    from .kh_saveassets import kh_OT_saveasset,kh_OT_edit_assets,kh_UL_mat_list,MATERIAL_UL_mats



def enum_previews_from_directory_items1(self, context):
    enum_items = []

    if context is None:
        return enum_items
    directory = os.path.join(os.path.dirname(__file__), "cycles_preview")

    pcoll = preview_collections1["main"]

    if directory == pcoll.scene_previews_dir:
        return pcoll.scene_previews1

    if directory and os.path.exists(directory):
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.scene_previews1 = enum_items
    pcoll.scene_previews_dir = directory
    return pcoll.scene_previews1

#auto_load//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

__all__ = (
    "init",
    "register",
    "unregister",
)

blender_version = bpy.app.version

modules = None
ordered_classes = None

def init():
    global modules
    global ordered_classes

    modules = get_all_submodules(Path(__file__).parent)
    ordered_classes = get_ordered_classes_to_register(modules)

def register():
    for cls in ordered_classes:
        bpy.utils.register_class(cls)

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "register"):
            module.register()

def unregister():
    for cls in reversed(ordered_classes):
        bpy.utils.unregister_class(cls)

    for module in modules:
        if module.__name__ == __name__:
            continue
        if hasattr(module, "unregister"):
            module.unregister()


# Import modules
#################################################

def get_all_submodules(directory):
    return list(iter_submodules(directory, directory.name))

def iter_submodules(path, package_name):
    for name in sorted(iter_submodule_names(path)):
        yield importlib.import_module("." + name, package_name)

def iter_submodule_names(path, root=""):
    for _, module_name, is_package in pkgutil.iter_modules([str(path)]):
        if is_package:
            sub_path = path / module_name
            sub_root = root + module_name + "."
            yield from iter_submodule_names(sub_path, sub_root)
        else:
            yield root + module_name


# Find classes to register
#################################################

def get_ordered_classes_to_register(modules):
    return toposort(get_register_deps_dict(modules))

def get_register_deps_dict(modules):
    my_classes = set(iter_my_classes(modules))
    my_classes_by_idname = {cls.bl_idname : cls for cls in my_classes if hasattr(cls, "bl_idname")}

    deps_dict = {}
    for cls in my_classes:
        deps_dict[cls] = set(iter_my_register_deps(cls, my_classes, my_classes_by_idname))
    return deps_dict

def iter_my_register_deps(cls, my_classes, my_classes_by_idname):
    yield from iter_my_deps_from_annotations(cls, my_classes)
    yield from iter_my_deps_from_parent_id(cls, my_classes_by_idname)

def iter_my_deps_from_annotations(cls, my_classes):
    for value in typing.get_type_hints(cls, {}, {}).values():
        dependency = get_dependency_from_annotation(value)
        if dependency is not None:
            if dependency in my_classes:
                yield dependency

def get_dependency_from_annotation(value):
    if blender_version >= (2, 93):
        if isinstance(value, bpy.props._PropertyDeferred):
            return value.keywords.get("type")
    else:
        if isinstance(value, tuple) and len(value) == 2:
            if value[0] in (bpy.props.PointerProperty, bpy.props.CollectionProperty):
                return value[1]["type"]
    return None

def iter_my_deps_from_parent_id(cls, my_classes_by_idname):
    if bpy.types.Panel in cls.__bases__:
        parent_idname = getattr(cls, "bl_parent_id", None)
        if parent_idname is not None:
            parent_cls = my_classes_by_idname.get(parent_idname)
            if parent_cls is not None:
                yield parent_cls

def iter_my_classes(modules):
    base_types = get_register_base_types()
    for cls in get_classes_in_modules(modules):
        if any(base in base_types for base in cls.__bases__):
            if not getattr(cls, "is_registered", False):
                yield cls

def get_classes_in_modules(modules):
    classes = set()
    for module in modules:
        for cls in iter_classes_in_module(module):
            classes.add(cls)
    return classes

def iter_classes_in_module(module):
    for value in module.__dict__.values():
        if inspect.isclass(value):
            yield value

def get_register_base_types():
    return set(getattr(bpy.types, name) for name in [
        "Panel", "Operator", "PropertyGroup",
        "AddonPreferences", "Header", "Menu",
        "Node", "NodeSocket", "NodeTree",
        "UIList", "RenderEngine",
        "Gizmo", "GizmoGroup",
    ])


# Find order to register to solve dependencies
#################################################

def toposort(deps_dict):
    sorted_list = []
    sorted_values = set()
    while len(deps_dict) > 0:
        unsorted = []
        for value, deps in deps_dict.items():
            if len(deps) == 0:
                sorted_list.append(value)
                sorted_values.add(value)
            else:
                unsorted.append(value)
        deps_dict = {value : deps_dict[value] - sorted_values for value in unsorted}
    return sorted_list

#bagabatch_render_coll//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
import bpy
import addon_utils
import os
import math
from mathutils import Vector


class KH_OP_batch_coll_preview(bpy.types.Operator):
    """Batch render preview for collections"""
    bl_idname = "kh.batch_coll_preview"
    bl_label = "Batch Thumbernails"

    def execute(self, context):
        pref = get_addon_preferences_safe(context)
        debug = pref.debug_mode if pref else False
        if debug:print("########################################################")
        if debug:print("###                   START RENDER                   ###")
        if debug:print("########################################################")
        selected_scene = bpy.context.window_manager.scene_previews1.removesuffix(".png")
        original_scene = bpy.context.scene
        render_device1= context.scene.render_device1
        collections = []
        selected_collection = context.collection
        all_scene_collection = context.scene.collection.children_recursive

        if pref.render_all_assets_coll:
            for col in all_scene_collection:
                if col.asset_data is not None:
                    collections.append(col)
        else:
            collections.append(selected_collection)

        # GET VIEW
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                break
        space = area.spaces.active
        view_matrix = space.region_3d.view_matrix
        user_view_orientation = view_matrix.inverted()
        user_view_focal = bpy.context.space_data.lens

        cam_rot = [0,0,0]
        if pref.use_current_orientation == True and bpy.context.scene.camera is not None:
            cam_rot=bpy.context.scene.camera.rotation_euler

        Set_Scene(self,context,selected_scene)
        
        # START GENERATE OBJECT PREVIEW HERE
        for col in collections:
            if debug:print("_____________________________________________")
            if debug:print("LOOP: "+col.name)

            # LINK OBJ TO kh SCENE AND SET SCENE
            bpy.ops.object.make_links_scene(scene=selected_scene)
            context.window.scene = bpy.data.scenes[selected_scene]
            
            for obj in bpy.context.scene.objects:
                if obj.type == 'EMPTY' and obj.name.startswith("TEMP_BB_Empty_"):
                    # Sélectionne l'objet
                    empty = obj
            empty.instance_type='COLLECTION'
            empty.instance_collection = col
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = empty
            empty.select_set(True)
            if debug:print("        SETUP = SUCCES")

            # SETUP CAMERA IF USE CURRENT VIEW IS TRUE
            Set_Camera(self, context, cam_rot, user_view_orientation, user_view_focal)
            if debug:print("        SET CAMERA = SUCCES")

            # RENDER PREVIEW
            image_path = Render_Preview(self, context, col,render_device1, user_view_orientation)
            if debug:print("        RENDER = SUCCES")
            if debug:print("        PATH   = "+image_path)
            
            Set_Preview(self, context,col,image_path)
            if debug:print("        SET PREVIEW = SUCCES")

            if debug:print("        SAVE EXTERNAL = " + str(pref.save_preview))
            if pref.save_preview == True:
                Save_Preview_External(self, context, image_path)
                if debug:print("        SAVE EXTERNAL = SUCCES")

            # REMOVE OBJ
            empty.instance_collection = None

            os.remove(image_path+".png")
        
            bpy.context.window.scene = original_scene

        Clean_Scene(self, context, selected_scene, original_scene)

        return{'FINISHED'}


#bagabatch_render_utils//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
import addon_utils
from mathutils import Vector
import re
import ntpath

def Set_Scene(self,context,scene_name):
    if scene_name not in bpy.context.scene:
        Import_Scene(self,context,scene_name)

def Import_Scene(self,context,scene_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "KH-Tools":
            file_path = os.path.join(script_dir, "render_setup.blend")
            break
        else: pass
    inner_path = "Scene"
    
    bpy.ops.wm.append(
        filepath = os.path.join(file_path, inner_path, scene_name),
        directory = os.path.join(file_path, inner_path),
        filename=scene_name
        )
    
    
###################################################################################
#   RENDER
###################################################################################
def Set_Camera(self, context, cam_rot, user_view_orientation, user_view_focal):
    pref = get_addon_preferences_safe(context)
    cam=bpy.context.scene.camera

    cam.data.lens = pref.camera_focal
    cam.data.clip_start = pref.camera_clip_start
    cam.data.clip_end = pref.camera_clip_end

    
    if pref.use_current_orientation == True:
        cam.rotation_euler = cam_rot
    else:
        cam.rotation_euler[2] = -(pref.camera_orientation/180)*3.1415

    if pref.use_view == False or pref.use_current_orientation == False:
        bpy.ops.view3d.camera_to_view_selected()
    else :
        cam.matrix_world = user_view_orientation
        cam.data.lens = user_view_focal
        if pref.force_focus_selected:
            bpy.ops.view3d.camera_to_view_selected()

def Cam_Rotation(self, context, user_view_orientation):
    pref = get_addon_preferences_safe(context)
    camera=bpy.context.scene.camera
    if pref.use_view==True and pref.use_current_orientation == True:
        cam_direction = user_view_orientation @ Vector((0.0, 0.0, -1.0))
    else:
        cam_direction = camera.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
    angle_rad = math.atan2(cam_direction.y, cam_direction.x)
    angle_deg = math.degrees(angle_rad)

    return(angle_rad)

def Render_Preview(self, context, obj,render_device1, user_view_orientation):
    pref = get_addon_preferences_safe(context)
    # EEVEE Render settings :
    if pref.render_engine:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        bpy.context.scene.eevee.taa_render_samples = pref.eevee_samples
        bpy.context.scene.eevee.use_gtao = pref.eevee_ao
        bpy.context.scene.eevee.use_ssr = pref.eevee_ssr
        bpy.context.scene.eevee.use_ssr_refraction = pref.eevee_refract
        bpy.context.scene.render.film_transparent = pref.eevee_transparent_background
        bpy.context.scene.render.resolution_x = pref.render_resolution
        bpy.context.scene.render.resolution_y = pref.render_resolution
        bpy.context.scene.view_settings.exposure = pref.render_exposition
    # Cycles Render settings :
    else:
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.samples = pref.cycles_samples
        bpy.context.scene.cycles.transparent_max_bounces = pref.cycles_transp_bounces
        bpy.context.scene.cycles.use_denoising = pref.cycles_denoise
        bpy.context.scene.cycles.device = render_device1
        bpy.context.scene.render.film_transparent = pref.cycles_transparent_background
        bpy.context.scene.cycles.film_transparent_glass = pref.cycles_transparent_background
        bpy.context.scene.render.resolution_x = pref.render_resolution
        bpy.context.scene.render.resolution_y = pref.render_resolution
        bpy.context.scene.view_settings.exposure = pref.render_exposition

    # Lighting sun orientation
    cam_rot = Cam_Rotation(self, context, user_view_orientation)
    orientation = pref.sun_orientation
    for node in bpy.context.scene.world.node_tree.nodes:
        sun_offset = -1.5707
        if pref.use_current_orientation:
            sun_offset = 1.5707
            if pref.use_view == False:
                orientation = orientation+180
            
        if node.label == "TEMP_BB_Sky":
            node.sun_rotation = -cam_rot+sun_offset+math.radians(orientation)
            break

    user_output = bpy.context.scene.render.filepath

    if pref.use_temp_files:
        temp_thumb_path = tempfile.gettempdir()
    else:
        addon_location = os.path.dirname(os.path.realpath(__file__))
        temp_thumb_path = os.path.join(addon_location, 'temp_thumb')
    temp_thumb_path_full = os.path.join(temp_thumb_path, obj.name)

    bpy.context.scene.render.filepath = temp_thumb_path_full

    bpy.ops.render.render(write_still = True)
    bpy.context.scene.render.filepath =user_output

    return(temp_thumb_path_full)

###################################################################################
#   ASSET BROWSER
###################################################################################
def Set_Preview(self, context, obj, image_path):
    obj.asset_mark()
    # obj.asset_generate_preview() 
    # time.sleep(0.05)
    with bpy.context.temp_override(id=obj):
        bpy.ops.ed.lib_id_load_custom_preview(
            filepath=image_path+".png"
        )

def normalize_fiepath(directory_path):
    normalized_path = os.path.normpath(directory_path)
    return os.path.join(normalized_path, '')

def Save_Preview_External(self,context,image_path):
    pref = get_addon_preferences_safe(context)
    debug = pref.debug_mode if pref else False
    blender_file_path = ntpath.dirname(bpy.data.filepath)

    if pref.save_preview_in_current_file_loc == False and os.path.isdir(pref.preview_filepath):
        # SAVE IN CUSTOM LOCATION
        if debug:print("        PREVIEW MODE = CUSTOM LOCATION")
        filepath = normalize_fiepath(pref.preview_filepath)
        if debug:print("        PREVIEW LOCATION = "+filepath)
        shutil.copy(image_path+".png", filepath)

    elif bpy.data.filepath != '' and pref.save_preview_in_current_file_loc == True:
        # SAVE IN CURRENT FILE LOCATION
        if debug:print("        PREVIEW MODE = CURRENT FILE LOCATION")
        filepath = normalize_fiepath(blender_file_path)
        if debug:print("        PREVIEW LOCATION = "+filepath)

        shutil.copy(image_path+".png", filepath)

    else: print("ERROR : no file path for image")


###################################################################################
#   REMOVE kh SCENE AND RESTORE ORIGINAL SCENE
###################################################################################
def Clean_Scene(self, context, scene, original_scene):

    delete_cameras()
    delete_objects()
    delete_collections()
    delete_worlds()

    bpy.context.window.scene = bpy.data.scenes[scene]
    bpy.ops.scene.delete()
    bpy.context.window.scene = original_scene

def to_delete(name):
    pattern = r"^(TEMP_)?[A-Z]{2}_(Camera|World|CamObj|Coll|Empty)(_)?[0-9]*"
    return re.match(pattern, name) is not None

def delete_cameras():
    to_delete_cameras = [cam for cam in bpy.data.cameras if to_delete(cam.name)]
    for cam in to_delete_cameras:
        bpy.data.cameras.remove(cam, do_unlink=True)

def delete_objects():
    to_delete_objects = [obj for obj in bpy.data.objects if to_delete(obj.name)]
    for obj in to_delete_objects:
        bpy.data.objects.remove(obj, do_unlink=True)

def delete_collections():
    to_delete_collections = [coll for coll in bpy.data.collections if to_delete(coll.name)]
    for coll in to_delete_collections:
        bpy.data.collections.remove(coll)

def delete_worlds():
    to_delete_worlds = [world for world in bpy.data.worlds if to_delete(world.name)]
    for world in to_delete_worlds:
        bpy.data.worlds.remove(world)
        
#bagabatch_render//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
import addon_utils
import math
from mathutils import Vector


class KH_OP_batch_preview(bpy.types.Operator):
    """Batch render preview for each selected objects"""
    bl_idname = "kh.batch_preview"
    bl_label = "Batch Thumbernails"

    @classmethod
    def poll(cls, context):
        o = context.object
        return (o is not None and o.type in ['MESH','CURVE','EMPTY'])

    def execute(self, context):
        pref = get_addon_preferences_safe(context)
        debug = pref.debug_mode if pref else False
        if debug:print("########################################################")
        if debug:print("###                   START RENDER                   ###")
        if debug:print("########################################################")
        selected_scene = bpy.context.window_manager.scene_previews1.removesuffix(".png")
        original_scene = bpy.context.scene
        objs =context.selected_objects
        render_device1 = context.scene.render_device1

        if len(objs) == 0:
            Warning("No assets selected","Empty !")
            return {'FINISHED'}

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                break
        space = area.spaces.active
        view_matrix = space.region_3d.view_matrix
        user_view_orientation = view_matrix.inverted()
        user_view_focal = bpy.context.space_data.lens

        cam_rot = [0,0,0]
        if pref.use_current_orientation == True and bpy.context.scene.camera is not None:
            cam_rot=bpy.context.scene.camera.rotation_euler
        if debug:print("GET VARIABLE = SUCCES")
        if debug:print("       CAM ROT : "+str(cam_rot))
        if debug:print("       VIEW FOCAL "+str(user_view_focal))
        if debug:print("       VIEW ORIENTATION "+str(user_view_orientation))
        Set_Scene(self,context,selected_scene)
        if debug:print("SETUP SCENE = SUCCES")
        
        # START GENERATE OBJECT PREVIEW HERE
        for obj in objs:
            # if debug:print("_____________________________________________")
            # if debug:print("LOOP: "+obj.name)
            try:
                #if debug:print("RENDER:")
                
                # LINK OBJ TO kh SCENE AND SET SCENE
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.make_links_scene(scene=selected_scene)
                bpy.context.window.scene = bpy.data.scenes[selected_scene]
                #if debug:print("        SETUP = SUCCES")

                # SETUP CAMERA IF USE CURRENT VIEW IS TRUE
                Set_Camera(self, context, cam_rot, user_view_orientation, user_view_focal)
                #if debug:print("        SET CAMERA = SUCCES")

                # RENDER PREVIEW
                image_path = Render_Preview(self, context, obj,render_device1, user_view_orientation)
                #if debug:print("        RENDER = SUCCES")
                #if debug:print("        PATH   = "+image_path)
                
                Set_Preview(self, context,obj,image_path)
                #if debug:print("        SET PREVIEW = SUCCES")

                if debug:print("        SAVE EXTERNAL = " + str(pref.save_preview))
                if pref.save_preview == True:
                    Save_Preview_External(self, context, image_path)
                    if debug:print("        SAVE EXTERNAL = SUCCES")

                # REMOVE OBJ
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.delete(use_global=False)

                os.remove(image_path+".png")
                bpy.context.window.scene = original_scene
                if debug:print("        RESTORE SCENE = SUCCES")

            except: 
                print("RENDER FAIL : "+obj.name)
                bpy.context.window.scene = original_scene
        
        Clean_Scene(self, context, selected_scene, original_scene)
        if debug:print("SCENE CLEAN = SUCCES")

        for ob in objs:
            ob.select_set(True)

        return{'FINISHED'}
    
#bagabatch_ui//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
from pathlib import Path

if not hasattr(bpy.types.Scene, "folder_props"):
    bpy.types.Scene.folder_props = {}

class KH_UL_assetslib_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text=item.name)

# FILE EXPLORER
class KH_OT_select_folder(bpy.types.Operator):
    bl_idname = "kh.select_folder"
    bl_label = "Select Folder"
    
    folder_path: bpy.props.StringProperty()
    entry_path: bpy.props.StringProperty()
    prop_id: bpy.props.StringProperty()

    def execute(self, context):
        pref = get_addon_preferences_safe(context)
        pref.save_path = self.folder_path
        
        bpy.ops.bagabatch.toggle_folder('INVOKE_DEFAULT', folder_path=self.entry_path, prop_id=self.prop_id)

        return {'FINISHED'}

class KH_OT_toggle_folder(bpy.types.Operator):
    bl_idname = "kh.toggle_folder"
    bl_label = "Toggle Folder View"

    folder_path: bpy.props.StringProperty()
    prop_id: bpy.props.StringProperty()

    def execute(self, context):
        bpy.types.Scene.folder_props[self.prop_id] = not bpy.types.Scene.folder_props[self.prop_id]
        return {'FINISHED'}

def draw_folder_hierarchy(layout, path, level=0,next_lvl=2):
    pref = get_addon_preferences_safe(bpy.context)
    if os.path.exists(path):
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    # utiliser chemin complet pour éviter les souci de noms
                    prop_id = f"folder_props['{entry.path}']"
                    if prop_id not in bpy.types.Scene.folder_props:
                        bpy.types.Scene.folder_props[prop_id] = False
                    has_subfolders = any(os.path.isdir(os.path.join(entry.path, d)) for d in os.listdir(entry.path))

                    col = layout.column(align=True)
                    split = col.split(factor=0.05)

                    col_toogle = split.column(align=True).column(align=True)
                    col_toogle.alignment = 'RIGHT'

                    col_new =split.column(align=True).column(align=True)
                    row = col_new.row(align=True)

                    if level < next_lvl and has_subfolders:
                        # bouton pour show/hide les sous-dossiers
                        icon = 'TRIA_RIGHT' if not bpy.types.Scene.folder_props[prop_id] else 'TRIA_DOWN'
                        op = col_toogle.operator("kh.toggle_folder", text="", icon=icon, emboss=False)
                        op.folder_path = entry.path
                        op.prop_id = prop_id
                    else:
                        col_toogle.label(text="  ")

                    
                    is_selected= False
                    if pref.save_path==entry.path:
                        is_selected= True
                    row.alignment = 'LEFT'
                    oz=row.operator("kh.select_folder", text=entry.name, depress  = is_selected, emboss=is_selected)
                    oz.folder_path = entry.path
                    oz.entry_path=entry.path
                    oz.prop_id=prop_id
                    
                    if bpy.types.Scene.folder_props[prop_id]:
                        draw_folder_hierarchy(col_new, entry.path, level + 1,next_lvl+1)

# CONVERT TXT TO catalog_data = 'uuid': uuid / 'path': path / 'name': name
def load_catalog_data(file_path):
    catalog_data = []
    file_path_with_name = os.path.join(file_path, "blender_assets.cats.txt")
    if os.path.exists(file_path_with_name) == False:
        return None
    with open(file_path_with_name, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split(':')
                if len(parts) == 3:
                    uuid, path, _ = parts
                    name = path.split('/')[-1].split('-')[-1]
                    catalog_data.append({
                        'uuid': uuid,
                        'path': path,
                        'name': name
                    })
    if catalog_data == []:
        return None
    else:
        return catalog_data

# CATALOG
class KH_OT_toggle_catalog(bpy.types.Operator):
    bl_idname = "kh.toggle_catalog"
    bl_label = "Toggle Folder View"

    path: bpy.props.StringProperty()

    def execute(self, context):
        pref = get_addon_preferences_safe(context)
        
        list_cats_open = pref.cats_expand.split(";")
        if self.path in list_cats_open:
            list_cats_open.remove(self.path)
            pref.cats_expand = ";".join(list_cats_open)
        else:
            pref.cats_expand += self.path + ";"
        return {'FINISHED'}

class KH_OT_select_catalog(bpy.types.Operator):
    bl_idname = "kh.select_catalog"
    bl_label = "Toggle Folder View"

    path: bpy.props.StringProperty()
    uuid: bpy.props.StringProperty()

    def execute(self, context):
        pref = get_addon_preferences_safe(context)
        pref.target_catalog = self.path
        pref.uuid = str(self.uuid)
        return {'FINISHED'}

def draw_catalog(layout, catalog_data, target_level=0, path="", draw=True):
    pref = get_addon_preferences_safe(bpy.context)
    sublevel=False
    for cats in catalog_data:
        
        current_level = cats['path'].count('/')
        
        if current_level == target_level and path in cats['path']:
            list_cats_open = pref.cats_expand.split(";")
            if path in list_cats_open or draw==True:
                embled = pref.target_catalog == cats['path']
                column = layout.column(align=True)
                split = column.split(factor=0.15*(current_level+1), align=True)
                
                row_top = split.row(align=True)
                row_bottom = split.row(align=True)   

                op = row_bottom.operator("kh.select_catalog", text=cats['name'], depress=embled, emboss=embled)
                op.path = cats['path']
                op.uuid = cats['uuid']

                if cats['path'] in list_cats_open:
                    icon = 'TRIA_DOWN'
                else:
                    sublev = False
                    icon = 'TRIA_RIGHT'
                sublev = draw_catalog(layout, catalog_data, target_level=target_level+1,path=cats['path'], draw=False)

                if sublev:
                    rocol = row_top.column(align=True)
                    split = rocol.split(factor=0.6, align=True)
                    row_top_bis = split.row(align=True)
                    row_bottom_bis = split.row(align=True)
                    row_bottom_bis.operator("kh.toggle_catalog",text="", icon=icon,emboss=False).path=cats['path']

            sublevel=True

    return sublevel

class KH_OT_set_asset_type(bpy.types.Operator):
    bl_idname = "kh.set_asset_type"
    bl_label = "Set Asset Type"
    type: bpy.props.StringProperty()
    def execute(self, context):
        pref = get_addon_preferences_safe(context)
        pref.export_type = self.type
        return {'FINISHED'}

class KH_OT_restore_scene(bpy.types.Operator):
    bl_idname = "kh.restore_scene"
    bl_label = "Restore Scene After Crash"
    def execute(self, context):
        for scn in bpy.data.scenes:
            if not scn.name.startswith("TEMP_BB_"):
                Clean_Scene(self, context, bpy.context.scene.name, scn)
                return {'FINISHED'}
        Warning("No Scene Found", "Error")
        return {'FINISHED'}


#bagabatch_utils//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class KH_tooltips(bpy.types.Operator):
    """Display a tooltips"""
    bl_idname = "kh.tooltips"
    bl_label = "Display Tooltip"

    message: bpy.props.StringProperty(default="None")
    title: bpy.props.StringProperty(default="Tooltip")
    icon: bpy.props.StringProperty(default="INFO")
    size: bpy.props.IntProperty(default=50)
    url: bpy.props.StringProperty(default="None")

    def execute(self, context):
        Tooltip(self.message, self.title, self.icon, self.size, self.url) 
        return {'FINISHED'}

def Tooltip(message = "", title = "Message Box", icon = 'INFO', size = 50, url = "None"):

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        # DIRTY LAZY CODE START
        count = 0
        mess = message
        length = int(size)
        caracter = length
        temp = 0
        for i in message:            
            if count == 0:
                if mess[0] == " ":
                    o = length
                    if len(mess) > o:
                        while mess[o] != " ":
                            o += 1
                            if len(mess) == o:
                                break
                    col.label(text=mess[1:o])
                    caracter = length

                elif mess == message:
                    o = length
                    if o >= len(mess):
                        o = len(mess)-1
                    while message[o] != " ":
                        o += 1
                        if len(mess) == o:
                            break
                    col.label(text=mess[0:o])
                    caracter = length                    
                else :
                    count = temp
                    caracter += 1
            count += 1
            temp = count
            mess = mess[1:]
            if count == caracter:
                count = 0
        # DIRTY LAZY CODE END
        if url != "None":
            col.separator(factor = 1.5)
            row = col.row()
            row.scale_y = 2
            row.operator("wm.url_open", text="Video Demo", icon = 'PLAY', depress = False).url = url
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
def Warning(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


preview_collections1 = {}

# ============= Library Organizer =============
# أداة تنظيم المكتبة - نقل الأصول إلى مجلدات حسب الكاتيجوري

# سكريبت Python لقراءة كاتيجوري الأصول من ملف blend
CATALOG_READER_SCRIPT = '''
import bpy
import sys
import json

blend_file = sys.argv[-1]
result = {"catalogs": [], "error": None}

try:
    bpy.ops.wm.open_mainfile(filepath=blend_file)
    
    for obj in bpy.data.objects:
        if obj.asset_data and obj.asset_data.catalog_simple_name:
            result["catalogs"].append(obj.asset_data.catalog_simple_name)
    
    # Remove duplicates
    result["catalogs"] = list(set(result["catalogs"]))
except Exception as e:
    result["error"] = str(e)

print("CATALOG_RESULT:" + json.dumps(result))
'''


class KH_OT_organize_library(bpy.types.Operator):
    """تنظيم مكتبة الأصول - نقل الملفات إلى مجلدات حسب الكاتيجوري"""
    bl_idname = "kh.organize_library"
    bl_label = "Organize Asset Library"
    bl_description = "Move blend files to folders matching their asset catalog (uses background process)"
    bl_options = {'REGISTER'}
    
    library_path: bpy.props.StringProperty(
        name="Library Path",
        description="Path to the asset library",
        subtype='DIR_PATH'
    )
    
    _timer = None
    _files_to_process = []
    _current_index = 0
    _total_files = 0
    _moved_count = 0
    _skipped_count = 0
    _error_count = 0
    _is_running = False
    _current_process = None
    _current_file = None
    _script_path = None
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            # التحقق من انتهاء العملية الحالية
            if self._current_process is not None:
                poll = self._current_process.poll()
                if poll is not None:
                    # العملية انتهت
                    self.handle_process_result(context)
                    self._current_process = None
                    self._current_index += 1
                return {'PASS_THROUGH'}
            
            # بدء معالجة الملف التالي
            if self._current_index < self._total_files:
                self.start_process_file(context)
                
                progress = (self._current_index / self._total_files) * 100
                context.workspace.status_text_set(
                    f"Organizing: {self._current_index}/{self._total_files} ({progress:.1f}%) | Moved: {self._moved_count} | Errors: {self._error_count}"
                )
            else:
                self.finish(context)
                return {'FINISHED'}
        
        elif event.type == 'ESC':
            self.cancel(context)
            return {'CANCELLED'}
        
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        import os
        import tempfile
        
        print(f"[Library Organizer] Starting with path: {self.library_path}")
        
        if not self.library_path or not os.path.exists(self.library_path):
            self.report({'ERROR'}, "Please select a valid library path")
            return {'CANCELLED'}
        
        # إنشاء ملف السكريبت المؤقت
        self._script_path = os.path.join(tempfile.gettempdir(), "kh_catalog_reader.py")
        with open(self._script_path, 'w', encoding='utf-8') as f:
            f.write(CATALOG_READER_SCRIPT)
        
        print(f"[Library Organizer] Script created at: {self._script_path}")
        
        # جمع كل ملفات blend
        self._files_to_process = []
        for root, dirs, files in os.walk(self.library_path):
            for file in files:
                if file.endswith('.blend'):
                    self._files_to_process.append(os.path.join(root, file))
        
        self._total_files = len(self._files_to_process)
        print(f"[Library Organizer] Found {self._total_files} blend files")
        
        if self._total_files == 0:
            self.report({'WARNING'}, "No blend files found in library")
            return {'CANCELLED'}
        
        self._current_index = 0
        self._moved_count = 0
        self._skipped_count = 0
        self._error_count = 0
        self._is_running = True
        self._current_process = None
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        
        self.report({'INFO'}, f"Starting organization of {self._total_files} files...")
        context.workspace.status_text_set(f"Starting library organization... ({self._total_files} files)")
        
        return {'RUNNING_MODAL'}
    
    def start_process_file(self, context):
        """بدء معالجة ملف في الخلفية"""
        import subprocess
        import sys
        
        if self._current_index >= len(self._files_to_process):
            return
        
        self._current_file = self._files_to_process[self._current_index]
        
        # الحصول على مسار Blender
        blender_path = bpy.app.binary_path
        
        try:
            # تشغيل Blender في الخلفية لقراءة الكاتيجوري
            self._current_process = subprocess.Popen(
                [blender_path, '--background', '--python', self._script_path, '--', self._current_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        except Exception as e:
            print(f"Error starting process for {self._current_file}: {e}")
            self._error_count += 1
            self._current_process = None
    
    def handle_process_result(self, context):
        """معالجة نتيجة العملية"""
        import os
        import shutil
        import json
        
        if self._current_process is None or self._current_file is None:
            return
        
        try:
            stdout, stderr = self._current_process.communicate(timeout=1)
            
            # البحث عن النتيجة في الإخراج
            catalogs = []
            for line in stdout.split('\n'):
                if line.startswith('CATALOG_RESULT:'):
                    result_json = line.replace('CATALOG_RESULT:', '')
                    result = json.loads(result_json)
                    catalogs = result.get('catalogs', [])
                    break
            
            # إذا وجدنا كاتيجوري واحدة، ننقل الملف
            if len(catalogs) == 1:
                catalog_name = catalogs[0]
                self.move_file_to_catalog(self._current_file, catalog_name)
            elif len(catalogs) > 1:
                # أكثر من كاتيجوري - نستخدم الأولى
                catalog_name = catalogs[0]
                self.move_file_to_catalog(self._current_file, catalog_name)
            else:
                self._skipped_count += 1
                
        except Exception as e:
            print(f"Error handling result for {self._current_file}: {e}")
            self._error_count += 1
    
    def move_file_to_catalog(self, blend_path, catalog_name):
        """نقل الملف إلى مجلد الكاتيجوري"""
        import os
        import shutil
        
        current_folder = os.path.dirname(blend_path)
        current_folder_name = os.path.basename(current_folder)
        
        # التحقق من أن الملف ليس في المجلد الصحيح بالفعل
        if current_folder_name == catalog_name:
            self._skipped_count += 1
            return
        
        # إنشاء المجلد الهدف
        target_folder = os.path.join(self.library_path, catalog_name)
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        
        # نقل الملف
        file_name = os.path.basename(blend_path)
        new_path = os.path.join(target_folder, file_name)
        
        # التحقق من عدم وجود ملف بنفس الاسم
        if os.path.exists(new_path):
            base, ext = os.path.splitext(file_name)
            counter = 1
            while os.path.exists(new_path):
                new_path = os.path.join(target_folder, f"{base}_{counter}{ext}")
                counter += 1
        
        try:
            shutil.move(blend_path, new_path)
            self._moved_count += 1
        except Exception as e:
            print(f"Error moving file: {e}")
            self._error_count += 1
    
    def finish(self, context):
        """إنهاء العملية"""
        import os
        
        wm = context.window_manager
        if self._timer:
            wm.event_timer_remove(self._timer)
        
        # حذف ملف السكريبت المؤقت
        if self._script_path and os.path.exists(self._script_path):
            try:
                os.remove(self._script_path)
            except:
                pass
        
        context.workspace.status_text_set(None)
        self._is_running = False
        
        self.report({'INFO'}, 
            f"Done! Moved: {self._moved_count}, Skipped: {self._skipped_count}, Errors: {self._error_count}")
    
    def cancel(self, context):
        """إلغاء العملية"""
        import os
        
        wm = context.window_manager
        if self._timer:
            wm.event_timer_remove(self._timer)
        
        # إيقاف العملية الحالية
        if self._current_process:
            try:
                self._current_process.terminate()
            except:
                pass
        
        # حذف ملف السكريبت المؤقت
        if self._script_path and os.path.exists(self._script_path):
            try:
                os.remove(self._script_path)
            except:
                pass
        
        context.workspace.status_text_set(None)
        self._is_running = False
        
        self.report({'WARNING'}, 
            f"Cancelled. Moved: {self._moved_count} files")


class KH_OT_select_library_to_organize(bpy.types.Operator):
    """اختيار مكتبة لتنظيمها"""
    bl_idname = "kh.select_library_organize"
    bl_label = "Select Library to Organize"
    bl_description = "Select an asset library folder to organize by catalog"
    
    directory: bpy.props.StringProperty(
        name="Directory",
        subtype='DIR_PATH'
    )
    
    def execute(self, context):
        if self.directory:
            bpy.ops.kh.organize_library('INVOKE_DEFAULT', library_path=self.directory)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class KH_PT_library_organizer(bpy.types.Panel):
    bl_idname = "KH_PT_library_organizer"
    bl_label = "Library Organizer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "KH-Tools"
    bl_parent_id = "OBJECT_PT_kh_asset_browser"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        row = box.row()
        row.label(text="Organize by Asset Catalog:", icon='FOLDER_REDIRECT')
        
        row = box.row()
        row.operator("kh.select_library_organize", 
                    text="Select Library & Organize", 
                    icon='FILE_REFRESH')
        
        col = box.column()
        col.label(text="• Reads actual catalog from assets", icon='INFO')
        col.label(text="• Moves files to matching folders", icon='INFO')
        col.label(text="• Press ESC to cancel", icon='INFO')


classes = (
    #asset/////////////////////////////
    kh_ASSET_PANEL,
    kh_ASSET_BROWSER_PANEL,  # القائمة الجديدة لـ Asset Browser
    KH_ORIGIN,
    kh_copy_object,
    KH_AddCurtain,  # إضافة كلاس الستائر
    OBJECT_OT_StartFrame,
    DeleteLocationKeyframesOperator,
    transform_apply,
    KH_OT_saveasset,
    KH_OT_savematerial,
    KH_OT_make_materials_assets,
    KH_OT_update_materials_list,
    KH_OT_skipped_materials_dialog,
    KH_OT_auto_rename_skipped,
    KH_OT_reset_skipped_names,
    KH_MaterialItem,
    KH_SkippedMaterialItem,
    KH_UL_selected_materials_list,
    KH_UL_skipped_materials_list,
    KH_UL_saveasset_list,
    KHLibrary,

    # Asset//////////////////////////////////////////////
    # BAGABATCH_PT_Panel,
    #BAGABATCH_Preferences,
    KH_OP_batch_preview,
    KH_OP_batch_coll_preview,
    KH_UL_assetslib_list,
    KH_OT_select_folder,
    KH_OT_toggle_folder,
    KH_OT_toggle_catalog,
    KH_OT_select_catalog,
    KH_OT_set_asset_type,
    KH_OT_restore_scene,
    KH_tooltips,
    IMPORT_OT_blend_files_operator,
    KH_OT_organize_library,
    KH_OT_select_library_to_organize,
    KH_PT_library_organizer,
    #AssetBlendCategoryOperator,
    )

# Register
def register():
    for cls in classes:    
        bpy.utils.register_class(cls)
    ## KH-Asset////////////////////////////////////////////////////////////////////////
    
    WindowManager.scene_previews1 = EnumProperty(
        items=enum_previews_from_directory_items1,
    )
    pcoll = bpy.utils.previews.new()
    pcoll.scene_previews_dir = ""
    pcoll.scene_previews1 = ()
    
    bpy.types.Scene.render_device1 = bpy.props.EnumProperty(
        items=[
            ('GPU', "GPU", ""),
            ('CPU', "CPU", "")
        ],
        name="Render Device",
        description="Choose the device for Cycles rendering"
    )



    preview_collections1["main"] = pcoll

    bpy.types.Scene.selected_folder = bpy.props.StringProperty()
    bpy.types.Scene.active_lib_path = bpy.props.StringProperty()

    # خصائص قائمة المواد المحددة
    bpy.types.Scene.kh_selected_materials = bpy.props.CollectionProperty(type=KH_MaterialItem)
    bpy.types.Scene.kh_selected_materials_index = bpy.props.IntProperty(default=0)

    # خصائص قائمة المواد المتخطاة
    bpy.types.Scene.kh_skipped_materials = bpy.props.CollectionProperty(type=KH_SkippedMaterialItem)
    bpy.types.Scene.kh_skipped_materials_index = bpy.props.IntProperty(default=0)

    # خاصية التحكم في كولكشن الستائر
    bpy.types.Scene.kh_use_curtain_collection = bpy.props.BoolProperty(
        name="Use Curtains Collection",
        description="وضع الستائر في كولكشن Curtains منفصل",
        default=True
    )
   
    make_asset.register()

# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # إزالة خصائص قائمة المواد المحددة
    del bpy.types.Scene.kh_selected_materials
    del bpy.types.Scene.kh_selected_materials_index

    # إزالة خصائص قائمة المواد المتخطاة
    del bpy.types.Scene.kh_skipped_materials
    del bpy.types.Scene.kh_skipped_materials_index

    # إزالة خاصية كولكشن الستائر
    if hasattr(bpy.types.Scene, 'kh_use_curtain_collection'):
        del bpy.types.Scene.kh_use_curtain_collection
    #KH-Asset////////////////////////////////////////////////////////////////////////////////////////

    # التحقق من وجود الخصائص قبل حذفها لتجنب الأخطاء
    if hasattr(WindowManager, 'scene_previews1'):
        del WindowManager.scene_previews1

    for pcoll in preview_collections1.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections1.clear()

    if hasattr(bpy.types.Scene, 'render_device1'):
        del bpy.types.Scene.render_device1
    if hasattr(bpy.types.Scene, 'selected_folder'):
        del bpy.types.Scene.selected_folder
    if hasattr(bpy.types.Scene, 'active_lib_path'):
        del bpy.types.Scene.active_lib_path
    if hasattr(bpy.types.Scene, 'selected'):
        del bpy.types.Scene.selected

    make_asset.unregister()


   

if __name__ == "__main__":
    register()
