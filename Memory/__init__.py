bl_info = {
    "name": "KH-Memory",
    "author": "Khaled Alnwesary",
    "version": (1, 5),
    "blender": (4, 00, 0),
    "location": "OUTLINER > HT",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "KH",
}

import bpy
import os
import subprocess
import ctypes
import gc
from bpy.utils import previews
from bpy.utils import register_class, unregister_class

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


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_memory_optimizer(self, context):
    script_directory = os.path.dirname(os.path.realpath(__file__) if __file__ else bpy.data.filepath)
    program_path = os.path.join(script_directory, "Wise", "WiseMemoryOptimzer.exe")

    if os.path.exists(program_path):
        if is_admin():
            subprocess.Popen(program_path)
            self.report({'INFO'}, f"تم تشغيل {program_path} بنجاح.")
        else:
            # إعادة تشغيل البرنامج بصلاحيات المشرف
            ctypes.windll.shell32.ShellExecuteW(None, "runas", program_path, None, None, 1)
    else:
        self.report({'WARNING'}, f"لم يتم العثور على {program_path} في المجلد.")

# إنشاء الزر أو القائمة
class MemoryOptimizerOperator(bpy.types.Operator):
    bl_idname = "object.memore"
    bl_label = "Memory Optimizer"

    def execute(self, context):
        run_memory_optimizer(self, context)
        return {'FINISHED'}

class kh_orphans_purge(bpy.types.Operator):
    bl_idname = "object.orphans_purge"
    bl_label = "orphans_purger"

    def execute(self, context):
        deleted_count = bpy.ops.outliner.orphans_purge(do_recursive=True)
        self.report({'INFO'}, f"Purge: {deleted_count} ")
        return {'FINISHED'}
    

    
script_dir = os.path.dirname(os.path.abspath(__file__))
my_icons_dir = os.path.join(script_dir, "icons")
preview_collection = bpy.utils.previews.new()
preview_collection.load("a.png", os.path.join(my_icons_dir, "a.png"), 'IMAGE')

 # Memore
