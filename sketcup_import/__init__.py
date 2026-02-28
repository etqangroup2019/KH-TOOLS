# <pep8-80 compliant>

__author__ = 'Martijn Berger'
__license__ = "GPL"

'''
This program is free software; you can redistribute it and
or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see http://www.gnu.org/licenses
'''
from collections import OrderedDict
from mathutils import Vector


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

from . import sketchup
from .SKPutil import *
from .progress_window import (
    start_import_progress, 
    start_setup_progress, 
    get_current_progress, 
    close_progress,
    show_confirm,
    show_message,
    show_finished_in_progress,
    show_skipped_components
)

#KH-Asset
import random 
from bpy.types import WindowManager
from bpy.props import (EnumProperty)


bl_info = {
    "name": "KH-Tools",
    "author": "Khaled Alnwesary",
    "version": (1, 5),
    "blender": (4, 0, 0),
    "location": "View3D > UI",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "KH",
}

addon_dir = os.path.dirname(__file__)
my_icons_dir = os.path.join(addon_dir, "icons")

DEBUG = False

LOGS = True

MIN_LOGS = False

if not LOGS:
    MIN_LOGS = True


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
        name="Asset_Maker",
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


def skp_log(*args):

    if len(args) > 0:
        print('SKP | ' + ' '.join(['%s' % a for a in args]))


def create_nested_collection(coll_name):
    context = bpy.context
    main_coll_name = 'SKP File'

    if not bpy.data.collections.get(main_coll_name):
        skp_main_coll = bpy.data.collections.new(main_coll_name)
        context.scene.collection.children.link(skp_main_coll)

    if not bpy.data.collections.get(coll_name):
        skp_nested_coll = bpy.data.collections.new(coll_name)
        bpy.data.collections[main_coll_name].children.link(skp_nested_coll)

    view_layer_coll = context.view_layer.layer_collection
    main_parent_coll = view_layer_coll.children[main_coll_name]
    coll_set_to_active = main_parent_coll.children[coll_name]
    context.view_layer.active_layer_collection = coll_set_to_active


def hide_one_level():

    context = bpy.context

    outliners = [a for a in context.screen.areas if a.type == 'OUTLINER']
    c = context.copy()
    for ol in outliners:
        c["area"] = ol
        bpy.ops.outliner.show_one_level(c, open=False)
        ol.tag_redraw()

    # context.view_layer.update()

