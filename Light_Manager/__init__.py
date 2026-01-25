bl_info = {
    "name": "KH-Light Manager",
    "author": "Khaled Alnwesary",
    "version": (1, 4),
    "blender": (3, 00, 0),
    "location": "View3D > UI",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "KH",
}
import bpy
import os
import re
from bpy.utils import register_class, unregister_class
from bpy.props import (EnumProperty)
from bpy.props import (BoolProperty, EnumProperty, FloatProperty, IntProperty,PointerProperty,StringProperty)

from bpy.props import *
from bpy.types import Panel, Operator, Menu
from bpy.utils import previews
from bpy.app.handlers import persistent

# استيراد الدالة المساعدة من الملف الرئيسي
try:
    from .. import get_addon_preferences
except ImportError:
    # إذا فشل الاستيراد، إنشاء دالة محلية
    def get_addon_preferences(context, preference_name):
        try:
            addon = context.preferences.addons['KH-Tools']
            if hasattr(addon.preferences, preference_name):
                return getattr(addon.preferences, preference_name)
        except KeyError:
            try:
                addon = context.preferences.addons['kh_tools']
                if hasattr(addon.preferences, preference_name):
                    return getattr(addon.preferences, preference_name)
            except KeyError:
                try:
                    for addon_name in context.preferences.addons.keys():
                        if 'kh' in addon_name.lower() or 'tools' in addon_name.lower():
                            addon = context.preferences.addons[addon_name]
                            if hasattr(addon.preferences, preference_name):
                                return getattr(addon.preferences, preference_name)
                except:
                    pass
        return True

preview_collections2 = {}
ies_preview_collections = {}
addon_dir = os.path.dirname(__file__)

# IES Browser Properties
def get_ies_enum_items(self, context):
    """Generate enum items for IES files with previews"""
    enum_items = []
    
    # Get active light object
    selected_object = context.active_object
    if not selected_object or selected_object.type != 'LIGHT':
        return enum_items
    
    # Check if light has IES node
    if not selected_object.data.use_nodes:
        return enum_items
        
    ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
    if not ies_node or ies_node.label != "KH-IES":
        return enum_items
    
    current_file = ies_node.filepath
    if not current_file or not os.path.exists(current_file):
        return enum_items
    
    # Get directory containing IES files
    ies_dir = os.path.dirname(current_file)
    if not os.path.exists(ies_dir):
        return enum_items
    
    # Get preview collection
    pcoll = ies_preview_collections.get("ies_files")
    if not pcoll:
        pcoll = bpy.utils.previews.new()
        ies_preview_collections["ies_files"] = pcoll
    
    # Get all IES files in directory
    ies_files = [f for f in os.listdir(ies_dir) if f.lower().endswith('.ies')]
    
    # Sort files by number
    def get_file_number(filename):
        match = re.search(r'\d+', filename)
        return int(match.group()) if match else float('inf')
    
    ies_files.sort(key=get_file_number)
    
    # Create enum items with previews
    for i, filename in enumerate(ies_files):
        filepath = os.path.join(ies_dir, filename)
        base_name = os.path.splitext(filename)[0]
        
        # Look for preview image
        image_path = None
        for ext in ['.png', '.jpg', '.jpeg']:
            potential_image = os.path.join(ies_dir, base_name + ext)
            if os.path.exists(potential_image):
                image_path = potential_image
                break
        
        # Load preview if available
        icon_id = 'LIGHT'
        if image_path:
            try:
                preview_id = f"ies_{base_name}"
                if preview_id not in pcoll:
                    preview = pcoll.load(preview_id, image_path, 'IMAGE')
                    icon_id = preview.icon_id
                else:
                    icon_id = pcoll[preview_id].icon_id
            except Exception as e:
                print(f"Error loading preview for {filename}: {e}")
        
        # Add to enum items
        enum_items.append((
            filepath,           # identifier
            base_name,          # name
            f"IES: {filename}", # description
            icon_id if isinstance(icon_id, int) else 'LIGHT',  # icon
            i                   # number
        ))
    
    return enum_items

def update_ies_selection(self, context):
    """Update IES file when selection changes"""
    selected_object = context.active_object
    if not selected_object or selected_object.type != 'LIGHT':
        return
    
    if not selected_object.data.use_nodes:
        return
        
    ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
    if not ies_node or ies_node.label != "KH-IES":
        return
    
    # Update IES node filepath
    new_filepath = context.scene.ies_files_enum
    if new_filepath and os.path.exists(new_filepath):
        ies_node.filepath = new_filepath
        
        # Update preview image in UI
        ies_dir = os.path.dirname(new_filepath)
        base_name = os.path.splitext(os.path.basename(new_filepath))[0]
        
        # Look for corresponding image file
        image_path = None
        for ext in ['.png', '.jpg', '.jpeg']:
            potential_image = os.path.join(ies_dir, base_name + ext)
            if os.path.exists(potential_image):
                image_path = potential_image
                break
        
        # Update the preview image
        if image_path:
            try:
                # Remove old image if exists
                if hasattr(context.scene, 'my_image') and context.scene.my_image:
                    old_image = context.scene.my_image
                    if old_image and old_image.name in bpy.data.images:
                        bpy.data.images.remove(old_image)
                
                # Load new image
                new_image = bpy.data.images.load(image_path)
                context.scene.my_image = new_image
            except Exception as e:
                print(f"Error loading preview image: {e}")
                context.scene.my_image = None
        else:
            # No image found, clear preview
            if hasattr(context.scene, 'my_image') and context.scene.my_image:
                old_image = context.scene.my_image
                if old_image and old_image.name in bpy.data.images:
                    bpy.data.images.remove(old_image)
                context.scene.my_image = None
        
        # Force UI update
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

#light_manager
script_dir = os.path.dirname(os.path.abspath(__file__))
my_icons_dir = os.path.join(script_dir, "icons")
preview_collection = bpy.utils.previews.new()
preview_collection.load("118.png", os.path.join(my_icons_dir, "118.png"), 'IMAGE')

class VIEW3D_PT_light_manager(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_light_manager"
    bl_label = "Light Manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'KH-Tools'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        # استخدام الدالة المساعدة للبحث عن إعدادات الإضافة
        return get_addon_preferences(context, 'Light_Manager') == True

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon_value=preview_collection['118.png'].icon_id)
        except KeyError:
            pass
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.operator("object.add_point_light", text="P" , icon="LIGHT_POINT")
        row.operator("object.add_spot_light", text="S" , icon="LIGHT_SPOT")
        row.operator("object.add_area_light", text="A" , icon="LIGHT_AREA")
        
        row.operator("object.kh_light_to_active_object", text="" , icon="RESTRICT_SELECT_OFF")
        row.operator("object.add_collection_operator" , icon='COLLECTION_COLOR_02', text="")
        
        
        material_curtain = [
            obj for obj in bpy.data.objects
            if obj.type == 'MESH' and obj.data and obj.data.materials and 
            any(mat and mat.name.lower().startswith("curtain") for mat in obj.data.materials)
        ]

        material_glass = [
            obj for obj in bpy.data.objects
            if obj.type == 'MESH' and obj.data and obj.data.materials and 
            any(mat and mat.name.lower().startswith("in glass") for mat in obj.data.materials)
        ]

        Roof_objects = [
            obj for obj in bpy.data.objects
            if obj.type == 'MESH' and obj.data and obj.data.materials and 
            any(mat and mat.name.lower().startswith("r spot") for mat in obj.data.materials)
        ]

        wall_objects = [
            obj for obj in bpy.data.objects
            if obj.type == 'MESH' and obj.data and obj.data.materials and 
            any(mat and mat.name.lower().startswith("w spot") for mat in obj.data.materials)
        ]
        
        if material_curtain or material_glass or Roof_objects or wall_objects:
            box = layout.box()
            row = box.row()

        if material_curtain: 
            row.operator("object.point_curtain", icon='OUTLINER_OB_LIGHT', text="Curtain")
        
        if material_glass and not material_curtain: 
            row.operator("object.point_glass", icon='OUTLINER_OB_LIGHT', text="Glass")
            
        if Roof_objects:
            row.operator("object.spot_roof", icon='LIGHT_SPOT', text="R Spot")

        if wall_objects:
            row.operator("object.spot_wall", icon='EVENT_W', text="Wall")
                
        
        for obj in bpy.context.scene.objects:
            if obj.type == 'LIGHT' and obj.data.type == 'SPOT':
                    row = box.row()
                    row.scale_y=0.9
                    row.operator("light_manager.scale_spot_lights", text="Min", icon= 'LIGHT_SPOT')
                    row.operator("light_manager.scale_spot", text="max", icon= 'LIGHT_SPOT')
                    break
        
        layout = self.layout
        lights = [obj for obj in bpy.data.objects if obj.type == 'LIGHT']
        unique_lights = []
        for light in lights:
            is_duplicate = False
            for unique_light in unique_lights:
                if light.data == unique_light.data:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_lights.append(light)
        
        selected_object = bpy.context.object
        if selected_object :
            if selected_object.type == 'LIGHT' and not selected_object.data.type == "SUN":
                box = layout.box()
                row = box.row(align=True)
                row.scale_x=1.6
                row.prop(selected_object.data, "type", text="",icon="LIGHT_%s" % selected_object.data.type,icon_only=True,)
                row.scale_x=1.4
                row.prop(context.object.data, "name", text="", icon='RESTRICT_SELECT_OFF')
                if selected_object.data.type == "AREA":
                    row.scale_x=0.5
                    row.prop(selected_object.data, "shape", text='')
                
                row.scale_x=0.3
                if not selected_object.data.use_nodes:
                    row.prop(selected_object.data, "color", text='')
                    row.scale_x=1.1
                    row.operator("object.temperature", text='', icon='EVENT_C')
                else:
                    if selected_object.data.use_nodes:
                        Temperature = selected_object.data.node_tree.nodes.get('Blackbody')
                        if Temperature and Temperature.label == "KH-Temperature":
                            row.scale_x=1.1
                            row.prop(Temperature.inputs[0], "default_value", text="")
                            row.operator("object.delet_temperature", text='', icon='EVENT_K') 
                        else:
                            row.prop(selected_object.data, "color", text='')
                            row.scale_x=1.1
                            row.operator("object.temperature", text='', icon='EVENT_C')

                row = box.row()
                #row.label(text="Selected :", icon='OUTLINER_OB_LIGHT')
                #row.scale_x=0.6
                # Loop through all objects in the scene
                
                if selected_object.data.type in {'POINT', 'SPOT', 'AREA'}:
                    if not selected_object.data.use_nodes :
                        row.operator("object.kh_ies", text='IES')
                    else: 
                        ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
                        if ies_node and  ies_node.label == "KH-IES":
                                row.operator("object.delet_kh_ies", text='IES', icon='RESTRICT_VIEW_OFF')
                                
                                
                                #row.prop(selected_object.data , "use_nodes", text='IES',toggle= True) 
                        else:
                            row.operator("object.kh_ies", text='IES')
                            
                row.prop(selected_object.data.cycles, "use_multiple_importance_sampling", text='Reflect',toggle= True)
                selected_objects = bpy.context.selected_objects 
                for obj in selected_objects:
                    if obj.visible_glossy:
                        row.operator("light_manager.disable_glossy", text="Gl", icon= 'HIDE_OFF')
                    else:
                        row.operator("light_manager.enable_glossy", text="Gl", icon= 'HIDE_ON')
                    break
            
                row = box.row()
                row.prop(selected_object.data, "energy", text='')
                if selected_object.data.type == "SPOT":
                    row.prop(selected_object.data, "shadow_soft_size", text='Radius')
                if selected_object.data.type == "SUN":
                    row.prop(selected_object.data, "angle")
                if selected_object.data.type == "AREA":
                    row.prop(selected_object.data, "spread", text="Radius")
                                                                   
                if selected_object.data.type == "POINT":
                    row.prop(selected_object.data, "shadow_soft_size", text='Radius')
    
                row = box.row()
                if selected_object.data.type == "SPOT":
                    row.prop(selected_object.data, "spot_size")
                    
                if selected_object.data.type == "AREA":
                    row.prop(selected_object.data, "size", text="size")
                    #row.scale_x=0.6
                    if selected_object.data.shape == 'RECTANGLE':
                        row.prop(selected_object.data, "size_y", text="Y")
                    if selected_object.data.shape == 'ELLIPSE':
                        row.prop(selected_object.data, "size_y", text="Y")
                
                # Check if the object is active and is a light type (Point, Spot, or Area)
                if selected_object.data.type in {'POINT', 'SPOT', 'AREA'}:
                    # Activate Use Nodes for the light if not already activated
                    if selected_object.data.use_nodes:
                        if selected_object.type == 'LIGHT':
                            ies_node = selected_object.data.node_tree.nodes.get('IES Texture')

                        if ies_node and ies_node.label == "KH-IES":
                            box = layout.box()

                            # IES File Info Section
                            row = box.row(align=True)
                            current_file = os.path.basename(ies_node.filepath)
                            
                            # File path property (smaller)
                            col = row.column(align=True)
                            #col.scale_x = 0.4
                            col.prop(ies_node, "filepath", text="")
                            
                            row = box.row(align=True)

                            # Current file display with click to browse
                            col = row.column(align=True)
                            #col.label(text="IES File:", icon='LIGHT')
                            
                            op = col.operator("object.ies_browser", text=current_file, icon='LIGHT')
                            
                            

                            
                            
                            

                            # IES Browser with icon view (similar to Gaffer HDRI)
                            box = layout.box()
                            col = box.column(align=True)
                            
                            # Header row
                            row = col.row(align=True)
                            row.label(text="IES Library", icon='LIGHT_DATA')
                            
                            # Get IES files count
                            ies_items = get_ies_enum_items(None, context)
                            if ies_items:
                                row.label(text=f"{len(ies_items)} files")
                            
                            col.separator()
                            
                            # Main icon view row (similar to Gaffer)
                            row = col.row(align=True)
                            
                            # Left navigation column
                            tmpc = row.column(align=True)
                            tmpr = tmpc.column(align=True)
                            tmpr.scale_y = 1
                            # Refresh button
                            tmpr.operator("object.refresh_ies_list", text="", icon="FILE_REFRESH")
                            
                            tmpcc = tmpc.column(align=True)
                            tmpcc.scale_y = 4
                            # Previous button
                            tmpcc.operator("script.change_ies_file", text="", icon="TRIA_LEFT").direction = 'PREVIOUS'
                            
                            tmpr = tmpc.column(align=True)
                            tmpr.scale_y = 1
                            # Generate images button
                            tmpr.operator("object.generate_ies_images", text="", icon="IMAGE_DATA")
                            
                            # Center: Icon view (main preview area)
                            tmpc = row.column()
                            tmpc.scale_y = 0.5
                            tmpc.template_icon_view(context.scene, "ies_files_enum", show_labels=True, scale=11)
                            
                            # Right navigation column
                            tmpc = row.column(align=True)
                            tmpr = tmpc.column(align=True)
                            tmpr.scale_y = 1
                            # Browse button (opens full browser)
                            tmpr.operator("object.ies_browser", text="", icon="FILEBROWSER")
                            
                            tmpcc = tmpc.column(align=True)
                            tmpcc.scale_y = 4
                            # Next button
                            tmpcc.operator("script.change_ies_file", text="", icon="TRIA_RIGHT").direction = 'NEXT'
                            
                            tmpr = tmpc.column(align=True)
                            tmpr.scale_y = 1
                            # Random button (optional)
                            tmpr.operator("object.random_ies_file", text="", icon="FILE_REFRESH")




class SetLightVisibilityOperator(bpy.types.Operator):
    bl_idname = "object.set_light_visibility"
    bl_label = "Set Light Visibility"
    light_name: bpy.props.StringProperty()
    
    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            if obj.type == 'LIGHT':
                obj.visible_diffuse = False
                obj.visible_glossy = False
                obj.visible_transmission = False
                obj.visible_volume_scatter = False
        
        return {'FINISHED'}
    
class SetLight_hidine_Operator(bpy.types.Operator):
    bl_idname = "object.set_light_hidden"
    bl_label = "Set Light Visibility"
    light_name: bpy.props.StringProperty()
    
    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            if obj.type == 'LIGHT':
                obj.visible_diffuse = True
                obj.visible_glossy = True
                obj.visible_transmission = True
                obj.visible_volume_scatter = True        
        return {'FINISHED'}

 #LIGHT LIST////////////////////////////////////////////////////////////////////////////////////         
class VIEW3D_PT_light_managerlist(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_light_managerlist"
    bl_label = "LIGHT LIST"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'KH-Tools'
    bl_parent_id = "VIEW3D_PT_light_manager"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon='COLLAPSEMENU')
        except KeyError:
            pass
    
    def draw(self, context):
        layout = self.layout
        lights = [obj for obj in bpy.data.objects if obj.type == 'LIGHT']
        unique_lights = []
        for light in lights:
            is_duplicate = False
            for unique_light in unique_lights:
                if light.data == unique_light.data:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_lights.append(light)
                
        selected_object = bpy.context.object
        for light in unique_lights:
            box = layout.box()
            row = box.row()
            row.scale_x=1.3
            row.scale_y=0.9
            if light.data.type == 'POINT':
                row.operator("object.select_by_name", text="", icon="LIGHT_POINT").light_name = light.name
            elif light.data.type == 'SPOT':
                row.operator("object.select_by_name", text="", icon="LIGHT_SPOT").light_name = light.name
            elif light.data.type == 'AREA':
                row.operator("object.select_by_name", text="", icon="LIGHT_AREA").light_name = light.name
            elif light.data.type == 'SUN':
                row.operator("object.select_by_name", text="", icon="LIGHT_SUN").light_name = light.name
            else:
                row.operator("object.select_by_name", text="", icon="RESTRICT_SELECT_OFF").light_name = light.name
            if selected_object is not None and selected_object.type == 'LIGHT':
                if light.data.name == selected_object.data.name:  # Check if the light is active in the scene
                       # row.operator("object.select_by_name", text="", icon="RESTRICT_SELECT_OFF").light_name = light.name
                    selected_objects = bpy.context.selected_objects 
                    for obj in selected_objects:
                        if obj.visible_diffuse:
                            row.operator("object.set_light_visibility", text="", icon="HIDE_OFF").light_name = light.name
                        else:
                            row.operator("object.set_light_hidden", text="", icon="HIDE_ON").light_name = light.name
                        break

            row.scale_x=1.3
            row.prop(light.data, "name",text="")
            row.scale_x=0.7
            row.prop(light.data, "users", text="")
            row = box.row()
            row.scale_y=0.8
            row.prop(light.data, "energy",text="")
            #row.scale_x=0.4
            #row.prop(light.data, "color",text="")
            row.scale_x=0.3
            if not light.data.use_nodes:
                row.prop(light.data, "color", text='')
                row.scale_x=1.1
                #row.operator("object.temperature", text='', icon='EVENT_K')
            else:
                if light.data.use_nodes:
                    Temperature = light.data.node_tree.nodes.get('Blackbody')
                    if Temperature and Temperature.label == "KH-Temperature":
                        row.scale_x=0.8
                        row.prop(Temperature.inputs[0], "default_value", text="")
                        #row.operator("object.delet_temperature", text='', icon='EVENT_K') 
                    else:
                        row.prop(light.data, "color", text='')
                        #row.scale_x=1.1
                       # row.operator("object.temperature", text='', icon='EVENT_K')
            
            row.scale_x=0.7
            box = layout.box()
            #row.prop(light.data, "type", text="")
            row = box.row()
            
        has_light = False
        for obj in bpy.context.scene.objects:
            if obj.type == 'LIGHT':
                has_light = True
                break
        
        if not has_light:
            box = layout.box()
            row = box.row()
            row.label(text=" No Light in the scene", icon='QUESTION')
                           
        #     row.prop(light.data, "energy")
        #     row.scale_x=0.6
        #     row.scale_y=0.75
        #     row.prop(light.data, "color", text='')
        #     row = box.row()
        #     if light.data.type == "SPOT":
        #         row.prop(light.data, "spot_size")
        #         row.scale_x=0.6
        #         row.scale_y=0.75
        #         row.prop(light.data, "shadow_soft_size", text='R')
                 
        #     if light.data.type == "SUN":
        #         row.prop(light.data, "angle")
                
        #     if light.data.type == "AREA":
        #         row.prop(light.data, "size",text="X")
        #         if light.data.shape == 'RECTANGLE':
        #             row.scale_x=0.6
        #             row.scale_y=0.75
        #             row.prop(light.data, "size_y", text="Y")
        #         row.scale_x=0.6
        #         row.scale_y=0.75
        #         row.prop(light.data, "shape", text='')
        #         row.scale_y=0.75
        #         row = box.row()  
        #     if light.data.type == "POINT":
        #         row.scale_y=0.75
        #         row.prop(light.data, "shadow_soft_size", text='Radius')
        # else:
        #     box = layout.box()
        #     row = box.row()
        #     row.label(text=" No light in the scene ", icon='QUESTION')


# Emission List///////////////////////////////////////////////////////////////////////////////////////////
def find_emission_control_node(material):
    """
    Finds the node that controls emission for a given material.
    This can be a Principled BSDF, an Emission node, or a Group node with the correct inputs.
    Returns the node, the color input name, and the strength input name.
    """
    if not (material and material.use_nodes and material.node_tree):
        return None, None, None

    # Priority 1: Principled BSDF or Emission at top level
    for node in material.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED' and 'Emission Strength' in node.inputs:
            color_name = 'Emission Color' if 'Emission Color' in node.inputs else 'Emission'
            return node, color_name, 'Emission Strength'
        if node.type == 'EMISSION':
            return node, 'Color', 'Strength'

    # Priority 2: Group node with exposed controls
    for node in material.node_tree.nodes:
        if node.type == 'GROUP':
            has_strength = 'Emission Strength' in node.inputs
            has_color = ('Emission Color' in node.inputs) or ('Emission' in node.inputs)
            if has_strength and has_color:
                color_name = 'Emission Color' if 'Emission Color' in node.inputs else 'Emission'
                return node, color_name, 'Emission Strength'
    
    return None, None, None


