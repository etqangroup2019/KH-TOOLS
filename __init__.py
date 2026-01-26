bl_info = {
    "name": "KH-Tools",
    "author": "Khaled Alnwesary",
    "version": (1, 99),
    "blender": (4, 2, 0),
    "location": "View3D > UI",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "KH",
}


import bpy
import os, platform, subprocess
import shutil
import aud
from bl_ui.utils import PresetPanel
import time, datetime



import bpy.utils.previews
from bpy.types import WindowManager
from bpy.props import (EnumProperty)


from ast import Delete
import math

import tempfile
import time
from types import NoneType
#from turtle import update


import sys
import typing
import inspect
import pkgutil
import importlib
from pathlib import Path


from bpy.utils import register_class, unregister_class
from bpy.props import (BoolProperty, EnumProperty, FloatProperty, IntProperty,PointerProperty,StringProperty)
from bpy.types import (AddonPreferences, Operator,Panel,Scene, PropertyGroup,Object,Menu, Panel, UIList)
from bpy_extras.io_utils import (ExportHelper, ImportHelper, unpack_face_list,unpack_list)
from mathutils import Matrix, Quaternion, Vector

# دالة مساعدة عامة للبحث عن إعدادات الإضافة
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


from .Camera import *
from .Memory import *
from .Light_Manager import *
from .Top_View import *
from .KH_Material import *
from .Asset_Maker import *
from .Asset_Manager import *
from .KH_Light_Mix import *
from .Scatter import *
from .Animation import *
from .sketcup_import import *
from .Random_Asset import *
from .update import *
from .select_linked_pick import *

if bpy.app.version >= (4, 2, 0):
    from . import skp_drag_drop