#New Importer-----------------------------------------------------------------------------------------------------
class SceneImporter():
    def __init__(self):
        self.filepath = '/tmp/untitled.skp'
        self.name_mapping = {}
        self.skipped_components = []  # قائمة الكومبوننتات المتجاوزة
        self.component_meshes = {}
        self.scene = None
        self.layers_skip = []

    def set_filename(self, filename):

        self.filepath = filename
        self.basepath, self.skp_filename = os.path.split(self.filepath)
        return self  # allow chaining

    def load(self, context, **options):
        """load a sketchup file"""

        self.context = context
        self.reuse_material = options['reuse_material']
        self.reuse_group = options['reuse_existing_groups']
        self.max_instance = options['max_instance']
        self.render_engine = options['render_engine']
        self.component_stats = defaultdict(list)
        self.component_skip = proxy_dict()
        self.component_depth = proxy_dict()
        self.group_written = {}
        ren_res_x = context.scene.render.resolution_x
        ren_res_y = context.scene.render.resolution_y
        self.aspect_ratio = ren_res_x / ren_res_y

        # الحصول على نافذة التقدم
        progress_win = get_current_progress()
        
        # الحصول على نافذة التقدم
        progress_win = get_current_progress()
        
        # لا حاجة لملف components Not imported.txt بعد الآن
        # سيتم عرض الكومبوننتات المتجاوزة في نافذة اللوق مباشرة
        
        # Start stopwatch for overall import
        _time_main = time.time()

        # Log filename being imported
        if LOGS:
            skp_log(f'Importing: {self.filepath}')
        if progress_win:
            progress_win.log_message(f"Importing: {self.filepath}")
            progress_win.update_progress(5, "Reading SketchUp file...")
        addon_name = __name__.split('.')[0]
        self.prefs = context.preferences.addons[addon_name].preferences

        # Open the SketchUp file and access the model using SketchUp API
        try:
            self.skp_model = sketchup.Model.from_file(self.filepath)
            if progress_win:
                progress_win.log_message("SketchUp file loaded successfully")
                progress_win.update_progress(15, "Importing cameras...")
        except Exception as e:
            if LOGS:
                skp_log(f'Error reading input file: {self.filepath}')
                skp_log(e)
            if progress_win:
                progress_win.log_message(f"Error reading file: {e}")
                show_finished_in_progress(f"Error: {e}")
            return {'FINISHED'}
        
        # Start stopwatch for camera import
        if not MIN_LOGS:
            skp_log("")
            skp_log("=== Importing Sketchup scenes and views as Blender "
                    "Cameras ===")
        _time_camera = time.time()



        if options['import_scene']:
            options['scenes_as_camera'] = False
            options['import_camera'] = True
            for s in self.skp_model.scenes:
                if s.name == options['import_scene']:
                    if not MIN_LOGS:
                        skp_log(f"Importing named SketchUp scene '{s.name}'")
                    self.scene = s

                    # Skip s.layers which are the invisible layers
                    self.layers_skip = [l for l in s.layers]
            if not self.layers_skip and not MIN_LOGS:
                skp_log("Scene: '{}' didn't have any invisible layers."
                        .format(options['import_scene']))
            if self.layers_skip != [] and not MIN_LOGS:
                hidden_layers = sorted([l.name for l in self.layers_skip])
                print("SU | Invisible Layer(s)/Tag(s): \n     ", end="")
                print(*hidden_layers, sep=', ')

        # Import each scene as a Blender camera
        if options['scenes_as_camera']:
            if not MIN_LOGS:
                skp_log("Importing all SketchUp scenes as Blender cameras")
            for s in self.skp_model.scenes:
                self.write_camera(s.camera, s.name)

        # Set the active camera and use for 3D view
        if options['import_camera']:
            if not MIN_LOGS:
                skp_log("Importing last SketchUp view as Blender camera")
            if self.scene:
                active_cam = self.write_camera(self.scene.camera,
                                               name=self.scene.name)
                context.scene.camera = bpy.data.objects[active_cam]
            else:
                active_cam = self.write_camera(self.skp_model.camera)
                context.scene.camera = bpy.data.objects[active_cam]
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.spaces[0].region_3d.view_perspective = 'CAMERA'
                    break
        SKP_util.layers_skip = self.layers_skip
        if not MIN_LOGS:
            skp_log("Cameras imported in "
                    f"{(time.time() - _time_camera):.4f} sec.")
        if progress_win:
            progress_win.log_message(f"Cameras imported in {(time.time() - _time_camera):.2f} sec")
            progress_win.update_progress(25, "Importing materials...")

        # Start stopwatch for material imports
        if not MIN_LOGS:
            skp_log("")
            skp_log("=== Importing Sketchup materials into Blender ===")
        _time_material = time.time()
        self.write_materials(self.skp_model.materials)
        if not MIN_LOGS:
            skp_log("Materials imported in "
                    f"{(time.time() - _time_material):.4f} sec.")
        if progress_win:
            progress_win.log_message(f"Materials imported in {(time.time() - _time_material):.2f} sec")
            progress_win.update_progress(40, "Analyzing components...")

        # Start stopwatch for component import
        if not MIN_LOGS:
            skp_log("")
            skp_log("=== Importing Sketchup components into Blender ===")
        _time_analyze_depth = time.time()

        create_nested_collection('new')

         # Determine the number of components that exist in the SketchUp model
        self.skp_components = proxy_dict(
            self.skp_model.component_definition_as_dict)
        u_comps = [k for k, v in self.skp_components.items()]
        if not MIN_LOGS:
            print(f"SU | Contains {len(u_comps)} components: \n     ", end="")
            print(*u_comps, sep=', ')
        if progress_win:
            progress_win.log_message(f"Components count: {len(u_comps)}")

        # Analyse component depths
        D = SKP_util()
        for c in self.skp_model.component_definitions:
            self.component_depth[c.name] = D.component_deps(c.entities)
            if DEBUG:
                print(f"     -- ({c.name}) --\n        "
                      f"Depth: {self.component_depth[c.name]}\n", end="")
                print("        Instances (Used): "
                      f"{c.numInstances} ({c.numUsedInstances})")
        if not MIN_LOGS:
            skp_log(f"Component depths analyzed in "
                    f"{(time.time() - _time_analyze_depth):.4f} sec.")
        if progress_win:
            progress_win.log_message(f"Components analyzed in {(time.time() - _time_analyze_depth):.2f} sec")
            progress_win.update_progress(55, "Importing groups...")

        # Import the components as duplicated groups then hide components
        self.write_duplicateable_groups()
        
        for vl in context.scene.view_layers:
            for l in vl.active_layer_collection.children:
                if l.name == 'SKP Components':
                    l.exclude = True  # hide component collection in view layer
        if options['dedub_only']:
            if progress_win:
                progress_win.update_progress(100, "Import completed!")
                show_finished_in_progress("Groups import completed successfully!")
            return {'FINISHED'}

        # Start stopwatch for mesh objects import
        if not MIN_LOGS:
            skp_log("")
            skp_log("=== Importing Sketchup mesh objects into Blender ===")
        if progress_win:
            progress_win.update_progress(65, "Importing entities...")
        _time_mesh_data = time.time()

        # Import mesh objects into structure that matches the SketchUp outliner
        self.write_entities(self.skp_model.entities,
                            "_(Loose Entity)",
                            Matrix.Identity(4))

        for k, _v in self.component_stats.items():
            name, mat = k
            if options['dedub_type'] == 'VERTEX':
                self.instance_group_dupli_vert(name, mat, self.component_stats)
            else:
                self.instance_group_dupli_face(name, mat, self.component_stats)
        if not MIN_LOGS:
            skp_log("Entities imported in "
                    f"{(time.time() - _time_mesh_data):.4f} sec.")
        if progress_win:
            progress_win.log_message(f"Entities imported in {(time.time() - _time_mesh_data):.2f} sec")
            progress_win.update_progress(85, "Finalizing import...")

        # Importing has completed
        if LOGS:
            skp_log("Finished entire importing process in %.4f sec.\n" %
                    (time.time() - _time_main))
        if progress_win:
            progress_win.log_message(f"Import completed in {(time.time() - _time_main):.2f} sec")
            progress_win.update_progress(95, "Cleaning up...")
                
        #kha
        
        collection_name = "new"
        collection = bpy.data.collections.get(collection_name)

        if collection is None:
            print("Collection", collection_name, "not found. Aborting operation.")
        else:
             
             if "SKP" in bpy.data.collections:
                 bpy.ops.outliner.orphans_purge(do_recursive=True) 
                 bpy.data.collections["SKP"].name = "SKP+"
                 collection_name = "SKP+"
                 collection = bpy.data.collections.get(collection_name)
                
             if "new" in bpy.data.collections:
                 bpy.data.collections["new"].name = "skp"

             collection_name = "skp"

            # Get the collection
             collection = bpy.data.collections.get(collection_name)

             if collection:            
                 materials = bpy.data.materials
                 collection = bpy.data.collections.get("skp")

                 # Check if the collection exists
                 if collection is not None:
                     # Iterate over each object in the collection
                     for obj in collection.objects:
                         # Check if the object has a material with an image texture node
                         has_image_texture = False
                         for slot in obj.material_slots:
                             if slot.material.node_tree:
                                 for node in slot.material.node_tree.nodes:
                                     if node.type == 'TEX_IMAGE':
                                         has_image_texture = True
                                         break        
        
                 material_name = "Material"  # اسم المادة المستهدفة

                 for material in bpy.data.materials:
                    if material.name == material_name and hasattr(material, 'diffuse_color'):
                        material.diffuse_color = (0.4, 0, 0.6, 1)


                 # Iterate over all materials in the scene
                 for material in bpy.data.materials:
                    # Check if the material has nodes disabled
                     if not material.use_nodes:
                        # Enable nodes
                         material.use_nodes = True
                        
                        # Check if the material has a Principled BSDF node
                         if 'Principled BSDF' in material.node_tree.nodes:
                            # Get the Principled BSDF node
                             principled_bsdf = material.node_tree.nodes['Principled BSDF']
                            
                            # Get the viewport color from material.diffuse_color
                             viewport_color = material.diffuse_color
                            
                            # Set the viewport color to Principled BSDF's default_value
                             principled_bsdf.inputs[0].default_value = viewport_color  
                 # إلغاء تحديد جميع العناصر في المشهد
                 bpy.ops.object.select_all(action='DESELECT')

                 # اسم الكولكشن الذي نريد تحديد العناصر فيه
                 collection_name = "skp"

                 # البحث عن الكولكشن باستخدام اسمه
                 collection = bpy.data.collections.get(collection_name)

                 if collection:
                    # تحديد جميع العناصر في الكولكشن
                     for obj in collection.objects:
                         obj.select_set(True)
                 else:
                     print("الكولكشن غير موجود")

        bpy.ops.outliner.orphans_purge(do_recursive=True)

        # لا حاجة لفتح Notepad - الكومبوننتات المتجاوزة معروضة في اللوق
        
        # إظهار رسالة الانتهاء في نافذة التقدم
        if progress_win:
            progress_win.update_progress(100, "Import completed!")
            progress_win.log_message("=" * 50)
            progress_win.log_message("Import process finished successfully")
            show_finished_in_progress("SKP file imported successfully!")
            
            # إظهار نافذة الكومبوننتات المتجاوزة إذا كانت موجودة
            if self.skipped_components:
                show_skipped_components(self.skipped_components)
        
        self.FenceCollection()    
        return {'FINISHED'}
    
    def write_duplicateable_groups(self):

        component_stats = self.analyze_entities(
            self.skp_model.entities,
            "Sketchup",
            Matrix.Identity(4),
            component_stats=defaultdict(list))
        instance_when_over = self.max_instance
        max_depth = max(self.component_depth.values(), default=0)
        component_stats = {
            k: v
            for k, v in component_stats.items() if len(v) >= instance_when_over
        }
        for i in range(max_depth + 1):
            for k, v in component_stats.items():
                name, mat = k
                # التحقق من وجود الكومبوننت قبل الوصول إليه
                if name not in self.component_depth:
                    if LOGS:
                        skp_log(f"Warning: Component '{name}' not found in depth analysis, skipping")
                    # إضافة إلى قائمة المتجاوزة
                    self.skipped_components.append(name)
                    progress_win = get_current_progress()
                    if progress_win:
                        progress_win.log_message(f"Skipped component: {name} (not in depth analysis)")
                    continue
                    
                depth = self.component_depth[name]
                #print(k, len(v), depth)
                comp_def = self.skp_components.get(name)
                if comp_def and depth == 1:
                    #self.component_skip[(name,mat)] = comp_def.entities
                    pass
                elif comp_def and depth == i:
                    gname = group_name(name, mat)
                    if self.reuse_group and gname in bpy.data.collections:
                        skp_log("Group {} already defined".format(gname))
                        #print("Group {} already defined".format(gname))
                        self.component_skip[(name, mat)] = comp_def.entities
                        # grp_name = bpy.data.collections[gname]
                        self.group_written[(name,
                                            mat)] = bpy.data.collections[gname]
                    else:
                        group = bpy.data.collections.new(name=gname)
                        #print("Component written as group".format(gname))
                        self.conponent_def_as_group(comp_def.entities,
                                                    name,
                                                    Matrix(),
                                                    default_material=mat,
                                                    etype=EntityType.outer,
                                                    group=group)
                        self.component_skip[(name, mat)] = comp_def.entities
                        self.group_written[(name, mat)] = group

    def analyze_entities(self,
                         entities,
                         name,
                         transform,
                         default_material="Material",
                         etype=EntityType.none,
                         component_stats=None,
                         component_skip=None):
        if component_skip is None:
            component_skip = []
        if etype == EntityType.component:
            component_stats[(name, default_material)].append(transform)

        for group in entities.groups:
            if self.layers_skip and group.layer in self.layers_skip:
                continue
            if DEBUG:
                print(f"     |G {group.name}")
                print(f"     {Matrix(group.transform)}")
            # print(transform)
            # print(Matrix(group.transform))
            self.analyze_entities(group.entities,
                                  "G-" + group_safe_name(group.name),
                                  transform @ Matrix(group.transform),
                                  default_material=inherent_default_mat(
                                      group.material, default_material),
                                  etype=EntityType.group,
                                  component_stats=component_stats)

        for instance in entities.instances:
            if self.layers_skip and instance.layer in self.layers_skip:
                continue
            mat = inherent_default_mat(instance.material, default_material)
            cdef = self.skp_components.get(instance.definition.name)
            
            if DEBUG:
                print(f"     |C {cdef.name}")
                print(f"     {Matrix(instance.transform)}")
            # KH
            if cdef is None:
                # عرض الكومبوننت المتجاوز في نافذة اللوق
                component_name = instance.definition.name
                # إزالة البادئة G- إذا كانت موجودة
                clean_name = component_name.replace("G-", "") if component_name.startswith("G-") else component_name
                self.skipped_components.append(clean_name)
                progress_win = get_current_progress()
                if progress_win:
                    progress_win.log_message(f"⚠ Skipped component: {clean_name}")
                if LOGS:
                    skp_log(f"Component not found: {clean_name}")
                continue
 
            self.analyze_entities(cdef.entities,
                                  "G-" + group_safe_name(cdef.name),
                                  transform @ Matrix(instance.transform),
                                  default_material=mat,
                                  etype=EntityType.component,
                                  component_stats=component_stats)

        return component_stats
    
    # Import materials from SketchUp into Blender.
    def write_materials(self, materials):

        if self.context.scene.render.engine != self.render_engine:
            self.context.scene.render.engine = self.render_engine

        self.materials = {}
        self.materials_scales = {}
        if self.reuse_material and 'Material' in bpy.data.materials:
            self.materials['Material'] = bpy.data.materials['Material']
        else:
            bmat = bpy.data.materials.new('Material')
            bmat.diffuse_color = (.8, .8, .8, 1)
            #if self.render_engine == 'CYCLES':
            bmat.use_nodes = True
            self.materials['Material'] = bmat

        for mat in materials:
            name = mat.name
            if mat.texture:
                self.materials_scales[name] = mat.texture.dimensions[2:]
            else:
                self.materials_scales[name] = (1.0, 1.0)
            if self.reuse_material and not name in bpy.data.materials:
                bmat = bpy.data.materials.new(name)
                r, g, b, a = mat.color
                tex = mat.texture
                bmat.diffuse_color = (math.pow((r / 255.0), 2.2),
                                      math.pow((g / 255.0), 2.2),
                                      math.pow((b / 255.0), 2.2),
                                      round((a / 255.0), 2))  # sRGB to Linear
                
                if round((a / 255.0), 2) < 1:
                    bmat.blend_method = 'BLEND'
                bmat.use_nodes = True
                default_shader = bmat.node_tree.nodes['Principled BSDF']
                default_shader_base_color = default_shader.inputs['Base Color']
                default_shader_base_color.default_value = bmat.diffuse_color
                default_shader_alpha = default_shader.inputs['Alpha']
                default_shader_alpha.default_value = round((a / 255.0), 2)

                if tex:
                    if tex and isinstance(tex, bpy.types.ImageTexture) and tex.name[0] == '.' and len(tex.name) < 5:
                        #Combine material name with image extension for a valid name
                        tex_name = mat.name + tex.name
                    else:
                        try:
                            tex_name = tex.name.split("\\")[-1]
                        except Exception as e:
                            # اتخذ إجراء مناسب للتعامل مع الخطأ
                            print(f"Error getting texture name: {e}")
                            tex_name = "default_texture_name"

                    tmp_name = os.path.join(tempfile.gettempdir(), tex_name)

                    temp_dir = tempfile.gettempdir()
                    skp_fname = self.filepath.split("\\")[-1].split(".")[0]
                    temp_dir += '\\' + skp_fname
                    if not os.path.isdir(temp_dir):
                        os.mkdir(temp_dir)

                    temp_file_path = os.path.join(temp_dir, tex_name)
                    # skp_log(f"Texture saved temporarily at {tmp_name}")
                    try:
                        tex.write(tmp_name)
                        tex.write(temp_file_path)
                    except Exception as e:
                        # اتخذ إجراء مناسب للتعامل مع الخطأ
                        print(f"Error writing texture to temp file: {e}")

                    img = None  # قيمة افتراضية

                    try:
                        img = bpy.data.images.load(tmp_name)
                        img = bpy.data.images.load(temp_file_path)
                    except Exception as e:
                        # اتخذ إجراء مناسب للتعامل مع الخطأ
                        print(f"Error loading image file: {e}")

                    if img:
                        img.pack()

                    # التحقق من وجود الملف قبل محاولة حذفه
                    if os.path.exists(tmp_name):
                        os.remove(tmp_name)
                    else:
                        print(f"File not found: {tmp_name}")

                    if self.render_engine == 'CYCLES':
                        #os.remove(temp_file_path)
                        shutil.rmtree(temp_dir)
                        #if self.render_engine == 'CYCLES':
                        #    bmat.use_nodes = True
                        tex_node = bmat.node_tree.nodes.new('ShaderNodeTexImage')
                        tex_node.image = img
                        tex_node.location = Vector((-750, 225))
                        bmat.node_tree.links.new(
                            tex_node.outputs['Color'], default_shader_base_color)
                        bmat.node_tree.links.new(
                            tex_node.outputs['Alpha'], default_shader_alpha)
                    else:
                        btex = bpy.data.textures.new(tex_name, 'IMAGE')
                        btex.image = img
                        slot = bmat.texture_slots.add()
                        slot.texture = btex

                    
                    #skp_log(f"Texture saved temporarily at {temp_file_path}")
                    
                self.materials[name] = bmat
            else:
                self.materials[name] = bpy.data.materials[name]
            if not MIN_LOGS:
                print(f"     {name}")

  

    def write_mesh_data(self,
                        entities=None,
                        name="",
                        default_material='Material'):

        mesh_key = (name, default_material)
        if mesh_key in self.component_meshes:
            return self.component_meshes[mesh_key]
        verts = []
        loops_vert_idx = []
        mat_index = []
        smooth = []
        mats = keep_offset()
        seen = keep_offset()
        uv_list = []
        alpha = False
        uvs_used = False

        for f in entities.faces:
            if f.material:
                mat_number = mats[f.material.name]
            else:
                mat_number = mats[default_material]
                if default_material != 'Material':
                    try:
                        f.st_scale = self.materials_scales[default_material]
                    except KeyError as _e:
                        pass
            
            vs, tri, uvs = f.tessfaces
            num_loops = 0

            mapping = {}
            for i, (v, uv) in enumerate(zip(vs, uvs)):
                l = len(seen)
                mapping[i] = seen[v]
                if len(seen) > l:
                    verts.append(v)
                uvs.append(uv)

            smooth_edge = False

            for edge in f.edges:
                if edge.GetSmooth() == True:
                    smooth_edge = True
                    break

            for face in tri:
                f0, f1, f2 = face[0], face[1], face[2]
                num_loops += 1

                if mapping[f2] == 0:
                    loops_vert_idx.extend([mapping[f2],
                                           mapping[f0],
                                           mapping[f1]])

                    uv_list.append((uvs[f2][0], uvs[f2][1],
                                    uvs[f0][0], uvs[f0][1],
                                    uvs[f1][0], uvs[f1][1]))

                else:
                    loops_vert_idx.extend([mapping[f0],
                                           mapping[f1],
                                           mapping[f2]])

                    uv_list.append((uvs[f0][0], uvs[f0][1],
                                    uvs[f1][0], uvs[f1][1],
                                    uvs[f2][0], uvs[f2][1]))

                smooth.append(smooth_edge)
                mat_index.append(mat_number)

        if len(verts) == 0:
            return None, False

        me = bpy.data.meshes.new(name)

        if len(mats) >= 1:
            mats_sorted = OrderedDict(sorted(mats.items(), key=lambda x: x[1]))
            for k in mats_sorted.keys():
                try:
                    bmat = self.materials[k]
                except KeyError as _e:
                    bmat = self.materials["Material"]
                me.materials.append(bmat)
                # if bmat.alpha < 1.0:
                #     alpha = True
                try:
                    if self.render_engine == 'CYCLES':
                        if 'Image Texture' in bmat.node_tree.nodes.keys():
                            uvs_used = True
                    else:
                        for ts in bmat.texture_slots:
                            if ts is not None and ts.texture_coords is not None:
                                uvs_used = True
                except AttributeError as _e:
                    uvs_used = False
        else:
            skp_log(f"WARNING: Object {name} has no material!")

        tri_faces = list(zip(*[iter(loops_vert_idx)] * 3))
        tri_face_count = len(tri_faces)

        loop_start = []
        i = 0
        for f in tri_faces:
            loop_start.append(i)
            i += len(f)

        loop_total = list(map(lambda f: len(f), tri_faces))

        me.vertices.add(len(verts))
        me.vertices.foreach_set("co", unpack_list(verts))

        me.loops.add(len(loops_vert_idx))
        me.loops.foreach_set("vertex_index", loops_vert_idx)

        me.polygons.add(tri_face_count)
        me.polygons.foreach_set("loop_start", loop_start)
        me.polygons.foreach_set("loop_total", loop_total)
        me.polygons.foreach_set("material_index", mat_index)
        me.polygons.foreach_set("use_smooth", smooth)

        if uvs_used:
            k, l = 0, 0
            me.uv_layers.new()
            for i in range(len(tri_faces)):
                for j in range(3):
                    uv_cordinates = (uv_list[i][l], uv_list[i][l + 1])
                    me.uv_layers[0].data[k].uv = Vector(uv_cordinates)
                    k += 1
                    if j != 2:
                        l += 2
                    else:
                        l = 0

        me.update(calc_edges=True)
        me.validate()
        self.component_meshes[mesh_key] = me, alpha

        return me, alpha




    def write_entities(self,
                       entities,
                       name,
                       parent_tranform,
                       default_material="Material",
                       etype=None):

        if etype == EntityType.component and (
                name, default_material) in self.component_skip:
            self.component_stats[(name,
                                  default_material)].append(parent_tranform)
            return

        me, alpha = self.write_mesh_data(entities=entities,
                                         name=name,
                                         default_material=default_material)

        if me:
            ob = bpy.data.objects.new(name, me)
            ob.matrix_world = parent_tranform
            if alpha > 0.01 and alpha < 1.0:
                ob.show_transparent = True
            me.update(calc_edges=True)
            bpy.context.collection.objects.link(ob)

        for group in entities.groups:
            if group.hidden:
                continue
            if self.layers_skip and group.layer in self.layers_skip:
                continue
            self.write_entities(group.entities,
                                "G-" + group_safe_name(group.name),
                                parent_tranform @ Matrix(group.transform),
                                default_material=inherent_default_mat(
                                    group.material, default_material),
                                etype=EntityType.group)

        for instance in entities.instances:
            if instance.hidden:
                continue
            if self.layers_skip and instance.layer in self.layers_skip:
                continue
            mat_name = inherent_default_mat(instance.material,
                                            default_material)
            cdef = self.skp_components.get(instance.definition.name)
            
            if cdef is None:
                    continue

            self.write_entities(cdef.entities,
                                "G-" + group_safe_name(cdef.name),
                                parent_tranform @ Matrix(instance.transform),
                                default_material=mat_name,
                                etype=EntityType.component)

    def instance_object_or_group(self, name, default_material):

        try:
            group = self.group_written[(name, default_material)]
            ob = bpy.data.objects.new(name=name, object_data=None)
            # ob.dupli_type = 'GROUP'
            # ob.dupli_group = group
            # ob.empty_draw_size = 0.01
            return ob
        except KeyError as _e:
            me, alpha = self.component_meshes[(name, default_material)]
            ob = bpy.data.objects.new(name, me)
            if alpha:
                ob.show_transparent = True
            me.update(calc_edges=True)
            return ob

    def conponent_def_as_group(self,
                               entities,
                               name,
                               parent_tranform,
                               default_material="Material",
                               etype=None,
                               group=None):

        if etype == EntityType.outer:
            if (name, default_material) in self.component_skip:
                return
            else:
                skp_log("Write instance definition as group {} {}".format(
                    group.name, default_material))
                self.component_skip[(name, default_material)] = True

        if etype == EntityType.component and (
                name, default_material) in self.component_skip:
            ob = self.instance_object_or_group(name, default_material)
            ob.matrix_world = parent_tranform
            # self.context.scene.objects.link(ob)
            self.context.collection.objects.link(ob)
            # ob.layers = 18 * [False] + [True] + [False]
            group.objects.link(ob)

            return

        else:
            me, alpha = self.write_mesh_data(entities=entities,
                                             name=name,
                                             default_material=default_material)

        if me:
            ob = bpy.data.objects.new(name, me)
            ob.matrix_world = parent_tranform
            if alpha:
                ob.show_transparent = True
            me.update(calc_edges=True)
            # self.context.scene.objects.link(ob)
            self.context.collection.objects.link(ob)
            # ob.layers = 18 * [False] + [True] + [False]
            group.objects.link(ob)

        for g in entities.groups:
            if self.layers_skip and g.layer in self.layers_skip:
                continue
            self.conponent_def_as_group(
                g.entities,
                "G-" + group_safe_name(g.name),
                parent_tranform @ Matrix(g.transform),
                default_material=inherent_default_mat(g.material,
                                                      default_material),
                etype=EntityType.group,
                group=group)

        for instance in entities.instances:
            if self.layers_skip and instance.layer in self.layers_skip:
                continue
            cdef = self.skp_components.get(instance.definition.name)
            if cdef is None:
                    continue
            self.conponent_def_as_group(
                cdef.entities,
                "G-" + group_safe_name(cdef.name),
                parent_tranform @ Matrix(instance.transform),
                default_material=inherent_default_mat(instance.material,
                                                      default_material),
                etype=EntityType.component,
                group=group)

    def instance_group_dupli_vert(self,
                                  name,
                                  default_material,
                                  component_stats):

        def get_orientations(v):

            orientations = defaultdict(list)

            for transform in v:
                loc, rot, scale = Matrix(transform).decompose()
                scale = (scale[0], scale[1], scale[2])
                rot = (rot[0], rot[1], rot[2], rot[3])
                orientations[(scale, rot)].append((loc[0], loc[1], loc[2]))

            for key, locs in orientations.items():
                scale, rot = key
                yield scale, rot, locs

        for scale, rot, locs in get_orientations(
                component_stats[(name, default_material)]):
            verts = []
            main_loc = Vector(locs[0])
            for c in locs:
                verts.append(Vector(c) - main_loc)
            
            '''
            dme = bpy.data.meshes.new('DUPLI_' + name)
            dme.vertices.add(len(verts))
            dme.vertices.foreach_set("co", unpack_list(verts))
            dme.update(calc_edges=True)  # Update mesh with new data
            dme.validate()
            dob = bpy.data.objects.new("DUPLI_" + name, dme)
            dob.location = main_loc
            # dob.dupli_type = 'VERTS'
            '''
            dme = bpy.data.meshes.new('DUPLI_' + name)
            dme.from_pydata(verts,[],faces)

            dob = bpy.data.objects.new("DUPLI_" + name, dme)
            dob.location = main_loc

            ob = self.instance_object_or_group(name, default_material)
            ob.scale = scale
            ob.rotation_quaternion = Quaternion(
                (rot[0], rot[1], rot[2], rot[3]))
            ob.parent = dob

            self.context.collection.objects.link(ob)
            self.context.collection.objects.link(dob)
            skp_log(
                "Complex group {} {} instanced {} times, scale -> {}".format(
                    name, default_material, len(verts), scale))

        return

    def instance_group_dupli_face(self,
                                  name,
                                  default_material,
                                  component_stats):

        def get_orientations(v):

            orientations = defaultdict(list)

            for transform in v:
                _loc, _rot, scale = Matrix(transform).decompose()
                scale = (scale[0], scale[1], scale[2])
                orientations[scale].append(transform)

            for scale, transforms in orientations.items():
                yield scale, transforms

        for _scale, transforms in get_orientations(
                component_stats[(name, default_material)]):
            main_loc, _, real_scale = Matrix(transforms[0]).decompose()
            verts = []
            faces = []
            f_count = 0

            for c in transforms:
                l_loc, l_rot, _l_scale = Matrix(c).decompose()
                mat = Matrix.Translation(l_loc) @ l_rot.to_matrix().to_4x4()

                verts.append(Vector(
                    (mat @ Vector((-0.05, -0.05, 0, 1.0)))[0:3]) - main_loc)
                verts.append(Vector(
                    (mat @ Vector((0.05, -0.05, 0, 1.0)))[0:3]) - main_loc)
                verts.append(Vector(
                    (mat @ Vector((0.05, 0.05, 0, 1.0)))[0:3]) - main_loc)
                verts.append(Vector(
                    (mat @ Vector((-0.05, 0.05, 0, 1.0)))[0:3]) - main_loc)

                faces.append(
                    (f_count + 0, f_count + 1, f_count + 2, f_count + 3))

                f_count += 4

            '''
            dme = bpy.data.meshes.new('DUPLI_' + name)
            dme.vertices.add(len(verts))
            dme.vertices.foreach_set("co", unpack_list(verts))

            # dme.loop_triangles.add(f_count / 4)
            dme.loop_triangles.foreach_set("vertices_raw", unpack_face_list(faces))
            dme.update(calc_edges=True)  # Update mesh with new data
            dme.validate()
            dob = bpy.data.objects.new("DUPLI_" + name, dme)
            # dob.dupli_type = 'FACES'
            dob.location = main_loc
            #dob.use_dupli_faces_scale = True
            #dob.dupli_faces_scale = 10
            '''

            dme = bpy.data.meshes.new('DUPLI_' + name)
            dme.from_pydata(verts,[],faces)

            dob = bpy.data.objects.new("DUPLI_" + name, dme)
            dob.location = main_loc

            ob = self.instance_object_or_group(name, default_material)
            ob.scale = real_scale
            ob.parent = dob
            self.context.collection.objects.link(ob)
            self.context.collection.objects.link(dob)
            skp_log("Complex group {} {} instanced {} times".format(
                name, default_material, f_count / 4))

        return

    def write_camera(self, camera, name="Active Camera"):

        pos, target, up = camera.GetOrientation()
        bpy.ops.object.add(type='CAMERA', location=pos)
        ob = self.context.object
        ob.name = name

        z = (Vector(pos) - Vector(target))
        x = Vector(up).cross(z)
        y = z.cross(x)

        x.normalize()
        y.normalize()
        z.normalize()

        ob.matrix_world.col[0] = x.resized(4)
        ob.matrix_world.col[1] = y.resized(4)
        ob.matrix_world.col[2] = z.resized(4)

        cam = ob.data
        aspect_ratio = camera.aspect_ratio
        fov = camera.fov
        if aspect_ratio == False:
            # skp_log(f"Camera:'{name}' uses dynamic/screen aspect ratio.")
            aspect_ratio = self.aspect_ratio
        if fov == False:
            skp_log(f"Camera:'{name}'' is in Orthographic Mode.")
            cam.type = 'ORTHO'
        else:
            cam.angle = (math.pi * fov / 180) * aspect_ratio
        cam.clip_end = self.prefs.camera_far_plane
        cam.name = name
    
    def FenceCollection(self):
        skp_col = bpy.data.collections.get("skp")
        if not skp_col:
            return {'CANCELLED'}

        # Helper to ensure collections exist and are nested correctly
        def get_or_create_col(name, parent=None):
            c = bpy.data.collections.get(name)
            if not c:
                c = bpy.data.collections.new(name)
                if parent:
                    if c.name not in parent.children:
                        parent.children.link(c)
                else:
                    if c.name not in bpy.context.scene.collection.children:
                        bpy.context.scene.collection.children.link(c)
            return c

        fence_group = get_or_create_col("Fence Group")
        col_map = {
            "g-f": get_or_create_col("Front", fence_group),
            "g-b": get_or_create_col("Back", fence_group),
            "g-r": get_or_create_col("Right", fence_group),
            "g-l": get_or_create_col("Left", fence_group)
        }

        prefixes = list(col_map.keys())
        processed = set()

        def move_recursive(ob, target_col):
            if ob in processed:
                return
            processed.add(ob)
            
            # Link to target collection if not already there
            if ob.name not in target_col.objects:
                target_col.objects.link(ob)
                
            # Unlink from all other collections (specifically 'skp')
            for coll in list(ob.users_collection):
                if coll != target_col:
                    coll.objects.unlink(ob)
            
            # Clean name: remove prefix but keep case for the rest
            if ob.name.lower().startswith("g-"):
                ob.name = ob.name[2:]
            
            # Recursively move all descendants to keep hierarchy together
            for child in ob.children:
                move_recursive(child, target_col)

        # Iterate over ALL objects in the file to catch nested instances and sub-components
        any_moved = False
        all_objs = list(bpy.data.objects)
        
        for obj in all_objs:
            if obj in processed:
                continue
            
            name_low = obj.name.lower()
            for p in prefixes:
                # Flexible check for f, f1, f 1, f 107 1, etc.
                if name_low == p or name_low.startswith(p + " ") or \
                   (name_low.startswith(p) and name_low[len(p):len(p)+1].isdigit()):
                    move_recursive(obj, col_map[p])
                    any_moved = True
                    break
        
        return {'FINISHED'} if any_moved else {'CANCELLED'}

        

   