class MemorePanel(bpy.types.Panel):
    """Creates a panel in the 3D View Toolbar"""
    bl_label = "Render Settings"
    bl_idname = "OBJECT_PT_memore"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KH-Tools"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        # استخدام الدالة المساعدة للبحث عن إعدادات الإضافة
        return get_addon_preferences(context, 'Memory') == True

    def draw_header(self, context: bpy.types.Context):
        try:
            
            self.layout.label(
                text="", icon_value=preview_collection['a.png'].icon_id)
        except KeyError:
            pass


    
    def draw(self, context):
        scene = bpy.context.scene
        # initial variable calculation resolution
        perc_res_v = 100 / scene.render.resolution_percentage
        res_x = scene.render.resolution_x / perc_res_v
        res_y = scene.render.resolution_y / perc_res_v
        res_val = str(int(res_x)) + " x " + str(int(res_y))
    
        layout = self.layout
        box = layout.box()
        
        # Clean Up
        row = box.row(align=True)
        row.label(text="Clean Up" , icon='BRUSH_DATA')
        row = box.row()
        row.operator(MemoryOptimizerOperator.bl_idname , icon='SEQ_HISTOGRAM')
        row = box.row()
        #row.operator("outliner.orphans_purge" , text='Clean Up File' , icon='BRUSH_DATA')
        row.operator("object.orphans_purge" , text='Clear File' , icon='BRUSH_DATA')
        
        #row = box.row()
        row.operator("render.texture_limit_clamp_offf" , text='Clear Material' , icon='MATERIAL')
        row = box.row()
        row.operator("render.texture_limit_clamp_off" , text='Clear GPU' , icon='MEMORY')
        # row = box.row()
        # row.operator("wm.save_mainfile" , text='Save File' , icon='FILE_TICK')
        # row = box.row()
        row.operator("render.out_of_memory" , text='Out Memory' , icon='ERROR')

   
        # External data
        #box = layout.box()
        #row = box.row()
        #row.label(text="External Texture" , icon='FILEBROWSER')
        #row = box.row()
        #row.operator("file.unpack_all",text='Export Texture' , icon='FOLDER_REDIRECT')        
        #row = box.row()
        #row.operator("render.texture_limit_clamp_ff",text='Import Texture' , icon='PACKAGE')
        #row = box.row()

        # Quality Presets (moved before Device)
        box = layout.box()
        row = box.row()
        row.label(text="Quality Presets:", icon="SETTINGS")
        # Display current resolution
        row.label(text=res_val)
        row = box.row()
        row.operator("render.quality_low", text="Low", icon="MESH_CIRCLE")
        row.operator("render.quality_medium", text="Medium", icon="MESH_UVSPHERE")
        row = box.row()
        row.operator("render.quality_high", text="High", icon="MESH_ICOSPHERE")
        row.operator("render.quality_ultra", text="Ultra", icon="SHADING_RENDERED")

        # Resolution % in Quality section
        row = box.row()
        row.prop(context.scene.render, "resolution_percentage", text="Resolution %", toggle=True)

        # Device
        box = layout.box()
        row = box.row()
        row.label(text="Device:",icon= "SCENE")
        if context.scene.render.engine == 'CYCLES':
            # Device
            row.prop(context.scene.cycles, "use_adaptive_sampling", text="Adaptive")
            row = box.row()
            row.prop(context.scene.cycles, "device", expand=True)
            row = box.row()
            row.prop(context.scene.cycles, "samples")
            if context.scene.cycles.use_adaptive_sampling==True:
                row = box.row()
                row.prop(context.scene.cycles, "adaptive_threshold", text="Noise Threshold")
            row = box.row()
            row.operator("object.kh_caustics" , text='Caustics' , icon='ADD')
            row.operator("object.kh_delete_caustics" , text='Caustics' , icon='TRASH')
        else:
            row = box.row()
            row.label(text="Works with Cycles engine only.", icon="ERROR")

        # Light Paths (separate section)
        box = layout.box()
        row = box.row()
        row.label(text="Light Paths:", icon="LIGHT_SUN")
        if context.scene.render.engine == 'CYCLES':
            # Max Bounces (unified control)
            row = box.row()
            row.prop(context.scene, "max_bounces", text="Max Bounces (Unified)")

            # First row: Total and Diffuse
            row = box.row()
            row.prop(context.scene.cycles, "max_bounces", text="Total")
            row.prop(context.scene.cycles, "diffuse_bounces", text="Diffuse")

            # Second row: Glossy and Transparent
            row = box.row()
            row.prop(context.scene.cycles, "glossy_bounces", text="Glossy")
            row.prop(context.scene.cycles, "transparent_max_bounces", text="Transparent")

            # Third row: Transmission and Volume
            row = box.row()
            row.prop(context.scene.cycles, "transmission_bounces", text="Transmission")
            row.prop(context.scene.cycles, "volume_bounces", text="Volume")

            # Direct and Indirect Light
            row = box.row()
            row.prop(context.scene.cycles, "sample_clamp_direct", text="Direct Light")
            row.prop(context.scene.cycles, "sample_clamp_indirect", text="Indirect Light")
        else:
            row = box.row()
            row.label(text="Works with Cycles engine only.", icon="ERROR")

        if context.scene.render.engine == 'CYCLES':
            # GPU VRAM
            box = layout.box()
            row = box.row()
            row.label(text="GPU VRAM :" , icon='MEMORY')
            row = box.row()
            row.prop(context.scene.render, "use_simplify", text="Texture Limit",icon= "QUIT", toggle=True)
            if context.scene.render.use_simplify:
                row = box.row()
                row.label(text="Preview :")
                row.prop(context.preferences.system, "gl_texture_limit", text="")
                row = box.row()
                row.label(text="Real Time :")
                row.prop(context.scene.cycles, "texture_limit", text="")
                row = box.row()
                row.label(text="Render :")
                row.prop(context.scene.cycles, "texture_limit_render", text="")
            # Resolution
            box = layout.box()
            row = box.row()
            row.label(text="Resolution :", icon="RESTRICT_VIEW_ON")
            #row.scale_x = 1.8
            row.label(text=res_val)
            row = box.row()
            row.prop(context.scene.render, "resolution_x", text="X")
            row.prop(context.scene.render, "resolution_y", text="Y")

            box = layout.box()
            row = box.row()
            row.prop(context.scene.cycles, "use_auto_tile", text="Use Tile",icon= "QUIT", toggle=True)
            if context.scene.cycles.use_auto_tile:
                row = box.row()
                row.prop(context.scene.cycles, "tile_size", text="Tile Size")

            row = box.row()
            row.prop(context.scene.render, "use_persistent_data", text="Save Data", toggle=True)

        else:
            row = box.row()
            row.label(text="Works with Cycles engine only.", icon="ERROR")

            
 
        
        
