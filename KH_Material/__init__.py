import bpy
from bpy.types import Panel
from bpy.utils import register_class, unregister_class
import os
from .import_maps import *
from .basic_materials import *

bl_info = {
        "name": "KH-Material",
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

# Color
class Add_Color_Operator(bpy.types.Operator):
    bl_idname = "object.add_mix_node"
    bl_label = "Add Mix Node to Image Texture"
    bl_description = "Add a mix node between Image Texture and BSDF Input Color"

    def execute(self, context):
        obj = bpy.context.active_object
        if obj and obj.active_material and obj.active_material.use_nodes:
            material = obj.active_material
            node_tree = material.node_tree
            nodes = node_tree.nodes
            bsdf_principled = None
            base_color_node = None
            coloring_group_exists = False
            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    bsdf_principled = node
                    color_input = node.inputs.get("Base Color")
                    if color_input and color_input.is_linked:
                        base_color_node = color_input.links[0].from_node
                    break
            for node in nodes:
                if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Coloring"):
                    coloring_group_exists = True
                    break

            if bsdf_principled and base_color_node and not coloring_group_exists :
                script_dir = os.path.dirname(os.path.realpath(__file__))
                folder_path = os.path.join(script_dir, "asset")
                file_name = "nods.blend"
                blend_file_path = os.path.join(folder_path, file_name)
                
                if not "KH-Coloring" in bpy.data.node_groups:
                    with bpy.data.libraries.load(blend_file_path) as (data_from, data_to):
                        data_to.node_groups = [name for name in data_from.node_groups if name.startswith("KH-Coloring")]

                if "KH-Coloring" in bpy.data.node_groups:
                    active_material = bpy.context.object.active_material
                    if active_material is not None:
                        coloring_group = False
                        for node in active_material.node_tree.nodes:
                            if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Coloring"):
                                group = node
                                coloring_group = True
                                break

                        if not coloring_group:
                            if "KH-Coloring" not in active_material.node_tree.nodes:
                                node_group = active_material.node_tree.nodes.new('ShaderNodeGroup')
                                node_group.node_tree = bpy.data.node_groups["KH-Coloring"]
                                node_group.location = (0, 500)
                                try:
                                    principled_node = active_material.node_tree.nodes.get("Principled BSDF")
                                    if principled_node is not None and principled_node.inputs[0].links:
                                        connected_node = principled_node.inputs[0].links[0].from_node
                                        if connected_node.type == 'MIX':
                                            active_material.node_tree.links.new(connected_node.outputs[2], node_group.inputs[0])
                                        else:
                                            active_material.node_tree.links.new(connected_node.outputs[0], node_group.inputs[0])
                                        active_material.node_tree.links.new(node_group.outputs[0], principled_node.inputs[0])
                                    else:
                                        principled_node_001 = active_material.node_tree.nodes.get("Principled BSDF.001")
                                        if principled_node_001 is not None and principled_node_001.inputs[0].links:
                                            connected_node = principled_node_001.inputs[0].links[0].from_node
                                            if connected_node.type == 'MIX':
                                                active_material.node_tree.links.new(connected_node.outputs[2], node_group.inputs[0])
                                            else:
                                                active_material.node_tree.links.new(connected_node.outputs[0], node_group.inputs[0])
                                            active_material.node_tree.links.new(node_group.outputs[0], principled_node_001.inputs[0])
                                except KeyError:
                                    print("Principled BSDF node not found in the material.")
                
        return {'FINISHED'}
    
    
class Delete_Coloring_Operator(bpy.types.Operator):
    bl_idname = "object.coloring_delete_node"
    bl_label = "Delete Coloring"
    bl_description = "Delete Coloring"

    def execute(self, context):
      obj = bpy.context.active_object
      if obj and obj.active_material and obj.active_material.use_nodes:
        material = obj.active_material
        node_tree = material.node_tree
        nodes = node_tree.nodes
        for node in nodes:
            connected_node = None
            bsdf_principled_node = None
            if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Coloring"):
                for input_node in node.inputs:
                    if input_node.name == "Color" and input_node.is_linked:
                        connected_node = input_node.links[0].from_node
                        break
            if connected_node:
                for node in nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        bsdf_principled_node = node
                        break
                if bsdf_principled_node:
                    node_tree.links.new(bsdf_principled_node.inputs["Base Color"],connected_node.outputs[0])
                    color_input = input_node.links[0].from_node
                    linked_node = color_input
                    if linked_node.type == 'MIX':
                        node_tree.links.new(bsdf_principled_node.inputs["Base Color"],connected_node.outputs[2])
        for node in nodes:
            if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Coloring"):
                nodes.remove(node)
                break

        return {'FINISHED'}
    
class Add_bump_node_Operator(bpy.types.Operator):
    bl_idname = "object.add_bump"
    bl_label = "Add bump Node to Image Texture"
    bl_description = "Add a bump node between Image Texture and BSDF Input Color"
    
    def execute(self, context):
        material = bpy.context.object.active_material
        if material:
            nodes = material.node_tree.nodes
            principled_bsdf = nodes.get("Principled BSDF")
            
            if principled_bsdf:
                connected_node = None
                for node in nodes:
                    if node.type == 'TEX_IMAGE':
                        for link in principled_bsdf.inputs[5].links:
                            if link.to_node == principled_bsdf and link.from_node == node:
                                connected_node = node
                                break
                        if connected_node:
                            break
                
                if connected_node:
                    image_name = connected_node.image.name
                    if "norm" not in image_name.lower():
                        bump_node = nodes.new(type='ShaderNodeBump')
                        bump_node.location= (-150,-300)
                        bump_node.inputs[0].default_value = 0.2
                        bump_node.inputs[1].default_value = 0.5
                        material.node_tree.links.new(connected_node.outputs[0], bump_node.inputs["Height"])
                        material.node_tree.links.new(bump_node.outputs[0], principled_bsdf.inputs["Normal"])
                        connected_node.image.colorspace_settings.name = 'Non-Color'
                
        return {'FINISHED'}

class NORMAL_MAPOperator(bpy.types.Operator):
    bl_idname = "object.normal_map"
    bl_label = "Add NORMAL MAP to Image Texture"
    bl_description = "Add a NORMAL MAP between Image Texture and BSDF Input Color"
    
    def execute(self, context):
        material = bpy.context.object.active_material
        if material:
            nodes = material.node_tree.nodes
            principled_bsdf = nodes.get("Principled BSDF")
            
            if principled_bsdf:
                connected_node = None
                for node in nodes:
                    if node.type == 'TEX_IMAGE':
                        for link in principled_bsdf.inputs[5].links:
                            if link.to_node == principled_bsdf and link.from_node == node:
                                connected_node = node
                                break
                        if connected_node:
                            break
                
                if connected_node:
                    bump_node = nodes.new(type='ShaderNodeNormalMap')
                    bump_node.inputs[0].default_value = 1
                    bump_node.location= (-150,-150)
                    material.node_tree.links.new(connected_node.outputs[0], bump_node.inputs[1])
                    material.node_tree.links.new(bump_node.outputs[0], principled_bsdf.inputs[5])
                    connected_node.image.colorspace_settings.name = 'Non-Color'
                
        return {'FINISHED'}

def kh_add_MAPPING():
    active_material = bpy.context.active_object.active_material
    has_tex_image_node = False
    for node in active_material.node_tree.nodes:
        if node.type == 'TEX_IMAGE':
            has_tex_image_node = True
            break
    has_mapping_node = False
    for node in active_material.node_tree.nodes:
        if node.type == 'MAPPING':
            has_mapping_node = True
            break
    if has_tex_image_node and not has_mapping_node:

        mapping_node = active_material.node_tree.nodes.new(type='ShaderNodeMapping')
        texture_coord_node = active_material.node_tree.nodes.new(type='ShaderNodeTexCoord')
        mapping_node.location = (-800, 200)
        texture_coord_node.location = (-1000, 200)
        for node in active_material.node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                active_material.node_tree.links.new(node.inputs['Vector'], mapping_node.outputs['Vector'])
        active_material.node_tree.links.new(texture_coord_node.outputs['UV'], mapping_node.inputs['Vector'])
    
class kh_add_MAPPING_Operator(bpy.types.Operator):
    bl_idname = "object.kh_mapping"
    bl_label = "Add mapping to Image Texture"
    bl_description = "Add a mapping to Image Texture"
    
    def execute(self, context):
        kh_add_MAPPING()  
        return {'FINISHED'}
    
    
# BEVEL///////////////////////////////////////////////////////////////////////////////////////////////////////////////  

def check_BEVEL_node():
    if bpy.context.object is None:
        return False
    if bpy.context.object.active_material is None:
        return False
    for node in bpy.context.object.active_material.node_tree.nodes:
        if node.type == 'BEVEL':
            return True
    return False

# def add_noise_texture():
#     if bpy.context.object is None:
#         return
#     if bpy.context.object.active_material is None:
#         return
#     material = bpy.context.object.active_material
#     noise_texture = material.node_tree.nodes.new('ShaderNodeBevel')
#     noise_texture.location = (-200, -100)
#     principled_node = None
#     connected_node = None
#     for node in material.node_tree.nodes:
#         if node.type == 'BSDF_PRINCIPLED':
#             principled_node = node
#             break
#     if principled_node is not None:
#         for link in bpy.context.object.active_material.node_tree.links:
#             if link.to_node == principled_node and link.to_socket.name == 'Normal':
#                 connected_node = link.from_node
#                 break
#         if connected_node is not None:
#             material.node_tree.links.new(noise_texture.inputs[1], connected_node.outputs[0])
#             material.node_tree.links.new(noise_texture.outputs[0], principled_node.inputs['Normal'])
#         else:
#             material.node_tree.links.new(noise_texture.outputs[0], principled_node.inputs['Normal'])
            
def add_BevelNode():
    obj = bpy.context.active_object
    if obj and obj.active_material and obj.active_material.use_nodes:
        material = obj.active_material
        node_tree = material.node_tree
        nodes = node_tree.nodes
        node_types = ['BSDF_PRINCIPLED', 'BSDF_DIFFUSE', 'BSDF_GLASS', 'BSDF_GLOSSY', 'BSDF_TRANSLUCENT', 'SUBSURFACE_SCATTERING']
        condition_node_types = ['NORMAL_MAP', 'BUMP', 'NORMAL']
        existing_bevel_node = next((node for node in nodes if node.name == 'BEVEL'), None)
        
        if not existing_bevel_node:
            condition_nodes_exist = any(node for node in nodes if node.type in condition_node_types)
            target_nodes = [node for node in nodes if node.type in node_types]
            for target_node in target_nodes:

                if condition_nodes_exist:
                    bevel_node = nodes.new(type='ShaderNodeBevel')
                    bevel_node.name = 'BEVEL'
                    bevel_node.samples = 6
                    bevel_node.inputs['Radius'].default_value = 0.02  

                normal_input = target_node.inputs.get('Normal')
                if normal_input and normal_input.is_linked:
                    # Disconnect the connected node
                    connected_node = normal_input.links[0].from_node
                    node_tree.links.remove(normal_input.links[0])
                    
                    node_tree.links.new(connected_node.outputs['Normal'], bevel_node.inputs['Normal'])
                    
                    node_tree.links.new(bevel_node.outputs['Normal'], normal_input)
                else:
                    # If condition nodes do not exist, create a single Bevel node for all target nodes
                    if not condition_nodes_exist and 'bevel_node' not in locals():
                        bevel_node = nodes.new(type='ShaderNodeBevel')
                        bevel_node.name = 'BEVEL'
                        bevel_node.samples = 6
                        bevel_node.inputs['Radius'].default_value = 0.02  # Use default_value instead of width
                    
                    node_tree.links.new(bevel_node.outputs['Normal'], target_node.inputs['Normal'])
    
def delete_BevelNode(): 
    obj = bpy.context.active_object
    if obj and obj.active_material and obj.active_material.use_nodes:
        material = obj.active_material
        node_tree = material.node_tree
        nodes = node_tree.nodes 
        node_types = ['BSDF_PRINCIPLED', 'BSDF_DIFFUSE', 'BSDF_GLASS', 'BSDF_GLOSSY', 'BSDF_TRANSLUCENT', 'SUBSURFACE_SCATTERING']
        condition_node_types = ['NORMAL_MAP', 'BUMP', 'NORMAL']

        condition_nodes_exist = any(node for node in nodes if node.type in condition_node_types)
        target_nodes = [node for node in nodes if node.type in node_types]
        for target_node in target_nodes:
            if condition_nodes_exist:
                active_material = bpy.context.active_object.active_material
                if active_material is not None:
                    for node in active_material.node_tree.nodes:
                        if node.type == 'BEVEL':
                            for link in active_material.node_tree.links:
                                if link.to_node == node and link.to_socket.name == 'Normal':
                                    shading_node = active_material.node_tree.nodes.get(target_node.name)
                                    if shading_node is not None:
                                        new_link = active_material.node_tree.links.new(shading_node.inputs['Normal'], link.from_socket)
                                        break
                                    
        active_material = bpy.context.active_object.active_material
        for node in active_material.node_tree.nodes:
            if node.type == 'BEVEL':
                active_material.node_tree.nodes.remove(node)


class Bevel_Operator(bpy.types.Operator):
    bl_idname = "object.kh_bevel"
    bl_label = "Add Bevel to Image Texture"
    bl_description = "Add a Bevel between Image Texture and BSDF Input Color"
    
    def execute(self, context):
        if not check_BEVEL_node():   
            add_BevelNode()
        else: 
            delete_BevelNode()                          
        return {'FINISHED'}

class RAMP_MAPOperator(bpy.types.Operator):
    bl_idname = "object.ramp_map"
    bl_label = "Add Color Ramp to Image Texture"
    bl_description = "Add a Color Ramp between Image Texture and BSDF Input Color"
    
    def execute(self, context):
        material = bpy.context.object.active_material
        if material:
            nodes = material.node_tree.nodes
            principled_bsdf = nodes.get("Principled BSDF")
            
            if principled_bsdf:
                connected_node = None
                for node in nodes:
                    if node.type == 'TEX_IMAGE':
                        for link in principled_bsdf.inputs[2].links:
                            if link.to_node == principled_bsdf and link.from_node == node:
                                connected_node = node
                                break
                        if connected_node:
                            break
                
                if connected_node:
                    bump_node = nodes.new(type='ShaderNodeValToRGB')
                    bump_node.location= (-250, 150)
                    material.node_tree.links.new(connected_node.outputs[0], bump_node.inputs[0])
                    material.node_tree.links.new(bump_node.outputs[0], principled_bsdf.inputs[2])
                    connected_node.image.colorspace_settings.name = 'Non-Color'
                
        return {'FINISHED'}

class Invert_MAPOperator(bpy.types.Operator):
    bl_idname = "object.invert_map"
    bl_label = "Add Invert to Image Texture"
    bl_description = "Add a Invert between Image Texture and BSDF Input Color"
    
    def execute(self, context):
        material = bpy.context.object.active_material
        if material:
            nodes = material.node_tree.nodes
            principled_bsdf = nodes.get("Principled BSDF")
            
            if principled_bsdf:
                connected_node = None
                for node in nodes:
                    if node.type == 'TEX_IMAGE':
                        for link in principled_bsdf.inputs[2].links:
                            if link.to_node == principled_bsdf and link.from_node == node:
                                connected_node = node
                                break
                        if connected_node:
                            break
                if connected_node:
                    bump_node = nodes.new(type='ShaderNodeInvert')
                    bump_node.inputs[0].default_value = 1
                    bump_node.location= (-150, 250)
                    material.node_tree.links.new(connected_node.outputs[0], bump_node.inputs[1])
                    material.node_tree.links.new(bump_node.outputs[0], principled_bsdf.inputs[2])
                    connected_node.image.colorspace_settings.name = 'Non-Color'
                
        return {'FINISHED'}


#bumpBUMP/Roughness
class AddBumpRoughnessOperator(bpy.types.Operator):
    bl_idname = "object.add_bump_roughness_operator"
    bl_label = "Add Bump/Roughness"
    bl_description = "Add description here"
    
    def execute(self, context):
        obj = bpy.context.active_object
        mat_slot = obj.material_slots[obj.active_material_index]
        if mat_slot:
            material = mat_slot.material
            node_tree = material.node_tree
            nodes = node_tree.nodes
            links = material.node_tree.links
            nodes = material.node_tree.nodes
            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    color_input = node.inputs.get("Base Color")
                    if color_input and color_input.is_linked:
                        linked_node = color_input.links[0].from_node
                        # Add Color Ramp and Bump nodes
                        color_ramp_1 = nodes.new(type="ShaderNodeValToRGB")
                        color_ramp_1.name = "Color Ramp I"
                        color_ramp_1.location = (-300, 0)
                        bump = nodes.new(type="ShaderNodeBump")
                        bump.name = "Bump"
                        bump.location = (-300, -300)
                        invert = nodes.new(type="ShaderNodeInvert")
                        invert.name = "Invert"
                        invert.location = (-750, -350)
                        
                        invert1 = nodes.new(type="ShaderNodeInvert")
                        invert1.name = "Invert"
                        invert1.location = (-500, -0)
                        
                        # Add second Color Ramp and connect to Bump node
                        color_ramp_2 = nodes.new(type="ShaderNodeValToRGB")
                        color_ramp_2.name = "Color Ramp II"
                        color_ramp_2.location = (-600, -300)
                        color_ramp_1_out = color_ramp_1.outputs["Color"]
                        bsdf_input = nodes["Principled BSDF"].inputs['Roughness']                    
                        bump_input = bump.inputs["Height"]
                        color_ramp_2_out = color_ramp_2.outputs["Color"]
                        bump_out = bump.outputs["Normal"]
                        bsdf_normal_input = nodes["Principled BSDF"].inputs["Normal"]

                        links.new(color_ramp_2_out, bump_input)
                        links.new(invert.outputs["Color"], color_ramp_2.inputs["Fac"])
                        links.new(invert1.outputs["Color"], color_ramp_1.inputs["Fac"])
                        
                        bump.inputs[0].default_value = 0.2
                        bump.inputs[1].default_value = 0.5
                        
                        links.new(linked_node.outputs[0], invert1.inputs["Color"])
                        links.new(linked_node.outputs[0], invert.inputs["Color"])
                        links.new(bump_out, bsdf_normal_input)
                        links.new(color_ramp_1_out, bsdf_input)
                        obj = bpy.context.active_object
                        mat_slot = obj.material_slots[obj.active_material_index]

                        if (mat_slot):
                            material = mat_slot.material
                            node_tree = material.node_tree
                            nodes = node_tree.nodes
                            links = material.node_tree.links                            
                            for node in nodes:
                                if node.type == 'BSDF_PRINCIPLED':
                                    color_input = node.inputs.get("Base Color")
                                    if color_input.is_linked:
                                        linked_node = color_input.links[0].from_node
                                        if linked_node.type == 'MIX':
                                            linked_node = color_input.links[0].from_node       
                                            material.node_tree.links.new(linked_node.outputs[2], invert1.inputs["Color"])
                                            material.node_tree.links.new(linked_node.outputs[2], invert.inputs["Color"])
                                            break  
 
        return {'FINISHED'}

# AmbientOcclusion Operator
class AmbientNodeOperator(bpy.types.Operator):
    bl_idname = "object.add_ambient_node"
    bl_label = "Add Ambient to Image Texture"
    bl_description = "Add a mix node between Image Texture and BSDF Input Color"

    def execute(self, context):           
        obj = bpy.context.active_object
        if obj and obj.active_material and obj.active_material.use_nodes:
            material = obj.active_material
            node_tree = material.node_tree
            nodes = node_tree.nodes
            bsdf_principled = None
            base_color_node = None
            coloring_group_exists = False
            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    bsdf_principled = node
                    color_input = node.inputs.get("Base Color")
                    if color_input and color_input.is_linked:
                        base_color_node = color_input.links[0].from_node
                    break
            for node in nodes:
                if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Ambient Occlusion"):
                    coloring_group_exists = True
                    break

            if bsdf_principled and base_color_node and not coloring_group_exists :
                script_dir = os.path.dirname(os.path.realpath(__file__))
                folder_path = os.path.join(script_dir, "asset")
                file_name = "nods.blend"
                blend_file_path = os.path.join(folder_path, file_name)
                if not "KH-Ambient Occlusion" in bpy.data.node_groups:
                    with bpy.data.libraries.load(blend_file_path) as (data_from, data_to):
                        data_to.node_groups = [name for name in data_from.node_groups if name.startswith("KH-Ambient Occlusion")]

                if "KH-Ambient Occlusion" in bpy.data.node_groups:
                    active_material = bpy.context.object.active_material
                    if active_material is not None:
                        coloring_group = False
                        for node in active_material.node_tree.nodes:
                            if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Ambient Occlusion"):
                                group = node
                                coloring_group = True
                                break

                        if not coloring_group:
                            if "KH-Ambient Occlusion" not in active_material.node_tree.nodes:
                                node_group = active_material.node_tree.nodes.new('ShaderNodeGroup')
                                node_group.node_tree = bpy.data.node_groups["KH-Ambient Occlusion"]
                                node_group.location = (0, 500) 

                                if active_material.node_tree.nodes["Principled BSDF"].inputs[0].links:
                                    connected_node = active_material.node_tree.nodes["Principled BSDF"].inputs[0].links[0].from_node
                                    if connected_node.type == 'MIX':
                                        active_material.node_tree.links.new(connected_node.outputs[2], node_group.inputs[0])
                                    else:
                                        active_material.node_tree.links.new(connected_node.outputs[0], node_group.inputs[0])
                                    active_material.node_tree.links.new(node_group.outputs[0], active_material.node_tree.nodes["Principled BSDF"].inputs[0]) 
                    
            else:
                if bsdf_principled and not base_color_node and not coloring_group_exists :
                    group = nodes.new(type='ShaderNodeGroup')
                    group.node_tree = bpy.data.node_groups.new(type="ShaderNodeTree", name="Ambient Occlusion")
                    group.location = (-400,500)
                    Group_Input=group.node_tree.nodes.new(type='NodeGroupInput')
                    Group_Input.location = (-500, 0)
                    color_socket = group.node_tree.interface.new_socket(name="Color", in_out='INPUT')
                    color_socket.socket_type = 'NodeSocketColor' 
                    
                    fac_socket = group.node_tree.interface.new_socket(name="fac", in_out='INPUT')
                    fac_socket.socket_type = 'NodeSocketFloat' 
                    for item in group.node_tree.interface.items_tree:
                        if item.name == "fac" and item.in_out == 'INPUT':
                            item.min_value = 0
                            item.max_value = 1
                    
                    dist_socket = group.node_tree.interface.new_socket(name="Distance", in_out='INPUT')
                    dist_socket.socket_type = 'NodeSocketFloat' 
                    for item in group.node_tree.interface.items_tree:
                        if item.name == "Distance" and item.in_out == 'INPUT':
                            item.min_value = 0
                    
                    color1_socket = group.node_tree.interface.new_socket(name="Color", in_out='INPUT')
                    color1_socket.socket_type = 'NodeSocketColor' 
                    
                    Group_Output=group.node_tree.nodes.new(type='NodeGroupOutput')
                    Group_Output.location = (500, 100)
                    output_socket = group.node_tree.interface.new_socket(name="Base Color", in_out='OUTPUT')
                    output_socket.socket_type = 'NodeSocketColor'
                    
                    # Add nodes to the NodeGroup
                    mix_node = group.node_tree.nodes.new(type='ShaderNodeMixRGB')
                    mix_node.blend_type = 'MULTIPLY'  # Set blend type to Multiply
                    mix_node.location = (0, -400)
                    mix_node.inputs[0].default_value = 0.2

                    hue_node = group.node_tree.nodes.new(type='ShaderNodeAmbientOcclusion')
                    hue_node.inputs[1].default_value = 0.01
                    hue_node.location = (0, -200)
                    
                    group.inputs[0].default_value = (1, 1, 1, 1)
                    group.inputs[1].default_value = 0.2
                    group.inputs[2].default_value = 0.01
                    group.inputs[3].default_value = (1, 1, 1, 1)
                    group.node_tree.links.new(Group_Input.outputs["Color"], mix_node.inputs[1])
                    group.node_tree.links.new(Group_Input.outputs[1], mix_node.inputs[0])
                    group.node_tree.links.new(Group_Input.outputs[2], hue_node.inputs[1])
                    group.node_tree.links.new(Group_Input.outputs[3], hue_node.inputs[0])
                    group.node_tree.links.new(hue_node.outputs[0], mix_node.inputs[2])                        
                    group.node_tree.links.new(mix_node.outputs["Color"], Group_Output.inputs["Base Color"])                        
                    node_tree.links.new(group.outputs["Base Color"], bsdf_principled.inputs["Base Color"])                                                
                        
        return {'FINISHED'}
    
# leavesOperator
class leavesOperator(bpy.types.Operator):
    """Add nodes to selected object's material"""
    bl_idname = "material.plant_operator"
    bl_label = "Plant Leaves"

    def execute(self, context):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        folder_path = os.path.join(script_dir, "asset")
        file_name = "nods.blend"
        blend_file_path = os.path.join(folder_path, file_name)

        if not "KH-leaves" in bpy.data.node_groups:
            with bpy.data.libraries.load(blend_file_path) as (data_from, data_to):
                data_to.node_groups = [name for name in data_from.node_groups if name.startswith("KH-leaves")]
                
        obj = bpy.context.active_object
        if obj and obj.active_material and obj.active_material.use_nodes:
            material = obj.active_material
            node_tree = material.node_tree
            nodes = node_tree.nodes
            links = node_tree.links.new 
            bsdf_principled = None
            base_color_node = None
            coloring_group = None
            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    bsdf_principled = node
                    color_input = node.inputs.get("Base Color")
                    if color_input and color_input.is_linked:
                        base_color_node = color_input.links[0].from_node
                    break
            for node in nodes:
                if node.type == 'GROUP' and node.node_tree.name.startswith("KH-leaves"):
                    coloring_group = node
                    break

            if bsdf_principled and base_color_node and not coloring_group :
                node_group_name = "KH-leaves"      
                if node_group_name in bpy.data.node_groups:
                    active_material = bpy.context.active_object.active_material
                    if active_material is not None:
                        node_group = bpy.data.node_groups[node_group_name]
                        node = active_material.node_tree.nodes.new("ShaderNodeGroup")
                        node.node_tree = node_group
                        node.location = (0, 600)
                        bpy.context.view_layer.update()
                        
                        for node in nodes:
                            if node.type == 'GROUP' and node.node_tree.name.startswith("KH-leaves"):
                                coloring_group = node
                                break
                            
                        if base_color_node :
                            if base_color_node.type == 'MIX':
                                linked_node = color_input.links[0].from_node 
                                material.node_tree.links.new(linked_node.outputs[2], coloring_group.inputs[1])
                            else:
                                if bsdf_principled.inputs['Base Color'].links:
                                    base_color_node = bsdf_principled.inputs['Base Color'].links[0].from_node
                                    links(base_color_node.outputs[0], coloring_group.inputs['Color'])
                            
                            if bsdf_principled.inputs['Alpha'].links:
                                base_color_node = bsdf_principled.inputs['Alpha'].links[0].from_node
                                links(base_color_node.outputs[0], coloring_group.inputs[2])
                                
                            links(bsdf_principled.outputs[0], coloring_group.inputs[0])           
                            links(material.node_tree.nodes['Material Output'].inputs['Surface'], coloring_group.outputs[0])
            else:
                if coloring_group :
                    links(material.node_tree.nodes['Material Output'].inputs['Surface'], bsdf_principled.outputs[0])
                    active_material = bpy.context.active_object.active_material
                    if active_material is not None:
                        nodes = active_material.node_tree.nodes
                        for node in nodes:
                            if node.type == 'GROUP' and node.node_tree.name.startswith("KH-leaves"):
                                active_material.node_tree.nodes.remove(node)
                                break
                                        
        return {'FINISHED'}


#Transparent
class AddMixCheddarOperator(bpy.types.Operator):
    bl_idname = "material.add_mix_cheddar"
    bl_label = "Transparent"
    def execute(self, context):
        obj = bpy.context.active_object
        if obj and obj.active_material and obj.active_material.use_nodes:
            nodes = obj.active_material.node_tree.nodes
            coloring_group_exists = False
            for node in nodes:
                if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Transparen"):
                    coloring_group_exists = True
                    break
            if not coloring_group_exists :
                # Get the active material
                material = bpy.context.active_object.active_material
                obj = bpy.context.active_object
                mat_slot = obj.material_slots[obj.active_material_index]
                material = mat_slot.material
                node_tree = material.node_tree
                nodes = node_tree.nodes
                links = material.node_tree.links
                nodes = material.node_tree.nodes
        
                # Check if the material has a node tree
                if material.node_tree:
                    group = nodes.new(type='ShaderNodeGroup')
                    group.node_tree = bpy.data.node_groups.new(type="ShaderNodeTree", name="KH-Transparen")
                    group.location = (300, 600)
                    Group_Input=group.node_tree.nodes.new(type='NodeGroupInput')
                    Group_Input.location = (-500, 100)
                    color_socket = group.node_tree.interface.new_socket(name="Shader", in_out='INPUT')
                    color_socket.socket_type = 'NodeSocketShader' 
            
                    fac_socket = group.node_tree.interface.new_socket(name="fac", in_out='INPUT')
                    fac_socket.socket_type = 'NodeSocketFloat' 
                    for item in group.node_tree.interface.items_tree:
                            if item.name == "fac" and item.in_out == 'INPUT':
                                item.min_value = 0
                                item.max_value = 1
                        
                    color1_socket = group.node_tree.interface.new_socket(name="Color", in_out='INPUT')
                    color1_socket.socket_type = 'NodeSocketColor' 
                    
                    Group_Output=group.node_tree.nodes.new(type='NodeGroupOutput')
                    Group_Output.location = (500, 100)
                    output_socket = group.node_tree.interface.new_socket(name="Shader", in_out='OUTPUT')
                    output_socket.socket_type = 'NodeSocketShader'
                    
                    group.inputs[1].default_value = .5
                    group.inputs[2].default_value = (1, 1, 1, 1)
                    
                    mix_cheddar_node = group.node_tree.nodes.new('ShaderNodeMixShader')
                    mix_cheddar1_node = group.node_tree.nodes.new('ShaderNodeMixShader')
                    light_path_node = group.node_tree.nodes.new('ShaderNodeLightPath')
                    transparent_node = group.node_tree.nodes.new('ShaderNodeBsdfTransparent')
                    output_node = material.node_tree.nodes.get('ShaderNodeOutputMaterial')
                    # Connect the nodes
                    group.node_tree.links.new(light_path_node.outputs[1], mix_cheddar_node.inputs[0])
                    group.node_tree.links.new(transparent_node.outputs['BSDF'], mix_cheddar_node.inputs[2])
                    group.node_tree.links.new(mix_cheddar_node.outputs[0], mix_cheddar1_node.inputs[2])
                    group.node_tree.links.new(Group_Input.outputs[0], mix_cheddar1_node.inputs[1])
                    group.node_tree.links.new(Group_Input.outputs[1], mix_cheddar1_node.inputs[0])
                    group.node_tree.links.new(Group_Input.outputs[0], mix_cheddar_node.inputs[1])
                    group.node_tree.links.new(Group_Input.outputs[2], transparent_node.inputs[0])
                    
                    group.node_tree.links.new(mix_cheddar1_node.outputs[0], Group_Output.inputs[0])
                    # Set the Mix Cheddar node properties
                    mix_cheddar_node.name = 'Mix Cheddar'
                    mix_cheddar_node.inputs[0].default_value = 0.5
                    mix_cheddar_node.location = (100, 500)
                    mix_cheddar1_node.location = (300, 500)
                    light_path_node.location = (-100, 900)
                    transparent_node.location = (-100, 500)
                    node_tree = material.node_tree
                    
            
                principled_bsdf_node = None
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        principled_bsdf_node = node
                        break   
                if principled_bsdf_node:
                        material.node_tree.links.new(principled_bsdf_node.outputs['BSDF'], group.inputs[0])
                        node_tree.links.new(material.node_tree.nodes['Material Output'].inputs['Surface'], group.outputs[0])
                
                glass_bsdf_node = None
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_GLASS':
                        glass_bsdf_node = node
                        break   
                if glass_bsdf_node:
                        material.node_tree.links.new(glass_bsdf_node.outputs['BSDF'], group.inputs[0])
                        node_tree.links.new(material.node_tree.nodes['Material Output'].inputs['Surface'], group.outputs[0])
            else:
                material = bpy.context.active_object.active_material
                obj = bpy.context.active_object
                mat_slot = obj.material_slots[obj.active_material_index]
                material = mat_slot.material
                node_tree = material.node_tree
                nodes = node_tree.nodes
                nodes = material.node_tree.nodes
                principled_bsdf_node = None
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        principled_bsdf_node = node
                        break   
                if principled_bsdf_node:
                        node_tree.links.new(material.node_tree.nodes['Material Output'].inputs['Surface'], principled_bsdf_node.outputs[0])
                
                glass_bsdf_node = None
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_GLASS':
                        glass_bsdf_node = node
                        break   
                if glass_bsdf_node:
                        node_tree.links.new(material.node_tree.nodes['Material Output'].inputs['Surface'], glass_bsdf_node.outputs[0])
                for node in nodes:
                    if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Transparen"):
                        material.node_tree.nodes.remove(node)
                        break    
        return {'FINISHED'}
        
#Glass Thickness
class FixGlassCurtainsOperator(bpy.types.Operator):
    bl_idname = "object.fix_glass_curtains"
    bl_label = "Glass Thickness"
    
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
    

# Material Control///////////////////////////////////////////////////////////////////////////////////////////////////////////////
preview_collection9= bpy.utils.previews.new()
preview_collection9.load("13.png", os.path.join(my_icons_dir, "13.png"), 'IMAGE')
class KH_tools_Material(bpy.types.Panel):
    bl_idname = "OBJECT_PT_tools_material"
    bl_label = "Material"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = 'KH-Material'
    bl_category = "KH-Tools"
    bl_options = {'DEFAULT_CLOSED'}
    
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
                text="", icon_value=preview_collection9['13.png'].icon_id)
        except KeyError:
            pass
    def draw(self, context):
        layout = self.layout
        selected_object = bpy.context.active_object
        obj = context.object
        
        if obj is not None and obj.type == 'MESH' and obj.active_material is not None:
            row = layout.row()
            material = obj.active_material
            box = layout.box()
            row = box.row()
            row.template_ID(obj, "active_material")

            #row.prop(material, "name", text="")