class SketchupAddonPreferences_k(AddonPreferences):

    bl_idname = __name__

    camera_far_plane: FloatProperty(
        name="Camera Clip Ends At :",
        default=250,
        unit='LENGTH'
    )

    draw_bounds: IntProperty(
        name="Draw Similar Objects As Bounds When It's Over :",
        default=1000
    )

    Camera_Manager: BoolProperty(
        name="Camera Manager",
        default=True,
    )

    Light_Manager: BoolProperty(
        name="Light Manager",
        default=True,
    )

    DOME_LIGHT: BoolProperty(
        name="DOME LIGHT",
        default=True,
    )

    HIDDEN_LIST : BoolProperty(
        name="HIDDEN LIST ",
        default=True,
    )

    Light_Mix : BoolProperty(
        name="Light Mix",
        default=True,
    )

    Memory: BoolProperty(
        name="Render Settings",
        default=True,
    )

    KH_Material: BoolProperty(
        name="Material",
        default=True,
    )

    KH_TopView: BoolProperty(
        name="TopView",
        default=True,
    )
    
    Asset_Maker: BoolProperty(
        name="Asset",
        default=True,
    )
    
    KH_Scatter: BoolProperty(
        name="Scatter",
        default=True,
    )
    
    KH_Sketchup: BoolProperty(
        name="Sketchup",
        default=True,
    )
    
    KH_Tutoril: BoolProperty(
        name="Tutoril",
        default=True,
    )
    
    KH_Animation: BoolProperty(
        name="Animation",
        default=False,
    )
    
    KH_SketchUp_plugin: BoolProperty(
        name="Install SketchUp plugin",
        default=False,
    )


    # def draw(self, context):

    #     layout = self.layout
    #     layout.label(text="ADDONS :")

    #     row = layout.row()
    #     row.prop(self, "Camera_Manager",icon='VIEW_CAMERA')
    #     row.prop(self, "Light_Manager",icon='OUTLINER_OB_LIGHT')
    #     row.prop(self, "DOME_LIGHT",icon='SPHERE')
    #     row.prop(self, "HIDDEN_LIST",icon='RESTRICT_VIEW_OFF')
    #     row = layout.row()
    #     row.prop(self, "Light_Mix",icon='OUTLINER_OB_LIGHT')
    #     row.prop(self, "Memory",icon='MEMORY')
    #     row.prop(self, "KH_Material",icon='MATERIAL')
    #     row.prop(self, "KH_TopView",icon='FILTER')

    #     layout.label(text="- Basic Import Options -")
    #     row = layout.row()
    #     row.use_property_split = True
    #     row.prop(self, "camera_far_plane")
    #     layout = self.layout
    #     row = layout.row()
    #     row.use_property_split = True
    #     row.prop(self, "draw_bounds")
    
    prefs = bpy.context.preferences
    filepaths = prefs.filepaths
    asset_libraries = filepaths.asset_libraries

    addon_pref_preview: bpy.props.BoolProperty(name="Addon Preferences", default=False)
    addon_pref: bpy.props.BoolProperty(name="Addon Preferences", default=False)
    addon_pref_advanced: bpy.props.BoolProperty(name="Addon Preferences", default=False)


    library_pipe: bpy.props.BoolProperty(name="Addon Preferences", default=False)
    render_preferences: bpy.props.BoolProperty(name="Addon Preferences", default=False)
    how_it_works: bpy.props.BoolProperty(name="Addon Preferences", default=False)
    preferences: bpy.props.BoolProperty(name="Addon Preferences", default=False)
    save_location: bpy.props.BoolProperty(name="Addon Preferences", default=True)
    save_path: bpy.props.StringProperty(name="Addon Preferences", default=asset_libraries[bpy.context.preferences.filepaths.active_asset_library].path)

    asset_type: bpy.props.BoolProperty(name="Assets Type", default=True)
    render_all_assets_coll: bpy.props.BoolProperty(
        name="Render all assets collection", 
        default=False,
        description="'All Marked Assets' = All Collections marked as assets in this scene will be rendered | 'Active Coll' = Render preview and Mark Assets the selected collection",
        )

    # CAMERA VIEW
    use_current_orientation: bpy.props.BoolProperty(name="Use Current View Orientation", default=False)
    use_view: bpy.props.BoolProperty(name="Use User View", default=True)
    force_focus_selected: bpy.props.BoolProperty(name="Fit view on object in user View", default=True)

    sun_orientation: bpy.props.FloatProperty(name="render_pref", default=90)
    camera_orientation: bpy.props.FloatProperty(name="render_pref", default=-45)
 
    render_engine: bpy.props.BoolProperty(name="Render Engine", default=False)
    render_exposition: bpy.props.FloatProperty(name="render_pref", default=0, min=-10, max=10)
    render_resolution: bpy.props.IntProperty(name="render_pref", default=256, min=2)

    camera_focal: bpy.props.FloatProperty(name="cam_focal", default=50, min=0.01)
    camera_clip_start: bpy.props.FloatProperty(name="cam_start", default=0.1, min=0.00001, unit='LENGTH')
    camera_clip_end: bpy.props.FloatProperty(name="cam_end", default=100, min=0.00001, unit='LENGTH')


    # CYCLES
    cycles_samples: bpy.props.IntProperty(name="cycle_pref", default=32, min=2)
    cycles_transp_bounces: bpy.props.IntProperty(name="cycle_pref", default=8, min=0)
    cycles_denoise: bpy.props.BoolProperty(name="cycle_pref", default=True)
    cycles_transparent_background: bpy.props.BoolProperty(name="cycle_pref", default=True)

    # EEVEE
    eevee_samples: bpy.props.IntProperty(name="eevee_pref", default=16, min=2)
    eevee_ao: bpy.props.BoolProperty(name="eevee_pref", default=True)
    eevee_ssr: bpy.props.BoolProperty(name="eevee_pref", default=True)
    eevee_refract: bpy.props.BoolProperty(name="eevee_pref", default=False)
    eevee_transparent_background: bpy.props.BoolProperty(name="eevee_pref", default=True)


    # EXPORT
    prefix: bpy.props.StringProperty(name="Asset_Prefix", default="")
    use_export: bpy.props.StringProperty(name="Asset_Prefix", default="")
    export_type: bpy.props.StringProperty(name="Asset_Type", default="object")
    export_all_assets_coll: bpy.props.BoolProperty(name="Asset_Prefix", default=True)
    destination_library: bpy.props.BoolProperty(name="Asset_Prefix", default=False)
    asset_location: bpy.props.BoolProperty(name="Asset_Prefix", default=False)
    asset_category: bpy.props.BoolProperty(name="Asset_Prefix", default=False)
    target_catalog: bpy.props.StringProperty(name="Asset_Prefix", default="")
    cats_expand: bpy.props.StringProperty(name="Asset_Prefix", default="")
    uuid: bpy.props.StringProperty(name="Asset_Prefix", default="")
    remplace_link_coll_file: bpy.props.BoolProperty(name="Replace Coll", default=False)
    export_all_material: bpy.props.BoolProperty(name="All marked Assets", default=False)
    export_all_object: bpy.props.BoolProperty(name="All marked Asset", default=True)


    # SAVE PREVIEW EXTERNAL
    save_preview: bpy.props.BoolProperty(name="Save Preview", default=False)
    preview_filepath: bpy.props.StringProperty(name="",subtype='FILE_PATH', default="")
    save_preview_in_current_file_loc: bpy.props.BoolProperty(name="Save Preview in Current File", default=True)


    # DATA
    data: bpy.props.BoolProperty(name="Asset_data", default=False)
    description: bpy.props.StringProperty(name="Asset_data", default="")
    license: bpy.props.StringProperty(name="Asset_data", default="")
    copyright: bpy.props.StringProperty(name="Asset_data", default="")
    author: bpy.props.StringProperty(name="Asset_data", default="")


    # DEBUG
    debug_mode: bpy.props.BoolProperty(name="Debug", default=False)
    use_temp_files: bpy.props.BoolProperty(name="Use Temp Files", default=False)
    remove_temp: bpy.props.BoolProperty(name="Remove Temp Files", default=False)
    
  
    max_threads: bpy.props.IntProperty(name="Max Threads", default=10, min=1)
    background: bpy.props.BoolProperty(
        name="Run child processes in background mode", default=True)
    factory_default: bpy.props.BoolProperty(
        name="Use factory default startup", description="Run child processes in factory default mode", default=True)
        


    def draw(self, context):
        layout = self.layout
        layout.label(text="SketchUp Plugin :")
        row = layout.row()
        row.operator("wm.sketchup_plugin_setup" , text="Install SketchUp Plugin V1.3", icon="EXPORT")
        
        layout.label(text="ADDONS :")

        row = layout.row()
        row.prop(self, "Camera_Manager",icon='VIEW_CAMERA')
        row.prop(self, "Light_Manager",icon='OUTLINER_OB_LIGHT')
        row.prop(self, "Asset_Maker",icon='ASSET_MANAGER')
        row.prop(self, "KH_Sketchup",icon='IMPORT')
        row = layout.row()
        row.prop(self, "KH_Material",icon='MATERIAL')
        row.prop(self, "Memory",icon='MEMORY')
        row.prop(self, "HIDDEN_LIST",icon='RESTRICT_VIEW_OFF')
        row.prop(self, "KH_Scatter",icon='OUTLINER_OB_CURVES')
        row = layout.row()
        row.prop(self, "KH_Tutoril",icon='FILE_MOVIE')
        row.prop(self, "KH_TopView",icon='FILTER')
        row.prop(self, "Light_Mix",icon='OUTLINER_OB_LIGHT')
        row.prop(self, "DOME_LIGHT",icon='SPHERE')
        row = layout.row()
        row.prop(self, "KH_Animation",icon='RENDER_ANIMATION')
                
        layout.label(text="- Basic Import Options -")
        row = layout.row()
        row.use_property_split = True
        row.prop(self, "camera_far_plane")
        layout = self.layout
        row = layout.row()
        row.use_property_split = True
        row.prop(self, "draw_bounds")
        
        layout = self.layout
        pref = context.preferences.addons['KH-Tools'].preferences        
        
        ###################################################################################
        # ADDON PREFERENCES
        ###################################################################################
        box = layout.box()
        box.prop(self, 'addon_pref_preview', text = "Preview Preferences", emboss = False, icon = "SEQ_PREVIEW")
        if self.addon_pref_preview == True:
            box.label(text="Asset Type :")
            row = box.row(align=True)
            row.prop(pref, 'asset_type', text="Object", icon = "OBJECT_DATA")
            row.prop(pref, 'asset_type', text="Collection", icon = "OUTLINER_COLLECTION", invert_checkbox = True)
            if pref.asset_type==False:
                row = box.row(align=True)
                row.prop(pref, 'render_all_assets_coll', text="Active Coll", toggle=True, invert_checkbox = True)
                row.prop(pref, 'render_all_assets_coll', text="All Marked Assets", toggle=True) 
            


            box.label(text="Camera Lens :")
            box.prop(pref, 'camera_focal', text="Focal Length")
            box.prop(pref, 'camera_clip_start', text="Clip Start")
            box.prop(pref, 'camera_clip_end', text="End")

            box.label(text="Camera Orientation :")
            row = box.row(align=True)
            row.prop(pref, 'use_current_orientation', text="Current", icon = "HIDE_OFF")
            row.prop(pref, 'use_current_orientation', text="Default", icon = "OUTLINER_OB_CAMERA", invert_checkbox = True)

            if pref.use_current_orientation:
                row = box.row(align=True)
                row.prop(pref, 'use_view', text="View", icon = "CAMERA_STEREO")
                row.prop(pref, 'use_view', text="Active Camera", icon = "OUTLINER_OB_CAMERA", invert_checkbox = True) 
                if pref.use_view:
                    box.prop(pref, 'force_focus_selected', text="Fit view to object")
            else:
                box.prop(pref, 'camera_orientation', text="Rotation Offset")

        box = layout.box()
        box.prop(self, 'addon_pref', text = "Render Preferences", emboss = False, icon = "SCENE")
        if self.addon_pref == True:
            col = box.column()
            col.label(text="Render Settings :")
            col.prop(pref, 'render_resolution', text="Resolution")

            row = col.row(align=True)
            row.scale_y=1.4
            row.prop(pref, 'render_engine', text="Cycles", invert_checkbox = True, toggle=True)
            row.prop(pref, 'render_engine', text="EEVEE", toggle=True)

            # CYCLES SETTINGS
            if pref.render_engine == False:
                box = col.box()
                box.label(text="Cycles Settings :")
                row=box.row()
                row.prop(pref, 'cycles_samples', text="Samples")
                row.prop(context.scene, "render_device", text="")
                box.prop(pref, 'cycles_transp_bounces', text="Transparency Bounces")
                box.prop(pref, 'cycles_denoise', text="Denoise")
                box.prop(pref, 'cycles_transparent_background', text="Transparent Background")
                box.prop(pref, 'render_exposition', text="Exposition", slider = True)
                box.prop(pref, 'sun_orientation', text="Default Sun Orientation (° deg)")

            # EEVEE SETTINGS
            else:
                box = col.box()
                box.label(text="EEVEE Settings :")
                box.prop(pref, 'eevee_samples', text="Samples")
                box.prop(pref, 'eevee_ao', text="Ambient Occlusion")
                box.prop(pref, 'eevee_ssr', text="Screen Space Reflection")
                if pref.eevee_ssr:
                    box.prop(pref, 'eevee_refract', text="Refraction")
                box.prop(pref, 'eevee_transparent_background', text="Transparent Background")
                box.prop(pref, 'render_exposition', text="Exposition", slider = True)
                box.prop(pref, 'sun_orientation', text="Default Sun Orientation (° deg)")

        box = layout.box()
        box.prop(self, 'addon_pref_advanced', text = "Advanced", emboss = False, icon = "SETTINGS")
        if self.addon_pref_advanced == True:
            box.prop(pref, 'debug_mode', text="Debug Mode (Open Console)")
            box.prop(pref, 'use_temp_files', text="Save Cache in Temp Files")

        layout = self.layout
        layout.label(text='Asset Tools:')
        layout.prop(self, 'max_threads', expand=True)
        layout.prop(self, 'background', expand=True)
        layout.prop(self, 'factory_default', expand=True)
        layout.label(
            text='--Prevents other addons from loading in child processes.')

classes = ( 
            #kh-tools////////////////////////////////////////////
            SketchupAddonPreferences_k,

                )

def register():
    for i in classes:
        register_class(i)
        
    Camera.register() 
    Light_Manager.register()  
    Asset_Maker.register() 
    KH_Material.register()
    Asset_Manager.register()
    Memory.register() 
    sketcup_import.register() 
    Scatter.register()
    Animation.register()  
    KH_Light_Mix.register()      
    Top_View.register()
    Random_Asset.register()
    select_linked_pick.register()
    if bpy.app.version >= (4, 2, 0):
        skp_drag_drop.register()

def unregister():
    for i in classes:
        unregister_class(i)
        
    Camera.unregister()  
    Light_Manager.unregister() 
    Asset_Maker.unregister() 
    KH_Material.unregister()   
    Asset_Manager.unregister()
    Memory.unregister()
    sketcup_import.unregister()
    Scatter.unregister() 
    Animation.unregister() 
    KH_Light_Mix.unregister() 
    Top_View.unregister()
    Random_Asset.unregister()
    select_linked_pick.unregister()

    if bpy.app.version >= (4, 2, 0):
        skp_drag_drop.unregister()

if __name__ == "__main__":
    try:
        register()
    except:
        pass
    unregister()
    