#Export Texture      
class TEXTURE_LIMIT_CLAMPF(bpy.types.Operator):
    """Set the GL texture limit to CLAMP_OFF"""
    bl_idname = "render.texture_limit_clamp_ff"
    bl_label = "Clear GPU Memory"

    def execute(self, context):
        bpy.ops.file.pack_all()
        bpy.ops.file.autopack_toggle()
  
        return {'FINISHED'}

#Clear GPU memory       
class TEXTURE_LIMIT_CLAMP_OFF(bpy.types.Operator):
    """Set the GL texture limit to CLAMP_OFF"""
    bl_idname = "render.texture_limit_clamp_off"
    bl_label = "Clear GPU Memory"

    def execute(self, context):
        bpy.context.preferences.system.gl_texture_limit = 'CLAMP_OFF'
        bpy.context.preferences.system.gl_texture_limit = 'CLAMP_1024'
        

        return {'FINISHED'}
    
#Out of Memory      
class Out_of_Memory(bpy.types.Operator):
    """Set the GL texture limit to CLAMP_OFF"""
    bl_idname = "render.out_of_memory"
    bl_label = "Out of Memory"

    def execute(self, context):
        bpy.context.space_data.shading.type = 'SOLID'
        bpy.context.preferences.system.gl_texture_limit = 'CLAMP_OFF'
        bpy.context.preferences.system.gl_texture_limit = 'CLAMP_1024'
        bpy.ops.outliner.orphans_purge(do_recursive=True)
        bpy.context.scene.render.use_simplify = True
        bpy.context.scene.cycles.texture_limit = '1024'
        bpy.context.scene.cycles.texture_limit_render = '2048'
        
        
        return {'FINISHED'}

 

class MaterialSlot(bpy.types.Operator):
    """Set the GL texture limit to CLAMP_OFF"""
    bl_idname = "render.texture_limit_clamp_offf"
    bl_label = "Clear Material"

    def execute(self, context):
        if bpy.context.active_object:
            # التحقق من أن الكائن النشط في وضع العدل
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
                
        view_layer = bpy.context.view_layer
        mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and not obj.hide_viewport]

        for obj in mesh_objects:
            try:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.material_slot_remove_unused()
                obj.select_set(False)
            except RuntimeError as e:
                self.report({'WARNING'}, str(e))

        if not mesh_objects:
            self.report({'INFO'}, "No mesh objects in the scene")
             
        
        # Check if there are materials in the scene
        if bpy.data.materials:
            # Loop through all materials in the scene
            for mat in bpy.data.materials:
                # Check if the material is using nodes
                if mat.use_nodes:
                    # Create a list to store image texture nodes to be removed
                    image_nodes_to_remove = []
                    # Loop through the nodes of the material
                    for node in mat.node_tree.nodes:
                        # Check if the node is of type 'ShaderNodeTexImage'
                        if node.type == 'TEX_IMAGE':
                            # Check if the image texture node is not connected to any other node
                            if not node.outputs['Color'].links:
                                # Append the image texture node to the list
                                image_nodes_to_remove.append(node)
                    # Remove the image texture nodes from the material
                    for node_to_remove in image_nodes_to_remove:
                        mat.node_tree.nodes.remove(node_to_remove)
        else:
            # Handle the case where there are no materials in the scene
            pass  # You can add your logic here

        bpy.ops.outliner.orphans_purge(do_recursive=True)
        self.report({'INFO'}, "Unused materials and images have been deleted")
        return {'FINISHED'}
    
    