#            if material.users > 1:
#                row.scale_x = 0.3
#                row.operator("object.make_single_user_material", text=f"{material.users}")
                
        else:
             box = layout.box()
             row = box.row()
             row.label(text="There is no active material.", icon='ERROR') 
              

# Mapping Control///////////////////////////////////////////////////////////////////////////////////////////////////////////////
preview_collection2= bpy.utils.previews.new()
preview_collection2.load("2.png", os.path.join(my_icons_dir, "2.png"), 'IMAGE')
class MappingControlsPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_idname = "OBJECT_PT_mapping"
    bl_region_type = "UI"
    bl_category = "KH-Tools"
    bl_label = "Mapping Controls"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id   = "OBJECT_PT_tools_material"
    

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon_value=preview_collection2['2.png'].icon_id)
        except KeyError:
            pass
  
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        if obj is not None and obj.type == 'MESH' and obj.active_material is not None:
            row = layout.row()
            material = obj.active_material
            # تقسيم الصف باستخدام مجموعة
            box = layout.box()
            row = box.row()
            row.operator("view3d.custom_operator" , icon='UV')
            row = box.row()
            row.operator("object.kh_mapping", text="Mapping", icon='EVENT_M')

            row = box.row()
            if "Scale Texture" in bpy.data.objects:
                cube_obj = bpy.data.objects["Scale Texture"]
                row.operator("object.delete_scale_texture", text="Delete Dimensions")
                row = box.row()
                row.prop(cube_obj, "dimensions", index=0, text="x")
                row.prop(cube_obj, "dimensions", index=1, text="y")
                row.prop(cube_obj, "dimensions", index=2, text="Z")
            else:
                row.operator("mesh.add_cube_at_cursor", text="Add Dimensions")
                row = box.row()
                row.prop(context.scene, "cube_scale_x", text="X")
                row.prop(context.scene, "cube_scale_y", text="Y")
                row.prop(context.scene, "cube_scale_z", text="Z")  

            mat = obj.active_material
            if mat is not None and mat.node_tree is not None:
                mapping_nodes = [node for node in mat.node_tree.nodes if node.type == 'MAPPING']
                for i, mapping_node in enumerate(mapping_nodes):
                    row = layout.row()
                    row.label(text=f"Mapping {i + 1}")
                    row.operator("object.texture_coordinate_obj", text="", icon='OBJECT_DATA')
                    row.operator("object.texture_coordinate_uv", text="", icon='MOD_UVPROJECT')
                    row.operator("object.texture_coordinate_generated", text="", icon='TEXTURE')
                    row.prop(mapping_node, "select", text="", icon='OPTIONS')

                    if mapping_node.select:
                        row = layout.row()
                        row.label(text="Scale", icon='FULLSCREEN_ENTER')
                        for j in range(3):
                            row = layout.row()
                            row.prop(mapping_node.inputs[3], "default_value", index=j, text=f"{['X', 'Y', 'Z'][j]}")

                            
                        row = layout.row()
                        row.label(text="Location", icon='CON_LOCLIMIT')
                        row.label(text="Rotation", icon='FILE_REFRESH')
                        for j in range(3):
                            row = layout.row()
                            row.prop(mapping_node.inputs[1], "default_value", index=j, text=f"{['X', 'Y', 'Z'][j]}")
                            row.prop(mapping_node.inputs[2], "default_value", index=j, text=f"{['X', 'Y', 'Z'][j]}")
        else:
             box = layout.box()
             row = box.row()
             row.label(text="There is no active material.", icon='ERROR') 