#update-----------------------------------------------------------------------------------------------------
class SceneImporterupdate():
    def __init__(self):

        self.filepath = '/tmp/untitled.skp'
        self.name_mapping = {}
        self.skipped_components = []  # قائمة الكومبوننتات المتجاوزة
        self.component_meshes = {}
        self.scene = None
        self.layers_skip = []

    def set_filename(self, filename):

        self.filepath = filename
        self.basepath, self.skp_filename = os.path.split(self.filepath)
        return self  # allow chaining

    def load(self, context, **options):
        """load a sketchup file"""

        self.context = context
        self.reuse_material = options['reuse_material']
        self.reuse_group = options['reuse_existing_groups']
        self.max_instance = options['max_instance']
        self.render_engine = options['render_engine']
        self.component_stats = defaultdict(list)
        self.component_skip = proxy_dict()
        self.component_depth = proxy_dict()
        self.group_written = {}
        ren_res_x = context.scene.render.resolution_x
        ren_res_y = context.scene.render.resolution_y
        self.aspect_ratio = ren_res_x / ren_res_y

        # الحصول على نافذة التقدم
        progress_win = get_current_progress()

        # لا حاجة لملف components Not imported.txt بعد الآن
        # سيتم عرض الكومبوننتات المتجاوزة في نافذة اللوق مباشرة

        skp_log(f'Importing: {self.filepath}')
        if progress_win:
            progress_win.log_message(f"Updating: {self.filepath}")
            progress_win.update_progress(5, "Reading SketchUp file...")

        addon_name = __name__.split('.')[0]
        self.prefs = context.preferences.addons[addon_name].preferences

        _time_main = time.time()

        try:
            self.skp_model = sketchup.Model.from_file(self.filepath)
            if progress_win:
                progress_win.log_message("SketchUp file loaded successfully")
                progress_win.update_progress(15, "Importing scenes...")
        except Exception as e:
            skp_log(f'Error reading input file: {self.filepath}')
            skp_log(e)
            if progress_win:
                progress_win.log_message(f"Error reading file: {e}")
                show_finished_in_progress(f"Error: {e}")
            return {'FINISHED'}

        if options['import_scene']:
            for s in self.skp_model.scenes:
                if s.name == options['import_scene']:
                    skp_log(f"Importing Scene '{s.name}'")
                    self.scene = s
                    self.layers_skip = [l for l in s.layers]
                    for l in s.layers:
                        skp_log(f"SKIP: {l.name}")
            if not self.layers_skip:
                skp_log('Could not find scene: {}, importing default.'
                        .format(options['import_scene']))

        if not self.layers_skip:
            self.layers_skip = [
                l for l in self.skp_model.layers if not l.visible
            ]

        skp_log('Skipping Layers ... ')

        for l in sorted([l.name for l in self.layers_skip]):
            skp_log(l)

        self.skp_components = proxy_dict(
            self.skp_model.component_definition_as_dict)

        skp_log(f'Parsed in {(time.time() - _time_main):.4f} sec.')
        if progress_win:
            progress_win.update_progress(25, "Importing cameras...")

        if options['scenes_as_camera']:
            for s in self.skp_model.scenes:
                self.write_camera(s.camera, s.name)

        if options['import_camera']:
            if self.scene:
                active_cam = self.write_camera(self.scene.camera,
                                               name=self.scene.name)
                context.scene.camera = active_cam
            else:
                active_cam = self.write_camera(self.skp_model.camera)
                context.scene.camera = active_cam

        _t1 = time.time()
        if progress_win:
            progress_win.update_progress(35, "Importing materials...")
        self.write_materials(self.skp_model.materials)

        skp_log(f'Materials imported in {(time.time() - _t1):.4f} sec.')
        if progress_win:
            progress_win.log_message(f"Materials imported in {(time.time() - _t1):.2f} sec")
            progress_win.update_progress(50, "Analyzing components...")

        _t1 = time.time()
        D = SKP_util()
        SKP_util.layers_skip = self.layers_skip

        for c in self.skp_model.component_definitions:
            self.component_depth[c.name] = D.component_deps(c.entities)

        skp_log(f'Component depths analyzed in {(time.time() - _t1):.4f} sec.')
        if progress_win:
            progress_win.log_message(f"Components analyzed in {(time.time() - _t1):.2f} sec")
            progress_win.update_progress(60, "Importing groups...")

        self.write_duplicateable_groups()

        if options["dedub_only"]:
            if progress_win:
                progress_win.update_progress(100, "Update completed")
                progress_win.log_message("Update completed successfully")
                show_finished_in_progress("Update completed successfully!")
            return {'FINISHED'}
        
        _time_mesh_data = time.time()
        if progress_win:
            progress_win.update_progress(70, "Importing entities...")

        create_nested_collection('new')

        self.component_stats = defaultdict(list)
        self.write_entities(self.skp_model.entities, "Sketchup",
                            Matrix.Identity(4))

        for k, _v in self.component_stats.items():
            name, mat = k
            if options['dedub_type'] == "VERTEX":
                self.instance_group_dupli_vert(name, mat, self.component_stats)
            else:
                self.instance_group_dupli_face(name, mat, self.component_stats)

        skp_log(f'Entities imported in {(time.time() - _t1):.4f} sec.')
        skp_log('Finished importing in %.4f sec.\n' %
                (time.time() - _time_main))
        if progress_win:
            progress_win.log_message(f"Entities imported in {(time.time() - _time_mesh_data):.2f} sec")
            progress_win.update_progress(90, "Cleaning up...")
                
        #kha
        collection_name = "new"
        collection = bpy.data.collections.get(collection_name)

        if collection is None:
            print("Collection", collection_name, "not found. Aborting operation.")
        else:
     
             if "SKP Master" in bpy.data.collections:
                 bpy.ops.outliner.orphans_purge(do_recursive=True) 
                 bpy.data.collections["SKP Master"].name = "skp_old"
                 collection_name = "skp_old"
                 collection = bpy.data.collections.get(collection_name)
                 if collection is not None:
                    objects = collection.objects
                    for obj in objects:
                        if obj.type == 'MESH':
                            obj.name += ".old"
                            obj.data.name += ".old"


             collection = bpy.data.collections.get("skp_old")
             if collection:
                collection.hide_viewport = True
                collection.hide_render = True
                
             if "new" in bpy.data.collections:
                 bpy.data.collections["new"].name = "SKP Master"

             collection_name = "SKP Master"

            # Get the collection
             collection = bpy.data.collections.get(collection_name)

             if collection:            
                 materials = bpy.data.materials
                 collection = bpy.data.collections.get("SKP Master")

                 # Check if the collection exists
                 if collection is not None:
                     # Iterate over each object in the collection
                     for obj in collection.objects:
                         # Check if the object has a material with an image texture node
                         has_image_texture = False
                         for slot in obj.material_slots:
                             if slot.material.node_tree:
                                 for node in slot.material.node_tree.nodes:
                                     if node.type == 'TEX_IMAGE':
                                         has_image_texture = True
                                         break        
        
                 material_name = "Material"  # اسم المادة المستهدفة

                 for material in bpy.data.materials:
                    if material.name == material_name and hasattr(material, 'diffuse_color'):
                        material.diffuse_color = (0.4, 0, 0.6, 1)

                 # Iterate over all materials in the scene
                 for material in bpy.data.materials:
                    # Check if the material has nodes disabled
                     if not material.use_nodes:
                        # Enable nodes
                         material.use_nodes = True
                        
                        # Check if the material has a Principled BSDF node
                         if 'Principled BSDF' in material.node_tree.nodes:
                            # Get the Principled BSDF node
                             principled_bsdf = material.node_tree.nodes['Principled BSDF']
                            
                            # Get the viewport color from material.diffuse_color
                             viewport_color = material.diffuse_color
                            
                            # Set the viewport color to Principled BSDF's default_value
                             principled_bsdf.inputs[0].default_value = viewport_color  
                
                 # إلغاء تحديد جميع العناصر في المشهد
                 bpy.ops.object.select_all(action='DESELECT')

                 # اسم الكولكشن الذي نريد تحديد العناصر فيه
                 collection_name = "SKP Master"

                 # البحث عن الكولكشن باستخدام اسمه
                 collection = bpy.data.collections.get(collection_name)

                 if collection:
                    # تحديد جميع العناصر في الكولكشن
                     for obj in collection.objects:
                         obj.select_set(True)
                 else:
                     print("الكولكشن غير موجود")

        bpy.ops.outliner.orphans_purge(do_recursive=True)
        documents_path = os.path.expanduser("~/Documents")
        # لا حاجة لفتح Notepad - الكومبوننتات المتجاوزة معروضة في اللوق
        
        # إظهار رسالة الانتهاء في نافذة التقدم
        if progress_win:
            progress_win.update_progress(100, "Update completed!")
            progress_win.log_message("=" * 50)
            progress_win.log_message("Update process finished successfully")
            show_finished_in_progress("SKP file updated successfully!")
            
            # إظهار نافذة الكومبوننتات المتجاوزة إذا كانت موجودة
            if self.skipped_components:
                show_skipped_components(self.skipped_components)
            
        self.FenceCollection()        
        return {'FINISHED'}

    def write_duplicateable_groups(self):

        component_stats = self.analyze_entities(
            self.skp_model.entities,
            "Sketchup",
            Matrix.Identity(4),
            component_stats=defaultdict(list))
        instance_when_over = self.max_instance
        max_depth = max(self.component_depth.values(), default=0)
        component_stats = {
            k: v
            for k, v in component_stats.items() if len(v) >= instance_when_over
        }
        for i in range(max_depth + 1):
            for k, v in component_stats.items():
                name, mat = k
                # التحقق من وجود الكومبوننت قبل الوصول إليه
                if name not in self.component_depth:
                    if LOGS:
                        skp_log(f"Warning: Component '{name}' not found in depth analysis, skipping")
                    # إضافة إلى قائمة المتجاوزة (إزالة البادئة G-)
                    clean_name = name.replace("G-", "") if name.startswith("G-") else name
                    self.skipped_components.append(clean_name)
                    progress_win = get_current_progress()
                    if progress_win:
                        progress_win.log_message(f"⚠ Skipped component: {clean_name} (not in depth analysis)")
                    continue
                    
                depth = self.component_depth[name]
                #print(k, len(v), depth)
                comp_def = self.skp_components[name]
                if comp_def and depth == 1:
                    #self.component_skip[(name,mat)] = comp_def.entities
                    pass
                elif comp_def and depth == i:
                    gname = group_name(name, mat)
                    if self.reuse_group and gname in bpy.data.collections:
                        #print("Group {} already defined".format(gname))
                        self.component_skip[(name, mat)] = comp_def.entities
                        # grp_name = bpy.data.collections[gname]
                        self.group_written[(name,
                                            mat)] = bpy.data.collections[gname]
                    else:
                        group = bpy.data.collections.new(name=gname)
                        #print("Component written as group".format(gname))
                        self.conponent_def_as_group(comp_def.entities,
                                                    name,
                                                    Matrix(),
                                                    default_material=mat,
                                                    etype=EntityType.outer,
                                                    group=group)
                        self.component_skip[(name, mat)] = comp_def.entities
                        self.group_written[(name, mat)] = group

    def analyze_entities(self,
                         entities,
                         name,
                         transform,
                         default_material="Material",
                         etype=EntityType.none,
                         component_stats=None,
                         component_skip=[]):

        if etype == EntityType.component:
            component_stats[(name, default_material)].append(transform)

        for group in entities.groups:
            if self.layers_skip and group.layer in self.layers_skip:
                continue
            # print(transform)
            # print(Matrix(group.transform))
            self.analyze_entities(group.entities,
                                  "G-" + group.name,
                                  transform @ Matrix(group.transform),
                                  default_material=inherent_default_mat(
                                      group.material, default_material),
                                  etype=EntityType.group,
                                  component_stats=component_stats)

        for instance in entities.instances:
            if self.layers_skip and instance.layer in self.layers_skip:
                continue
            mat = inherent_default_mat(instance.material, default_material)
            cdef = self.skp_components.get(instance.definition.name)

            if cdef is None:
                # عرض الكومبوننت المتجاوز في نافذة اللوق
                component_name = instance.definition.name
                # إزالة البادئة G- إذا كانت موجودة
                clean_name = component_name.replace("G-", "") if component_name.startswith("G-") else component_name
                self.skipped_components.append(clean_name)
                progress_win = get_current_progress()
                if progress_win:
                    progress_win.log_message(f"⚠ Skipped component: {clean_name}")
                if LOGS:
                    skp_log(f"Component not found: {clean_name}")
                continue

            self.analyze_entities(cdef.entities,
                                  cdef.name,
                                  transform @ Matrix(instance.transform),
                                  default_material=mat,
                                  etype=EntityType.component,
                                  component_stats=component_stats)

        return component_stats

    def write_materials(self, materials):

        if self.context.scene.render.engine != self.render_engine:
            self.context.scene.render.engine = self.render_engine

        self.materials = {}
        self.materials_scales = {}
        if self.reuse_material and 'Material' in bpy.data.materials:
            self.materials['Material'] = bpy.data.materials['Material']
        else:
            bmat = bpy.data.materials.new('Material')
            bmat.diffuse_color = (.8, .8, .8, 1)
            #if self.render_engine == 'CYCLES':
            bmat.use_nodes = True
            self.materials['Material'] = bmat

        for mat in materials:
            name = mat.name
            if mat.texture:
                self.materials_scales[name] = mat.texture.dimensions[2:]
            else:
                self.materials_scales[name] = (1.0, 1.0)
            if self.reuse_material and not name in bpy.data.materials:
                bmat = bpy.data.materials.new(name)
                r, g, b, a = mat.color
                tex = mat.texture
                bmat.diffuse_color = (math.pow((r / 255.0), 2.2),
                                      math.pow((g / 255.0), 2.2),
                                      math.pow((b / 255.0), 2.2),
                                      round((a / 255.0), 2))  # sRGB to Linear
                
                if round((a / 255.0), 2) < 1:
                    bmat.blend_method = 'BLEND'
                bmat.use_nodes = True
                default_shader = bmat.node_tree.nodes['Principled BSDF']
                default_shader_base_color = default_shader.inputs['Base Color']
                default_shader_base_color.default_value = bmat.diffuse_color
                default_shader_alpha = default_shader.inputs['Alpha']
                default_shader_alpha.default_value = round((a / 255.0), 2)

                if tex:
                    if tex and isinstance(tex, bpy.types.ImageTexture) and tex.name[0] == '.' and len(tex.name) < 5:
                        #Combine material name with image extension for a valid name
                        tex_name = mat.name + tex.name
                    else:
                        try:
                            tex_name = tex.name.split("\\")[-1]
                        except Exception as e:
                            # اتخذ إجراء مناسب للتعامل مع الخطأ
                            print(f"Error getting texture name: {e}")
                            tex_name = "default_texture_name"

                    tmp_name = os.path.join(tempfile.gettempdir(), tex_name)

                    temp_dir = tempfile.gettempdir()
                    skp_fname = self.filepath.split("\\")[-1].split(".")[0]
                    temp_dir += '\\' + skp_fname
                    if not os.path.isdir(temp_dir):
                        os.mkdir(temp_dir)
                        
                    temp_file_path = os.path.join(temp_dir, tex_name)
                    # skp_log(f"Texture saved temporarily at {tmp_name}")
                    try:
                        tex.write(tmp_name)
                        tex.write(temp_file_path)
                    except Exception as e:
                        # اتخذ إجراء مناسب للتعامل مع الخطأ
                        print(f"Error writing texture to temp file: {e}")

                    img = None  # قيمة افتراضية

                    try:
                        img = bpy.data.images.load(tmp_name)
                        img = bpy.data.images.load(temp_file_path)
                    except Exception as e:
                        # اتخذ إجراء مناسب للتعامل مع الخطأ
                        print(f"Error loading image file: {e}")

                    if img:
                        img.pack()

                    # التحقق من وجود الملف قبل محاولة حذفه
                    if os.path.exists(tmp_name):
                        os.remove(tmp_name)
                    else:
                        print(f"File not found: {tmp_name}")

                    if self.render_engine == 'CYCLES':
                        #os.remove(temp_file_path)
                        shutil.rmtree(temp_dir)
                        #if self.render_engine == 'CYCLES':
                        #    bmat.use_nodes = True
                        tex_node = bmat.node_tree.nodes.new('ShaderNodeTexImage')
                        tex_node.image = img
                        tex_node.location = Vector((-750, 225))
                        bmat.node_tree.links.new(
                            tex_node.outputs['Color'], default_shader_base_color)
                        bmat.node_tree.links.new(
                            tex_node.outputs['Alpha'], default_shader_alpha)
                    else:
                        btex = bpy.data.textures.new(tex_name, 'IMAGE')
                        btex.image = img
                        slot = bmat.texture_slots.add()
                        slot.texture = btex
                    
                    #skp_log(f"Texture saved temporarily at {temp_file_path}")

                self.materials[name] = bmat
            else:
                self.materials[name] = bpy.data.materials[name]
            if not MIN_LOGS:
                print(f"     {name}")

    def write_mesh_data(self,
                        entities=None,
                        name="",
                        default_material='Material'):

        mesh_key = (name, default_material)
        if mesh_key in self.component_meshes:
            return self.component_meshes[mesh_key]
        verts = []
        loops_vert_idx = []
        mat_index = []
        smooth = []
        mats = keep_offset()
        seen = keep_offset()
        uv_list = []
        alpha = False
        uvs_used = False

        for f in entities.faces:
            if f.material:
                mat_number = mats[f.material.name]
            else:
                mat_number = mats[default_material]
                if default_material != 'Material':
                    try:
                        f.st_scale = self.materials_scales[default_material]
                    except KeyError as _e:
                        pass
            
            vs, tri, uvs = f.tessfaces
            num_loops = 0

            mapping = {}
            for i, (v, uv) in enumerate(zip(vs, uvs)):
                l = len(seen)
                mapping[i] = seen[v]
                if len(seen) > l:
                    verts.append(v)
                uvs.append(uv)

            smooth_edge = False

            for edge in f.edges:
                if edge.GetSmooth() == True:
                    smooth_edge = True
                    break

            for face in tri:
                f0, f1, f2 = face[0], face[1], face[2]
                num_loops += 1

                if mapping[f2] == 0:
                    loops_vert_idx.extend([mapping[f2],
                                           mapping[f0],
                                           mapping[f1]])

                    uv_list.append((uvs[f2][0], uvs[f2][1],
                                    uvs[f0][0], uvs[f0][1],
                                    uvs[f1][0], uvs[f1][1]))

                else:
                    loops_vert_idx.extend([mapping[f0],
                                           mapping[f1],
                                           mapping[f2]])

                    uv_list.append((uvs[f0][0], uvs[f0][1],
                                    uvs[f1][0], uvs[f1][1],
                                    uvs[f2][0], uvs[f2][1]))

                smooth.append(smooth_edge)
                mat_index.append(mat_number)

        if len(verts) == 0:
            return None, False

        me = bpy.data.meshes.new(name)

        if len(mats) >= 1:
            mats_sorted = OrderedDict(sorted(mats.items(), key=lambda x: x[1]))
            for k in mats_sorted.keys():
                try:
                    bmat = self.materials[k]
                except KeyError as _e:
                    bmat = self.materials["Material"]
                me.materials.append(bmat)
                # if bmat.alpha < 1.0:
                #     alpha = True
                try:
                    if self.render_engine == 'CYCLES':
                        if 'Image Texture' in bmat.node_tree.nodes.keys():
                            uvs_used = True
                    else:
                        for ts in bmat.texture_slots:
                            if ts is not None and ts.texture_coords is not None:
                                uvs_used = True
                except AttributeError as _e:
                    uvs_used = False
        else:
            skp_log(f"WARNING: Object {name} has no material!")

        tri_faces = list(zip(*[iter(loops_vert_idx)] * 3))
        tri_face_count = len(tri_faces)

        loop_start = []
        i = 0
        for f in tri_faces:
            loop_start.append(i)
            i += len(f)

        loop_total = list(map(lambda f: len(f), tri_faces))

        me.vertices.add(len(verts))
        me.vertices.foreach_set("co", unpack_list(verts))

        me.loops.add(len(loops_vert_idx))
        me.loops.foreach_set("vertex_index", loops_vert_idx)

        me.polygons.add(tri_face_count)
        me.polygons.foreach_set("loop_start", loop_start)
        me.polygons.foreach_set("loop_total", loop_total)
        me.polygons.foreach_set("material_index", mat_index)
        me.polygons.foreach_set("use_smooth", smooth)

        if uvs_used:
            k, l = 0, 0
            me.uv_layers.new()
            for i in range(len(tri_faces)):
                for j in range(3):
                    uv_cordinates = (uv_list[i][l], uv_list[i][l + 1])
                    me.uv_layers[0].data[k].uv = Vector(uv_cordinates)
                    k += 1
                    if j != 2:
                        l += 2
                    else:
                        l = 0

        me.update(calc_edges=True)
        me.validate()
        self.component_meshes[mesh_key] = me, alpha

        return me, alpha

    def write_entities(self,
                       entities,
                       name,
                       parent_tranform,
                       default_material="Material",
                       etype=None):

        if etype == EntityType.component and (
                name, default_material) in self.component_skip:
            self.component_stats[(name,
                                  default_material)].append(parent_tranform)
            return

        me, alpha = self.write_mesh_data(entities=entities,
                                         name=name,
                                         default_material=default_material)

        if me:
            ob = bpy.data.objects.new(name, me)
            ob.matrix_world = parent_tranform
            if alpha > 0.01 and alpha < 1.0:
                ob.show_transparent = True
            me.update(calc_edges=True)
            bpy.context.collection.objects.link(ob)

        for group in entities.groups:
            if group.hidden:
                continue
            if self.layers_skip and group.layer in self.layers_skip:
                continue
            self.write_entities(group.entities,
                                "G-" + group_safe_name(group.name),
                                parent_tranform @ Matrix(group.transform),
                                default_material=inherent_default_mat(
                                    group.material, default_material),
                                etype=EntityType.group)

        for instance in entities.instances:
            if instance.hidden:
                continue
            if self.layers_skip and instance.layer in self.layers_skip:
                continue
            mat_name = inherent_default_mat(instance.material,
                                            default_material)
            cdef = self.skp_components.get(instance.definition.name)
            if cdef is None:
                    continue
            self.write_entities(cdef.entities,
                                cdef.name,
                                parent_tranform @ Matrix(instance.transform),
                                default_material=mat_name,
                                etype=EntityType.component)

    def instance_object_or_group(self, name, default_material):

        try:
            group = self.group_written[(name, default_material)]
            ob = bpy.data.objects.new(name=name, object_data=None)
            # ob.dupli_type = 'GROUP'
            # ob.dupli_group = group
            # ob.empty_draw_size = 0.01
            return ob
        except KeyError as _e:
            me, alpha = self.component_meshes[(name, default_material)]
            ob = bpy.data.objects.new(name, me)
            if alpha:
                ob.show_transparent = True
            me.update(calc_edges=True)
            return ob

    def conponent_def_as_group(self,
                               entities,
                               name,
                               parent_tranform,
                               default_material="Material",
                               etype=None,
                               group=None):

        if etype == EntityType.outer:
            if (name, default_material) in self.component_skip:
                return
            else:
                skp_log("Write instance definition as group {} {}".format(
                    group.name, default_material))
                self.component_skip[(name, default_material)] = True

        if etype == EntityType.component and (
                name, default_material) in self.component_skip:
            ob = self.instance_object_or_group(name, default_material)
            ob.matrix_world = parent_tranform
            # self.context.scene.objects.link(ob)
            self.context.collection.objects.link(ob)
            # ob.layers = 18 * [False] + [True] + [False]
            group.objects.link(ob)

            return

        else:
            me, alpha = self.write_mesh_data(entities=entities,
                                             name=name,
                                             default_material=default_material)

        if me:
            ob = bpy.data.objects.new(name, me)
            ob.matrix_world = parent_tranform
            if alpha:
                ob.show_transparent = True
            me.update(calc_edges=True)
            # self.context.scene.objects.link(ob)
            self.context.collection.objects.link(ob)
            # ob.layers = 18 * [False] + [True] + [False]
            group.objects.link(ob)

        for g in entities.groups:
            if self.layers_skip and g.layer in self.layers_skip:
                continue
            self.conponent_def_as_group(
                g.entities,
                "G-" + g.name,
                parent_tranform @ Matrix(g.transform),
                default_material=inherent_default_mat(g.material,
                                                      default_material),
                etype=EntityType.group,
                group=group)

        for instance in entities.instances:
            if self.layers_skip and instance.layer in self.layers_skip:
                continue
            cdef = self.skp_components.get(instance.definition.name)
            if cdef is None:
                    continue
            self.conponent_def_as_group(
                cdef.entities,
                cdef.name,
                parent_tranform @ Matrix(instance.transform),
                default_material=inherent_default_mat(instance.material,
                                                      default_material),
                etype=EntityType.component,
                group=group)

    def instance_group_dupli_vert(self,
                                  name,
                                  default_material,
                                  component_stats):

        def get_orientations(v):

            orientations = defaultdict(list)

            for transform in v:
                loc, rot, scale = Matrix(transform).decompose()
                scale = (scale[0], scale[1], scale[2])
                rot = (rot[0], rot[1], rot[2], rot[3])
                orientations[(scale, rot)].append((loc[0], loc[1], loc[2]))

            for key, locs in orientations.items():
                scale, rot = key
                yield scale, rot, locs

        for scale, rot, locs in get_orientations(
                component_stats[(name, default_material)]):
            verts = []
            main_loc = Vector(locs[0])
            for c in locs:
                verts.append(Vector(c) - main_loc)
            
            '''
            dme = bpy.data.meshes.new('DUPLI_' + name)
            dme.vertices.add(len(verts))
            dme.vertices.foreach_set("co", unpack_list(verts))
            dme.update(calc_edges=True)  # Update mesh with new data
            dme.validate()
            dob = bpy.data.objects.new("DUPLI_" + name, dme)
            dob.location = main_loc
            # dob.dupli_type = 'VERTS'
            '''
            dme = bpy.data.meshes.new('DUPLI_' + name)
            dme.from_pydata(verts,[],faces)

            dob = bpy.data.objects.new("DUPLI_" + name, dme)
            dob.location = main_loc

            ob = self.instance_object_or_group(name, default_material)
            ob.scale = scale
            ob.rotation_quaternion = Quaternion(
                (rot[0], rot[1], rot[2], rot[3]))
            ob.parent = dob

            self.context.collection.objects.link(ob)
            self.context.collection.objects.link(dob)
            skp_log(
                "Complex group {} {} instanced {} times, scale -> {}".format(
                    name, default_material, len(verts), scale))

        return

    def instance_group_dupli_face(self,
                                  name,
                                  default_material,
                                  component_stats):

        def get_orientations(v):

            orientations = defaultdict(list)

            for transform in v:
                _loc, _rot, scale = Matrix(transform).decompose()
                scale = (scale[0], scale[1], scale[2])
                orientations[scale].append(transform)

            for scale, transforms in orientations.items():
                yield scale, transforms

        for _scale, transforms in get_orientations(
                component_stats[(name, default_material)]):
            main_loc, _, real_scale = Matrix(transforms[0]).decompose()
            verts = []
            faces = []
            f_count = 0

            for c in transforms:
                l_loc, l_rot, _l_scale = Matrix(c).decompose()
                mat = Matrix.Translation(l_loc) @ l_rot.to_matrix().to_4x4()

                verts.append(Vector(
                    (mat @ Vector((-0.05, -0.05, 0, 1.0)))[0:3]) - main_loc)
                verts.append(Vector(
                    (mat @ Vector((0.05, -0.05, 0, 1.0)))[0:3]) - main_loc)
                verts.append(Vector(
                    (mat @ Vector((0.05, 0.05, 0, 1.0)))[0:3]) - main_loc)
                verts.append(Vector(
                    (mat @ Vector((-0.05, 0.05, 0, 1.0)))[0:3]) - main_loc)

                faces.append(
                    (f_count + 0, f_count + 1, f_count + 2, f_count + 3))

                f_count += 4

            '''
            dme = bpy.data.meshes.new('DUPLI_' + name)
            dme.vertices.add(len(verts))
            dme.vertices.foreach_set("co", unpack_list(verts))

            # dme.loop_triangles.add(f_count / 4)
            dme.loop_triangles.foreach_set("vertices_raw", unpack_face_list(faces))
            dme.update(calc_edges=True)  # Update mesh with new data
            dme.validate()
            dob = bpy.data.objects.new("DUPLI_" + name, dme)
            # dob.dupli_type = 'FACES'
            dob.location = main_loc
            #dob.use_dupli_faces_scale = True
            #dob.dupli_faces_scale = 10
            '''

            dme = bpy.data.meshes.new('DUPLI_' + name)
            dme.from_pydata(verts,[],faces)

            dob = bpy.data.objects.new("DUPLI_" + name, dme)
            dob.location = main_loc

            ob = self.instance_object_or_group(name, default_material)
            ob.scale = real_scale
            ob.parent = dob
            self.context.collection.objects.link(ob)
            self.context.collection.objects.link(dob)
            skp_log("Complex group {} {} instanced {} times".format(
                name, default_material, f_count / 4))
        return

    def write_camera(self,
                     camera,
                     name="Last View"):
        skp_log(f"Writing camera: {name}")
        pos, target, up = camera.GetOrientation()
        bpy.ops.object.add(type='CAMERA', location=pos)
        ob = self.context.object
        ob.name = "Cam: " + name
        z = (Vector(pos) - Vector(target))
        x = Vector(up).cross(z)
        y = z.cross(x)
        x.normalize()
        y.normalize()
        z.normalize()
        ob.matrix_world.col[0] = x.resized(4)
        ob.matrix_world.col[1] = y.resized(4)
        ob.matrix_world.col[2] = z.resized(4)
        cam = ob.data
        aspect_ratio = camera.aspect_ratio
        fov = camera.fov
        if aspect_ratio == False:
            skp_log(f"Cam: '{name}' uses dynamic/screen aspect ratio.")
            aspect_ratio = self.aspect_ratio
        if fov == False:
            skp_log(f"Cam: '{name}' is in Orthographic Mode.")
            cam.type = 'ORTHO'
        #cam.ortho_scale = 3.0
        else:
            cam.angle = (math.pi * fov / 180) * aspect_ratio
        cam.clip_end = self.prefs.camera_far_plane
        cam.name = "Cam: " + name
        return cam.name
    
    def FenceCollection(self):
        collection = bpy.data.collections.get("SKP Master")
        if collection is not None:
            objects_in_collection = collection.objects
            kh_objects = [obj for obj in objects_in_collection if obj.name.lower() ==("g-f") or (obj.name.lower().startswith("g-f") and obj.name.lower()[len("g-f"):].isdigit())]
            if not kh_objects:
                return {'CANCELLED'} 
             
        fence_group = bpy.data.collections.get("Fence Group")
        if fence_group:
            fence_group.name = "OLD-" + fence_group.name
            fence_group.hide_viewport = True
            fence_group.hide_render = True
        
        fence_group = bpy.data.collections.new("Fence Group")
        bpy.context.scene.collection.children.link(fence_group)

        front_collection = bpy.data.collections.get("Front")
        if front_collection:
            front_collection.name = "OLD-" + front_collection.name
        
        front_collection = bpy.data.collections.new("Front")
        fence_group.children.link(front_collection)
    
        Right_collection = bpy.data.collections.get("Right")
        if Right_collection:
            Right_collection.name = "OLD-" + Right_collection.name
        
        Right_collection = bpy.data.collections.new("Right")
        fence_group.children.link(Right_collection)    
                    
        Left_collection = bpy.data.collections.get("Left")
        if Left_collection:
            Left_collection.name = "OLD-" + Left_collection.name
        
        Left_collection = bpy.data.collections.new("Left")
        fence_group.children.link(Left_collection)
                    
        Back_collection = bpy.data.collections.get("Back")
        if Back_collection:
            Back_collection.name = "OLD-" + Back_collection.name
       
        Back_collection = bpy.data.collections.new("Back")
        fence_group.children.link(Back_collection)
              
        collection = bpy.data.collections.get("SKP Master")
        
        for obj in collection.objects:
            if obj.name.lower() ==("g-f") or (obj.name.lower().startswith("g-f") and obj.name.lower()[len("g-f"):].isdigit()):
            #if obj.name.startswith("G-F"):
                obj.users_collection[0].objects.unlink(obj)
                bpy.data.collections["Front"].objects.link(obj)
                obj.name = obj.name.lower().replace("g-", "")
            if obj.name.lower() ==("g-r") or (obj.name.lower().startswith("g-r") and obj.name.lower()[len("g-r"):].isdigit()):   
            #if obj.name.startswith("G-R"):
                obj.users_collection[0].objects.unlink(obj)
                bpy.data.collections["Right"].objects.link(obj)
                obj.name = obj.name.lower().replace("g-", "")
            if obj.name.lower() ==("g-b") or (obj.name.lower().startswith("g-b") and obj.name.lower()[len("g-b"):].isdigit()):   
            #if obj.name.startswith("G-B","G-b"):
                obj.users_collection[0].objects.unlink(obj)
                bpy.data.collections["Back"].objects.link(obj)
                obj.name = obj.name.lower().replace("g-", "")
            if obj.name.lower() ==("g-l") or (obj.name.lower().startswith("g-l") and obj.name.lower()[len("g-l"):].isdigit()):   
            #if obj.name.startswith("G-L"):
                obj.users_collection[0].objects.unlink(obj)
                bpy.data.collections["Left"].objects.link(obj)
                obj.name = obj.name.lower().replace("g-", "")
                
        return {'FINISHED'}
 
  