def update_render_settings(self, context):
    scene = context.scene

    # تحديث إعدادات الرندر بناءً على القيمة المدخلة

    scene.cycles.max_bounces = scene.max_bounces
    scene.cycles.diffuse_bounces = scene.max_bounces
    scene.cycles.glossy_bounces = scene.max_bounces
    scene.cycles.transmission_bounces = scene.max_bounces
    scene.cycles.volume_bounces = scene.max_bounces
    scene.cycles.transparent_max_bounces = scene.max_bounces

# سيتم تسجيل الخاصية في دالة register()


# OBJECT Display
class BoundsTypeOperator(bpy.types.Operator):
    bl_idname = "object.bounds_type"
    bl_label = "Set Low Display"
    bl_options = {"REGISTER", "UNDO"}

    bounds_type: bpy.props.EnumProperty(
        items=[
            ("BOX", "Box", ""),
            ("SPHERE", "Sphere", ""),
            ("CAPSULE", "Capsule", ""),
            ("CONE", "Cone", ""),
            ("CYLINDER", "Cylinder", ""),
        ],
        name="Bounds Type",
        default="BOX",
    )
    def execute(self, context):
        if bpy.context.active_object:
            # التحقق من أن الكائن النشط في وضع العدل
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        # Get the selected objects
        objects = context.selected_objects
        # Loop through each object
        for obj in objects:
            # Select the object and its linked data
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.select_linked(type='OBDATA')
            
            # Set the display type and bounds type
            obj.display_type = 'BOUNDS'
            obj.display_bounds_type = self.bounds_type
            
        return {"FINISHED"}

# Define the second operator
class TexturedDisplayOperator(bpy.types.Operator):
    bl_idname = "object.textured_display"
    bl_label = "Full Display"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if bpy.context.active_object:
            # التحقق من أن الكائن النشط في وضع العدل
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.select_linked(type='OBDATA')
                
                # Set the display type and bounds visibility
                obj.display_type = 'TEXTURED'
                obj.show_bounds = False
                obj.display_type = 'TEXTURED'
                obj.show_bounds = False
              
        return {"FINISHED"}


# High Poly
class MyAddonPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_my_addon"
    bl_label = "HIGH POLY"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'KH-Tools'
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id   = "OBJECT_PT_kh_asset"

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon='MESH_ICOSPHERE')
        except KeyError:
            pass
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.operator(HighPolyOperator.bl_idname, text="Select High Poly", icon = 'RESTRICT_SELECT_OFF')
        #row = box.row()
        #row.operator("object.cleanup_segmentation", text="Clean Up Selected", icon = 'BRUSH_DATA')
        box = layout.box()
        box.label(text="Hide Low Poly:")
        
        row = box.row()
        #row.prop(context.scene, "hide_viewport_modifiers")
        #row.prop(context.scene, "hide_render_modifiers", text="Hidden in Render")
        #row = box.row()
        row.prop(context.scene, "decimate_ratio", text="Low Poly Ratio")
        
        row = box.row()
        row.operator("myaddon.decimate", text="Add Low Poly", icon = 'ADD')
        row = box.row()
        row.operator("object.delete_modifier_operator", text="Delete", icon = 'TRASH')
        row = box.row()
        row.operator("object.decimate_modifier_operator", text="Apply", icon = 'CHECKMARK')
        
       


class HighPolyOperator(bpy.types.Operator):
    bl_idname = "object.high_poly"
    bl_label = "High Poly"

    triangle_count: bpy.props.IntProperty(
        name="Faces Count",
        default=500000,
        min=0,
        description="Minimum number of triangles to consider as high poly"
    )

    def execute(self, context):
        # iterate over all objects in the scene
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                # check if the mesh has more than the specified number of triangles
                if len(obj.data.polygons) > self.triangle_count:
                    obj.select_set(True)
                else:
                    obj.select_set(False)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        # تنظيف الذاكرة قبل فتح النافذة
        gc.collect()
        return wm.invoke_props_dialog(self)

    def check(self, context):
        # re-run the execute method when the operator properties are changed
        return True
    
