import bpy
import os
import ctypes  # لإظهار رسالة في ويندوز
from datetime import datetime
from datetime import timedelta
from bpy.app import handlers

from bpy.props import StringProperty, IntProperty
from bpy.types import Operator, Panel
from bpy_extras.io_utils import ImportHelper

# دالة مساعدة للبحث عن إعدادات الإضافة
def get_addon_preferences(context, preference_name):
    """
    البحث عن إعدادات الإضافة في المسارات المختلفة
    """
    try:
        # محاولة البحث بالاسم الافتراضي
        addon = context.preferences.addons['KH-Tools']
        if hasattr(addon.preferences, preference_name):
            return getattr(addon.preferences, preference_name)
    except KeyError:
        try:
            # محاولة البحث باسم المجلد الحالي
            addon = context.preferences.addons['kh_tools']
            if hasattr(addon.preferences, preference_name):
                return getattr(addon.preferences, preference_name)
        except KeyError:
            try:
                # البحث في جميع الإضافات المحملة
                for addon_name in context.preferences.addons.keys():
                    if 'kh' in addon_name.lower() or 'tools' in addon_name.lower():
                        addon = context.preferences.addons[addon_name]
                        if hasattr(addon.preferences, preference_name):
                            return getattr(addon.preferences, preference_name)
            except:
                pass
    # إرجاع True كقيمة افتراضية إذا لم يتم العثور على الإعداد
    return True

# initail global variable timer
ti_init = None
ti_start = None
ti_complete = None
ti_cancel = None
rt_init_render = None
rt_one_frame = None
rt_info = "[MDSANIMA RT]"

@handlers.persistent
def kh_rt_init(dummy):
    global ti_init
    ti_init = datetime.now()
    print(rt_info, "->", str(ti_init).ljust(26), "=> Render Init")


@handlers.persistent
def kh_rt_start(dummy):
    global ti_start
    global rt_init_render
    ti_start = datetime.now()
    rt_init_render = ti_start - ti_init
    print(rt_info, "->", str(ti_start).ljust(26), "=> Render Start")
    print(rt_info, "->", "RT Initialization =>", rt_init_render)


@handlers.persistent
def kh_rt_complete(dummy):
    global ti_complete
    global rt_one_frame
    ti_complete = datetime.now()
    rt_one_frame = ti_complete - ti_start
    print(rt_info, "->", str(ti_complete).ljust(26), "=> Render Complete")
    print(rt_info, "->", "RT One Frame =>", rt_one_frame)


@handlers.persistent
def kh_rt_cancel(dummy):
    global ti_cancel
    global rt_one_frame
    ti_cancel = datetime.now()
    rt_one_frame = ti_cancel - ti_start
    print(rt_info, "->", str(ti_cancel).ljust(26), "=> Render Cancel")
    print(rt_info, "->", "RT One Frame =>", rt_one_frame)
    
    
