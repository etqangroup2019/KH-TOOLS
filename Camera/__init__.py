import bpy
import os, platform, subprocess
import aud
import re
from bl_ui.utils import PresetPanel
import time, datetime
from bpy.utils import previews
from bpy.utils import register_class, unregister_class

from bpy.types import (
    Operator,
    Panel,Scene, PropertyGroup,Object,Menu, Panel, UIList
)
from bpy.props import (IntProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       PointerProperty,
                       )

#SETTINGS//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
from bpy.props import FloatProperty, IntProperty, BoolProperty
import time
from bpy.app.handlers import persistent

# Compatibility helpers for Blender 5.0+ Compositor
def get_compositor_tree(scene):
    """Get compositor node tree with Blender 5.0+ compatibility"""
    if bpy.app.version >= (5, 0, 0):
        return scene.compositing_node_group
    else:
        if scene.use_nodes:
            return scene.node_tree
        return None

def create_compositor_tree(scene):
    """Create compositor node tree with Blender 5.0+ compatibility"""
    if bpy.app.version >= (5, 0, 0):
        if not scene.compositing_node_group:
            tree = bpy.data.node_groups.new("Compositor", "CompositorNodeTree")
            scene.compositing_node_group = tree
            # Default setup: Render Layers -> Group Output
            rlayers = tree.nodes.new(type="CompositorNodeRLayers")
            output = tree.nodes.new(type='NodeGroupOutput')
            if not tree.interface.items_tree:
                tree.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
            rlayers.location = (-300, 0)
            output.location = (300, 0)
            if len(output.inputs) > 0:
                tree.links.new(rlayers.outputs["Image"], output.inputs[0])
        return scene.compositing_node_group
    else:
        if not scene.use_nodes:
            scene.use_nodes = True
        return scene.node_tree

def get_or_create_output_node(tree, nodes):
    """Get or create output node (Composite or GroupOutput depending on Blender version)"""
    if bpy.app.version >= (5, 0, 0):
        for node in nodes:
            if node.type == 'GROUP_OUTPUT':
                return node
        output = nodes.new('NodeGroupOutput')
        if not tree.interface.items_tree:
            tree.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
        return output
    else:
        if 'Composite' in nodes:
            return nodes['Composite']
        return nodes.new('CompositorNodeComposite')

def set_output_node_path(output_node, slot_index, path_value):
    """Set Output File node slot path with 5.0 compatibility"""
    if bpy.app.version >= (5, 0, 0):
        # In 5.0 file_slots are gone, use file_output_items
        if hasattr(output_node, 'file_output_items') and len(output_node.file_output_items) > slot_index:
            output_node.file_output_items[slot_index].name = path_value
    else:
        # 4.x logic
        if hasattr(output_node, 'file_slots') and len(output_node.file_slots) > slot_index:
            output_node.file_slots[slot_index].path = path_value

def new_output_node_slot(output_node, path_name):
    """Create a new slot on Output File node with 5.0 compatibility"""
    if bpy.app.version >= (5, 0, 0):
         # In 5.0 we use file_output_items.new(name)
         # Note: base_path is now split, but name should suffice for path slots.
         return output_node.file_output_items.new(path_name)
    else:
         return output_node.file_slots.new(path_name)

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


class kh_MYBIGBUTTON_Settings(PropertyGroup):

### Render button panel Quick Settings[ -----------------------------
    
    playAfterRender: bpy.props.BoolProperty(
        name="Play sound",
        description="Play Sound when render is done",
        default = False)
   
   
   
    alarmInProgress: bpy.props.BoolProperty(
        name="Alarm In Progress",
        description="Alarm In Progress",
        default = False)

    abortAlarm: bpy.props.BoolProperty(
        name="Abort Alarm",
        description="Abort Alarm",
        default = False)
        ## ]Sound alarm

    ## Power off[---
    poweroffAfterRender: bpy.props.BoolProperty(
        name="Power Off",
        description="Power Off after render",
        default = False)

    timeoutPowerOff: bpy.props.IntProperty(
        name='Timeout Delay',
        description='Delay in secondes before Power Off',
        min=15, max=1200,step=1,default = 60)

    countDownAfterRender : bpy.props.IntProperty(
        name="Countdown after render",
        description="Countdown after render",
        default = 0)

    saveAtPowerOff: bpy.props.BoolProperty(
        name="Save Blender File",
        description="Save Blender file before Power Off",
        default = False)
        ## ]Power off

    ## Auto save render[---
    saveInBlendFolder: bpy.props.BoolProperty(
        name="Save in blend folder",
        description="Save Camera Output in blend folder",
        default = False)

    storeRenderInSlots: bpy.props.BoolProperty(
        name="Store in Slots",
        description="Store Cameras Output in Render Slots",
        default = False)
        ## ]Auto save render
    ### ]Render button panel Quick Settings


### Dimensions settings[ -------------------------------------
    switchRenderRotation_prop : bpy.props.BoolProperty(
        name="Rotation",
        description="Toggle Landscape / Portrait",
        default = False)

    Default_HRes_prop : bpy.props.IntProperty(
        name="DHres",
        description="Horizontal Default Dimension",
        default = 1920,max=65536,min=4,step=1
        )

    Default_VRes_prop : bpy.props.IntProperty(
        name="DVres",
        description="Vertical Default Dimension",
        default = 1080,max=65536,min=4,step=1
        )

    Default_HPixRes_prop : bpy.props.FloatProperty(
        name="DHPix",
        description="Horizontal Default Pixel Aspect",
        default = 1)

    Default_VPixRes_prop : bpy.props.FloatProperty(
        name="DVPix",
        description="Vertical Default Pixel Aspect",
        default = 1)
    ### ]Dimensions settings


### Camera Manager panel Quick Settings[ -----------------------------------------
    ## Cameras Manager quick settings UI[---
    cmOptions : bpy.props.BoolProperty(
        name="Camera Manager Quick Settings",
        #description="Toggle Quick Settings",
        default = False)

    cmBut_Render : bpy.props.BoolProperty(
        name="Toggle Render Camera",
        default = True)

    cmBut_AlignV : bpy.props.BoolProperty(
        name="Toggle Align Camera To View",
        default = False)

    cmBut_AlignO : bpy.props.BoolProperty(
        name="Toggle Aligne Camera To Object",
        default = False)
   

    cmBut_Trackto : bpy.props.BoolProperty(
        name="Copy Cam",
        default = True)

    cmBut_Marker : bpy.props.BoolProperty(
        name="Toggle Marker",
        default = True)

    cmBut_AnimData : bpy.props.BoolProperty(
        name="Toggle AnimData",
        default = True)

    Manager_ShowSelect : bpy.props.BoolProperty(
        name="Hilighlight Selected Camera",
        default = True)

    Manager_ShowSelect_Color : bpy.props.BoolProperty(
        name="Selected Camera Hilighlight with red",
        description="Selected Camera Hilighlight with red",
        default = True)

    Manager_ShowSelect_Gray : bpy.props.BoolProperty(
        name="Not selected Camera Grayed out",
        description="Not selected Camera Grayed out",
        default = True)

    Manager_ShowSelect_Pointer : bpy.props.BoolProperty(
        name="Add a pointer before Selected Camera",
        description="Add a pointer before Selected Camera",
        default = False)
        ## ]Cameras Manager quick settings UI

    ## Default settings for new cameras[---
    NewCam_lensPersp : bpy.props.IntProperty(
        name='Focal Length',
        description='New camera Focal Length ',
        min=1, max=5000,step=1,default = 50)

    NewCam_lensOrtho : bpy.props.FloatProperty(
        name='Orthographic Scale',
        description='New camera Orthographic Scale',
        min=0.001, max=100000,step=0.1,default = 35.000, precision= 3)

    NewCam_ClipStart : bpy.props.FloatProperty(
        name='Clip Start',
        description='New camera Clip start',
        min=0.001, max=100000,step=0.1,default = 0.1, precision= 3)

    NewCam_ClipEnd : bpy.props.FloatProperty(
        name='Clip End',
        description='New camera clip end',
        min=0.001, max=100000,step=0.1,default = 1000, precision= 3)

    NewCam_ClipStartOrtho : bpy.props.FloatProperty(
        name='Ortho Clip Start',
        description='New camera Orthographic clip start',
        min=0.001, max=100000,step=0.1,default = 0.1, precision= 3)

    NewCam_ClipEndOrtho : bpy.props.FloatProperty(
        name='Ortho Clip End',
        description='New camera Orthographic clip end',
        min=0.001, max=100000,step=0.1,default = 1000, precision= 3)
        ## ]Default settings for new cameras
    ### ]Camera Manager panel Quick Settings


### Batch Render Property[ -----------------------------------------
    switchRenderSelection: bpy.props.BoolProperty(
        name="Cameras Listing ",
        description="Toglle to Cameras listing for Batch Rendering",
        default = False)
    ### ]Batch Render Property

### Frame Render Type[ -----------------------------------------
    frameRenderType: bpy.props.StringProperty(
        name="Frame render type",
        description="Specify frame render type",
        default="")
    ### ]Frame Render Type

### Current Format Render Type[ -----------------------------------------
    currentFormatRenderType: bpy.props.StringProperty(
        name="Current frame render type",
        description="Current frame render type",
        default="")
    ### ]Current Format Render Type

### Only For This Job[ -----------------------------------------
    onlyForThisJob: bpy.props.BoolProperty(
        name="Set Render Format For This Job",
        description="Revert To Current Format After This Job",
        default = False)
    ### ]Only For This Job





class kh_MYBIGBUTTON_obj_Settings(PropertyGroup):
### Cameras Properties[ -------------------------------------------------
    Custom_Camtrack_prop : bpy.props.BoolProperty(
        name="Track",
        description="Camera Track To property",
        default = False)

    Custom_CamMarker_prop : bpy.props.BoolProperty(
        name="Marker",
        description="Camera Marker property",
        default = False)

    Custom_CamRes_prop : bpy.props.BoolProperty(
        name="Custom Resolution",
        description="Camera custom resolution property",
        default = False)

    Custom_CamRender_prop : bpy.props.BoolProperty(
        name="Add This Camera",
        description="Add in batch rendering list",
        default = False)
    ### ]Cameras Properties


## Cameras Custom resolution[------------------------------------------
    Custom_CamHRes_prop : bpy.props.IntProperty(
        name="Custom Horizontal Resolution",
        description="Custom Horizontal Resolution",
        default = 1920)

    Custom_CamVRes_prop : bpy.props.IntProperty(
        name="Custom Vertical Resolution",
        description="Custom Vertical Resolution",
        default = 1080)

    Custom_CamHPixRes_prop : bpy.props.FloatProperty(
        name="Custom Horizontal Pixel Aspect",
        description="Custom Horizontal Pixel Aspect",
        default = 1)

    Custom_CamVPixRes_prop : bpy.props.FloatProperty(
        name="Custom Vertical Pixel Aspect",
        description="Custom Vertical Pixel Aspect",
        default = 1)
    ## ]Cameras Custom resolution



#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#Function /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


def visualAlarm(self, context):
    scene = context.scene
    rd    = scene.render
    rs    = scene.RBTab_Settings

    layout      = self.layout
    row         = layout.row(align=True)
    row.scale_y = 3
    row.alert   = True

    if rs.countDownAfterRender == 0 and rs.playAfterRender == True:
        row.prop(rs,"abortAlarm", text="RENDER IS DONE",icon='BLANK1',emboss=False)
    elif rs.countDownAfterRender == 0:
        row.prop(rs,"abortAlarm", text="RENDER IS DONE".format(rs.countDownAfterRender),icon='BLANK1',emboss=False)
    else:
        if rs.countDownAfterRender%2 == 0 :
            row.alert = False
        else : row.alert = True
        row.prop(rs,"abortAlarm", text="POWER OFF IN {0} SEC".format(rs.countDownAfterRender),icon='BLANK1',emboss=False)

    row       = layout.row(align=True)
    row.alert = False

    row.prop(rs,"abortAlarm", text="Click or ESC to Abort",icon='BLANK1',emboss=False)


def SetCameraDimension(self, context):
        scene  = context.scene
        render = scene.render

        chosen_camera       = context.active_object
        previousSceneCamera = scene.camera
        scene.camera        = chosen_camera

        cs = chosen_camera.RBTab_obj_Settings
        rs = scene.RBTab_Settings

        if cs.Custom_CamRes_prop == True:
            render.resolution_x   = cs.Custom_CamHRes_prop
            render.resolution_y   = cs.Custom_CamVRes_prop
            render.pixel_aspect_x = cs.Custom_CamHPixRes_prop
            render.pixel_aspect_y = cs.Custom_CamVPixRes_prop
        else :
            render.resolution_x   = rs.Default_HRes_prop
            render.resolution_y   = rs.Default_VRes_prop
            render.pixel_aspect_x = rs.Default_HPixRes_prop
            render.pixel_aspect_y = rs.Default_VPixRes_prop

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#OPERATOR /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# ADD CAMERA ##################################################################################
class kh_SCENECAMERA_OT_Add(Operator):
    bl_idname      = "cameramanager.add_scene_camera"
    bl_label       = "add Camera"
    bl_description = "Add Camera"
    bl_options = {'UNDO'}

    def execute(self, context):

        scene = context.scene
        rd    = scene.render
        sp    = scene.RBTab_Settings

        #Store active collection before add Camera
        Active_Coll = bpy.context.view_layer.active_layer_collection

        # Make Master Collection active before add camera
        context.view_layer.active_layer_collection = context.view_layer.layer_collection

        if bpy.context.active_object:
            # التحقق من أن الكائن النشط في وضع العدل
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.camera_add()
        bpy.context.space_data.lock_camera = True

        # اسم الكولكشن المستهدف
        target_collection_name = "Cam"
        
        # الحصول على الكولكشن المستهدفة
        target_collection = bpy.data.collections.get(target_collection_name)
        
        # إنشاء الكولكشن إذا لم يكن موجودًا
        if target_collection is None:
            target_collection = bpy.data.collections.new(target_collection_name)
            bpy.context.scene.collection.children.link(target_collection)
        
        # الحصول على جميع الكاميرات في المشهد
        all_cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
        
        for camera in all_cameras:
            # التحقق مما إذا كانت الكاميرا في الكولكشن المستهدفة
            if target_collection not in camera.users_collection:
                # إزالة الكاميرا من الكولكشن الحالي إذا كانت موجودة
                for collection in camera.users_collection:
                    collection.objects.unlink(camera)
                # إضافة الكاميرا إلى الكولكشن المستهدف
                target_collection.objects.link(camera)
                

        cameras = [obj for obj in bpy.data.objects if obj.type == "CAMERA"]
        numbers = set()

        # Collect existing camera numbers
        for cam in cameras:
            if cam.name.startswith("Cam-"):
                number_str = cam.name.split("-")[1]
                if number_str.isdigit():
                    numbers.add(int(number_str))

        # Find the first available number
        count = 1
        while count in numbers:
            count += 1

        # Rename newly added cameras
        for obj in bpy.data.objects:
            if obj.type == "CAMERA" and not obj.name.startswith("Cam-"):
                if count < 10:
                    obj.name = f"Cam-00{count}"
                else:
                    obj.name = f"Cam-{count}"
                count += 1


        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                if context.area.spaces[0].region_3d.is_perspective:
                    bpy.context.object.data.type       = 'PERSP'
                    bpy.context.object.data.lens       = sp.NewCam_lensPersp
                    bpy.context.object.data.clip_start = sp.NewCam_ClipStart
                    bpy.context.object.data.clip_end   = sp.NewCam_ClipEnd
                else:
                    bpy.context.object.data.type        = 'ORTHO'
                    bpy.context.object.data.ortho_scale = sp.NewCam_lensOrtho
                    bpy.context.object.data.clip_start  = sp.NewCam_ClipStartOrtho
                    bpy.context.object.data.clip_end    = sp.NewCam_ClipEndOrtho
                break

        bpy.context.object.show_name      = True
        bpy.context.object.data.show_name = True

        #Restore collection active before adding camera
        bpy.context.view_layer.active_layer_collection = Active_Coll

    ###Align to view last camera added
        chosen_camera = context.active_object
        scene.camera  = chosen_camera

        bpy.context.space_data.camera = bpy.data.objects[chosen_camera.name]

        bpy.ops.object.select_all(action='DESELECT')
        chosen_camera.select_set(state = True)

        if rd.resolution_x != sp.Default_HRes_prop or rd.resolution_y != sp.Default_VRes_prop:
            chosen_camera.RBTab_obj_Settings.Custom_CamRes_prop     = True
            chosen_camera.RBTab_obj_Settings.Custom_CamHRes_prop    = rd.resolution_x
            chosen_camera.RBTab_obj_Settings.Custom_CamVRes_prop    = rd.resolution_y
            chosen_camera.RBTab_obj_Settings.Custom_CamHPixRes_prop = rd.pixel_aspect_x
            chosen_camera.RBTab_obj_Settings.Custom_CamVPixRes_prop = rd.pixel_aspect_y

        # trick to prevent error if align camera to view in camera view mode!
        bpy.ops.view3d.view_persportho()
        bpy.ops.view3d.view_persportho()

        bpy.ops.view3d.camera_to_view()
        bpy.ops.view3d.view_center_camera()
        bpy.context.object.data.lens = 26
        bpy.context.object.data.show_composition_thirds = True
        bpy.context.object.data.passepartout_alpha = 0.8
        bpy.context.scene.render.use_border = True
        bpy.context.scene.render.use_crop_to_border = True
        
        # تحقق من وجود الـ 3D View في وضع الـ UI
        if bpy.context.area.type == 'VIEW_3D' and bpy.context.area.ui_type == 'UI':
            main(bpy.context)
                         

        return {'FINISHED'}
    

# Cope CAMERA ##################################################################################
class kh_SCENECAMERA_OT_Copy_location(Operator):
    bl_idname      = "cameramanager.copy_location"
    bl_label       = "copy location"
    bl_description = "Copy location and properties between selected cameras"
    bl_options = {'UNDO'}

    def execute(self, context):
        # احصل على الكاميرا النشطة
        active_camera = bpy.context.scene.camera
        # احصل على الكاميرا المحددة والغير نشطة
        selected_camera = bpy.context.selected_objects 
        # تحقق مما إذا كانت الكاميرا المحددة فعلاً كاميرا وغير نشطة
        if len(selected_camera) == 2:
            # نسخ الروتيشن واللوكيشن
            active_camera.rotation_euler = selected_camera[0].rotation_euler
            active_camera.location = selected_camera[0].location
            active_camera.data.lens = selected_camera[0].data.lens  
            active_camera.data.shift_y  = selected_camera[0].data.shift_y  
            active_camera.data.clip_start  = selected_camera[0].data.clip_start  
            cam1 = selected_camera[0]
            cam2 = selected_camera[1]
            self.hide_objects_from_cameras(cam1, cam2)   
            
            active_camera.rotation_euler = selected_camera[1].rotation_euler
            active_camera.location = selected_camera[1].location 
            active_camera.data.lens = selected_camera[1].data.lens  
            active_camera.data.shift_y  = selected_camera[1].data.shift_y  
            active_camera.data.clip_start  = selected_camera[1].data.clip_start  
            cam1 = selected_camera[1]
            cam2 = selected_camera[0]
            self.hide_objects_from_cameras(cam1, cam2)  
            
        return {'FINISHED'}
    #نسخ الابجكتات من الكاميرا الأصلية إلى الكاميرا الثانية
    # إخفاء الأوبجكتات التي تحتوي على رقم الكاميرا الأصلية من الكاميرتين
    def hide_objects_from_cameras(self, cam1, cam2):
        """ إخفاء الأوبجكتات التي تحتوي على رقم الكاميرا الأصلية من الكاميرتين """
        all_objects = bpy.context.scene.objects
        cam1_name_cleaned = re.sub(r"Cam-|00|-", "", cam1.name)
        cam2_name_cleaned = re.sub(r"Cam-|00|-", "", cam2.name)

        for obj in all_objects:
            if f"({cam1_name_cleaned})" in obj.name:
                # تعديل الاسم لإضافة الكاميرا الثانية وإخفاء الأوبجكت
                if f"({cam2_name_cleaned})" not in obj.name:
                    obj.name += f"({cam2_name_cleaned})"
                
                obj.hide_viewport = True
                obj.hide_render = True



          
    
