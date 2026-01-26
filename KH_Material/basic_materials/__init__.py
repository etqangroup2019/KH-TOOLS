import bpy
from bpy.types import Panel
import os
bl_info = {
        "name": "KH-Basic materials",
    "author": "Khaled Alnwesary",
    "version": (1, 72),
    "blender": (4, 0, 0),
    "location": "View3D > UI",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "KH",
}

addon_dir = os.path.dirname(__file__)
my_icons_dir = os.path.join(addon_dir, "icons")

script_dir = os.path.dirname(os.path.realpath(__file__))
folder_path = os.path.join(script_dir, "asset")
file_name = "Basic materials.blend"
material_file_path = os.path.join(folder_path, file_name)

def material_users_1():
    if bpy.context.object:
        obj = bpy.context.object
        if obj.active_material:
            material = obj.active_material
            if material.users > 1:
                new_material = material.copy()
                obj.active_material = new_material
                
def material_add(name):
    material_name = name    
    if bpy.context.object is not None and bpy.context.object.type == 'MESH':
        active_object = bpy.context.object

        if material_name not in bpy.data.materials:

            with bpy.data.libraries.load(material_file_path, link=False) as (data_from, data_to):
                data_to.materials = [material_name]

        if material_name in bpy.data.materials:
            material = bpy.data.materials[material_name]

            if active_object.data.materials:
                active_object.data.materials[active_object.active_material_index] = material
            else:
                active_object.data.materials.append(material)
    bpy.context.view_layer.update()
    
#KHM-Glass
class KHM_GlassOperator(bpy.types.Operator):
    bl_idname = "object.khm_glass"
    bl_label = "Add Glass"
    bl_description = "Add a Glass"
    def execute(self, context):
        
        material_add("KHM-Glass")
        material_users_1()
        return {'FINISHED'}
    
    # Water
class KHM_Water_CausticsOperator(bpy.types.Operator):
    bl_idname = "object.khm_water_caustics"
    bl_label = "Add Water"
    bl_description = "Add a Water"
    def execute(self, context):  
            
        material_add("KHM-Water")
        material_users_1()
        return {'FINISHED'}
    
# metal
class KHM_MetalOperator(bpy.types.Operator):
    bl_idname = "object.khm_metal"
    bl_label = "Add metal"
    bl_description = "Add a metal"
    def execute(self, context):
        
        material_add("KHM-Metal")         
        material_users_1()
        return {'FINISHED'}
    
#KHM-Car paint
class KHM_Car_paintOperator(bpy.types.Operator):
    bl_idname = "object.khm_car_paint"
    bl_label = "Add Car paint"
    bl_description = "Add a Car paint"
    def execute(self, context):
        
        material_add("KHM-Car paint")        
        material_users_1()
        return {'FINISHED'}
    
    # KHM-Steel
class KHM_SteellOperator(bpy.types.Operator):
    bl_idname = "object.khm_steel"
    bl_label = "Add Steel"
    bl_description = "Add a Steel"
    def execute(self, context):
        
        material_add("KHM-Steel")  
        material_users_1()
        return {'FINISHED'}
    
    # KHM-Gold
class KHM_GoldOperator(bpy.types.Operator):
    bl_idname = "object.khm_gold"
    bl_label = "Add Gold"
    bl_description = "Add a Gold"
    def execute(self, context):
        
        material_add("KHM-Gold")  
        material_users_1()
        return {'FINISHED'}
    
    # KHM-Paint
class KHM_PaintOperator(bpy.types.Operator):
    bl_idname = "object.khm_paint"
    bl_label = "Add Paint"
    bl_description = "Add a Paint"
    def execute(self, context):

        material_add("KHM-Paint")  
        material_users_1()
        return {'FINISHED'}

    # KHM-Curtain
class KHM_CurtainOperator(bpy.types.Operator):
    bl_idname = "object.khm_curtain"
    bl_label = "Add Curtain"
    bl_description = "Add a Curtain"
    def execute(self, context):
        
        material_add("KHM-Curtain")           
        material_users_1()
        return {'FINISHED'}
    
    # KHM-Plastic