#uv
class CustomOperator(bpy.types.Operator):
    bl_idname = "view3d.custom_operator"
    bl_label = "UV Editor"

    def execute(self, context):
        bpy.ops.wm.window_new()
        bpy.context.area.ui_type = 'UV'
        scene = bpy.context.scene       
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.select_all(action='SELECT')
        bpy.context.space_data.show_region_toolbar = True
        return {'FINISHED'}
     
class MakeSingleUserMaterialOperator(bpy.types.Operator):
    bl_idname = "object.make_single_user_material"
    bl_label = "نسخ كنسخة واحدة"
    bl_options = {'REGISTER', 'UNDO'}
    #material: bpy.props.PointerProperty(type=bpy.types.Material)
    def execute(self, context):
        bpy.ops.object.make_single_user(object=False, obdata=False, material=True, animation=False, obdata_animation=False)
        return {'FINISHED'}
    

class TEX_COORD_Object(bpy.types.Operator):
    """texture coordinate Object"""
    bl_idname = "object.texture_coordinate_obj"
    bl_label = "texture coordinate Object"

    def execute(self, context):
        # الحصول على المادة النشطة
        active_material = bpy.context.active_object.active_material
        if active_material:
            node_tree = active_material.node_tree
            mapping_nodes = [node for node in node_tree.nodes if node.type == 'MAPPING']
            texture_coordinate_nodes = [node for node in node_tree.nodes if node.type == 'TEX_COORD']
            # التحقق من وجود نود مابنق ونود تكتشر كوردينات
            if mapping_nodes and texture_coordinate_nodes:
                for mapping_node in mapping_nodes:
                    for texture_coordinate_node in texture_coordinate_nodes:
                        # ربط الأوتبوت "Object" لنود تكتشر كوردنيت مع الإنبوت "Vector" لنود المابنق
                        node_tree.links.new(texture_coordinate_node.outputs["Object"], mapping_node.inputs["Vector"])
               
        return {'FINISHED'}
    