class OBJECT_OT_cleanup_segmentation(bpy.types.Operator):
    bl_idname = "object.cleanup_segmentation"
    bl_label = "Clean Up Selected"
    bl_description = "Clean up segmentation for selected objects"

    def execute(self, context):
        if bpy.context.active_object:
            # التحقق من أن الكائن النشط في وضع العدل
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.tris_convert_to_quads()
                bpy.ops.mesh.tris_convert_to_quads(face_threshold=1.74533, shape_threshold=1.74533)
                bpy.ops.mesh.remove_doubles()
                bpy.ops.mesh.remove_doubles(threshold=0.0005)
                bpy.ops.object.editmode_toggle()
                bpy.ops.outliner.orphans_purge(do_recursive=True)

        return {'FINISHED'}



class MYADDON_OT_decimate(bpy.types.Operator):
    bl_idname = "myaddon.decimate"
    bl_label = "Add Decimate Modifier"
    bl_description = "Add Decimate Modifier with a given ratio to selected objects"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        if bpy.context.active_object:
            if bpy.context.active_object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
   
            objects = context.selected_objects
            ratio = context.scene.decimate_ratio
            for obj in objects:
                if obj.type=='MESH':
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.select_linked(type='OBDATA')
                    has_decimate = False
                    for mod in obj.modifiers:
                        if mod.type == 'DECIMATE':
                            mod.ratio = ratio
                            has_decimate = True
                            break

                    if not has_decimate:
                        mod = obj.modifiers.new("Decimate", 'DECIMATE')
                        mod.ratio = ratio

                    # Hide the modifier in the viewport if the option is enabled
                    mod.show_viewport = not context.scene.hide_viewport_modifiers

                    # Hide the modifier in the render if the option is enabled
                    mod.show_render = not context.scene.hide_render_modifiers

        return {'FINISHED'}

class DecimateModifierOperator(bpy.types.Operator):
    """Apply decimate modifier"""
    bl_idname = "object.decimate_modifier_operator"
    bl_label = "Apply "

    def execute(self, context):
        if bpy.context.active_object:
            bpy.ops.object.mode_set(mode='OBJECT')
            selected_objects = bpy.context.selected_objects
            decimate_modifier_name = "Decimate"
            for obj in selected_objects:
                if decimate_modifier_name in obj.modifiers:
                    modifier = obj.modifiers[decimate_modifier_name]
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.convert(target='MESH')
                    #bpy.ops.object.modifier_apply(modifier=decimate_modifier_name)
                
        return {'FINISHED'}


class DeleteModifierOperator(bpy.types.Operator):
    """Delete decimate modifier"""
    bl_idname = "object.delete_modifier_operator"
    bl_label = "Delete Decimate"
    
    def execute(self, context):
        for obj in context.selected_objects:
            if obj.modifiers.get("Decimate"):
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_remove(modifier="Decimate")
        return {'FINISHED'}
    



def add_button_to_toolbar():
    # get the current toolbar
    toolbar = bpy.context.workspace.tools.from_space_view3d_mode(bpy.context.mode).toolbar

#Caustics///////////////////////////////////////////////////////////////////////////////////////////////////////////// 
def kh_Caustics():  
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            obj.data.cycles.is_caustics_light = True

    if bpy.context.scene.world is not None:
        bpy.context.scene.world.cycles.is_caustics_light = True

    def has_glass_shader(material):
        if not material.use_nodes:
            return False
        for node in material.node_tree.nodes:
            if node.type == 'BSDF_GLASS':
                return True
        return False

    def has_transmission(material):
        if not material.use_nodes:
            return False
        for node in material.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED' and node.inputs[17].default_value != 0:
                return True
        return False

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for mat_slot in obj.material_slots:
                mat = mat_slot.material
                if mat and (has_glass_shader(mat) or has_transmission(mat)):
                    obj.cycles.is_caustics_caster = True
                    break
                
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for mat_slot in obj.material_slots:
                mat = mat_slot.material
                if mat and not has_glass_shader(mat):
                    if not has_transmission(mat):
                        obj.cycles.is_caustics_receiver = True
                        break
    