class KHM_PlasticOperator(bpy.types.Operator):
    bl_idname = "object.khm_plastic"
    bl_label = "Add Plastic"
    bl_description = "Add a Plastic"
    def execute(self, context):
        
        material_add("KHM-Plastic")  
        material_users_1()
        return {'FINISHED'}
    
    # LED: KHM-LED
class KHM_LEDOperator(bpy.types.Operator):
    bl_idname = "object.khm_led"
    bl_label = "Add LED"
    bl_description = "Add a LED"
    def execute(self, context):
        material_add("LED: KHM-LED")  
        material_users_1()
        return {'FINISHED'}
    
    # KHM-Ground
class KHM_GroundOperator(bpy.types.Operator):
    bl_idname = "object.khm_ground"
    bl_label = "Add Ground"
    bl_description = "Add a Ground"
    def execute(self, context):
        material_add("KHM-Ground")  
        material_users_1()
        return {'FINISHED'}

# KHM-Wood
class KHM_WoodOperator(bpy.types.Operator):
    bl_idname = "object.khm_wood"
    bl_label = "Add Wood"
    bl_description = "Add a Wood"
    def execute(self, context):
        
        material_add("KHM-Wood")  
        material_users_1()
        return {'FINISHED'}

# KHM-Concrete
class KHM_ConcreteOperator(bpy.types.Operator):
    bl_idname = "object.khm_concrete"
    bl_label = "Add Concrete"
    bl_description = "Add a Concrete"
    def execute(self, context):
        
        material_add("KHM-Concrete")  
        material_users_1()
        return {'FINISHED'}

#KHM-Marble
class KHM_MarbleOperator(bpy.types.Operator):
    bl_idname = "object.khm_marble"
    bl_label = "Add Marble"
    bl_description = "Add a Marble"
    def execute(self, context):
        
        material_add("KHM-Marble")  
        material_users_1()
        return {'FINISHED'}

# KHM-Fabric
class KHM_FabricOperator(bpy.types.Operator):
    bl_idname = "object.khm_fabric"
    bl_label = "Add Fabric"
    bl_description = "Add a Fabric"
    def execute(self, context):

        material_add("KHM-Fabric")
        material_users_1()
        return {'FINISHED'}

# مادة بول مسبح بلاط
class KHM_PoolTileOperator(bpy.types.Operator):
    bl_idname = "object.khm_pool_tile"
    bl_label = "Add Pool Tile"
    bl_description = "Add a Pool Tile material"
    def execute(self, context):

        material_add("KHM-Pool Tile")
        material_users_1()
        return {'FINISHED'}

# مادة الأسفلت
class KHM_AsphaltOperator(bpy.types.Operator):
    bl_idname = "object.khm_asphalt"
    bl_label = "Add Asphalt"
    bl_description = "Add an Asphalt material"
    def execute(self, context):

        material_add("KHM-Asphalt")
        material_users_1()
        return {'FINISHED'}
    
       
#Glass Thickness
class ThicknessGlassCurtainsOperator(bpy.types.Operator):
    bl_idname = "object.thickness_glass_curtains"
    bl_label = "Thickness"
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            solidify_modifier = next((m for m in obj.modifiers if m.type == 'SOLIDIFY'), None)
            if solidify_modifier:
                obj.modifiers.remove(solidify_modifier)
            else:
                solidify_modifier = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
                solidify_modifier.thickness = 0.003  
                
        return {'FINISHED'}   
    