class EmissionListPanel(bpy.types.Panel):
    bl_label = ("EMISSION LIST")
    bl_idname = "OBJECT_PT_shader_node_emission_list"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "KH-Tools"
    bl_options = {'DEFAULT_CLOSED'}
    #bl_parent_id   = "CAMMANAGER_PT_Cammanager"
    bl_parent_id   = "VIEW3D_PT_light_manager"
    
    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon='LIGHT_HEMI')
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout
        if bpy.context.mode == 'EDIT_MESH':
            layout.label(text="Close Edit Mode.", icon='ERROR')
            layout.label(text=" Works in Object Mode only.")
        else:
            materials = [mat for mat in bpy.data.materials if
                         (mat.name.lower().startswith("LED:")) or mat.name.startswith("LED:") and mat.users > 0]
            row = layout.row()
            #row.scale_x = 0.6
            row.operator("object.shader_node_emission_name", text="ADD TO LIST", icon='ADD')
            row.scale_x = 0.6
            row.operator("object.shader_node_emission_name_all", text="All", icon='PLUS')
            row = layout.row()
            row.scale_x = 0.3
            materials1 = bpy.data.materials
            for material in materials1:
                if material.name.startswith("LED:"):
                    row.operator("object.shader_node_emission_show100", text="100", icon='RESTRICT_VIEW_OFF')
                    row.scale_x = 0.3
                    row.operator("object.shader_node_emission_show", text="10", icon='RESTRICT_VIEW_OFF')
                    row.scale_x = 1.3
                    row.operator("object.shader_node_emission_hide", text="", icon='RESTRICT_VIEW_ON')
                    row.scale_x = 1.3
                    row.operator("object.shader_node_emission_keyframe_delete", text="", icon='FILE_REFRESH') 
                         
                    row = layout.row()
                    row.scale_x = 0.6
                    break 
           #row.operator("object.shader_node_emission_keyframe", text="Apply", icon='RESTRICT_RENDER_OFF')
            materials1 = bpy.data.materials
            for material in materials1:
                if material.name.startswith("LED:"):
                    node, color_prop, strength_prop = find_emission_control_node(material)
                    if node and color_prop:
                        emission_color = node.inputs[color_prop].default_value
                        mat_color = material.diffuse_color
                        # Compare RGB values with rounding to avoid float precision issues
                        if tuple(round(c, 4) for c in mat_color[:3]) != tuple(round(c, 4) for c in emission_color[:3]):
                            row.operator("object.shader_node_emission_keyframe", text="Apply", icon='ERROR')
                            break # Found one, no need to check others

            for material in materials:
                target_node, color_prop, strength_prop = find_emission_control_node(material)

                row = layout.row()
                # Add an icon to select or deselect objects with the same name as the material
                row.scale_x = 1.3
                if context.object and context.object.active_material:
                    icon = 'RESTRICT_SELECT_OFF' if context.object.active_material and material.name == context.object.active_material.name else 'RESTRICT_SELECT_ON'
                else:
                    icon = 'RESTRICT_SELECT_ON'

                op = row.operator("object.shader_node_emission_selectb", text="", icon=icon)
                op.material_name = material.name
                row.prop(material, "name", text="", icon='MATERIAL_DATA')

                if target_node:
                    row.scale_x = 0.17
                    row.prop(target_node.inputs[color_prop], "default_value", text="")
                    row.scale_x = 0.6
                    row.prop(target_node.inputs[strength_prop], "default_value", index=0, text="")
                else:
                    # Add a spacer to align the delete button
                    row.label(text="", icon='NODE_INSERT_OFF')


                op = row.operator("object.delete_led", text="", icon="TRASH")
                op.material_name = material.name

            else:
                row = layout.row()
                row.label(text="Select the material, then click ADD", icon='QUESTION')
                row = layout.row()
                row.label(text="Do not delete the word (LED:).", icon='QUESTION')
                
                

class kh_ShaderNodeEmissionSelectb(bpy.types.Operator):
    bl_idname = "object.shader_node_emission_selectb"
    bl_label = ""
    bl_description = "Select by Material Name"
    
    material_name: bpy.props.StringProperty()

    def execute(self, context):
        selected_objects = []
        for obj in context.view_layer.objects:
            if obj.type == 'MESH':
                for slot_index, slot in enumerate(obj.material_slots):
                    if slot.material and slot.material.name == self.material_name:
                        selected_objects.append(obj)
                        obj.active_material_index = slot_index
                        obj.active_material = slot.material

        bpy.ops.object.select_all(action='DESELECT')

        for obj in selected_objects:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

        return {'FINISHED'}
    
#Delete the material from the list  
class kh_Delete_Led(bpy.types.Operator):
    bl_idname = "object.delete_led"
    bl_label = ""
    bl_description  = "Delete the material from the list"

    material_name: bpy.props.StringProperty()
    def execute(self, context):
        for obj in context.view_layer.objects:
            if obj.type == 'MESH':
                for slot_index, slot in enumerate(obj.material_slots):
                    if slot.material and slot.material.name == self.material_name:
                        bpy.ops.object.select_all(action='DESELECT')
                        obj.select_set(True)
                        bpy.context.view_layer.objects.active = obj
                        obj.active_material_index = slot_index
                        if bpy.context.active_object.active_material :
                            active_material = bpy.context.active_object.active_material

                        if active_material is not None:
                            new_name = active_material.name.replace("LED: ", "")
                            active_material.name = new_name

        return {'CANCELLED'}


class kh_ShaderNodeEmissionKeyframe(bpy.types.Operator):
    bl_idname = "object.shader_node_emission_keyframe"
    bl_label = "Keyframe Emission Strength & Strength"
    material_name: bpy.props.StringProperty()
    
    def execute(self, context):
        materials = bpy.data.materials
        for material in materials:
            if material.name.startswith("LED:"):
                node, color_prop, strength_prop = find_emission_control_node(material)
                if node and color_prop:
                    emission_color = node.inputs[color_prop].default_value
                    material.diffuse_color = (emission_color[0], emission_color[1], emission_color[2], 1.0)
                    
        return {'FINISHED'}
    
#Emission 100   
class kh_ShaderNodeEmissionShow100(bpy.types.Operator):
    bl_idname = "object.shader_node_emission_show100"
    bl_label = "Keyframe Emission Strength & Strength"
    material_name: bpy.props.StringProperty()
    
    def execute(self, context):
        for material in bpy.data.materials:
            if material.name.startswith("LED:"):
                node, color_prop, strength_prop = find_emission_control_node(material)
                if node and strength_prop:
                    node.inputs[strength_prop].default_value = 100.0
        
        bpy.context.view_layer.update()
        return {'FINISHED'}


#Emission 10   
class kh_ShaderNodeEmissionShow(bpy.types.Operator):
    bl_idname = "object.shader_node_emission_show"
    bl_label = "Keyframe Emission Strength & Strength"
    material_name: bpy.props.StringProperty()
    
    def execute(self, context):
        for material in bpy.data.materials:
            if material.name.startswith("LED:"):
                node, color_prop, strength_prop = find_emission_control_node(material)
                if node and strength_prop:
                    node.inputs[strength_prop].default_value = 10.0
        
        bpy.context.view_layer.update()
        return {'FINISHED'}
    
    
#Emission Hide    
class kh_ShaderNodeEmissionHide(bpy.types.Operator):
    bl_idname = "object.shader_node_emission_hide"
    bl_label = "Keyframe Emission Strength & Strength"
    
    material_name: bpy.props.StringProperty()
    
    def execute(self, context):
        for material in bpy.data.materials:
            if material.name.startswith("LED:"):
                node, color_prop, strength_prop = find_emission_control_node(material)
                if node and strength_prop:
                    node.inputs[strength_prop].default_value = 0.0
        
        bpy.context.view_layer.update()
        return {'FINISHED'}
    
#Delete the K-Frame
class kh_ShaderNodeEmissionKeyframeDelete(bpy.types.Operator):
    bl_idname = "object.shader_node_emission_keyframe_delete"
    bl_label = "Delete the K-Frame"
    material_name: bpy.props.StringProperty()
    def execute(self, context):
        
        materials = bpy.data.materials
        for material in materials:
            if material.name.startswith("LED:"):
                node, color_prop, strength_prop = find_emission_control_node(material)
                if node and color_prop:
                    node.inputs[color_prop].default_value = (
                        material.diffuse_color[0],
                        material.diffuse_color[1],
                        material.diffuse_color[2],
                        1.0  # Alpha value
                    )
                                        
        return {'FINISHED'}

    
#Emission name 
class kh_ShaderNodeEmissionName(bpy.types.Operator):
    bl_idname = "object.shader_node_emission_name"
    bl_label = "Keyframe Emission Strength & Strength"
    
    material_name: bpy.props.StringProperty()
    
    def execute(self, context):
        if bpy.context.selected_objects:
            selected_object = bpy.context.selected_objects[0]
            if selected_object.active_material:
                material_name = selected_object.active_material.name
                if not material_name.startswith("LED:"):
                    selected_object.active_material.name = ("LED: ")+ material_name

                material = selected_object.active_material
                if material.node_tree:
                    for node in material.node_tree.nodes:
                        if node.type == 'BLACKBODY':
                            material.node_tree.nodes.remove(node)

        return {'FINISHED'}
    
# ALL Emission name 
class kh_ShaderNodeEmissionName_ALL(bpy.types.Operator):
    bl_idname = "object.shader_node_emission_name_all"
    bl_label = "Keyframe Emission Strength & Strength"
    material_name: bpy.props.StringProperty()
    def execute(self, context):
        all_MESH = [obj for obj in bpy.data.objects if obj.type == 'MESH' and (
        any(node.type == 'BSDF_PRINCIPLED' for mat_slot in obj.material_slots if mat_slot.material for node in (mat_slot.material.node_tree.nodes if mat_slot.material.node_tree else [])) or
        any(node.type == 'EMISSION' for mat_slot in obj.material_slots if mat_slot.material for node in (mat_slot.material.node_tree.nodes if mat_slot.material.node_tree else []))
        )]
        for obj in all_MESH:
            if obj.hide_render or (obj.users_collection and obj.users_collection[0].hide_render):
                continue 
            if obj.type == 'MESH' :
                for material_slot in obj.material_slots:
                    material = material_slot.material
                    if material and material.name in obj.data.materials:
                        principled_bsdf = None
                        if material.use_nodes:
                            for node in material.node_tree.nodes:
                                if node.type == 'BSDF_PRINCIPLED':
                                    principled_bsdf = node
                                    break
                        if principled_bsdf:
                            active_material = material_slot.material
                            nodes = active_material.node_tree.nodes   
                            bsdf_node = None 
                            for node in nodes: 
                                if node.type == 'BSDF_PRINCIPLED':
                                    bsdf_node = node 
                            if bsdf_node is not None:
                                if bsdf_node:
                                    if 'Emission Color' in bsdf_node.inputs:
                                        emission_input = bsdf_node.inputs['Emission Color']
                                        if tuple(principled_bsdf.inputs["Emission Color"].default_value) != (0, 0, 0, 1) or emission_input.is_linked:
                                            if principled_bsdf.inputs["Emission Strength"].default_value != 0:
                                                if not material.name.startswith("LED:"):
                                                    material.name = ("LED: ")+ material.name
                                                    for node in material.node_tree.nodes:
                                                        if node.type == 'BLACKBODY':
                                                            material.node_tree.nodes.remove(node)
                                                            principled_bsdf.inputs["Emission Color"].default_value = (1, 1, 1, 1)
                                    else:
                                        emission_input = bsdf_node.inputs['Emission']
                                        if tuple(principled_bsdf.inputs["Emission"].default_value) != (0, 0, 0, 1) or emission_input.is_linked:
                                            if principled_bsdf.inputs["Emission Strength"].default_value != 0:
                                                if not material.name.startswith("LED:"):
                                                    material.name = ("LED: ")+ material.name
                                                    for node in material.node_tree.nodes:
                                                        if node.type == 'BLACKBODY':
                                                            material.node_tree.nodes.remove(node)
                                                            principled_bsdf.inputs["Emission"].default_value = (1, 1, 1, 1)
                                                            
                        emission = None             
                        if material.use_nodes:
                            for node in material.node_tree.nodes:
                                if node.type == 'EMISSION':
                                    emission = node
                                    break            
                        if emission:
                            if tuple(emission.inputs[0].default_value) != (0, 0, 0, 1) or emission.inputs[0].is_linked :
                                if emission.inputs[1].default_value != 0:
                                    if not material.name.startswith("LED:"):
                                        material.name = ("LED: ")+ material.name
                                        for node in material.node_tree.nodes:
                                            if node.type == 'BLACKBODY':
                                                material.node_tree.nodes.remove(node)
                                                emission.inputs[0].default_value = (1, 1, 1, 1) 
        
        return {'FINISHED'}
    
# Dome_light //////////////////////////////////////////////////////////////////////////////////////////////////
def update_dome_light(self, context):
    if self.dome_light_enabled:
        bpy.ops.object.dome_light()
    else:
        bpy.ops.object.delete_dome_light()

preview_collection1= bpy.utils.previews.new()
preview_collection1.load("31.png", os.path.join(my_icons_dir, "31.png"), 'IMAGE')

class AddDomeLightPanel(bpy.types.Panel):
    bl_idname = "VIEW_3D_PT_add_dome_light"
    bl_label = ""
    #bl_space_type = "VIEW_3D"
    #bl_region_type = "UI"
    #bl_category = "KH-Tools"
    #bl_parent_id = "VIEW3D_PT_light_manager"
    #bl_options = {'DEFAULT_CLOSED'}

    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "world"
    #bl_parent_id = "GAFFER_PT_hdris"
    
    bpy.types.Scene.create_dome_light = bpy.props.BoolProperty(name="Create Dome Light", default=False)
    bpy.types.Scene.delete_dome_light = bpy.props.BoolProperty(name="Delete Dome Light", default=False)


    @classmethod
    def poll(cls, context):
        # استخدام الدالة المساعدة للبحث عن إعدادات الإضافة
        return get_addon_preferences(context, 'DOME_LIGHT') == True

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.prop(context.scene, "dome_light_enabled", text="")
            self.layout.label(text="DOME LIGHT", icon_value=preview_collection1['31.png'].icon_id)
            
            
            if 'Dome Light' in bpy.data.objects:    
                dome_light = bpy.data.objects['Dome Light']
                if  dome_light.hide_viewport:
                    #self.layout.label(text="Night" , icon= "COLORSET_06_VEC")
                    self.layout.operator("object.activate_dom_day", text="Night", icon="COLORSET_06_VEC")
                else:
                    self.layout.operator("object.activate_dom_night", text="Day", icon="COLORSET_09_VEC")
                
        except KeyError:
            pass

    def draw(self, context):   
        layout = self.layout
        row = layout.row()
        if 'Dome Light' not in bpy.data.objects:
            row = layout.row()
            #row.operator("object.dome_light", text="Create Dome Light", icon="LIGHT_HEMI")
        else:
            scene= bpy.context.scene  
            row = layout.row()
            #row.operator("object.delete_dome_light", text="Delete", icon="TRASH")
            active_world = bpy.context.scene.world
            if active_world is not None:
                world_mapping_node = None
                for node1 in active_world.node_tree.nodes:
                    if node1.type == 'MAPPING':
                        world_mapping_node = node1
                        break
                if world_mapping_node is not None:
                    row.prop(context.scene,"lunk_dom", text = 'World', icon = 'LINK_BLEND')
            
                    if not scene.link_dome_mapping:
                        row.prop(scene, "link_dome_mapping", text="Rotation" , icon = 'LINK_BLEND')               
                    else:
                        row.prop(scene, "link_dome_mapping", text="Rotation" , icon = 'LINK_BLEND')
                
            row.operator("object.reset_dome_light", text="Reset", icon="FILE_REFRESH")

            dome_light = bpy.data.objects['Dome Light']
            if not dome_light.hide_viewport:
                material = bpy.data.materials.get("Dome Light")
            else:
                material = bpy.data.materials.get("Dome Light-N")

            scn = context.scene
            favs = get_favs()
            dir = bpy.path.abspath(scn.previews_dir)
            recursion = scn.recursive_search
            layout = self.layout        
            col = layout.column(align=True)
            active_hdr = ''
            prev_list = 0        
            
            if 'previews_list' in scn:
                prev_list = len(scn['previews_list'])
            
            if len(preview_collections2["prev"]) > 0 and prev_list > 0:
                active_hdr = scn.prev        
            if scn.render.engine in ['CYCLES', 'BLENDER_EEVEE'] and not scene.lunk_dom :
                
                row = col.row(align=True)
                if os.path.exists(dir):
                    if not dir in favs:
                        row.operator("easyhdr.add_to_fav", text = '', icon = 'SOLO_ON')
                    else: 
                        row.operator("easyhdr.remove_from_fav", text = '', icon = 'X')
                         
                row.prop(scn, "previews_dir", text = '')
                row.prop(scn, 'favs', text = '', icon = 'SOLO_OFF', icon_only=True) 
                if recursion:
                    col.prop(scn, "sub_dirs", text = 'Recursion level')

                if not scene.lunk_dom : 
                    if len(preview_collections2["prev"]) > 0 and prev_list > 0:                             
                        row = layout.row()
                        row.template_icon_view(scn, "prev", show_labels=True, scale = 10)
                        col = row.column(align=True)
                        col.operator("easyhdr.reload_previews", text = '',  icon = 'FILE_REFRESH')
                        col.menu("EASYHDRI_MT_settings_menu", text = '', icon = 'TOOL_SETTINGS')
                    else:
                        col.label(text = 'HDRI folder is not selected', icon = 'ERROR') 
                        
                col = layout.column()                             
                if len(preview_collections2["prev"]) > 0 and prev_list > 0:
                    box = col.box() 
                    box.scale_y = 1.0                             
                    row = box.row(align = True)
                    row.scale_y = 1.2
                    row.operator("easyhdr.previous", text = '',  icon = 'TRIA_LEFT')
                   
                    if len(preview_collections2["prev"]) > 0 and prev_list > 0:
                        row.label(text = active_hdr, icon = 'IMAGE_DATA')  
                    row.operator("easyhdr.next", text = '', icon = 'TRIA_RIGHT')
               
            box = layout.box()
            for obj in bpy.context.scene.objects:
                if obj.name.startswith("Dome Light") and obj.hide_viewport != True:
                    row = box.row()
                    row.prop(obj, "display_type", text="") 
                    break    
                                  
            node_tree = material.node_tree
            for node in node_tree.nodes:
                if node.type == "MAPPING":
                    row = box.row()
                    if not scene.link_dome_mapping:
                        row.prop(node.inputs["Rotation"], "default_value", index=2, text="Rotation")
                      
            node_tree = material.node_tree
            for node in node_tree.nodes:
                if node.type == 'EMISSION':
                    hue_saturation_node = node 
                    pass
            if hue_saturation_node is not None:
                row.prop(hue_saturation_node.inputs[1], "default_value", text="Strength")
                
            for obj in bpy.context.scene.objects:
                if obj.name.startswith("Dome Light") and obj.hide_viewport != True:
                    node_tree = material.node_tree
                    for node in node_tree.nodes:
                        if node.type == 'GAMMA':
                            gamma_node = node 
                            pass
                    node_tree = material.node_tree
                    color_node = None 
                    for node in node_tree.nodes:
                        if node.label == 'Color Multiply':
                            color_node = node
                            pass

                    layout = self.layout
                    active_material = material
                    nodes = active_material.node_tree.nodes   
                    bright_contrast_node = None 
                    for node in nodes: 
                        if node.type == 'HUE_SAT':
                            bright_contrast_node = node 
                            pass
                        
                    if bright_contrast_node is not None:
                        row = box.row()
                        #col.prop(hue_saturation_node.inputs[1], "default_value", text="Strength")
                        row.prop(obj, "location",index=2, text="Hight")
                        row.prop(gamma_node.inputs[1], "default_value", text="Gamma")
                        row = box.row()
                        row.prop(bright_contrast_node.inputs[2], "default_value", text="Value")
                        row.prop(bright_contrast_node.inputs[1], "default_value", text="Saturation")
                        row = box.row()
                        row.prop(color_node.inputs[2], "default_value", text = "") 
                        row.prop(color_node.inputs[0], "default_value", text = "Color Strength")

                        #col.prop(bright_contrast_node.inputs[0], "default_value", text="Color")            
                        #col.prop(bright_contrast_node.inputs[3], "default_value", text="Effect")  
                    row = box.row()
                    #row.prop(obj, "visible_shadow", text="Shadow")
                    row.prop(obj, "visible_transmission", text="Transmission")
                    #row.prop(obj, "visible_diffuse", text="Diffuse")
                    row.prop(obj, "visible_glossy", text="Glossy")
                    row.prop(obj, "visible_camera", text="camera")
                    