def Plant_animation():  
    if bpy.context.active_object and bpy.context.active_object.type == 'MESH':
        selected_obj = bpy.context.active_object
        if selected_obj.material_slots:
            bpy.ops.kh.transform_apply()
            Delete_Plant_animation()
            used_materials = set(slot.material for slot in selected_obj.material_slots if slot.material)
                    
            modifier1 = selected_obj.modifiers.new(name="SimpleDeform1", type='SIMPLE_DEFORM')
            modifier1.deform_method = 'BEND'
            modifier1.angle = 0 
            bpy.context.scene.frame_set(0)
            modifier1.keyframe_insert(data_path='angle')
            
            selected_obj.select_set(True)
            bpy.context.view_layer.objects.active = selected_obj
            
            original_context = bpy.context.area.type
            bpy.context.area.type = 'GRAPH_EDITOR'
            bpy.ops.graph.fmodifier_add(type='NOISE')
            fmodifier = selected_obj.animation_data.action.fcurves[-1].modifiers[-1]
            fmodifier.scale = 100
            fmodifier.strength = 1
            bpy.context.area.type = original_context
            
            empty_name = selected_obj.name + "m"
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=selected_obj.location)
            empty_obj = bpy.context.active_object
            empty_obj.name = empty_name
            empty_obj.rotation_euler = (0, 0, 0)
            empty_obj.keyframe_insert(data_path='rotation_euler', frame=0, index=2)
            empty_obj.select_set(True)
            
            bpy.context.view_layer.objects.active = empty_obj
            original_context = bpy.context.area.type
            bpy.context.area.type = 'GRAPH_EDITOR'
            bpy.ops.graph.fmodifier_add(type='NOISE')
            fmodifier = empty_obj.animation_data.action.fcurves[-1].modifiers[-1]
            fmodifier.scale = 200
            fmodifier.strength = 1
            bpy.context.area.type = original_context

            selected_obj.select_set(True)
            empty_obj.select_set(True)
            bpy.context.view_layer.objects.active = selected_obj
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            
            for material in used_materials:
                vertex_group = selected_obj.vertex_groups.new(name=material.name)
                vertices = []
                for poly in selected_obj.data.polygons:
                    if poly.material_index == selected_obj.material_slots.find(material.name):
                        vertices.extend(poly.vertices)
                vertex_group.add(vertices, 1.0, 'REPLACE')

                displace_modifier = selected_obj.modifiers.new(name=material.name, type='DISPLACE')
                displace_modifier.vertex_group = material.name 
                displace_modifier.strength = 0.1 
                displace_modifier.texture_coords = 'OBJECT'
                displace_modifier.texture_coords_object = empty_obj
 
                texture = bpy.data.textures.new(name="T"+material.name, type='CLOUDS')
                displace_modifier.texture = texture


def Delete_Plant_animation():
    if bpy.context.active_object and bpy.context.active_object.type == 'MESH':
        selected_obj = bpy.context.active_object
        if selected_obj.material_slots:
            used_materials = set(slot.material for slot in selected_obj.material_slots if slot.material)
            # حذف أي موديفاير من النوع "DISPLACE"
            for modifier in selected_obj.modifiers:
                if modifier.type == 'SIMPLE_DEFORM':
                    selected_obj.modifiers.remove(modifier)

            for modifier in selected_obj.modifiers:
                if modifier.type == 'DISPLACE':
                    selected_obj.modifiers.remove(modifier)

            for group in selected_obj.vertex_groups:
                selected_obj.vertex_groups.remove(group)
            
            empty_name = selected_obj.name + "m"
            empty_obj = bpy.data.objects.get(empty_name)
            if empty_obj:
                bpy.data.objects.remove(empty_obj)
                
        if selected_obj.animation_data:   
            for fcurve in selected_obj.animation_data.action.fcurves:
                selected_obj.animation_data.action.fcurves.remove(fcurve)
        bpy.ops.outliner.orphans_purge(do_recursive=True)
        

def FOLLOW_PATH():        
    if bpy.context.object is not None:
        selected_obj = bpy.context.active_object
        constraint = selected_obj.constraints.new(type='FOLLOW_PATH')
        constraint.name = selected_obj.name
        constraint.up_axis = 'UP_Z'
        constraint.use_curve_follow = True
        constraint.use_curve_radius = True
        constraint.use_fixed_location = True
        constraint.offset_factor = 0 
        
        bpy.context.scene.frame_set(0)
        constraint.keyframe_insert(data_path='offset_factor')
        selected_obj.select_set(True)
        bpy.context.view_layer.objects.active = selected_obj
        original_context = bpy.context.area.type
        bpy.context.area.type = 'GRAPH_EDITOR'
        bpy.ops.graph.fmodifier_add(type='GENERATOR')
        fmodifier = selected_obj.animation_data.action.fcurves[-1].modifiers[-1]
        fmodifier.coefficients[1] = 0.01
        bpy.context.area.type = original_context
        path_name = "P"+bpy.context.active_object.name
        if path_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[path_name], do_unlink=True)
        location = selected_obj.location
        locationx = 2
        new_path_name = "P"+selected_obj.name
        bpy.ops.curve.primitive_nurbs_path_add(radius=1, location=location)
        bpy.context.active_object.name = new_path_name
         # الآن يجب العثور على كائن المسار المناسب وتعيينه كهدف
        path_object = bpy.data.objects[new_path_name]
        path_object.location[0] += locationx
        constraint.target = path_object
        selected_obj.location[0] = 0
        selected_obj.location[1] = 0
        selected_obj.location[2] = 0
        if selected_obj.type == 'CAMERA':
            selected_obj.rotation_euler[0] = 1.5708
            selected_obj.rotation_euler[1] = 0
            selected_obj.rotation_euler[2] = 0
            selected_obj.lock_location[0] = True
            selected_obj.lock_location[1] = True
            selected_obj.lock_location[2] = True
            selected_obj.lock_rotation[0] = True
            selected_obj.lock_rotation[1] = True
            selected_obj.lock_rotation[2] = True
            
        selected_obj.select_set(True)
        bpy.context.view_layer.objects.active = selected_obj
        