# Basic materials///////////////////////////////////////////////////////////////////////////////////////////////////////////////
preview_collection3 = bpy.utils.previews.new()
preview_collection3.load("books.png", os.path.join(my_icons_dir, "books.png"), 'IMAGE')
class kh_Basic_materials_ControlsPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_idname = "OBJECT_PT_Basic_materials"
    bl_region_type = "UI"
    bl_category = "KH-Tools"
    bl_label = "Basic Material"
    bl_options = {'DEFAULT_CLOSED'}
    #bl_parent_id   = "OBJECT_PT_tools_material"
    @classmethod
    def poll(cls, context):
        # البحث عن الإضافة في المسارات المختلفة
        try:
            KH = context.preferences.addons['KH-Tools'].preferences.KH_Material == True
        except KeyError:
            try:
                KH = context.preferences.addons['kh_tools'].preferences.KH_Material == True
            except KeyError:
                try:
                    KH = False
                    for addon_name in context.preferences.addons.keys():
                        if 'kh' in addon_name.lower() or 'tools' in addon_name.lower():
                            addon = context.preferences.addons[addon_name]
                            if hasattr(addon.preferences, 'KH_Material'):
                                KH = addon.preferences.KH_Material == True
                                break
                except:
                    KH = True
        return KH
    
    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon_value=preview_collection3['books.png'].icon_id)
        except KeyError:
            pass
  
    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj is not None and obj.type == 'MESH':
            material = obj.active_material
            mat = obj.active_material
            # if mat is not None and mat.node_tree is not None:
            #     if material.use_nodes and material.node_tree:
            #         coloring_found = False
            #         box = layout.box()
            #         for node in material.node_tree.nodes:
            #             if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Coloring"):
            #                 coloring_found = True
            #                 row = box.row()
            #                 row.operator("object.coloring_delete_node", text="Coloring", icon='TRASH')
            #                 row = box.row()
            #                 row.prop(node.inputs[1], "default_value", text="Color", icon='COLORSET_04_VEC')
            #                 row = box.row()
            #                 row.prop(node.inputs[2], "default_value", text="Saturation")
            #                 row = box.row()
            #                 row.prop(node.inputs[3], "default_value", text="Strength")
            #                 row = box.row()
            #                 row.prop(node.inputs[4], "default_value", text="Brightness")
            #                 break  

            #         if not coloring_found:
            box = layout.box()
            row = box.row()
            row.operator("object.khm_glass", text="Glass")
            row.operator("object.khm_water_caustics", text="Water")
            row = box.row()
            row.operator("object.khm_metal", text="Metal")
            row.operator("object.khm_car_paint", text="Car paint")
            row = box.row()
            row.operator("object.khm_steel", text="Steel")
            row.operator("object.khm_gold", text="Gold")
            row = box.row()
            row.operator("object.khm_paint", text="Paint")
            row.operator("object.khm_concrete", text="Concrete")
            row = box.row()
            row.operator("object.khm_plastic", text="Plastic")
            row.operator("object.khm_led", text="LED")
            row = box.row()
            row.operator("object.khm_wood", text="Wood")
            row.operator("object.khm_marble", text="Marble")
            row = box.row()
            row.operator("object.khm_fabric", text="Fabric")
            row.operator("object.khm_curtain", text="Curtain")
            row = box.row()
            row.operator("object.khm_ground", text="Ground")
            row.operator("object.khm_pool_tile", text="Pool Tile")
            row = box.row()
            row.operator("object.khm_asphalt", text="Asphalt")
            #row.operator("object.thickness_glass_curtains", text="Thickness")
            
            # التحقق من وجود موديفاير SOLIDIFY
            if any(mod.type == 'SOLIDIFY' for mod in obj.modifiers):
                row.operator("object.thickness_glass_curtains", text="Thickness", icon='TRASH')
            else:
                row.operator("object.thickness_glass_curtains", text="Thickness")
                     
        else:
            box = layout.box()
            row = box.row()
            row.label(text="There is no Object.", icon='ERROR') 