class DoomLitePanel(bpy.types.Panel):
    bl_idname = "DOOM_PT_panel"
    bl_label = "MAPPING"
    #bl_space_type = "VIEW_3D"
    #bl_region_type = "UI"
    bl_category = "Dome light"
    bl_parent_id = "VIEW_3D_PT_add_dome_light"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "world"

    @classmethod
    def poll(cls, context):
        return any(obj.name == "Dome Light" for obj in bpy.context.scene.objects)

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon='STICKY_UVS_LOC')
        except KeyError:
            pass
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        if 'Dome Light' in bpy.data.objects:
            dome_light = bpy.data.objects['Dome Light']
            if not dome_light.hide_viewport:
                mat = bpy.data.materials.get("Dome Light")
            else:
                mat = bpy.data.materials.get("Dome Light-N")
 
            mapping_nodes = [node for node in mat.node_tree.nodes if node.type == 'MAPPING']
            for i, mapping_node in enumerate(mapping_nodes):
                if i >= len(mapping_nodes):
                    break

                if mapping_node:     
                    row = layout.row()
                    row.label(text=f"Location" , icon='CON_LOCLIMIT')
                    row.label(text=f"Scale" , icon='FULLSCREEN_EXIT')
                    for j in range(3):
                        row = layout.row()
                        row.prop(mapping_node.inputs[1], "default_value", index=j, text=f"{['X', 'Y', 'Z'][j]}")
                        row.prop(mapping_node.inputs[3], "default_value", index=j, text=f"{['X', 'Y', 'Z'][j]}")
                        
        else:
            layout.label(text="No material named 'Dome Light' found in scene.")


# MAPPING_linke_dom
#-------------------------------------------------------------------------------
# def driver_add():
#     if 'Dome Light' in bpy.data.objects:
#         dome_light = bpy.data.objects['Dome Light']
#         if not dome_light.hide_viewport:
#             material = bpy.data.materials.get("Dome Light") 
#         else:
#             material = bpy.data.materials.get("Dome Light-N")             
    
#         if material is not None and material.node_tree is not None:
#             mapping_node_material = None
#             for node in material.node_tree.nodes:
#                 if node.type == 'MAPPING':
#                     mapping_node_material = node
#                     break
#             if mapping_node_material is not None:      
#                 if bpy.context.scene.world is not None:
#                     world = bpy.context.scene.world
#                     mapping_node_world = None
#                     for node in world.node_tree.nodes:
#                         if node.type == 'MAPPING':
#                             mapping_node_world = node
#                             break
#                     if mapping_node_world is not None:
#                         input_index = 2 
#                         driver_material = mapping_node_material.inputs[input_index].driver_add("default_value", 2).driver
#                         driver_material.type = 'AVERAGE'
#                         driver_material_variable = driver_material.variables.new()
#                         driver_material_variable.name = "world_driver"
#                         driver_material.expression = "world_driver"
#                         world = bpy.context.scene.world
#                         driver_material_variable.targets[0].id_type = "WORLD"
#                         driver_material_variable.targets[0].id = world      
#                         driver_material_variable.targets[0].data_path = f"node_tree.nodes[\"{mapping_node_world.name}\"].inputs[{input_index}].default_value[2]"
                        
def driver_dome_add_h(scene):
    if scene.link_dome_mapping:
        if 'Dome Light' in bpy.data.objects:
            dome_light = bpy.data.objects['Dome Light']
            if not dome_light.hide_viewport:
                material = bpy.data.materials.get("Dome Light") 
            else:
                material = bpy.data.materials.get("Dome Light-N")             
        
            if material is not None and material.node_tree is not None:
                mapping_node_material = None
                for node in material.node_tree.nodes:
                    if node.type == 'MAPPING':
                        mapping_node_material = node
                        break
                if mapping_node_material is not None:      
                    if bpy.context.scene.world is not None:
                        world = bpy.context.scene.world
                        mapping_node_world = None
                        for node in world.node_tree.nodes:
                            if node.type == 'MAPPING':
                                mapping_node_world = node
                                break
                        if mapping_node_world is not None:
                            mapping_node_material.inputs[2].default_value[2] = mapping_node_world.inputs[2].default_value[2] 
                
                
                
#bpy.app.handlers.depsgraph_update_post.append(driver_world_add_heder) 
def check_dome_rotation(scene):
    kh_sun = None
    # Check if world and node_tree exist
    if not scene.world or not scene.world.node_tree:
        return None
    
    for node in bpy.context.scene.world.node_tree.nodes:
        if node.type == 'MAPPING':
            kh_sun = node
            break
    if kh_sun:
        return kh_sun.inputs[2].default_value[2]
    return None

@persistent
def check_dome_rotation_callback(scene, depsgraph):
    current_rotation = check_dome_rotation(scene)
    if current_rotation is not None and current_rotation != getattr(check_dome_rotation_callback, "prev_rotation", None):
        check_dome_rotation_callback.prev_rotation = current_rotation
        driver_dome_add_h(scene)

# MAPPING_delete_linke_dom
#-------------------------------------------------------------------------------
# def delete_driver():
#     if 'Dome Light' in bpy.data.objects:
#         dome_light = bpy.data.objects['Dome Light']
#         if not dome_light.hide_viewport:
#             material = bpy.data.materials.get("Dome Light") 
#         else:
#             material = bpy.data.materials.get("Dome Light-N")
             
#         if material is not None and material.node_tree is not None:
#             mapping_node_material = None
#             for node in material.node_tree.nodes:
#                 if node.type == 'MAPPING':
#                     mapping_node_material = node
#                     break
#             if mapping_node_material is not None:
#                 input_index = 2
#                 mapping_node_material.inputs[input_index].driver_remove("default_value")


#COPY HDRI---------------------------------------------------------------------------------
def find_tex_environment_node(world):
    if world is not None:
        for node in world.node_tree.nodes:
            if node.type == 'TEX_ENVIRONMENT':
                return node
    return None

def find_dome_light_material():
    if 'Dome Light' in bpy.data.objects:
        dome_light = bpy.data.objects['Dome Light']
        if not dome_light.hide_viewport:
            dome_light_material_name = "Dome Light"
        else:
            dome_light_material_name = "Dome Light-N"
        for material in bpy.data.materials:
            if material.name == dome_light_material_name:
                return material
    return None

def copy_environment_texture():
    world = bpy.context.scene.world
    tex_environment_node = find_tex_environment_node(world)
    if tex_environment_node:
        dome_light_material = find_dome_light_material()
        if dome_light_material:
            tex_image_node = None
            for node in dome_light_material.node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    tex_image_node = node
                    break
            if tex_image_node:
                if tex_image_node.image != tex_environment_node.image:
                    tex_image_node.image = tex_environment_node.image

@persistent
def handle_environment_texture_change(scene):
    if scene.lunk_dom:
        copy_environment_texture()
        
 
def add_dome_HDRI(): 
    material_name = "Dome Light"
    image_texture_node_name = "Image Texture"
    script_dir = os.path.dirname(os.path.realpath(__file__))
    folder_path = os.path.join(script_dir, "asset")
    file_name = "Day-2K.exr"
    default_image_path = os.path.join(folder_path, file_name)

    def find_material(material_name):
        for material in bpy.data.materials:
            if material.name == material_name:
                return material
        return None

    def find_image_texture_node(material):
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.name == image_texture_node_name:
                return node
        return None

    material = find_material(material_name)
    if material:
        image_texture_node = find_image_texture_node(material)
        if image_texture_node:
            if not image_texture_node.image:
                image_path = default_image_path
                if os.path.exists(image_path):
                    bpy.ops.image.open(filepath=image_path)
                    image_texture_node.image = bpy.data.images.get(os.path.basename(image_path))
                    
def add_dome_HDRI_N(): 
    material_name = "Dome Light-N"
    
    script_dir = os.path.dirname(os.path.realpath(__file__))
    folder_path = os.path.join(script_dir, "asset")
    file_name = "Night-2K.hdr"
    default_image_path = os.path.join(folder_path, file_name)

    def find_material(material_name):
        for material in bpy.data.materials:
            if material.name == material_name:
                return material
        return None

    def find_image_texture_node(material):
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE' :
                return node
        return None

    material = find_material(material_name)
    if material:
        image_texture_node = find_image_texture_node(material)
        if image_texture_node:
            #if not image_texture_node.image:
                image_path = default_image_path
                if os.path.exists(image_path):
                    bpy.ops.image.open(filepath=image_path)
                    image_texture_node.image = bpy.data.images.get(os.path.basename(image_path))
    
          
#ADD DOOM
def add_dome_light(self, context):
    if bpy.context.active_object:
        if bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
            
    if "Dome Light" in bpy.data.materials:
        mat = bpy.data.materials["Dome Light"]
    else:
        mat = bpy.data.materials.new(name="Dome Light")
        mat.use_nodes = True
        for node in mat.node_tree.nodes:
            if node.type == 'OUTPUT_MATERIAL':
                mat.node_tree.nodes.remove(node)
        for node in mat.node_tree.nodes:                        
            if node.type == 'BSDF_PRINCIPLED':
                mat.node_tree.nodes.remove(node)

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        Bsdf_node = nodes.new(type='ShaderNodeEmission')
        #Bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
        TexImage_node = nodes.new(type="ShaderNodeTexImage")
        TexImage_node.projection = 'SPHERE'
        group_Mapping = nodes.new(type="ShaderNodeMapping")
        group_Mapping.inputs[1].default_value[2] = 20.0
        group_Mapping.vector_type = 'TEXTURE'

        group_TexCoord = nodes.new(type="ShaderNodeTexCoord")
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        Saturation_node = nodes.new(type='ShaderNodeHueSaturation')
        BrightContrast_node = nodes.new(type='ShaderNodeGamma')
        color_node = nodes.new(type="ShaderNodeMixRGB")
        
        color_node.label = 'Color Multiply'  
        color_node.blend_type = 'MULTIPLY'  
        color_node.inputs[0].default_value = 0.0
        
        links.new(Bsdf_node.outputs[0], output_node.inputs[0])
        links.new(group_TexCoord.outputs[3], group_Mapping.inputs[0])
        links.new(color_node.outputs[0], Saturation_node.inputs[4])
        links.new(Saturation_node.outputs[0], BrightContrast_node.inputs[0])
        links.new(BrightContrast_node.outputs[0], Bsdf_node.inputs[0])
        links.new(group_Mapping.outputs[0], TexImage_node.inputs[0])
        links.new(TexImage_node.outputs[0], color_node.inputs[1])
        Saturation_node.inputs[2].default_value = 1
        Bsdf_node.location = (-500, 0)
        group_TexCoord.location = (-2000, 0)
        group_Mapping.location = (-1800, 0)
        output_node.location = (-100, 0)
        TexImage_node.location = (-1500, 0)
        color_node.location = (-1200, 0)
        Saturation_node.location = (-1000, 0)
        BrightContrast_node.location = (-800, 0)

    for obj in bpy.data.objects:
        if obj.name == "Dome Light":
            self.report({'ERROR'}, "Dome Light already exists in the scene")
            return {'CANCELLED'}

    bpy.ops.mesh.primitive_uv_sphere_add(radius=300, enter_editmode=False, location=context.scene.cursor.location)
    dome_light = context.active_object 
    dome_light.name = "Dome Light"
    try:
        bpy.ops.object.shade_smooth(use_auto_smooth=True)
    except TypeError:
        bpy.ops.object.shade_smooth_by_angle()
    bpy.context.active_object.display_type = 'BOUNDS'
    bool_modifier = dome_light.modifiers.new(name="Boolean", type='BOOLEAN')
    bool_modifier.operation = 'DIFFERENCE'
    dome_light.data.materials.append(mat)
    bpy.context.active_object.active_material = mat
    bpy.ops.mesh.primitive_plane_add(size=900, enter_editmode=False, location=context.scene.cursor.location)
    plane = context.active_object 
    plane.name = "BL"
    bool_modifier.object = plane
    bpy.context.view_layer.objects.active = dome_light
    bool_modifier_apply = bpy.ops.object.modifier_apply(modifier="Boolean")
    bpy.ops.object.delete(use_global=False, confirm=False)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.active_object.location[2] -= 0.01
    bpy.context.active_object.rotation_euler[2] = 4.71239
    bpy.context.active_object.scale[0] = -1
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.active_object.visible_shadow = False
    bpy.context.active_object.visible_diffuse = False
    bpy.context.active_object.visible_glossy = False
    bpy.context.active_object.visible_transmission = False
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, properties=True)
    obj = context.active_object
    collection_name = "Dome Light"
    collection = bpy.data.collections.get(collection_name)
    if collection is None:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
    obj.users_collection[0].objects.unlink(obj)
    collection.objects.link(obj)

    #COPY HDRI                 
    copy_environment_texture()
    
    material_name = "Dome Light"
    material = bpy.data.materials.get(material_name)
    if material is not None:
        active_world = bpy.context.scene.world
        if active_world is not None:
            world_mapping_node = None
            for node in active_world.node_tree.nodes:
                if node.type == 'MAPPING':
                    world_mapping_node = node
                    break
            if world_mapping_node is not None:
                material_mapping_node = None
                for node in material.node_tree.nodes:
                    if node.type == 'MAPPING':
                        material_mapping_node = node
                        break
                if material_mapping_node is not None:
                    material_mapping_node.inputs[2].default_value = world_mapping_node.inputs[2].default_value
    add_dome_HDRI()               
                        
def Dome_Light_N():
    collection_name = "Dome Light"
    if collection_name in bpy.data.collections:
        if not "Dome Light-N" in bpy.data.collections[collection_name].objects:
            for obj in bpy.data.collections[collection_name].objects:
                if obj.name == "Dome Light" :
                    new_obj = obj.copy()
                    new_obj.data = obj.data.copy()
                    new_obj.name = "Dome Light-N"
                    new_material = obj.data.materials[0].copy()
                    new_material.name = "Dome Light-N"  
                    new_obj.data.materials.clear()
                    new_obj.data.materials.append(new_material)
                    bpy.data.collections[collection_name].objects.link(new_obj)
                    new_obj.hide_viewport = True
                    new_obj.hide_render = True
                    add_dome_HDRI_N()
                    break
    
    

class OBJECT_OT_dome_light(bpy.types.Operator):
     """Add a UV Sphere with radius 300 and apply emission shader"""
     bl_idname = "object.dome_light"
     bl_label = "Dome Light"
    
     def execute(self, context):
        #ADD DOOM
        add_dome_light(self, context)
        #delete_driver()
        #driver_add()
        Dome_Light_N()
        bpy.ops.easyhdr.reload_previews()
        return {'FINISHED'}
    
#Reset Dome Light                    
class Reset_DomeLightOperator(bpy.types.Operator):
    """Reset Dome Light"""
    bl_idname = "object.reset_dome_light"
    bl_label = "Reset Dome Light"
    
    def execute(self, context):
        #DELETE
        bpy.ops.object.delete_dome_light()

        #ADD DOOM
        add_dome_light(self, context)
        #delete_driver() 
        #driver_add()
        Dome_Light_N()
        return {'FINISHED'} 

#Delete Dome Light                    
class DeleteDomeLightOperator(bpy.types.Operator):
    """Delete Dome Light"""
    bl_idname = "object.delete_dome_light"
    bl_label = "Delete Dome Light"

    def execute(self, context):
        if bpy.context.active_object:
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
                
        scene = context.scene
        dome_light = scene.objects.get("Dome Light")
        if dome_light:
            bpy.ops.object.select_all(action='DESELECT')
            dome_light.select_set(True)
            bpy.ops.object.delete(use_global=False)
            
        collection_name = "Dome Light"
        collection = bpy.data.collections.get(collection_name)
        if collection:
            bpy.data.collections.remove(collection, do_unlink=True)
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            self.report({'INFO'}, f"{collection_name} collection deleted")

        material_name_to_delete = "Dome Light"
        for obj in bpy.data.objects:
            if obj.data:
                for material_slot in obj.material_slots:
                    if material_slot.material and material_slot.material.name == material_name_to_delete:
                        bpy.data.materials.remove(material_slot.material)

        return {'FINISHED'} 
 
 # تبديل الدوم
#-------------------------------------------------------------------------------
class Activate_Dom_Nightly(bpy.types.Operator):
    bl_idname = "object.activate_dom_night"
    bl_label = "Activate Dome Nigh"
    def execute(self, context):
        if bpy.context.scene.lunk_dom:
            bpy.context.scene.lunk_dom = False
        if 'Dome Light' in bpy.data.objects:
            dome_light = bpy.data.objects['Dome Light']
            dome_light.hide_viewport = True
            dome_light.hide_render = True
        if 'Dome Light-N' in bpy.data.objects:
            cube_light_night = bpy.data.objects['Dome Light-N']
            cube_light_night.hide_viewport = False
            cube_light_night.hide_render = False  
        return {'FINISHED'}
    
class Activate_Dom_day(bpy.types.Operator):
    bl_idname = "object.activate_dom_day"
    bl_label = "Activate Dome day"
    def execute(self, context):
        if bpy.context.scene.lunk_dom:
            bpy.context.scene.lunk_dom = False
        if 'Dome Light' in bpy.data.objects:
            dome_light = bpy.data.objects['Dome Light']
            dome_light.hide_viewport = False
            dome_light.hide_render = False
        if 'Dome Light-N' in bpy.data.objects:
            cube_light_night = bpy.data.objects['Dome Light-N']
            cube_light_night.hide_viewport = True
            cube_light_night.hide_render = True 
        return {'FINISHED'}   

#درايفر
#-------------------------------------------------------------------------------
# class Link_DomeLight_driver(bpy.types.Operator):
#     """Link Dome Light"""
#     bl_idname = "object.dome_driver_add"
#     bl_label = "Link Rotation"
    
#     def execute(self, context):
#         driver_add()
#         return {'FINISHED'} 
     
class DeleteDomeLight_driver(bpy.types.Operator):
    """Delete Dome Light"""
    bl_idname = "object.delete_dome_driver"
    bl_label = "Delete Link Rotation"
    
    def execute(self, context):
        #delete_driver()
        material_name = "Dome Light"
        material = bpy.data.materials.get(material_name)
        if material is not None:
            active_world = bpy.context.scene.world
            if active_world is not None:
                world_mapping_node = None
                for node in active_world.node_tree.nodes:
                    if node.type == 'MAPPING':
                        world_mapping_node = node
                        break
                if world_mapping_node is not None:
                    material_mapping_node = None
                    for node in material.node_tree.nodes:
                        if node.type == 'MAPPING':
                            material_mapping_node = node
                            break
                    if material_mapping_node is not None:
                          material_mapping_node.inputs[2].default_value[2] += 0.1

        
        return {'FINISHED'}   

# Load an empty list(First launch)
def env_previews(self, context):  
    pcoll1 = preview_collections2.get("prev")
    if not pcoll1:
        return []
    return pcoll1.prev

def get_hdris(dir, level = 1):    
    assert os.path.isdir(dir)
    num_sep = dir.count(os.path.sep)
    hdris = []
    for root, dirs, files in os.walk(dir):
        for fn in files:
            if fn.lower().endswith(".hdr") or fn.lower().endswith(".exr"):
                hdris.append(os.path.join(root, fn).replace(dir, ''))            
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]
    return hdris       
   
# Update the previews list if the folder changes
def update_dir(self, context):
    scn = bpy.context.scene
    enum_items = []
    if not 'previews_dir' in scn:
        scn['previews_dir'] = ''
    if not 'previews_list' in scn:
        scn['previews_list'] = []
    if not 'sub_dirs' in scn:
        scn['sub_dirs'] = 0  
    if not 'recursive_search' in scn:
        scn['recursive_search'] = 0              
    scn['previews_list'] = []
    
    previews_list = []
    recursion_level = scn.sub_dirs
    recursion = scn.recursive_search        
    previews_folder = bpy.path.abspath(scn['previews_dir'])
    pcoll1 = preview_collections2["prev"]    
    if os.path.exists(bpy.path.abspath(previews_folder)):
        if recursion:
            image_paths = get_hdris(previews_folder, recursion_level)        
        else: image_paths = get_hdris(previews_folder, 0)    
        for i, name in enumerate(image_paths):            
            filepath = os.path.join(previews_folder, name)
            if not pcoll1.get(filepath):
                thumb = pcoll1.load(filepath, filepath, 'IMAGE')
            else: thumb = pcoll1[filepath]   
            enum_items.append((name, name, name, thumb.icon_id, i))
            previews_list.append(name)
        scn['previews_list'] = previews_list    
    pcoll1.prev = enum_items
    pcoll1.previews_dir = previews_folder
    if len(previews_list) > 0:
        scn.prev = previews_list[0]       
    return None