class SceneExporter():

    def __init__(self):

        self.filepath = '/tmp/untitled.skp'

    def set_filename(self, filename):

        self.filepath = filename
        self.basepath, self.skp_filename = os.path.split(self.filepath)

        return self

    def save(self, context, **options):

        skp_log(f'Finished exporting: {self.filepath}')

        return {'FINISHED'}


class ImportSKP_k(Operator, ImportHelper):
    """Load Sketchup (SKP) file"""

    bl_idname = "import_scene.skp_k"
    bl_label = "Import SKP"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".skp"

    filter_glob: StringProperty(
        default="*.skp",
        options={'HIDDEN'},
    )

    import_camera: BoolProperty(
        name="Last View In SketchUp As Camera View",
        description="Import last saved view in SketchUp as a Blender Camera.",
        default=False
    )

    reuse_material: BoolProperty(
        name="Use Existing Materials",
        description="Doesn't copy material IDs already in the Blender Scene.",
        default=True
    )

    max_instance: IntProperty(
        name="Threshold :",
        default=1000
    )

    dedub_type: EnumProperty(
        name="Instancing Type :",
        items=(('FACE', "Faces", ""),
               ('VERTEX', "Verts", ""),),
        default='FACE',
    )

    dedub_only: BoolProperty(
        name="Groups Only",
        description="Import instanciated groups only.",
        default=False
    )

    scenes_as_camera: BoolProperty(
        name="Scene(s) As Camera(s)",
        description="Import SketchUp Scenes As Blender Camera.",
        default=False
    )

    import_scene: StringProperty(
        name="Import A Scene :",
        description="Import a specific Sketchup Scene",
        default=""
    )

    reuse_existing_groups: BoolProperty(
        name="Reuse Groups",
        description="Use existing Blender groups to instance componenets with.",
        default=False
    )

    render_engine: EnumProperty(
        name="Default Shaders In :",
        items=(('CYCLES', "Cycles", ""),
               #    ('BLENDER_RENDER', "Blender Render", "")
               ),
        default='CYCLES'
    )

    def execute(self, context):

        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        
        # بدء نافذة التقدم للاستيراد
        progress_win = start_import_progress()
        progress_win.log_message("Starting SketchUp import...")
        progress_win.update_progress(0, "Loading file...")

        return SceneImporter().set_filename(keywords['filepath']).load(
            context, **keywords)

    def draw(self, context):

        layout = self.layout
        layout.label(text="- Primary Import Options -")
        row = layout.row()
        row.prop(self, "scenes_as_camera")
        row = layout.row()
        row.prop(self, "import_camera")
        row = layout.row()
        row.prop(self, "reuse_material")
        row = layout.row()
        row.prop(self, "dedub_only")
        row = layout.row()
        row.prop(self, "reuse_existing_groups")
        col = layout.column()
        col.label(text="- Instanciate When Similar Objects Are Over -")
        split = col.split(factor=0.5)
        col = split.column()
        col.prop(self, "max_instance")
        row = layout.row()
        row.use_property_split = True
        row.prop(self, "dedub_type")
        row = layout.row()
        row.use_property_split = True
        row.prop(self, "import_scene")
        row = layout.row()
        row.use_property_split = True
        row.prop(self, "render_engine")