# Cope CAMERA ##################################################################################
class kh_SCENECAMERA_OT_Copy(Operator):
    bl_idname      = "cameramanager.copy_scene_camera"
    bl_label       = "Copy Cam"
    bl_description = "Copy Camera"
    bl_options = {'UNDO'}

    def execute(self, context):

        scene = context.scene
        rd    = scene.render
        sp    = scene.RBTab_Settings

        Active_Coll = bpy.context.view_layer.active_layer_collection

        context.view_layer.active_layer_collection = context.view_layer.layer_collection
        
        if bpy.context.active_object:
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
    
        if bpy.context.scene.camera:
            active_camera_name = bpy.context.scene.camera.name
        else:
            self.report({'ERROR'}, "No active camera found.")
            return {'CANCELLED'}
            
        count = 0
        if bpy.data.objects.get(active_camera_name) is not None:
            max_number = 0
            for obj in bpy.data.objects:
                if obj.name.startswith("Cam-"):
                    try:
                        number = int(obj.name.split("-")[1])
                        max_number = max(max_number, number)
                    except ValueError:
                        pass
            count = max_number + 1
            if count < 10:
                new_camera_name = f"Cam-00{count}"
            else:
                new_camera_name = f"Cam-{count}"

        max_number = 0
        if active_camera_name.endswith("-N"):
            max_number = 0
            for obj in bpy.data.objects:
                if obj.name.startswith("Cam-"):
                    try:
                        number = int(obj.name.split("-")[1])
                        max_number = max(max_number, number)
                    except ValueError:
                        pass
            count = max_number + 1
            if count < 10:
                new_camera_name = f"Cam-00{count}"
                
            else:
                new_camera_name = f"Cam-{count}"
            

        active_camera = bpy.context.scene.camera
        new_camera = active_camera.copy()
        new_camera.name = new_camera_name 


        new_camera.data = active_camera.data.copy()
        new_camera.location = active_camera.location.copy()
        new_camera.rotation_euler = active_camera.rotation_euler.copy()

        bpy.context.scene.collection.objects.link(new_camera)
        active_camera.select_set(False)

        new_camera.select_set(True)
        bpy.context.view_layer.objects.active = new_camera
        bpy.context.scene.camera = new_camera
        scene = context.scene
        cameras = [ob for ob in scene.objects if ob.type == 'CAMERA']
        
        if not bpy.data.collections.get("Cam"):
            cam_collection = bpy.data.collections.new("Cam")
            scene.collection.children.link(cam_collection)
        else:
            cam_collection = bpy.data.collections["Cam"]

        for camera in cameras:
            if camera.name not in cam_collection.objects:
                if camera.name in scene.collection.objects:
                    cam_collection.objects.link(camera)
                    scene.collection.objects.unlink(camera)
                else:
                    print(f"Camera '{camera.name}' not found in 'Scene Collection'.")
                    
        if bpy.context.area.type == 'VIEW_3D' and bpy.context.area.ui_type == 'UI':
            main(bpy.context)
        else:
            print("Please make sure the addon is placed in the 3D View UI.")


        # Check if the scene is in 'Camera Perspective'
        if bpy.context.space_data.region_3d.view_perspective != 'CAMERA':
            # If not in 'Camera Perspective', loop through screen areas
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    bpy.context.area.ui_type = 'VIEW_3D'
                    bpy.ops.view3d.camera_to_view()
                    break  # Exit the loop once we find the 'VIEW_3D' area
                
        world_names = [world.name for world in bpy.data.worlds]
        n_worlds = [name for name in world_names if not name.endswith('N') and name.startswith('Cam') ]
        if n_worlds:
            last_n_world = bpy.data.worlds[n_worlds[-1]]
            bpy.context.scene.world = last_n_world       
        

        return {'FINISHED'}

#night CAMERA ##################################################################################
class kh_SCENECAMERA_OT_Night(Operator):
    bl_idname      = "cameramanager.night_scene_camera"
    bl_label       = "N Cam"
    bl_description = "Copy Night"
    bl_options = {'UNDO'}

    def execute(self, context):

        # احصل على الكاميرا النشطة في المشهد
        active_camera = bpy.context.scene.camera

        # تحقق من أن اسم الكاميرا النشطة لا ينتهي بـ "N"
        if not active_camera.name.endswith("-N"):

            # قم بتحقق من وجود كاميرا بنفس الاسم مع اللاحقة "-N"
            camera_name = active_camera.name + "-N"
            if not bpy.data.objects.get(camera_name):

                # إنشاء نسخة جديدة من الكاميرا النشطة مع الاسم المعدل
                new_camera = active_camera.copy()
                new_camera.name = camera_name

                # نسخ جميع الإعدادات والخصائص من الكاميرا القديمة إلى الجديدة
                new_camera.data = active_camera.data.copy()
                new_camera.location = active_camera.location.copy()
                new_camera.rotation_euler = active_camera.rotation_euler.copy()

                # إضافة الكاميرا الجديدة إلى المشهد
                bpy.context.scene.collection.objects.link(new_camera)
                active_camera.select_set(False)

                # تفعيل وتحديد الكاميرا الجديدة
                new_camera.select_set(True)
                bpy.context.view_layer.objects.active = new_camera
                bpy.context.scene.camera = new_camera
           
        
        scene = context.scene
        cameras = [ob for ob in scene.objects if ob.type == 'CAMERA']
        
        # Create the Cam collection if it doesn't exist
        if not bpy.data.collections.get("Cam"):
            cam_collection = bpy.data.collections.new("Cam")
            scene.collection.children.link(cam_collection)
        
        # Move the cameras to the Cam collection
        cam_collection = bpy.data.collections["Cam"]
        for camera in cameras:
            if camera.name not in cam_collection.objects:
                cam_collection.objects.link(camera)
                scene.collection.objects.unlink(camera)
        

        return {'FINISHED'}

# ACTIV & PREVIEW CHOSEN CAMERA ##################################################################################
class kh_SCENECAMERA_OT_ActivPreview(Operator):
    bl_idname      = "cameramanager.activpreview_scene_camera"
    bl_label       = "Preview Camera"
    bl_description = "Active & Preview Camera"
    #bl_options = {'UNDO'}

    DeselectCam : bpy.props.BoolProperty(default = False)

    def invoke(self, context, event):

        scene         = context.scene
        chosen_camera = context.active_object

        previousSceneCamera = scene.camera

        render        = scene.render
        cs            = chosen_camera.RBTab_obj_Settings
        rs            = scene.RBTab_Settings
        marker_list   = context.scene.timeline_markers

        selectedObj = bpy.context.selected_objects
        selectedCam = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)

        if event.shift or self.DeselectCam == True:
            if chosen_camera in selectedCam:
                chosen_camera.select_set(state = False)
                self.DeselectCam = False
            else:
                chosen_camera.select_set(state = True)
                scene.camera  = chosen_camera
                bpy.context.view_layer.objects.active = chosen_camera
                

        elif event!= 'shift' :
            scene.camera = chosen_camera
            for marker in marker_list:
                if marker.camera == scene.camera:
                    scene.frame_current = marker.frame

            bpy.context.view_layer.objects.active = chosen_camera
            

            #if len(selectedCam)<=1 and chosen_camera not in selectedCam:
            if chosen_camera not in selectedCam:
                bpy.ops.object.select_all(action='DESELECT')
                chosen_camera.select_set(state = True)

        #ACTIV & PREVIEW CHOSEN CAMERA

            bpy.context.space_data.camera = bpy.data.objects[chosen_camera.name]


            SetCameraDimension(self, context)

            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    
                    if context.area.spaces[0].region_3d.view_perspective == 'CAMERA' and scene.camera == previousSceneCamera and scene.camera in selectedCam:

                        bpy.ops.view3d.view_camera()
                        
                    else:
                        bpy.ops.view3d.view_camera()
                        
                        context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                        bpy.ops.view3d.view_center_camera()
                    break
            
        return {'FINISHED'}


# ALIGN CHOSEN CAMERA TO ACTIV VIEW ##################################################################################
class kh_SCENECAMERA_OT_AlignView(Operator):
    bl_idname      = "cameramanager.alignview_scene_camera"
    bl_label       = "Align Camera View to Activ View"
    bl_options = {'UNDO'}
    bl_description = (" \u2022 In perpective View: Align to View \n"
                      " \u2022 In Camera View: Align to Cursor")

    def execute(self, context):
        scene         = context.scene
        chosen_camera = context.active_object
        scene.camera  = chosen_camera
        render        = scene.render
        cs            = chosen_camera.RBTab_obj_Settings
        rs            = scene.RBTab_Settings
        marker_list   = context.scene.timeline_markers

        for marker in marker_list:
            if marker.camera == scene.camera:
                scene.frame_current = marker.frame

        object_to_track = bpy.context.selected_objects
        bpy.context.view_layer.objects.active = chosen_camera

        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')

    #ALIGN CHOSEN CAMERA TO ACTIV VIEW

        # Align to 3d Cursor IF in camera view
        if area.spaces[0].region_3d.view_perspective == 'CAMERA':
            if len(chosen_camera.constraints) > 0:
                CamTarget = chosen_camera.constraints[0].target
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[CamTarget.name].select_set(state = True)
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                bpy.ops.object.select_all(action='DESELECT')
                chosen_camera.select_set(state = True)

            else:
                Active_Coll = bpy.context.view_layer.active_layer_collection
                context.view_layer.active_layer_collection = context.view_layer.layer_collection

                bpy.ops.object.empty_add(type='PLAIN_AXES')

                bpy.context.view_layer.active_layer_collection = Active_Coll
                bpy.context.object.name = "target"
                object_to_track = bpy.context.selected_objects
                chosen_camera.select_set(state = True)
                scene.camera = chosen_camera

                bpy.context.view_layer.objects.active = bpy.data.objects[object_to_track[0].name]
                bpy.ops.object.track_set(type='TRACKTO')
                bpy.ops.object.track_clear(type='CLEAR_KEEP_TRANSFORM')
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects["target"].select_set(state = True)
                bpy.ops.object.delete(use_global=False, confirm=False)
                bpy.ops.object.select_all(action='DESELECT')
                chosen_camera.select_set(state = True)

        # Align to activ View IF NOT in Camera View
        else:
            bpy.ops.object.select_all(action='DESELECT')
            chosen_camera.select_set(state = True)
            bpy.ops.view3d.view_persportho()
            bpy.ops.view3d.view_persportho()
            bpy.ops.view3d.camera_to_view()

        chosen_camera.select_set(state = False)

        bpy.context.view_layer.objects.active = chosen_camera
        bpy.context.space_data.camera = bpy.data.objects[chosen_camera.name]

        SetCameraDimension(self, context)

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break
        return {'FINISHED'}


# ALIGN CHOSEN CAMERA TO SELECTED OBJECT ##################################################################################
class kh_SCENECAMERA_OT_AlignObj(Operator):
    bl_idname      = "cameramanager.alignobj_scene_camera"
    bl_label       = "Align Camera View to Object(s)"
    bl_options = {'UNDO'}
    bl_description = (" \u2022 Object(s) Selected: Align to Object(s) \n"
                      " \u2022 No Object Selected: View All")

    def execute(self, context):
        scene         = context.scene
        chosen_camera = context.active_object
        render        = scene.render
        op            = chosen_camera.RBTab_obj_Settings
        sp            = scene.RBTab_Settings

        selectedAny   = bpy.context.selected_objects
        selectedObj   = sorted([o for o in selectedAny if o.type != 'CAMERA'],key=lambda o: o.name)
        selectedCams  = sorted([o for o in selectedAny if o.type == 'CAMERA'],key=lambda o: o.name)

        chosen_camera = context.active_object
        scene.camera  = chosen_camera

        if chosen_camera not in selectedCams:
            selectedCams = []
            selectedCams.append(chosen_camera)

        bpy.context.view_layer.objects.active = chosen_camera


    #ALIGN CHOSEN CAMERA TO SELECTED OBJECT

        # View All IF no object selected OR current camera selected
        if len(selectedObj) == 0:# or chosen_camera.name == selectedObj[0].name:
            for cam in selectedCams:
                chosen_camera = cam
                scene.camera  = chosen_camera

                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.view3d.camera_to_view_selected()
                bpy.ops.object.select_all(action='DESELECT')

        # View Selected object(s)
        else:
            for cam in selectedCams:
                chosen_camera = cam
                scene.camera  = chosen_camera

                bpy.ops.view3d.camera_to_view_selected()

        bpy.ops.object.select_all(action='DESELECT')
        if len(selectedCams) > 1:
            for cam in selectedCams:
                cam.select_set(state = True)

        SetCameraDimension(self, context)

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break
        return {'FINISHED'}


## TRACK TO SELECTED OBJECT ##
### ADD TRACK ################################################################################
class kh_SCENECAMERA_OT_AddTrackTo(Operator):
    bl_idname      = "cameramanager.trackto_scene_camera"
    bl_label       = "Night Cam"
    #bl_options = {'UNDO'}
    bl_description = ("Add a night camera from this camera")

    def execute(self, context):
        if bpy.context.scene.camera:
            active_camera = bpy.context.scene.camera
            if not active_camera.name.endswith("-N"):
                camera_name = active_camera.name + "-N"
                if not bpy.data.objects.get(camera_name):
                    new_camera = active_camera.copy()
                    new_camera.name = camera_name
                    new_camera.data = active_camera.data.copy()
                    new_camera.location = active_camera.location.copy()
                    new_camera.rotation_euler = active_camera.rotation_euler.copy()
                    bpy.context.scene.collection.objects.link(new_camera)
                    active_camera.select_set(False)
                    new_camera.select_set(True)
                    bpy.context.view_layer.objects.active = new_camera
                    bpy.context.scene.camera = new_camera

                    scene = context.scene
                    cameras = [ob for ob in scene.objects if ob.type == 'CAMERA']
                    if not bpy.data.collections.get("Cam"):
                        cam_collection = bpy.data.collections.new("Cam")
                        scene.collection.children.link(cam_collection)
                    
                    cam_collection = bpy.data.collections["Cam"]
                    for camera in cameras:
                        if camera.name not in cam_collection.objects:
                            cam_collection.objects.link(camera)
                            scene.collection.objects.unlink(camera)
                            
                    world_names = [world.name for world in bpy.data.worlds]
                    n_worlds = [name for name in world_names if name.endswith('N')]
                    if n_worlds:
                        last_n_world = bpy.data.worlds[n_worlds[-1]]
                        bpy.context.scene.world = last_n_world

        return {'FINISHED'}



### REMOVE TRACK TO ################################################################################
class kh_SCENECAMERA_OT_RemoveTrackTo(Operator):
    bl_idname      = "cameramanager.removetrackto_scene_camera"
    bl_label       = "Remove Track to Object : Clear Track"
    #bl_options = {'UNDO'}
    bl_description = (" \u2022 Shift : Clear and Keep Transformation")

    event_Shift: bpy.props.BoolProperty(default = False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        if event.shift: self.event_Shift = True
        else: self.event_Shift = False

        return self.execute(context)

    def execute(self, context):
        scene  = context.scene
        render = scene.render

        selectedObj     = bpy.context.selected_objects
        cameras         = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        object_to_track = sorted([o for o in selectedObj if o.type != 'CAMERA'],key=lambda o: o.name)
        selectedCams    = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)

        targetedCams = []
        targetsName  = []
        tc_Append    = targetedCams.append
        tn_Append    = targetsName.append
        for o in cameras:
            if o.constraints is not None:
                for c in o.constraints:
                    if c.type == 'TRACK_TO':
                        tc_Append(o)
                        if c.target is not None:
                            tn_Append(c.target.name)


        chosen_camera = context.active_object

        op = chosen_camera.RBTab_obj_Settings
        sp = scene.RBTab_Settings

        if chosen_camera not in selectedCams:
            selectedCams = []
            selectedCams.append(chosen_camera)

        object_to_track = bpy.context.selected_objects
        bpy.context.view_layer.objects.active = chosen_camera

        targets = sorted([o for o in scene.objects if o.type == 'EMPTY'], key=lambda o: o.name)

    #REMOVE TRACK TO SELECTED OBJECT

        for cam in selectedCams:
            chosen_camera = cam
            if chosen_camera in targetedCams :
                CamTarget = chosen_camera.constraints[0].target
                bpy.ops.object.select_all(action='DESELECT')
                chosen_camera.select_set(state = True)
                if CamTarget is not None: targetsName.remove(CamTarget.name)
                print(len(targetsName))
                print(targetsName)

                # Shift Click = Clear Keep
                if self.event_Shift:
                    bpy.ops.object.track_clear(type='CLEAR_KEEP_TRANSFORM')

                # Click = Clear
                else:
                    bpy.ops.object.track_clear(type='CLEAR')

                # Remove Target after Clear Track IF Target Type = Empty and
                # name starts with = t_
                if CamTarget is not None and targetsName.count(CamTarget.name) == 0:
                    _tname = CamTarget.name[0:2]

                    if CamTarget.type == 'EMPTY' and _tname == "t_":
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.data.objects[CamTarget.name].select_set(state = True)
                        bpy.ops.object.delete(use_global=False, confirm=False)

                chosen_camera.RBTab_obj_Settings.Custom_Camtrack_prop = False

        bpy.ops.object.select_all(action='DESELECT')

        if len(selectedCams) > 1:
            for cam in selectedCams:
                cam.select_set(state = True)

        SetCameraDimension(self, context)

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break
        return {'FINISHED'}


# ADD CAMERA MARKER ##################################################################################
class kh_SCENECAMERA_OT_AddMarker(Operator):
    bl_idname      = "cameramanager.add_camera_marker"
    bl_label       = "Add Camera Marker"
    bl_description = "Add a timeline marker bound to this camera"
    #bl_options = {'UNDO'}

    def execute(self, context):
        chosen_camera = context.active_object
        scene         = context.scene
        current_frame = scene.frame_current
        marker        = None

        for m in reversed(sorted(filter(lambda m: m.frame <= current_frame,scene.timeline_markers),key=lambda m: m.frame)):
            marker = m
            break

        marker_name = chosen_camera.name

        if marker and (marker.frame == current_frame):
            marker.name = marker_name
        else:
            marker = scene.timeline_markers.new(marker_name)

        marker.frame  = scene.frame_current
        marker.camera = chosen_camera
        marker.select = True

        chosen_camera.RBTab_obj_Settings.Custom_CamMarker_prop = True

        for other_marker in [m for m in scene.timeline_markers if m != marker]:
            other_marker.select = False

        return {'FINISHED'}


# REMOVE CAMERA MARKER ##################################################################################
class kh_SCENECAMERA_OT_removeMarker(Operator):
    bl_idname = "cameramanager.remove_camera_marker"
    bl_label = "Remove Camera Marker"
    bl_description = (" \u2022 Shift : Remove all Camera marker")
    #bl_options = {'UNDO'}

    event_Shift: bpy.props.BoolProperty(default = False)


    def invoke(self, context, event):
        if event.shift: self.event_Shift = True
        else: self.event_Shift = False
        return self.execute(context)

    def execute(self, context):

    #def invoke(self, context, event):
        scene  = context.scene
        render = scene.render

        selectedObj     = bpy.context.selected_objects
        object_to_track = sorted([o for o in selectedObj if o.type != 'CAMERA'],key=lambda o: o.name)
        selectedCams    = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)

        chosen_camera  = context.active_object
        scene.camera   = chosen_camera
        marker_list    = context.scene.timeline_markers

        op = chosen_camera.RBTab_obj_Settings
        sp = scene.RBTab_Settings


        if chosen_camera not in selectedCams:
            if len(selectedCams) == 0:
                selectedCams = []
                selectedCams.append(chosen_camera)
            elif len(selectedCams) > 0:
                chosen_camera = selectedCams[0]

        # Shift Click = Remove All Marker
        if self.event_Shift:
            for marker in marker_list:
                scene.camera        = marker.camera
                scene.frame_current = marker.frame
                scene.timeline_markers.remove(marker)
        else:

            for cam in selectedCams:
                chosen_camera = cam
                for marker in marker_list:
                    if marker.camera == chosen_camera:
                        scene.camera        = marker.camera
                        scene.frame_current = marker.frame
                        scene.timeline_markers.remove(marker)

        chosen_camera.RBTab_obj_Settings.Custom_CamMarker_prop = False

        bpy.ops.object.select_all(action='DESELECT')

        if len(selectedCams) > 1:
            for cam in selectedCams:
                cam.select_set(state = True)

        SetCameraDimension(self, context)

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break

        return {'FINISHED'}