# Update the material texture
def update_hdr(self, context):
    scn = bpy.context.scene
    dynamic = scn.dynamic_load
    dynamic_cleanup = scn.dynamic_cleanup
    sub_path = scn.prev
    set_projection = scn.set_projection
    image = os.path.basename(sub_path)
    images = bpy.data.images
    scn['previews_dir'] = bpy.path.abspath(scn.previews_dir)
    path = bpy.path.abspath(scn.previews_dir)

    if 'Dome Light' in bpy.data.objects:    
        obj = bpy.data.objects['Dome Light']
        if  obj.hide_viewport == False:
                if 'Dome Light' in obj.data.materials and dynamic:
                    for mat_slot in obj.material_slots:
                        if mat_slot.material.name == 'Dome Light':
                            nodes = mat_slot.material.node_tree.nodes
                            if 'Image Texture' in nodes:
                                env = nodes['Image Texture']
                                if image in images:
                                    env.image = images[image]
                                    if dynamic_cleanup:
                                        cleanup_images()
                                    if set_projection:
                                        x, y = images[image].size
                                        if x == y:
                                            env.projection = 'MIRROR_BALL'
                                        else:
                                            env.projection = 'EQUIRECTANGULAR'
                                else:
                                    if os.path.exists(path):
                                        if os.access(os.path.join(path, sub_path), os.F_OK):
                                            filepath = os.path.join(path, sub_path)
                                            images.load(filepath)
                                            if image in images:
                                                env.image = images[image]
                                                if dynamic_cleanup:
                                                    cleanup_images()
                                                if set_projection:
                                                    x, y = images[image].size
                                                    if x == y:
                                                        env.projection = 'MIRROR_BALL'
                                                    else:
                                                        env.projection = 'EQUIRECTANGULAR'
        else:
            obj = bpy.data.objects['Dome Light-N']
            if  obj.hide_viewport == False:
                    if 'Dome Light-N' in obj.data.materials and dynamic:
                        for mat_slot in obj.material_slots:
                            if mat_slot.material.name == 'Dome Light-N':
                                nodes = mat_slot.material.node_tree.nodes
                                if 'Image Texture' in nodes:
                                    env = nodes['Image Texture']
                                    if image in images:
                                        env.image = images[image]
                                        if dynamic_cleanup:
                                            cleanup_images()
                                        if set_projection:
                                            x, y = images[image].size
                                            if x == y:
                                                env.projection = 'MIRROR_BALL'
                                            else:
                                                env.projection = 'EQUIRECTANGULAR'
                                    else:
                                        if os.path.exists(path):
                                            if os.access(os.path.join(path, sub_path), os.F_OK):
                                                filepath = os.path.join(path, sub_path)
                                                images.load(filepath)
                                                if image in images:
                                                    env.image = images[image]
                                                    if dynamic_cleanup:
                                                        cleanup_images()
                                                    if set_projection:
                                                        x, y = images[image].size
                                                        if x == y:
                                                            env.projection = 'MIRROR_BALL'
                                                        else:
                                                            env.projection = 'EQUIRECTANGULAR'   
        return None

# Update the preview directory when the favorites change
def update_favs(self, context):
    scn = context.scene 
    favs = scn.favs
    if not favs in ['Empty', '']:
        scn.previews_dir = favs
    return None

# Remove unused images 
def cleanup_images():
    images = bpy.data.images
    for image in images:
        if image.users == 0:
            images.remove(image)

# Get the list of favorites (enum)
def get_favs_enum(self, context):
    dirs = get_favs()
    if len(dirs) > 0:
        return [(i, i, '') for i in dirs]
    else: return [('Empty', '__Empty__', '')]

# return the list of favorites
def get_favs():
    dirs = []
    fav_file = os.path.join(addon_dir, "Favorites.fav")
    if os.path.exists(fav_file):    
        with open(fav_file, 'r') as ff:
            lines = ff.read()
            fav_dirs = lines.splitlines()
            dirs = [i for i in fav_dirs if i.strip() != '']
    return dirs

################################### Operators #############################################
# Add to favorites
class EASYHDRI_OT_add_to_fav(Operator):
    bl_idname = "easyhdr.add_to_fav"
    bl_label = "Add to fav"
    bl_options = {'UNDO'}
    bl_description = "Add the current folder to the favorites"

    def execute(self, context):
        scn = context.scene
        new_fav = bpy.path.abspath(scn.previews_dir)
        fav_file = os.path.join(addon_dir, "Favorites.fav")
        if os.path.exists(new_fav):
            if not os.path.exists(fav_file):
                with open(fav_file, 'w') as ff:
                    ff.write('')            
            dirs = get_favs()
            if not new_fav in dirs:
                dirs.append(new_fav)
                with open(fav_file, 'w') as ff:
                    for d in dirs:
                        if d : ff.write(d + '\n')
        else: self.report({'WARNING'}, 'Directory not found !')                       
                
        return {'FINISHED'}
    
# Remove from favorites
class EASYHDRI_OT_remove_from_fav(Operator):
    bl_idname = "easyhdr.remove_from_fav"
    bl_label = "Remove"
    bl_options = {'UNDO'}
    bl_description = "Remove the current folder from the favorites"

    def execute(self, context):
        scn = context.scene
        dir = bpy.path.abspath(scn.previews_dir)
        fav_file = os.path.join(addon_dir, "Favorites.fav")                    
        dirs = get_favs()
        dirs.remove(dir)
        with open(fav_file, 'w') as ff:
            for d in dirs:
                if d : ff.write(d + '\n')                            
        return {'FINISHED'}          
    

# Reload previews
class EASYHDRI_OT_reload_previews(Operator):
    bl_idname = "easyhdr.reload_previews"
    bl_label = "Reload previews"
    bl_options = {'UNDO'}
    bl_description = "Reload previews"

    def execute(self, context):
        scn = context.scene
        if 'previews_dir' in scn:
            if scn.previews_dir:
                scn.previews_dir = scn.previews_dir
        
        return {'FINISHED'}     

# Remove unused images
class EASYHDRI_OT_remove_unused_images(Operator):
    bl_idname = "easyhdr.remove_unused_images"
    bl_label = "Remove unused images"
    bl_options = {'UNDO'}
    bl_description = "Remove 0 user images"
    
    def execute(self, context):
        cleanup_images()
        return {'FINISHED'}
     
# Next next image
class EASYHDRI_OT_next_image(Operator):
    bl_idname = "easyhdr.next"
    bl_label = "Next"
    bl_options = {'UNDO'}
    bl_description = "Next image"

    def execute(self, context):        
        scn = context.scene
        list = scn['previews_list']
        prev = scn.prev
        count = len(list)
        index = list.index(prev) + 1
        if index > count - 1:
            index = 0
        image = list[index]     
        if image != prev:
            scn.prev = image                      
        return {'FINISHED'}
    
# Preview previous image
class EASYHDRI_OT_previous_image(Operator):
    bl_idname = "easyhdr.previous"
    bl_label = "Previous"
    bl_options = {'UNDO'}
    bl_description = "Previous image"

    def execute(self, context):
        scn = context.scene
        list = scn['previews_list']
        prev = scn.prev
        count = len(list)
        index = list.index(prev) - 1
        if index < 0:
            index = count-1
        image = list[index]     
        if image != prev:
            scn.prev = image                      
        return {'FINISHED'}

# Settings Menu
class SettingsMenu(Menu):
    bl_idname = "EASYHDRI_MT_settings_menu"
    bl_label = "Settings"
    bl_description = "Settings"
    def draw(self, context):
        scn = context.scene        
        layout = self.layout
        layout.label(text = 'Cleanup:')    
        layout.operator("easyhdr.remove_unused_images", icon = 'RENDERLAYERS')
        layout.separator()
        layout.label(text = 'Loading images:')
        layout.prop(scn, 'dynamic_load', text = 'Load dynamically')
        layout.prop(scn, 'dynamic_cleanup', text = 'Cleanup dynamically')
        layout.prop(scn, 'set_projection', text = 'Set projection dynamically')
        layout.separator()
        layout.label(text = 'Recursive file search:')
        layout.prop(scn, 'recursive_search', text = 'Search in sub-folders')
        layout.separator()
        layout.label(text = 'Reset:')
        reset = layout.operator("easyhdr.reset_to_default", icon = 'LOOP_BACK')
        reset.reset_type = 'ALL' 

#SUN ///////////////////////////////////////////////////////////////////////////////////////////////////////
class AddSunPanel(bpy.types.Panel):
    bl_label = "SUN"
    bl_idname = "VIEW_3D_PT_add_sun"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KH-Tools"
    bl_parent_id = "VIEW3D_PT_light_manager"
    #bl_parent_id = "VIEW_3D_PT_kh_add_sky"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # استخدام الدالة المساعدة للبحث عن إعدادات الإضافة
        return get_addon_preferences(context, 'Light_Manager') == True

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon='LIGHT_SUN')
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        sun = scene.objects.get("Sun")
        row = layout.row()
        if not sun:
            row.operator("object.add_sun", text="Add Sun", icon="ADD")
        else:
            row.operator("object.remove_sun", text="Remove Sun", icon="TRASH")
            row = layout.row(align=True)
            row.prop(sun.data, "energy")
            row.scale_x =0.5
            #row.prop(sun.data, "color", text="")
            row.scale_x=0.3
            if not sun.data.use_nodes:
                row.prop(sun.data, "color", text='')
                row.scale_x=1.1
                row.operator("object.sun_temperature", text='', icon='EVENT_C')
            else:
                if sun.data.use_nodes:
                    Temperature = sun.data.node_tree.nodes.get('Blackbody')
                    if Temperature and Temperature.label == "KH-Temperature":
                        row.scale_x=1.1
                        row.prop(Temperature.inputs[0], "default_value", text="")
                        row.operator("object.delet_sun_temperature", text='', icon='EVENT_K') 
                    else:
                        row.prop(sun.data, "color", text='')
                        row.scale_x=1.1
                        row.operator("object.sun_temperature", text='', icon='EVENT_C')
            row = layout.row()
            row.prop(sun.data, "angle")
            row = layout.row()
            row.prop(sun, "rotation_euler", index=0, text="Elevation")
            row = layout.row()
            row.prop(sun, "rotation_euler", index=2, text="Rotation")
            
            
class AddSunOperator(bpy.types.Operator):
    """Add Sun to Scene"""
    bl_idname = "object.add_sun"
    bl_label = "Add Sun"

    def execute(self, context):
        if bpy.context.active_object:
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        scene = context.scene
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 100))
        lamp = context.active_object
        lamp.name = "Sun"
        obj = context.object
        collection_name = "KH-SUN"
        collection = bpy.data.collections.get(collection_name)
        if collection is None:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)
        obj.users_collection[0].objects.unlink(obj)
        collection.objects.link(obj)
        bpy.context.object.rotation_euler[2] = 1.0472
        bpy.context.object.rotation_euler[0] = 0.785398
        return {'FINISHED'}
       
class RemoveSunOperator(bpy.types.Operator):
    """Remove Sun from Scene"""
    bl_idname = "object.remove_sun"
    bl_label = "Remove Sun"

    def execute(self, context):
        if bpy.context.active_object:
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        scene = context.scene
        sun = scene.objects.get("Sun")
        if sun:
            bpy.ops.object.select_all(action='DESELECT')
            sun.select_set(True)
            bpy.ops.object.delete(use_global=False)
            bpy.ops.outliner.orphans_purge(do_recursive=True)
        collection_name = "KH-SUN"
        collection = bpy.data.collections.get(collection_name)
        if collection:
            bpy.data.collections.remove(collection, do_unlink=True)
            self.report({'INFO'}, f"{collection_name} collection deleted")
        else:
            self.report({'WARNING'}, f"No {collection_name} collection found")
        return {'FINISHED'}

class KH_sun_Temperature(bpy.types.Operator):
    bl_idname = "object.sun_temperature"
    bl_label = "SUN Temperature"

    def execute(self, context):
        scene = context.scene
        selected_object = scene.objects.get("Sun")
        if selected_object :
            if selected_object.type == 'LIGHT' and selected_object.data.type == 'SUN':
                if not selected_object.data.use_nodes:
                    selected_object.data.use_nodes = True
                Blackbody = selected_object.data.node_tree.nodes.get('Blackbody')
                if Blackbody:
                        selected_object.data.node_tree.nodes.remove(Blackbody)  
                Blackbody = selected_object.data.node_tree.nodes.new('ShaderNodeBlackbody')
                Blackbody.label = "KH-Temperature"
                shader_node = selected_object.data.node_tree.nodes.get('Emission')
                if shader_node:
                    strength_input = shader_node.inputs.get('Color')
                    if strength_input:
                        selected_object.data.node_tree.links.new(Blackbody.outputs[0], strength_input)
        return {'FINISHED'} 
            
class delet_KH_sun_Temperature(bpy.types.Operator):
    bl_idname = "object.delet_sun_temperature"
    bl_label = "Delet Sun Temperature"

    def execute(self, context):
        scene = context.scene
        selected_object = scene.objects.get("Sun")
        if selected_object :
            if selected_object.type == 'LIGHT' and selected_object.data.type == 'SUN':
                if not selected_object.data.use_nodes:
                    selected_object.data.use_nodes = True
                Blackbody = selected_object.data.node_tree.nodes.get('Blackbody')
                if Blackbody:
                        selected_object.data.node_tree.nodes.remove(Blackbody)  
        return {'FINISHED'} 

# Add Light/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class AddPointLightOperator(bpy.types.Operator):
    bl_idname = "object.add_point_light"
    bl_label = "Add Point Light"
    def execute(self, context):
        if bpy.context.active_object:
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.light_add(type='POINT')
        return {'FINISHED'}
    
class AddSpotLightOperator(bpy.types.Operator):
    bl_idname = "object.add_spot_light"
    bl_label = "Add Spot Light"
    def execute(self, context):
        if bpy.context.active_object:
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.light_add(type='SPOT')
        return {'FINISHED'}

class AddAreaLightOperator(bpy.types.Operator):
    bl_idname = "object.add_area_light"
    bl_label = "Add Area Light"
    def execute(self, context):
        if bpy.context.active_object:
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.light_add(type='AREA')
        return {'FINISHED'}

class LightManagerScaleSpotLights(bpy.types.Operator):
    bl_idname = "light_manager.scale_spot_lights"
    bl_label = "Scale Spot Lights"
    
    def execute(self, context):
        for obj in bpy.context.scene.objects:
            if obj.type == 'LIGHT' and obj.data.type == 'SPOT':
                if obj.scale.z < 0:
                    obj.scale = (0.1, 0.1, -0.1)
                else:
                    obj.scale = (0.1, 0.1, 0.1)

        return {'FINISHED'}

class LightManagerScaleSpot(bpy.types.Operator):
    bl_idname = "light_manager.scale_spot"
    bl_label = "Reset Scale"
    
    def execute(self, context):
        for obj in bpy.context.scene.objects:
            for obj in bpy.context.scene.objects:
                if obj.type == 'LIGHT' and obj.data.type == 'SPOT':
                    if obj.scale.z < 0:
                        obj.scale = (1, 1, -1)
                    else:
                        obj.scale = (1, 1, 1)

        return {'FINISHED'}
        
class LightManagerEnableGlossy(bpy.types.Operator):
    bl_idname = "light_manager.enable_glossy"
    bl_label = "Enable Glossy"
    bl_description = "Set all light objects to have glossy reflections enabled"

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'LIGHT':
                obj.visible_glossy = True
                obj.visible_transmission = True

        return {'FINISHED'}

class LightManagerDisableGlossy(bpy.types.Operator):
    bl_idname = "light_manager.disable_glossy"
    bl_label = "Disable Glossy"
    bl_description = "Set all light objects to have glossy reflections disabled"

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'LIGHT':
                obj.visible_glossy = False
                obj.visible_transmission = False
        return {'FINISHED'}
    
class OBJECT_OT_select_by_name(bpy.types.Operator):
    bl_idname = "object.select_by_name"
    bl_label = ""
    light_name: bpy.props.StringProperty()

    def execute(self, context):
        light_name = self.light_name
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[light_name].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[light_name]
        bpy.ops.object.select_linked(type='OBDATA')
        return {'FINISHED'}
    

# MATERIAL_PT_override //////////////////////////////////////////////////////////////////////////////////////////////////     
class MATERIAL_PT_override(bpy.types.Panel):
    bl_label = "Material Override" 
    bl_idname = "VIEW_3D_PT_material_override"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KH-Tools"
    bl_parent_id = "VIEW3D_PT_light_manager"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon='MATSPHERE')
        except KeyError:
            pass
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        material_name = "OV"
        material = bpy.data.materials.get(material_name)
        if material is not None:
            row.operator("object.delete_override", text="Delete Override", icon='TRASH')
            row = box.row()
            row.prop(material.node_tree.nodes["Principled BSDF"].inputs['Base Color'], "default_value", text="")
        else:
            row.operator("object.add_override", text="Material Override", icon='ADD')
        row = box.row()
        row.prop(context.scene.render, "film_transparent", text="Transparent Background" , icon='WORLD')
        
        
class Add_Override(bpy.types.Operator):
    bl_idname = "object.add_override"
    bl_label = "Material Override"
    def execute(self, context):
        material = bpy.data.materials.new(name="OV")
        material.use_nodes = True
        material.use_fake_user = True
        nodes = material.node_tree.nodes
        principled_bsdf = nodes.get("Principled BSDF")
        if principled_bsdf is not None:
            principled_bsdf.inputs["Base Color"].default_value = (0.25, 0.25, 0.25, 1.0)  # Set base color to red     
        bpy.context.scene.view_layers["ViewLayer"].material_override = bpy.data.materials["OV"]
        return {'FINISHED'}

class Delete_Override(bpy.types.Operator):
    bl_idname = "object.delete_override"
    bl_label = "Delete Override"
    def execute(self, context):
        for material in bpy.data.materials:
            if material.name == "OV":
                bpy.data.materials.remove(material)
        bpy.context.scene.view_layers["ViewLayer"].material_override = None
        return {'FINISHED'}
    
# Volumemetric //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////                
class VolumetricPanel(bpy.types.Panel):
    bl_idname = "VIEW_3D_PT_volumetric_panel"
    bl_label = "VOLUMETRIC"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "KH-Tools"
    bl_parent_id = "VIEW3D_PT_light_manager"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon='OUTLINER_DATA_VOLUME')
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        if 'KH-Volumetric' not in bpy.data.objects:
            row = layout.row()
            row.operator("object.create_volumemetric_cube", text="Create Volumetric" , icon='MAT_SPHERE_SKY')
        else:
            row = layout.row()
            row.operator("object.delete_volumetric_cube", text="Delete Volumetric" , icon='TRASH')
            volumetric_obj = bpy.data.objects.get('KH-Volumetric')
            row = layout.row()
            row = layout.row()
            row.prop(volumetric_obj, "scale", text="")
            row = layout.row()
            row.prop(volumetric_obj, "hide_viewport", text="Viewport")
            row.prop(volumetric_obj, "hide_render", text="Render")
            row = layout.row()
            row = layout.row()
            material = bpy.data.materials.get('KH-Volumetric')
            if material:
                volume_node = material.node_tree.nodes.get('Principled Volume')
                if volume_node:
                    layout.prop(volume_node.inputs[0], "default_value", text="Color")
                    layout.prop(volume_node.inputs[2], "default_value", text="Density")
                    layout.prop(volume_node.inputs[4], "default_value", text="Anisotropy")
                    layout.prop(volume_node.inputs[5], "default_value", text="Absorption Color")
                    layout.prop(volume_node.inputs[6], "default_value", text="Emission Strength")
                    layout.prop(volume_node.inputs[7], "default_value", text="Emission Color")
                    layout.prop(volume_node.inputs[8], "default_value", text="Blackbody Intensity")
                    layout.prop(volume_node.inputs[9], "default_value", text="Blackbody Tint")
                    layout.prop(volume_node.inputs[10], "default_value", text="Temperature")
                else:
                    layout.label(text="Principled Volume node not found in material")
            else:
                layout.label(text="Volumetric material not found")
                
class CreateVolumemetricCube(bpy.types.Operator):
    bl_idname = "object.create_volumemetric_cube"
    bl_label = "Create Volumetric Cube"

    def execute(self, context):
        if bpy.context.active_object:
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        if 'KH-Volumetric' not in bpy.data.objects:
            location = bpy.context.scene.cursor.location
            bpy.ops.mesh.primitive_cube_add(size=100, enter_editmode=False, align='WORLD', location=location)
            volumetric_obj = bpy.context.active_object
            volumetric_obj.name = 'KH-Volumetric'
            volumetric_obj.display_type = 'BOUNDS'
            
            if 'KH-Volumetric' not in bpy.data.materials:
                material = bpy.data.materials.new(name="KH-Volumetric")
                material.use_nodes = True
                material.use_fake_user = True
                material.node_tree.nodes.remove(material.node_tree.nodes.get('Principled BSDF'))
                volume_node = material.node_tree.nodes.new('ShaderNodeVolumePrincipled')
                output_node = material.node_tree.nodes.get('Material Output')
                material.node_tree.links.new(volume_node.outputs['Volume'], output_node.inputs['Volume'])            
                volume_node.inputs[2].default_value = 0.02
                volume_node.inputs[4].default_value = 0.3
            else:
                material = bpy.data.materials['KH-Volumetric']
            volumetric_obj.active_material = material
            obj = context.object
            collection_name = "KH-Volumetric"
            collection = bpy.data.collections.get(collection_name)
            if collection is None:
                collection = bpy.data.collections.new(collection_name)
                bpy.context.scene.collection.children.link(collection)
            obj.users_collection[0].objects.unlink(obj)
            collection.objects.link(obj)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Volumetric cube already exists")
            return {'CANCELLED'}


class DeleteVolumemetricCube(bpy.types.Operator):
    bl_idname = "object.delete_volumetric_cube"
    bl_label = "Delete Volumetric Cube"

    def execute(self, context):
        if bpy.context.active_object:
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        volumetric_obj = bpy.data.objects.get('KH-Volumetric')
        if volumetric_obj:
            bpy.data.objects.remove(volumetric_obj, do_unlink=True)
            bpy.ops.outliner.orphans_purge(do_recursive=True)
        collection_name = "KH-Volumetric"
        collection = bpy.data.collections.get(collection_name)
        if collection:
            bpy.data.collections.remove(collection, do_unlink=True)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Volumetric cube not found")
            return {'CANCELLED'}    