def DELETE_FOLLOW_PATH():
    selected_obj = bpy.context.active_object
    if selected_obj.type == 'CAMERA':
    #            selected_obj.rotation_euler[0] = 1.5708
    #            selected_obj.rotation_euler[1] = 0
    #            selected_obj.rotation_euler[2] = 0
        selected_obj.lock_location[0] = False
        selected_obj.lock_location[1] = False
        selected_obj.lock_location[2] = False
        selected_obj.lock_rotation[0] = False
        selected_obj.lock_rotation[1] = False
        selected_obj.lock_rotation[2] = False
        
    for constraint in selected_obj.constraints:
        if constraint.type == 'FOLLOW_PATH':
            selected_obj.constraints.remove(constraint)
    PATH_name = "P"+selected_obj.name 
    PATH_obj = bpy.data.objects.get(PATH_name)
    if PATH_obj:
        if selected_obj.type == 'CAMERA':
            selected_obj.location[0] = PATH_obj.location[0]
            selected_obj.location[1] = PATH_obj.location[1]
            selected_obj.location[2] = PATH_obj.location[2]
            #selected_obj.rotation_euler[0] = PATH_obj.rotation_euler[0]
            #selected_obj.rotation_euler[1] = PATH_obj.rotation_euler[1]
            selected_obj.rotation_euler[2] = PATH_obj.rotation_euler[2] -1.5708
        bpy.data.objects.remove(PATH_obj)
        
    if selected_obj.animation_data:   
        for fcurve in selected_obj.animation_data.action.fcurves:
            selected_obj.animation_data.action.fcurves.remove(fcurve)
    bpy.ops.outliner.orphans_purge(do_recursive=True)


                 
# class//////////////////////////////////////////////////////////////////////////////////////         

class kh_Keyframe_Creator_Operator(bpy.types.Operator):
    bl_idname = "object.kh_keyframe_creator"
    bl_label = "add Keyframe"
        
    def execute(self, context):
        selected_object = bpy.context.active_object
        if selected_object is not None:
            selected_object.keyframe_insert(data_path="location", frame=bpy.context.scene.frame_current)
            selected_object.keyframe_insert(data_path="rotation_euler", frame=bpy.context.scene.frame_current)
            selected_object.keyframe_insert(data_path="scale", frame=bpy.context.scene.frame_current)
        return {'FINISHED'}

class kh_Delete_Keyframe_Creator_Operator(bpy.types.Operator):
    bl_idname = "object.kh_delete_keyframe_creator"
    bl_label = "Delete Keyframe"
        
    def execute(self, context):
        selected_object = bpy.context.active_object
        if selected_object is not None:
            selected_object.animation_data_clear()
        return {'FINISHED'}
    
    