#update
class ImportSKPupdate(Operator, ImportHelper):
    """ Reload Sketchup file and Update"""
    bl_idname = "import_scene_update.skp"
    bl_label = "Update SKP"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".skp"
    filter_glob: StringProperty(
        default="*.skp",
        options={'HIDDEN'},
    )

    import_camera: BoolProperty(
        name="Last View In SketchUp As Camera View",
        description="Import last saved view in SketchUp as a Blender Camera.",
        default=False
    )

    reuse_material: BoolProperty(
        name="Use Existing Materials",
        description="Doesn't copy material IDs already in the Blender Scene.",
        default=True
    )

    max_instance: IntProperty(
        name="Threshold :",
        default=1000
    )

    dedub_type: EnumProperty(
        name="Instancing Type :",
        items=(('FACE', "Faces", ""),
               ('VERTEX', "Verts", ""),),
        default='FACE',
    )

    dedub_only: BoolProperty(
        name="Groups Only",
        description="Import instanciated groups only.",
        default=False
    )

    scenes_as_camera: BoolProperty(
        name="Scene(s) As Camera(s)",
        description="Import SketchUp Scenes As Blender Camera.",
        default=False
    )

    import_scene: StringProperty(
        name="Import A Scene :",
        description="Import a specific Sketchup Scene",
        default=""
    )

    reuse_existing_groups: BoolProperty(
        name="Reuse Groups",
        description="Use existing Blender groups to instance componenets with.",
        default=False
    )

    render_engine: EnumProperty(
        name="Default Shaders In :",
        items=(('CYCLES', "Cycles", ""),
               #    ('BLENDER_RENDER', "Blender Render", "")
               ),
        default='CYCLES'
    )

    def execute(self, context):
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode"))
        
        # بدء نافذة التقدم للتحديث
        progress_win = start_import_progress()
        progress_win.log_message("Starting SketchUp update...")
        progress_win.update_progress(0, "Loading file...")
        
        return SceneImporterupdate().set_filename(keywords['filepath']).load(
            context, **keywords)

    def draw(self, context):

        layout = self.layout
        layout.label(text="- Primary Import Options -")
        row = layout.row()
        row.prop(self, "scenes_as_camera")
        row = layout.row()
        row.prop(self, "import_camera")
        row = layout.row()
        row.prop(self, "reuse_material")
        row = layout.row()
        row.prop(self, "dedub_only")
        row = layout.row()
        row.prop(self, "reuse_existing_groups")
        col = layout.column()
        col.label(text="- Instanciate When Similar Objects Are Over -")
        split = col.split(factor=0.5)
        col = split.column()
        col.prop(self, "max_instance")
        row = layout.row()
        row.use_property_split = True
        row.prop(self, "dedub_type")
        row = layout.row()
        row.use_property_split = True
        row.prop(self, "import_scene")
        row = layout.row()
        row.use_property_split = True
        row.prop(self, "render_engine")


def menu_func_import(self, context):
    self.layout.operator(ImportSKP_k.bl_idname, text="KH-Import Sketchup (.skp)")
def menu_func_import(self, context):
    self.layout.operator(ImportSKPupdate.bl_idname, text="KH-Update Sketchup(.skp)")


            
# New File Setup---------------------------------------------------------------------------------------------------------------- 
                                           
from bpy.props import IntProperty
import ctypes 

def join_by_data_users(collection_name):
    bpy.ops.object.select_all(action='DESELECT')
    skp_collection = bpy.data.collections.get(collection_name)
    selected_objects = []
    for obj in skp_collection.objects:
        if hasattr(obj.data, 'users') and hasattr(obj.data, 'materials') and obj.data.users > 50 and obj.data.users < 100:
            selected_objects.append(obj)

    if selected_objects:
        bpy.context.view_layer.objects.active = selected_objects[0]
        for obj in selected_objects:
            obj.select_set(True)
        bpy.ops.object.join()
        
           
def join_by_material_Higher_than_10(collection_name):
    skp_collection = bpy.data.collections.get(collection_name)
    objects_to_join = {}
    for obj in skp_collection.objects:
        if obj.type == 'MESH' and obj.data.materials and obj.data.users > 1 and obj.data.users < 10:
            material_name = obj.data.materials[0].name
            objects_to_join.setdefault(material_name, []).append(obj)
        
    for object_list in objects_to_join.values():
        if len(object_list) > 1:
            bpy.ops.object.select_all(action='DESELECT')                                 
            for obj in object_list:
                obj.select_set(True)                                       
            bpy.context.view_layer.objects.active = object_list[-1]
            bpy.ops.object.join()
        

def join_by_material_Higher_than_30(collection_name):
    skp_collection = bpy.data.collections.get(collection_name)
    objects_to_join = {}
    for obj in skp_collection.objects:
        if obj.type == 'MESH' and obj.data.materials and obj.data.users > 10 and obj.data.users < 30:
            material_name = obj.data.materials[0].name
            objects_to_join.setdefault(material_name, []).append(obj)
        
    for object_list in objects_to_join.values():
        if len(object_list) > 1:
            bpy.ops.object.select_all(action='DESELECT')                                 
            for obj in object_list:
                obj.select_set(True)                                       
            bpy.context.view_layer.objects.active = object_list[-1]
            bpy.ops.object.join()


def join_by_material_Higher_than_50(collection_name):
    skp_collection = bpy.data.collections.get(collection_name)
    objects_to_join = {}
    for obj in skp_collection.objects:
        if obj.type == 'MESH' and obj.data.materials and obj.data.users > 30 and obj.data.users < 50:
            material_name = obj.data.materials[0].name
            objects_to_join.setdefault(material_name, []).append(obj)
        
    for object_list in objects_to_join.values():
        if len(object_list) > 1:
            bpy.ops.object.select_all(action='DESELECT')                                 
            for obj in object_list:
                obj.select_set(True)                                       
            bpy.context.view_layer.objects.active = object_list[-1]
            bpy.ops.object.join()
             

def join_by_material_Higher_than_all(collection_name):
    skp_collection = bpy.data.collections.get(collection_name)
    objects_to_join = {}
    for obj in skp_collection.objects:
        if obj.type == 'MESH' and obj.data.materials and obj.data.users > 1 :#and obj.data.users < 201
            material_name = obj.data.materials[0].name
            objects_to_join.setdefault(material_name, []).append(obj)
        
    for object_list in objects_to_join.values():
        if len(object_list) > 1:
            bpy.ops.object.select_all(action='DESELECT')                                 
            for obj in object_list:
                obj.select_set(True)                                       
            bpy.context.view_layer.objects.active = object_list[-1]
            bpy.ops.object.join()
               
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def separate_by_MATERIAL(collection_name):
    bpy.ops.object.select_all(action='DESELECT')
    skp_collection = bpy.data.collections.get(collection_name)
    mesh_objects_in_collection = [obj for obj in skp_collection.objects if obj.type == 'MESH']
    if mesh_objects_in_collection:
        bpy.context.view_layer.objects.active = None
        selected_objects = []
        for obj in skp_collection.objects:
            if obj.data and hasattr(obj.data, "materials") and len(obj.data.materials) > 1  and len(obj.data.materials) < 10:
                obj.select_set(True)
                selected_objects.append(obj)
        if selected_objects:
            bpy.context.view_layer.objects.active = selected_objects[0]
            #if bpy.context.active_object.data.materials and len(bpy.context.active_object.data.materials) > 1:
                #bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.separate(type='MATERIAL')
            bpy.ops.object.editmode_toggle()
                        
                                            
def separate_by_MATERIAL10(collection_name):
    bpy.ops.object.select_all(action='DESELECT')
    skp_collection = bpy.data.collections.get(collection_name)
    mesh_objects_in_collection = [obj for obj in skp_collection.objects if obj.type == 'MESH']
    if mesh_objects_in_collection:
        bpy.context.view_layer.objects.active = None
        selected_objects = []
        for obj in skp_collection.objects:
            if obj.data and hasattr(obj.data, "materials") and len(obj.data.materials) > 9 : #and len(obj.data.materials) < 20
                obj.select_set(True)
                selected_objects.append(obj)
        if selected_objects:
            bpy.context.view_layer.objects.active = selected_objects[0]
            # if bpy.context.active_object.data.materials and len(bpy.context.active_object.data.materials) > 1:
            #     bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.separate(type='MATERIAL')
            bpy.ops.object.editmode_toggle()
                    

def separate_by_MATERIAL20(collection_name):
    bpy.ops.object.select_all(action='DESELECT')
    skp_collection = bpy.data.collections.get(collection_name)
    if skp_collection:
        mesh_objects_in_collection = [obj for obj in skp_collection.objects if obj.type == 'MESH']
        if mesh_objects_in_collection:
            bpy.context.view_layer.objects.active = None
            selected_objects = []
            for obj in skp_collection.objects:
                if obj.data and hasattr(obj.data, "materials") and len(obj.data.materials) > 19 and len(obj.data.materials) < 40:
                    obj.select_set(True)
                    selected_objects.append(obj)
            if selected_objects:
                bpy.context.view_layer.objects.active = selected_objects[0]
                if bpy.context.active_object.data.materials and len(bpy.context.active_object.data.materials) > 1:
                    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.separate(type='MATERIAL')
                    bpy.ops.object.editmode_toggle()
                        
                         
def separate_by_MATERIAL40(collection_name):
    bpy.ops.object.select_all(action='DESELECT')
    skp_collection = bpy.data.collections.get(collection_name)
    if skp_collection:
        mesh_objects_in_collection = [obj for obj in skp_collection.objects if obj.type == 'MESH']
        if mesh_objects_in_collection:
            bpy.context.view_layer.objects.active = None
            selected_objects = []
            for obj in skp_collection.objects:
                if obj.data and hasattr(obj.data, "materials") and len(obj.data.materials) > 39:
                    obj.select_set(True)
                    selected_objects.append(obj)
            if selected_objects:
                bpy.context.view_layer.objects.active = selected_objects[0]
                if bpy.context.active_object.data.materials and len(bpy.context.active_object.data.materials) > 1:
                    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.separate(type='MATERIAL')
                    bpy.ops.object.editmode_toggle()
                                                
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                       
def dissolve_limited(collection_name):
    bpy.ops.object.select_all(action='DESELECT')
    collection = bpy.data.collections.get(collection_name)
    if collection:
        for obj in (obj for obj in collection.objects if obj.type == 'MESH' and len(obj.data.polygons) < 7000 and obj.data.users == 1):
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            
        if bpy.context.active_object and bpy.context.active_object.type == 'MESH':
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.dissolve_limited(angle_limit=0.001)
            bpy.ops.object.editmode_toggle()
            
            
def join_by_material(collection_name):
    skp_collection = bpy.data.collections.get(collection_name)
    objects_to_join = {}
    for obj in skp_collection.objects:
        if obj.type == 'MESH' and obj.data.materials and obj.data.users == 1:
            material_name = obj.data.materials[0].name
            objects_to_join.setdefault(material_name, []).append(obj)
        
    for object_list in objects_to_join.values():
        if len(object_list) > 1:
            bpy.ops.object.select_all(action='DESELECT')                                 
            for obj in object_list:
                obj.select_set(True)                                       
            bpy.context.view_layer.objects.active = object_list[-1]
            bpy.ops.object.join()
        

def transform_apply_origin_set(collection_name):
    bpy.ops.object.select_all(action='DESELECT')
    collection = bpy.data.collections.get(collection_name)
    if collection:
        for obj in collection.objects:
            if obj.type == 'MESH' and obj.data.users == 1:
                obj.select_set(True)
            
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        bpy.ops.object.select_all(action='DESELECT')
        print(f"transform_apply / origin_set")

def Sketchup_Fix_UV (collection_name):
    bpy.ops.object.select_all(action='DESELECT')
    collection = bpy.data.collections.get(collection_name)
    if collection:
        mesh_objects = [obj for obj in collection.objects if obj.type == 'MESH']
        for obj in mesh_objects:
            has_tex_image = False
            for material_slot in obj.material_slots:
                for node in material_slot.material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE':
                        has_tex_image = True
                        break
                    
            if not has_tex_image:
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
            
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.cube_project(cube_size=3)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        print(f"Fix UV")
        for obj in mesh_objects:
            obj.select_set(True)
            
def remove_EMPTY(collection_name):
    collection = bpy.data.collections.get(collection_name)
    if collection:
        for obj in collection.objects:
            if obj.type == 'EMPTY':
                bpy.data.objects.remove(obj, do_unlink=True)
                
                
def skp_to_Master():            
    new_collection_name = "skp Master"
    selected_collection = bpy.data.collections.get("skp")
    existing_collection = bpy.data.collections.get("SKP Master")
    if existing_collection:
        print("SKP Master collection already exists. Rename process canceled.")
    else:
        if selected_collection:
            selected_collection.name = new_collection_name
        
        bpy.ops.outliner.orphans_purge(do_recursive=True)
        
        