# add sky //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////  
preview_collection3 = bpy.utils.previews.new()
preview_collection3.load("cloudy.png", os.path.join(my_icons_dir, "cloudy.png"), 'IMAGE')              
class AddSkyPanel(bpy.types.Panel):
    bl_label = "World Light"
    bl_idname = "VIEW_3D_PT_kh_add_sky"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KH-Tools"
    #bl_parent_id = "VIEW3D_PT_light_manager"
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        # استخدام الدالة المساعدة للبحث عن إعدادات الإضافة
        return get_addon_preferences(context, 'Light_Manager') == True

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon_value=preview_collection3['cloudy.png'].icon_id)
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout
        world = bpy.context.scene.world
        row = layout.row()
        texsky_node = None
        Clouds_node = None
        SKY_node = None
        Mapping_node = None
        HDRI_node = None
        MIX_node = None
        Shadow_node = None
        Night_node = None
        NIGHT_MIX_node = None
        sky_connected = False
        Night_connected = False
        
        if world and world.node_tree:
            for node in world.node_tree.nodes:
                if node.type == 'TEX_SKY'and node.label == "KH-SUN":
                    texsky_node = node
                    break
            for node in world.node_tree.nodes:
                if node.type == 'GROUP' and node.label == "KH-Clouds":
                    Clouds_node = node
                    break
                        
            for node in world.node_tree.nodes:
                if node.type == 'GROUP' and node.label == "KH-SKY":
                    SKY_node = node
                    break
                
            for node in world.node_tree.nodes:
                if node.label == "KH-Clouds Output":
                    for other_node in world.node_tree.nodes:
                        if other_node.label == "KH-SKY":
                            for link in world.node_tree.links:
                                if link.to_node == node and link.from_node == other_node:
                                    sky_connected = True
                                    break
                                    
            for node in world.node_tree.nodes:
                if node.type == 'GROUP' and node.label == "KH-NIGHT":
                    Night_node = node
                    break
                
            for node in world.node_tree.nodes:
                if node.label == "KH-Clouds Output":
                    for other_node1 in world.node_tree.nodes:
                        if other_node1.label == "KH-NIGHT":
                            for link in world.node_tree.links:
                                if link.to_node == node and link.from_node == other_node1:
                                    Night_connected = True
                                    break
                
            for node in world.node_tree.nodes:
                if node.type == 'GROUP' and node.label == "KH-Clouds":
                    Clouds_node = node
                    break
            for node in world.node_tree.nodes:
                if node.type == 'GROUP' and node.label == "KH-NIGHT MIX":
                    NIGHT_MIX_node = node
                    break
            for node in world.node_tree.nodes:
                if node.type == 'GROUP' and node.label == "KH-Custom Shadow":
                    Shadow_node = node
                    break
                
            for node in world.node_tree.nodes:
                if node.type == 'OUTPUT_WORLD':
                    for other_node in world.node_tree.nodes:
                        if other_node.label == "KH-Custom Shadow":
                            Shadow_connected = False
                            for link in world.node_tree.links:
                                if link.to_node == node and link.from_node == other_node:
                                    Shadow_connected = True
                                    break
                
            for node in world.node_tree.nodes:
                if node.type == 'MAPPING' and node.label == "KH-MAPPING":
                    Mapping_node = node
                    break
            
            for node in world.node_tree.nodes:
                if node.type == 'TEX_ENVIRONMENT' and node.label == "KH-HDRI":
                    HDRI_node = node
                    break
            for node in world.node_tree.nodes:
                if node.label == "KH-MIX":
                    MIX_node = node
                    break
  
        if not Clouds_node and not Night_node:
            row.operator("object.add_sky", text="Day", icon="ADD")
            row.operator("object.kh_add_night", text="Night", icon="ADD")
            
        elif Clouds_node:
            world = bpy.context.scene.world
            for node in world.node_tree.nodes:
                if node.label == "KH-Clouds Output":
                    for other_node in world.node_tree.nodes:
                        if other_node.label == "KH-SKY":
                            is_connected = False
                            for link in world.node_tree.links:
                                if link.to_node == node and link.from_node == other_node:
                                    is_connected = True
                                    break
                            if not is_connected:
                                row.operator("object.update_sky", text="Update Day", icon="FILE_REFRESH")
                                row = layout.row()
                                break
                            else:                            
                                row = layout.row()                          
                                row.operator("object.delete_sky", text="Delete", icon="TRASH")
                                box = layout.box()
                                row = box.row()
                                row.label(text="Day HDRI:", icon='IMAGE_DATA')
                                row = layout.row()
                                row.prop(HDRI_node.image, "name", text="")
                                row = layout.row() 
                                row.operator("object.kh_image_open_hdri", text="HDRI", icon="FILEBROWSER")
                                row.operator("object.kh_image_open_exr", text="HDRI 2", icon="FILEBROWSER")
                                row = layout.row()
                                row.prop(MIX_node.inputs[0], "default_value", text="HDRI 2")
                                row.prop(MIX_node, "blend_type", text="")
                                
                                box = layout.box()
                                row = box.row()
                                row.label(text="World:", icon='OPTIONS')
                                row.prop(texsky_node, "sun_disc",text="")
                                row = layout.row()
                                row.prop(SKY_node.inputs[0], "default_value", text="Sky" )
                                row.prop(Clouds_node.inputs[1], "default_value", text="HDRI" )
                                if texsky_node.sun_disc == True:
                                    row = layout.row()
                                    row.prop(texsky_node, "sun_intensity",text="Sun")
                                    row.prop(texsky_node, "sun_size")
                                                                
                                box = layout.box()
                                row = layout.row()
                                row.prop(texsky_node, "sun_elevation")
                                row = layout.row()
                                row.prop(texsky_node, "sun_rotation")
                                scene = bpy.context.scene
                                row.prop(scene, "link_world_mapping", text="" , icon = 'LINK_BLEND')
                                if not scene.link_world_mapping:
                                    row = layout.row()
                                    row.prop(Mapping_node.inputs["Rotation"], "default_value", index=2, text="HDRI Rotation")
  
                                #row.operator("object.delete_world_driver", text = '', icon = 'UNLINKED')  
                                #row.operator("object.world_driver_add", text = '', icon = 'LINK_BLEND')
                                
                                                            
                                box = layout.box()
                                row = box.row()
                                row.label(text="Shadow:", icon='VOLUME_DATA')
                                row = layout.row()
                                row.prop(SKY_node.inputs[11], "default_value", text="Shadow")
                                row = layout.row()
                                row.prop(SKY_node.inputs[10], "default_value", text="Color Strength")
                                row.prop(SKY_node.inputs[9], "default_value", text="")
                                   
                                box = layout.box()
                                row = box.row()
                                row.label(text="Atmosphere:", icon='MAT_SPHERE_SKY')
                                
                                # Blender 5.0+ uses different Sky Texture properties
                                if bpy.app.version >= (5, 0, 0):
                                    # New properties in Blender 5.0
                                    if hasattr(texsky_node, 'aerosol_density'):
                                        row = layout.row()
                                        row.prop(texsky_node, "air_density")
                                        row.prop(texsky_node, "ozone_density")
                                        row = layout.row()
                                        row.prop(texsky_node, "aerosol_density")
                                        row.prop(texsky_node, "altitude")
                                else:
                                    # Old properties for Blender 4.x and earlier
                                    row = layout.row()
                                    row.prop(texsky_node, "air_density")
                                    row.prop(texsky_node, "ozone_density")
                                    row = layout.row()
                                    if hasattr(texsky_node, 'dust_density'):
                                        row.prop(texsky_node, "dust_density")
                                    row.prop(texsky_node, "altitude")
                                   
                                box = layout.box()
                                row = box.row()
                                row.label(text="Background:", icon='OUTLINER_OB_VOLUME')
                                row = layout.row() 
                                row.prop(SKY_node.inputs[1], "default_value", text="HDRI Effect")
                                row = layout.row()
                                row.prop(SKY_node.inputs[2], "default_value", text="Glossy Effect")
                                row = layout.row()
                                row.prop(Clouds_node.inputs[4], "default_value", text="Saturation")
                                row.prop(Clouds_node.inputs[2], "default_value", text="Gamma" )
                                row = layout.row()
                                row.prop(Clouds_node.inputs[3], "default_value", text="Hue" )
                                row.prop(Clouds_node.inputs[5], "default_value", text="Fac")
                                row = layout.row()
                                row.prop(Mapping_node.inputs["Location"], "default_value", index=2, text="Hight")
                                row.prop(Mapping_node.inputs["Scale"], "default_value", index=2, text="z")
                                row = layout.row()
                                # row = layout.row()
                                # row.prop(Clouds_node.inputs[7], "default_value", text="" )
                                # row = layout.row()
                                # row.prop(Clouds_node.inputs[8], "default_value", text="Color Strength" )
                                # row = layout.row()
                                # row.prop(Clouds_node.inputs[10], "default_value", text="" )
                                break
        
        elif Night_node:
            
            if not Night_connected:
                row.operator("object.update_sky", text="Update Night", icon="FILE_REFRESH")
                row = layout.row()
            else: 
                row = layout.row()                      
                row.operator("object.delete_sky", text="Delete", icon="TRASH")
                box = layout.box()
                row = box.row()
                row.label(text="Night HDRI:", icon='IMAGE_DATA')
                row = layout.row()
                row.prop(HDRI_node.image, "name", text="")
                row = layout.row() 
                row.operator("object.kh_image_open_hdri", text="HDRI", icon="FILEBROWSER")
                row.operator("object.kh_image_open_exr", text="HDRI 2", icon="FILEBROWSER")
                row = layout.row()
                row.prop(MIX_node.inputs[0], "default_value", text="HDRI 2")
                row.prop(MIX_node, "blend_type", text="")
                
                box = layout.box()
                row = box.row()
                row.label(text="World:", icon='OPTIONS')
                #row.prop(texsky_node, "sun_disc",text="")
                row = layout.row()
                row.prop(Night_node.inputs[0], "default_value", text="Sky" )
                # if texsky_node.sun_disc == True:
                #     row = layout.row()
                #     row.prop(texsky_node, "sun_intensity",text="Sun")
                #row = layout.row()
                row.prop(NIGHT_MIX_node.inputs[1], "default_value", text="HDRI" )
                row = layout.row()
                row.prop(texsky_node, "sun_elevation")
                row = layout.row()
                row.prop(texsky_node, "sun_rotation")
                scene = bpy.context.scene
                row.prop(scene, "link_world_mapping", text="" , icon = 'LINK_BLEND')
                if not scene.link_world_mapping:
                    row = layout.row()
                    row.prop(Mapping_node.inputs["Rotation"], "default_value", index=2, text="HDRI Rotation")

                #row.operator("object.delete_world_driver", text = '', icon = 'UNLINKED')  
                #row.operator("object.world_driver_add", text = '', icon = 'LINK_BLEND')
                
                # row = box.row()
                # if texsky_node.sun_disc == True:
                #     row = layout.row()
                #     row.prop(texsky_node, "sun_size")
                
                box = layout.box()
                row = box.row()
                row.label(text="Shadow:", icon='VOLUME_DATA')
                row = layout.row()
                row.prop(Night_node.inputs[11], "default_value", text="Shadow")
                row = layout.row()
                row.prop(Night_node.inputs[10], "default_value", text="Color Strength")
                row.prop(Night_node.inputs[9], "default_value", text="")
                    
                box = layout.box()
                row = box.row()
                row.label(text="Atmosphere:", icon='MAT_SPHERE_SKY')
                
                # Blender 5.0+ uses different Sky Texture properties
                if bpy.app.version >= (5, 0, 0):
                    # New properties in Blender 5.0
                    if hasattr(texsky_node, 'aerosol_density'):
                        row = layout.row()
                        row.prop(texsky_node, "air_density")
                        row.prop(texsky_node, "ozone_density")
                        row = layout.row()
                        row.prop(texsky_node, "altitude")
                        row.prop(texsky_node, "aerosol_density")
                else:
                    # Old properties for Blender 4.x and earlier
                    row = layout.row()
                    row.prop(texsky_node, "air_density")
                    row.prop(texsky_node, "ozone_density")
                    row = layout.row()
                    row.prop(texsky_node, "altitude")
                    if hasattr(texsky_node, 'dust_density'):
                        row.prop(texsky_node, "dust_density")
                
                
                box = layout.box()
                row = box.row()
                row.label(text="Background:", icon='OUTLINER_OB_VOLUME')                
                row = layout.row() 
                row.prop(Night_node.inputs[1], "default_value", text="HDRI Effect")
                row = layout.row()
                row.prop(Night_node.inputs[2], "default_value", text="Glossy Effect")
                row = layout.row()
                row.prop(NIGHT_MIX_node.inputs[4], "default_value", text="Saturation")
                row.prop(NIGHT_MIX_node.inputs[2], "default_value", text="Gamma" )
                row = layout.row()
                row.prop(NIGHT_MIX_node.inputs[3], "default_value", text="Hue" )
                row.prop(NIGHT_MIX_node.inputs[5], "default_value", text="Fac")
                row = layout.row()
                row.prop(Mapping_node.inputs["Location"], "default_value", index=2, text="Hight")
                row.prop(Mapping_node.inputs["Scale"], "default_value", index=2, text="z")
                row = layout.row()
                # row = layout.row()
                # row.prop(Clouds_node.inputs[7], "default_value", text="" )
                # row = layout.row()
                # row.prop(Clouds_node.inputs[8], "default_value", text="Color Strength" )
                # row = layout.row()
                # row.prop(Clouds_node.inputs[10], "default_value", text="" )
                                          
        if not Shadow_node and not Clouds_node and not Night_node:
            row = layout.row()
            row.operator("object.kh_add_shadow", text="Add Shadow", icon="ADD") 
        else:      
            if not Shadow_node and not sky_connected and not Night_connected:
                row = layout.row()
                row.operator("object.kh_add_shadow", text="Add Shadow", icon="ADD")
                        
        if  Shadow_node :                    
            if Shadow_connected:
                box = layout.box()
                row = box.row()
                row.label(text="Shadow:", icon='VOLUME_DATA')
                row = layout.row()
                row.prop(Shadow_node.inputs[3], "default_value", text="Shadow")
                row = layout.row()
                row.prop(Shadow_node.inputs[2], "default_value", text="Color Strength")
                row = layout.row()
                row.prop(Shadow_node.inputs[1], "default_value", text="")
            else:
                if not Shadow_connected and not sky_connected and not Night_connected:
                    row = layout.row()
                    row.operator("object.update_shadow", text="Update Shadow",icon="FILE_REFRESH")
        
                # if not Shadow_connected and not SKY_node and not Night_node:
                #     row = layout.row()
                #     row.operator("object.update_shadow", text="Update Shadow",icon="FILE_REFRESH")
                          
#sky IMAGE hdri                                         
class KH_IMAGE_OT_open_hdri(bpy.types.Operator):
    bl_idname = "object.kh_image_open_hdri"
    bl_label = "Open Image"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        image_path = self.filepath
        world = context.scene.world
        for node in world.node_tree.nodes:
            if node.type == 'TEX_ENVIRONMENT' and node.label == "KH-HDRI":
                node.image = bpy.data.images.load(image_path)
                break
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#sky IMAGE hdri                                         
class KH_IMAGE_OT_open_exr(bpy.types.Operator):
    bl_idname = "object.kh_image_open_exr"
    bl_label = "Open Image"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        image_path = self.filepath
        world = context.scene.world
        for node in world.node_tree.nodes:
            if node.type == 'TEX_ENVIRONMENT' and node.label == "KH-EXR":
                node.image = bpy.data.images.load(image_path)
                break
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}




def driver_world_add_h(scene):
    if scene.link_world_mapping:
        if bpy.context.scene.world is not None:
            world = bpy.context.scene.world  
            kh_sun = None
            mapping_node = None
            for node in world.node_tree.nodes:
                if node.label == "KH-SUN":
                    kh_sun = node
                    break
            for node in world.node_tree.nodes:   
                if node.label == "KH-MAPPING":
                    mapping_node = node
                    break
            if kh_sun and mapping_node :
                mapping_node.inputs[2].default_value[2] = kh_sun.sun_rotation -1.5708
                
#bpy.app.handlers.depsgraph_update_post.append(driver_world_add_heder) 
def check_sun_rotation(scene):
    kh_sun = None
    # Check if world and node_tree exist
    if not scene.world or not scene.world.node_tree:
        return None
    
    for node in bpy.context.scene.world.node_tree.nodes:
        if node.label == "KH-SUN":
            kh_sun = node
            break
    if kh_sun:
        return kh_sun.sun_rotation
    return None
@persistent
def check_sun_rotation_callback(scene, depsgraph):
    current_rotation = check_sun_rotation(scene)
    if current_rotation is not None and current_rotation != getattr(check_sun_rotation_callback, "prev_rotation", None):
        check_sun_rotation_callback.prev_rotation = current_rotation
        driver_world_add_h(scene)

# Handler to update IES preview image when active object changes
@persistent
def update_ies_preview_on_selection(scene, depsgraph):
    """Update IES preview image when switching between lights"""
    context = bpy.context
    
    # Check if active object changed
    active_obj = context.active_object
    if not active_obj:
        return
    
    # Check if it's a light with IES
    if active_obj.type != 'LIGHT':
        return
    
    if not active_obj.data.use_nodes:
        return
    
    ies_node = active_obj.data.node_tree.nodes.get('IES Texture')
    if not ies_node or ies_node.label != "KH-IES":
        return
    
    current_file = ies_node.filepath
    if not current_file or not os.path.exists(current_file):
        return
    
    # Check if this is a different light than before
    prev_light = getattr(update_ies_preview_on_selection, "prev_light", None)
    if prev_light == active_obj.name:
        return
    
    # Update the previous light tracker
    update_ies_preview_on_selection.prev_light = active_obj.name
    
    # Update enum property to sync with template_icon_view
    try:
        context.scene.ies_files_enum = current_file
    except:
        pass
    
    # Update preview image
    ies_dir = os.path.dirname(current_file)
    base_name = os.path.splitext(os.path.basename(current_file))[0]
    
    # Look for corresponding image file
    image_path = None
    for ext in ['.png', '.jpg', '.jpeg']:
        potential_image = os.path.join(ies_dir, base_name + ext)
        if os.path.exists(potential_image):
            image_path = potential_image
            break
    
    # Update the preview image
    if image_path:
        try:
            # Remove old image if exists
            if hasattr(context.scene, 'my_image') and context.scene.my_image:
                old_image = context.scene.my_image
                if old_image and old_image.name in bpy.data.images:
                    bpy.data.images.remove(old_image)
            
            # Load new image
            new_image = bpy.data.images.load(image_path)
            context.scene.my_image = new_image
        except Exception as e:
            print(f"Error loading preview image: {e}")
    else:
        # No image found, clear preview
        if hasattr(context.scene, 'my_image') and context.scene.my_image:
            old_image = context.scene.my_image
            if old_image and old_image.name in bpy.data.images:
                bpy.data.images.remove(old_image)
            context.scene.my_image = None
        
# @persistent
# def driver_world_add_handler(dummy):
#     scene = bpy.context.scene
#     driver_world_add_h(scene)
              
                    
# def driver_world_add():  
#     if bpy.context.scene.world is not None:
#         world = bpy.context.scene.world  
#         kh_sun = None
#         mapping_node_world = None
        
#         for node in world.node_tree.nodes:
#             if node.label == "KH-SUN":
#                 mapping_node_world = node
#                 break
#         for node in world.node_tree.nodes:   
#             if node.label == "KH-MAPPING":
#                 kh_sun = node
#                 break
#         if kh_sun and mapping_node_world :
#             driver_material = kh_sun.inputs[2].driver_add("default_value", 2).driver
#             driver_material.type = 'SCRIPTED'
#             driver_material_variable = driver_material.variables.new()
#             driver_material_variable.name = "sun_rotation"
#             driver_material.expression = "sun_rotation -1.5708"
#             driver_material_variable.targets[0].id_type = "WORLD"
#             driver_material_variable.targets[0].id = world      
#             driver_material_variable.targets[0].data_path = f"node_tree.nodes[\"{mapping_node_world.name}\"].sun_rotation"
            
            

# def delete_world_driver():
#     if bpy.context.scene.world is not None:
#         world = bpy.context.scene.world  
#         kh_sun = None
#         for node in world.node_tree.nodes:   
#             if node.label == "KH-MAPPING":
#                 kh_sun = node
#                 break
#         if kh_sun :
#             kh_sun.inputs[2].driver_remove("default_value")
            

class kh_Add_Shadow(bpy.types.Operator):
    bl_idname = "object.kh_add_shadow"
    bl_label = "Add Shadow"

    def execute(self, context):
        if bpy.context.scene.world is not None:
            world_name = "KH-Custom Shadow"
            world = bpy.data.worlds.get(world_name)
            if world is None:
                script_dir = os.path.dirname(os.path.realpath(__file__))
                folder_path = os.path.join(script_dir, "asset")
                file_name = "KH-Custom Shadow.blend"
                world_file_path = os.path.join(folder_path, file_name)
                with bpy.data.libraries.load(world_file_path, link=False) as (data_from, data_to):
                    data_to.worlds = [name for name in data_from.worlds if name.startswith("KH-Custom Shadow")]

            active_world = bpy.context.scene.world
            if 'KH-Custom Shadow' not in bpy.data.node_groups:
                print("Node group 'KH-Custom Shadow' not found.")
            else:
                node_exists = False
                for node in active_world.node_tree.nodes:
                    if node.label == "KH-Custom Shadow":
                        node_exists = True
                        break
                world_output_node = None
                for node in active_world.node_tree.nodes:
                    if node.type == 'OUTPUT_WORLD':
                        world_output_node = node
                        break
                if not node_exists and world_output_node:
                    custom_shadow_node = active_world.node_tree.nodes.new('ShaderNodeGroup')
                    custom_shadow_node.location = (-300, 300) 
                    custom_shadow_node.label = 'KH-Custom Shadow'
                    custom_shadow_node.node_tree = bpy.data.node_groups.get('KH-Custom Shadow')  # 
                
                    previous_link = None
                    for link in active_world.node_tree.links:
                        if link.to_socket == world_output_node.inputs['Surface']:
                            previous_link = link
                            break
                        
                    if previous_link:
                        active_world.node_tree.links.new(previous_link.from_socket, custom_shadow_node.inputs[0])
                    
                    world_output_link = active_world.node_tree.links.new(custom_shadow_node.outputs['Shader'], world_output_node.inputs['Surface'])
                                
            return {'FINISHED'}   