class kh_camera_timeline_markers(bpy.types.Operator):
    bl_idname = "object.kh_camera_timeline_markers"
    bl_label = "Camera Marker"
    bl_description = "Add Camera Marke"
    
    def execute(self, context):
        active_camera = bpy.context.scene.camera
        if active_camera is not None:
            camera_name = active_camera.name
            marker = bpy.context.scene.timeline_markers.new(name=camera_name, frame=bpy.context.scene.frame_current)
            marker.camera = active_camera
            print("Camera marker created at frame", bpy.context.scene.frame_current, "with name", camera_name)

        return {'FINISHED'}
    
class kh_delete_camera_timeline_markers(bpy.types.Operator):
    bl_idname = "object.kh_delete_camera_timeline_markers"
    bl_label = "Delete Camera Marken"
    bl_description = "Delete Camera Marken"
    
    def execute(self, context):
        active_camera = bpy.context.scene.camera
        if active_camera is not None:
            camera_name = active_camera.name
            for marker in bpy.context.scene.timeline_markers:
                if marker.name == camera_name:
                    bpy.context.scene.timeline_markers.remove(marker)

        return {'FINISHED'}

        
class kh_Plant_animation_Operator(bpy.types.Operator):
    bl_idname = "object.kh_plant_animation"
    bl_label = "Plant animation"
    bl_description = "Add Plant animation"
    
    def execute(self, context):
        Plant_animation()
        return {'FINISHED'}

class kh_delete_Plant_animation_Operator(bpy.types.Operator):
    bl_idname = "object.kh_delete_plant_animation"
    bl_label = "Delete Plant animation"
    bl_description = "Delete Plant animation"
    
    def execute(self, context):
        Delete_Plant_animation()
        return {'FINISHED'}
    
class kh_Follow_path_Operator(bpy.types.Operator):
    bl_idname = "object.kh_follow_path"
    bl_label = "Follow path"
    bl_description = "Add Follow path"
    
    def execute(self, context):
        FOLLOW_PATH()
        return {'FINISHED'}

class kh_delete_Follow_path_Operator(bpy.types.Operator):
    bl_idname = "object.kh_delete_follow_path"
    bl_label = "Delete Follow path"
    bl_description = "Delete Follow path"

    def execute(self, context):
        DELETE_FOLLOW_PATH()
        return {'FINISHED'}
    

# Panel////////////////////////////////////////////////////////////////////////////////////// 
class kh_AnimationPanel(bpy.types.Panel):
    bl_label = "Animation"
    bl_idname = "KH_PT_kh_AnimationPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'KH-Tools'
    bl_options = {'DEFAULT_CLOSED'} 
    
    @classmethod
    def poll(cls, context):
        # استخدام الدالة المساعدة للبحث عن إعدادات الإضافة
        return get_addon_preferences(context, 'KH_Animation') == True
    
    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(text="", icon="RENDER_ANIMATION")
        except KeyError:
            pass
    def draw(self, context):
        pass

         
         