class TEX_COORD_UV(bpy.types.Operator):
    """texture coordinate UV"""
    bl_idname = "object.texture_coordinate_uv"
    bl_label = "texture coordinate UV"

    def execute(self, context):
        # الحصول على المادة النشطة
        active_material = bpy.context.active_object.active_material
        if active_material:
            node_tree = active_material.node_tree
            mapping_nodes = [node for node in node_tree.nodes if node.type == 'MAPPING']
            texture_coordinate_nodes = [node for node in node_tree.nodes if node.type == 'TEX_COORD']
            # التحقق من وجود نود مابنق ونود تكتشر كوردينات
            if mapping_nodes and texture_coordinate_nodes:
                for mapping_node in mapping_nodes:
                    for texture_coordinate_node in texture_coordinate_nodes:
                        # ربط الأوتبوت "Object" لنود تكتشر كوردنيت مع الإنبوت "Vector" لنود المابنق
                        node_tree.links.new(texture_coordinate_node.outputs["UV"], mapping_node.inputs["Vector"])

        return {'FINISHED'}

class TEX_COORD_Generated(bpy.types.Operator):
    """texture coordinate Generated"""
    bl_idname = "object.texture_coordinate_generated"
    bl_label = "texture coordinate Generated"

    def execute(self, context):
        # الحصول على المادة النشطة
        active_material = bpy.context.active_object.active_material
        if active_material:
            node_tree = active_material.node_tree
            mapping_nodes = [node for node in node_tree.nodes if node.type == 'MAPPING']
            texture_coordinate_nodes = [node for node in node_tree.nodes if node.type == 'TEX_COORD']
            # التحقق من وجود نود مابنق ونود تكتشر كوردينات
            if mapping_nodes and texture_coordinate_nodes:
                for mapping_node in mapping_nodes:
                    for texture_coordinate_node in texture_coordinate_nodes:
                        # ربط الأوتبوت "Generated" لنود تكتشر كوردنيت مع الإنبوت "Vector" لنود المابنق
                        node_tree.links.new(texture_coordinate_node.outputs["Generated"], mapping_node.inputs["Vector"])

        return {'FINISHED'}

class AddCubeAtCursorOperator(bpy.types.Operator):
    """Add a cube at the 3D cursor"""
    bl_idname = "mesh.add_cube_at_cursor"
    bl_label = "Add Cube at Cursor"

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add(size=1, location=context.scene.cursor.location)
        cube = bpy.context.active_object
        cube.scale = (context.scene.cube_scale_x, context.scene.cube_scale_y, context.scene.cube_scale_z)
        cube.name = "Scale Texture"
        
        # Create a new material
        mat = bpy.data.materials.new(name="Scale Texture Material")
        mat.diffuse_color = (0, 1, 0, 1)  # Green color
        
        # Assign the material to the cube
        if cube.data.materials:
            cube.data.materials[0] = mat
        else:
            cube.data.materials.append(mat)
        return {'FINISHED'}

class DeleteScaleTextureOperator(bpy.types.Operator):
    """Delete Scale Texture object"""
    bl_idname = "object.delete_scale_texture"
    bl_label = "Delete Scale Texture"

    def execute(self, context):
        if "Scale Texture" in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects["Scale Texture"], do_unlink=True)
        return {'FINISHED'}

# Displacement -------------------------------------------------------------------------------------------------------------------------   
preview_collection3= bpy.utils.previews.new()
preview_collection3.load("6.png", os.path.join(my_icons_dir, "6.png"), 'IMAGE')
   
class DisplsPanel(bpy.types.Panel):
    bl_label = "Displacement"
    bl_idname = "VIEW3D_PT_displs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KH-Tools"
    bl_parent_id   = "OBJECT_PT_tools_material"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon_value=preview_collection3['6.png'].icon_id)
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout                
        selected_object = bpy.context.active_object
        if selected_object:
            if selected_object.material_slots:
                material_slots = selected_object.material_slots
            
        obj = context.object
        if obj is not None and obj.type == 'MESH' and obj.active_material is not None:
            material = obj.active_material
            mat = obj.active_material
            if mat is not None and mat.node_tree is not None:
        
                if material and material.cycles:          
                    box = layout.box()
                    row = box.row()
                    if hasattr(material.cycles, "displacement_method"):
                        row.prop(material.cycles, "displacement_method", text="")
                    else:
                        row.prop(material, "displacement_method", text="")
                    
                    obj = context.object
                    if obj.modifiers.get("Subdivision") is None:
                        row = box.row()
                        row.operator("displace.add_modifier", text="Displacement", icon='ADD')
                    else:
                        row = box.row()
                        row.operator("object.remove_subdivision_modifier", text="Remove Displacement", icon='TRASH')
                    obj = context.object
                    if obj.modifiers.get("Triangulate") is None:
                        row = box.row()
                        row.operator("object.add_triangulate_modifier", text="Fix Triangle", icon='MESH_ICOSPHERE')
                    else:
                        row = box.row()
                        row.operator("object.remove_triangulate_modifier", text="Remove Triangle system", icon='TRASH')
                    disp_node = None
                    if obj.type == 'MESH':
                        for mat_slot in obj.material_slots:
                            if mat_slot.material and mat_slot.material.use_nodes:
                                for node in mat_slot.material.node_tree.nodes:
                                    if node.type == 'DISPLACEMENT':
                                        disp_node = node
                                        break
                    if disp_node:
                        row = box.row()
                        row.prop(disp_node.inputs[2], "default_value", text="Scale")
                        row = box.row()
                        row.prop(disp_node.inputs[1], "default_value", text="Midlevel") 
                    else:
                        box = layout.box()
                        row = box.row()
                        row.label(text="No Displacement Node found.", icon='ERROR')                   
                    
                    bump_node = None
                    if obj.type == 'MESH':
                        for mat_slot in obj.material_slots:
                            if mat_slot.material and mat_slot.material.use_nodes:
                                for node in mat_slot.material.node_tree.nodes:
                                    if node.type == 'BUMP':
                                        bump_node = node
                                        break
                    if bump_node:
                        box = layout.box()
                        row = box.row()
                        row.label(text="Bump :")
                        row = box.row()
                        row.prop(bump_node.inputs[0], "default_value", text="Strength")
                        row = box.row()
                        row.prop(bump_node.inputs[1], "default_value", text="Distance")
                    
                    Normal_node = None
                    if obj.type == 'MESH':
                        for mat_slot in obj.material_slots:
                            if mat_slot.material and mat_slot.material.use_nodes:
                                for node in mat_slot.material.node_tree.nodes:
                                    if node.type == 'NORMAL_MAP':
                                        Normal_node = node
                                        break
                    
                    if Normal_node:
                        row = box.row()
                        row.label(text="Normal :")
                        row = box.row()
                        row.prop(Normal_node.inputs[0], "default_value", text="Strength")
                    
                    box = layout.box()
                    row = box.row()
                    row.label(text="Quality :")
                    row = box.row()
                    row.prop(context.scene.cycles, "preview_dicing_rate", text="Preview")
                    row = box.row()
                    row.prop(context.scene.cycles, "dicing_rate", text="Render")
                else:
                        box = layout.box()
                        row = box.row()
                        row.label(text="This object does not have a Material.", icon='ERROR') 
        else:
            
            box = layout.box()
            row = box.row()
            row.label(text="Quality :")
            row = box.row()
            row.prop(context.scene.cycles, "preview_dicing_rate", text="Preview")
            row = box.row()
            row.prop(context.scene.cycles, "dicing_rate", text="Render")
            row = box.row()
            row.label(text="There is no active material.", icon='ERROR') 

            
# Displacement
class AddDisplaceModifier(bpy.types.Operator):
    bl_idname = "displace.add_modifier"
    bl_label = "Add Displacement"

    def execute(self, context):
        scene = bpy.context.scene       
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0005)
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        
        # feature_set was removed in Blender 5.0 (adaptive subdivision is always available)
        if bpy.app.version < (5, 0, 0) and hasattr(bpy.context.scene.cycles, 'feature_set'):
            bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL'
        
        # dicing_rate settings (only for Blender < 5.0)
        if bpy.app.version < (5, 0, 0):
            bpy.context.scene.cycles.dicing_rate = 3
            bpy.context.scene.cycles.preview_dicing_rate = 6
        
        if bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # Add Subdivision modifier
        if bpy.context.object.modifiers.get("Subdivision") is None:
            bpy.ops.object.modifier_add(type='SUBSURF')
            
        # Set subdivision properties
        subdiv_mod = bpy.context.object.modifiers["Subdivision"]
        subdiv_mod.subdivision_type = 'SIMPLE'
        
        # Adaptive subdivision - API changed in Blender 5.0
        if bpy.app.version >= (5, 0, 0):
            # Blender 5.0+: use modifier's use_adaptive_subdivision property
            if hasattr(subdiv_mod, 'use_adaptive_subdivision'):
                subdiv_mod.use_adaptive_subdivision = True
        else:
            # Blender 4.x: use object.cycles properties
            if hasattr(bpy.context.object.cycles, 'dicing_rate'):
                bpy.context.object.cycles.dicing_rate = 0.85
            if hasattr(bpy.context.object.cycles, 'use_adaptive_subdivision'):
                bpy.context.object.cycles.use_adaptive_subdivision = True
        
        bpy.ops.object.shade_smooth()
        
        obj = context.object
        if obj is not None and obj.type == 'MESH' and obj.active_material is not None:
            material = obj.active_material
            mat = obj.active_material
            if mat is not None and mat.node_tree is not None:
                if material and material.cycles:  
                    if hasattr(material.cycles, "displacement_method"):
                        bpy.context.object.active_material.cycles.displacement_method = 'BOTH'
                    else:
                        bpy.context.object.active_material.displacement_method = 'BOTH'

       
        return {'FINISHED'}
    