def obj_name_to_material_name (collection_name):       
    collection = bpy.data.collections.get(collection_name)
    if collection:
        objects_in_collection = [obj for obj in collection.objects if obj.type == 'MESH']
        for obj in objects_in_collection:
            material = None
            if obj.data.materials:
                material = obj.data.materials[0]
            else:
                print(f"Object '{obj.name}' in collection '{collection_name}' has no materials.")
                continue
            if material:
                obj.name = material.name
            if material.name in obj.data.materials:
                obj.data.name = material.name
   
 
def Material_diffuse_color():        
    material_name = "Material"  
    for material in bpy.data.materials:
        if material.name == material_name and hasattr(material, 'diffuse_color'):
            material.diffuse_color = (1, 1, 1, 1) 
        
    materials = bpy.data.materials
    for material in materials:
        if material.diffuse_color[3] != 1.0:
            material.diffuse_color[0] = 0.5
            material.diffuse_color[1] = 0.7
            material.diffuse_color[2] = 1
            #material.diffuse_color[3] = 0.5
        

def skp_Master_to_SKP_Master(): 
    new_collection_name = "SKP Master"
    selected_collection = bpy.data.collections.get("skp Master")
    existing_collection = bpy.data.collections.get(new_collection_name)
    if existing_collection:
        print("SKP Master collection already exists. Rename process canceled.")
    else:
        if selected_collection:
            selected_collection.name = new_collection_name

def skp_name_to_SKP():           
    new_collection_name = "SKP"
    selected_collection = bpy.data.collections.get("skp")
    existing_collection = bpy.data.collections.get(new_collection_name)
    if existing_collection:
        print("SKP Master collection already exists. Rename process canceled.")
    else:
        if selected_collection:
            selected_collection.name = new_collection_name



class SKPN(bpy.types.Operator):
    bl_idname = "object.skp_addonn"
    bl_label =  "Sketchup File NEW" 
    bl_description  = "Join by material\nSeparate by MATERIAL\nDissolve_limited\nTransform_apply / Origin_set\nSketchup Fix UV\n"
    
    _steps = [
        ("Join materials (>10)", join_by_material_Higher_than_10),
        ("Join materials (>30)", join_by_material_Higher_than_30),
        ("Join materials (>50)", join_by_material_Higher_than_50),
        
        ("Join all materials", join_by_material_Higher_than_all),
        ("Separate by material", separate_by_MATERIAL),
        ("Separate by material (10)", separate_by_MATERIAL10),
        ("Dissolve limited", dissolve_limited),
        ("Join by material", join_by_material),
        ("Apply transforms", transform_apply_origin_set),
        ("Fix UV", Sketchup_Fix_UV),
        ("Remove empties", remove_EMPTY),
        
        # ("skp_to_Master", skp_to_Master),
        # ("obj_name_to_material_name", obj_name_to_material_name),
        # ("Material_diffuse_color", Material_diffuse_color),
        # ("skp_Master_to_SKP_Master", skp_Master_to_SKP_Master),
        # ("skp_name_to_SKP", skp_name_to_SKP),
    ]
    _current_step = 0
    _total_time = 0.0
    _progress_window = None

    def execute(self, context):
        if "skp" in bpy.data.collections:
            all_time = time.time()
            context.scene.loading_progress = 0
            self._current_step = 0
            self._total_time = 0.0 
            
            # بدء نافذة التقدم للتجهيز
            self._progress_window = start_setup_progress(len(self._steps))
            self._progress_window.log_message("Starting file setup...")
            self._progress_window.update_progress(0, "Preparing...")
            
            bpy.app.timers.register(self.process_step)            
            return {'RUNNING_MODAL'}
    
    def process_step(self):
        context = bpy.context
        
        # التحقق من إلغاء العملية
        if self._progress_window and self._progress_window.is_cancelled():
            self._progress_window.log_message("Setup cancelled by user")
            self._progress_window.show_finished("Setup cancelled!")
            self._progress_window = None
            context.scene.loading_progress = 0
            return None  # إيقاف المؤقت
        
        if self._current_step < len(self._steps):
            progress_percent = int((self._current_step) / len(self._steps) * 100)
            context.scene.loading_progress = progress_percent
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            
            # تنفيذ الخطوة بعد تحديث شريط التحميل
            step_name, step_func = self._steps[self._current_step]
            
            # تحديث نافذة التقدم
            if self._progress_window:
                self._progress_window.update_progress(progress_percent, f"Processing: {step_name}")
                self._progress_window.log_message(f"Starting: {step_name}")
            
            start_time = time.time()
            step_func("skp")
            elapsed_time = time.time() - start_time
            self._total_time += elapsed_time 
            print(f"{step_name} {elapsed_time:.2f} seconds.")
            
            # تحديث نافذة التقدم بعد اكتمال الخطوة
            if self._progress_window:
                self._progress_window.log_message(f"Completed: {step_name} ({elapsed_time:.2f} sec)")
            
            self._current_step += 1
           
            return 0.1  # عودة المؤقت بعد 0.1 ثانية لمتابعة الخطوات
        else:
            context.scene.loading_progress = 100
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            print("")
            print(f"Total Time for all steps: {self._total_time:.2f} seconds.")
            print("")
            
            # إظهار رسالة الانتهاء في نافذة التقدم
            if self._progress_window:
                self._progress_window.update_progress(100, "Setup completed!")
                self._progress_window.log_message(f"Total time: {self._total_time:.2f} sec")
                self._progress_window.show_finished("SKP file imported and setup successfully!")
                self._progress_window = None
            
            bpy.app.timers.register(self.reset_progress)
            return None  # إيقاف المؤقت
       
    def reset_progress(self):
        bpy.context.scene.loading_progress = 0
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        skp_to_Master()
        obj_name_to_material_name("skp Master")
        Material_diffuse_color()
        skp_Master_to_SKP_Master()
        skp_name_to_SKP()
        if bpy.data.filepath:
            bpy.ops.wm.save_mainfile()
        return None  # إيقاف المؤقت

        
#Update-------------------------------------------------------------------------------------------------------------------

def assign_materials():
    if 'skp_old' in bpy.data.collections and 'SKP Master' in bpy.data.collections:
        skp_old_collection = bpy.data.collections['skp_old']
        skp_collection = bpy.data.collections['SKP Master']
        for obj_old in skp_old_collection.objects:
            obj_name = obj_old.data.name
            obj_name_without_suffix = obj_name.split('.old')[0]  # Remove '.001' suffix
            if obj_name_without_suffix in bpy.data.objects:
                obj = bpy.data.objects[obj_name_without_suffix]
                if obj.data is not None and obj.type == 'MESH':
                    obj.data.materials.clear()
                    for slot in obj_old.material_slots:
                        if slot.material is not None:  # Check if the material slot is not None
                            obj.data.materials.append(slot.material)
                            obj.name = obj_old.name[:-4]

def copy_uv():
    collection = bpy.data.collections.get("skp_old")
    if collection:
        collection.hide_viewport = False
        collection.hide_render = False
        objects_in_collection = collection.objects
        
        for obj in objects_in_collection:
            obj.hide_viewport = False
            obj.hide_render = False

    for skp_old_obj in bpy.data.collections['skp_old'].all_objects:
        if skp_old_obj.type == 'MESH':
            skp_old_name = skp_old_obj.data.name[:-4] if skp_old_obj.data.name.endswith(".old") else skp_old_obj.data.name
            skp_master_obj = bpy.data.objects.get(skp_old_name)
            if skp_master_obj is not None and skp_master_obj.type == 'MESH':
                
                for mat_slot in skp_master_obj.material_slots:
                    material = mat_slot.material
                    if material is not None:
                        for node in material.node_tree.nodes:
                            if node.type == 'TEX_IMAGE':
                                bpy.context.view_layer.objects.active = skp_master_obj
                                bpy.ops.object.select_all(action='DESELECT')
                                skp_old_obj.select_set(True)
                                skp_master_obj.select_set(True)
                                bpy.context.view_layer.objects.active = skp_old_obj
                                bpy.ops.object.join_uvs()

def copy_modifier():
    for skp_old_obj in bpy.data.collections['skp_old'].all_objects:
        if skp_old_obj.type == 'MESH':
            skp_old_name = skp_old_obj.data.name[:-4] if skp_old_obj.data.name.endswith(".old") else skp_old_obj.data.name
            skp_master_obj = bpy.data.objects.get(skp_old_name)
            if skp_master_obj is not None and skp_master_obj.type == 'MESH':
                modifiers = skp_old_obj.modifiers
                if modifiers:
                    for modifier in modifiers:
                        new_modifier = skp_master_obj.modifiers.new(name=modifier.name, type=modifier.type)
                        # نسخ جميع الخصائص من الموديفاير القديم إلى الجديد
                        for attr in dir(modifier):
                            if not attr.startswith("_") and hasattr(new_modifier, attr):
                                try:
                                    setattr(new_modifier, attr, getattr(modifier, attr))
                                except AttributeError:
                                    print(f"Ignoring read-only attribute '{attr}' for modifier '{modifier.name}'")
                
                # نسخ نظام الجسيمات إذا وجد
                particle_systems = skp_old_obj.particle_systems
                if particle_systems:
                    for ps in particle_systems:
                        #new_particle_system = skp_master_obj.modifiers.new(name=ps.name, type='PARTICLE_SYSTEM')
                        # الحصول على نظام الجسيمات من الموديفاير
                        new_psys = skp_master_obj.particle_systems[-1]
                        new_psys.settings = ps.settings
                        new_psys.name = ps.name
                        
                print("copy modifier Done")
                        
                                    
          
def hide_skp_old_remove():
    bpy.ops.object.select_all(action='DESELECT')
    collection = bpy.data.collections.get("skp_old")
    if collection:
        collection.hide_viewport = True
        collection.hide_render = True

    #DELET skp_old
    main_collection_name = "SKP File"
    sub_collection_name = "skp_old"
    if main_collection_name in bpy.data.collections:
        main_collection = bpy.data.collections[main_collection_name]
        if sub_collection_name in main_collection.children:
            remove_collection(sub_collection_name)

def remove_collection(collection_name):
    if collection_name in bpy.data.collections:
        bpy.data.collections.remove(bpy.data.collections[collection_name], do_unlink=True)
        bpy.ops.outliner.orphans_purge(do_recursive=True) 
                       
                    
class Update_File(bpy.types.Operator):
    bl_idname = "object.skp_update_file"
    bl_label =  "Sketchup File update"
    bl_description  = "Join by material\nSeparate by MATERIAL\nDissolve_limited\nTransform_apply / Origin_set\nSketchup Fix UV\nAssign materials\nCopy uv\n" 
    
    _steps = [
    ("Join materials (>10)", join_by_material_Higher_than_10),
    ("Join materials (>30)", join_by_material_Higher_than_30),
    ("Join materials (>50)", join_by_material_Higher_than_50),
    
    ("Join all materials", join_by_material_Higher_than_all),
    ("Separate by material", separate_by_MATERIAL),
    ("Separate by material (10)", separate_by_MATERIAL10),
    ("Dissolve limited", dissolve_limited),
    ("Join by material", join_by_material),
    ("Apply transforms", transform_apply_origin_set),
    ("Fix UV", Sketchup_Fix_UV),
    ("Remove empties", remove_EMPTY),
    
    # ("skp_to_Master", skp_to_Master),
    # ("obj_name_to_material_name", obj_name_to_material_name),
    # ("Material_diffuse_color", Material_diffuse_color),
    # ("skp_Master_to_SKP_Master", skp_Master_to_SKP_Master),
    # ("skp_name_to_SKP", skp_name_to_SKP),
]
    _current_step = 0
    _total_time = 0.0
    _progress_window = None
    
    def execute(self, context):
        skp_old_exists = False
        for collection in bpy.data.collections:
            if collection.name == "skp_old":
                skp_old_exists = True
                break
        if skp_old_exists:
            all_time = time.time()
            context.scene.loading_progress = 0
            self._current_step = 0
            self._total_time = 0.0 
            
            # بدء نافذة التقدم للتحديث
            self._progress_window = start_setup_progress(len(self._steps))
            self._progress_window.log_message("Starting file update...")
            self._progress_window.update_progress(0, "Preparing...")
            
            bpy.app.timers.register(self.process_step)           
            return {'RUNNING_MODAL'}
    
    def process_step(self):
        context = bpy.context
        
        # التحقق من إلغاء العملية
        if self._progress_window and self._progress_window.is_cancelled():
            self._progress_window.log_message("Update cancelled by user")
            self._progress_window.show_finished("Update cancelled!")
            self._progress_window = None
            context.scene.loading_progress = 0
            return None  # إيقاف المؤقت
        
        if self._current_step < len(self._steps):
            progress_percent = int((self._current_step) / len(self._steps) * 100)
            context.scene.loading_progress = progress_percent
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            
            # تنفيذ الخطوة بعد تحديث شريط التحميل
            step_name, step_func = self._steps[self._current_step]
            
            # تحديث نافذة التقدم
            if self._progress_window:
                self._progress_window.update_progress(progress_percent, f"Processing: {step_name}")
                self._progress_window.log_message(f"Starting: {step_name}")
            
            start_time = time.time()
            step_func("SKP Master")
            elapsed_time = time.time() - start_time
            self._total_time += elapsed_time 
            print(f"{step_name} {elapsed_time:.2f} seconds.")
            
            # تحديث نافذة التقدم بعد اكتمال الخطوة
            if self._progress_window:
                self._progress_window.log_message(f"Completed: {step_name} ({elapsed_time:.2f} sec)")
            
            self._current_step += 1
           
            return 0.1  # عودة المؤقت بعد 0.1 ثانية لمتابعة الخطوات
        else:
            context.scene.loading_progress = 100
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            print("")
            print(f"Total Time for all steps: {self._total_time:.2f} seconds.")
            print("")
            
            # إظهار رسالة الانتهاء في نافذة التقدم
            if self._progress_window:
                self._progress_window.update_progress(100, "Update completed!")
                self._progress_window.log_message(f"Total time: {self._total_time:.2f} sec")
                self._progress_window.show_finished("SKP file updated successfully!")
                self._progress_window = None
            
            bpy.app.timers.register(self.reset_progress)
            return None  # إيقاف المؤقت
       
    def reset_progress(self):
        obj_name_to_material_name ("SKP Master")                      
        Material_diffuse_color()
        assign_materials()
        copy_uv()
        copy_modifier()     
        hide_skp_old_remove()
        bpy.context.scene.loading_progress = 0
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        
        #return None  # إيقاف المؤقت 
        self.report({'INFO'}, "Update File Finished")
                
                
 #Explode Object---------------------------------------------------------------------------------------------------------
class Explode(bpy.types.Operator):
     bl_idname = "object.skp_explode"
     bl_label =  "Explode Object"
     bl_description  = "Explode Selected Object by LOOSE" 
 
     def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')  
                bpy.ops.mesh.separate(type='LOOSE')
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)  
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                bpy.ops.outliner.orphans_purge(do_recursive=True)
                
        return {'FINISHED'}       

# Merge By material----------------------------------------------------------------------------------------------------------------
class Merge(bpy.types.Operator):
     bl_idname = "object.skp_merge"
     bl_label =  "Merge By material"
     bl_description  = "Merge Selected objects By material" 
 
     def execute(self, context):
            for obj in bpy.context.selected_objects:
                if obj.type == 'MESH':
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.select_linked(type='MATERIAL')
                    bpy.ops.object.join()
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                    bpy.ops.outliner.orphans_purge(do_recursive=True)
                    def remove_numbers_from_object_name():
                        selected_object = bpy.context.active_object
                        if selected_object:
                            object_name = selected_object.name
                            if "." in object_name:
                                object_name = object_name.split(".")[0]
                                selected_object.name = object_name
                                selected_object.data.name = object_name
                    remove_numbers_from_object_name()
            return {'FINISHED'}       