# REMOVE CAMERA ##################################################################################
class kh_SCENECAMERA_OT_Remove(Operator):
    bl_idname      = "cameramanager.del_scene_camera"
    bl_label       = "Remove Scene Camera"
    bl_description = (" \u2022 shift + click: Remove All Cameras ")
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        chosen_camera = context.active_object
        scene         = context.scene
        marker_list   = context.scene.timeline_markers

        scene.camera = chosen_camera

        selectedObj = bpy.context.selected_objects
        selectedCam = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)

        cameras = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)

        if event.shift or len(selectedCam) == len(cameras):
            for camera in cameras:
                if len(camera.constraints) >0:
                    CamTarget = camera.constraints[0].target
                    if CamTarget is not None:
                        _tname = CamTarget.name[0:2]
                        if CamTarget.type == 'EMPTY' and _tname == "t_":
                            bpy.ops.object.select_all(action='DESELECT')
                            bpy.data.objects[CamTarget.name].select_set(state = True)
                            bpy.ops.object.delete(use_global=False, confirm=False)

                scene.camera = camera
                bpy.ops.object.select_all(action='DESELECT')
                camera.select_set(state = True)
                bpy.ops.object.delete(use_global=False, confirm=False)

            if len(marker_list)>0:
                for marker in marker_list:
                    scene.timeline_markers.remove(marker)

            return {'FINISHED'}

        elif chosen_camera in selectedCam and len(selectedCam) >1:
            for camera in cameras:
                if camera in selectedCam:
                    if len(camera.constraints) >0:
                        CamTarget = camera.constraints[0].target
                        if CamTarget is not None:
                            _tname = CamTarget.name[0:2]
                            if CamTarget.type == 'EMPTY' and _tname == "t_":
                                bpy.ops.object.select_all(action='DESELECT')
                                bpy.data.objects[CamTarget.name].select_set(state = True)
                                bpy.ops.object.delete(use_global=False, confirm=False)

                    scene.camera = camera
                    bpy.ops.object.select_all(action='DESELECT')
                    camera.select_set(state = True)
                    bpy.ops.object.delete(use_global=False, confirm=False)
            return {'FINISHED'}
        else:
            if len(marker_list)>0:
                for marker in marker_list:
                    if marker.camera == scene.camera:
                        scene.camera        = marker.camera
                        scene.frame_current = marker.frame
                        scene.timeline_markers.remove(marker)

            if len(chosen_camera.constraints) >0:
                CamTarget = chosen_camera.constraints[0].target
                if CamTarget is not None:
                    _tname = CamTarget.name[0:2]
                    if CamTarget.type == 'EMPTY' and _tname == "t_":
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.data.objects[CamTarget.name].select_set(state = True)
                        bpy.ops.object.delete(use_global=False, confirm=False)

            scene.camera = chosen_camera
            bpy.ops.object.select_all(action='DESELECT')
            chosen_camera.select_set(state = True)
            bpy.ops.object.delete(use_global=False, confirm=False)
            return {'FINISHED'}


# RENDER ANIMATION ##################################################################################
class kh_SCENECAMERA_OT_RenderAnimation(Operator):
    bl_idname      = "cameramanager.render_scene_animation"
    bl_label       = "Render Camera"
    bl_description = "Render this camera"

    _timer          = None
    _finish         = None
    _stop           = None
    _autoSaveRender = None
    path            = "//"
    _cameras        = None

    renderFrom  : bpy.props.StringProperty(default ='')

    def renderComplete(self, dummy, thrd = None):
        self._finish = True
        # اسم الكولكشن المستهدف
        target_collection_name = "3D Model"
        target_collection = bpy.data.collections.get(target_collection_name)
        if target_collection:
            target_collection.hide_viewport = False
        

    def renderCancel(self, dummy, thrd = None):
        self._stop = True
        # اسم الكولكشن المستهدف
        target_collection_name = "3D Model"

        # التحقق من وجود الكولكشن
        target_collection = bpy.data.collections.get(target_collection_name)

        # إذا كان الكولكشن موجودًا، قم بتعيين hide_viewport إلى True
        if target_collection:
            target_collection.hide_viewport = False
       

    def execute(self, context):

        scene = bpy.context.scene
        rs    = scene.RBTab_Settings

        self._cameras = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)

        ### Check Sound File For Alarm[---
        if rs.playAfterRender == True:
            a,soundType = os.path.splitext(rs.soundToPlay)
            soundExt    = bpy.path.extensions_audio

            if str.lower(soundType) not in soundExt or os.path.exists(bpy.path.abspath(rs.soundToPlay)) == False:
                rs.soundToPlay = ''
                ShowMessageBox("Choose a sound file for alarm before !", "Wrong Sound File Type OR Not Exist", 'ERROR')
                self.report({"WARNING"}, 'Wrong Sound File Type OR Not Exist')
                return {"CANCELLED"}
        ### ]Check Sound File For Alarm

    ## Autosave & Render file path[---
        if len(bpy.context.scene.render.filepath) == 0:
            if rs.saveInBlendFolder == False: self._autoSaveRender = False
            else:
                self._autoSaveRender = True
                self.path = '//'
        else:
            self._autoSaveRender = True
            if rs.saveInBlendFolder == False:
                self.path = bpy.context.scene.render.filepath
            else: self.path = '//'
        ### ]Autosave

    ## Application handlers[---
        bpy.app.handlers.render_complete.append(self.renderComplete)
        bpy.app.handlers.render_cancel.append(self.renderCancel)
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window) #Timer event
        context.window_manager.modal_handler_add(self)
        ## ]Application handlers

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        scene = context.scene
        rs    = scene.RBTab_Settings

    ### EXIT after render is done or canceled[---
        if self._finish or self._stop:

            if self._autoSaveRender == True: scene.render.filepath = self.path
            else: scene.render.filepath = ''
            #Remove handlers
            bpy.app.handlers.render_complete.remove(self.renderComplete)
            bpy.app.handlers.render_cancel.remove(self.renderCancel)
            context.window_manager.event_timer_remove(self._timer)
            #Alarm
            if rs.playAfterRender == True or rs.poweroffAfterRender == True: bpy.ops.renderevents.end_events("INVOKE_DEFAULT")

            return {'FINISHED'}
        ### ]EXIT

        scene.render.filepath = self.path

        if len(self._cameras) == 0:
            ShowMessageBox("No camera found in this scene !", "Render Error", 'ERROR')
            self.report({"ERROR"}, 'No camera found in this scene !')
            return {"FINISHED"}
        else:
            bpy.ops.render.render('INVOKE_DEFAULT',animation=True)

        return {"PASS_THROUGH"}


# BATCH RENDER All CAMERA ##################################################################################
class kh_SCENECAMERA_OT_BatchRenderAll(Operator):
    bl_idname      = "cameramanager.render_all_camera"
    bl_label       = "Batch Render All Camera"
    bl_description = "Render All Cameras"

    _timer              = None
    cameras             = []
    _lenCameras         = 0
    _cameras            = None
    marker_list         = None
    marker_list_cameras = None
    stop                = None
    rendering           = None
    path                = "//"
    _autoSaveRender     = None
    _currentRenderFileFormat = ''

    tmarkers : bpy.props.BoolProperty(default = False)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None or context.scene.camera is not None

    def pre(self, dummy, thrd = None):
        self.rendering = True
        

    def post(self, dummy, thrd = None):
        scene   = bpy.context.scene
        rs      = scene.RBTab_Settings
        img     = bpy.data.images['Render Result']

        if scene.frame_current == 0:
            marker_list = scene.timeline_markers
            marker_list_cameras = [o for o in self.marker_list if o.camera != None]
            for m in marker_list_cameras:
                if m.camera == scene.camera:
                    scene.timeline_markers.remove(m)

        if rs.storeRenderInSlots == True and img.render_slots.active_index < (self._lenCameras - 1):
            img.render_slots.active_index += 1

        self.cameras.pop(0)
        self.rendering = False
        

    def cancelled(self, dummy, thrd = None):
        scene  = bpy.context.scene
        if scene.frame_current == 0:
            marker_list = scene.timeline_markers
            for m in marker_list:
                if m.camera == scene.camera:
                    scene.timeline_markers.remove(m)

        self.stop = True

        # اسم الكولكشن المستهدف
        target_collection_name = "3D Model"
        target_collection = bpy.data.collections.get(target_collection_name)
        if target_collection:
            target_collection.hide_viewport = False
                

    def execute(self, context):
        self.stop      = False
        self.rendering = False
        self._lenCameras = 0
        self.cameras     = []
        
        bpy.context.space_data.shading.type = 'SOLID'
        bpy.context.preferences.system.gl_texture_limit = 'CLAMP_OFF'
        bpy.context.preferences.system.gl_texture_limit = 'CLAMP_1024'
        try:
            if bpy.data.filepath:
                if os.path.exists(bpy.data.filepath):
                    bpy.ops.wm.save_mainfile()
        except RuntimeError as e:
            if "Unable to pack file, source path" in str(e):
                pass  # تجاوز الأمر في حالة حدوث الخطأ المحدد
            else:
                raise e 

        # اسم الكولكشن المستهدف
        target_collection_name = "3D Model"
        target_collection = bpy.data.collections.get(target_collection_name)
        if target_collection:
            target_collection.hide_viewport = True
        else:
            print(f"الكولكشن '{target_collection_name}' غير موجود.")


        bpy.ops.render.view_show("INVOKE_DEFAULT")

        #bpy.ops.image.view_all(fit_view=True)

        scene  = bpy.context.scene
        render = scene.render
        rs     = scene.RBTab_Settings
        img    = bpy.data.images['Render Result']
        
        if rs.saveInBlendFolder: render.filepath = '//'

#        rs.frameRenderType = "BATCH"

        selectedObj = bpy.context.selected_objects
        selectedCam = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)

        self.marker_list         = context.scene.timeline_markers
        self.marker_list_cameras = [o for o in self.marker_list if o.camera != None]


        ### Check render File Format[---
        imageFormat   = ['TIFF','BMP','IRIS','JPEG2000','TARGA','TARGA_RAW','CINEON','DPX','OPEN_EXR','OPEN_EXR_MULTILAYER','HDR','JPEG','PNG']
        if render.image_settings.file_format not in imageFormat:
            self.report({"WARNING"}, 'Cannot write a single file with an animation format selected')
            bpy.ops.render.renderformat("INVOKE_DEFAULT")
            return {"CANCELLED"}
        #]Check render File Format

        ### Check Sound File For Alarm[---
        if rs.playAfterRender == True:
            a,soundType = os.path.splitext(rs.soundToPlay)
            soundExt    = bpy.path.extensions_audio

            if str.lower(soundType) not in soundExt or os.path.exists(bpy.path.abspath(rs.soundToPlay)) == False:
                rs.soundToPlay = ''
                ShowMessageBox("Choose a sound file for alarm before !", "Wrong Sound File Type OR Not Exist", 'ERROR')
                self.report({"WARNING"}, 'Wrong Sound File Type OR Not Exist')
                return {"CANCELLED"}
        #]Check Sound File For Alarm

        #test to ignore markers without binded cameras
        if len(self.marker_list_cameras) == 0: self.marker_list = []

    ## Build cameras list[---
        if rs.switchRenderSelection == True :
            if self.tmarkers == True:
                self.cameras = sorted([o.name for o in self.marker_list_cameras])
                self.tmarkers = False
            else:
                for o in scene.objects:
                    cs = o.RBTab_obj_Settings
                    if o.type == 'CAMERA'and cs.Custom_CamRender_prop == True:
                        self.cameras += sorted([o.name])
        elif len(selectedCam) > 1:
            self.cameras = sorted([o.name for o in selectedCam])
        else:
            if self.tmarkers == True:
                self.cameras = sorted([o.name for o in self.marker_list_cameras])
                self.tmarkers = False
            else:
                self.cameras = sorted([o.name for o in scene.objects if o.type == 'CAMERA'])
        #]Build cameras list

        self._lenCameras = len(self.cameras)

    ## Initialise render slots[---
        if rs.storeRenderInSlots == True:
            if len(img.render_slots) < len(self.cameras):
                _slotToAdd = len(self.cameras)-len(img.render_slots) #+1
                i = 0
                while i < _slotToAdd:
                    i+=1
                    img.render_slots.new()

        bpy.data.images['Render Result'].render_slots.active_index = 0
        #]Initialise render slots

    ## Autosave & Render file path[---
        if len(bpy.context.scene.render.filepath) == 0:
            if rs.saveInBlendFolder == False: self._autoSaveRender = False
            else:
                self._autoSaveRender = True
                self.path = '//'
        else:
            self._autoSaveRender = True
            if rs.saveInBlendFolder == False:
                self.path = bpy.context.scene.render.filepath
            else: self.path = '//'
        #]Autosave

    ## Application handlers[---
        bpy.app.handlers.render_pre.append(self.pre)
        bpy.app.handlers.render_post.append(self.post)
        bpy.app.handlers.render_cancel.append(self.cancelled)
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window) #timer Event
        context.window_manager.modal_handler_add(self)
        #]Application handlers
        

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        sc = bpy.context.scene
        render = sc.render
        cs = sc.camera.RBTab_obj_Settings
        rs = sc.RBTab_Settings

        if event.type == 'TIMER':
            KamRender = False

            #Test to avoid render display mode SCREEN.
            #If is active during this batch render mode, you lose your workspace layout!
            #if bpy.context.scene.render.display_mode not in ('AREA', 'NONE', 'WINDOW'):
            if bpy.context.preferences.view.render_display_type not in ('AREA', 'NONE', 'WINDOW'):
                #Force AREA mode if chosen.
                bpy.context.preferences.view.render_display_type ='AREA'

        ## Exit Batch Render[---
            if True in (not self.cameras, self.stop is True):
                bpy.app.handlers.render_pre.remove(self.pre)
                bpy.app.handlers.render_post.remove(self.post)
                bpy.app.handlers.render_cancel.remove(self.cancelled)
                context.window_manager.event_timer_remove(self._timer)

                #sc.frame_current = 1

                rs.frameRenderType = ""
                    
                if rs.onlyForThisJob:
                    render.image_settings.file_format = rs.currentFormatRenderType
                    rs.onlyForThisJob = False

                if self._autoSaveRender == True:  sc.render.filepath = self.path
                else: sc.render.filepath = ''

                if self.stop == True: return {"FINISHED"}
                elif rs.playAfterRender == True or rs.poweroffAfterRender == True: bpy.ops.renderevents.end_events("INVOKE_DEFAULT")

                return {"FINISHED"}
            #]Exit Batch Render

            elif self.rendering is False:

            ## Batch Render without timeline marker[---
                if len(self.marker_list) == 0:
                    sc.camera = bpy.data.objects[self.cameras[0]]

                    cs = sc.camera.RBTab_obj_Settings
                    rs = sc.RBTab_Settings

                    if cs.Custom_CamRes_prop == True:
                        render.resolution_x   = cs.Custom_CamHRes_prop
                        render.resolution_y   = cs.Custom_CamVRes_prop
                        render.pixel_aspect_x = cs.Custom_CamHPixRes_prop
                        render.pixel_aspect_y = cs.Custom_CamVPixRes_prop
                    else :
                        render.resolution_x   = rs.Default_HRes_prop
                        render.resolution_y   = rs.Default_VRes_prop
                        render.pixel_aspect_x = rs.Default_HPixRes_prop
                        render.pixel_aspect_y = rs.Default_VPixRes_prop

                    sc.render.filepath = self.path + self.cameras[0]

                    bpy.ops.render.render("INVOKE_DEFAULT", write_still=self._autoSaveRender)
#                    bpy.ops.render.render('INVOKE_DEFAULT',animation=True)
                #]Batch Render with no timeline marker

            ## Batch Render with timeline marker[---
                elif len(self.marker_list) >0:

                ## Render camera with timeline marker[---
                    for marker in self.marker_list_cameras:
                        if self.cameras[0] == marker.camera.name :
                            sc.camera = bpy.data.objects[self.cameras[0]]
                            sc.frame_current = marker.frame

                            cs = sc.camera.RBTab_obj_Settings
                            rs = sc.RBTab_Settings

                            if cs.Custom_CamRes_prop == True:
                                render.resolution_x   = cs.Custom_CamHRes_prop
                                render.resolution_y   = cs.Custom_CamVRes_prop
                                render.pixel_aspect_x = cs.Custom_CamHPixRes_prop
                                render.pixel_aspect_y = cs.Custom_CamVPixRes_prop
                            else :
                                render.resolution_x   = rs.Default_HRes_prop
                                render.resolution_y   = rs.Default_VRes_prop
                                render.pixel_aspect_x = rs.Default_HPixRes_prop
                                render.pixel_aspect_y = rs.Default_VPixRes_prop

                            sc.render.filepath = self.path + self.cameras[0]

                            bpy.ops.render.render("INVOKE_DEFAULT", write_still= self._autoSaveRender)
#                            bpy.ops.render.render('INVOKE_DEFAULT',animation=True)

                            KamRender = True
                            break
                    #]Render with timeline marker

                ## Render camera without timeline marker[---
                    if KamRender == False:

                        sc.camera = bpy.data.objects[self.cameras[0]]
                        chosen_camera = sc.camera

                        cs = sc.camera.RBTab_obj_Settings
                        rs = sc.RBTab_Settings

                        if cs.Custom_CamRes_prop == True:
                            render.resolution_x   = cs.Custom_CamHRes_prop
                            render.resolution_y   = cs.Custom_CamVRes_prop
                            render.pixel_aspect_x = cs.Custom_CamHPixRes_prop
                            render.pixel_aspect_y = cs.Custom_CamVPixRes_prop
                        else :
                            render.resolution_x   = rs.Default_HRes_prop
                            render.resolution_y   = rs.Default_VRes_prop
                            render.pixel_aspect_x = rs.Default_HPixRes_prop
                            render.pixel_aspect_y = rs.Default_VPixRes_prop

                        sc.render.filepath = self.path + self.cameras[0]

                        marker = None
                        bpy.context.scene.frame_current = 0
                        current_frame = sc.frame_current
                        for m in reversed(sorted(filter(lambda m: m.frame <= current_frame,sc.timeline_markers),key=lambda m: m.frame)):
                            marker = m
                            break
                        marker_name = chosen_camera.name
                        if marker and (marker.frame == current_frame):
                            marker.name = marker_name
                        else:
                            marker = sc.timeline_markers.new(marker_name)
                        marker.frame = sc.frame_current
                        marker.camera = chosen_camera
                        marker.select = True
                        for other_marker in [m for m in sc.timeline_markers if m != marker]:
                            other_marker.select = False

                        bpy.ops.render.render("INVOKE_DEFAULT", write_still=self._autoSaveRender)
#                        bpy.ops.render.render('INVOKE_DEFAULT',animation=True)
                    #]Render camera without timeline marker

                #]Batch Render with timeline marker
                

        return {"PASS_THROUGH"}