class UpdateShadow(bpy.types.Operator):
    bl_idname = "object.update_shadow"
    bl_label = "Update Shadow"

    def execute(self, context):
        active_world = bpy.context.scene.world
        for node in active_world.node_tree.nodes:
            if node.type == 'OUTPUT_WORLD':
                world_output_node = node
                break
            
        for node in active_world.node_tree.nodes:
            if node.label == "KH-Custom Shadow":
                Shadow_node = node
                break
        if world_output_node and Shadow_node:
            previous_link = None
            for link in active_world.node_tree.links:
                if link.to_socket == world_output_node.inputs['Surface']:
                    previous_link = link
                    break
                
            if previous_link:
                active_world.node_tree.links.new(previous_link.from_socket, Shadow_node.inputs[0])
            
            world_output_link = active_world.node_tree.links.new(Shadow_node.outputs['Shader'], world_output_node.inputs['Surface'])
        return {'FINISHED'} 
                
            
class addsky(bpy.types.Operator):
    bl_idname = "object.add_sky"
    bl_label = "Add Sky"

    def execute(self, context):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        folder_path = os.path.join(script_dir, "asset")
        hdri_add = "Day-2K.exr"
        exr_add = "Day1-2K.exr"
        hdri_add_image_path = os.path.join(folder_path, hdri_add)
        exr_add_image_path = os.path.join(folder_path, exr_add)
        
        if bpy.context.scene.world is None:
            world_name = "KH - Clouds"
            world = bpy.data.worlds.get(world_name)
            if world is not None:
                bpy.context.scene.world = world
            else:
                script_dir = os.path.dirname(os.path.realpath(__file__))
                folder_path = os.path.join(script_dir, "asset")
                file_name = "KH- Clouds.blend"
                world_file_path = os.path.join(folder_path, file_name)
                with bpy.data.libraries.load(world_file_path, link=False) as (data_from, data_to):
                    data_to.worlds = [name for name in data_from.worlds if name.startswith("KH - Clouds")]
                world_name = "KH - Clouds"
                world = bpy.data.worlds.get(world_name)
                if world is not None:
                    bpy.context.scene.world = world
                
                for node in world.node_tree.nodes:                                      
                    if node.label == "KH-HDRI":
                        image_path = hdri_add_image_path
                        if os.path.exists(image_path):
                            bpy.ops.image.open(filepath=image_path)
                            node.image = bpy.data.images.get(os.path.basename(image_path))
                        
                    if node.label == "KH-EXR":
                        image_path = exr_add_image_path
                        if os.path.exists(image_path):
                            bpy.ops.image.open(filepath=image_path)
                            node.image = bpy.data.images.get(os.path.basename(image_path))
                    
            return {'FINISHED'}   
        else:
            world_name = "KH - Clouds"
            world = bpy.data.worlds.get(world_name)
            if world is None:
                script_dir = os.path.dirname(os.path.realpath(__file__))
                folder_path = os.path.join(script_dir, "asset")
                file_name = "KH- Clouds.blend"
                world_file_path = os.path.join(folder_path, file_name)
                with bpy.data.libraries.load(world_file_path, link=False) as (data_from, data_to):
                    data_to.worlds = [name for name in data_from.worlds if name.startswith("KH - Clouds")]
                world_name = "KH - Clouds"
                world = bpy.data.worlds.get(world_name)
            
            source_world_name = "KH - Clouds"
            target_world = bpy.context.scene.world
            source_world = bpy.data.worlds.get(source_world_name)

            if source_world:
                bpy.context.scene.world = source_world
                node_map = {}
                for node in source_world.node_tree.nodes:
                    new_node = target_world.node_tree.nodes.new(type=node.bl_idname)
                    new_node.name = node.name
                    new_node.location = node.location
                    for attr in node.bl_rna.properties.keys():
                        try:
                            setattr(new_node, attr, getattr(node, attr))
                        except AttributeError:
                            pass

                    node_map[node.name] = new_node
                for node in source_world.node_tree.nodes:
                    for input in node.inputs:
                        if input.is_linked:
                            for link in input.links:
                                output_node = link.from_node
                                output_socket = link.from_socket
                                if output_node.name in node_map.keys():
                                    target_node = node_map[output_node.name]
                                    target_socket = target_node.outputs[output_socket.name]
                                    bpy.context.scene.world.node_tree.links.new(target_socket, input)

                bpy.context.scene.world = target_world
                world = bpy.context.scene.world
                if world is None:
                    print("There is no active world in the scene.")
                else:
                    # Blender 5.0+: Set sky_type for Sky Texture nodes
                    if bpy.app.version >= (5, 0, 0):
                        for node in world.node_tree.nodes:
                            if node.type == 'TEX_SKY' and hasattr(node, 'sky_type'):
                                node.sky_type = 'MULTIPLE_SCATTERING'
                    
                    for node in world.node_tree.nodes:                                      
                        if node.label == "KH-SKY":
                            for other_node in world.node_tree.nodes:
                                if other_node.label == "KH-LIGHT PATH":
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[3])
                                    world.node_tree.links.new(other_node.outputs[4], node.inputs[4])
                                    
                                if other_node.label == "KH-SUN":
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[5])
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[6])
                                    
                                if other_node.label == "KH-Clouds":
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[7])
                                    world.node_tree.links.new(other_node.outputs[1], node.inputs[8])
                                
                        elif node.label == "KH-MAPPING":
                            for other_node in world.node_tree.nodes:
                                if other_node.label == "KH-EXR":
                                    world.node_tree.links.new(other_node.inputs[0], node.outputs[0])
                                    
                                if other_node.label == "KH-HDRI":
                                    world.node_tree.links.new(other_node.inputs[0], node.outputs[0])
                                    
                                if other_node.label == "KH-COOR":
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[0])
 
                        elif node.label == "KH-MIX":
                            for other_node in world.node_tree.nodes:
                                if other_node.label == "KH-Clouds":
                                    world.node_tree.links.new(other_node.inputs[0], node.outputs[0])
                                    world.node_tree.links.new(other_node.inputs[0], node.outputs[2])
                                        
                                if other_node.label == "KH-HDRI":
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[6])
                                    image_path = hdri_add_image_path
                                    if os.path.exists(image_path):
                                        bpy.ops.image.open(filepath=image_path)
                                        other_node.image = bpy.data.images.get(os.path.basename(image_path))
                                    
                                if other_node.label == "KH-EXR":
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[7])
                                    image_path = exr_add_image_path
                                    if os.path.exists(image_path):
                                        bpy.ops.image.open(filepath=image_path)
                                        other_node.image = bpy.data.images.get(os.path.basename(image_path))
                                                        
                                node.inputs[0].default_value = 0
                                node.blend_type = 'MIX'



                        elif node.label == "KH-Clouds Output":
                            for other_node in world.node_tree.nodes:
                                if other_node.label == "KH-SKY":
                                    #if len(node.inputs[0].links) == 0:
                                        world.node_tree.links.new(node.inputs[0], other_node.outputs[0])
                                        
            scene = bpy.context.scene
            world = scene.world
            nodes = world.node_tree.nodes
            nodes_to_delete = [node for node in nodes if node.type == 'OUTPUT_WORLD' and node.label != "KH-Clouds Output"]
            for node in nodes_to_delete:
                nodes.remove(node)
                
            nodes_to_delete = [node for node in nodes if node.type == 'MAPPING' and node.label != "KH-MAPPING"]
            for node in nodes_to_delete:
                nodes.remove(node)
                
            nodes_to_delete = [node for node in nodes if node.type == 'TEX_ENVIRONMENT' and node.label != "KH-HDRI" and node.label != "KH-EXR"]
            for node in nodes_to_delete:
                nodes.remove(node)
                
            #delete_world_driver()
            #driver_world_add()
        return {'FINISHED'} 
    
class KH_NIGHT(bpy.types.Operator):
    bl_idname = "object.kh_add_night"
    bl_label = "Add Night"

    def execute(self, context):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        folder_path = os.path.join(script_dir, "asset")
        hdri_add = "Night-2K.exr"
        exr_add = "Night1-2K.hdr"
        hdri_add_image_path = os.path.join(folder_path, hdri_add)
        exr_add_image_path = os.path.join(folder_path, exr_add)
        
        if bpy.context.scene.world is None:
            world_name = "KH-NIGHT"
            world = bpy.data.worlds.get(world_name)
            if world is not None:
                bpy.context.scene.world = world
            else:
                script_dir = os.path.dirname(os.path.realpath(__file__))
                folder_path = os.path.join(script_dir, "asset")
                file_name = "KH-NIGHT.blend"
                world_file_path = os.path.join(folder_path, file_name)
                with bpy.data.libraries.load(world_file_path, link=False) as (data_from, data_to):
                    data_to.worlds = [name for name in data_from.worlds if name.startswith("KH-NIGHT")]
                world_name = "KH-NIGHT"
                world = bpy.data.worlds.get(world_name)
                if world is not None:
                    bpy.context.scene.world = world
                
                for node in world.node_tree.nodes:                                      
                    if node.label == "KH-HDRI":
                        image_path = hdri_add_image_path
                        if os.path.exists(image_path):
                            bpy.ops.image.open(filepath=image_path)
                            node.image = bpy.data.images.get(os.path.basename(image_path))
                        
                    if node.label == "KH-EXR":
                        image_path = exr_add_image_path
                        if os.path.exists(image_path):
                            bpy.ops.image.open(filepath=image_path)
                            node.image = bpy.data.images.get(os.path.basename(image_path))
                    
            return {'FINISHED'}   
        else:
            world_name = "KH-NIGHT"
            world = bpy.data.worlds.get(world_name)
            if world is None:
                script_dir = os.path.dirname(os.path.realpath(__file__))
                folder_path = os.path.join(script_dir, "asset")
                file_name = "KH-NIGHT.blend"
                world_file_path = os.path.join(folder_path, file_name)
                with bpy.data.libraries.load(world_file_path, link=False) as (data_from, data_to):
                    data_to.worlds = [name for name in data_from.worlds if name.startswith("KH-NIGHT")]
                world_name = "KH-NIGHT"
                world = bpy.data.worlds.get(world_name)
            
            source_world_name = "KH-NIGHT"
            target_world = bpy.context.scene.world
            source_world = bpy.data.worlds.get(source_world_name)

            if source_world:
                bpy.context.scene.world = source_world
                node_map = {}
                for node in source_world.node_tree.nodes:
                    new_node = target_world.node_tree.nodes.new(type=node.bl_idname)
                    new_node.name = node.name
                    new_node.location = node.location
                    for attr in node.bl_rna.properties.keys():
                        try:
                            setattr(new_node, attr, getattr(node, attr))
                        except AttributeError:
                            pass

                    node_map[node.name] = new_node
                for node in source_world.node_tree.nodes:
                    for input in node.inputs:
                        if input.is_linked:
                            for link in input.links:
                                output_node = link.from_node
                                output_socket = link.from_socket
                                if output_node.name in node_map.keys():
                                    target_node = node_map[output_node.name]
                                    target_socket = target_node.outputs[output_socket.name]
                                    bpy.context.scene.world.node_tree.links.new(target_socket, input)

                bpy.context.scene.world = target_world
                world = bpy.context.scene.world
                if world is None:
                    print("There is no active world in the scene.")
                else:
                    # Blender 5.0+: Set sky_type for Sky Texture nodes
                    if bpy.app.version >= (5, 0, 0):
                        for node in world.node_tree.nodes:
                            if node.type == 'TEX_SKY' and hasattr(node, 'sky_type'):
                                node.sky_type = 'MULTIPLE_SCATTERING'
                    
                    for node in world.node_tree.nodes:                                      
                        if node.label == "KH-NIGHT":
                            for other_node in world.node_tree.nodes:
                                if other_node.label == "KH-LIGHT PATH":
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[3])
                                    world.node_tree.links.new(other_node.outputs[4], node.inputs[4])
                                    
                                if other_node.label == "KH-SUN":
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[5])
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[6])
                                    
                                if other_node.label == "KH-NIGHT MIX":
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[7])
                                    world.node_tree.links.new(other_node.outputs[1], node.inputs[8])
                                
                        elif node.label == "KH-MAPPING":
                            for other_node in world.node_tree.nodes:
                                if other_node.label == "KH-EXR":
                                    world.node_tree.links.new(other_node.inputs[0], node.outputs[0])
                                    
                                if other_node.label == "KH-HDRI":
                                    world.node_tree.links.new(other_node.inputs[0], node.outputs[0])
                                    
                                if other_node.label == "KH-COOR":
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[0])
                            node.inputs[1].default_value[2]=0.12
 
                        elif node.label == "KH-MIX":
                            for other_node in world.node_tree.nodes:
                                if other_node.label == "KH-NIGHT MIX":
                                    world.node_tree.links.new(other_node.inputs[0], node.outputs[0])
                                    world.node_tree.links.new(other_node.inputs[0], node.outputs[2])
                                        
                                if other_node.label == "KH-HDRI":
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[6])
                                    image_path = hdri_add_image_path
                                    if os.path.exists(image_path):
                                        bpy.ops.image.open(filepath=image_path)
                                        other_node.image = bpy.data.images.get(os.path.basename(image_path))
                                    
                                if other_node.label == "KH-EXR":
                                    world.node_tree.links.new(other_node.outputs[0], node.inputs[7])
                                    image_path = exr_add_image_path
                                    if os.path.exists(image_path):
                                        bpy.ops.image.open(filepath=image_path)
                                        other_node.image = bpy.data.images.get(os.path.basename(image_path))
                                                        
                                node.inputs[0].default_value = 0
                                node.blend_type = 'MIX'

                        elif node.label == "KH-Clouds Output":
                            for other_node in world.node_tree.nodes:
                                if other_node.label == "KH-NIGHT":
                                    #if len(node.inputs[0].links) == 0:
                                        world.node_tree.links.new(node.inputs[0], other_node.outputs[0])
                                        
            scene = bpy.context.scene
            world = scene.world
            nodes = world.node_tree.nodes
            nodes_to_delete = [node for node in nodes if node.type == 'OUTPUT_WORLD' and node.label != "KH-Clouds Output"]
            for node in nodes_to_delete:
                nodes.remove(node)
                
            nodes_to_delete = [node for node in nodes if node.type == 'MAPPING' and node.label != "KH-MAPPING"]
            for node in nodes_to_delete:
                nodes.remove(node)
                
            nodes_to_delete = [node for node in nodes if node.type == 'TEX_ENVIRONMENT' and node.label != "KH-HDRI" and node.label != "KH-EXR"]
            for node in nodes_to_delete:
                nodes.remove(node)
                
            #delete_world_driver()
            #driver_world_add()
        return {'FINISHED'}        


# class Link_world_driver(bpy.types.Operator):
#     """Link world HDRI"""
#     bl_idname = "object.world_driver_add"
#     bl_label = "Link Rotation"
    
#     def execute(self, context):
#         #delete_world_driver()
#         #driver_world_add()
#         return {'FINISHED'} 
     
# class Delete_world_driver(bpy.types.Operator):
#     """Delete Link world"""
#     bl_idname = "object.delete_world_driver"
#     bl_label = "Delete Link Rotation"
    
#     def execute(self, context):
#         delete_world_driver()
#         return {'FINISHED'} 
    
class Updatesky(bpy.types.Operator):
    bl_idname = "object.update_sky"
    bl_label = "Update Sky"

    def execute(self, context):
        world = bpy.context.scene.world
        for node in world.node_tree.nodes:
            if node.label == "KH-Clouds Output":
                for other_node in world.node_tree.nodes:
                    if other_node.label == "KH-SKY":
                            world.node_tree.links.new(node.inputs[0], other_node.outputs[0])
                    elif other_node.label == "KH-NIGHT":
                            world.node_tree.links.new(node.inputs[0], other_node.outputs[0])
                            
            scene = bpy.context.scene
            world = scene.world
            nodes = world.node_tree.nodes
            nodes_to_delete = [node for node in nodes if node.type == 'OUTPUT_WORLD' and node.label != "KH-Clouds Output"]
            for node in nodes_to_delete:
                nodes.remove(node)
                
            nodes_to_delete = [node for node in nodes if node.type == 'MAPPING' and node.label != "KH-MAPPING"]
            for node in nodes_to_delete:
                nodes.remove(node)
                
            nodes_to_delete = [node for node in nodes if node.type == 'TEX_ENVIRONMENT' and node.label != "KH-HDRI" and node.label != "KH-EXR"]
            for node in nodes_to_delete:
                nodes.remove(node)
        return {'FINISHED'} 
   
def delete_world_by_name(world_name):
    for world in bpy.data.worlds:
        if world.name == world_name:
            bpy.data.worlds.remove(world, do_unlink=True)
            return
 
class deletesky(bpy.types.Operator):
    bl_idname = "object.delete_sky"
    bl_label = "Delete Sky"

    def execute(self, context):
        # if bpy.context.scene.world is not None:
        #     scene = bpy.context.scene
        #     world = scene.world
        #     nodes = world.node_tree.nodes
        #     nodes_to_delete = [node for node in nodes if node.label == "KH-Clouds Output" or node.label == "KH-SKY" or node.label == "KH-SUN" or node.label == "KH-Clouds"]
        #     for node in nodes_to_delete:
        #         nodes.remove(node)
        if bpy.context.scene.world is not None:
            scene = bpy.context.scene
            world = scene.world
            nodes = world.node_tree.nodes
            nodes_to_delete = [node for node in nodes if node.label.startswith("KH-")]
            for node in nodes_to_delete:
                nodes.remove(node)
                
        world_name_to_delete = "KH - Clouds"
        world_name_to_delete1 = "KH-NIGHT"
        delete_world_by_name(world_name_to_delete)
        delete_world_by_name(world_name_to_delete1)
        bpy.ops.outliner.orphans_purge(do_recursive=True)
        return {'FINISHED'} 
    
#kh_ies/////////////////////////////////////////////////////////////////////////////////////////// 
class kh_ies(bpy.types.Operator):
    bl_idname = "object.kh_ies"
    bl_label = "IES"

    def execute(self, context):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        folder_path = os.path.join(script_dir, "IES")
        file_name = "1.IES"
        ies_file_path = os.path.join(folder_path, file_name)
        selected_object = bpy.context.object
        if selected_object :
            if selected_object.type == 'LIGHT' and selected_object.data.type in {'POINT', 'SPOT', 'AREA'}:
                if not selected_object.data.use_nodes:
                    selected_object.data.use_nodes = True
                
                ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
                if ies_node:
                        selected_object.data.node_tree.nodes.remove(ies_node)
                
                ies_node = selected_object.data.node_tree.nodes.new('ShaderNodeTexIES')
                ies_node.mode = 'EXTERNAL'
                ies_node.label = "KH-IES"
                ies_node.filepath = ies_file_path
                
                shader_node = selected_object.data.node_tree.nodes.get('Emission')
                if shader_node:
                    strength_input = shader_node.inputs.get('Strength')
                    if strength_input:
                        selected_object.data.node_tree.links.new(ies_node.outputs[0], strength_input)
                        scene = context.scene
                        scene.my_image_index -= 1
        return {'FINISHED'} 

class delet_kh_ies(bpy.types.Operator):
    bl_idname = "object.delet_kh_ies"
    bl_label = "delet_kh_ies"

    def execute(self, context):
        selected_object = bpy.context.object
        if selected_object :
            if selected_object.type == 'LIGHT' and selected_object.data.type in {'POINT', 'SPOT', 'AREA'}:
                if not selected_object.data.use_nodes:
                    selected_object.data.use_nodes = True
                ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
                if ies_node:
                        selected_object.data.node_tree.nodes.remove(ies_node)  
        return {'FINISHED'} 
    
class OBJECT_OT_change_ies_file(bpy.types.Operator):
    """Change the IES file for the active light"""
    bl_idname = "script.change_ies_file"
    bl_label = "Change IES File"
    direction: bpy.props.StringProperty()

    def execute(self, context):
        selected_object = context.active_object
        if selected_object:
            ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
            if ies_node and ies_node.label == "KH-IES":
                current_file = ies_node.filepath
                script_dir = os.path.dirname(current_file)
                ies_files = [f for f in os.listdir(script_dir) if f.lower().endswith(('.ies', '.ies'))]  # Check both .IES and .ies
                ies_files.sort(key=lambda x: self.get_file_number(x))  # Custom sort by extracting numbers
                if ies_files:
                    current_index = ies_files.index(os.path.basename(current_file))
                    if self.direction == 'NEXT':
                        next_index = (current_index + 1) % len(ies_files)
                    else:
                        next_index = (current_index - 1) % len(ies_files)
                    next_file = os.path.join(script_dir, ies_files[next_index])
                    ies_node.filepath = next_file
                    
                    # Update enum property to sync with template_icon_view
                    context.scene.ies_files_enum = next_file
                    
                    # Update preview image
                    base_name = os.path.splitext(ies_files[next_index])[0]
                    image_path = None
                    for ext in ['.png', '.jpg', '.jpeg']:
                        potential_image = os.path.join(script_dir, base_name + ext)
                        if os.path.exists(potential_image):
                            image_path = potential_image
                            break
                    
                    if image_path:
                        try:
                            # Remove old image if exists
                            if hasattr(context.scene, 'my_image') and context.scene.my_image:
                                old_image = context.scene.my_image
                                if old_image and old_image.name in bpy.data.images:
                                    bpy.data.images.remove(old_image)
                            
                            # Load new image
                            new_image = bpy.data.images.load(image_path)
                            context.scene.my_image = new_image
                        except Exception as e:
                            print(f"Error loading preview image: {e}")
                    
                    # Force UI update
                    for area in context.screen.areas:
                        if area.type == 'VIEW_3D':
                            area.tag_redraw()
                    
                    bpy.ops.outliner.orphans_purge()
        return {'FINISHED'}

    def get_file_number(self, filename):
        match = re.search(r'\d+', filename)
        if match:
            return int(match.group())
        else:
            return float('inf')  # If no number found, place it at the end