#الخصائص
class MATERIAL_PT_active_properties_submenu(bpy.types.Panel):
    """Submenu to display the active material properties of the selected object."""
    bl_label = ""
    bl_idname = "MATERIAL_PT_active_properties_submenu"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KH-Tools"
    bl_parent_id = "OBJECT_PT_Basic_materials"  # ربط بقائمة Basic Material
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        """التحقق من وجود كائن محدد من نوع MESH مع مادة نشطة"""
        obj = context.object
        return (obj is not None and 
                obj.type == 'MESH' and 
                obj.active_material is not None)

    def draw_header(self, context):
        obj = context.object
        material = obj.active_material
        """رسم رأس القائمة"""
        self.layout.label(text=f"{material.name}", icon='MATERIAL')

    def draw(self, context):
        """رسم محتوى القائمة"""
        layout = self.layout
        obj = context.object
        material = obj.active_material
        
        # عرض معلومات المادة
        # info_box = layout.box()
        # info_box.label(text=f"Material: {material.name}", icon='MATERIAL')
        
        if material.use_nodes:
            nodes = material.node_tree.nodes
            
            # البحث عن عقدة Principled BSDF
            principled_node = None
            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    principled_node = node
                    break
            
            if principled_node:
                # عرض الخصائص الأساسية لـ Principled BSDF
                self.draw_principled_properties(layout, principled_node)
            
            # البحث عن العقد المجمعة
            group_nodes = [node for node in nodes if node.type == 'GROUP']
            if group_nodes:
                self.draw_group_nodes_properties(layout, group_nodes)
            
            # إذا لم توجد عقد مفيدة
            if not principled_node and not group_nodes:
                box = layout.box()
                box.label(text="No controllable nodes found", icon='INFO')

        else:
            # المادة لا تستخدم العقد
            box = layout.box()
            box.label(text="Material doesn't use nodes", icon='INFO')
            row = box.row()
            row.operator("material.enable_nodes", text="Enable Nodes", icon='NODETREE')

    def draw_principled_properties(self, layout, principled_node):
        """رسم خصائص عقدة Principled BSDF"""
        box = layout.box()
        box.label(text="Principled BSDF", icon='MATERIAL_DATA')

        # عرض جميع المدخلات المتاحة كما هي في المادة
        for input_socket in principled_node.inputs:
            if hasattr(input_socket, 'default_value'):
                row = box.row()

                if input_socket.is_linked:
                    # التحقق من العقد الخاصة (Normal و Tangent)
                    if input_socket.name in ['Normal', 'Tangent']:
                        # عرض إعدادات العقدة المتصلة
                        connected_node = input_socket.links[0].from_node
                        self.draw_connected_node_properties(layout, connected_node, input_socket.name)
                    else:
                        # إذا كان المدخل متصل بعقدة أخرى
                        row.label(text=f"{input_socket.name}: Connected", icon='LINKED')
                else:
                    # إذا كان المدخل غير متصل، اعرض التحكم باسمه الأصلي
                    row.prop(input_socket, "default_value", text=input_socket.name)

    def draw_connected_node_properties(self, layout, connected_node, socket_name):
        """رسم خصائص العقدة المتصلة بـ Normal أو Tangent"""
        box = layout.box()
        box.label(text=f"{socket_name} Node: {connected_node.name}", icon='NODE')

        # عرض مدخلات العقدة المتصلة القابلة للتعديل
        editable_inputs = []
        for inp in connected_node.inputs:
            if hasattr(inp, 'default_value') and not inp.is_linked:
                editable_inputs.append(inp)

        if editable_inputs:
            for input_socket in editable_inputs:
                row = box.row()
                row.prop(input_socket, "default_value", text=input_socket.name)
        else:
            row = box.row()
            row.label(text="All inputs connected", icon='LINKED')

    def draw_group_nodes_properties(self, layout, group_nodes):
        """رسم خصائص العقد المجمعة"""
        for group_node in group_nodes:
            box = layout.box()
            box.label(text=f"Group Node: {group_node.name}", icon='NODETREE')

            # عرض مدخلات العقدة المجمعة القابلة للتعديل
            editable_inputs = [inp for inp in group_node.inputs
                             if not inp.is_linked and hasattr(inp, 'default_value')]

            if editable_inputs:
                for input_socket in editable_inputs:
                    row = box.row()
                    # عرض الاسم الأصلي للمدخل كما هو في المادة
                    row.prop(input_socket, "default_value", text=input_socket.name)
            else:
                row = box.row()
                row.label(text="All inputs connected", icon='LINKED')




class MATERIAL_OT_enable_nodes(bpy.types.Operator):
    """Enable nodes in active material"""
    bl_idname = "material.enable_nodes"
    bl_label = "Enable Nodes"
    bl_description = "Enable node system in active material"

    def execute(self, context):
        obj = context.object
        if obj and obj.active_material:
            obj.active_material.use_nodes = True
            self.report({'INFO'}, "Nodes enabled in material")
        else:
            self.report({'ERROR'}, "No active material")
        return {'FINISHED'}


            