# RENDER CHOSEN CAMERA ##################################################################################
class kh_SCENECAMERA_OT_Render(Operator):
    bl_idname      = "cameramanager.render_scene_camera"
    bl_label       = "Render Camera"
    bl_description = "Render this camera"

    KamCurrent      = None
    _timer          = None
    finish         = None
    _stop           = None
    _chosenCamera   = None
    path            = "//"
    _autoSaveRender = None
    _rendering      = None
    _currentRenderFileFormat = ''

    renderFrom : bpy.props.StringProperty(default ='')
    
    def renderComplete(self, dummy, thrd = None):
        scene  = bpy.context.scene
        rs     = scene.RBTab_Settings
        render = scene.render
        self.finish = True
        if scene.frame_current == 0:
            marker_list = scene.timeline_markers
            for m in marker_list:
                if m.camera == scene.camera:
                    scene.timeline_markers.remove(m)
        # اسم الكولكشن المستهدف
        target_collection_name = "3D Model"
        target_collection = bpy.data.collections.get(target_collection_name)
        if target_collection:
            target_collection.hide_viewport = False
        else:
            print(f"الكولكشن '{target_collection_name}' غير موجود.")

    def renderCancel(self, dummy, thrd = None):
        scene  = bpy.context.scene
        render = scene.render
        self._stop = True
        if scene.frame_current == 0:
            marker_list = scene.timeline_markers
            for m in marker_list:
                if m.camera == scene.camera:
                    scene.timeline_markers.remove(m)
        # اسم الكولكشن المستهدف
        target_collection_name = "3D Model"
        target_collection = bpy.data.collections.get(target_collection_name)
        if target_collection:
            target_collection.hide_viewport = False
            

        else:
            print(f"الكولكشن '{target_collection_name}' غير موجود.")

    def execute(self, context):                
        scene = context.scene
        rs    = scene.RBTab_Settings
        chosen_camera = context.active_object
        render        = scene.render
        KamCurrent    = None
        self._chosenCamera = context.active_object
        bpy.context.space_data.shading.type = 'SOLID'
        bpy.context.preferences.system.gl_texture_limit = 'CLAMP_OFF'
        bpy.context.preferences.system.gl_texture_limit = 'CLAMP_1024'
        
        try:
            if bpy.data.filepath:
                if os.path.exists(bpy.data.filepath):
                    bpy.ops.wm.save_mainfile()
        except RuntimeError as e:
            if "Unable to pack file, source path" in str(e):
                pass  # تجاوز الأمر في حالة حدوث الخطأ المحدد
            else:
                raise e 
        # اسم الكولكشن المستهدف
        target_collection_name = "3D Model"
        target_collection = bpy.data.collections.get(target_collection_name)
        if target_collection:
            target_collection.hide_viewport = True
        else:
            print(f"الكولكشن '{target_collection_name}' غير موجود.")
        

        if rs.saveInBlendFolder: render.filepath = '//'
        
        ### Check render File Format[---
        imageFormat   = ['TIFF','BMP','IRIS','JPEG2000','TARGA','TARGA_RAW','CINEON','DPX','OPEN_EXR','OPEN_EXR_MULTILAYER','HDR','JPEG','PNG']
        if render.image_settings.file_format not in imageFormat and render.filepath != '':
            self.report({"WARNING"}, 'Cannot write a single file with an animation format selected')
            bpy.ops.render.renderformat("INVOKE_DEFAULT")
            return {"CANCELLED"}
        #]Check render File Format

        ### Check Sound File For Alarm[---
        if rs.playAfterRender == True:
            a,soundType = os.path.splitext(rs.soundToPlay)
            soundExt    = bpy.path.extensions_audio

            if str.lower(soundType) not in soundExt or os.path.exists(bpy.path.abspath(rs.soundToPlay)) == False:
                rs.soundToPlay = ''
                ShowMessageBox("Choose a sound file for alarm before !", "Wrong Sound File Type OR Not Exist", 'ERROR')
                self.report({"WARNING"}, 'Wrong Sound File Type OR Not Exist')
                return {"CANCELLED"}
        #]Check Sound File For Alarm

        ### Autosave & Render file path[---
        if len(bpy.context.scene.render.filepath) == 0:
            if rs.saveInBlendFolder == False: self._autoSaveRender = False
            else:
                self._autoSaveRender = True
                self.path = '//'
        else:
            self._autoSaveRender = True
            if rs.saveInBlendFolder == False:
                self.path = bpy.context.scene.render.filepath
            else: self.path = '//'
        #]Autosave

        bpy.app.handlers.render_complete.append(self.renderComplete)
        bpy.app.handlers.render_cancel.append(self.renderCancel)
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)

        self._rendering = True

        return {"RUNNING_MODAL"}


    def modal(self, context, event):
        scene  = context.scene
        render = scene.render
        rs     = scene.RBTab_Settings

    ### EXIT after render is done or canceled[---
        if self.finish or self._stop:
            self._rendering = False

            bpy.app.handlers.render_complete.remove(self.renderComplete)
            bpy.app.handlers.render_cancel.remove(self.renderCancel)
            context.window_manager.event_timer_remove(self._timer)

            rs.frameRenderType = ""
            
            if rs.onlyForThisJob:
                render.image_settings.file_format = rs.currentFormatRenderType
                rs.onlyForThisJob = False

            if self._autoSaveRender == True:  scene.render.filepath = self.path
            else: scene.render.filepath = ''

            if self._stop == True: return {"FINISHED"}
            elif rs.playAfterRender == True or rs.poweroffAfterRender == True: bpy.ops.renderevents.end_events("INVOKE_DEFAULT")

            return {"FINISHED"}
        #]EXIT

        if self._rendering == True:
            self._rendering = False

            render        = scene.render
            KamCurrent    = None

            bpy.context.view_layer.objects.active = self._chosenCamera

            marker_list = context.scene.timeline_markers
            cameras     = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)


        ### Checklist for avoid some errors[---
            if context.active_object is None:
                if len(cameras) == 0:
                    ShowMessageBox("No camera found in this scene !", "Render Error", 'ERROR')
                    self.report({"ERROR"}, 'No camera found in this scene !')
                    return {"FINISHED"}
                elif len(cameras) > 0 and scene.camera is None:
                    bpy.ops.object.select_all(action='DESELECT')
                    self._chosenCamera = cameras[0]
                    self._chosenCamera.select_set(state = True)
                    scene.camera  = self._chosenCamera
                elif len(cameras) == 1 :
                    bpy.ops.object.select_all(action='DESELECT')
                    self._chosenCamera = cameras[0]
                    self._chosenCamera.select_set(state = True)
                    scene.camera  = self._chosenCamera
                elif len(cameras) > 1:
                    bpy.ops.object.select_all(action='DESELECT')
                    self._chosenCamera = scene.camera
                    self._chosenCamera.select_set(state = True)
                    bpy.context.view_layer.objects.active = self._chosenCamera
            else:
                if len(cameras) == 0:
                    ShowMessageBox("No Camera in this scene !", "Render", 'ERROR')
                    return {"FINISHED"}
                elif len(cameras) > 0 and scene.camera is None:
                    bpy.ops.object.select_all(action='DESELECT')
                    self._chosenCamera = cameras[0]
                    self._chosenCamera.select_set(state = True)
                    scene.camera  = self._chosenCamera
                elif len(cameras) == 1 :
                    if context.active_object.type != 'CAMERA':
                        #print("no camera active")
                        bpy.ops.object.select_all(action='DESELECT')
                        self._chosenCamera = cameras[0]
                        self._chosenCamera.select_set(state = True)
                        scene.camera  = self._chosenCamera
                elif len(cameras) > 1:
                    if context.active_object.type != 'CAMERA' :
                        bpy.ops.object.select_all(action='DESELECT')
                        self._chosenCamera = scene.camera
                        self._chosenCamera.select_set(state = True)
                        bpy.context.view_layer.objects.active = self._chosenCamera
            #]Checklist


            #if bpy.context.scene.render.display_mode not in ('AREA', 'NONE', 'WINDOW'):  self.renderFrom = 'PROPERTIES'
            if bpy.context.preferences.view.render_display_type not in ('AREA', 'NONE', 'WINDOW'):  self.renderFrom = 'PROPERTIES'

            if self.renderFrom == 'TAB':
                scene.camera  = bpy.context.space_data.camera
                self._chosenCamera = bpy.context.space_data.camera
            elif self.renderFrom in ('PROPERTIES','CAMANAGER'): scene.camera  = self._chosenCamera

            x  = render.resolution_x
            y  = render.resolution_y

            cs = self._chosenCamera.RBTab_obj_Settings
            rs = scene.RBTab_Settings

            if cs.Custom_CamRes_prop == True:
                render.resolution_x   = cs.Custom_CamHRes_prop
                render.resolution_y   = cs.Custom_CamVRes_prop
                render.pixel_aspect_x = cs.Custom_CamHPixRes_prop
                render.pixel_aspect_y = cs.Custom_CamVPixRes_prop
            else :
                render.resolution_x   = rs.Default_HRes_prop
                render.resolution_y   = rs.Default_VRes_prop
                render.pixel_aspect_x = rs.Default_HPixRes_prop
                render.pixel_aspect_y = rs.Default_VPixRes_prop

            if len(marker_list) > 0:
                bpy.ops.object.select_all(action='DESELECT')
                self._chosenCamera.select_set(state = True)
                bpy.context.view_layer.objects.active = scene.camera

                if self.renderFrom == 'TAB':

                    bpy.context.space_data.camera = bpy.data.objects[scene.camera.name]
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                            break

                for marker in marker_list:
                    if self._chosenCamera == marker.camera:
                        scene.camera  = marker.camera
                        scene.frame_current = marker.frame

                        scene.render.filepath = self.path + scene.camera.name
                        bpy.ops.render.render("INVOKE_DEFAULT", write_still=self._autoSaveRender)

                        return {"PASS_THROUGH"}

                marker = None

                scene.frame_current = 0

                current_frame = scene.frame_current

                for m in reversed(sorted(filter(lambda m: m.frame <= current_frame,scene.timeline_markers),key=lambda m: m.frame)):
                    marker = m
                    break

                marker_name = scene.camera.name

                if marker and (marker.frame == current_frame):
                    marker.name = marker_name
                else:
                    marker = scene.timeline_markers.new(marker_name)

                marker.frame  = scene.frame_current
                marker.camera = scene.camera
                marker.select = True

                for other_marker in [m for m in scene.timeline_markers if m != marker]:
                    other_marker.select = False

                scene.render.filepath = self.path + scene.camera.name
                bpy.ops.render.render("INVOKE_DEFAULT", write_still=self._autoSaveRender)

            elif len(marker_list) == 0 :
                bpy.ops.object.select_all(action='DESELECT')
                self._chosenCamera.select_set(state = True)
                bpy.context.view_layer.objects.active = scene.camera

                if self.renderFrom in ('TAB', 'CAMANAGER'):
                    bpy.context.space_data.camera = bpy.data.objects[scene.camera.name]
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            context.area.spaces[0].region_3d.view_perspective = 'CAMERA'
                            break

                scene.render.filepath = self.path + scene.camera.name
                bpy.ops.render.render("INVOKE_DEFAULT", write_still=self._autoSaveRender)

        return {"PASS_THROUGH"}


# TOGGLE RENDER ORIENTATION ##################################################################################
class kh_MYBIGBUTTONTAB_OT_toggle_orientation(Operator):
    bl_idname      = "render.toggle_orientation"
    bl_label       = "Toggle Orientation"
    bl_description = (" \u2022 shift + click: Square dimensions \n"
                     "    (H Dimension as reference)")
    #bl_options = {'UNDO'}}

    def invoke(self, context, event):
        scene  = context.scene
        rs     = scene.RBTab_Settings
        render = scene.render
        bpy.ops.view3d.view_center_camera()
       
        

        if event.shift:
            render.resolution_y   = render.resolution_x
            render.pixel_aspect_y = render.pixel_aspect_x
            bpy.ops.view3d.view_center_camera()
           
            return {'FINISHED'}

        if rs.switchRenderRotation_prop == False:
            x    = render.resolution_x
            y    = render.resolution_y
            pa_x = render.pixel_aspect_x
            pa_y = render.pixel_aspect_y

            render.resolution_x   = y
            render.resolution_y   = x
            render.pixel_aspect_x = pa_y
            render.pixel_aspect_y = pa_x

            rs.switchRenderRotation_prop = True
            bpy.ops.view3d.view_center_camera()

        elif rs.switchRenderRotation_prop == True:
            x    = render.resolution_y
            y    = render.resolution_x
            pa_x = render.pixel_aspect_y
            pa_y = render.pixel_aspect_x

            render.resolution_x   = x
            render.resolution_y   = y
            render.pixel_aspect_x = pa_x
            render.pixel_aspect_y = pa_y

            rs.switchRenderRotation_prop = False
            bpy.ops.view3d.view_center_camera()

        return {'FINISHED'}


# STORE DEFAULT DIMENSION ##################################################################################
class kh_MYBIGBUTTONTAB_OT_store_defaultres(Operator):
    bl_idname      = "render.store_as_defaultres"
    bl_label       = "Set Current Resolution as Default"
    #bl_options = {'UNDO'}
    bl_description = (" \u2022 Shift + Click: Recover Last")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        scene = context.scene
        rs    = scene.RBTab_Settings
        rd    = scene.render

        if event.shift:
            rd.resolution_x   = rs.Default_HRes_prop
            rd.resolution_y   = rs.Default_VRes_prop
            rd.pixel_aspect_x = rs.Default_HPixRes_prop
            rd.pixel_aspect_y = rs.Default_VPixRes_prop
           

        else:
            rs.Default_HRes_prop    = rd.resolution_x
            rs.Default_VRes_prop    = rd.resolution_y
            rs.Default_HPixRes_prop = rd.pixel_aspect_x
            rs.Default_VPixRes_prop = rd.pixel_aspect_y
            

        return {'FINISHED'}


# CUSTOM CAMERA RESOLUTION ##################################################################################
class kh_SCENECAMERA_OT_CustomResolution(Operator):
    bl_idname = "cameramanager.custom_resolution"
    bl_label = "Custom Resolution"
    bl_description = "Set current resolution as custom camera resolution"
    #bl_options = {'UNDO'}

    crrefresh : bpy.props.BoolProperty(default = False)
    crdel     : bpy.props.BoolProperty(default = False)

    def invoke(self, context, event):
        scene  = context.scene
        render = scene.render
        ob     = context.active_object
        rs     = scene.RBTab_Settings
        cs     = ob.RBTab_obj_Settings

        x      = render.resolution_x
        y      = render.resolution_y
        pa_x   = render.pixel_aspect_x
        pa_y   = render.pixel_aspect_y
        bpy.ops.view3d.view_center_camera()


        cameras      = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        selectedObj  = bpy.context.selected_objects
        selectedCam  = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        noCustomDimCam = sorted([o for o in cameras if o.RBTab_obj_Settings.Custom_CamRes_prop == False],key=lambda o: o.name)

        selectedCustomDimCam = list(set(selectedCam) - set(noCustomDimCam))
        _cameras = []

        if self.crdel == True:

            if event.alt: _cameras = selectedCustomDimCam
            else : _cameras.append(context.active_object)

            for camera in _cameras :
                cs = camera.RBTab_obj_Settings

                cs.Custom_CamRes_prop     = False

                cs.Custom_CamHRes_prop    = rs.Default_HRes_prop
                cs.Custom_CamVRes_prop    = rs.Default_VRes_prop
                cs.Custom_CamHPixRes_prop = rs.Default_HPixRes_prop
                cs.Custom_CamVPixRes_prop = rs.Default_VPixRes_prop

                render.resolution_x       = rs.Default_HRes_prop
                render.resolution_y       = rs.Default_VRes_prop
                render.pixel_aspect_x     = rs.Default_HPixRes_prop
                render.pixel_aspect_y     = rs.Default_VPixRes_prop

            self.crdel = False
        
            return {'FINISHED'}

        if cs.Custom_CamRes_prop == False:
            if event.alt: _cameras = selectedCam
            else : _cameras.append(context.active_object)
            for camera in _cameras :
                cs = camera.RBTab_obj_Settings

                cs.Custom_CamHRes_prop    = x
                cs.Custom_CamVRes_prop    = y
                cs.Custom_CamHPixRes_prop = pa_x
                cs.Custom_CamVPixRes_prop = pa_y
                cs.Custom_CamRes_prop     = True

            return {'FINISHED'}

        elif cs.Custom_CamRes_prop == True:
            if self.crrefresh == False:
               return {'FINISHED'}

            elif self.crrefresh == True:
                cs.Custom_CamHRes_prop    = x
                cs.Custom_CamVRes_prop    = y
                cs.Custom_CamHPixRes_prop = pa_x
                cs.Custom_CamVPixRes_prop = pa_y
                self.crrefresh            = False
                return {'FINISHED'}
            
        


#EVENTS AFTER RENDER##################################################################################
class kh_RENDEREVENTS_OT_endEvents(Operator):
    bl_description = 'Play sound and/or Power Off'
    bl_idname      = 'renderevents.end_events'
    bl_label       = 'Events After Render'

    _stop    = False
    _play    = False
    _timer   = None
    _timeout = None
    handle   = None

    if platform.system().startswith('Win'): OS  ='WINDOWS'
    elif platform.system().startswith('Lin'):OS ='LINUX'
    else : OS ='MacOS'

    testSoundToPlay: bpy.props.BoolProperty(default = False)

#    @classmethod
#    def poll(cls, context):
#        return context.scene.RBTab_Settings.soundToPlay != ''

    def modal(self, context, event):
        scene  = context.scene
        rs     = scene.RBTab_Settings

        if event.type == 'ESC' or rs.abortAlarm == True:
            context.window_manager.event_timer_remove(self._timer)
            if rs.playAfterRender == True: self.handle.stop()
            rs.alarmInProgress = False
            rs.abortAlarm = False
            rs.countDownAfterRender = 0
            self.testSoundToPlay = False
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
            #print("________________Abort")
            return {'FINISHED'}

        elif event.type =='TIMER':
            if self._play == True:
                if self._stop == False and self.handle.status == False:
                    context.window_manager.event_timer_remove(self._timer)
                    rs.alarmInProgress = False
                    rs.abortAlarm = False
                    self.testSoundToPlay = False
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
                    #print("________________Abort")
                    return {'FINISHED'}
                elif self._stop == True and self.testSoundToPlay == False:
                    if self.handle.status == False:
                        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                        self._timeout -= 1
                        rs.countDownAfterRender = self._timeout
                        print(self._timeout)
                        if self._timeout == 0:
                            rs.countDownAfterRender = 0
                            rs.abortAlarm = False
                            if self.OS == 'WINDOWS':
                                print(self.OS)
                                subprocess.call('shutdown /s /f')
                            elif self.OS == 'LINUX':
                                print(self.OS)