# #Collection Setup ---------------------------------------------------------------------------------------------------------------           
class OBJECT_OT_JoinAndModifyOperator(bpy.types.Operator):
    bl_idname = "object.join_and_modify_operator"
    bl_label = "Collection Setup"
    bl_description  = "Select Collection\nJoin by material\nSeparate by MATERIAL\nDissolve_limited\nTransform_apply / Origin_set\nSketchup Fix UV"
    
    def execute(self, context):
        collection = bpy.context.view_layer.active_layer_collection.collection
        collection_name = bpy.context.view_layer.active_layer_collection.collection
        #join by material
        bpy.ops.object.select_all(action='DESELECT')
        skp_collection =  bpy.context.view_layer.active_layer_collection.collection
        if skp_collection:
            objects_to_join = {}
            for obj in skp_collection.objects:
                if obj.type == 'MESH' and obj.data.materials and obj.data.users > 1:
                    material_name = obj.data.materials[0].name
                    objects_to_join.setdefault(material_name, []).append(obj)
                
            for object_list in objects_to_join.values():
                if len(object_list) > 1:
                    bpy.ops.object.select_all(action='DESELECT')                                 
                    for obj in object_list:
                        obj.select_set(True)                                       
                    bpy.context.view_layer.objects.active = object_list[-1]
                    bpy.ops.object.join()
               

        
        bpy.ops.object.select_all(action='DESELECT')
        skp_collection =  bpy.context.view_layer.active_layer_collection.collection
        if skp_collection:
            mesh_objects_in_collection = [obj for obj in skp_collection.objects if obj.type == 'MESH']
            if mesh_objects_in_collection:
                bpy.context.view_layer.objects.active = None
                collection_name =  bpy.context.view_layer.active_layer_collection.collection
                collection = bpy.context.view_layer.active_layer_collection.collection
                if collection:
                    selected_objects = []
                    for obj in collection.objects:
                        if obj.data and hasattr(obj.data, "materials") and len(obj.data.materials) > 1:
                            obj.select_set(True)
                            selected_objects.append(obj)
                    if selected_objects:
                        bpy.context.view_layer.objects.active = selected_objects[0]
                        if bpy.context.active_object.data.materials and len(bpy.context.active_object.data.materials) > 1:
                            bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
                            bpy.ops.object.mode_set(mode='EDIT')
                            bpy.ops.mesh.select_all(action='SELECT')
                            bpy.ops.mesh.separate(type='MATERIAL')
                            bpy.ops.object.editmode_toggle()
                            bpy.ops.outliner.orphans_purge(do_recursive=True)
                        

        # dissolve_limited
        bpy.ops.object.select_all(action='DESELECT')
        collection_name =  bpy.context.view_layer.active_layer_collection.collection
        collection = bpy.context.view_layer.active_layer_collection.collection
        
        if collection :

            for obj in (obj for obj in collection.objects if obj.type == 'MESH' and len(obj.data.polygons) < 7000 and obj.data.users == 1):
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
            
            obj = context.object
            if obj:
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.dissolve_limited(angle_limit=0.001)
                bpy.ops.object.editmode_toggle()
            
        bpy.ops.outliner.orphans_purge(do_recursive=True)
            
        #join by material
        bpy.ops.object.select_all(action='DESELECT')
        skp_collection =  bpy.context.view_layer.active_layer_collection.collection
        if skp_collection:
            objects_to_join = {}
            for obj in skp_collection.objects:
                if obj.type == 'MESH' and obj.data.materials and obj.data.users == 1:
                    material_name = obj.data.materials[0].name
                    objects_to_join.setdefault(material_name, []).append(obj)
                
            
            for object_list in objects_to_join.values():
                if len(object_list) > 1:
                    bpy.ops.object.select_all(action='DESELECT')                                 
                    for obj in object_list:
                        obj.select_set(True)                                       
                    bpy.context.view_layer.objects.active = object_list[-1]
                    bpy.ops.object.join()
                
        
        # transform_apply / origin_set
        bpy.ops.object.select_all(action='DESELECT')
        collection_name =  bpy.context.view_layer.active_layer_collection.collection
        collection = bpy.context.view_layer.active_layer_collection.collection
        if collection:
            for obj in collection.objects:
                if obj.type == 'MESH' and obj.data.users == 1:
                    obj.select_set(True)
                
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            bpy.ops.object.select_all(action='DESELECT')
       
        
        #Sketchup Fix UV
        bpy.ops.object.select_all(action='DESELECT')
        collection_name =  bpy.context.view_layer.active_layer_collection.collection
        collection = bpy.context.view_layer.active_layer_collection.collection
        if collection:
            mesh_objects = [obj for obj in collection.objects if obj.type == 'MESH']
            for obj in mesh_objects:
                has_tex_image = False
                for material_slot in obj.material_slots:
                    for node in material_slot.material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            has_tex_image = True
                            break
                        
                if not has_tex_image:
                    bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)
                
        obj = context.object
        if obj:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.uv.cube_project(cube_size=3)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            for obj in mesh_objects:
                obj.select_set(True)
            

        # Material diffuse color = 1, 1, 1, 1
        material_name = "Material"  
        for material in bpy.data.materials:
            if material.name == material_name and hasattr(material, 'diffuse_color'):
                material.diffuse_color = (1, 1, 1, 1) 
            

        materials = bpy.data.materials
        for material in materials:
            if material.diffuse_color[3] != 1.0:
                material.diffuse_color[0] = 0.5
                material.diffuse_color[1] = 0.7
                material.diffuse_color[2] = 1
                #material.diffuse_color[3] = 0.5

        return {'FINISHED'}
    

#Objects Clean     
class OBJECT_OT_JoinAndModifyOperatorc(bpy.types.Operator):
    bl_idname = "object.join_and_modify_operatorc"
    bl_label = "Clean up Objects"
    bl_description = "Clean up selected Objects dissolve_limited 0.02"
    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.dissolve_limited(angle_limit=0.02)
                bpy.ops.object.editmode_toggle()
        return {'FINISHED'}
    

#Rivet  
class OBJECT_OT_RivetOperator(bpy.types.Operator):
    bl_idname = "object.rivet"
    bl_label = "Revit file Setup"
    bl_description = "Add collection(Revit)and Alpha 1 Metallic 1"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        collection_name = "Revit"
        scene = bpy.context.scene
        if collection_name in bpy.data.collections:
            selected_objects = bpy.context.selected_objects
            collection = bpy.data.collections[collection_name]
            for obj in selected_objects:
                for old_collection in obj.users_collection:
                    old_collection.objects.unlink(obj)
                collection.objects.link(obj)
        else:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)
            selected_objects = bpy.context.selected_objects
            for obj in selected_objects:
                for old_collection in obj.users_collection:
                    old_collection.objects.unlink(obj)
                collection.objects.link(obj)
            bpy.context.view_layer.objects.active = None
            bpy.context.selected_objects.clear()

        print("تم تنفيذ السكربت بنجاح.")
        selected_collection = bpy.data.collections.get("Revit")
        if selected_collection:
            for obj in selected_collection.objects:
                if obj.type == 'MESH':
                    for slot in obj.material_slots:
                        material = slot.material
                        if material and material.use_nodes:
                            principled_bsdf_node = material.node_tree.nodes.get("Principled BSDF")
                            if principled_bsdf_node:
                                principled_bsdf_node.inputs["Metallic"].default_value = 0
                                principled_bsdf_node.inputs["Alpha"].default_value = 1
        else:
            print("Collection 'Revit' not found.")
        current_collection = bpy.data.collections.get("Revit")
        if current_collection:
            for obj in current_collection.objects:
                if obj.type == 'MESH' and obj.data.materials:
                    for material_slot in obj.material_slots:
                        material = material_slot.material
                        if hasattr(material, 'diffuse_color'):
                            material.diffuse_color[3] = 1.0
                            material.metallic = 0

        else:
            print("لم يتم تحديد كولكشن في Outliner.")
        bpy.context.view_layer.update()

        return {'FINISHED'}
        


# fence     
#-----------------------------------------------------------------------------------------------------------------------------------
#KH-Collections
class FenceCollection(bpy.types.Operator):
    """Move selected objects to a collection called 'Fence Group'"""
    bl_idname = "object.fence_collection"
    bl_label = "KH-Collections"
    bl_description = "Add collection\n(3D Model, Homes, Road, Curtains,3D Light)"

    def execute(self, context):
        collections_names = ["3D Model", "Homes", "Road", "Curtains","3D Light"]
        scene = bpy.context.scene
        existing_collections = [collection.name for collection in bpy.data.collections]
        for name in collections_names:
            if name not in existing_collections:
                new_collection = bpy.data.collections.new(name)
                scene.collection.children.link(new_collection)
        
        return {'FINISHED'}
    
class FrontCollection(bpy.types.Operator):
    
    bl_idname = "object.front_collection"
    bl_label = "F"
    bl_description = "Add collection Fence to the scene"
    def execute(self, context):
        # Get all selected objects
        selected_objects = context.selected_objects
        # Get or create a collection with the name "Fence Group"
        fence_group = bpy.data.collections.get("Fence Group")
        if not fence_group:
            fence_group = bpy.data.collections.new("Fence Group")
            context.scene.collection.children.link(fence_group)
        # Get or create a sub-collection called "Front" within "Fence Group"
        front_collection = bpy.data.collections.get("Front")
        if not front_collection:
            front_collection = bpy.data.collections.new("Front")
            fence_group.children.link(front_collection)
        # Move all selected objects to the "Front" collection
        for obj in selected_objects:
            obj.users_collection[0].objects.unlink(obj)
            front_collection.objects.link(obj)
        
        # # قم بتعريف اسم الكولكشن المراد استثناءه
        # exception_collection_name = "Front"

        # for collection in bpy.data.collections:
        #     # التحقق مما إذا كان اسم الكولكشن يساوي الاسم المعين للاستثناء
        #     if collection.name == exception_collection_name:
        #         continue  # تجاهل هذا الكولكشن واستكمل البحث في الكولكشنات الأخرى

        #     for obj in collection.objects:
        #         if obj.name.lower() == "g-f" or (obj.name.lower().startswith("g-f") and obj.name.lower()[len("g-f"):].isdigit()):
        #             # فصل الكائن من المجموعة الحالية
        #             obj.users_collection[0].objects.unlink(obj)
        #             # إضافة الكائن إلى مجموعة "Front"
        #             bpy.data.collections[exception_collection_name].objects.link(obj)

        return {'FINISHED'}
    

class RightCollection(bpy.types.Operator):
    bl_idname = "object.right_collection"
    bl_label = "R"
    bl_description = "Add collection Fence to the scene"

    def execute(self, context):
        selected_objects = context.selected_objects
        fence_group = bpy.data.collections.get("Fence Group")
        if not fence_group:
            fence_group = bpy.data.collections.new("Fence Group")
            context.scene.collection.children.link(fence_group)
        front_collection = bpy.data.collections.get("Right")
        if not front_collection:
            front_collection = bpy.data.collections.new("Right")
            fence_group.children.link(front_collection)
        for obj in selected_objects:
            obj.users_collection[0].objects.unlink(obj)
            front_collection.objects.link(obj)
            
        # for collection in bpy.data.collections:
        #     for obj in collection.objects:
        #         if obj.name.lower() ==("g-r") or (obj.name.lower().startswith("g-r") and obj.name.lower()[len("g-r"):].isdigit()):
        #         #if obj.name.startswith("G-R"):
        #             # فصل الكائن من المجموعة الحالية
        #             obj.users_collection[0].objects.unlink(obj)
        #             # إضافة الكائن إلى مجموعة "Front"
        #             bpy.data.collections["Right"].objects.link(obj)

        return {'FINISHED'}

class LeftCollection(bpy.types.Operator):
    bl_idname = "object.left_collection"
    bl_label = "L"
    bl_description = "Add collection Fence to the scene"
    def execute(self, context):
        selected_objects = context.selected_objects
        fence_group = bpy.data.collections.get("Fence Group")
        if not fence_group:
            fence_group = bpy.data.collections.new("Fence Group")
            context.scene.collection.children.link(fence_group)
        front_collection = bpy.data.collections.get("Left")
        if not front_collection:
            front_collection = bpy.data.collections.new("Left")
            fence_group.children.link(front_collection)
        for obj in selected_objects:
            obj.users_collection[0].objects.unlink(obj)
            front_collection.objects.link(obj)
        
        # for collection in bpy.data.collections:
        #     for obj in collection.objects:
        #         if obj.name.lower() ==("g-l") or (obj.name.lower().startswith("g-l") and obj.name.lower()[len("g-l"):].isdigit()):
        #         #if obj.name.startswith("G-L"):
        #             # فصل الكائن من المجموعة الحالية
        #             obj.users_collection[0].objects.unlink(obj)
        #             # إضافة الكائن إلى مجموعة "Front"
        #             bpy.data.collections["Left"].objects.link(obj)
                    
        return {'FINISHED'}
    
class BackCollection(bpy.types.Operator):
    bl_idname = "object.back_collection"
    bl_label = "B"
    bl_description = "Add collection Fence to the scene"

    def execute(self, context):
        selected_objects = context.selected_objects
        fence_group = bpy.data.collections.get("Fence Group")
        if not fence_group:
            fence_group = bpy.data.collections.new("Fence Group")
            context.scene.collection.children.link(fence_group)
        front_collection = bpy.data.collections.get("Back")
        if not front_collection:
            front_collection = bpy.data.collections.new("Back")
            fence_group.children.link(front_collection)
        for obj in selected_objects:
            obj.users_collection[0].objects.unlink(obj)
            front_collection.objects.link(obj)
            
        # for collection in bpy.data.collections:
        #     for obj in collection.objects:
        #         if obj.name.lower() ==("g-b") or (obj.name.lower().startswith("g-b") and obj.name.lower()[len("g-b"):].isdigit()):
        #         #if obj.name.startswith("G-B"):
        #             # فصل الكائن من المجموعة الحالية
        #             obj.users_collection[0].objects.unlink(obj)
        #             # إضافة الكائن إلى مجموعة "Front"
        #             bpy.data.collections["Back"].objects.link(obj)

        return {'FINISHED'}


#Light Collection
class CollectionOperator(bpy.types.Operator):
    bl_idname = "object.add_collection_operator"
    bl_label = "Light"
    bl_description = "Add collections (Light )to the scene"

    option: bpy.props.EnumProperty(
        items=[
            ('LIGHTS', 'Light', 'Add Light collection'),
            ('CURTAINS', 'Curtains', 'Add Curtains collection'),
            ('3D', '3D', 'Add 3D collection')
        ]
    )

    def execute(self, context):
        if self.option == 'LIGHTS':
            light_collection = bpy.data.collections.new("Light")
            internal_collection = bpy.data.collections.new("Internal")
            spot_collection = bpy.data.collections.new("Spot")
            wall_collection = bpy.data.collections.new("Wall")
            floor_collection = bpy.data.collections.new("Floor")
            external_collection = bpy.data.collections.new("External")
            light_collection.children.link(internal_collection)
            light_collection.children.link(spot_collection)
            light_collection.children.link(wall_collection)
            light_collection.children.link(floor_collection)
            light_collection.children.link(external_collection)
            context.scene.collection.children.link(light_collection)
        elif self.option == 'CURTAINS':
            curtains_collection = bpy.data.collections.new("Curtains")
            context.scene.collection.children.link(curtains_collection)
        else:
            d_collection = bpy.data.collections.new("3D")
            context.scene.collection.children.link(d_collection)
        return {'FINISHED'}