class OBJECT_OT_AddTriangulateModifier(bpy.types.Operator):
    bl_label = "Add Triangulate Modifier"
    bl_idname = "object.add_triangulate_modifier"
    def execute(self, context):
        scene = bpy.context.scene       
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = context.object
        if obj.modifiers.get("Triangulate") is None:
            modifier = obj.modifiers.new(name="Triangulate", type='TRIANGULATE')
            bpy.ops.object.modifier_move_to_index(modifier="Triangulate", index=0)
            bpy.context.object.modifiers["Triangulate"].quad_method = 'FIXED'
            self.report({'INFO'}, "Triangulate modifier added.")
        else:
            self.report({'WARNING'}, "Triangulate modifier already exists for the object.")
        return {'FINISHED'}

class OBJECT_OT_RemoveTriangulateModifier(bpy.types.Operator):
    bl_label = "Remove Triangulate Modifier"
    bl_idname = "object.remove_triangulate_modifier"
    def execute(self, context):
        scene = bpy.context.scene       
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = context.object
        modifier = obj.modifiers.get("Triangulate")
        if modifier is not None:
            obj.modifiers.remove(modifier)
            self.report({'INFO'}, "Triangulate modifier removed.")
        else:
            self.report({'WARNING'}, "Triangulate modifier does not exist for the object.")
        return {'FINISHED'}
    
class OBJECT_OT_RemoveSubdivisionModifier(bpy.types.Operator):
    bl_label = "Remove Triangulate Modifier"
    bl_idname = "object.remove_subdivision_modifier"
    def execute(self, context):
        scene = bpy.context.scene       
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = context.object
        modifier = obj.modifiers.get("Subdivision")
        if modifier is not None:
            obj.modifiers.remove(modifier)
            bpy.ops.object.shade_flat()
            self.report({'INFO'}, "Subdivision modifier removed.")
        else:
            self.report({'WARNING'}, "Subdivision modifier does not exist for the object.")
        return {'FINISHED'}
               
               
# Make it rainy------------------------------------------------------------
class new_RainyOperator(bpy.types.Operator):
    bl_idname = "object.new_rainy_mix_node"
    bl_label = "Rainy"
    bl_description = ""

    def execute(self, context): 
        script_dir = os.path.dirname(os.path.realpath(__file__))
        folder_path = os.path.join(script_dir, "asset")
        file_name = "nods.blend"
        blend_file_path = os.path.join(folder_path, file_name)
        
        obj = bpy.context.active_object
        material = obj.active_material
        node_tree = material.node_tree
        nodes = node_tree.nodes
        bsdf_node = None               
        for node in nodes: 
            if node.type == 'BSDF_PRINCIPLED':
                bsdf_node = node 
                break
        if bsdf_node :
            
            if not "KH-Rainy" in bpy.data.node_groups:
                with bpy.data.libraries.load(blend_file_path) as (data_from, data_to):
                    data_to.node_groups = [name for name in data_from.node_groups if name.startswith("KH-Rainy")]

            if "KH-Rainy" in bpy.data.node_groups:
                active_material = bpy.context.object.active_material
                group_node = active_material.node_tree.nodes.new('ShaderNodeGroup')
                group_node.node_tree = bpy.data.node_groups["KH-Rainy"]
                group_node.location = (0, 0)
                
                obj = bpy.context.active_object
                mat_slot = obj.active_material

                if (mat_slot):
                    material = obj.active_material
                    node_tree = material.node_tree
                    nodes = node_tree.nodes
                    links = material.node_tree.links
                    for node in nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            color_input = node.inputs.get("Base Color")
                            if color_input.is_linked:
                                linked_node = color_input.links[0].from_node
                                if linked_node.type == 'MIX':
                                    linked_node = color_input.links[0].from_node       
                                    material.node_tree.links.new(linked_node.outputs[2], group_node.inputs["Base Color"])
                                    break
                                else :
                                    node_tree.links.new(group_node.inputs["Base Color"], linked_node.outputs[0])
                                
                    bsdf_node = None               
                    for node in nodes: 
                        if node.type == 'BSDF_PRINCIPLED':
                            bsdf_node = node 
                            color_input = node.inputs.get("Base Color")
                            if color_input and color_input.is_linked:
                                base_color_node = color_input.links[0].from_node
                            break

                    for node in nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            color_input = node.inputs.get("Roughness")
                            if color_input.is_linked:
                                linked_node = color_input.links[0].from_node
                                if linked_node.type == 'MIX':
                                    linked_node = color_input.links[0].from_node       
                                    material.node_tree.links.new(linked_node.outputs[2], group_node.inputs["Roughness"])
                                    break
                                else :
                                    material.node_tree.links.new(linked_node.outputs[0], group_node.inputs["Roughness"])

                            node_tree.links.new(group_node.outputs["Roughness"], bsdf_node.inputs["Roughness"])
                            node_tree.links.new(group_node.outputs["Base Color"], bsdf_node.inputs["Base Color"])
                
#---------------------------------------------------------------------
                
                rainy_group_node = None
                bump_node = None
                Normal_node = None
                Displacement_node = None
                mat_output = None
                material = obj.active_material
                node_tree = material.node_tree
                nodes = node_tree.nodes
                links = node_tree.links.new  
                
                for node in nodes:
                    if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Rainy"):
                        rainy_group_node = node
                        break
                    
                for node in nodes:
                    if node.type == 'BUMP':
                        bump_node = node
                        break
                
                for node in nodes:
                    if node.type == 'NORMAL_MAP':
                        Normal_node = node
                        break
                
                for node in nodes:
                    if node.type == 'DISPLACEMENT':
                        Displacement_node = node
                        break
                    
                if 'Specular' in bsdf_node.inputs:
                    bsdf_node.inputs['Specular'].default_value = 0.5
                else:
                    bsdf_node.inputs['Specular IOR Level'].default_value = 0.5
                    
                if Normal_node:
                    color_input = Normal_node.inputs.get("Color")
                    if color_input and color_input.is_linked:
                        linked_node = color_input.links[0].from_node
                        links(linked_node.outputs[0], rainy_group_node.inputs[2])
                        links(Normal_node.inputs[1], rainy_group_node.outputs[2]) 
                        
                if bump_node :
                    color_input = bump_node.inputs.get("Height")
                    if color_input and color_input.is_linked:
                        linked_node = color_input.links[0].from_node
                        links(linked_node.outputs[0], rainy_group_node.inputs[3])
                        links(bump_node.inputs[2], rainy_group_node.outputs[3])
                else:                                       
                    group_Bump = nodes.new("ShaderNodeBump")
                    group_Bump.location = (-100, -100)
                    group_Bump.inputs[0].default_value = 0.1
                    links(bsdf_node.inputs['Normal'],  group_Bump.outputs[0]) 
                    links(group_Bump.inputs[2], rainy_group_node.outputs[3])                    
                    if Normal_node:
                        links(Normal_node.outputs[0], group_Bump.inputs[3]) 

                if Displacement_node :
                    color_input = Displacement_node.inputs.get("Height")
                    if color_input and color_input.is_linked:
                        linked_node = color_input.links[0].from_node
                        links(linked_node.outputs[0], rainy_group_node.inputs[4])  
                        links(Displacement_node.inputs[0], rainy_group_node.outputs[4])

        return {'FINISHED'}   
    

class RainyDeleteOperator(bpy.types.Operator):
    bl_idname = "object.rainy_delete_node"
    bl_label = "Delete Rain"
    bl_description = "Delete Rain"

    def execute(self, context):
        obj = bpy.context.active_object
        if obj and obj.active_material and obj.active_material.use_nodes:
            material = obj.active_material
            node_tree = material.node_tree
            nodes = node_tree.nodes
            for node in nodes:
                connected_node = None
                connected_node1 = None
                connected_node2 = None
                connected_node3 = None
                connected_node4 = None
                connected_node5 = None
                bsdf_principled_node = None
                if node.type == 'GROUP' and  node.node_tree.name.startswith("KH-Rainy"):
                    for input_node in node.inputs:
                        if input_node.name == "Base Color" and input_node.is_linked:
                            connected_node = input_node.links[0].from_node
                            break
                    for input_node1 in node.inputs:   
                        if input_node1.name == "Roughness" and input_node1.is_linked:
                            connected_node1 = input_node1.links[0].from_node
                            break
                    for input_node3 in node.inputs:
                        if input_node3.name == "Normal" and input_node3.is_linked:
                            connected_node3 = input_node3.links[0].from_node
                            break
                    for input_node4 in node.inputs:
                        if input_node4.name == "Bump" and input_node4.is_linked:
                            connected_node4 = input_node4.links[0].from_node
                            break
                    for input_node5 in node.inputs:
                        if input_node5.name == "Displacement" and input_node5.is_linked:
                            connected_node5 = input_node5.links[0].from_node
                            break
                        
                    for node in nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            bsdf_principled_node = node
                            break
                if bsdf_principled_node:          
                    if connected_node:
                        node_tree.links.new(bsdf_principled_node.inputs["Base Color"],connected_node.outputs[0])
                        color_input = input_node.links[0].from_node
                        linked_node = color_input
                        if linked_node.type == 'MIX':
                            node_tree.links.new(bsdf_principled_node.inputs["Base Color"],connected_node.outputs[2])
                            
                    if connected_node1:
                        node_tree.links.new(bsdf_principled_node.inputs["Roughness"],connected_node1.outputs[0])
                        
                    if connected_node3:
                        for node in nodes:
                            if node.type == 'NORMAL_MAP':
                                bsdf_principled_node = node
                                break
                        node_tree.links.new(bsdf_principled_node.inputs["Color"],connected_node3.outputs[0])
                        
                    if connected_node4:
                        for node in nodes:
                            if node.type == 'BUMP':
                                bsdf_principled_node = node
                                break
                        node_tree.links.new(bsdf_principled_node.inputs["Height"],connected_node4.outputs[0])
                        
                    if connected_node5:
                        for node in nodes:
                            if node.type == 'DISPLACEMENT':
                                bsdf_principled_node = node
                                break
                        node_tree.links.new(bsdf_principled_node.inputs["Height"],connected_node5.outputs[0])
                        
            rainy_node_group_name = "Rainy"+ material.name
            rainy_node_group = bpy.data.node_groups.get(rainy_node_group_name)
            for node in nodes:
                if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Rainy"):
                    nodes.remove(node)
                    break  

        active_material = obj.active_material
        rainy_node_group_name = "Rainy"+ active_material.name
        rainy_node_group = bpy.data.node_groups.get(rainy_node_group_name)

        if rainy_node_group:
            for material in bpy.data.materials:
                if material.use_nodes:
                    tree = material.node_tree
                    for node in tree.nodes:
                        if node.type == 'GROUP' and node.node_tree == rainy_node_group:
                            tree.nodes.remove(node)
                            break

            bpy.data.node_groups.remove(rainy_node_group)
            
        return {'FINISHED'}
    
addon_dir = os.path.dirname(__file__)
my_icons_dir = os.path.join(addon_dir, "icons")
preview_collection = bpy.utils.previews.new()
preview_collection.load("16.png", os.path.join(my_icons_dir, "16.png"), 'IMAGE')

class RainyPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_rainy_panel"
    bl_label = "Rainy Tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'KH-Tools'
    bl_parent_id   = "OBJECT_PT_tools_material"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon_value=preview_collection['16.png'].icon_id)
        except KeyError:
            pass

    def draw(self, context):
        layout = self.layout
        selected_object = bpy.context.active_object
        if selected_object:
            if selected_object.material_slots:
                material_slots = selected_object.material_slots
        obj = bpy.context.active_object
        if obj is not None and obj.type == 'MESH' and obj.active_material is not None:
            if obj.material_slots and obj.active_material_index < len(obj.material_slots):
                mat_slot = obj.material_slots[obj.active_material_index]
                material = mat_slot.material
                active_material = bpy.context.active_object.active_material 
        else:
            box = layout.box()
            row = box.row()
            row.label(text="There is no active material.", icon='ERROR') 

        obj = context.object
        # = obj.active_material
        obj = bpy.context.active_object
        if obj is not None and obj.type == 'MESH' and obj.active_material is not None:
            material = obj.active_material
            node_tree = material.node_tree
            nodes = node_tree.nodes
            bsdf_principled = None
            base_color_node = None
            mat_output = None
            for node in nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    bsdf_principled = node
                    color_input = node.inputs.get("Base Color")
                    if color_input and color_input.is_linked:
                        base_color_node = color_input.links[0].from_node
                    break
            if bsdf_principled and base_color_node:
                if "KH-Rainy" in bpy.data.node_groups:
                    active_material = bpy.context.active_object.active_material
                    if active_material and active_material.use_nodes:
                        node_tree = active_material.node_tree
                        rainy_group_node = None
                        for node in node_tree.nodes:
                            if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Rainy"):
                                rainy_group_node = node
                                break
                        if rainy_group_node:
                            layout.operator("object.rainy_delete_node", text="Delete Rain", icon='MOD_FLUIDSIM')
                            row = layout.row()
                    
                            # عرض المدخل
                            row.prop(rainy_group_node.inputs.get("Water Color"), "default_value", text="Water Color")
                            row = layout.row()
                            row.prop(rainy_group_node.inputs.get("Dirty"), "default_value", text="Roughness Intensity", slider=True)
                            row = layout.row()
                            row.prop(rainy_group_node.inputs.get("Scale"), "default_value", text="Scale", slider=True)
                            row = layout.row()
                            row.prop(rainy_group_node.inputs.get("Density"), "default_value", text="Density", slider=True)
                            row = layout.row()
                            row.prop(rainy_group_node.inputs.get("Detail"), "default_value", text="Detail", slider=True)
                            row = layout.row()
                            row.prop(rainy_group_node.inputs.get("Distortion"), "default_value", text="Distortion", slider=True)
                            row = layout.row()
                            row.prop(rainy_group_node.inputs.get("Lacunarity"), "default_value", text="Lacunarity", slider=True)
                            row = layout.row()
                            row.prop(rainy_group_node.inputs.get("Sharpness"), "default_value", text="Sharpness", slider=True)

                            layout = self.layout
                            active_material = context.active_object.active_material
                            nodes = active_material.node_tree.nodes   
                            bsdf_node = None 
                            NORMAL_node = None 
                            Bump_node = None    
                            DISPLAC_node = None 
                            
                            for node in nodes: 
                                if node.type == 'BSDF_PRINCIPLED':
                                    bsdf_node = node 
                            if bsdf_node is not None:
                                if bsdf_node:
                                    if 'Specular' in bsdf_node.inputs:
                                        col = layout.column()
                                        col.prop(bsdf_node.inputs['Specular'], "default_value", text="Reflection")
                                    else:
                                        col = layout.column()
                                        col.prop(bsdf_node.inputs['Specular IOR Level'], "default_value", text="Reflection")

                            for node in nodes: 
                                if node.type == 'NORMAL_MAP':
                                    NORMAL_node = node 

                            if NORMAL_node is not None:
                                col = layout.column()
                                col.prop(NORMAL_node.inputs[0], "default_value", text="Normal", slider=True)
                                row = layout.row()
                                row.prop(rainy_group_node.inputs.get("Normal MIX"), "default_value", text="Normal MIX", slider=True)
                                
                            for node in nodes: 
                                if node.type == 'BUMP':
                                    Bump_node = node 

                            if Bump_node is not None:
                                col = layout.column()
                                col.prop(Bump_node.inputs[0], "default_value", text="Bump")
                                row = layout.row()
                                row.prop(rainy_group_node.inputs.get("Bump MIX"), "default_value", text="Bump MIX", slider=True)
                                
                            for node in nodes: 
                                if node.type == 'DISPLACEMENT':
                                    DISPLAC_node = node 

                            if DISPLAC_node is not None:
                                col = layout.column()
                                col.prop(DISPLAC_node.inputs[2], "default_value", text="Displacement")
                                row = layout.row()
                                row.prop(rainy_group_node.inputs.get("Displacement MIX"), "default_value", text="Displacement MIX", slider=True)
                        else:
                            layout.operator("object.new_rainy_mix_node", text="Rainy", icon='MOD_FLUIDSIM')    
                else:
                    layout.operator("object.new_rainy_mix_node", text="Rainy", icon='MOD_FLUIDSIM')
            else:
                box = layout.box()
                row = box.row()
                row.label(text="Not There (Image Texture) in Base color!", icon='ERROR')