class kh_Animation_Panel1(bpy.types.Panel):
    bl_label = ""
    bl_idname = "KH_PT_kh_Animation_Panel1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'KH-Tools'
    bl_parent_id   = "KH_PT_kh_AnimationPanel"
    
    @classmethod
    def poll(cls, context):
        # استخدام الدالة المساعدة للبحث عن إعدادات الإضافة
        return get_addon_preferences(context, 'KH_Animation') == True
    
    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(text="Tools", icon="ARMATURE_DATA")
            last_render_time = context.scene.kh_my_addon_props.last_render_time
            frame_end = context.scene.frame_end
            frame_current = context.scene.frame_current
            if frame_current ==1:
                frame_current = 1-context.scene.frame_current
            frame_time_in_seconds = last_render_time * (frame_end - frame_current)
            frame_time_in_m = (frame_time_in_seconds)/60
            frame_time_in_h = (frame_time_in_m)/ 60
            frame_time_in_d = (frame_time_in_h)/ 24
            if frame_time_in_m <60:
                self.layout.label(text=f"{frame_time_in_m:.2f}m", icon="TIME")
            else:
                if frame_time_in_h<24:
                    self.layout.label(text=f"{frame_time_in_h:.2f}h", icon="TIME")
                else:
                    self.layout.label(text=f"{frame_time_in_d:.2f}D", icon="TIME")
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout
        
        #layout.prop(context.scene.render, "use_viewport")
        
        box = layout.box()
        row = box.row()
        row.scale_y = 1.3
        row.operator("render.render", text="Render Animation", icon="RENDER_ANIMATION").animation = True
        row = box.row()
        row.operator(ExportAnimationOperator.bl_idname, text="Image TO Video", icon="FILE_FOLDER")
        
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "frame_current", text="Frame")
        row.prop(context.scene.kh_my_addon_props, "last_render_time", text="Time", icon="TIME")
        row = box.row()
        row.operator("object.kh_keyframe_creator", text="Add Keyframe", icon="ANIM")
        if context.active_object is not None:
            if context.active_object.animation_data is not None:
                row.operator("object.kh_delete_keyframe_creator", text="", icon="TRASH")
        row = box.row()
        row.operator("object.kh_camera_timeline_markers", text="Camera Marker", icon="OUTLINER_DATA_CAMERA")
        active_camera = bpy.context.scene.camera
        if active_camera is not None:
            markers = bpy.context.scene.timeline_markers
            marker_name = active_camera.name
            if marker_name in markers:
                row.operator("object.kh_delete_camera_timeline_markers", text="", icon="TRASH")
                
        box = layout.box()
        row = box.row()
        row.operator("object.kh_follow_path", text="Follow Path", icon="CON_FOLLOWPATH")
        selected_obj = context.object
        if selected_obj:
            follow_path_constraint = selected_obj.constraints.get(selected_obj.name)
            if follow_path_constraint:
                row.operator("object.kh_delete_follow_path", text="", icon="TRASH")
                row = box.row()
                if follow_path_constraint.type == 'FOLLOW_PATH':
                    row.prop(selected_obj.animation_data.action.fcurves[-1].modifiers[-1], "coefficients", index=1, text="Spead")
                #row.prop(follow_path_constraint, "up_axis")
            
        box = layout.box()
        row = box.row()
        row.operator("object.kh_plant_animation", text="Plant Animation", icon="STRANDS")
        selected_object = bpy.context.active_object
        if selected_object is not None and selected_object.type == 'MESH':
            modifiers = selected_object.modifiers
            displacement_modifiers = [modifier for modifier in modifiers if modifier.type == 'DISPLACE']
            if displacement_modifiers :
               row.operator("object.kh_delete_plant_animation", text="", icon="TRASH")
               row = box.row()
               row.prop(selected_obj.animation_data.action.fcurves[-1].modifiers[-1], "scale", index=1, text="scale")
               row = box.row()
               row.prop(selected_obj.animation_data.action.fcurves[-1].modifiers[-1], "strength", index=1, text="Spead")
               empty_name = selected_obj.name + "m"
               empty_obj = bpy.data.objects.get(empty_name)
               if empty_obj:
                   row = box.row()
                   row.label(text="Leaves :", icon="MODIFIER")
                   row = box.row()
                   row.prop(empty_obj.animation_data.action.fcurves[-1].modifiers[-1], "scale", index=1, text="scale")
                   row = box.row()
                   row.prop(empty_obj.animation_data.action.fcurves[-1].modifiers[-1], "strength", index=1, text="Spead")

            for displacement_modifier in displacement_modifiers:
                box = layout.box()
                row = box.row()
                row.prop(displacement_modifier, "name",text= "")
                row.prop(displacement_modifier, "strength")
        
        # box = layout.box()
        # row = box.row()
        # row.operator("object.start_frame", text="water Animation", icon='MOD_FLUIDSIM')        
        # box = layout.box()
        # row = box.row()
        # row.operator("object.start_frame", text="Car Animation", icon='AUTO')
        # if context.active_object is not None:
        #     obj = context.active_object
        #     if obj.animation_data is not None:
        #         for fcurve in obj.animation_data.action.fcurves:
        #             if fcurve.data_path == "location":
        #                 row.operator("object.kh_delete_location_keyframes",text="", icon='TRASH')
        #                 break
        
                