#import folder////////////////////////////////////////////////////////
# وظيفة لاستيراد ملفات SketchUp من المجلد المحدد والمجلدات الفرعية
def import_skp_files(folder_path):
    if os.path.exists(folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith(".skp"):
                    file_path = os.path.join(root, file_name)
                    print(f"Importing {file_name} from {root}...")
                    bpy.ops.import_scene.skp_k(filepath=file_path)
        print("تم استيراد جميع الملفات.")
    else:
        print("المجلد غير موجود.")

# أوبيراتور لاستيراد ملفات SketchUp
class ImportSKPFolder(bpy.types.Operator):
    bl_idname = "import_skp.all_files"
    bl_label = "Import All SKP Files"

    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        import_skp_files(self.directory)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    
preview_collection1 = bpy.utils.previews.new()
preview_collection1.load("25.png", os.path.join(my_icons_dir, "25.png"), 'IMAGE')

preview_collection4 = bpy.utils.previews.new()
preview_collection4.load("9.png", os.path.join(my_icons_dir, "9.png"), 'IMAGE')

preview_collection5 = bpy.utils.previews.new()
preview_collection5.load("11.png", os.path.join(my_icons_dir, "11.png"), 'IMAGE')

preview_collection6 = bpy.utils.previews.new()
preview_collection6.load("10.png", os.path.join(my_icons_dir, "10.png"), 'IMAGE')

preview_collection7 = bpy.utils.previews.new()
preview_collection7.load("7.png", os.path.join(my_icons_dir, "7.png"), 'IMAGE')

#Sketchup File Manager
class CopyNameMaterialPanel(bpy.types.Panel):
    """Creates a panel in the 3D view UI"""
    bl_label = "Sketchup Manager"
    bl_idname = "OBJECT_PT_copy_name_material"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category  = 'KH-Tools'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # البحث عن الإضافة في المسارات المختلفة
        try:
            # محاولة البحث بالاسم الافتراضي
            KH = context.preferences.addons['KH-Tools'].preferences.KH_Sketchup == True
            return KH
        except KeyError:
            try:
                # محاولة البحث باسم المجلد الحالي
                KH = context.preferences.addons['kh_tools'].preferences.KH_Sketchup == True
                return KH
            except KeyError:
                try:
                    # البحث في جميع الإضافات المحملة
                    for addon_name in context.preferences.addons.keys():
                        if 'kh' in addon_name.lower() or 'tools' in addon_name.lower():
                            addon = context.preferences.addons[addon_name]
                            if hasattr(addon.preferences, 'KH_Sketchup'):
                                KH = addon.preferences.KH_Sketchup == True
                                return KH
                except:
                    pass
        # إذا لم يتم العثور على الإضافة، إرجاع True كقيمة افتراضية
        return True

    def draw_header(self, context: bpy.types.Context):
        layout = self.layout
        row = layout.row()
        row.alignment = 'RIGHT'

        # Only KH-Collections icon button in header using preview_collection1 icon
        try:
            row.operator("object.fence_collection", text="", icon_value=preview_collection1['25.png'].icon_id)
        except KeyError:
            row.operator("object.fence_collection", text="", icon='COLLECTION_COLOR_04')
   
    def draw(self, context):
        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label(text="Close Edit Mode.", icon='ERROR')
            layout.label(text=" Works in Object Mode only.")
        else: 
            skp_old_exists = False
            for collection in bpy.data.collections:
                if collection.name == "skp_old":
                    skp_old_exists = True
                    break

            if skp_old_exists:
                box = layout.box() 
                row = box.row()
                row.label(text=f"Update SKP File :", icon='FILE_REFRESH')
                row = box.row()
                row.operator("object.skp_update_file", text="Update File", icon_value=preview_collection4['9.png'].icon_id)
                row = box.row()
                row.prop(context.scene, "loading_progress", text="Loading", slider=True)  
            else:
                box = layout.box()  
                row = box.row()
                row.label(text=f"Import SketchUP File :", icon='NEWFOLDER')
                row = box.row()
                row.operator(ImportSKP_k.bl_idname, text="Import New File", icon_value=preview_collection5['11.png'].icon_id)
                row = box.row()
                row.operator(ImportSKPFolder.bl_idname, text="Import Folder", icon='FILE_FOLDER')
                
                skp_old_exists = False
                for collection in bpy.data.collections:
                    if collection.name == "SKP Master":
                        skp_old_exists = True
                        break

                if skp_old_exists:
                    row = box.row()
                    row.operator(ImportSKPupdate.bl_idname, text="Reload SKP File", icon_value=preview_collection6['10.png'].icon_id)
                skp_old_exists = False
                for collection in bpy.data.collections:
                    if collection.name == "skp":
                        skp_old_exists = True
                        break

                if skp_old_exists:
                    row = box.row()
                    row.operator("object.skp_addonn", text="SKP File Setup" , icon_value=preview_collection7['7.png'].icon_id)  
                    row = box.row()
                    row.prop(context.scene, "loading_progress", text="Loading", slider=True)        
            #row.operator("object.skp_addon" , icon='PREFERENCES')
            #row = box.row()
            #row.operator("object.skp_addonc" , icon='BRUSH_DATA')
            #row.label(text=f"Update SKP File :", icon='FILE_REFRESH')
            skp_old_exists = False
            for collection in bpy.data.collections:
                if collection.name == "skp_old":
                    skp_old_exists = True
                    break

            #if skp_old_exists:
                
            #else:
               # row = box.row()
               # row.operator(ImportSKPupdate.bl_idname, text="Reload Sketchup", icon='IMPORT')
           
            box = layout.box()
            row = box.row()
            row.label(text=f"Custom :", icon='CURRENT_FILE')
            row = box.row()
            row.operator("object.skp_explode", text="Explode" , icon='MOD_EXPLODE')
            row.operator("object.skp_merge", text="Merge" , icon='MATCUBE') 
            row = box.row()
            row.operator("object.join_and_modify_operatorc", text="Clean Selected Objects" , icon='OUTLINER_OB_MESH') 
            row = box.row()
            row.operator("object.join_and_modify_operator", text="Collection Setup" , icon='COLLECTION_COLOR_01')
            row = box.row()
            row.operator("object.rivet" , text="Revit Fix", icon='COLOR_RED')
            #row = box.row()
            #row.operator("object.add_collection_operator" , icon='COLLECTION_COLOR_02')
            #row.operator("object.fence_collection", text="KH-Collections" , icon='COLLECTION_COLOR_04')
            box = layout.box()
            row = box.row() 
            row.label(text=f"Fence:", icon='COLLECTION_COLOR_05')
            row = box.row()
            row.operator("object.front_collection", text="Front" , icon='EVENT_F') 
            row.operator("object.right_collection" , text="Right", icon='EVENT_R') 
            row = box.row()
            row.operator("object.back_collection" , text="Back", icon='EVENT_B') 
            row.operator("object.left_collection" , text="Left", icon='EVENT_L') 
            # box = layout.box()
            # row = box.row()
            # row.operator("wm.sketchup_plugin_setup" , text="Install SketchUp plugin", icon='PLUGIN')
            # row.scale_y=1.3
        
   
# KH_tools_Tutoril///////////////////////////////////////////////////////////////////////////////////////////////////////////////

import webbrowser

class OpenLink_khtoolsOperator(bpy.types.Operator):
    bl_idname = "wm.open_link_khtools"
    bl_label = "YouTube"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        webbrowser.open("https://www.youtube.com/playlist?list=PLRrETGQR_7qJqvlELqqF6ReO45dVsYxyt")
        return {'FINISHED'}

preview_collection8 = bpy.utils.previews.new()
preview_collection8.load("24.png", os.path.join(my_icons_dir, "24.png"), 'IMAGE')
class KH_tools_Tutoril(bpy.types.Panel):
    bl_idname = "OBJECT_PT_tools_Tutoril"
    bl_label = "Tutoril"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "KH-Tools"
    bl_options = {'DEFAULT_CLOSED'} 
    
    @classmethod
    def poll(cls, context):
        # البحث عن الإضافة في المسارات المختلفة
        try:
            # محاولة البحث بالاسم الافتراضي
            KH = context.preferences.addons['KH-Tools'].preferences.KH_Tutoril == True
            return KH
        except KeyError:
            try:
                # محاولة البحث باسم المجلد الحالي
                KH = context.preferences.addons['kh_tools'].preferences.KH_Tutoril == True
                return KH
            except KeyError:
                try:
                    # البحث في جميع الإضافات المحملة
                    for addon_name in context.preferences.addons.keys():
                        if 'kh' in addon_name.lower() or 'tools' in addon_name.lower():
                            addon = context.preferences.addons[addon_name]
                            if hasattr(addon.preferences, 'KH_Tutoril'):
                                KH = addon.preferences.KH_Tutoril == True
                                return KH
                except:
                    pass
        # إذا لم يتم العثور على الإضافة، إرجاع True كقيمة افتراضية
        return True
    
    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon_value=preview_collection8['24.png'].icon_id)
        except KeyError:
            pass
        
    def draw(self, context):
        layout = self.layout
        layout.operator("wm.open_link_khtools", icon_value=preview_collection8['24.png'].icon_id)

#aoto import//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def sketchup_script():
    file_path = os.path.join(os.path.expanduser("~"), "Documents", "sketchup_import_data.txt")
    if os.path.exists(file_path):
        try:
            # قراءة بيانات الملف
            action = None
            model_path = None
            file_name = None
            
            # محاولة قراءة الملف مع إعادة المحاولة
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if len(lines) >= 3:
                            action = lines[0].strip()
                            model_path = lines[1].strip()
                            file_name = lines[2].strip()
                    break  # نجحت القراءة
                except PermissionError:
                    if attempt < max_retries - 1:
                        time.sleep(0.2)  # انتظر قليلاً وحاول مرة أخرى
                    else:
                        raise  # فشلت جميع المحاولات
            
            # إغلاق الملف قبل الحذف
            if action == "IMPORT" and model_path and file_name:
                # حذف الملف بعد إغلاقه
                for attempt in range(5):
                    try:
                        time.sleep(0.1)
                        os.remove(file_path)
                        break
                    except PermissionError:
                        if attempt < 4:
                            time.sleep(0.2)
                        else:
                            print(f"SKP | Warning: Could not delete file, will try later")
                
                # إظهار نافذة تأكيد الاستيراد
                import_confirmation = show_confirm(
                    "Import SketchUp", 
                    f"Do you want to import the file?\n\n{file_name}"
                )
                
                if import_confirmation:
                    # حساب مسار الحفظ
                    file_base = os.path.splitext(file_name)[0]
                    folder_path = os.path.dirname(model_path)
                    blender_file_name = file_base + ".blend"
                    
                    # التأكد من أن الاسم فريد
                    count = 1
                    while os.path.exists(os.path.join(folder_path, blender_file_name)):
                        blender_file_name = f"{file_base}_{count}.blend"
                        count += 1
                    
                    # تحويل المسار لعرض صحيح (استبدال \ بـ /)
                    display_path = folder_path.replace('\\', '/')
                    
                    # نافذة تأكيد الحفظ
                    save_confirmation = show_confirm(
                        "Save After Import", 
                        f"Do you want to save the file after import?\n\nPath: {display_path}\nFile: {blender_file_name}"
                    )
                    
                    # بدء عملية الاستيراد
                    progress_win = start_import_progress()
                    progress_win.log_message(f"Importing: {file_name}")
                    
                    bpy.ops.import_scene.skp_k(filepath=model_path)
                    bpy.ops.object.skp_addonn()
                    
                    if save_confirmation:
                        save_path = os.path.join(folder_path, blender_file_name)
                        bpy.ops.wm.save_mainfile(filepath=save_path)
                        progress_win.log_message(f"File saved: {save_path}")
                    
                    show_finished_in_progress("Import completed successfully!")
                else:
                    # إذا ألغى المستخدم، حاول حذف الملف
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except:
                        pass
                        
        except PermissionError:
            # الملف مفتوح من قبل عملية أخرى، سنحاول في المرة القادمة
            pass
        except Exception as e:
            print(f"SKP | Error in sketchup_script: {e}")
            # حاول حذف الملف في حالة الخطأ
            try:
                if os.path.exists(file_path):
                    time.sleep(0.3)
                    os.remove(file_path)
            except:
                pass
    
    return 5

@bpy.app.handlers.persistent 
def load_handler(dummy):
    sketchup_script()
    bpy.app.timers.register(sketchup_script) 
 


def update_script():
    file_path = os.path.join(os.path.expanduser("~"), "Documents", "sketchup_update_data.txt")
    if os.path.exists(file_path):
        try:
            # قراءة بيانات الملف
            action = None
            model_path = None
            file_name = None
            
            # محاولة قراءة الملف مع إعادة المحاولة
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if len(lines) >= 3:
                            action = lines[0].strip()
                            model_path = lines[1].strip()
                            file_name = lines[2].strip()
                    break  # نجحت القراءة
                except PermissionError:
                    if attempt < max_retries - 1:
                        time.sleep(0.2)  # انتظر قليلاً وحاول مرة أخرى
                    else:
                        raise  # فشلت جميع المحاولات
            
            # إغلاق الملف قبل الحذف
            if action == "UPDATE" and model_path and file_name:
                # التحقق من وجود SKP Master
                skp_old_exists = False
                for collection in bpy.data.collections:
                    if collection.name == "SKP Master":
                        skp_old_exists = True
                        break
                
                if skp_old_exists:
                    # حذف الملف بعد إغلاقه
                    for attempt in range(5):
                        try:
                            time.sleep(0.1)
                            os.remove(file_path)
                            break
                        except PermissionError:
                            if attempt < 4:
                                time.sleep(0.2)
                            else:
                                print(f"SKP | Warning: Could not delete file, will try later")
                    
                    # إظهار نافذة تأكيد التحديث
                    update_confirmation = show_confirm(
                        "Update SketchUp", 
                        f"Do you want to update the file?\n\n{file_name}"
                    )
                    
                    if update_confirmation:
                        # بدء عملية التحديث
                        progress_win = start_import_progress()
                        progress_win.log_message(f"Updating: {file_name}")
                        
                        bpy.ops.import_scene_update.skp(filepath=model_path)
                        bpy.ops.object.skp_update_file()
                        
                        show_finished_in_progress("Update completed successfully!")
                    else:
                        # إذا ألغى المستخدم، حاول حذف الملف
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        except:
                            pass
                            
        except PermissionError:
            # الملف مفتوح من قبل عملية أخرى، سنحاول في المرة القادمة
            pass
        except Exception as e:
            print(f"SKP | Error in update_script: {e}")
            # حاول حذف الملف في حالة الخطأ
            try:
                if os.path.exists(file_path):
                    time.sleep(0.3)
                    os.remove(file_path)
            except:
                pass
    
    return 5

@bpy.app.handlers.persistent  
def update_script_timer(dummy):
    update_script()
    bpy.app.timers.register(update_script)

#SketchUp Plugins2013//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
import shutil
import ctypes

def SketchUp_Plugin2013():
    addon_dir = os.path.dirname(__file__)
    source_dir = os.path.join(addon_dir, "SketchUp Plugins")
   # source_dir = os.path.join(os.getenv('APPDATA'), r'Blender Foundation\Blender\4.2\scripts\addons\KH-Tools\SketchUp Plugins')
    print(f"Source directory: {source_dir}")

    # Define base destination directory
    base_destination_dir = os.path.join(os.getenv('APPDATA'), r'SketchUp')

    # Ensure the base destination directory exists
    if not os.path.exists(base_destination_dir):
        print(f"The base directory {base_destination_dir} does not exist.")
    else:
        copied_folders = [] 
        # Loop through all directories in the base destination directory
        for dir_name in os.listdir(base_destination_dir):
            if dir_name.startswith("SketchUp"):
                destination_dir = os.path.join(base_destination_dir, dir_name, 'SketchUp', 'Plugins')
                print(f"Copying to: {destination_dir}")
                
                # Ensure the destination directory exists, create if it does not
                os.makedirs(destination_dir, exist_ok=True)
                
                # Copy the contents of the source directory to the destination directory
                try:
                    for item in os.listdir(source_dir):
                        s = os.path.join(source_dir, item)
                        d = os.path.join(destination_dir, item)
                        if os.path.isdir(s):
                            shutil.copytree(s, d, dirs_exist_ok=True)
                        else:
                            shutil.copy2(s, d)
                    print(f"Contents copied successfully to {destination_dir}.")
                    copied_folders.append(dir_name)
                except Exception as e:
                    print(f"Error copying to {destination_dir}: {e}")
                    
        show_message("SketchUp Plugin Installed", f"Plugin installed in:\n{chr(10).join(copied_folders)}")
#SketchUp Plugins2008//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def SketchUp_Plugin2008():
    def copy_file_as_admin(src, dest):
        # Convert to absolute paths
        src = os.path.abspath(src)
        dest = os.path.abspath(dest)
        
        # Create the destination directory if it doesn't exist
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        
        # Construct the command
        command = f'xcopy /E /I /Y "{src}" "{dest}"'
        
        # Display the UAC (User Account Control) prompt to request admin privileges
        try:
            result = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f"/c {command}", None, 1)
            if result <= 32:
                raise Exception("Failed to obtain admin privileges.")
        except Exception as e:
            print(f"Error: {e}")

    def find_sketchup_plugins_folder():
        # Search for folders starting with "Google SketchUp" inside the "Google" folder
        google_folder = r'C:\Program Files (x86)\Google'
        sketchup_folders = [folder for folder in os.listdir(google_folder) if folder.startswith("Google SketchUp")]

        # Look for "Plugins" folder in the found SketchUp folders
        plugins_folders = []
        for folder in sketchup_folders:
            plugins_path = os.path.join(google_folder, folder, "Plugins")
            if os.path.exists(plugins_path):
                plugins_folders.append(plugins_path)

        return plugins_folders

    addon_dir = os.path.dirname(__file__)
    source_dir = os.path.join(addon_dir, "SketchUp Plugins")
    src_folder = source_dir #r'C:\Users\looks\AppData\Roaming\Blender Foundation\Blender\4.2\scripts\addons\KH-Tools\sketcup_import\SketchUp Plugins'
    dest_folders = find_sketchup_plugins_folder()

    # Copy files and folders from source to destination
    for dest_folder in dest_folders:
        copy_file_as_admin(src_folder, dest_folder)
        
        # Modify message to display paths without "Plugins" and backslashes
    modified_dest_folders = [folder.replace("\\Plugins", "") for folder in dest_folders]
    modified_dest_folders = [folder.replace("\\", "/") for folder in modified_dest_folders]
    
    if modified_dest_folders:
        show_message("SketchUp Plugin Installed", f"Plugin installed in:\n{chr(10).join(modified_dest_folders)}")

    
    
class KH_SketchUp_Plugin_Setup(bpy.types.Operator):
    bl_idname = "wm.sketchup_plugin_setup"
    bl_label = "Setup SketchUp Plugin"

    def execute(self, context):
        SketchUp_Plugin2013()
        SketchUp_Plugin2008()
        #ctypes.windll.user32.MessageBoxW(0, "Installation of the SketchUp Plugin has been Completed.", "Install SketchUp Extension is Finished", 0)
        return {'FINISHED'}

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#preview_collections1 = {}

classes = (            
            #kh-tools////////////////////////////////////////////
            SketchupAddonPreferences_k,
            ImportSKP_k,
            ImportSKPupdate,
            ImportSKPFolder,
            Explode,
            SKPN,
            Update_File,
            Merge,
            OBJECT_OT_RivetOperator,
            FenceCollection,
            CopyNameMaterialPanel,
            CollectionOperator,
            FrontCollection,
            RightCollection,
            LeftCollection,
            BackCollection,
            OBJECT_OT_JoinAndModifyOperator,
            OBJECT_OT_JoinAndModifyOperatorc,
    
            #KH_tools_Tutoril//////////////////////////////
            KH_tools_Tutoril,
            OpenLink_khtoolsOperator,
            KH_SketchUp_Plugin_Setup,

                )

addon_keymaps = []

def register():
    for i in classes:
        register_class(i)
    
    # تسجيل نافذة التقدم
    from . import progress_window
    progress_window.register()
    
   #kh-tools------------------------------------------------------------------
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.Scene.cube_scale_x = bpy.props.FloatProperty(name="Scale X", default=0.6, min=0.1)
    bpy.types.Scene.cube_scale_y = bpy.props.FloatProperty(name="Scale Y", default=0.6, min=0.1)
    bpy.types.Scene.cube_scale_z = bpy.props.FloatProperty(name="Scale Z", default=0.2, min=0.1)
    
    bpy.types.Scene.loading_progress = IntProperty(
        name="Loading Progress",
        description="Shows the progress of loading",
        default=0,
        min=0,
        max=100
    )
    bpy.app.handlers.load_post.append(load_handler)
    bpy.app.timers.register(sketchup_script) 
    
    bpy.app.handlers.load_post.append(update_script_timer)
    bpy.app.timers.register(update_script) 

def unregister():
    for i in classes:
        unregister_class(i)
    
    # إلغاء تسجيل نافذة التقدم
    from . import progress_window
    progress_window.unregister()

    #KH-TOOLS//////////////////////////////////////////////////////////////
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    
    del bpy.types.Scene.cube_scale_x
    del bpy.types.Scene.cube_scale_y
    del bpy.types.Scene.cube_scale_z
    del bpy.types.Scene.loading_progress
    

if __name__ == "__main__":
    try:
        register()
    except:
        pass
    unregister()
    