class kh_Randomize_Operator(bpy.types.Operator):
    bl_idname = "material.kh_randomize"
    bl_label = "Advanced Randomize UV"
    bl_description = "Advanced randomization system for materials with better distribution and less repetition"
    bl_options = {'REGISTER', 'UNDO'}

    # خصائص متقدمة للتحكم في التوزيع العشوائي
    scale_variation: bpy.props.FloatProperty(
        name="Scale Variation",
        description="Amount of scale variation between tiles",
        default=0.2,
        min=0.0,
        max=2.0,
        step=0.01
    )

    rotation_variation: bpy.props.FloatProperty(
        name="Rotation Variation",
        description="Amount of rotation variation between tiles",
        default=0.5,
        min=0.0,
        max=1.0,
        step=0.01
    )

    noise_scale: bpy.props.FloatProperty(
        name="Noise Scale",
        description="Scale of the noise pattern for randomization",
        default=5.0,
        min=0.1,
        max=50.0,
        step=0.1
    )

    detail_level: bpy.props.FloatProperty(
        name="Detail Level",
        description="Level of detail in the randomization pattern",
        default=2.0,
        min=0.1,
        max=10.0,
        step=0.1
    )

    roughness_variation: bpy.props.FloatProperty(
        name="Roughness Variation",
        description="Amount of roughness variation",
        default=0.3,
        min=0.0,
        max=1.0,
        step=0.01
    )

    distortion_strength: bpy.props.FloatProperty(
        name="Distortion Strength",
        description="Strength of UV distortion to reduce repetition",
        default=0.1,
        min=0.0,
        max=1.0,
        step=0.01
    )

    use_advanced_mode: bpy.props.BoolProperty(
        name="Advanced Mode",
        description="Enable advanced randomization features",
        default=True
    )

    def execute(self, context):
        try:
            script_dir = os.path.dirname(os.path.realpath(__file__))
            folder_path = os.path.join(script_dir, "asset", "Randomize.blend")
            blend_file_path = folder_path
            node_group_name = "KH-Randomize"

            # التحقق من وجود الكائن والمادة النشطة
            obj = context.active_object
            if not obj:
                self.report({'ERROR'}, "No active object selected")
                return {'CANCELLED'}

            material = obj.active_material
            if not material or not material.node_tree:
                self.report({'ERROR'}, "No active material with node tree found")
                return {'CANCELLED'}

            # البحث عن العقد المطلوبة
            node_tree = material.node_tree
            tex_coord_nodes = [node for node in node_tree.nodes if node.type == 'TEX_COORD']
            mapping_nodes = [node for node in node_tree.nodes if node.type == 'MAPPING']
            existing_randomize_groups = [node for node in node_tree.nodes
                                       if node.type == 'GROUP' and node.node_tree
                                       and node.node_tree.name.startswith("KH-Randomize")]

            # التحقق من وجود العقد المطلوبة
            if not tex_coord_nodes:
                # إنشاء Texture Coordinate node إذا لم يكن موجوداً
                tex_coord_node = node_tree.nodes.new('ShaderNodeTexCoord')
                tex_coord_node.location = (-800, 0)
                tex_coord_nodes = [tex_coord_node]

            if not mapping_nodes:
                # إنشاء Mapping node إذا لم يكن موجوداً
                mapping_node = node_tree.nodes.new('ShaderNodeMapping')
                mapping_node.location = (-600, 0)
                mapping_nodes = [mapping_node]

                # ربط Texture Coordinate مع Mapping
                node_tree.links.new(tex_coord_nodes[0].outputs['Generated'], mapping_node.inputs['Vector'])

            # معالجة الـ Randomize Group
            if existing_randomize_groups:
                # إذا كان موجوداً، قم بحذفه
                self._remove_randomize_group(node_tree, existing_randomize_groups[0])
                self.report({'INFO'}, "Randomize UV system removed")
            else:
                # إذا لم يكن موجوداً، قم بإضافته
                self._add_randomize_group(context, node_tree, tex_coord_nodes[0], mapping_nodes, blend_file_path, node_group_name)
                self.report({'INFO'}, "Advanced Randomize UV system added")

        except Exception as e:
            self.report({'ERROR'}, f"Error in randomize operation: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def _add_randomize_group(self, context, node_tree, tex_coord_node, mapping_nodes, blend_file_path, node_group_name):
        """إضافة مجموعة العقد للتوزيع العشوائي"""
        try:
            # تحميل node group من الملف
            with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
                if node_group_name in data_from.node_groups:
                    data_to.node_groups.append(node_group_name)
                else:
                    self.report({'WARNING'}, f"Node group '{node_group_name}' not found in asset file")
                    return

            # إنشاء node group جديد
            new_node_group = node_tree.nodes.new('ShaderNodeGroup')
            new_node_group.node_tree = bpy.data.node_groups[node_group_name]
            new_node_group.name = "KH-Randomize Advanced"
            new_node_group.label = "Advanced Randomize UV"

            # تحديد موقع العقدة
            new_node_group.location = (tex_coord_node.location.x + 300, tex_coord_node.location.y)

            # ربط العقد
            for mapping_node in mapping_nodes:
                # البحث عن الاتصالات الموجودة
                connected_socket = None
                for link in node_tree.links:
                    if link.to_node == mapping_node and link.to_socket.name == 'Vector':
                        connected_socket = link.from_socket
                        node_tree.links.remove(link)
                        break

                # ربط العقد الجديدة
                if connected_socket:
                    node_tree.links.new(connected_socket, new_node_group.inputs[0])
                else:
                    # ربط مع Generated إذا لم يكن هناك اتصال موجود
                    node_tree.links.new(tex_coord_node.outputs['Generated'], new_node_group.inputs[0])

                node_tree.links.new(new_node_group.outputs[0], mapping_node.inputs['Vector'])

            # تطبيق الإعدادات المتقدمة
            self._apply_advanced_settings(new_node_group)

        except Exception as e:
            self.report({'ERROR'}, f"Error adding randomize group: {str(e)}")

    def _remove_randomize_group(self, node_tree, randomize_group):
        """إزالة مجموعة العقد للتوزيع العشوائي"""
        try:
            # استعادة الاتصالات الأصلية
            input_socket = randomize_group.inputs[0] if randomize_group.inputs else None
            output_socket = randomize_group.outputs[0] if randomize_group.outputs else None

            from_socket = None
            output_links = []

            # البحث عن الاتصالات
            for link in node_tree.links:
                if link.to_node == randomize_group and input_socket and link.to_socket == input_socket:
                    from_socket = link.from_socket
                elif link.from_node == randomize_group and output_socket and link.from_socket == output_socket:
                    output_links.append(link.to_socket)

            # إعادة ربط الاتصالات
            if from_socket and output_links:
                for to_socket in output_links:
                    node_tree.links.new(from_socket, to_socket)

            # حذف العقدة
            node_tree.nodes.remove(randomize_group)

        except Exception as e:
            self.report({'ERROR'}, f"Error removing randomize group: {str(e)}")

    def _apply_advanced_settings(self, node_group):
        """تطبيق الإعدادات المتقدمة على مجموعة العقد"""
        try:
            if not node_group.inputs:
                return

            # تطبيق القيم المخصصة مع تحسينات الأداء
            input_mapping = {
                1: max(0.1, min(10.0, self.scale_variation)),      # Scale (محدود بين 0.1 و 10)
                2: max(0.1, min(100.0, self.noise_scale)),         # Noise Scale (محدود بين 0.1 و 100)
                3: max(0.0, min(1.0, self.rotation_variation)),    # Tile Rotation (محدود بين 0 و 1)
                4: max(0.1, min(20.0, self.detail_level)),         # Details (محدود بين 0.1 و 20)
                5: max(0.0, min(1.0, self.roughness_variation)),   # Roughness (محدود بين 0 و 1)
                6: max(0.0, min(2.0, self.distortion_strength))    # Distortion (محدود بين 0 و 2)
            }

            # تطبيق القيم مع التحقق من صحتها
            for index, value in input_mapping.items():
                if index < len(node_group.inputs) and node_group.inputs[index]:
                    try:
                        node_group.inputs[index].default_value = value
                    except (TypeError, ValueError) as e:
                        print(f"Warning: Could not set input {index} to {value}: {str(e)}")

            # تحسينات إضافية للأداء
            self._optimize_node_group_performance(node_group)

        except Exception as e:
            print(f"Error applying advanced settings: {str(e)}")

    def _optimize_node_group_performance(self, node_group):
        """تحسينات إضافية لأداء مجموعة العقد"""
        try:
            # تعيين اسم مميز للعقدة
            node_group.name = "KH-Randomize-Advanced"
            node_group.label = "Advanced UV Randomizer"

            # تحسين موقع العقدة لتجنب التداخل
            if hasattr(node_group, 'width'):
                node_group.width = 200

            # إضافة تلميحات للمستخدم
            if hasattr(node_group, 'description'):
                node_group.description = "Advanced UV randomization with optimized performance"

        except Exception as e:
            print(f"Warning: Could not apply performance optimizations: {str(e)}")

    def _validate_material_setup(self, material):
        """التحقق من صحة إعداد المادة للتوزيع العشوائي"""
        if not material or not material.node_tree:
            return False, "No valid material with node tree"

        node_tree = material.node_tree

        # التحقق من وجود العقد الأساسية
        has_principled = any(node.type == 'BSDF_PRINCIPLED' for node in node_tree.nodes)
        has_image_texture = any(node.type == 'TEX_IMAGE' for node in node_tree.nodes)

        if not has_principled:
            return False, "Material needs a Principled BSDF node"

        if not has_image_texture:
            return False, "Material needs at least one Image Texture node"

        return True, "Material setup is valid"

    def _get_optimal_settings_preset(self, preset_name="balanced"):
        """الحصول على إعدادات محسنة مسبقاً"""
        presets = {
            "subtle": {
                "scale_variation": 0.1,
                "rotation_variation": 0.2,
                "noise_scale": 3.0,
                "detail_level": 1.0,
                "roughness_variation": 0.1,
                "distortion_strength": 0.05
            },
            "balanced": {
                "scale_variation": 0.2,
                "rotation_variation": 0.5,
                "noise_scale": 5.0,
                "detail_level": 2.0,
                "roughness_variation": 0.3,
                "distortion_strength": 0.1
            },
            "strong": {
                "scale_variation": 0.4,
                "rotation_variation": 0.8,
                "noise_scale": 8.0,
                "detail_level": 4.0,
                "roughness_variation": 0.5,
                "distortion_strength": 0.2
            }
        }

        return presets.get(preset_name, presets["balanced"])

    def draw(self, context):
        """رسم واجهة المستخدم للإعدادات المتقدمة"""
        layout = self.layout

        # عنوان رئيسي
        layout.label(text="Advanced Randomize UV Settings", icon='UV_VERTEXSEL')
        layout.separator()

        # إعدادات مسبقة سريعة
        preset_box = layout.box()
        preset_row = preset_box.row()
        preset_row.label(text="Quick Presets:", icon='PRESET')

        preset_buttons = preset_box.row(align=True)
        preset_op = preset_buttons.operator("material.kh_randomize_preset", text="Subtle")
        preset_op.preset_name = "subtle"
        preset_op = preset_buttons.operator("material.kh_randomize_preset", text="Balanced")
        preset_op.preset_name = "balanced"
        preset_op = preset_buttons.operator("material.kh_randomize_preset", text="Strong")
        preset_op.preset_name = "strong"

        layout.separator()

        # تبديل الوضع المتقدم
        layout.prop(self, "use_advanced_mode", toggle=True)

        if self.use_advanced_mode:
            # تحكمات متقدمة
            advanced_box = layout.box()
            advanced_box.label(text="Advanced Controls:", icon='SETTINGS')

            # تحكمات أساسية
            basic_col = advanced_box.column()
            basic_col.label(text="Basic Parameters:")

            row = basic_col.row(align=True)
            row.prop(self, "scale_variation", text="Scale Var")
            row.prop(self, "rotation_variation", text="Rotation")

            row = basic_col.row(align=True)
            row.prop(self, "noise_scale", text="Noise")
            row.prop(self, "detail_level", text="Detail")

            # تحكمات متقدمة
            advanced_col = advanced_box.column()
            advanced_col.separator()
            advanced_col.label(text="Advanced Parameters:")

            row = advanced_col.row(align=True)
            row.prop(self, "roughness_variation", text="Roughness")
            row.prop(self, "distortion_strength", text="Distortion")

            # معلومات مفيدة
            info_box = layout.box()
            info_box.label(text="💡 Performance Tips:", icon='INFO')
            info_col = info_box.column(align=True)
            info_col.scale_y = 0.8
            info_col.label(text="• Lower values = Better performance")
            info_col.label(text="• Higher noise scale = More variation")
            info_col.label(text="• Distortion helps reduce repetition")
        else:
            # وضع بسيط
            simple_box = layout.box()
            simple_box.label(text="Simple Mode - Use Quick Presets Above", icon='CHECKMARK')


class kh_Randomize_Preset_Operator(bpy.types.Operator):
    """Apply preset settings for randomize UV system"""
    bl_idname = "material.kh_randomize_preset"
    bl_label = "Apply Randomize Preset"
    bl_description = "Apply predefined settings for optimal randomization"
    bl_options = {'REGISTER', 'UNDO'}

    preset_name: bpy.props.StringProperty(
        name="Preset Name",
        description="Name of the preset to apply",
        default="balanced"
    )

    def execute(self, context):
        try:
            # الحصول على المادة النشطة
            obj = context.active_object
            if not obj or not obj.active_material:
                self.report({'ERROR'}, "No active material found")
                return {'CANCELLED'}

            material = obj.active_material
            node_tree = material.node_tree

            # البحث عن مجموعة الـ Randomize
            randomize_group = None
            for node in node_tree.nodes:
                if (node.type == 'GROUP' and node.node_tree and
                    node.node_tree.name.startswith("KH-Randomize")):
                    randomize_group = node
                    break

            if not randomize_group:
                self.report({'WARNING'}, "No randomize system found. Add it first.")
                return {'CANCELLED'}

            # تطبيق الإعدادات المسبقة
            presets = {
                "subtle": {
                    1: 0.8,   # Scale
                    2: 3.0,   # Noise Scale
                    3: 0.2,   # Rotation
                    4: 1.0,   # Details
                    5: 0.1,   # Roughness
                    6: 0.05   # Distortion
                },
                "balanced": {
                    1: 1.0,   # Scale
                    2: 5.0,   # Noise Scale
                    3: 0.5,   # Rotation
                    4: 2.0,   # Details
                    5: 0.3,   # Roughness
                    6: 0.1    # Distortion
                },
                "strong": {
                    1: 1.5,   # Scale
                    2: 8.0,   # Noise Scale
                    3: 0.8,   # Rotation
                    4: 4.0,   # Details
                    5: 0.5,   # Roughness
                    6: 0.2    # Distortion
                }
            }

            if self.preset_name not in presets:
                self.report({'ERROR'}, f"Unknown preset: {self.preset_name}")
                return {'CANCELLED'}

            # تطبيق القيم
            preset_values = presets[self.preset_name]
            for index, value in preset_values.items():
                if index < len(randomize_group.inputs):
                    randomize_group.inputs[index].default_value = value

            self.report({'INFO'}, f"Applied '{self.preset_name}' preset successfully")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error applying preset: {str(e)}")
            return {'CANCELLED'}


class KH_Material_Panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_kh_material"
    bl_label = "KH-Material"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'KH-Material'
    @classmethod
    def poll(cls, context):
        KH = context.preferences.addons['KH-Tools'].preferences.KH_Material == True
        return context.active_object is not None and context.object.active_material is not None and KH
    
    def draw(self, context):
        layout = self.layout
        selected_object = bpy.context.active_object

        if selected_object is not None and selected_object.type == 'MESH' and selected_object.material_slots:
            obj = bpy.context.active_object
            mat_slot = obj.material_slots[obj.active_material_index]
            material = mat_slot.material
            box = layout.box()
            row = box.row()
            
            obj = context.object
            if obj is not None and obj.type == 'MESH' and obj.active_material is not None:
                material = obj.active_material
                mat = obj.active_material
                if mat is not None and mat.node_tree is not None:
                    if material.use_nodes and material.node_tree:
                        coloring_found = False
                        box = layout.box()
                        for node in material.node_tree.nodes:
                            if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Coloring"):
                                coloring_found = True
                                row.operator("object.coloring_delete_node", text="Coloring", icon='TRASH')
                                break
                        if not coloring_found:
                            row.operator("object.add_mix_node", text="Coloring", icon='COLORSET_04_VEC')
            row = box.row()
            row.operator("object.kh_mapping", text="Mapping", icon='EVENT_M')

            row = box.row()
            row.operator("object.add_bump", text="Bump", icon='COLORSET_13_VEC')
            row.operator("object.normal_map", text="Normal", icon='COLORSET_11_VEC')
            row = box.row()
            row.operator("object.ramp_map", text="Ramp", icon='EVENT_R')
            row.operator("object.invert_map", text="Invert", icon='EVENT_I')
            row = box.row()
            row.operator("object.kh_bevel", text="Bevel", icon='EVENT_B')
            
            row.operator("object.add_ambient_node", text="AO", icon='META_CUBE')
            
            layout = self.layout
            layout.operator("object.add_bump_roughness_operator", text="Bump / Roughness", icon='EVENT_B')
            
            layout.operator("material.add_mix_cheddar", text="Light Path", icon='ANIM')             
            layout.operator("material.plant_operator", text="Plant Leaves", icon='STRANDS')
            
            # نظام التوزيع العشوائي المتقدم
            randomize_box = layout.box()
            randomize_row = randomize_box.row()
            randomize_row.label(text="Advanced Randomize System", icon='UV_VERTEXSEL')

            group_node = next((node for node in material.node_tree.nodes if node.type == 'GROUP' and node.node_tree and node.node_tree.name.startswith("KH-Randomize")), None)
            if group_node:
                randomize_row = randomize_box.row()
                randomize_row.scale_y = 1.2
                randomize_row.operator("material.kh_randomize", text="Remove Advanced Randomize", icon='TRASH')
            else:
                randomize_row = randomize_box.row()
                randomize_row.scale_y = 1.2
                randomize_row.operator("material.kh_randomize", text="Add Advanced Randomize", icon='ADD')
            
            box = layout.box()
            row = box.row()
            row.operator("object.fix_glass_curtains", icon='MODIFIER') 
            obj = context.object
            if obj and obj.type == 'MESH' and "Solidify" in obj.modifiers:
                solidify_modifier = obj.modifiers["Solidify"]
                row = box.row()
                row.prop(solidify_modifier, "thickness")
                row = box.row()
                row.prop(solidify_modifier, "offset")
                row = box.row()
                row.prop(solidify_modifier, "use_rim")
                row = box.row()
                row.prop(solidify_modifier, "use_rim_only")
            else:
                pass  
        else:
            layout.label(text="No materials or invalid object selected.")

# Coloring Control///////////////////////////////////////////////////////////////////////////////////////////////////////////////

class ColoringControlsPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_idname = "OBJECT_PT_Coloring"
    bl_region_type = "UI"
    bl_category = "KH-Tools"
    bl_label = "Material"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id   = "OBJECT_PT_tools_material"
    
    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="",  icon_value=preview_collection['16.png'].icon_id)
        except KeyError:
            pass
  
    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj is not None and obj.type == 'MESH' and obj.active_material is not None:
            material = obj.active_material
            mat = obj.active_material
            if mat is not None and mat.node_tree is not None:
                if material.use_nodes and material.node_tree:
                    coloring_found = False
                    box = layout.box()
                    for node in material.node_tree.nodes:
                        if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Coloring"):
                            coloring_found = True
                            row = box.row()
                            row.scale_y=1.3
                            row.operator("object.coloring_delete_node", text="Coloring", icon='TRASH')
                            row = box.row()
                            row.prop(node.inputs[1], "default_value", text="Color", icon='COLORSET_04_VEC')
                            row = box.row()
                            row.prop(node.inputs[2], "default_value", text="Saturation")
                            row = box.row()
                            row.prop(node.inputs[3], "default_value", text="Strength")
                            row = box.row()
                            row.prop(node.inputs[4], "default_value", text="Brightness")
                            box = layout.box()
                            break  

                    if not coloring_found:
                        row = box.row()
                        row.scale_y=1.3
                        row.operator("object.add_mix_node", text="Coloring", icon='COLORSET_04_VEC')
                     
                    Bevel_found = False   
                    for node in material.node_tree.nodes:
                        if node.type == 'BEVEL':
                            Bevel_found = True
                            box = layout.box()
                            row = box.row()
                            row.scale_y=1.3
                            row.operator("object.kh_bevel", text="Bevel", icon='TRASH')
                            row = box.row()
                            row.prop(node, "samples", text="Samples")
                            row = box.row()
                            row.prop(node.inputs[0], "default_value", text="Radius")
                            box = layout.box()
                            break  
                    if not Bevel_found:
                        box = layout.box()
                        row = box.row()
                        row.scale_y=1.3
                        row.operator("object.kh_bevel", text="Bevel", icon='EVENT_B')
                        
                        
                    
                    selected_object = bpy.context.active_object
                    if selected_object:
                        if selected_object.material_slots:
                            material_slots = selected_object.material_slots
                    obj = bpy.context.active_object
                    if obj is not None and obj.type == 'MESH' and obj.active_material is not None:
                        if obj.material_slots and obj.active_material_index < len(obj.material_slots):
                            mat_slot = obj.material_slots[obj.active_material_index]
                            material = mat_slot.material
                            active_material = bpy.context.active_object.active_material 
                    else:
                        box = layout.box()
                        row = box.row()
                        row.label(text="There is no active material.", icon='ERROR') 

                    obj = context.object
                    # = obj.active_material
                    obj = bpy.context.active_object
                    if obj is not None and obj.type == 'MESH' and obj.active_material is not None:
                        material = obj.active_material
                        node_tree = material.node_tree
                        nodes = node_tree.nodes
                        bsdf_principled = None
                        base_color_node = None
                        mat_output = None
                        for node in nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                bsdf_principled = node
                                color_input = node.inputs.get("Base Color")
                                if color_input and color_input.is_linked:
                                    base_color_node = color_input.links[0].from_node
                                break
                        if bsdf_principled and base_color_node:
                            if "KH-Rainy" in bpy.data.node_groups:
                                active_material = bpy.context.active_object.active_material
                                if active_material and active_material.use_nodes:
                                    node_tree = active_material.node_tree
                                    rainy_group_node = None
                                    for node in node_tree.nodes:
                                        if node.type == 'GROUP' and node.node_tree.name.startswith("KH-Rainy"):
                                            rainy_group_node = node
                                            break
                                    if rainy_group_node:
                                        box = layout.box()
                                        row = box.row()
                                        row.scale_y=1.3
                                        row.operator("object.rainy_delete_node", text="Delete Rain", icon='TRASH')
                                        row = box.row()
                                
                                        # عرض المدخل
                                        row.prop(rainy_group_node.inputs.get("Water Color"), "default_value", text="Water Color")
                                        row = box.row()
                                        row.prop(rainy_group_node.inputs.get("Dirty"), "default_value", text="Roughness Intensity", slider=True)
                                        row = box.row()
                                        row.prop(rainy_group_node.inputs.get("Scale"), "default_value", text="Scale", slider=True)
                                        row = box.row()
                                        row.prop(rainy_group_node.inputs.get("Density"), "default_value", text="Density", slider=True)
                                        row = box.row()
                                        row.prop(rainy_group_node.inputs.get("Detail"), "default_value", text="Detail", slider=True)
                                        row = box.row()
                                        row.prop(rainy_group_node.inputs.get("Distortion"), "default_value", text="Distortion", slider=True)
                                        row = box.row()
                                        row.prop(rainy_group_node.inputs.get("Lacunarity"), "default_value", text="Lacunarity", slider=True)
                                        row = box.row()
                                        row.prop(rainy_group_node.inputs.get("Sharpness"), "default_value", text="Sharpness", slider=True)

                                        box = layout.box()
                                        active_material = context.active_object.active_material
                                        nodes = active_material.node_tree.nodes   
                                        bsdf_node = None 
                                        NORMAL_node = None 
                                        Bump_node = None    
                                        DISPLAC_node = None 
                                        
                                        for node in nodes: 
                                            if node.type == 'BSDF_PRINCIPLED':
                                                bsdf_node = node 
                                        if bsdf_node is not None:
                                            if bsdf_node:
                                                if 'Specular' in bsdf_node.inputs:
                                                    row = box.row()
                                                    row.prop(bsdf_node.inputs['Specular'], "default_value", text="Reflection")
                                                else:
                                                    row = box.row()
                                                    row.prop(bsdf_node.inputs['Specular IOR Level'], "default_value", text="Reflection")

                                        for node in nodes: 
                                            if node.type == 'NORMAL_MAP':
                                                NORMAL_node = node 

                                        if NORMAL_node is not None:
                                            row = box.row()
                                            row.prop(NORMAL_node.inputs[0], "default_value", text="Normal", slider=True)
                                            row = box.row()
                                            row.prop(rainy_group_node.inputs.get("Normal MIX"), "default_value", text="Normal MIX", slider=True)
                                            
                                        for node in nodes: 
                                            if node.type == 'BUMP':
                                                Bump_node = node 

                                        if Bump_node is not None:
                                            row = box.row()
                                            row.prop(Bump_node.inputs[0], "default_value", text="Bump")
                                            row = box.row()
                                            row.prop(rainy_group_node.inputs.get("Bump MIX"), "default_value", text="Bump MIX", slider=True)
                                            
                                        for node in nodes: 
                                            if node.type == 'DISPLACEMENT':
                                                DISPLAC_node = node 

                                        if DISPLAC_node is not None:
                                            row = box.row()
                                            row.prop(DISPLAC_node.inputs[2], "default_value", text="Displacement")
                                            row = box.row()
                                            row.prop(rainy_group_node.inputs.get("Displacement MIX"), "default_value", text="Displacement MIX", slider=True)
                                    else:
                                        box = layout.box()
                                        row = box.row()
                                        row.scale_y=1.3
                                        row.operator("object.new_rainy_mix_node", text="Rainy", icon='MOD_FLUIDSIM')    
                            else:
                                box = layout.box()
                                row = box.row()
                                row.scale_y=1.3
                                row.operator("object.new_rainy_mix_node", text="Rainy", icon='MOD_FLUIDSIM')
                        else:
                            box = layout.box()
                            row = box.row()
                            row.scale_y=1.3
                            row.operator("object.new_rainy_mix_node", text="Rainy", icon='MOD_FLUIDSIM') 
                            #row.label(text="Not There (Image Texture) in Base color!", icon='ERROR')
                            
                        #KH-Randomize
                        group_node = next((node for node in material.node_tree.nodes if node.type == 'GROUP' and node.node_tree and node.node_tree.name.startswith("KH-Randomize")), None)
                        if group_node:
                            box = layout.box()
                            # عنوان القسم
                            row = box.row()
                            row.label(text="Advanced Randomize UV System", icon='UV_VERTEXSEL')

                            # زر الحذف
                            row = box.row()
                            row.scale_y=1.3
                            row.operator("material.kh_randomize", text="Remove Randomize System", icon='TRASH')

                            # تحكمات أساسية
                            col = box.column()
                            col.label(text="Basic Controls:", icon='SETTINGS')

                            row = col.row(align=True)
                            row.prop(group_node.inputs[1], "default_value", text="Scale")
                            row.prop(group_node.inputs[2], "default_value", text="Noise Scale")

                            row = col.row(align=True)
                            row.prop(group_node.inputs[3], "default_value", text="Rotation")
                            row.prop(group_node.inputs[4], "default_value", text="Details")

                            # تحكمات متقدمة
                            col.separator()
                            col.label(text="Advanced Controls:", icon='MODIFIER')

                            row = col.row(align=True)
                            row.prop(group_node.inputs[5], "default_value", text="Roughness")
                            row.prop(group_node.inputs[6], "default_value", text="Distortion")

                        else:
                            box = layout.box()
                            # زر الإضافة
                            row = box.row()
                            row.scale_y=1.5
                            row.operator("material.kh_randomize", text="Randomize UV", icon='ADD')

        else:
            box = layout.box()
            row = box.row()
            row.label(text="There is no active material.", icon='ERROR') 
            