#                                bpy.ops.wm.quit_blender()
                                os.system('shutdown -h now')
                            elif self.OS == 'MacOS':
                                print(self.OS)
                                subprocess.call(['osascript', '-e','tell app "System Events" to shut down'])

                            rs.alarmInProgress = False
                            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
                            #rs.countDownAfterRender = 0
                            #print("________________STOP")
                            self.handle.stop()
                            context.window_manager.event_timer_remove(self._timer)
                            return {'FINISHED'}
            elif self._play == False and self.testSoundToPlay == False:
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                rs.countDownAfterRender = self._timeout
                self._timeout -= 1
                print(self._timeout)
                if self._timeout == 0:
                    rs.alarmInProgress = False
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
                    rs.countDownAfterRender = 0
                    if self.OS == 'WINDOWS':
                        print(self.OS)
                        subprocess.call('shutdown /s /f')
                    elif self.OS == 'LINUX':
                        print(self.OS)
                        bpy.ops.wm.quit_blender()
                        #os.system('shutdown -h now')
                    elif self.OS == 'MacOS':
                        print(self.OS)
                        subprocess.call(['osascript', '-e','tell app "System Events" to shut down'])

                    #print("________________STOP")
                    context.window_manager.event_timer_remove(self._timer)
                    
                    return {'FINISHED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        scene  = context.scene
        rs     = scene.RBTab_Settings
        self._timeout = rs.timeoutPowerOff

        if rs.soundToPlay !='':
            a,soundType = os.path.splitext(rs.soundToPlay)
            soundExt    = bpy.path.extensions_audio

        ### Save a Copy of current file with "_powerOff" suffix before shutdown IF is dirty[---
        if rs.poweroffAfterRender and bpy.data.is_dirty and self.testSoundToPlay == False:
            _name,_ext = os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))
            _path      = os.path.dirname(bpy.data.filepath)
            _name      = _name + "_PowerOff" + _ext
            _pathName  = os.path.join(_path,_name)

            bpy.ops.wm.save_as_mainfile(filepath=_pathName,copy=True)
        #]Save a Copy

        if rs.playAfterRender == True:
            if (str.lower(soundType) in soundExt) and os.path.exists(bpy.path.abspath(rs.soundToPlay)) == True:
                soundToPlay = bpy.path.abspath(rs.soundToPlay)
                if self._play == False:
                    device = aud.Device()
                    sound  = aud.Sound(os.path.normpath(soundToPlay))
                    self.handle = device.play(sound.volume(80))
                    if rs.loopSoundToPlay == True and rs.poweroffAfterRender == True: rs.loopSoundToPlay = False
                    if rs.loopSoundToPlay == True and rs.poweroffAfterRender == False: self.handle.loop_count = -1
                    else: self.handle.loop_count = rs.repeatSoundToPlay
                    self._play = True
            else:
                rs.soundToPlay = ''
                self.testSoundToPlay == False
                ShowMessageBox("Choose a sound file before !", "Wrong Sound File Type OR Not Exist", 'ERROR')
                self.report({"WARNING"}, 'Wrong Sound File Type OR Not Exist')
                return {"CANCELLED"}

            if rs.poweroffAfterRender == True and self.testSoundToPlay == False: self._stop = True
        else: self._stop = True

        rs.alarmInProgress = True
        rs.countDownAfterRender = 0
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
        self._timer = context.window_manager.event_timer_add(1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


#RENDER FILE FORMAT ##################################################################################
class kh_RENDER_OT_Renderformat(Operator):
    bl_idname = "render.renderformat"
    bl_label = "WARNING !"
    
    imageFileFormat: EnumProperty(
        name        ="Image File Format",
        description ='Image File Format',
        items       =[('PNG','PNG','','IMAGE',1),
                      ('JPEG','JPEG','','IMAGE',2),
                      ('JPEG2000','JPEG2000','','IMAGE',5),
                      ('BMP','BMP','','IMAGE',3),
                      ('TIFF','TIFF','','IMAGE',4),
                      ('TARGA','TARGA','','IMAGE',6),
                      ('TARGA_RAW','TARGA_RAW','','IMAGE',7),
                      ('CINEON','CINEON','','IMAGE',8),
                      ('DPX','DPX','','IMAGE',9),
                      ('OPEN_EXR','OPEN_EXR','','IMAGE',10),
                      ('OPEN_EXR_MULTILAYER','OPEN_EXR_MULTILAYER','','IMAGE',11),
                      ('HDR','HDR','','IMAGE',12),
                      ],default='PNG')

    def draw(self, context):
        scene          = context.scene
        rs             = scene.RBTab_Settings
        rd             = scene.render
        image_settings = rd.image_settings

        box = self.layout.box()
        row = box.row(align=True)
        row.alignment='CENTER'
        row.alert = True
        row.label(text = "Animation format selected !", icon="ERROR")


        row = box.row(align=True)
        row.alignment='CENTER'
        row.alert = True
        row.scale_y = 0.25
        row.label(text = "     Cannot write a single file")
        
        row = box.row()
        row.alignment='CENTER'
        row.scale_y = 1.5
        row.label(text = "Please Choose an IMAGE File Format")

        row = box.row()
        row.prop(self,'imageFileFormat',icon='IMAGE',text="")

        box.use_property_split = True
        box.use_property_decorate = False
        row = box.row(align=True)
        row.prop(rs,'onlyForThisJob',text='only for this job')

        if rs.onlyForThisJob:
            row = box.row(align=True)
            row.active = False
            row.alignment='CENTER'
            row.label(text = "( After Render Reset to : {0} )".format(image_settings.file_format))


    def execute(self, context):
        scene  = bpy.context.scene
        rs     = scene.RBTab_Settings
        rd     = scene.render
        image_settings = rd.image_settings
        
        image_settings.file_format = self.imageFileFormat

        return {'FINISHED'}


    def invoke(self, context, event):
        
        scene  = bpy.context.scene
        rs     = scene.RBTab_Settings
        rd     = scene.render

        rs.onlyForThisJob = False
        rs.currentFormatRenderType = rd.image_settings.file_format

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


# Null ##################################################################################
class kh_SCENECAMERA_OT_Null(Operator):
    bl_idname      = "cameramanager.null_tool"
    bl_label       = ""
    bl_description = "Camera Manager"

    nullMode : bpy.props.StringProperty(name="tool", default="")

    def invoke(self, context, event):
        scene         = context.scene
        chosen_camera = context.active_object
        selectedObj   = context.selected_objects
        cameras       = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        selectedCam   = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)

        if self.nullMode == 'SELECT':
            if chosen_camera not in selectedCam:
                if event.alt:
                    bpy.ops.cameramanager.select_tool("INVOKE_DEFAULT",selectTool = "INVERT")
                elif event.shift:
                    bpy.ops.cameramanager.select_tool("INVOKE_DEFAULT",selectTool = "ALL")
                else:
                    bpy.ops.cameramanager.select_tool("INVOKE_DEFAULT",selectTool = "NONE")

        elif self.nullMode == 'NOTSELECTED':
            self.report({"INFO"}, 'Select Camera Before !')

        elif self.nullMode == 'NULL':
            self.nullMode == ''
            return {"FINISHED"}

        self.nullMode == ''

        return {"FINISHED"}


# CAMERA MANAGER PANEL ######################################################################################
script_dir = os.path.dirname(os.path.abspath(__file__))
my_icons_dir = os.path.join(script_dir, "icons")

preview_collection = bpy.utils.previews.new()
preview_collection.load("12.png", os.path.join(my_icons_dir, "12.png"), 'IMAGE')

preview_collection3 = bpy.utils.previews.new()
preview_collection3.load("3.png", os.path.join(my_icons_dir, "3.png"), 'IMAGE')

preview_collection4 = bpy.utils.previews.new()
preview_collection4.load("5.png", os.path.join(my_icons_dir, "5.png"), 'IMAGE')

preview_collection5 = bpy.utils.previews.new()
preview_collection5.load("14.png", os.path.join(my_icons_dir, "14.png"), 'IMAGE')

preview_collection6 = bpy.utils.previews.new()
preview_collection6.load("18.png", os.path.join(my_icons_dir, "18.png"), 'IMAGE')




class kh_CAMMANAGER_PT_Cammanager(Panel):
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context     = ""
    bl_category    = "KH-Tools"
    bl_label       = "Camera Manager"
    bl_idname      = "CAMMANAGER_PT_Cammanager"
    
    

    @classmethod
    def poll(cls, context):
        # استخدام الدالة المساعدة للبحث عن إعدادات الإضافة
        return get_addon_preferences(context, 'Camera_Manager') == True

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon_value=preview_collection['12.png'].icon_id)
        except KeyError:
            pass


    def draw(self, context):
        
        layout  = self.layout
        scene   = context.scene
        rs      = scene.RBTab_Settings
        render  = scene.render
        cameras = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)

        selectedObj    = bpy.context.selected_objects
        selectedCam    = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        constraintsCam = sorted([o for o in cameras if len(o.constraints) > 0],key=lambda o: o.name)

        animDataCam    = sorted([o for o in cameras
                                    if (o.animation_data is not None) or (o.data.animation_data is not None)
                                    ],key=lambda o: o.name)
        emptyAnimCam   = sorted([o for o in animDataCam
                                    if (o.animation_data is not None and o.animation_data.action is None)
                                    or (o.data.animation_data is not None and o.data.animation_data.action is None)
                                    ],key=lambda o: o.name)

        render_all_list = []

        if rs.cmOptions == False:
            for camera in cameras:
                rs_obj = camera.RBTab_obj_Settings
                if rs_obj.Custom_CamRender_prop == True:
                    render_all_list += sorted([cameras])

            marker_list         = context.scene.timeline_markers
            marker_list_camera  = [o for o in marker_list if o.camera != None]
            list_marked_cameras = [o.camera for o in marker_list if o != None]
            render_marker_list  = []

            for marker in marker_list_camera:
                rs_obj = marker.camera.RBTab_obj_Settings
                if rs_obj.Custom_CamRender_prop == True:
                    render_marker_list += sorted([marker])

    ###Buttons above Cameras List[ ________________________________________________________________________________
            #Add Camera to view button
            row = layout.row(align=True)
            row.operator("cameramanager.add_scene_camera",text='Add', icon='OUTLINER_DATA_CAMERA')
            


            view = context.space_data

            if len(cameras) > 0:
            

                #Camera Lock view button
                _iconlockview=''
                if bpy.context.space_data.lock_camera == True: _iconlockview='LOCKED'
                else: _iconlockview='UNLOCKED'
                #row.operator("object.fullscreen", text="", icon='FULLSCREEN_ENTER')
                row.operator("cameramanager.copy_scene_camera",text='', icon='DUPLICATE')
                row.prop(view, "lock_camera", text="",icon=_iconlockview)
                #row = layout.row(align=True)
                
                row = layout.row()
                row.scale_x=1.7
                #row.prop(view, "lock_camera", text="",icon=_iconlockview)
                
                
                #row = layout.row()
                #row.scale_x=1.7
                row.prop(scene, "depsgraph_update_pre", text="" , icon_value=preview_collection3['3.png'].icon_id)
                row.prop(scene, "depsgraph_load_post", text="" , icon_value=preview_collection4['5.png'].icon_id)
                
                

                #if not scene.depsgraph_update_pre:
                    #row.operator("object.linkd_camera" , icon='WORLD_DATA')           
                

                #row = layout.row(align=True)
                row.prop(scene, "audio_playback_enabled", text="" , icon_value=preview_collection5['14.png'].icon_id)
                row.prop(scene, "render_channels_enabled", text="" , icon="NODE_COMPOSITING")
                row.prop(scene, "computer_to_sleep", text="" , icon_value=preview_collection6['18.png'].icon_id)
                box = layout.box()
                if scene.depsgraph_update_pre:
                    row = box.row()
                    row.prop(scene, "world", text="")
                    
                    active_camera = context.scene.camera
                    active_world = context.scene.world
                    if active_world is not None and active_camera is not None:
                        if active_world.name != active_camera.name:
                            row.operator("object.kh_copyworld", text="" , icon="FILE_REFRESH")
                            
                    row.scale_x= 0.8
                    row.operator("object.delete_world_and_disable_fake_user", text="" , icon="TRASH")
                    
                if scene.audio_playback_enabled:  
                    row = box.row()
                    row.prop(scene, "audio_file" , text="", icon='SOUND')
                        
                #row = layout.row(align=True)
                               

                
    ### ]Buttons above Cameras List

                layout.separator()

    ###Cameras List[ ______________________________________________________________________________________________

                   
                for camera in cameras:
                    rs_obj = camera.RBTab_obj_Settings
                    row    = layout.row(align=True)

                    row.context_pointer_set("active_object", camera)

                    if rs.Manager_ShowSelect == True:
                        if len(selectedCam)>0:

                            if rs.Manager_ShowSelect_Gray == True and len(selectedCam)>1: row.active = False

                            if camera in selectedObj:

                                if rs.Manager_ShowSelect_Pointer == True:
                                    row.operator("cameramanager.null_tool", text="", icon='RIGHTARROW_THIN',emboss=False).nullMode='SELECT'
                                    #row.label(text ="",icon='RIGHTARROW_THIN')

                                if rs.Manager_ShowSelect_Color == True:
                                    row.alert = True

                                row.active = True
                            else:
                                if rs.Manager_ShowSelect_Pointer == True:
                                    row.operator("cameramanager.null_tool", text="", icon='BLANK1',emboss=False).nullMode='SELECT'

                    elif len(selectedCam)>0 and camera in selectedObj: row.alert = True

                    #Preview Camera button
                    _iconPreview       = ''
                    _iconPreviewEmboss = None
                    if camera == bpy.context.space_data.camera:
                        _iconPreview       = 'RESTRICT_VIEW_OFF'
                        _iconPreviewEmboss = True
                        
                    else:
                        if rs_obj.Custom_CamRes_prop == True:
                            if camera == scene.camera:
                                _iconPreview       = 'CAMERA_DATA'
                                _iconPreviewEmboss = False
                            else:
                                _iconPreview       = 'WORKSPACE'
                                _iconPreviewEmboss = False
                        else:
                            if camera == scene.camera:
                                _iconPreview       = 'CAMERA_DATA'
                                _iconPreviewEmboss = False
                            else:
                                _iconPreview       = 'RESTRICT_VIEW_ON'
                                _iconPreviewEmboss = False
                    

                    if len(selectedCam) <=1:
                        row.operator("cameramanager.activpreview_scene_camera",text='', icon=_iconPreview, emboss=_iconPreviewEmboss)
                    elif len(selectedCam) >1 and camera in selectedObj: row.operator("cameramanager.activpreview_scene_camera",text='', icon=_iconPreview)
                    elif len(selectedCam) >1 and camera not in selectedObj:row.operator("cameramanager.activpreview_scene_camera",text='', icon=_iconPreview, emboss=_iconPreviewEmboss)
                    if rs.Manager_ShowSelect == False: row.alert = False

                    #Render button
                    if rs.cmBut_Render == True:
                        if len(selectedCam) <=1:
                            row.operator("cameramanager.render_scene_camera",text='', icon='SEQ_PREVIEW').renderFrom = 'CAMANAGER'
                        #elif len(selectedCam) >1 and camera in selectedObj:row.operator("cameramanager.null_tool", text="", icon='BLANK1',emboss=True).nullMode='SELECT'
                        elif camera not in selectedObj:row.operator("cameramanager.null_tool", text="", icon='SEQ_PREVIEW',emboss=True).nullMode='SELECT'

                    #Camera name          
                    if len(selectedCam) <=1 and camera not in selectedObj: row.prop(camera, "name", text="")
                    elif len(selectedCam) >=1 and camera in selectedObj: row.operator("cameramanager.null_tool", text="{0}".format(camera.name)).nullMode='SELECT'#row.prop(camera, "name", text="",emboss=False)                        
                    else: row.operator("cameramanager.null_tool", text="{0}".format(camera.name),emboss=False).nullMode='SELECT'
                    if camera == bpy.context.space_data.camera:
                        row.operator("cameramanager.copy_scene_camera",text='', icon='DUPLICATE')
                        icon = 'OUTLINER_OB_LIGHT' if camera.name.endswith('-N') else 'LIGHT_DATA'
                        if not camera.name.endswith('-N'):
                            row.operator("cameramanager.trackto_scene_camera", text="", icon=icon)
                            
                        
                        selected_camera = bpy.context.selected_objects 
                        if len(selected_camera) == 2 and selected_camera[0].type == 'CAMERA' and selected_camera[1].type == 'CAMERA':
                            row.operator("cameramanager.copy_location", text="", icon="ORIENTATION_VIEW")


                    #Align View button
                    if rs.cmBut_AlignV == True:
                        if len(selectedCam)<=1:
                            row.operator("cameramanager.alignview_scene_camera", text="", icon='VIEW_PERSPECTIVE')
                        #elif len(selectedCam) >1 and camera in selectedObj:row.operator("cameramanager.null_tool", text="", icon='BLANK1',emboss=True).nullMode='SELECT'
                        elif camera not in selectedObj: row.operator("cameramanager.null_tool", text="", icon='VIEW_PERSPECTIVE',emboss=True).nullMode='SELECT'

               
                    #Align Obj button
                    if rs.cmBut_AlignO == True:
                        if len(selectedCam) <=1 or  camera in selectedCam:
                            row.operator("cameramanager.alignobj_scene_camera", text="", icon='CUBE')
                        else:row.operator("cameramanager.null_tool", text="", icon='CUBE',emboss=True).nullMode='SELECT'

                    #Track To button: Add/Remove
                    if rs.cmBut_Trackto == True:
                        if len(camera.constraints) == 0:
                            #Add TrackTo button
                            if camera in selectedObj or len(selectedCam) <=1:
                                icon = 'OUTLINER_OB_LIGHT' if camera.name.endswith('-N') else 'DUPLICATE'
                                if camera.name.endswith('-N'):
                                    row.operator("cameramanager.trackto_scene_camera", text="", icon=icon)
                                    #row.label(text="", icon=icon)                            
                                 
                            else:row.operator("cameramanager.null_tool", text="", icon='TRACKER',emboss=True).nullMode='SELECT'
                        else :
                            #Remove TrackTo button
                            if camera not in selectedCam and len(selectedCam) <=1:
                                row.operator("cameramanager.removetrackto_scene_camera", text="", icon='CON_FOLLOWTRACK', emboss=False)
                            elif camera in selectedCam and len(selectedCam) >= 1:
                                row.operator("cameramanager.removetrackto_scene_camera", text="", icon='CON_FOLLOWTRACK', emboss=True)
                            elif camera not in selectedCam and len(selectedCam) > 1:
                                row.operator("cameramanager.null_tool", text="", icon='CON_FOLLOWTRACK',emboss=True).nullMode='SELECT'

                    # #Marker button
                    # if rs.cmBut_Marker == True:
                    #     if camera in list_marked_cameras :
                    #         m = 0
                    #         for i,marker in enumerate(marker_list_camera):
                    #             if marker_list_camera[i].frame != 0:
                    #                 if marker.camera == camera and m < 1:#prevent adding button if multiple marker on same camera
                    #                     #Remove marker button
                    #                     if camera in selectedCam :#and len(selectedCam) <=1:
                    #                         row.operator("cameramanager.remove_camera_marker",text='', icon='MARKER_HLT', emboss=True)
                    #                     elif camera not in selectedCam and len(selectedCam) <=1:
                    #                         row.operator("cameramanager.remove_camera_marker",text='', icon='MARKER_HLT', emboss=False)
                    #                     elif camera not in selectedCam and len(selectedCam) > 1:
                    #                         row.operator("cameramanager.null_tool", text="", icon='MARKER_HLT',emboss=False).nullMode='SELECT'
                    #                     m += 1
                    #             elif marker_list_camera[i].frame == 0 and marker.camera == camera:
                    #                 if camera in selectedObj:
                    #                     row.operator("cameramanager.null_tool", text="", icon='BLANK1',emboss=False).nullMode='NULL'
                    #                 elif rs_obj.Custom_CamRender_prop == True and camera not in selectedObj:
                    #                     row.operator("cameramanager.add_camera_marker",text='', icon='MARKER')
                    #                 else:
                    #                     row.operator("cameramanager.add_camera_marker",text='', icon='MARKER')

                    #     #Add marker button
                    #     else:
                    #         if len(selectedCam)<=1:
                    #             row.operator("cameramanager.add_camera_marker",text='', icon='MARKER')
                    #         #elif len(list_marked_cameras)>0 and camera in selectedObj:
                    #         elif camera in selectedObj:
                    #             row.operator("cameramanager.null_tool", text="", icon='BLANK1',emboss=True).nullMode='SELECT'
                    #         elif camera not in selectedObj:
                    #             row.operator("cameramanager.null_tool", text="", icon='MARKER',emboss=True).nullMode='SELECT'


                    #Animation Data
                    if rs.cmBut_AnimData == True:
                        if len(animDataCam) >0:
                            #if bpy.data.cameras[camera.name].animation_data.action != None :
                            if camera in animDataCam:# or bpy.data.cameras[camera.name].animation_data != None :
                                if camera in emptyAnimCam :
                                    if camera in selectedObj and len(selectedCam) <=1:
                                        row.operator("cameramanager.null_tool", text="", icon='KEYFRAME',emboss=True).nullMode='NULL'
                                    elif camera in selectedCam and len(selectedCam) >1:
                                        row.operator("cameramanager.null_tool", text="", icon='KEYFRAME',emboss=True).nullMode='SELECT'
                                    else: row.operator("cameramanager.null_tool", text="", icon='KEYFRAME',emboss=False).nullMode='SELECT'
                                else:
                                    if camera not in selectedObj and len(selectedCam) <=1:
                                        row.operator("cameramanager.null_tool", text="", icon='KEYTYPE_KEYFRAME_VEC',emboss=False).nullMode='NULL'
                                    elif camera not in selectedObj and len(selectedCam) >1:
                                        row.operator("cameramanager.null_tool", text="", icon='KEYFRAME_HLT',emboss=False).nullMode='SELECT'
                                    elif camera in selectedObj or len(selectedCam) >1:
                                        row.operator("cameramanager.null_tool", text="", icon='KEYTYPE_KEYFRAME_VEC',emboss=True).nullMode='NULL'
                                    #else: row.operator("cameramanager.null_tool", text="", icon='KEYFRAME_HLT',emboss=False).nullMode='SELECT'
                            else:
                                if camera in selectedObj:
                                    row.operator("cameramanager.null_tool", text="", icon='BLANK1').nullMode='SELECT'
                                else:row.operator("cameramanager.null_tool", text="", icon='BLANK1',emboss=False).nullMode='SELECT'
                    if len(animDataCam) < 1:row.separator()

                    #Remove camera button
                    if camera not in selectedCam and len(selectedCam) <=1:
                        row.operator("cameramanager.del_scene_camera",text='', icon='PANEL_CLOSE', emboss=False)
                    elif camera in selectedCam and len(selectedCam) >=1:
                        row.operator("cameramanager.del_scene_camera",text='', icon='PANEL_CLOSE', emboss=True)
                    elif camera not in selectedCam and len(selectedCam) >1:
                        row.operator("cameramanager.null_tool", text="", icon='PANEL_CLOSE',emboss=False).nullMode='SELECT'

                    #Render Selection prop
                    if len(cameras) > 2 and rs.switchRenderSelection == True:
                        #row.active = True
                        row.alert = False
                        row.prop(rs_obj,'Custom_CamRender_prop',text='')

                    

    ### ]Cameras List
                
                layout.separator()
                row = layout.row(align=True)

    ###Buttons below Cameras List[ _____________________________________________________________________________________
                #Render All buttons for batch rendering
                if len(cameras) > 1:
                    #row.prop(rs,'SwitchPropertiesBatch',text='', icon ='PROPERTIES')
                    if rs.switchRenderSelection == False:
                        if len(marker_list_camera) < 1 or len(selectedCam) >1:
                            if len(selectedCam) >1:
                                row.operator("cameramanager.render_all_camera",text='Render Selection: {0}'.format(len(selectedCam)), icon='RENDER_RESULT')
                            else:
                                row.operator("cameramanager.render_all_camera",text='Render All Cameras', icon='RENDER_RESULT')
                        if 1 <= len(marker_list_camera) < len(cameras) and len(selectedCam)<2:
                            row.operator("cameramanager.render_all_camera",text='Render All', icon='RENDER_RESULT')
                            row.operator("cameramanager.render_all_camera",text='Render Markers', icon='RENDER_RESULT').tmarkers = True
                        elif len(marker_list_camera) == len(cameras):
                            if scene.frame_current>0 :
                                row.operator("cameramanager.render_all_camera",text='Render All Cameras', icon='RENDER_RESULT')
                            else:
                                row.operator("cameramanager.render_all_camera",text='Render All', icon='RENDER_RESULT')
                                row.operator("cameramanager.render_all_camera",text='Render Markers', icon='RENDER_RESULT').tmarkers = True
                    else:
                        if len(render_all_list) <2:
                            row.label(text='Choose at least two Cameras', icon ='ERROR')
                        elif 1 < len(render_all_list) < len(cameras) :
                            row.operator("cameramanager.render_all_camera",text='Render Selection: {0}'.format(len(render_all_list)), icon='RENDER_RESULT')
                        elif len(render_all_list) == len(cameras) :
                            row.operator("cameramanager.render_all_camera",text='Render All Cameras', icon='RENDER_RESULT')
                elif len(cameras) > 2:
                    if rs.switchRenderSelection == True:
                        if len(render_all_list) <2:
                            row.label(text='Choose at least two Cameras', icon ='ERROR')

                #Switch button for cameras listing for batch rendering
                if len(cameras) > 2:
                    row.separator()
                    row.prop(rs,"switchRenderSelection",text='', icon='RESTRICT_SELECT_OFF')
    ### ]Buttons below Cameras List
                
                row = layout.row()
                current_file_path = bpy.data.filepath
                if current_file_path: 
                    row.operator("object.filepath", text="", icon='FILE_TICK')
                else:
                    row.operator("wm.save_mainfile" , text='Save File' , icon='FILE_TICK')

                row.prop(context.scene.render, "filepath", text="")
                

                row = layout.row(align=True)

            else:
                ##
                row = layout.row(align=True)
                row.alignment='CENTER'
                row.alert = True
                row.label(text=" No cameras in this scene", icon ='ERROR')
                row.alert = False
            
    ###Camera Manager Settings[ _____________________________________________________________________________________
        else:

        ## Manager Options [-----------
            row = layout.row(align=True)
            box = layout.box()
            row = box.row(align=True)
            row.alert = True
            row.alignment='CENTER'

            row.label(text='Manager Options')

            row = box.row(align=True)

            row = row.box()
            row = row.row(align=True)

            row.label(text='Tools Toggles:')

            row.prop(rs,"cmBut_Render",text="",icon='SEQ_PREVIEW')
            row.prop(rs,"cmBut_AlignV",text="",icon='VIEW_PERSPECTIVE')
            
            row.prop(rs,"cmBut_Trackto",text="",icon='DUPLICATE')
            row.prop(rs,"cmBut_Marker",text="",icon='MARKER')
            row.prop(rs,"cmBut_AnimData",text="",icon='KEYTYPE_KEYFRAME_VEC')

            box.use_property_split = True
            box.use_property_decorate = False
            row = layout.row(align=True)
            row = box.row(align=True)
            row = row.box()
            row.prop(rs,'Manager_ShowSelect_Color',text='Selection Highlight')
        ## ]Manager Options

        ## New Camera Lens Settings [-----------
            row = layout.row(align=True)
            box = layout.box()
            row = box.row(align=True)
            row.alert = True
            row.alignment='CENTER'

            row.label(text='New Camera Lens Settings')

            row = box.row(align=True)

            row = row.box()
            row.label(text='Camera Perspective',icon='VIEW_PERSPECTIVE')

            row.prop(rs,"NewCam_lensPersp")
            row = row.row(align=True)

            row.prop(rs,"NewCam_ClipStart",text="Clip Start")
            row.prop(rs,"NewCam_ClipEnd",text="End")

            row = box.row(align=True)

            row = row.box()
            row.label(text='Camera Orthogaphic',icon='VIEW_ORTHO')
            row.prop(rs,"NewCam_lensOrtho",text="Scale")

            row = row.row(align=True)
            row.prop(rs,"NewCam_ClipStartOrtho",text="Clip Start")
            row.prop(rs,"NewCam_ClipEndOrtho",text="End")
            
        ## ]New Camera Lens Settings