def kh_Delete_Caustics():  
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            obj.data.cycles.is_caustics_light = False

    if bpy.context.scene.world is not None:
        bpy.context.scene.world.cycles.is_caustics_light = False

    def has_glass_shader(material):
        if not material.use_nodes:
            return False
        for node in material.node_tree.nodes:
            if node.type == 'BSDF_GLASS':
                return True
        return False

    def has_transmission(material):
        if not material.use_nodes:
            return False
        for node in material.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED' and node.inputs[17].default_value != 0:
                return True
        return False

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for mat_slot in obj.material_slots:
                mat = mat_slot.material
                if mat and (has_glass_shader(mat) or has_transmission(mat)):
                    obj.cycles.is_caustics_caster = False
                    break
                
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for mat_slot in obj.material_slots:
                mat = mat_slot.material
                if mat and not has_glass_shader(mat):
                    if not has_transmission(mat):
                        obj.cycles.is_caustics_receiver = False
                        break
   
 

class kh_causticsOperator(bpy.types.Operator):
    """add Caustics"""
    bl_idname = "object.kh_caustics"
    bl_label = "Caustics"
    
    def execute(self, context):
        kh_Delete_Caustics()
        kh_Caustics()
        bpy.ops.render.texture_limit_clamp_offf()
        return {'FINISHED'}
    
class kh_delete_causticsOperator(bpy.types.Operator):
    """delete Caustics"""
    bl_idname = "object.kh_delete_caustics"
    bl_label = "Delete Caustics"

    def execute(self, context):
        kh_Delete_Caustics()
        bpy.ops.render.texture_limit_clamp_offf()
        return {'FINISHED'}

# Quality Preset Operators
class QualityLowOperator(bpy.types.Operator):
    """Set render quality to Low"""
    bl_idname = "render.quality_low"
    bl_label = "Low Quality"

    def execute(self, context):
        scene = context.scene

        # Set render engine to Cycles
        scene.render.engine = 'CYCLES'

        # Low quality settings
        scene.cycles.samples = 256

        # Light paths
        scene.cycles.max_bounces = 6
        scene.cycles.diffuse_bounces = 6
        scene.cycles.glossy_bounces = 6
        scene.cycles.transmission_bounces = 6
        scene.cycles.volume_bounces = 6
        scene.cycles.transparent_max_bounces = 6

        # Indirect light
        scene.cycles.sample_clamp_indirect = 8

        self.report({'INFO'}, "Low quality settings applied")
        return {'FINISHED'}

class QualityMediumOperator(bpy.types.Operator):
    """Set render quality to Medium"""
    bl_idname = "render.quality_medium"
    bl_label = "Medium Quality"

    def execute(self, context):
        scene = context.scene

        # Set render engine to Cycles
        scene.render.engine = 'CYCLES'

        # Medium quality settings
        scene.cycles.samples = 800

        # Light paths
        scene.cycles.max_bounces = 12
        scene.cycles.diffuse_bounces = 12
        scene.cycles.glossy_bounces = 12
        scene.cycles.transmission_bounces = 12
        scene.cycles.volume_bounces = 12
        scene.cycles.transparent_max_bounces = 12

        # Indirect light
        scene.cycles.sample_clamp_indirect = 10

        self.report({'INFO'}, "Medium quality settings applied")
        return {'FINISHED'}

class QualityHighOperator(bpy.types.Operator):
    """Set render quality to High"""
    bl_idname = "render.quality_high"
    bl_label = "High Quality"

    def execute(self, context):
        scene = context.scene

        # Set render engine to Cycles
        scene.render.engine = 'CYCLES'

        # High quality settings
        scene.cycles.samples = 1500

        # Light paths
        scene.cycles.max_bounces = 16
        scene.cycles.diffuse_bounces = 16
        scene.cycles.glossy_bounces = 16
        scene.cycles.transmission_bounces = 16
        scene.cycles.volume_bounces = 16
        scene.cycles.transparent_max_bounces = 16

        # Indirect light
        scene.cycles.sample_clamp_indirect = 15

        self.report({'INFO'}, "High quality settings applied")
        return {'FINISHED'}