class PreviewPanel(bpy.types.Panel):
    bl_label = "Material preview"
    bl_idname = "OBJECT_PT_material_preview"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = 'KH-Material'

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
        return KH and context.active_object is not None and context.object.active_material is not None
    def draw(self, context):
        ob = context.active_object
        self.layout.template_ID_preview(ob, "active_material")
        
        
#Image Preview
class VIEW3D_PT_preview_image(Panel):
    bl_label = "Image Preview"
    bl_idname = "OBJECT_PT_preview_image"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'KH-Material'
    bl_context = "shader"
    @classmethod
    def poll(cls, context):
        KH = context.preferences.addons['KH-Tools'].preferences.KH_Material == True
        return KH

    def draw(self, context):
        layout = self.layout
        if context.active_object and context.active_object.active_material:
            selected_node = context.active_node
            if selected_node and selected_node.type == 'TEX_IMAGE':
                box = layout.box()
                box.template_ID_preview(selected_node, "image")
            else:
                layout.label(text="Select a TEX_IMAGE node")
        else:
            layout.label(text="Select an object with an active material")

       
classes = ( ## KH-Material////////////////////////////////////////////////////////////////////////
            PreviewPanel,
            VIEW3D_PT_preview_image,
            KH_tools_Material,
            KH_Material_Panel,
            ColoringControlsPanel,
            MappingControlsPanel,
            DisplsPanel,
            kh_Basic_materials_ControlsPanel,
            
            Add_Color_Operator,
            Delete_Coloring_Operator,
            leavesOperator,
            
            AddBumpRoughnessOperator,
            AddMixCheddarOperator,
            AmbientNodeOperator,
            FixGlassCurtainsOperator,
            Add_bump_node_Operator,
            NORMAL_MAPOperator, 
            RAMP_MAPOperator,
            Invert_MAPOperator,
            kh_add_MAPPING_Operator,
            Bevel_Operator,
            RainyDeleteOperator,
            #RainyPanel,  
            new_RainyOperator, 
            ActivateNodeWranglerOperator, 
            kh_show_previewOperator,
            
            
            KHM_GlassOperator,
            KHM_Water_CausticsOperator,
            KHM_MetalOperator,
            KHM_Car_paintOperator,
            KHM_SteellOperator,
            KHM_GoldOperator,
            KHM_PaintOperator,
            KHM_CurtainOperator,
            KHM_PlasticOperator,
            KHM_LEDOperator,
            KHM_GroundOperator,
            KHM_WoodOperator,
            KHM_ConcreteOperator,
            KHM_MarbleOperator,
            KHM_FabricOperator,
            KHM_PoolTileOperator,
            KHM_AsphaltOperator,
            ThicknessGlassCurtainsOperator,
            
            CustomOperator,
            
            
            AddCubeAtCursorOperator,
            DeleteScaleTextureOperator,
            MakeSingleUserMaterialOperator,
            TEX_COORD_Object,
            TEX_COORD_UV,
            TEX_COORD_Generated,

            AddDisplaceModifier,
            OBJECT_OT_RemoveSubdivisionModifier,
            OBJECT_OT_AddTriangulateModifier,
            OBJECT_OT_RemoveTriangulateModifier,
            
            kh_Randomize_Operator,
            kh_Randomize_Preset_Operator,

            MATERIAL_PT_active_properties_submenu,
            MATERIAL_OT_enable_nodes,
                )

def register():
    for i in classes:
        register_class(i)
    ## KH-Material////////////////////////////////////////////////////////////////////////
    bpy.types.Scene.my_uv_type = bpy.props.EnumProperty(
        items=[('UV', 'UV', 'UV'),
               ('NORMAL', 'Normal', 'Normal')],
        default='UV',
        description="Choose UV Type"
    )
    bpy.types.NODE_MT_editor_menus.append(kh_activate_node_wrangler)
        


def unregister():
    for i in classes:
        unregister_class(i)
    ## KH-Material////////////////////////////////////////////////////////////////////////
    bpy.types.NODE_MT_editor_menus.remove(kh_activate_node_wrangler)
    # التحقق من وجود الخاصية قبل حذفها لتجنب الأخطاء
    if hasattr(bpy.types.Scene, 'my_uv_type'):
        del bpy.types.Scene.my_uv_type



if __name__ == "__main__":
        register()
     
    
   