# CAMERA QUICK SETTINGS ######################################################################################
class kh_CAMMANAGER_PT_QuickSettings(Panel):
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context     = ""
    bl_category    = "KH-CAM"
    bl_label       = "Settings :"
    #bl_options     = {'DEFAULT_CLOSED'}
    bl_idname      = "CAMMANAGER_PT_QuickSettings"
    bl_parent_id   = "CAMMANAGER_PT_Cammanager"

    _selectedCam   = []

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and context.active_object==bpy.context.space_data.camera) and bpy.context.scene.RBTab_Settings.cmOptions == False

     
    def draw_header_preset(self, context):
        scene   = context.scene
        cameras = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        ob      = context.active_object

        selectedObj    = bpy.context.selected_objects
        selectedCam    = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        noCustomDimCam = sorted([o for o in cameras if o.RBTab_obj_Settings.Custom_CamRes_prop == False],key=lambda o: o.name)

        layout = self.layout
        row    = layout.row(align=True)

        if len(cameras) > 0 and (ob in cameras):
            if len(selectedCam) == 1 :
                if ob in selectedCam:
                    chosen_camera = context.active_object
                    row.label(text="{0}".format(chosen_camera .name))

            elif len(selectedCam) > 1:
                if ob in selectedCam:
                    row.alert = True
                    chosen_camera = context.active_object
                    row.label(text="[..{0}..]".format(chosen_camera .name))
                else:
                    row.active = False
                    chosen_camera = context.active_object
                    row.label(text="{0}".format(chosen_camera .name))
            else:
                chosen_camera = context.active_object
                row.label(text="{0}".format(chosen_camera .name))


    def draw(self, context):
        scene          = context.scene
        rs             = scene.RBTab_Settings
        ob             = context.active_object
        cs             = ob.RBTab_obj_Settings
        render         = scene.render
        cameras        = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)
        view           = context.space_data
        chosen_camera  = bpy.context.object.data
        cam            = chosen_camera

        selectedObj    = bpy.context.selected_objects
        selectedCam    = sorted([o for o in selectedObj if o.type == 'CAMERA'],key=lambda o: o.name)
        noCustomDimCam = sorted([o for o in cameras if o.RBTab_obj_Settings.Custom_CamRes_prop == False],key=lambda o: o.name)

        selectedCustomDimCam = list(set(selectedCam) - set(noCustomDimCam))
        self._selectedCam    = selectedCam

        layout = self.layout

        if len(cameras) > 0 and (ob in cameras):

            row = layout.row(align=True)

#            if len(selectedCam) > 1 and ob not in selectedCam:
#                row.enabled = False
#                layout.emboss = 'NONE'################

            #row.prop(cam, "type", text="")
            #row = layout.row()

            #if len(selectedCam) > 1 and ob not in selectedCam: row.enabled = False ################
            
            if cam.type == 'PERSP':
                camera = context.scene.camera
                row.prop(context.object.data, "show_composition_thirds", text="Grid")
                row.prop(context.object.data.dof, "use_dof", text="Depth of Field")
                
                row = layout.row(align=True)
      
                if context.object.data.dof.use_dof:
                    if context.object.data.dof.focus_object is None:
                        row.prop(context.object.data.dof, "focus_distance", text="Focus Distance")
                    row.prop(context.object.data.dof, "focus_object", text="")
                    
                        
                    layout.prop(context.object.data.dof, "aperture_fstop", text="F-Stop")
                    row = layout.row(align=True)

                row = layout.row()
                row.prop(cam, "lens", text="Focal")
                row.prop(camera, "rotation_euler", text="Rotate", index=2,icon="FILE_REFRESH")
                
                row = layout.row()
                active_camera = context.scene.camera

                #if len(selectedCam) > 1 and ob not in selectedCam: row.enabled = False ################

                row.operator("object.rotate_x_90_operator", text="Two Point", icon="SNAP_PERPENDICULAR")
                row.prop(camera, "location", text='Hi', icon='EMPTY_SINGLE_ARROW', index=2)
                row = layout.row()
                row.prop(active_camera, "lock_rotation", index=0, toggle=True, text="Lock")
                row.prop(camera, "rotation_euler", text="RV", index=0, icon="CON_DISTLIMIT")    
                layout = self.layout
                camera = context.scene.camera
                row = layout.row()
                row.prop(cam, "clip_start", text="Clipping", icon="MOD_PHYSICS")
                row.prop(cam, "shift_y", text="V", icon='MODIFIER')
                
                
            elif cam.type == 'ORTHO':
                box = layout.box()
                row = box.row()
                row.prop(cam, "type", text="Type")
                row = box.row()
                row.prop(cam, "ortho_scale", text="Scale")
                
                row.operator("object.rotate_x_90_operator", text="Front", icon="SNAP_PERPENDICULAR")

            elif cam.type == 'PANO':
                
                engine = context.scene.render.engine
                if engine == 'CYCLES':
                    box = layout.box()
                    row = box.row()
                    row.prop(cam, "panorama_type", text="")
                    row  = box.row()

                    if cam.panorama_type == 'FISHEYE_EQUIDISTANT':
                        row.prop(cam, "fisheye_fov", text="FOV")

                    elif cam.panorama_type == 'FISHEYE_EQUISOLID':
                        row.prop(cam, "fisheye_lens", text="Lens")
                        row.prop(cam, "fisheye_fov", text="FOV")

                    elif cam.panorama_type == 'EQUIRECTANGULAR':
                        row = box.row()
                        row.label(text="Latitude:")
                        row = box.row()
                        row.prop(cam, "latitude_min", text="Min")
                        row.prop(cam, "latitude_max", text="Max")

                        row = box.row()
                        row.label(text="Longitude:")
                        row = box.row()
                        row.prop(cam, "longitude_min", text="Min")
                        row.prop(cam, "longitude_max", text="Max")

                elif engine in {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}:
                    if cam.lens_unit == 'MILLIMETERS':
                        row.prop(cam, "lens")

                    elif cam.lens_unit == 'FOV':
                        row.prop(cam, "angle")

                    row.prop(cam, "lens_unit")

                       
            #if len(selectedCam) > 1 and ob not in selectedCam: row.enabled = False ################

            layout.separator()
            row = layout.row(align=True)

            #if len(selectedCam) > 1 and ob not in selectedCam: row.enabled = False ################

            if cs.Custom_CamRes_prop == False:
                row.operator('cameramanager.custom_resolution',text="Save Custom Resolution",icon='FILE_TICK').crrefresh = False

            elif cs.Custom_CamRes_prop == True and (cs.Custom_CamHRes_prop == render.resolution_x) and (cs.Custom_CamVRes_prop == render.resolution_y):
                row.operator('cameramanager.custom_resolution',text="{0} x {1}".format(cs.Custom_CamHRes_prop,cs.Custom_CamVRes_prop), icon='LOCKED')
                row.operator('cameramanager.custom_resolution',text="", icon='PANEL_CLOSE',emboss=False).crdel = True

            elif cs.Custom_CamRes_prop == True and (cs.Custom_CamHRes_prop != render.resolution_x) or (cs.Custom_CamVRes_prop != render.resolution_y):
                row.operator('cameramanager.custom_resolution',text=" Update Resolution".format(cs.Custom_CamHRes_prop,cs.Custom_CamVRes_prop), icon='FILE_REFRESH').crrefresh = True
                row.operator('cameramanager.custom_resolution',text="", icon='PANEL_CLOSE',emboss=False).crdel = True
                
        
        #row = layout.row()
        scene  = context.scene
        rd     = scene.render
        rs     = scene.RBTab_Settings

        layout = self.layout
        row    = layout.row(align=True)
        

        row.prop(scene.render, 'resolution_x', text="H")
        row.operator("render.toggle_orientation", text="", icon='ARROW_LEFTRIGHT')
        row.prop(scene.render, 'resolution_y', text="V")

        if (rd.resolution_x != rs.Default_HRes_prop) or (rd.resolution_y != rs.Default_VRes_prop):
            row.operator("render.store_as_defaultres", text="", icon='FILE_TICK',emboss=False)
        #file path save render
        



# CAMERA MANAGER FOOTER INFOS ######################################################################################
class kh_CAMMANAGER_PT_InfosCamActiv(Panel):
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context     = ""
    bl_category    = "Render"
    bl_label       = "Camera Infos"
    bl_idname      = "CAMMANAGER_PT_InfosCamActiv"
    bl_options     = {'HIDE_HEADER'}
    bl_parent_id   = "CAMMANAGER_PT_Cammanager"

    @classmethod
    def poll(cls, context):
        return (context.active_object is not None
                and context.active_object==bpy.context.space_data.camera
                and bpy.context.scene.RBTab_Settings.cmOptions == False)

    def draw(self, context):
        scene         = context.scene
        ob            = context.active_object
        cs            = ob.RBTab_obj_Settings
        marker_list   = context.scene.timeline_markers
        chosen_camera = context.active_object
        render        = context.scene.render
        cameras       = sorted([o for o in scene.objects if o.type == 'CAMERA'],key=lambda o: o.name)

        layout = self.layout
        split  = layout.split()

        layout.use_property_split    = True
        layout.use_property_decorate = False

        row         = layout.row(align=True)
        row.scale_y = 0.7

        if (context.active_object is not None):

            if len(cameras) > 0 and (ob in cameras):

                _customDim   = ""
                _trackTo     = ""
                _markerName  = ""
                _markerFrame = ""
                _infos       = ""

                if cs.Custom_CamRes_prop == True: _customDim = "{0}x{1} ".format(cs.Custom_CamHRes_prop,cs.Custom_CamVRes_prop)

                if len(chosen_camera.constraints) > 0 and chosen_camera.constraints[0].target is not None: _trackTo = " [{0}] ".format(chosen_camera.constraints[0].target.name)


                for marker in marker_list:
                    if marker.camera == chosen_camera and scene.frame_current != 0:
                        _markerName  = " <{0}>".format(marker.camera.name)
                        _markerFrame = "({0})".format(marker.frame)

                _infos = _customDim + _trackTo + _markerName + _markerFrame

                if len(chosen_camera.constraints) > 0 and chosen_camera.constraints[0].target is None: _infos ="No Target"

                if _infos != "":
                    if _infos == "No Target":
                        row.alert = True
                        row.label(text = "Track To Error : " + _infos, icon ='ERROR')
                    else: row.label(text = _infos, icon ='INFO')
                


# # RENDER PRESET ######################################################################################
# class kh_RENDER_PT_presets(PresetPanel, Panel):
#     bl_label            = "Render Presets"
#     preset_subdir       = "render"
#     preset_operator     = "script.execute_preset"
#     preset_add_operator = "render.preset_add"


# RENDER DIMENSIONS SUBPANEL ######################################################################################