class QualityUltraOperator(bpy.types.Operator):
    """Set render quality to Ultra"""
    bl_idname = "render.quality_ultra"
    bl_label = "Ultra Quality"

    def execute(self, context):
        scene = context.scene

        # Set render engine to Cycles
        scene.render.engine = 'CYCLES'

        # Ultra quality settings
        scene.cycles.samples = 2048

        # Light paths
        scene.cycles.max_bounces = 24
        scene.cycles.diffuse_bounces = 24
        scene.cycles.glossy_bounces = 24
        scene.cycles.transmission_bounces = 24
        scene.cycles.volume_bounces = 24
        scene.cycles.transparent_max_bounces = 24

        # Indirect light
        scene.cycles.sample_clamp_indirect = 20

        self.report({'INFO'}, "Ultra quality settings applied")
        return {'FINISHED'}
    

classes = (
            #MEMORY////////////////////////////////////////////////////////////////////////////
            MemoryOptimizerOperator,
            MemorePanel,
            MaterialSlot,
            TEXTURE_LIMIT_CLAMPF,
            kh_orphans_purge,
            #Object
            BoundsTypeOperator,
            TexturedDisplayOperator,
            # High Poly
            HighPolyOperator,
            OBJECT_OT_cleanup_segmentation,
            MyAddonPanel,
            DecimateModifierOperator,
            DeleteModifierOperator,
            MYADDON_OT_decimate,
            TEXTURE_LIMIT_CLAMP_OFF,
            Out_of_Memory,
            kh_causticsOperator,
            kh_delete_causticsOperator,
            # Quality Presets
            QualityLowOperator,
            QualityMediumOperator,
            QualityHighOperator,
            QualityUltraOperator,
                )

def register():
    for i in classes:
        register_class(i)

    # MEMORY////////////////////////////////////////////////////////////////////////////

    bpy.types.Scene.decimate_ratio = bpy.props.FloatProperty(
        name="Decimate Ratio",
        default=0.65,
        min=0,
        max=1,
        description="Ratio for the Decimate Modifier"
    )
    bpy.types.Scene.hide_viewport_modifiers = bpy.props.BoolProperty(
        name="H-Viewport",
        default=False,
        description="Hide all modifiers in the viewport"
    )
    bpy.types.Scene.hide_render_modifiers = bpy.props.BoolProperty(
        name="H-Render",
        default=False,
        description="Hide all modifiers in the render"
    )

    bpy.types.Scene.my_value = bpy.props.FloatProperty(
        name="",
        description="Value to set for input 20 of all Principled BSDF materials",
        default=1.0,
        min=0.0,
        max=1000
    )

    # تسجيل الخاصية لتحديث إعدادات الرندر
    bpy.types.Scene.max_bounces = bpy.props.IntProperty(
        name="Max Bounces",
        default=8,
        min=0,
        update=update_render_settings
    )
    #bpy.utils.previews.register(preview_collection)
        


def unregister():
    for i in classes:
        unregister_class(i)

    #MEMORY /////////////////////////////////////////////////////////////////////////////
    # التحقق من وجود الخصائص قبل حذفها لتجنب الأخطاء
    if hasattr(bpy.types.Scene, 'decimate_ratio'):
        del bpy.types.Scene.decimate_ratio
    if hasattr(bpy.types.Scene, 'hide_viewport_modifiers'):
        del bpy.types.Scene.hide_viewport_modifiers
    if hasattr(bpy.types.Scene, 'hide_render_modifiers'):
        del bpy.types.Scene.hide_render_modifiers
    if hasattr(bpy.types.Scene, 'my_value'):
        del bpy.types.Scene.my_value
    if hasattr(bpy.types.Scene, 'max_bounces'):
        del bpy.types.Scene.max_bounces


    #bpy.utils.previews.unregister(preview_collection)



if __name__ == "__main__":
    try:
        register()
    except:
        pass
    unregister() 
     
  