class OBJECT_OT_ies_browser(bpy.types.Operator):
    """Browse IES files with preview thumbnails"""
    bl_idname = "object.ies_browser"
    bl_label = "IES Browser"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        # Load IES previews for current directory
        self.load_ies_previews(context)
        return context.window_manager.invoke_props_dialog(self, width=500)

    def load_ies_previews(self, context):
        """Load IES file previews with images from current directory"""
        selected_object = context.active_object
        if not selected_object or selected_object.type != 'LIGHT':
            return

        ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
        if not ies_node or ies_node.label != "KH-IES":
            return

        current_file = ies_node.filepath
        if not current_file:
            return

        script_dir = os.path.dirname(current_file)
        if not os.path.exists(script_dir):
            return

        # Clear existing previews
        if "ies_files" in ies_preview_collections:
            bpy.utils.previews.remove(ies_preview_collections["ies_files"])

        # Create new preview collection
        pcoll = bpy.utils.previews.new()
        ies_preview_collections["ies_files"] = pcoll

        # Get all IES files in directory
        ies_files = [f for f in os.listdir(script_dir) if f.lower().endswith('.ies')]
        ies_files.sort(key=lambda x: self.get_file_number(x))

        # Load preview images and create enum items
        enum_items = []
        for i, filename in enumerate(ies_files):
            filepath = os.path.join(script_dir, filename)

            # Find corresponding image file
            base_name = os.path.splitext(filename)[0]
            image_path = None

            # Check for different image extensions
            for ext in ['.png', '.jpg', '.jpeg']:
                potential_image = os.path.join(script_dir, base_name + ext)
                if os.path.exists(potential_image):
                    image_path = potential_image
                    break

            # Load image preview if available
            if image_path and os.path.exists(image_path):
                try:
                    # Create unique identifier for this preview
                    preview_id = f"ies_{base_name}"

                    # Load image into preview collection
                    preview = pcoll.load(preview_id, image_path, 'IMAGE')
                    enum_items.append((filepath, filename, f"IES: {filename}", preview.icon_id, i))
                    print(f"Loaded preview for {filename}: {preview.icon_id}")
                except Exception as e:
                    print(f"Error loading preview for {filename}: {e}")
                    # Fallback to default icon
                    enum_items.append((filepath, filename, f"IES: {filename}", 'LIGHT', i))
            else:
                # No image found, use default icon
                print(f"No image found for {filename}")
                enum_items.append((filepath, filename, f"IES: {filename}", 'LIGHT', i))

        # Store enum items in preview collection
        pcoll.ies_files = enum_items

        # Set current selection
        context.scene.ies_browser_selection = current_file

    def get_file_number(self, filename):
        """Extract number from filename for sorting"""
        match = re.search(r'\d+', filename)
        if match:
            return int(match.group())
        else:
            return float('inf')

    def update_ies_selection(self, context):
        """Update IES file when selection changes"""
        if hasattr(context.scene, 'ies_files_enum'):
            selected_path = context.scene.ies_files_enum
            selected_object = context.active_object
            if selected_object and selected_object.type == 'LIGHT':
                ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
                if ies_node and ies_node.label == "KH-IES":
                    ies_node.filepath = selected_path

    def draw(self, context):
        layout = self.layout

        # Header with better styling
        # header_box = layout.box()
        # header_row = header_box.row()
        #header_row.label(text="IES Library Browser", icon='LIGHT')
        #header_row.scale_y = 1.2

        layout.separator()

        # Get current IES file info
        selected_object = context.active_object
        current_file = ""

        if selected_object and selected_object.type == 'LIGHT':
            ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
            if ies_node and ies_node.label == "KH-IES":
                current_file = ies_node.filepath
                current_filename = os.path.basename(current_file)

                # Show current selection
                box = layout.box()
                row = box.row()
                row.label(text=f"Current: {current_filename}", icon='FILE_TICK')

        # Check if we have loaded previews
        if "ies_files" in ies_preview_collections:
            pcoll = ies_preview_collections["ies_files"]
            if hasattr(pcoll, 'ies_files') and pcoll.ies_files:

                layout.separator()

                # Header with file count
                header_row = layout.row()
                header_row.label(text=f"IES Library ({len(pcoll.ies_files)} files)", icon='LIGHT_DATA')

                # Create scrollable area for grid with better spacing
                # box = layout.box()
                # box.label(text="Click on any image to select IES file:", icon='INFO')

                # Add scroll area for better navigation with improved spacing
                scroll_box = box.column()
                scroll_box.scale_y = 2  # Reset to normal scale for better proportions
                scroll_box.scale_x = 1  # Reset to normal scale for better proportions

                # Grid layout - 2 columns per row (reduced for much larger images)
                files_per_row = 5
                total_files = len(pcoll.ies_files)

                for row_start in range(0, total_files, files_per_row):
                    row_end = min(row_start + files_per_row, total_files)

                    # Create row with 2 columns and better spacing
                    grid_row = scroll_box.row(align=False)  # Changed to False for better spacing between columns

                    for i in range(row_start, row_end):
                        filepath, filename, desc, icon_id, index = pcoll.ies_files[i]

                        # Create column for each file with better spacing
                        col = grid_row.column(align=True)
                        col.scale_x = 1  # Make columns much wider for larger image display

                        # Highlight current file with border
                        if filepath == current_file:
                            # Create highlighted box for current file
                            highlight_box = col.box()
                            highlight_box.alert = True
                            inner_col = highlight_box.column(align=True)
                        else:
                            inner_col = col

                        # Image preview button (extra large size for clear IES pattern visibility)
                        inner_col.scale_y = 1  # Make buttons significantly taller to see light distribution patterns clearly

                        if isinstance(icon_id, int):
                            # Custom image preview
                            op = inner_col.operator("object.select_ies_file", text="", icon_value=icon_id)
                        else:
                            # Default icon
                            op = inner_col.operator("object.select_ies_file", text="", icon=icon_id)

                        op.filepath = filepath

                        # File name label (better readable text)
                        inner_col.scale_y = 1
                        inner_col.label(text=filename)

                    # Fill remaining columns if needed
                    for j in range(row_end - row_start, files_per_row):
                        grid_row.column()

                    # Add spacing between rows for better visual separation
                    if row_end < total_files:
                        scroll_box.separator()

                # Action buttons
                layout.separator()
                row = layout.row()
                row.scale_y = 1.2
                # زر توليد الصور المصغرة
                row.operator("object.generate_ies_images", text="Generate Images", icon='IMAGE_DATA')
                #row.operator("object.ies_browser", text="Refresh", icon='FILE_REFRESH')

            else:
                layout.label(text="No preview data loaded", icon='ERROR')
                #layout.operator("object.ies_browser", text="Load Previews", icon='FILE_REFRESH')
        else:
            layout.label(text="Loading IES previews...", icon='TIME')
            #layout.operator("object.ies_browser", text="Load Previews", icon='FILE_REFRESH')

class OBJECT_OT_generate_ies_images(bpy.types.Operator):
    """
    توليد صور مصغرة لجميع ملفات IES في المجلد الحالي

    هذا الـ Operator محسن ليعمل مع أو بدون المكتبات الخارجية:
    - مع numpy & matplotlib: صور عالية الجودة
    - بدون المكتبات: صور بديلة بسيطة
    - معالجة شاملة للأخطاء
    - رسائل واضحة للمستخدم
    """
    bl_idname = "object.generate_ies_images"
    bl_label = "Generate IES Images"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # الحصول على مسار المجلد الحالي من IES node
        selected_object = context.active_object
        if not selected_object or selected_object.type != 'LIGHT':
            self.report({'ERROR'}, "يجب تحديد مصدر ضوء أولاً")
            return {'CANCELLED'}

        ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
        if not ies_node or ies_node.label != "KH-IES":
            self.report({'ERROR'}, "لا يوجد IES node في مصدر الضوء المحدد")
            return {'CANCELLED'}

        current_file = ies_node.filepath
        if not current_file:
            self.report({'ERROR'}, "لم يتم تحديد ملف IES")
            return {'CANCELLED'}

        # الحصول على مسار المجلد
        ies_folder = os.path.dirname(current_file)
        if not os.path.exists(ies_folder):
            self.report({'ERROR'}, "مجلد IES غير موجود")
            return {'CANCELLED'}

        # استيراد الدالة المطلوبة من Generate_IES_image
       
        from .Generate_IES_image import generate_images_for_folder

         

        # توليد الصور لجميع ملفات IES في المجلد
        generated_count, skipped_count = generate_images_for_folder(ies_folder)

        # إعادة تحميل المعاينات
        self.load_ies_previews(context)

        # تقرير النتائج
        if generated_count > 0:
            self.report({'INFO'}, f"تم توليد {generated_count} صورة جديدة")
            if skipped_count > 0:
                self.report({'INFO'}, f"تم تخطي {skipped_count} ملف")
        elif skipped_count > 0:
            self.report({'INFO'}, f"جميع الصور موجودة مسبقاً ({skipped_count} ملف)")
        else:
            self.report({'INFO'}, "لا توجد ملفات IES في المجلد")

        return {'FINISHED'}

    def load_ies_previews(self, context):
        """إعادة تحميل معاينات IES بعد توليد الصور"""
        # نسخ نفس الكود من OBJECT_OT_ies_browser
        selected_object = context.active_object
        if not selected_object or selected_object.type != 'LIGHT':
            return

        ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
        if not ies_node or ies_node.label != "KH-IES":
            return

        current_file = ies_node.filepath
        if not current_file:
            return

        script_dir = os.path.dirname(current_file)
        if not os.path.exists(script_dir):
            return

        # Clear existing previews
        if "ies_files" in ies_preview_collections:
            bpy.utils.previews.remove(ies_preview_collections["ies_files"])

        # Create new preview collection
        pcoll = bpy.utils.previews.new()
        ies_preview_collections["ies_files"] = pcoll

        # Get all IES files in directory
        ies_files = [f for f in os.listdir(script_dir) if f.lower().endswith('.ies')]
        ies_files.sort(key=lambda x: self.get_file_number(x))

        # Load preview images and create enum items
        enum_items = []
        for i, filename in enumerate(ies_files):
            filepath = os.path.join(script_dir, filename)

            # Find corresponding image file
            base_name = os.path.splitext(filename)[0]
            image_path = None

            # Check for different image extensions
            for ext in ['.png', '.jpg', '.jpeg']:
                potential_image = os.path.join(script_dir, base_name + ext)
                if os.path.exists(potential_image):
                    image_path = potential_image
                    break

            if image_path:
                try:
                    thumb = pcoll.load(filepath, image_path, 'IMAGE')
                    icon_id = thumb.icon_id
                except:
                    icon_id = 'LIGHT'
            else:
                icon_id = 'LIGHT'

            enum_items.append((filepath, filename, f"IES File: {filename}", icon_id, i))

        # Store enum items in preview collection
        pcoll.ies_files = enum_items

        # Set current selection
        context.scene.ies_browser_selection = current_file

    def get_file_number(self, filename):
        """Extract number from filename for sorting"""
        import re
        match = re.search(r'\d+', filename)
        if match:
            return int(match.group())
        else:
            return float('inf')

class OBJECT_OT_select_ies_file(bpy.types.Operator):
    """Select an IES file"""
    bl_idname = "object.select_ies_file"
    bl_label = "Select IES File"

    filepath: bpy.props.StringProperty()

    def execute(self, context):
        selected_object = context.active_object
        if selected_object and selected_object.type == 'LIGHT':
            ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
            if ies_node and ies_node.label == "KH-IES":
                # Update the IES file path
                ies_node.filepath = self.filepath
                
                # Update enum property to sync with template_icon_view
                context.scene.ies_files_enum = self.filepath

                # Update the preview image in the UI
                scene = context.scene
                ies_file_name = os.path.splitext(os.path.basename(self.filepath))[0]

                # Find corresponding image file in the same directory as IES file
                ies_dir = os.path.dirname(self.filepath)

                # Look for image with same base name
                image_path = None
                for ext in ['.png', '.jpg', '.jpeg']:
                    potential_image = os.path.join(ies_dir, ies_file_name + ext)
                    if os.path.exists(potential_image):
                        image_path = potential_image
                        break

                # Load the corresponding image
                if image_path:
                    try:
                        # Remove old image if exists
                        if hasattr(scene, 'my_image') and scene.my_image:
                            old_image = scene.my_image
                            if old_image and old_image.name in bpy.data.images:
                                bpy.data.images.remove(old_image)
                        # Load new image
                        scene.my_image = bpy.data.images.load(image_path)
                    except Exception as e:
                        print(f"Error loading image: {e}")
                        scene.my_image = None
                else:
                    # No image found, clear preview
                    if hasattr(scene, 'my_image') and scene.my_image:
                        old_image = scene.my_image
                        if old_image and old_image.name in bpy.data.images:
                            bpy.data.images.remove(old_image)
                        scene.my_image = None

                # Update scene to reflect changes
                context.scene.frame_set(context.scene.frame_current)

                filename = os.path.basename(self.filepath)
                self.report({'INFO'}, f"IES file changed to: {filename}")

                # Force redraw of any open browsers and UI
                try:
                    for area in context.screen.areas:
                        area.tag_redraw()
                except:
                    pass

                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "No IES node found")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "No light selected")
            return {'CANCELLED'}


class OBJECT_OT_refresh_ies_list(bpy.types.Operator):
    """Refresh IES files list and previews"""
    bl_idname = "object.refresh_ies_list"
    bl_label = "Refresh IES List"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Clear existing preview collection
        if "ies_files" in ies_preview_collections:
            bpy.utils.previews.remove(ies_preview_collections["ies_files"])
            del ies_preview_collections["ies_files"]
        
        # Force update of enum property
        context.scene.property_unset("ies_files_enum")
        
        # Redraw UI
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        self.report({'INFO'}, "IES list refreshed")
        return {'FINISHED'}


class OBJECT_OT_random_ies_file(bpy.types.Operator):
    """Select a random IES file"""
    bl_idname = "object.random_ies_file"
    bl_label = "Random IES"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        import random
        
        selected_object = context.active_object
        if not selected_object or selected_object.type != 'LIGHT':
            self.report({'ERROR'}, "No light selected")
            return {'CANCELLED'}
        
        if not selected_object.data.use_nodes:
            self.report({'ERROR'}, "Light doesn't use nodes")
            return {'CANCELLED'}
            
        ies_node = selected_object.data.node_tree.nodes.get('IES Texture')
        if not ies_node or ies_node.label != "KH-IES":
            self.report({'ERROR'}, "No IES node found")
            return {'CANCELLED'}
        
        current_file = ies_node.filepath
        if not current_file:
            self.report({'ERROR'}, "No IES file set")
            return {'CANCELLED'}
        
        # Get directory and all IES files
        ies_dir = os.path.dirname(current_file)
        if not os.path.exists(ies_dir):
            self.report({'ERROR'}, "IES directory not found")
            return {'CANCELLED'}
        
        ies_files = [f for f in os.listdir(ies_dir) if f.lower().endswith('.ies')]
        
        if len(ies_files) <= 1:
            self.report({'WARNING'}, "Not enough IES files to randomize")
            return {'CANCELLED'}
        
        # Select random file (different from current)
        current_filename = os.path.basename(current_file)
        available_files = [f for f in ies_files if f != current_filename]
        
        if not available_files:
            self.report({'WARNING'}, "No other IES files available")
            return {'CANCELLED'}
        
        random_file = random.choice(available_files)
        new_filepath = os.path.join(ies_dir, random_file)
        
        # Update IES node
        ies_node.filepath = new_filepath
        
        # Update enum property (this will trigger update_ies_selection which updates the image)
        context.scene.ies_files_enum = new_filepath
        
        # Update preview image
        base_name = os.path.splitext(random_file)[0]
        image_path = None
        for ext in ['.png', '.jpg', '.jpeg']:
            potential_image = os.path.join(ies_dir, base_name + ext)
            if os.path.exists(potential_image):
                image_path = potential_image
                break
        
        if image_path:
            try:
                # Remove old image if exists
                if hasattr(context.scene, 'my_image') and context.scene.my_image:
                    old_image = context.scene.my_image
                    if old_image and old_image.name in bpy.data.images:
                        bpy.data.images.remove(old_image)
                
                # Load new image
                new_image = bpy.data.images.load(image_path)
                context.scene.my_image = new_image
            except Exception as e:
                print(f"Error loading preview image: {e}")
        
        # Force UI update
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        
        self.report({'INFO'}, f"Random IES: {random_file}")
        return {'FINISHED'}

    
        
# Define the directory path
script_dir = os.path.dirname(os.path.realpath(__file__))
directoryies = os.path.join(script_dir, "IES")
#directory = "C:/Users/looks/AppData/Roaming/Blender Foundation/Blender/4.2/scripts/addons/KH-Tools/Light_Manager/IES"

# Function to update the image displayed in the UI
def update_image(self, context):
    scene = context.scene
    light = bpy.context.object
    if light.type == 'LIGHT' and light.data.type in {'POINT', 'SPOT', 'AREA'}:
        ies_file_name = os.path.splitext(os.path.basename(light.data.node_tree.nodes['IES Texture'].filepath))[0]
        img_path_png = os.path.join(directoryies, ies_file_name + ".png")
        img_path_jpg = os.path.join(directoryies, ies_file_name + ".jpg")
        
        if os.path.exists(img_path_png):
            scene.my_image = bpy.data.images.load(img_path_png)
        elif os.path.exists(img_path_jpg):
            scene.my_image = bpy.data.images.load(img_path_jpg)
        else:
            scene.my_image = None

# Function to update the IES file path
def update_ies_path(image_path):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    folder_path = os.path.join(script_dir, "IES")
    file_name = os.path.splitext(os.path.basename(image_path))[0] + ".IES"
    ies_file_path = os.path.join(directoryies, file_name)
    
    # Set the IES file path for selected light objects
    for obj in bpy.context.selected_objects:
        if obj.type == 'LIGHT' and obj.data.type in {'POINT', 'SPOT', 'AREA'}:
            if not obj.data.use_nodes:
                obj.data.use_nodes = True
            
            ies_node = obj.data.node_tree.nodes.get('IES Texture')
            if ies_node:
                obj.data.node_tree.nodes.remove(ies_node)
            
            ies_node = obj.data.node_tree.nodes.new('ShaderNodeTexIES')
            ies_node.mode = 'EXTERNAL'
            ies_node.label = "KH-IES"
            ies_node.filepath = ies_file_path
            
            shader_node = obj.data.node_tree.nodes.get('Emission')
            if shader_node:
                strength_input = shader_node.inputs.get('Strength')
                if strength_input:
                    obj.data.node_tree.links.new(ies_node.outputs[0], strength_input)


# Define the previous image operator
class IMAGE_OT_Previous(bpy.types.Operator):
    bl_idname = "image.previous"
    bl_label = "Previous Image"

    def execute(self, context):
        scene = context.scene
        scene.my_image_index -= 1
        return {'FINISHED'}

# Define the next image operator
class IMAGE_OT_Next(bpy.types.Operator):
    bl_idname = "image.next"
    bl_label = "Next Image"

    def execute(self, context):
        scene = context.scene
        scene.my_image_index += 1
        return {'FINISHED'}


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class KH_Temperature(bpy.types.Operator):
    bl_idname = "object.temperature"
    bl_label = "Temperature"

    def execute(self, context):
        selected_object = bpy.context.object
        if selected_object :
            if selected_object.type == 'LIGHT' and selected_object.data.type in {'POINT', 'SPOT', 'AREA'}:
                if not selected_object.data.use_nodes:
                    selected_object.data.use_nodes = True
                Blackbody = selected_object.data.node_tree.nodes.get('Blackbody')
                if Blackbody:
                        selected_object.data.node_tree.nodes.remove(Blackbody)  
                Blackbody = selected_object.data.node_tree.nodes.new('ShaderNodeBlackbody')
                Blackbody.label = "KH-Temperature"
                shader_node = selected_object.data.node_tree.nodes.get('Emission')
                if shader_node:
                    strength_input = shader_node.inputs.get('Color')
                    if strength_input:
                        selected_object.data.node_tree.links.new(Blackbody.outputs[0], strength_input)
        return {'FINISHED'} 
    
class delet_KH_Temperature(bpy.types.Operator):
    bl_idname = "object.delet_temperature"
    bl_label = "delet_temperature"

    def execute(self, context):
        selected_object = bpy.context.object
        if selected_object :
            if selected_object.type == 'LIGHT' and selected_object.data.type in {'POINT', 'SPOT', 'AREA'}:
                if not selected_object.data.use_nodes:
                    selected_object.data.use_nodes = True
                Blackbody = selected_object.data.node_tree.nodes.get('Blackbody')
                if Blackbody:
                        selected_object.data.node_tree.nodes.remove(Blackbody)  
        return {'FINISHED'} 

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def check_and_explode(mat_name):
    bpy.ops.object.select_all(action='DESELECT')
    object_with_material = None
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and any(mat.name.lower().startswith(mat_name) for mat in obj.data.materials):
            for slot in obj.material_slots:
                if slot.material:
                    if slot.material and slot.material.name.lower().startswith(mat_name):
                        object_with_material = obj
                        
                        if object_with_material and object_with_material.data.users == 1:
                            object_with_material.select_set(True)
                            bpy.context.view_layer.objects.active = object_with_material
                            bpy.ops.object.skp_explode()
                            #break