# visual alarm ######################################################################################
class kh_MYBIGBUTTONTAB_PT_VisualAlarm(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Render"
    bl_label       = "ALARME - ESC to Abort"
    bl_options     = {'HIDE_HEADER'}
    bl_idname      = "MYBIGBUTTONTAB_PT_VisualAlarm"


    @classmethod
    def poll(cls, context):
        return bpy.context.scene.RBTab_Settings.alarmInProgress == True

    def draw(self, context):

        scene = context.scene
        rd    = scene.render
        rs    = scene.RBTab_Settings

        visualAlarm(self, context)


# visual alarm ######################################################################################
class kh_IMAGE_PT_VisualAlarm(Panel):
    bl_space_type  = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category    = "Tool"
    bl_label       = "ALARME - ESC to Abort"
    bl_options     = {'HIDE_HEADER'}
    bl_idname      = "IMAGE_PT_VisualAlarm"


    @classmethod
    def poll(cls, context):
        return bpy.context.scene.RBTab_Settings.alarmInProgress == True

    def draw(self, context):
        scene = context.scene
        rd    = scene.render
        rs    = scene.RBTab_Settings

        visualAlarm(self, context)



 # visual alarm ######################################################################################
class kh_PROPERTIES_PT_VisualAlarm(Panel):
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    #bl_category = "Alarm"
    bl_label       = "ALARME - ESC to Abort"
    bl_options     = {'HIDE_HEADER'}
    bl_idname      = "PROPERTIES_PT_VisualAlarm"


    @classmethod
    def poll(cls, context):
        return bpy.context.scene.RBTab_Settings.alarmInProgress == True

    def draw(self, context):
        scene = context.scene
        rd    = scene.render
        rs    = scene.RBTab_Settings

        visualAlarm(self, context)

#LOK

class kh_RotateX90Operator(bpy.types.Operator):
    bl_idname = "object.rotate_x_90_operator"
    bl_label = "Rotate X 90"

    def execute(self, context):
        bpy.context.scene.camera.rotation_euler[0] = 1.5708 # 90 degrees in radians
        return {'FINISHED'}

class kh_LockRotationOperator(bpy.types.Operator):
    bl_idname = "object.lock_rotation_operator"
    bl_label = "Lock X Rotation"

    def execute(self, context):
        active_camera = context.scene.camera
        active_camera.lock_rotation[0] = not active_camera.lock_rotation[0]
        return {'FINISHED'}
    
## link cam addon//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#file path save render////////////////////////////////////////////////////////////////////////////////

active_camera_name = None
@persistent
def render_init(scene):
    global active_camera_name
    active_camera_name = scene.camera.name
    print(f"Render init: Active camera is set to {active_camera_name}")


@persistent
def render_complete(scene):
    global active_camera_name
    time.sleep(1)
    if active_camera_name == scene.camera.name:
        play_audio(scene)

def play_audio(scene): 
    if scene.audio_playback_enabled:
        file_path = bpy.path.abspath(scene.audio_file)
        if os.path.isfile(file_path):
            os.startfile(file_path)
        else:
            file_name = "KH-SMS.mp3"
            script_directory = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
            folder_path = os.path.join(script_directory, "KHMUSIC")
            file_path = os.path.join(folder_path, file_name)

            if os.path.isfile(file_path):
                os.startfile(file_path)
            else:
                print("File not found at:", file_path)
                
#SLEEP////////////////////////////////////////////////////////////////////////////////

    if scene.computer_to_sleep:
        if not scene.audio_playback_enabled:
            file_path = bpy.path.abspath(scene.audio_file)
            if os.path.isfile(file_path):
                os.startfile(file_path)
            else:
                file_name = "KH-SMS.mp3"
                script_directory = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
                folder_path = os.path.join(script_directory, "KHMUSIC")
                file_path = os.path.join(folder_path, file_name)

                if os.path.isfile(file_path):
                    os.startfile(file_path)
                else:
                    print("File not found at:", file_path)
                
        time.sleep(30)
        if scene.computer_to_sleep:
            system_platform = platform.system()
            if system_platform == 'Windows':
                # Windows-specific command to put the computer to sleep
                subprocess.run('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
            elif system_platform == 'Darwin':
                # MacOS-specific command to put the computer to sleep
                subprocess.run(['pmset', 'sleepnow'])
            elif system_platform == 'Linux':
                # Linux-specific command to put the computer to sleep
                subprocess.run(['systemctl', 'suspend'])
            
            else:
                print(f"Unsupported platform: {system_platform}")
     
    
    target_collection_name = "3D Model"
    target_collection = bpy.data.collections.get(target_collection_name)
    if target_collection and target_collection.hide_viewport == True:
        target_collection.hide_viewport = False


#file path save render////////////////////////////////////////////////////////////////////////////////
    
class kh_filepathOperator(bpy.types.Operator):
    bl_idname = "object.filepath"
    bl_label = "file path save render"
    def execute(self, context):
        current_file_path = bpy.data.filepath
        if current_file_path:
            current_folder = os.path.dirname(current_file_path)

            render_folder = os.path.join(current_folder, "Render/")
            if not os.path.exists(render_folder):
                os.makedirs(render_folder)
            bpy.context.scene.render.filepath = render_folder
        else:
            self.report({'WARNING'},"Save the file first")
        return {'FINISHED'}


def load_world(scene):
    if scene.depsgraph_update_pre:
        active_camera_name = bpy.context.scene.camera.name
        if active_camera_name != getattr(load_world_handler, "prev_active_camera_name", None):
            camera = bpy.context.scene.camera
            if camera:
                world = bpy.data.worlds.get(camera.name)
                if world:
                    scene.world = world
                    pass
                else:
                    current_world = scene.world
                    if current_world:
                        world = current_world.copy()
                        world.name = camera.name
                        scene.world = world
                        world.use_nodes = True
                        world.use_fake_user = True 
                        pass                    
                    else:
                        new_world = bpy.data.worlds.new(camera.name)
                        scene.world = new_world
                        new_world.use_nodes = True
                        new_world.use_fake_user = True
                        background_output = new_world.node_tree.nodes.get("Background")
                        sky_texture = new_world.node_tree.nodes.new(type='ShaderNodeTexSky')
                        new_world.node_tree.links.new(sky_texture.outputs["Color"], background_output.inputs["Color"])

                all_objects = bpy.context.scene.objects
                camera_name_inside_brackets = f"({camera.name})"
                camera_name_inside_brackets4= camera_name_inside_brackets.replace("Cam-","").replace("-","").replace("00","")#.replace("N","")
                
                for objects in all_objects:
                    #if pattern in collection.name:
                    if re.search(r'\(\d+\)', objects.name):
                        objects.hide_viewport = False
                        objects.hide_render = False
                    
                    #if pattern in collection.name:
                    elif re.search(r'\(\d+N\)', objects.name):
                        objects.hide_viewport = False
                        objects.hide_render = False

                for objects in all_objects:
                    if camera_name_inside_brackets4 in objects.name:
                        objects.hide_viewport = True
                        objects.hide_render = True 
                
                if active_camera_name.endswith('N'): 
                    if 'Dome Light' in bpy.data.objects:
                        dome_light = bpy.data.objects['Dome Light']
                        dome_light.hide_viewport = True
                        dome_light.hide_render = True
                    if 'Dome Light-N' in bpy.data.objects:
                        cube_light_night = bpy.data.objects['Dome Light-N']
                        cube_light_night.hide_viewport = False
                        cube_light_night.hide_render = False                          
                else:
                    if 'Dome Light' in bpy.data.objects:
                        dome_light = bpy.data.objects['Dome Light']
                        dome_light.hide_viewport = False
                        dome_light.hide_render = False
                    if 'Dome Light-N' in bpy.data.objects:
                        cube_light_night = bpy.data.objects['Dome Light-N']
                        cube_light_night.hide_viewport = True
                        cube_light_night.hide_render = True                                                         
           
            load_world_handler.prev_active_camera_name = active_camera_name  
 
@persistent
def load_world_handler(dummy):
        load_world(bpy.context.scene,)


#lode light ##################################################################################

def load_light(scene):
    if scene.depsgraph_load_post:
        active_camera_name = bpy.context.scene.camera.name
        if active_camera_name != getattr(load_light_handler, "prev_active_camera_name", None):
            camera = bpy.context.scene.camera
            if camera:
                if not scene.depsgraph_update_pre: 
                    camera_name_inside_brackets = f"({camera.name})"
                    camera_name_inside_brackets4= camera_name_inside_brackets.replace("Cam-","").replace("-","").replace("00","")#.replace("N","")
                    all_objects = bpy.context.scene.objects
                    for objects in all_objects:
                        
                        if re.search(r'\(\d+\)', objects.name):
                            objects.hide_viewport = False
                            objects.hide_render = False
                        
                        elif re.search(r'\(\d+N\)', objects.name):
                            objects.hide_viewport = False
                            objects.hide_render = False

                    for objects in all_objects:
                        if camera_name_inside_brackets4 in objects.name:
                            objects.hide_viewport = True
                            objects.hide_render = True 

                if active_camera_name.endswith('N'):
                    target_collection_name1 = "KH-SUN"
                    target_collection1 = bpy.data.collections.get(target_collection_name1)
                    if target_collection1:
                        target_collection1.hide_render = True
                        target_collection1.hide_viewport = True
                        
                    # target_collection_name = "Light"
                    # target_collection = bpy.data.collections.get(target_collection_name)
                    
                    # if target_collection:
                    #     # # قم بإخفاء الكولكشن الفرعي إذا وجد
                    #     # for sub_collection in target_collection.children:
                    #     #     sub_collection.hide_render = False
                    #     #     sub_collection.hide_viewport = False
                    #     target_collection.hide_render = False
                    #     target_collection.hide_viewport = False
                    # else:
                    #     target_collection = bpy.data.collections.new("Light")
                    #     bpy.context.scene.collection.children.link(target_collection)
                    
                    target_collection_name = "Light".lower()
                    target_collection = None

                    # البحث عن الكولكشن بغض النظر عن حالة الأحرف
                    for collection in bpy.data.collections:
                        if collection.name.lower() == target_collection_name:
                            target_collection = collection
                            break

                    if target_collection:
                        # إظهار الكولكشن
                        target_collection.hide_render = False
                        target_collection.hide_viewport = False
                    # else:
                    #     # إنشاء الكولكشن إذا لم يكن موجودًا
                    #     target_collection = bpy.data.collections.new("Light")
                    #     bpy.context.scene.collection.children.link(target_collection)

                    # materials = bpy.data.materials
                    # for material in materials:
                    #     if material.name.startswith("LED:"):
                    #         principled_bsdf = None
                    #         for node in material.node_tree.nodes:
                    #             if node.type == 'BSDF_PRINCIPLED':
                    #                 principled_bsdf = node
                    #                 break
                    #         if principled_bsdf:
                    #             if 'Emission Color' in node.inputs:
                    #                 principled_bsdf.inputs["Emission Color"].default_value = (
                    #                 material.diffuse_color[0],
                    #                 material.diffuse_color[1],
                    #                 material.diffuse_color[2],
                    #                 1.0  # قيمة الألفا
                    #             )
                    #             elif 'Emission' in node.inputs:
                    #                 principled_bsdf.inputs["Emission"].default_value = (
                    #                 material.diffuse_color[0],
                    #                 material.diffuse_color[1],
                    #                 material.diffuse_color[2],
                    #                 1.0  # قيمة الألفا
                    #             )
                    #         emission = None
                    #         for node in material.node_tree.nodes:
                    #             if node.type == 'EMISSION':
                    #                 emission = node
                    #                 break
                    #         if emission:
                    #             emission.inputs["Color"].default_value = (
                    #                 material.diffuse_color[0],
                    #                 material.diffuse_color[1],
                    #                 material.diffuse_color[2],
                    #                 1.0  # قيمة الألفا
                    #             )
                    
                    materials = bpy.data.materials
                    for material in materials:
                        if material.name.startswith("LED:") and material.use_nodes:
                            diffuse = material.diffuse_color

                            for node in material.node_tree.nodes:
                                # 1. عقدة BSDF Principled
                                if node.type == 'BSDF_PRINCIPLED':
                                    if "Emission Color" in node.inputs:
                                        node.inputs["Emission Color"].default_value = (*diffuse[:3], 1.0)
                                    elif "Emission" in node.inputs:
                                        node.inputs["Emission"].default_value = (*diffuse[:3], 1.0)

                                # 2. عقدة Emission مباشرة
                                elif node.type == 'EMISSION':
                                    if "Color" in node.inputs:
                                        node.inputs["Color"].default_value = (*diffuse[:3], 1.0)

                                # 3. عقدة NodeGroup
                                elif node.type == 'GROUP':
                                    group_node = node
                                    if "Emission Color" in group_node.inputs:
                                        group_node.inputs["Emission Color"].default_value = (*diffuse[:3], 1.0)

                else:
                    target_collection_name1 = "KH-SUN"
                    target_collection1 = bpy.data.collections.get(target_collection_name1)
                    if target_collection1:
                        target_collection1.hide_render = False
                        target_collection1.hide_viewport = False
                        
                    # target_collection_name = "Light"
                    # target_collection = bpy.data.collections.get(target_collection_name)
                    
                    target_collection_name = "Light".lower()
                    target_collection = None

                    # البحث عن الكولكشن بغض النظر عن حالة الأحرف
                    for collection in bpy.data.collections:
                        if collection.name.lower() == target_collection_name:
                            target_collection = collection
                            break
                        
                    if target_collection:
                        target_collection.hide_render = True
                        target_collection.hide_viewport = True
                    # else:
                    #     target_collection = bpy.data.collections.new("Light")
                    #     bpy.context.scene.collection.children.link(target_collection)

                    # materials = bpy.data.materials
                    # for material in materials:
                    #     if material.name.startswith("LED:"):
                    #         bsdf_node = material.node_tree.nodes.get("Principled BSDF")
                    #         if bsdf_node and bsdf_node.inputs.get("Emission Color"):
                    #             emission_color = bsdf_node.inputs["Emission Color"].default_value = (0,0,0,1)                            
                            
                    #         elif bsdf_node and bsdf_node.inputs.get("Emission"):
                    #             emission_color = bsdf_node.inputs["Emission"].default_value = (0,0,0,1) 
                            
                    #         em_node = material.node_tree.nodes.get("Emission")
                    #         if em_node and em_node.inputs.get("Color"):
                    #             emission_color = em_node.inputs["Color"].default_value = (0,0,0,1)                            
                    
                    materials = bpy.data.materials

                    for material in materials:
                        if material.name.startswith("LED:") and material.use_nodes:
                            node_tree = material.node_tree

                            # محاولة الوصول لعقدة Principled BSDF
                            bsdf_node = node_tree.nodes.get("Principled BSDF")
                            if bsdf_node:
                                if bsdf_node.inputs.get("Emission Color"):
                                    bsdf_node.inputs["Emission Color"].default_value = (0, 0, 0, 1)
                                elif bsdf_node.inputs.get("Emission"):
                                    bsdf_node.inputs["Emission"].default_value = (0, 0, 0, 1)

                            # محاولة الوصول لعقدة Emission
                            em_node = node_tree.nodes.get("Emission")
                            if em_node and em_node.inputs.get("Color"):
                                em_node.inputs["Color"].default_value = (0, 0, 0, 1)

                            # محاولة التعديل على نود قروب إذا فيه مدخل باسم Emission Color
                            for node in node_tree.nodes:
                                if node.type == 'GROUP':
                                    if "Emission Color" in node.inputs:
                                        node.inputs["Emission Color"].default_value = (0, 0, 0, 1)


            load_light_handler.prev_active_camera_name = active_camera_name 

    return {'FINISHED'}

@persistent
def load_light_handler(dummy):
    scene = bpy.context.scene
    #if scene.depsgraph_load_post:
    load_light(bpy.context.scene)


#Cannel
def render_channels(scene):
    if scene.render_channels_enabled:
        tree = create_compositor_tree(scene)
        nodes = tree.nodes
        
        # Cleanup
        to_remove = []
        for node in nodes:
            if node.label in ["Channels Output", "Channels Denoise"]:
                to_remove.append(node)
        
        for node in to_remove:
            nodes.remove(node)

        vl = scene.view_layers.get("ViewLayer")
        if vl:
            vl.use_pass_mist = True
            if hasattr(vl.cycles, 'denoising_store_passes'):
                vl.cycles.denoising_store_passes = True
            vl.use_pass_diffuse_color = True
            vl.use_pass_glossy_direct = True
            vl.use_pass_glossy_indirect = True
            vl.use_pass_glossy_color = True
            vl.use_pass_transmission_indirect = True
            vl.use_pass_environment = True        
            vl.use_pass_ambient_occlusion = True

        output_node = nodes.new(type="CompositorNodeOutputFile")
        output_node.label ="Channels Output"
        output_node.location = (100, 500)
        
        cam_name = scene.camera.name if scene.camera else "Camera"
        base_render_path = os.path.join(bpy.path.abspath("//"), "Render", cam_name)
        
        if bpy.app.version >= (5, 0, 0):
             output_node.directory = base_render_path
        else:
             output_node.base_path = base_render_path
        
        # Create slots with compatibility
        new_output_node_slot(output_node, cam_name + " Mist")
        new_output_node_slot(output_node, cam_name + " Diffuse")
        new_output_node_slot(output_node, cam_name + " Glossy")
        new_output_node_slot(output_node, cam_name + " Reflection")
        new_output_node_slot(output_node, cam_name + " Glossy Color")
        new_output_node_slot(output_node, cam_name + " Transmission")
        new_output_node_slot(output_node, cam_name + " Environment")
        new_output_node_slot(output_node, cam_name + " Ambient_Occlusion")

        if not os.path.exists(base_render_path):
            os.makedirs(base_render_path)

        denoise_nodes = []
        for i in range(9):
            denoise_node = nodes.new(type="CompositorNodeDenoise")
            denoise_node.label = "Channels Denoise"
            denoise_node.location = (-100, 500)
            denoise_nodes.append(denoise_node)
            # Use compatibility if needed, but prefilter usually exists
            if hasattr(denoise_node, 'prefilter'):
                denoise_node.prefilter = 'FAST'

        render_layer_node = None
        for n in nodes:
            if n.type == 'R_LAYERS':
                render_layer_node = n
                break
        
        if not render_layer_node:
            render_layer_node = nodes.new('CompositorNodeRLayers')

        if render_layer_node:
            # Connect logic (simplified and updated for 5.0)
            links = tree.links
            out_socks = render_layer_node.outputs
            
            mapping = {
                7: ("Mist", 1),
                6: ("DiffCol", 2),
                5: ("GlossDir", 3),
                4: ("GlossInd", 4),
                3: ("GlossCol", 5),
                2: ("TransInd", 6),
                1: ("Env", 7),
                0: ("AO", 8)
            }
            
            # Connect Normal/Albedo to all for base denoising or specific ones?
            # Original code was a bit messy, let's keep it functional
            for i, denoise_node in enumerate(denoise_nodes):
                if "Denoising Normal" in out_socks:
                    links.new(out_socks["Denoising Normal"], denoise_node.inputs[1])
                if "Denoising Albedo" in out_socks:
                    links.new(out_socks["Denoising Albedo"], denoise_node.inputs[2])
                
                if i in mapping:
                    sock_name, file_idx = mapping[i]
                    if sock_name in out_socks:
                        links.new(out_socks[sock_name], denoise_node.inputs[0])
                        links.new(denoise_node.outputs[0], output_node.inputs[file_idx])
    else:
        tree = get_compositor_tree(scene)
        if tree:
            nodes = tree.nodes
            to_remove = [n for n in nodes if n.label in ["Channels Output", "Channels Denoise"]]
            for n in to_remove:
                nodes.remove(n)
                    
                
@bpy.app.handlers.persistent
def render_channels_handler(dummy):
    render_channels(bpy.context.scene)

# Delete World
class kh_DeleteWorld(bpy.types.Operator):
    bl_idname = "object.delete_world_and_disable_fake_user"
    bl_label = "Delete World"
    bl_description = "Delete the world linked to the active camera."
    
    def execute(self, context):
        active_camera = context.scene.camera
        active_world = context.scene.world
        if active_world is None:
            return {'CANCELLED'}

        if active_world.name == active_camera.name:
            active_world.name = "DELET"
            bpy.data.worlds.remove(active_world, do_unlink=True)

        return {'FINISHED'}

def delete_world_if_name_matches_active_camera():
    scene = bpy.context.scene
    active_camera = scene.camera
    if active_camera is None:
        return
    
    world = bpy.data.worlds.get(active_camera.name)
    if world:
        scene.world = world
    else:
        current_world = scene.world
        if current_world:
            world = current_world.copy()
            world.name = active_camera.name
            scene.world = world
            world.use_nodes = True
            world.use_fake_user = True 
        else:
            new_world = bpy.data.worlds.new(active_camera.name)
            scene.world = new_world
            new_world.use_nodes = True
            new_world.use_fake_user = True
            # Shader node trees are still accessing through .node_tree, 
            # this change only affects compositor/geometry nodes scene levels.
            background_output = new_world.node_tree.nodes.get("World Output")
            if not background_output:
                background_output = new_world.node_tree.nodes.new(type='ShaderNodeOutputWorld')
            
            bg_node = new_world.node_tree.nodes.get("Background")
            if not bg_node:
                bg_node = new_world.node_tree.nodes.new(type='ShaderNodeBackground')
            
            sky_texture = new_world.node_tree.nodes.new(type='ShaderNodeTexSky')
            new_world.node_tree.links.new(sky_texture.outputs["Color"], bg_node.inputs["Color"])
            new_world.node_tree.links.new(bg_node.outputs["Background"], background_output.inputs["Surface"])


# Copy World
class kh_copyWorld(bpy.types.Operator):
    bl_idname = "object.kh_copyworld"
    bl_label = "copy World"
    bl_description = "Copy World to the active camera."
    
    def execute(self, context):
        active_camera = context.scene.camera
        active_world = context.scene.world
        if active_world is None:
            return {'CANCELLED'}
        
        
        camera_name = active_camera.name
        for world in bpy.data.worlds:
            if world.name == camera_name:
                bpy.data.worlds.remove(world)
                break
    
        #if active_world.name != active_camera.name:
        delete_world_if_name_matches_active_camera()    
        return {'FINISHED'}

# Hide Selected show/////////////////////////////////////////////////////////////////////////////////////////////////////////
class kh_Hideselected_objects(bpy.types.Operator):
    bl_idname = "object.selected_objects"
    bl_label = "Hide Selected"
    def execute(self, context):
    
        selected_objects = context.selected_objects
        active_camera = context.scene.camera
        
        for obj in selected_objects:
            if obj is not None and not obj.type == 'CAMERA':
                obj.hide_viewport = True
                obj.hide_render = True
                
                if active_camera is not None:
                    camera_name = active_camera.name
                    active_camera_name1 = camera_name.replace("Cam-", "").replace("00", "").replace("-", "")#.replace("N", "")
                    object_name = obj.name
                    if f"({active_camera_name1})" not in object_name:
                        #obj.name = f"{object_name} ({camera_name})"
                        obj.name = f"{object_name}({active_camera_name1})"
        return {'FINISHED'}

class kh_show_selected_objects(bpy.types.Operator):
    bl_idname = "object.show_selected_objects"
    bl_label = "Show Selected"
    def execute(self, context):
        bpy.ops.myaddon.add_to_selection()
        bpy.ops.object.show_object()
        return {'FINISHED'}
    
class kh_AddToSelectionOperator(bpy.types.Operator):
    bl_idname = "myaddon.add_to_selection"
    bl_label = "Add Selected to Selection"
    def execute(self, context):

        if context.object:
            if not context.object.type == 'CAMERA':
                selected_object= context.scene.selected_object
                context.scene.selected_object = context.object
        return {'FINISHED'} 
    
# render_collection.show_all/////////////////////////////////////////////////////////////////////////////////////////////////////////

class kh_OBJECT_OT_ShowAll(bpy.types.Operator):
    bl_idname = "render_collection.show_all"
    bl_label = "Show All"

    def execute(self, context):
        collection = bpy.data.collections.get(context.scene.collection_to_render)
        if collection is not None:
            objects_to_render = get_objects_to_render(collection)
            for obj in objects_to_render:
                if not obj.type == 'CAMERA':
                    active_camera = bpy.context.scene.camera
                    active_camera_name1 = active_camera.name.replace("Cam-", "").replace("00", "").replace("-", "")#.replace("N", "")         
                    obj.name = obj.name.replace(f"({active_camera_name1})","")
                    obj.hide_viewport = False
                    obj.hide_render = False
            
        return {'FINISHED'}

class kh_OBJECT_OT_HideAll(bpy.types.Operator):
    bl_idname = "render_collection.hide_all"
    bl_label = "Hide All"

    def execute(self, context):
        collection = bpy.data.collections.get(context.scene.collection_to_render)
        if collection is not None:
            objects_to_render = get_objects_to_render(collection)
            for obj in objects_to_render:
                if not obj.type == 'CAMERA':
                    active_camera = bpy.context.scene.camera
                    active_camera_name1 = active_camera.name.replace("Cam-", "").replace("00", "").replace("-", "")#.replace("N", "")
                    if f"({active_camera_name1})" not in obj.name:
                        obj.name += f"({active_camera_name1})"
                    obj.hide_viewport = True
                    obj.hide_render = True

        return {'FINISHED'}

# hide object show /////////////////////////////////////////////////////////////////////////////////////////////////////////
class kh_HideObjectOperator(bpy.types.Operator):
    bl_idname = "object.hide_object"
    bl_label = "Hide Object"

    def execute(self, context):
        obj = context.scene.selected_object
        if obj is not None and not obj.type == 'CAMERA':
            obj.hide_viewport = True
            obj.hide_render = True
            
            active_camera = bpy.context.scene.camera
            selected_object = context.scene.selected_object
            if active_camera is not None and selected_object is not None:
                camera_name = active_camera.name
                active_camera_name1 = camera_name.replace("Cam-", "").replace("00", "").replace("-", "")#.replace("N", "")
                object_name = selected_object.name
                if f"({active_camera_name1})" not in object_name:
                    selected_object.name = f"{object_name}({active_camera_name1})"
                
        return {'FINISHED'}
    
class kh_ShowObjectOperator(bpy.types.Operator):
    bl_idname = "object.show_object"
    bl_label = "Show Object"

    def execute(self, context):
        obj = context.scene.selected_object
        if obj is not None and not obj.type == 'CAMERA':
            obj.hide_viewport = False
            obj.hide_render = False

            selected_object = context.scene.selected_object
            if selected_object is not None:
                active_camera_name = bpy.context.scene.camera.name if bpy.context.scene.camera else ""
                active_camera_name1 = active_camera_name.replace("Cam-", "").replace("00", "").replace("-", "")#.replace("N", "")
                object_data_name = selected_object.name
                modified_data_name = object_data_name.replace(f"({active_camera_name1})","")
                selected_object.name = modified_data_name
                      
        return {'FINISHED'}
    
#Culling  /////////////////////////////////////////////////////////////////////////////////////////////////////////  

class kh_camera_culling(bpy.types.Operator):
    bl_idname = "object.camera_culling"
    bl_label = "Camera Culling"
    def execute(self, context):
        bpy.ops.object.select_all(action='INVERT')
        selected_objects = context.selected_objects
        active_camera = context.scene.camera
        
        for obj in selected_objects:
            if obj is not None and not obj.type == 'CAMERA' and not obj.type == 'LIGHT':
                obj.hide_viewport = True
                obj.hide_render = True
                
                if active_camera is not None:
                    camera_name = active_camera.name
                    active_camera_name1 = camera_name.replace("Cam-", "").replace("00", "").replace("-", "")#.replace("N", "")
                    object_name = obj.name
                    if f"({active_camera_name1})" not in object_name:
                        obj.name = f"{object_name}({active_camera_name1})"

        bpy.ops.object.select_all(action='DESELECT')
        
        return {'FINISHED'}
      
# Cancel Culling
class kh_CancelCulling(bpy.types.Operator):
    bl_idname = "object.cancel_culling"
    bl_label = "Cancel Culling"

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if obj.type != 'CAMERA' and obj.type != 'LIGHT':
                active_camera = bpy.context.scene.camera
                if active_camera:
                    all_obj = bpy.context.scene.objects
                    camera_name_inside_brackets = f"({active_camera.name})"                    
                    camera_name_inside_brackets1 = camera_name_inside_brackets.replace("Cam-", "").replace("00", "").replace("-", "")#.replace("N", "")
                    for obj in all_obj:
                        if camera_name_inside_brackets1 in obj.name:
                            obj.hide_viewport = False
                            obj.hide_render = False
                            bpy.context.view_layer.objects.active = obj
                            obj.select_set(True)                            
                            active_camera_name = bpy.context.scene.camera.name if bpy.context.scene.camera else ""
                            active_camera_name1 = active_camera_name.replace("Cam-", "").replace("00", "").replace("-", "")#.replace("N", "")
                            object_data_name = obj.name
                            modified_data_name = object_data_name.replace(f"({active_camera_name1})","")
                            obj.name = modified_data_name
        return {'FINISHED'}


def get_objects_to_render(collection):
    objects = []
    for obj in collection.objects:
        objects.append(obj)
    for sub_collection in collection.children:
        sub_objects = get_objects_to_render(sub_collection)
        objects += sub_objects
    return objects


 
    
### Panel ////////////////////////////////////////////////////////////////////////////////////////////////////

preview_collection2 = bpy.utils.previews.new()
preview_collection2.load("13.png", os.path.join(my_icons_dir, "13.png"), 'IMAGE')
#Link Cam To World
class kh_link_cam_Panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_hide_show_keyframe"
    bl_label = "LINK SETTINGS"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "KH-Tools"
    bl_options = {'DEFAULT_CLOSED'}
    #bl_parent_id   = "CAMMANAGER_PT_Cammanager"
    
    @classmethod
    def poll(cls, context):
        return context.scene.depsgraph_update_pre ==True or context.scene.depsgraph_load_post==True

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon_value=preview_collection2['13.png'].icon_id)
        except KeyError:
            pass
 
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        box = layout.box()
        row = box.row()
        row.operator("object.selected_objects", text="Hide Selected",icon="RESTRICT_SELECT_OFF")
        row.operator("object.show_selected_objects", text="",icon="RESTRICT_VIEW_OFF")
        box = layout.box()
        row = box.row()
        #row.prop_search(context.scene, "selected_collection", bpy.data, "collections", text="Select Collection")
        row.prop_search(scene, "collection_to_render", bpy.data, "collections", text="")
        row = box.row()
        row.operator("render_collection.show_all", text="Show", icon="RESTRICT_VIEW_OFF")
        row.operator("render_collection.hide_all", text="Hide", icon="RESTRICT_VIEW_ON")
        box = layout.box()
        row = box.row() 
        row.operator("myaddon.add_to_selection", text="",icon="RESTRICT_SELECT_OFF")               
        row.prop_search(context.scene, "selected_object", bpy.data, "objects", text="")
        row = box.row()
        row.operator("object.show_object", text="Show",icon="HIDE_OFF")
        row.operator("object.hide_object", text="Hide",icon="HIDE_ON")
        box = layout.box()
        row = box.row()
        row.operator("object.camera_culling", text="Camera Culling",icon="OUTLINER_OB_CAMERA")
        row = box.row()
        row.operator("object.cancel_culling", text="Cancel Culling",icon="TRASH")
         

# Hidden Elements//////////////////////////////////////////////////////////////////////////////////////////
preview_collection1= bpy.utils.previews.new()
preview_collection1.load("1.png", os.path.join(my_icons_dir, "1.png"), 'IMAGE')

class kh_HiddenElementsPanel(bpy.types.Panel):
    bl_label = "Hidden List"
    bl_idname = "OUTLINER_PT_show_hidden_elements"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "KH-Tools"
    bl_options = {'DEFAULT_CLOSED'}
    #bl_parent_id   = "CAMMANAGER_PT_Cammanager"

    @classmethod
    def poll(cls, context):
        # استخدام الدالة المساعدة للبحث عن إعدادات الإضافة
        return get_addon_preferences(context, 'HIDDEN_LIST') == True

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon_value=preview_collection1['1.png'].icon_id)
        except KeyError:
            pass
  
    def draw(self, context):
        layout = self.layout

        if not any(collection.hide_viewport or collection.hide_render for collection in bpy.data.collections) and \
        not any(obj.hide_viewport or obj.hide_render or obj.hide_get() for obj in context.scene.objects):
            box = layout.box()
            row = box.row()
            row.label(text="No collections or objects hidden", icon='ERROR')
        
        for collection in bpy.data.collections:
            if collection.hide_viewport or collection.hide_render:
                row = layout.row()
                row.operator("outliner.select_hidden_element", icon='GROUP').object_name = collection.name
                row.prop(collection, "hide_viewport", text=collection.name)
                row.prop(collection, "hide_render", text="")

        for obj in context.scene.objects:
            if obj.hide_viewport or obj.hide_render or obj.hide_get():
                row = layout.row()
                if obj.type == 'CAMERA':
                    icon = 'CAMERA_DATA'
                elif obj.type == 'LIGHT':
                    icon = 'LIGHT_DATA'
                else:
                    icon = 'OBJECT_DATA'
                    
                if obj.hide_get():
                    icon1 = 'HIDE_ON'
                else:
                    icon1 = 'HIDE_OFF'
                row.operator("outliner.select_hidden_element", icon=icon).object_name = obj.name
                row.operator("object.toggle_hide_show",text="", icon=icon1).object_name = obj.name
                row.prop(obj, "hide_viewport", text=obj.name)
                row.prop(obj, "hide_render", text="")
                
                