class kh_Animation_Settings_Panel(bpy.types.Panel):
    bl_label = ""
    bl_idname = "KH_PT_kh_Animation_Settings_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animation'
    bl_options = {'DEFAULT_CLOSED'} 
    bl_parent_id   = "KH_PT_kh_AnimationPanel"
    
    @classmethod
    def poll(cls, context):
        # استخدام الدالة المساعدة للبحث عن إعدادات الإضافة
        return get_addon_preferences(context, 'KH_Animation') == True
    
    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(text="Settings", icon="SETTINGS")
            frame_current = context.scene.frame_current
            frame_end = context.scene.frame_end
            if frame_current ==1:
                frame_current = 1-context.scene.frame_current
            fps = context.scene.render.fps
            if fps != 0:
                frame_time = (frame_end-frame_current )/ fps
                frame_time60 = ((frame_end-frame_current) / fps)/60
            if frame_time <60:
                self.layout.label(text=f" {frame_time:.2f}s", icon="FILE_MOVIE")
            else:
                self.layout.label(text=f" {frame_time60:.2f}m", icon="FILE_MOVIE") 
             
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        frame_end = context.scene.frame_end
        frame_start = context.scene.frame_start
        if frame_start ==1:
            frame_start = 1-context.scene.frame_start
        
        frame_current = context.scene.frame_current
        if frame_current ==1:
            frame_current = 1-context.scene.frame_current
            
        fps = context.scene.render.fps
        if fps != 0:
            frame_time1 = (frame_end-frame_start) / fps
            frame_time160 = ((frame_end-frame_start) / fps)/60
            if frame_time1 <60:
                row.label(text=f"Video :{frame_time1:.2f}s", icon="FILE_MOVIE")
            else:
                row.label(text=f"Video :{frame_time160:.2f}m", icon="FILE_MOVIE")  
     
        row = box.row()
        row.prop(context.scene.render, "resolution_x")
        row.prop(context.scene.render, "resolution_y")
        row = box.row()
        row.prop(context.scene, "frame_start")
        row.prop(context.scene, "frame_end")
        row = box.row()
        row.prop(context.scene.render, "fps")
        row.prop(context.scene, "frame_step")
        row = box.row()
        row.prop(context.scene.render, "resolution_percentage")  
        row.prop(context.scene.render, "use_persistent_data", toggle=True)
        # row = box.row()
        # row.prop(context.scene.render, "use_motion_blur", text="Motion Blur",icon= "SETTINGS", toggle=True)
        # if bpy.context.scene.render.use_motion_blur == True:
        #     row = box.row()
        #     row.prop(context.scene.render, "motion_blur_shutter", text="Motion Blur", toggle=True)
        row = box.row()
        row.prop(context.scene.render, "filepath")
        row = box.row()
        row.prop(context.scene.render.image_settings, "file_format")
        row = box.row()
        file_format = bpy.context.scene.render.image_settings.file_format
        if file_format == 'PNG':
            row.prop(context.scene.render.image_settings, "color_depth")
            row.prop(context.scene.render.image_settings, "compression")
        elif file_format == 'JPEG':
            row.prop(context.scene.render.image_settings, "quality")
        elif file_format == 'FFMPEG':
            row.prop(context.scene.render.ffmpeg, "constant_rate_factor")
            row = box.row()
            row.prop(context.scene.render.ffmpeg, "ffmpeg_preset")  # إضافة إعدادات ffmpeg_preset

        elif file_format == 'OPEN_EXR':  # إضافة هذا الشرط لصيغة الملف OPEN_EXR
            row.prop(context.scene.render.image_settings, "color_depth")
        elif file_format == 'OPEN_EXR' or file_format == 'OPEN_EXR_MULTILAYER':  # تحديث الشرط ليشمل OPEN_EXR_MULTILAYER
            row.prop(context.scene.render.image_settings, "color_depth")