def delete_spot_r_lights(light_delete):
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.name.startswith(light_delete):
            bpy.data.objects.remove(obj, do_unlink=True)


def rename_objects(kh_opj):
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.name.lower().startswith(kh_opj):
            obj.name = "KH " + obj.name
            

def rename_materials(old_mat,kh_materials):
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            if obj.data.materials:
                for material_slot in obj.material_slots:
                    mat = material_slot.material
                    if mat and material_slot.material.name.lower().startswith(old_mat):
                        material_slot.material.name = kh_materials


def rename_materials_delete_kh(old_mat):
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            if obj.data.materials:
                for material_slot in obj.material_slots:
                    mat = material_slot.material
                    if mat and material_slot.material.name.lower().startswith(old_mat):
                        material_slot.material.name = material_slot.material.name.lower().replace("kh ","")
                        
                        
def merge_objects_with_material_prefix(prefix):
    objects = bpy.context.scene.objects
    objects_to_merge = []
    for obj in objects:
        if obj.type == 'MESH' and len(obj.data.materials) == 1:
            material = obj.data.materials[0]
            if material and material.name.startswith(prefix) and material.users > 1:
                objects_to_merge.append(obj)
    
    if objects_to_merge:
        for obj in objects_to_merge:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects_to_merge[0]
        bpy.ops.object.join()

def collection_selected_object_name():
    if bpy.context.object is not None :
        selected_object = bpy.context.object
        object_name = selected_object.name
        collection = bpy.data.collections.new(object_name)

        if 'Light' in bpy.data.collections:
            light_collection = bpy.data.collections['Light']
        else:
            light_collection = bpy.data.collections.new('Light')
            bpy.context.scene.collection.children.link(light_collection)

        light_collection.children.link(collection)
                        

        
def point_Curtain():
    delete_spot_r_lights('KH Internal')
    #check_and_explode("curtain")
    rename_materials_delete_kh("kh curtain")
    material_objects = [
            obj for obj in bpy.data.objects
            if obj.type == 'MESH' and any(mat and mat.name.lower().startswith("curtain") for mat in obj.data.materials)
        ]

    light_objects = [
        obj for obj in bpy.data.objects
        if obj.type == 'LIGHT' and obj.name.lower().startswith("kh internal")
    ]
    added_lights = []
    if not light_objects :
        if material_objects:
            for obj in material_objects:
                center = obj.location
                if not light_objects :
                    bpy.ops.object.light_add(type='POINT', location=center)
                    bpy.context.active_object.name = "KH Internal"
                    added_light = bpy.context.active_object
                    added_light.location[2] += 0.6
                    added_lights.append(added_light)
    
            bpy.ops.object.select_all(action='DESELECT')
            for light in added_lights:
                light.select_set(True)
                
            bpy.context.view_layer.objects.active = added_lights[0]
            bpy.ops.object.make_links_data(type='OBDATA')
            
             # الحصول على أو إنشاء مجموعة "Spot"
            if "Internal" not in bpy.data.collections:
                spot_collection = bpy.data.collections.new("Internal")
                bpy.context.scene.collection.children.link(spot_collection)
            else:
                spot_collection = bpy.data.collections["Internal"]
            
            # إضافة الأضواء إلى مجموعة "Spot" وإزالتها من أي مجموعة سابقة
            for light in added_lights:
                for collection in light.users_collection:
                    collection.objects.unlink(light)
                spot_collection.objects.link(light)
    #rename_objects("curtain")
    rename_materials("curtain","kh curtain")
    bpy.ops.outliner.orphans_purge()
    
def point_glass():
    delete_spot_r_lights('KH Internal')
    check_and_explode("in glass")
    rename_materials_delete_kh("kh in glass")
    material_objects = [
            obj for obj in bpy.data.objects
            if obj.type == 'MESH' and any(mat.name.lower().startswith("in glass") for mat in obj.data.materials)
        ]

    light_objects = [
        obj for obj in bpy.data.objects
        if obj.type == 'LIGHT' and obj.name.lower().startswith("kh internal")
    ]
    added_lights = []
    if not light_objects :
        if material_objects:
            for obj in material_objects:
                center = obj.location
                if not light_objects :
                    bpy.ops.object.light_add(type='POINT', location=center)
                    bpy.context.active_object.name = "KH Internal"
                    added_light = bpy.context.active_object
                    added_light.location[2] += 0.6
                    added_lights.append(added_light)
    
            bpy.ops.object.select_all(action='DESELECT')
            for light in added_lights:
                light.select_set(True)
                
            bpy.context.view_layer.objects.active = added_lights[0]
            bpy.ops.object.make_links_data(type='OBDATA')
            
             # الحصول على أو إنشاء مجموعة "Spot"
            if "Internal" not in bpy.data.collections:
                spot_collection = bpy.data.collections.new("Internal")
                bpy.context.scene.collection.children.link(spot_collection)
            else:
                spot_collection = bpy.data.collections["Internal"]
            
            # إضافة الأضواء إلى مجموعة "Spot" وإزالتها من أي مجموعة سابقة
            for light in added_lights:
                for collection in light.users_collection:
                    collection.objects.unlink(light)
                spot_collection.objects.link(light)
    #rename_objects("in glass")
    rename_materials("in glass","kh in glass")
    
    merge_objects_with_material_prefix("kh in glass")
    bpy.ops.outliner.orphans_purge()
    
           
def spot_roof():
    delete_spot_r_lights('KH Spot Roof')
    check_and_explode("r spot")
    rename_materials_delete_kh("kh r spot")
    Roof_objects = [
        obj for obj in bpy.data.objects
        if obj.type == 'MESH' and any(mat.name.lower().startswith("r spot") for mat in obj.data.materials)
    ]

    spot_objects = [
        obj for obj in bpy.data.objects
        if obj.type == 'LIGHT' and obj.name.lower().startswith("kh spot roof")
    ]
    
    added_lights = []
    if not spot_objects :
        if Roof_objects:
            for obj in Roof_objects:
                center = obj.location
                if not spot_objects :
                    bpy.ops.object.light_add(type='SPOT', location=center)
                    bpy.context.active_object.name = "KH Spot Roof"
                    added_light = bpy.context.active_object
                    added_light.location[2] -= 0.03
                    added_lights.append(added_light)
    
            bpy.ops.object.select_all(action='DESELECT')
            for light in added_lights:
                light.select_set(True)
                
            bpy.context.view_layer.objects.active = added_lights[0]
            bpy.ops.object.make_links_data(type='OBDATA')
            
            # الحصول على أو إنشاء مجموعة "Spot"
            if "Spot" not in bpy.data.collections:
                spot_collection = bpy.data.collections.new("Spot")
                bpy.context.scene.collection.children.link(spot_collection)
            else:
                spot_collection = bpy.data.collections["Spot"]
            
            # إضافة الأضواء إلى مجموعة "Spot" وإزالتها من أي مجموعة سابقة
            for light in added_lights:
                for collection in light.users_collection:
                    collection.objects.unlink(light)
                spot_collection.objects.link(light)
    #rename_objects("r spot")
    rename_materials("r spot","kh r spot")
    merge_objects_with_material_prefix("kh r spot")
    bpy.ops.outliner.orphans_purge()
    
def spot_wall():
    delete_spot_r_lights('KH Spot Wall')
    check_and_explode("w spot")
    rename_materials_delete_kh("kh w spot")
    wall_objects = [
            obj for obj in bpy.data.objects
            if obj.type == 'MESH' and any(mat.name.lower().startswith("w spot") for mat in obj.data.materials)
        ]

    spot_wall = [
        obj for obj in bpy.data.objects
        if obj.type == 'LIGHT' and obj.name.lower().startswith("KH Spot Wall")
    ]
    added_lights = []
    if not spot_wall :
        if wall_objects:
            for obj in wall_objects:
                center = obj.location
                if not spot_wall :
                    bpy.ops.object.light_add(type='SPOT', location=center)
                    bpy.context.active_object.name = "KH Spot Wall"
                    added_light = bpy.context.active_object
                    added_light.location[2] -= 0.1
                    added_lights.append(added_light)
                    
                    bpy.ops.object.light_add(type='SPOT', location=center)
                    bpy.context.active_object.name = "KH Spot Wall"
                    added_light = bpy.context.active_object
                    added_light.location[2] += 0.1
                    added_light.rotation_euler[0] = 3.14159
                    added_lights.append(added_light)
                    
            bpy.ops.object.select_all(action='DESELECT')
            for light in added_lights:
                light.select_set(True)
                
            bpy.context.view_layer.objects.active = added_lights[0]
            bpy.ops.object.make_links_data(type='OBDATA')
            
            if "Wall" not in bpy.data.collections:
                spot_collection = bpy.data.collections.new("Wall")
                bpy.context.scene.collection.children.link(spot_collection)
            else:
                spot_collection = bpy.data.collections["Wall"]
                
            for light in added_lights:
                for collection in light.users_collection:
                    collection.objects.unlink(light)
                spot_collection.objects.link(light)
    #rename_objects("w spot")
    rename_materials("w spot","kh w spot")
    
    merge_objects_with_material_prefix("kh w spot")
    bpy.ops.outliner.orphans_purge()
    
    
def add_lights_to_active_object():
    if bpy.context.object is not None :
        selected_object = bpy.context.object
        object_name = selected_object.name
        collection1 = bpy.data.collections.new(object_name)

        if 'Light' in bpy.data.collections:
            light_collection = bpy.data.collections['Light']
        else:
            light_collection = bpy.data.collections.new('Light')
            bpy.context.scene.collection.children.link(light_collection)

        light_collection.children.link(collection1)
        
    added_lights = []
    exploded_objects = []
    active_object = bpy.context.active_object
    if active_object and active_object.type == 'MESH' and len(bpy.context.selected_objects) == 1:
        if len(active_object.material_slots) == 1:
            if active_object.data.users == 1:
                bpy.ops.object.skp_explode()
                
        exploded_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
        for obj in exploded_objects:
            center = obj.location
            bpy.ops.object.light_add(type='POINT', location=center)
            bpy.context.active_object.name = obj.name
            added_light = bpy.context.active_object
            added_lights.append(added_light)
            
    if exploded_objects:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in exploded_objects:
            if len(obj.material_slots) == 1:
                if obj.data.users == 1:
                    obj.select_set(True)
        if bpy.context.view_layer.objects.active is not None:            
            bpy.context.view_layer.objects.active = exploded_objects[0]
            bpy.ops.object.join()
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')


    if added_lights:
        bpy.ops.object.select_all(action='DESELECT')
        for light in added_lights:
            light.select_set(True)
        bpy.context.view_layer.objects.active = added_lights[0]
        bpy.ops.object.make_links_data(type='OBDATA')
    
        for light in added_lights:
            obj_name = light.name.split('.')[0] 
            light_collection_name = collection1.name 
            light_collection = bpy.data.collections.get(light_collection_name) 
            if light_collection is not None: 
                for collection in light.users_collection:
                    collection.objects.unlink(light)
                light_collection.objects.link(light)
                
    bpy.ops.outliner.orphans_purge()



    
class KH_point_Curtain(bpy.types.Operator):
    bl_idname = "object.point_curtain"
    bl_label = "light to curtain (Curtain)"
    bl_description = "light to curtain (Curtain)"
    
    def execute(self, context):
        point_Curtain()
        return {'FINISHED'}

class KH_point_glass(bpy.types.Operator):
    bl_idname = "object.point_glass"
    bl_label = "light to Glass (KH Glass)"
    bl_description = "light to Glass (KH Glass)"
    
    def execute(self, context):
        point_glass()
        return {'FINISHED'}

class KH_spot_roof(bpy.types.Operator):
    bl_idname = "object.spot_roof"
    bl_label = "light to Spot Roof (R Spot)"
    bl_description = "light to Spot Roof (R Spot)"

    def execute(self, context):
        spot_roof() 
        return {'FINISHED'}   
    
class KH_spot_wall(bpy.types.Operator):
    bl_idname = "object.spot_wall"
    bl_label = "spot to light wall(W Spot)"
    bl_description = "spot to light wall(W Spot)"

    def execute(self, context):
        spot_wall() 
        return {'FINISHED'} 

class kh_light_to_active_object(bpy.types.Operator):
    bl_idname = "object.kh_light_to_active_object"
    bl_label = " add light to active object"
    bl_description = "add light to active object"

    def execute(self, context):
        add_lights_to_active_object() 
        return {'FINISHED'} 
    

classes = (                              
            kh_ShaderNodeEmissionKeyframe,
            kh_ShaderNodeEmissionKeyframeDelete,
            kh_ShaderNodeEmissionName,
            kh_ShaderNodeEmissionName_ALL,
            kh_ShaderNodeEmissionShow100,
            kh_ShaderNodeEmissionShow,
            kh_ShaderNodeEmissionHide,
            kh_ShaderNodeEmissionSelectb,
            kh_Delete_Led,

            #Light Manager//////////////////////////////////////////////////////
            VIEW3D_PT_light_manager,
            VIEW3D_PT_light_managerlist,
            EmissionListPanel,
            AddSkyPanel,
            AddSunPanel,
            MATERIAL_PT_override,
            VolumetricPanel,
            
            EASYHDRI_OT_reload_previews,
            EASYHDRI_OT_remove_unused_images,
            EASYHDRI_OT_next_image,
            EASYHDRI_OT_previous_image,
            EASYHDRI_OT_add_to_fav,
            EASYHDRI_OT_remove_from_fav,
            SettingsMenu,

            AddPointLightOperator,
            AddSpotLightOperator,
            AddAreaLightOperator,
            LightManagerScaleSpotLights,
            LightManagerScaleSpot,
            LightManagerEnableGlossy,
            LightManagerDisableGlossy,
            OBJECT_OT_select_by_name,
            
            AddSunOperator,
            RemoveSunOperator,
            addsky,
            Updatesky,
            deletesky,
            
            CreateVolumemetricCube,
            DeleteVolumemetricCube,
            OBJECT_OT_dome_light,
            DeleteDomeLightOperator,
            Reset_DomeLightOperator,
            AddDomeLightPanel,
            DoomLitePanel,
               
            Add_Override,
            Delete_Override,
            kh_ies,
            delet_kh_ies,
            OBJECT_OT_change_ies_file,
            OBJECT_OT_ies_browser,
            OBJECT_OT_generate_ies_images,
            OBJECT_OT_select_ies_file,
            OBJECT_OT_refresh_ies_list,
            OBJECT_OT_random_ies_file,
            KH_Temperature,
            delet_KH_Temperature,
            KH_sun_Temperature,
            delet_KH_sun_Temperature,
            SetLightVisibilityOperator,
            SetLight_hidine_Operator,
            Activate_Dom_Nightly,
            Activate_Dom_day,
            #Link_DomeLight_driver,
            DeleteDomeLight_driver,
            KH_IMAGE_OT_open_hdri,
            KH_IMAGE_OT_open_exr,
            #Link_world_driver,
            #Delete_world_driver,
            kh_Add_Shadow,
            UpdateShadow,
            KH_point_Curtain,
            KH_point_glass,
            KH_spot_roof,
            KH_spot_wall,
            kh_light_to_active_object,
            
            KH_NIGHT,
            
            #ies/////////////
            #IMAGE_PT_Panel,
            IMAGE_OT_Previous,
            IMAGE_OT_Next,
           
                )

def register():
    for i in classes:
        register_class(i)
    
    #Light Manager//////////////////////////////////////////////////////
    pcoll1 = previews.new()     
    preview_collections2["prev"] = pcoll1
    bpy.types.Scene.prev = EnumProperty(items = env_previews, update = update_hdr)
    bpy.types.Scene.favs = EnumProperty(name = 'Favorites', items = get_favs_enum, update = update_favs, description = 'List of the favorit folders')
    bpy.types.Scene.dynamic_load = BoolProperty(default = True, description = 'Load the images dynamically')        
    bpy.types.Scene.dynamic_cleanup = BoolProperty(default = True, description = 'Remove 0 user images dynamically')    
    bpy.types.Scene.recursive_search = BoolProperty(default = False, update = update_dir, description = 'Enable/Disable Recursive search')
    bpy.types.Scene.set_projection = BoolProperty(default = False, update = update_hdr, description = 'Set the projection dynamically')    
    bpy.types.Scene.previews_dir = StringProperty(
            name="Folder Path",
            subtype='DIR_PATH',
            default="",
            update = update_dir,
            description = 'Path to the folder containing the images'      
            )
    bpy.types.Scene.sub_dirs = IntProperty(
            default = 0,
            min = 0, max = 20,
            update = update_dir,
            description = 'Look for HDRIs in the sub folder(s), at this level, 0 = No recursion'
            )
           
    bpy.types.Scene.easyhdr_expand_settings = BoolProperty(default = True, description = 'Expand/collapse this menu')
    bpy.types.Scene.easyhdr_expand_bg = BoolProperty(default = False, description = 'Expand/collapse this menu')
    bpy.types.Scene.easyhdr_expand_color = BoolProperty(default = False, description = 'Expand/collapse this menu')  
  
    bpy.types.Scene.lunk_dom = bpy.props.BoolProperty(
        name="Link Dom Light",
        description="Link Dom Light",
        default=False,
    ) 
    
    bpy.app.handlers.depsgraph_update_pre.append(handle_environment_texture_change)
    
    bpy.types.Scene.link_world_mapping = bpy.props.BoolProperty(
        name="Link Rotation",
        description="link world mapping & Hdri",
        default=True,
    )
    
    bpy.types.Scene.link_dome_mapping = bpy.props.BoolProperty(
        name="LINK DOME Rotation",
        description="Link Dome Mapping & world",
        default=False,
    )

    # IES Browser Properties
    bpy.types.Scene.ies_browser_selection = bpy.props.StringProperty(
        name="IES Selection",
        description="Currently selected IES file",
        default="",
    )
    
    # IES Files Enum with previews (similar to Gaffer HDRI)
    bpy.types.Scene.ies_files_enum = bpy.props.EnumProperty(
        name="IES Files",
        description="IES files with preview thumbnails",
        items=get_ies_enum_items,
        update=update_ies_selection,
    )
    
    bpy.types.Scene.dome_light_enabled = bpy.props.BoolProperty(
        name="Enable Dome Light",
        description="Enable or Disable the Dome Light",
        default=False,
        update=update_dome_light
    )
    
    #bpy.app.handlers.depsgraph_update_post.append(driver_world_add_handler)
    bpy.app.handlers.depsgraph_update_post.append(check_sun_rotation_callback)
    bpy.app.handlers.depsgraph_update_post.append(check_dome_rotation_callback)
    bpy.app.handlers.depsgraph_update_post.append(update_ies_preview_on_selection)
 
        
    #ies
    # Add properties to the scene
    bpy.types.Scene.my_image = bpy.props.PointerProperty(type=bpy.types.Image)
    bpy.types.Scene.my_image_index = bpy.props.IntProperty(default=0, min=0, update=update_image)

def unregister():
    for i in classes:
        unregister_class(i) 
    
    #Light Manager//////////////////////////////////////////////////////
    for pcoll1 in preview_collections2.values():
        previews.remove(pcoll1)
    preview_collections2.clear()

    # Clean up IES preview collections
    for pcoll in ies_preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    ies_preview_collections.clear()
    
    # التحقق من وجود الخصائص قبل حذفها لتجنب الأخطاء
    if hasattr(bpy.types.Scene, 'dynamic_load'):
        del bpy.types.Scene.dynamic_load
    if hasattr(bpy.types.Scene, 'dynamic_cleanup'):
        del bpy.types.Scene.dynamic_cleanup
    if hasattr(bpy.types.Scene, 'recursive_search'):
        del bpy.types.Scene.recursive_search
    if hasattr(bpy.types.Scene, 'set_projection'):
        del bpy.types.Scene.set_projection
    if hasattr(bpy.types.Scene, 'previews_dir'):
        del bpy.types.Scene.previews_dir
    if hasattr(bpy.types.Scene, 'easyhdr_expand_settings'):
        del bpy.types.Scene.easyhdr_expand_settings
    if hasattr(bpy.types.Scene, 'easyhdr_expand_bg'):
        del bpy.types.Scene.easyhdr_expand_bg
    if hasattr(bpy.types.Scene, 'easyhdr_expand_color'):
        del bpy.types.Scene.easyhdr_expand_color
    if hasattr(bpy.types.Scene, 'lunk_dom'):
        del bpy.types.Scene.lunk_dom
    if hasattr(bpy.types.Scene, 'link_dome_mapping'):
        del bpy.types.Scene.link_dome_mapping
    if hasattr(bpy.types.Scene, 'ies_browser_selection'):
        del bpy.types.Scene.ies_browser_selection
    if hasattr(bpy.types.Scene, 'ies_files_enum'):
        del bpy.types.Scene.ies_files_enum

    # إزالة handlers بأمان
    try:
        bpy.app.handlers.depsgraph_update_pre.remove(handle_environment_texture_change)
    except ValueError:
        pass  # Handler already removed or not present

    try:
        bpy.app.handlers.depsgraph_update_post.remove(check_sun_rotation_callback)
    except ValueError:
        pass  # Handler already removed or not present

    try:
        bpy.app.handlers.depsgraph_update_post.remove(update_ies_preview_on_selection)
    except ValueError:
        pass  # Handler already removed or not present

    #ies
    if hasattr(bpy.types.Scene, 'my_image'):
        del bpy.types.Scene.my_image
    if hasattr(bpy.types.Scene, 'my_image_index'):
        del bpy.types.Scene.my_image_index



if __name__ == "__main__":
    try:
        register()
    except:
        pass
    unregister()