class kh_ToggleHideShowOperator(bpy.types.Operator):
    """Toggle Hide/Show Edges"""
    bl_idname = "object.toggle_hide_show"
    bl_label = "Toggle Hide/Show Edges"
    
    object_name: bpy.props.StringProperty(name="Object Name")

    def execute(self, context):
        # Get the active object
        obj = bpy.data.objects.get(self.object_name)

        # Toggle hide/show
        if obj.hide_get():
            obj.hide_set(False)
        else:
            obj.hide_set(True)
        return {'FINISHED'}

    
class kh_ShowHiddenElements(bpy.types.Operator):
    """ Show Hidden Elements in Outliner """
    bl_idname = "outliner.show_hidden_elements"
    bl_label = "Show Hidden Elements"
    
    def execute(self, context):
        for obj in context.scene.objects:
            obj.hide_viewport = False
            obj.hide_render = False
        
        for collection in bpy.data.collections:
            collection.hide_viewport = False
            collection.hide_render = False
        return {'FINISHED'}

class kh_SelectHiddenElement(bpy.types.Operator):
    """ Select Hidden Element in Outliner """
    bl_idname = "outliner.select_hidden_element"
    bl_label = ""
    
    object_name: bpy.props.StringProperty(name="Object Name")
    
    def execute(self, context):
        obj = bpy.data.objects.get(self.object_name)
        if obj:
            obj.select_set(True)
            context.view_layer.objects.active = obj
        return {'FINISHED'}
#----------------------------------------------------



classes = (kh_MYBIGBUTTON_Settings,
            kh_MYBIGBUTTON_obj_Settings,
            kh_SCENECAMERA_OT_Add,
            kh_SCENECAMERA_OT_Copy_location,
            kh_SCENECAMERA_OT_Copy,
            kh_SCENECAMERA_OT_Night,
            kh_SCENECAMERA_OT_ActivPreview,
            kh_SCENECAMERA_OT_AlignView,
            kh_SCENECAMERA_OT_AlignObj,
            kh_SCENECAMERA_OT_AddTrackTo,
            kh_SCENECAMERA_OT_RemoveTrackTo,
            kh_SCENECAMERA_OT_AddMarker,
            kh_SCENECAMERA_OT_removeMarker,
            kh_SCENECAMERA_OT_Remove,
            kh_SCENECAMERA_OT_RenderAnimation,
            kh_SCENECAMERA_OT_BatchRenderAll,
            kh_SCENECAMERA_OT_Render,
            kh_RENDER_OT_Renderformat,
            kh_RENDEREVENTS_OT_endEvents,
            kh_SCENECAMERA_OT_CustomResolution,
            kh_SCENECAMERA_OT_Null,
            kh_RotateX90Operator,
            kh_LockRotationOperator,     
            kh_MYBIGBUTTONTAB_OT_toggle_orientation,
            kh_MYBIGBUTTONTAB_OT_store_defaultres,
            kh_MYBIGBUTTONTAB_PT_VisualAlarm,
            kh_IMAGE_PT_VisualAlarm,
            kh_PROPERTIES_PT_VisualAlarm,
            kh_CAMMANAGER_PT_Cammanager,
            kh_CAMMANAGER_PT_QuickSettings,
            #kh_RENDER_PT_presets,
            
            kh_filepathOperator,

            ## link cam addon////////////////////////////////////////////////////////////////////////
            kh_link_cam_Panel,
            kh_OBJECT_OT_ShowAll,
            kh_OBJECT_OT_HideAll,
            kh_camera_culling,
            kh_CancelCulling,
            kh_DeleteWorld,
            kh_copyWorld,
           
            kh_ToggleHideShowOperator,
            #Hide Objec
            kh_HideObjectOperator,
            kh_ShowObjectOperator,
            kh_Hideselected_objects,
            kh_show_selected_objects,
            kh_AddToSelectionOperator,
            kh_ShowHiddenElements,
            kh_SelectHiddenElement,
            kh_HiddenElementsPanel,
            
                )

addon_keymaps = []


def register():
    for i in classes:
        register_class(i)
        
     #Camwra addon////////////////////////////////////////////////////////////////////////////////////////////////////////
    Scene.RBTab_Settings = PointerProperty(type=kh_MYBIGBUTTON_Settings)
    Object.RBTab_obj_Settings = PointerProperty(type=kh_MYBIGBUTTON_obj_Settings)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        km = kc.keymaps.new(name="Object Mode")
        kmi = km.keymap_items.new(kh_SCENECAMERA_OT_Add.bl_idname, "C", "PRESS", alt=True)
        addon_keymaps.append((km, kmi))


    # link cam addon////////////////////////////////////////////////////////////////////////////////////////////////////////
    bpy.types.Scene.collection_to_render = bpy.props.StringProperty()
     
    bpy.types.Scene.audio_file = bpy.props.StringProperty(
        name="Audio File",
        description="Audio file to play after rendering",
        subtype='FILE_PATH',
    )
    bpy.types.Scene.audio_playback_enabled = bpy.props.BoolProperty(
        name="Audio Enabled",
        description="Toggle audio playback after rendering",
        default=False,
    )
    
    bpy.types.Scene.depsgraph_update_pre = bpy.props.BoolProperty(
        name="",
        description="Create a custom world for each camera",
        default=False,
    )

    bpy.types.Scene.depsgraph_load_post = bpy.props.BoolProperty(
    name="Connecting Light with night cameras",
    description="Connecting Light collection with night cameras",
    default=False,
    )

    # تعريف خاصية render_channels_enabled لتحديد ما إذا كان يتم تمكين القنوات أم لا
    bpy.types.Scene.render_channels_enabled = bpy.props.BoolProperty(
        name="channels",
        description="Add channels",
        default=False,
    )

    bpy.types.Scene.computer_to_sleep = bpy.props.BoolProperty(
        name="Sleep",
        description="Computer_to_sleep after rendering",
        default=False,
    )

    bpy.app.handlers.depsgraph_update_pre.append(load_light_handler)
    bpy.app.handlers.depsgraph_update_pre.append(load_world_handler)
    #bpy.app.handlers.depsgraph_update_post.append(load_world_change)
       
    bpy.app.handlers.render_pre.append(render_init)
    bpy.app.handlers.render_complete.append(render_complete)

    #bpy.app.handlers.render_init.append(render_init_sleep)
    #bpy.app.handlers.render_complete.append(computer_to_sleep_handler)
  
    #bpy.app.handlers.render_complete.append(play_audio_handler)
    bpy.app.handlers.render_pre.append(render_channels_handler)
    #bpy.app.handlers.render_init.append(Disable_channels_handler)
    
    bpy.types.Scene.selected_object = bpy.props.PointerProperty(type=bpy.types.Object)
    
def unregister():
    for i in classes:
        unregister_class(i)  
        
    # التحقق من وجود الخصائص قبل حذفها لتجنب الأخطاء
    if hasattr(Scene, 'RBTab_Settings'):
        del Scene.RBTab_Settings
    if hasattr(Object, 'RBTab_obj_Settings'):
        del Object.RBTab_obj_Settings
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()

   # link cam addon///////////////////////////////////////////////////////////////////

    if hasattr(bpy.types.Scene, 'collection_to_render'):
        del bpy.types.Scene.collection_to_render

    # إزالة handlers بأمان
    try:
        bpy.app.handlers.depsgraph_update_pre.remove(load_light_handler)
    except ValueError:
        pass  # Handler already removed or not present

    try:
        bpy.app.handlers.depsgraph_update_pre.remove(load_world_handler)
    except ValueError:
        pass  # Handler already removed or not present

    try:
        bpy.app.handlers.render_pre.remove(render_init)
    except ValueError:
        pass  # Handler already removed or not present

    try:
        bpy.app.handlers.render_complete.remove(render_complete)
    except ValueError:
        pass  # Handler already removed or not present

    #bpy.app.handlers.render_init.remove(render_init_sleep)
    #bpy.app.handlers.render_complete.remove(computer_to_sleep_handler)

    #bpy.app.handlers.render_complete.remove(play_audio_handler)
    try:
        bpy.app.handlers.render_pre.remove(render_channels_handler)
    except ValueError:
        pass  # Handler already removed or not present
    #bpy.app.handlers.render_init.remove(Disable_channels_handler)

    if hasattr(bpy.types.Scene, 'audio_file'):
        del bpy.types.Scene.audio_file
    if hasattr(bpy.types.Scene, 'audio_playback_enabled'):
        del bpy.types.Scene.audio_playback_enabled
    if hasattr(bpy.types.Scene, 'render_channels_enabled'):
        del bpy.types.Scene.render_channels_enabled
    

if __name__ == "__main__":
    try:
        register()
    except:
        pass
    unregister() 