#        scene = bpy.context.scene
#        if rt_init_render is None or rt_one_frame is None:
#            pass
#        else:
#            # initial variable calculation render time
#            ini_frame_rt = rt_init_render
#            sta_frames = scene.frame_start
#            end_frames = scene.frame_end
#            check_frame = 1 if sta_frames == 1 or sta_frames == 0 else 0
#            all_frames = (end_frames - sta_frames) + check_frame
#            one_frame_rt = rt_one_frame
#            all_frame_rt = one_frame_rt * all_frames
#            layout.separator()
#            row = layout.grid_flow(row_major=True,columns=2,even_columns=True,even_rows=True,align=False,)
#            row.label(text="RT One Frame", icon="OUTPUT")
#            row.label(text=str(one_frame_rt)[:-4])
#            row.label(text="RT All Frames", icon="FILE_MOVIE")
#            row.label(text=str(all_frame_rt)[:-4])



class kh_MyAddonProperties(bpy.types.PropertyGroup):
    last_render_time: bpy.props.FloatProperty(
        name="Last Render Time second",
        description="Enter the time of the last render time in seconds",
        default=0.0
    )     




# وظيفة للحصول على دقة الصورة الأولى من المجلد لتعيين دقة الرندر
def get_image_resolution(images_path):
    for image_name in os.listdir(images_path):
        image_path = os.path.join(images_path, image_name)
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            image = bpy.data.images.load(image_path)
            width, height = image.size
            bpy.data.images.remove(image)  # إزالة الصورة من الذاكرة
            return width, height
    return 1920, 1080  # دقة افتراضية إذا لم يجد أي صورة

# مشغل لجمع الصور وعمل رندر للفيديو
class ExportAnimationOperator(Operator, ImportHelper):
    bl_idname = "export.animation"
    bl_label = "Anime export"
    bl_description = "Selects a folder containing photos and collects them into a video"
    bl_options = {'REGISTER', 'UNDO'}

    directory: StringProperty(
        name="Directory",
        description="Select the path to the image folder",
        subtype='DIR_PATH'
    )
    fps: IntProperty(
        name="FPS",
        description="Frames per second",
        default=24,
        min=1,
        max=60
    )

    def execute(self, context):
        images_path = self.directory
        image_files = sorted([f for f in os.listdir(images_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp'))])
        
        if not image_files:
            self.report({'ERROR'}, "No images were found in the specified folder.")
            return {'CANCELLED'}

        # تحديد اسم الفيديو بناءً على أول وآخر صورة
        first_image = image_files[0].split('.')[0]
        last_image = image_files[-1].split('.')[0]
        video_name = f"{first_image}_to_{last_image}.mp4"
        output_path = os.path.join(images_path, video_name)

        # تنظيف مشهد الفيديو الحالي
        bpy.context.scene.sequence_editor_clear()

        # إضافة محرر تسلسل الفيديو إذا لم يكن موجودًا
        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()
        
        # إعدادات الدقة بناءً على أول صورة
        width, height = get_image_resolution(images_path)
        bpy.context.scene.render.resolution_x = width
        bpy.context.scene.render.resolution_y = height
        bpy.context.scene.render.fps = self.fps
        bpy.context.scene.render.image_settings.color_mode = 'RGB'
        bpy.context.scene.render.image_settings.color_management = 'FOLLOW_SCENE'
        #bpy.context.scene.render.image_settings.color_management = 'OVERRIDE'
        bpy.context.scene.view_settings.view_transform = 'Standard'
        bpy.context.scene.view_settings.look = 'None'

        # إضافة الصور إلى نافذة تحرير الفيديو
        frame_start = 1
        for image_name in image_files:
            image_path = os.path.join(images_path, image_name)
            bpy.context.scene.sequence_editor.sequences.new_image(
                name=image_name,
                filepath=image_path,
                channel=1,
                frame_start=frame_start
            )
            frame_start += 1  # تعيين بداية الإطار للصورة التالية

        # إعدادات إخراج الفيديو
        bpy.context.scene.render.filepath = output_path
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.ffmpeg.format = 'MPEG4'
        bpy.context.scene.render.ffmpeg.codec = 'H264'
        bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
        bpy.context.scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
        bpy.context.scene.render.ffmpeg.video_bitrate = 8000

        # تحديد نهاية الإطار حسب عدد الصور
        bpy.context.scene.frame_end = frame_start - 1
        
        # إضافة دالة الإشعار إلى handlers عند اكتمال الرندر
        bpy.app.handlers.render_complete.append(show_completion_notification)
        
        # تنفيذ الرندر كفيديو مع ظهور نافذة الرندر
        bpy.ops.render.render('INVOKE_DEFAULT', animation=True)
                
        self.report({'INFO'}, f"Video saved in: {output_path}")
        return {'FINISHED'}
# دالة لتشغيل الإشعار بعد اكتمال الرندر
def show_completion_notification(scene):
    ctypes.windll.user32.MessageBoxW(0, "اكتمل تصدير الفيديو بنجاح!", "إشعار", 1)
    
def register():
    bpy.utils.register_class(kh_AnimationPanel)
    bpy.utils.register_class(kh_Animation_Panel1)
    bpy.utils.register_class(kh_Animation_Settings_Panel)
    
    bpy.utils.register_class(kh_Keyframe_Creator_Operator)
    bpy.utils.register_class(kh_Delete_Keyframe_Creator_Operator)
    
    bpy.utils.register_class(kh_camera_timeline_markers)
    bpy.utils.register_class(kh_delete_camera_timeline_markers)
        
    bpy.utils.register_class(kh_Plant_animation_Operator)
    bpy.utils.register_class(kh_delete_Plant_animation_Operator)
    
    bpy.utils.register_class(kh_Follow_path_Operator)
    bpy.utils.register_class(kh_delete_Follow_path_Operator)
    
    bpy.utils.register_class(kh_MyAddonProperties)
    
    bpy.types.Scene.kh_my_addon_props = bpy.props.PointerProperty(type=kh_MyAddonProperties)
    
    handlers.render_init.append(kh_rt_init)
    handlers.render_pre.append(kh_rt_start)
    handlers.render_complete.append(kh_rt_complete)
    handlers.render_cancel.append(kh_rt_cancel)
    
    bpy.utils.register_class(ExportAnimationOperator)



def unregister():
    bpy.utils.unregister_class(kh_AnimationPanel)
    bpy.utils.unregister_class(kh_Animation_Panel1)
    bpy.utils.unregister_class(kh_Animation_Settings_Panel)
    
    bpy.utils.unregister_class(kh_Keyframe_Creator_Operator)
    bpy.utils.unregister_class(kh_Delete_Keyframe_Creator_Operator)
    
    bpy.utils.unregister_class(kh_camera_timeline_markers)
    bpy.utils.unregister_class(kh_delete_camera_timeline_markers)
      
    bpy.utils.unregister_class(kh_Plant_animation_Operator)
    bpy.utils.unregister_class(kh_delete_Plant_animation_Operator)
    
    bpy.utils.unregister_class(kh_Follow_path_Operator)
    bpy.utils.unregister_class(kh_delete_Follow_path_Operator)
    
    bpy.utils.unregister_class(kh_MyAddonProperties)

    # التحقق من وجود الخاصية قبل حذفها لتجنب الأخطاء
    if hasattr(bpy.types.Scene, 'kh_my_addon_props'):
        del bpy.types.Scene.kh_my_addon_props

    # إزالة handlers بأمان
    try:
        handlers.render_init.remove(kh_rt_init)
    except ValueError:
        pass  # Handler already removed or not present

    try:
        handlers.render_pre.remove(kh_rt_start)
    except ValueError:
        pass  # Handler already removed or not present

    try:
        handlers.render_complete.remove(kh_rt_complete)
    except ValueError:
        pass  # Handler already removed or not present

    try:
        handlers.render_cancel.remove(kh_rt_cancel)
    except ValueError:
        pass  # Handler already removed or not present

    bpy.utils.unregister_class(ExportAnimationOperator)

if __name__ == "__main__":
    register()

