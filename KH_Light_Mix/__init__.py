from ast import Not
from enum import auto
import bpy
from bpy.app.handlers import persistent
import  os
from .Post_Production import *
from .Export_exr import*

light_mix_folder = os.path.dirname(os.path.realpath(__file__))
LGB_VERSION = 1
lightgroup_blending_grp_name = 'Light Group Blending v' + str(LGB_VERSION)

# Helper function for Blender 5.0+ compositing node tree compatibility
def get_scene_compositor(scene):
    """Get compositor node tree with Blender 5.0+ compatibility
    Note: Returns None if compositor doesn't exist - caller should handle this"""
    if bpy.app.version >= (5, 0, 0):
        # Blender 5.0+: use compositing_node_group
        return scene.compositing_node_group
    else:
        # Blender 4.x and earlier: use scene.node_tree
        if scene.use_nodes:
            return scene.node_tree
        return None

def create_scene_compositor(scene):
    """Create compositor node tree with Blender 5.0+ compatibility
    Use this in operators/execute methods where we can write to scene"""
    if bpy.app.version >= (5, 0, 0):
        # Blender 5.0+: create compositing_node_group if needed
        if not scene.compositing_node_group:
            tree = bpy.data.node_groups.new("Compositor", "CompositorNodeTree")
            scene.compositing_node_group = tree
            # Add default nodes
            rlayers = tree.nodes.new(type="CompositorNodeRLayers")
            output = tree.nodes.new(type='NodeGroupOutput')
            # Create output socket
            if not tree.interface.items_tree:
                tree.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
            rlayers.location = (-300, 0)
            output.location = (300, 0)
            if len(output.inputs) > 0:
                tree.links.new(rlayers.outputs["Image"], output.inputs[0])
        return scene.compositing_node_group
    else:
        # Blender 4.x and earlier
        if not scene.use_nodes:
            scene.use_nodes = True
        return scene.node_tree

def get_or_create_output_node(tree, nodes):
    """Get or create output node (Composite or GroupOutput depending on Blender version)"""
    if bpy.app.version >= (5, 0, 0):
        # Blender 5.0: Look for NodeGroupOutput
        for node in nodes:
            if node.type == 'GROUP_OUTPUT':
                return node
        # Create if not found
        output = nodes.new('NodeGroupOutput')
        if not tree.interface.items_tree:
            tree.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
        return output
    else:
        # Blender 4.x: Use CompositorNodeComposite
        if 'Composite' in nodes:
            return nodes['Composite']
        return nodes.new('CompositorNodeComposite')

def set_denoise_prefilter(denoise_node, prefilter_value):
    """Set denoise prefilter with Blender 5.0+ compatibility (options as inputs)"""
    if bpy.app.version >= (5, 0, 0):
        # Blender 5.0: prefilter is an input, enum values are 'None', 'Fast', 'Accurate'
        if 'Prefilter' in denoise_node.inputs:
            # Convert old enum values to new ones
            prefilter_map = {
                'FAST': 'Fast',
                'ACCURATE': 'Accurate',
                'NONE': 'None',
                'Fast': 'Fast',
                'Accurate': 'Accurate',
                'None': 'None'
            }
            mapped_value = prefilter_map.get(prefilter_value, prefilter_value)
            denoise_node.inputs['Prefilter'].default_value = mapped_value
    else:
        # Blender 4.x: prefilter is a property
        if hasattr(denoise_node, 'prefilter'):
            denoise_node.prefilter = prefilter_value

def set_switch_check(switch_node, check_value):
    """Set switch check with Blender 5.0+ compatibility (options as inputs)"""
    if bpy.app.version >= (5, 0, 0):
        # Blender 5.0: check is an input named 'Switch'
        if 'Switch' in switch_node.inputs:
            switch_node.inputs['Switch'].default_value = check_value
        elif 'Check' in switch_node.inputs:
            switch_node.inputs['Check'].default_value = check_value
        elif len(switch_node.inputs) > 0:
            # Fallback to index 0 as it's typically the boolean input
            switch_node.inputs[0].default_value = check_value
    else:
        # Blender 4.x: check is a property
        if hasattr(switch_node, 'check'):
            switch_node.check = check_value

def get_switch_check(switch_node):
    """Get switch check with Blender 5.0+ compatibility (options as inputs)"""
    if bpy.app.version >= (5, 0, 0):
        # Blender 5.0: check is an input named 'Switch'
        if 'Switch' in switch_node.inputs:
            return switch_node.inputs['Switch'].default_value
        elif 'Check' in switch_node.inputs:
            return switch_node.inputs['Check'].default_value
        elif len(switch_node.inputs) > 0:
            return switch_node.inputs[0].default_value
        return False
    else:
        # Blender 4.x: check is a property
        if hasattr(switch_node, 'check'):
            return switch_node.check
        return False

bl_info = {
        "name": "KH-Light Mix",
    "author": "Khaled Alnwesary",
    "version": (0, 6),
    "blender": (4, 00, 0),
    "location": "Image Editor > UI",
    "description": "",
    "warning": "",
    "doc_url": "",
    "category": "KH",
}



#Activate Compositing //////////////////////////////////////////////////////////////////////////////////////////
'''def switch_to_workspace(scene):
        if scene.light_mix_enabled:
            target_workspace = "Compositing"
            main_window = bpy.context.window_manager.windows[0]
            main_window.workspace = bpy.data.workspaces[target_workspace]

@persistent
def Compositor_handler(scene):
    if scene.light_mix_enabled:
        switch_to_workspace(scene)'''
        

              

def Aoto_light_mix(scene):
    if scene.light_mix_enabled:
        if scene.depsgraph_load_post:
            active_camera_name = bpy.context.scene.camera.name
            if active_camera_name != getattr(render_pre_Aoto_light_mix, "prev_active_camera_name", None):
                render_pre_Aoto_light_mix.prev_active_camera_name = active_camera_name 
                bpy.ops.view3d.update_light_group()
                return {'FINISHED'}
    

@persistent
def render_pre_Aoto_light_mix(dummy):
    Aoto_light_mix(bpy.context.scene)   

#///////////////////////////////////////////////////////////////////////////
def auto_delet_mix(scene):
    if scene.light_mix_enabled:
        if scene.depsgraph_load_post:
            active_camera_name = bpy.context.scene.camera.name
            if active_camera_name != getattr(render_pre_auto_delet_light_mix, "prev_active_camera_name", None):
                render_pre_auto_delet_light_mix.prev_active_camera_name = active_camera_name 
                bpy.ops.view3d.auto_delet_light_mix()
                return {'FINISHED'} 

@persistent
def render_pre_auto_delet_light_mix(dummy):
    auto_delet_mix(bpy.context.scene)  



class CompositorOperator(bpy.types.Operator):
    bl_idname = "object.compositor"
    bl_label = "Activate Compositor"

    def execute(self, context):
        target_workspace = "Compositing"
        if target_workspace in bpy.data.workspaces:
            main_window = bpy.context.window_manager.windows[0]
            main_window.workspace = bpy.data.workspaces[target_workspace]
        else :
             bpy.ops.wm.window_new()
             window = bpy.context.window_manager.windows[-1]
             bpy.context.area.ui_type = 'CompositorNodeTree'
        return {'FINISHED'}




def lightmix_Compositor():
    bpy.context.scene.view_layers[0].cycles.denoising_store_passes = True
    scene = bpy.context.scene
    
    # Use compatibility helper - create if needed
    node_tree = create_scene_compositor(scene)
    nodes = node_tree.nodes
    
    if 'Render Layers' not in nodes:
        r_layers = nodes.new('CompositorNodeRLayers')
        r_layers.location = (-1200, 0)
    else:
        r_layers = nodes['Render Layers']
        r_layers.location = (-1200, 0)
    
    # Get or create output node (Composite or GroupOutput depending on Blender version)
    composite = get_or_create_output_node(node_tree, nodes)
    composite.location = (200, 0)
    
    # Link Render Layers to output
    links = node_tree.links
    if bpy.app.version >= (5, 0, 0):
        # Blender 5.0+: Use first input of NodeGroupOutput
        if len(composite.inputs) > 0 and not composite.inputs[0].links:
            links.new(r_layers.outputs['Image'], composite.inputs[0])
    else:
        # Blender 4.x: Use Image input of Composite
        if 'Image' in composite.inputs and not composite.inputs['Image'].links:
            links.new(r_layers.outputs['Image'], composite.inputs['Image'])



def collection_children():
    for collection in bpy.data.collections:
        if collection.children:
            for sub_collection in collection.children:
                if not collection.hide_render: 
                    for obj in sub_collection.objects:
                        if not  sub_collection.hide_render:
                            if obj.type == 'LIGHT' and not obj.hide_render:                 
                                if obj.data.users >1:
                                    collection_name = sub_collection.name
                                    original_name = "C-" + collection_name + " / " + obj.data.name
                                    light_group_name = original_name.replace('.', '_')
                                    obj.lightgroup = ""
                                    bpy.ops.scene.view_layer_add_lightgroup(name=light_group_name)
                                    obj.lightgroup = light_group_name

                                                                    
                    # for obj in collection.objects:
                    #     if obj.type == 'LIGHT' and not obj.hide_render :            
                    #         if obj.data.users >1:
                    #             collection_name = collection.name     
                    #             original_name = collection_name + " / " + obj.data.name
                    #             light_group_name = original_name.replace('.', '_')
                    #             bpy.ops.scene.view_layer_add_lightgroup(name=light_group_name)
                    #             obj.lightgroup = light_group_name

                    #         if obj.data.users == 1:
                    #             collection_name = collection.name
                    #             original_name = "1-" + collection_name + " / " + obj.data.name
                    #             light_group_name = original_name.replace('.', '_')
                    #             bpy.ops.scene.view_layer_add_lightgroup(name=light_group_name)
                    #             obj.lightgroup = light_group_name

def object1():
    for collection in bpy.data.collections:
        if collection.children:
            for sub_collection in collection.children:
                if not collection.hide_render: 
                    for obj in sub_collection.objects:
                        if not  sub_collection.hide_render:
                            if obj.type == 'LIGHT' and not obj.hide_render: 
                                                
                                if obj.data.users == 1:
                                    collection_name = sub_collection.name
                                    original_name = "1-" + collection_name + " / " + obj.data.name
                                    light_group_name = original_name.replace('.', '_')
                                    obj.lightgroup = ""
                                    bpy.ops.scene.view_layer_add_lightgroup(name=light_group_name)
                                    obj.lightgroup = light_group_name
    
    
    all_objects = [obj for obj in bpy.data.objects if obj.type == 'LIGHT' and not obj.hide_render]
    for obj in all_objects:
        light_collection = obj.users_collection[0].name if obj.users_collection and not obj.users_collection[0].hide_render else None
        if light_collection in bpy.context.scene.collection.children.keys() :             
                if obj.data.users == 1:
                    collection_name = obj.users_collection[0].name
                    original_name = "1-" + collection_name + " / " + obj.data.name
                    light_group_name = original_name.replace('.', '_')
                    obj.lightgroup = ""
                    bpy.ops.scene.view_layer_add_lightgroup(name=light_group_name)
                    obj.lightgroup = light_group_name
                                    
                                    
def collection_Main():
    all_objects = [obj for obj in bpy.data.objects if obj.type == 'LIGHT' and not obj.hide_render]
    for obj in all_objects:        
        if obj.type == 'LIGHT' and obj.users_collection:
          if obj.users_collection[0] == bpy.context.scene.collection:
            if obj.data.users >1:
                collection_name = "Main"
                original_name = "C-" + collection_name + " / " + obj.data.name
                light_group_name = original_name.replace('.', '_')
                obj.lightgroup = ""
                bpy.ops.scene.view_layer_add_lightgroup(name=light_group_name)
                obj.lightgroup = light_group_name

            if obj.data.users == 1:
                collection_name = "Main"
                original_name = "1-" + collection_name + " / " + obj.data.name
                light_group_name = original_name.replace('.', '_')
                obj.lightgroup = ""
                bpy.ops.scene.view_layer_add_lightgroup(name=light_group_name)
                obj.lightgroup = light_group_name
            
def collection1():
    all_objects = [obj for obj in bpy.data.objects if obj.type == 'LIGHT' and not obj.hide_render]
    for obj in all_objects:
        light_collection = obj.users_collection[0].name if obj.users_collection and not obj.users_collection[0].hide_render else None
        if light_collection in bpy.context.scene.collection.children.keys() :             
                if obj.data.users > 1:
                    collection_name = obj.users_collection[0].name
                    original_name = "C-" + collection_name + " / " + obj.data.name
                    light_group_name = original_name.replace('.', '_')
                    obj.lightgroup = ""
                    bpy.ops.scene.view_layer_add_lightgroup(name=light_group_name)
                    obj.lightgroup = light_group_name

                                    


def add_lightgroup():
    if bpy.context.scene.world :
        active_world_name = bpy.context.scene.world.name
        bpy.ops.scene.view_layer_add_lightgroup(name="World")
        bpy.context.scene.world.lightgroup = "World"
    
    collection_children() 
    collection1()
    object1()
    collection_Main()
    # all_objects = [obj for obj in bpy.data.objects if obj.type == 'LIGHT' and not obj.hide_render]
    # for obj in all_objects:
    #     if obj.users_collection and obj.users_collection[0].hide_render:
    #         continue
   
    #     if obj.data.users >1:
    #         collection_name = "Main"
    #         for collection in bpy.data.collections:
    #             if obj.name in collection.objects:
    #                 collection_name = collection.name
    #                 break
    #         original_name = collection_name + " / " + obj.data.name
    #         light_group_name = original_name.replace('.', '_')
    #         bpy.ops.scene.view_layer_add_lightgroup(name=light_group_name)
    #         obj.lightgroup = light_group_name

    #     if obj.data.users == 1:
    #         collection_name = "Main"
    #         for collection in bpy.data.collections:
    #             if obj.name in collection.objects:
    #                 collection_name = collection.name
    #                 break
    #         original_name = "1-" + collection_name + " / " + obj.data.name
    #         light_group_name = original_name.replace('.', '_')
    #         bpy.ops.scene.view_layer_add_lightgroup(name=light_group_name)
    #         obj.lightgroup = light_group_name
                                        
                                    

    # all_MESH = [obj for obj in bpy.data.objects if obj.type == 'MESH' and (
    # any(node.type == 'BSDF_PRINCIPLED' for mat_slot in obj.material_slots for node in mat_slot.material.node_tree.nodes) or
    # any(node.type == 'EMISSION' for mat_slot in obj.material_slots for node in mat_slot.material.node_tree.nodes)
    # )]
    all_MESH = [obj for obj in bpy.data.objects if obj.type == 'MESH' and (
    any(node.type == 'BSDF_PRINCIPLED' for mat_slot in obj.material_slots if mat_slot.material for node in (mat_slot.material.node_tree.nodes if mat_slot.material.node_tree else [])) or
    any(node.type == 'EMISSION' for mat_slot in obj.material_slots if mat_slot.material for node in (mat_slot.material.node_tree.nodes if mat_slot.material.node_tree else []))
    )]
    for obj in all_MESH:
        if obj.hide_render or (obj.users_collection and obj.users_collection[0].hide_render):
            continue 

    #for obj in all_MESH:
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
                                        #if principled_bsdf.inputs[27].default_value != 0:
                                        if principled_bsdf.inputs["Emission Strength"].default_value != 0:
                                            #original_material_name = material.name +" / " + obj.data.name
                                            original_material_name = (material.name[:25] if len(material.name) > 25 else material.name) + " / " + (obj.data.name[:15] if len(obj.data.name) > 15 else obj.data.name) 
                                            cleaned_material_name = "M-"+original_material_name.replace('.', '_')
                                            obj.lightgroup = ""
                                            bpy.ops.scene.view_layer_add_lightgroup(name=cleaned_material_name)
                                            obj.lightgroup = cleaned_material_name
                                else:
                                    emission_input = bsdf_node.inputs['Emission']
                                    if tuple(principled_bsdf.inputs["Emission"].default_value) != (0, 0, 0, 1) or emission_input.is_linked:
                                        if principled_bsdf.inputs["Emission Strength"].default_value != 0:
                                            original_material_name = material.name +" / " + obj.data.name
                                            cleaned_material_name = "M-"+original_material_name.replace('.', '_')
                                            obj.lightgroup = ""
                                            bpy.ops.scene.view_layer_add_lightgroup(name=cleaned_material_name)
                                            obj.lightgroup = cleaned_material_name
                                                        
                    
                    emission = None             
                    if material.use_nodes:
                        for node in material.node_tree.nodes:
                            if node.type == 'EMISSION':
                                emission = node
                                break            
                    if emission:
                        if tuple(emission.inputs[0].default_value) != (0, 0, 0, 1) or emission.inputs[0].is_linked :
                            if emission.inputs[1].default_value != 0:
                                original_material_name = (material.name[:25] if len(material.name) > 25 else material.name) + " / " + (obj.data.name[:15] if len(obj.data.name) > 15 else obj.data.name) 
                                cleaned_material_name = "M-"+original_material_name.replace('.', '_')
                                obj.lightgroup = ""
                                bpy.ops.scene.view_layer_add_lightgroup(name=cleaned_material_name)
                                obj.lightgroup = cleaned_material_name
                                
                                
    bpy.ops.scene.view_layer_remove_unused_lightgroups()
        

def add_lightmix_nodes(self, context):
    scene = bpy.context.scene
    node_tree = create_scene_compositor(scene)
    nodes = node_tree.nodes
    links = node_tree.links 

    # Get or create output node (different types for Blender 5.0+)
    if bpy.app.version >= (5, 0, 0):
        # Blender 5.0: Look for NodeGroupOutput
        composite_node = None
        for node in nodes:
            if node.type == 'GROUP_OUTPUT':
                composite_node = node
                break
        if not composite_node:
            composite_node = nodes.new('NodeGroupOutput')
            if not node_tree.interface.items_tree:
                node_tree.interface.new_socket(name="Image", in_out='OUTPUT', socket_type='NodeSocketColor')
    else:
        # Blender 4.x: Use CompositorNodeComposite
        if 'Composite' not in nodes:
            composite_node = nodes.new('CompositorNodeComposite')
        else:
            composite_node = nodes['Composite']
    if composite_node:
        # nodes already defined above
        if 'Render Layers' not in nodes:
            r_layers = nodes.new('CompositorNodeRLayers')
            r_layers.location = (-1200, 0)
        else:
            r_layers = nodes['Render Layers']
            r_layers.location = (-1200, 0)

        denoise_node = nodes.new("CompositorNodeDenoise")
        denoise_node.location = (-350, -100)
        set_denoise_prefilter(denoise_node, 'FAST')
        denoise_node.label = "Denoise Light Mix"
        #denoise_node.mute = True

        Switch = nodes.new('CompositorNodeSwitch')
        Switch.label = "Switch Light Mix"
        Switch.location = (-200, 0)
        set_switch_check(Switch, False)
        
        # Use compatibility for Denoise node inputs
        if 'Image' in denoise_node.inputs:
            links.new(r_layers.outputs["Image"], denoise_node.inputs["Image"])
        else:
            links.new(r_layers.outputs["Image"], denoise_node.inputs[0])
            
        if 'Normal' in denoise_node.inputs:
            links.new(r_layers.outputs["Denoising Normal"], denoise_node.inputs["Normal"])
        elif len(denoise_node.inputs) > 1:
            # Fallback for older versions if name not found
            links.new(r_layers.outputs["Denoising Normal"], denoise_node.inputs[1])
            
        if 'Albedo' in denoise_node.inputs:
            links.new(r_layers.outputs["Denoising Albedo"], denoise_node.inputs["Albedo"])
        elif len(denoise_node.inputs) > 2:
            # Fallback for older versions if name not found
            links.new(r_layers.outputs["Denoising Albedo"], denoise_node.inputs[2])
        
        switch_label = "Switch Light Mix"
        switch_node = None
        for node in nodes:
            if node.type == 'SWITCH' and node.label == switch_label:
                switch_node = node
                break
       
        for link in links:
            if link.from_socket == r_layers.outputs['Image']:
                links.new(link.to_socket, switch_node.outputs[0])
                break
                      
        if switch_node:
            # Connect image to switch
            if bpy.app.version >= (5, 0, 0):
                # Search for input by name or use index
                if 'Off' in switch_node.inputs:
                    links.new(r_layers.outputs['Image'], switch_node.inputs['Off'])
                elif len(switch_node.inputs) > 1:
                    # In Blender 5.0, if name not found, Off is at index 1 (index 0 is boolean Switch)
                    links.new(r_layers.outputs['Image'], switch_node.inputs[1])
                else:
                    links.new(r_layers.outputs['Image'], switch_node.inputs[0])

                if 'On' in switch_node.inputs:
                    # Logic to find what was connected to composite
                    target_socket = composite_node.inputs[0] # Group Output Image
                    if target_socket.is_linked:
                        connected = target_socket.links[0].from_node
                        links.new(connected.outputs[0], switch_node.inputs['On'])
                    
                    # Connect switch output to composite
                    links.new(switch_node.outputs[0], target_socket)
            else:
                # 4.x logic
                links.new(r_layers.outputs['Image'], switch_node.inputs['Off'])
                image_input = composite_node.inputs.get('Image')
                if image_input and image_input.is_linked:
                    connected = image_input.links[0].from_node
                    links.new(connected.outputs[0], switch_node.inputs['On'])
                
                if image_input:
                    links.new(switch_node.outputs[0], image_input)


        lightgroup_blending_grp = append_node_group(lightgroup_blending_grp_name)
        # Look for Render Layers nodes and store links from Image socket
        render_layers_nodes = {}
        for node in nodes:
            if node.type == 'R_LAYERS': # and node.layer == view_layer.name:
                render_layers_nodes[node] = []
                for link in links:
                    if link.from_socket == node.outputs['Image']:
                        render_layers_nodes[node].append(link.to_socket)
        # If no Render Layers node, create one
        if not render_layers_nodes:
            render_layers_node = nodes.new('CompositorNodeRLayers')
            render_layers_nodes[render_layers_node] = []
        # Look for 'Light Groups' frame and delete it
        for n in nodes:
            if n.name == 'PG_Lightgroups_Frame':
                nodes.remove(n)
        for rln in render_layers_nodes:
            vl = rln.layer
            loc = rln.location
            lg_loc = None   
            # Create Lightgroup group nodes for as many Lightgroups in the view layer
            lgs = [lg.name for lg in scene.view_layers[vl].lightgroups]
            for i, lg in enumerate(lgs):
                lg_blending=[]
                # Check if there is already a Lightgroup node connected to the Render Layer output
                for link in links:
                    if link.from_socket == rln.outputs['Combined_'+lg]:
                        if link.to_node.type == 'GROUP' and link.to_node.node_tree.name == lightgroup_blending_grp_name:
                            lg_blending = link.to_node
                            lg_loc = lg_blending.location
                # If not, create a Lightgroup node
                if not lg_blending:
                    lg_blending = nodes.new('CompositorNodeGroup')
                    lg_blending.node_tree = lightgroup_blending_grp
                    lg_blending.label = lg_blending.name = lg
                    lg_blending.node_tree.use_fake_user = True
                    lg_blending.width = 170
                    # Arrange position based on already existing Lightgroup
                    if lg_loc:
                        lg_blending.location = (lg_loc[0], loc[1] + int(i)*-200)
                    # Or take Render Layer node position
                    else:
                        if i == 0:
                            rln.location[0] = -850
                            lg_blending.location = (loc[0]+300, loc[1] + int(i)*-200)
                        else:
                            lg_blending.location = (loc[0]+300, loc[1] + int(i)*-200)
                # Store Lightgroup index to reconnect them later
                lg_blending['lg_index'] = i
                # Connect first Lightgroup output reusing Render Layer node output connection
                # if i == 0:
                for link in render_layers_nodes[rln]:
                    links.new(lg_blending.outputs[0], link)
                # Connect Render Layer node to Lightgroup node
                links.new(rln.outputs['Combined_'+lg], lg_blending.inputs[1])
                # Connect Lightgroups together
                if i>=1:
                    for node in nodes:
                        if node.get('lg_index',-1) == i-1:
                            lg_blending.location = (node.location[0], loc[1] + int(i)*-200)
                            links.new(node.outputs[0], lg_blending.inputs[0])
                            # for link in links:
                            #     if link.from_socket == node.outputs[0]:
                            #         links.new(lg_blending.outputs[0], link.to_socket)    
                else:
                    if lg_loc:
                        lg_blending.location = (lg_loc[0], loc[1] + int(i)*-200)
                    else:
                        rln.location[0] = -850
                        lg_blending.location = (loc[0]+300, loc[1] + int(i)*-200)
        #bpy.context.scene.node_tree.links.new(denoise_node.outputs[0], composite_node.inputs[0])
        # Deselecting nodes
        selected_nodes = [n for n in nodes if n.select==True]
        for n in selected_nodes:
            n.select = False

        # Listing Light Group nodes to frame them
        '''lg_nodes = [n for n in nodes if n.type == 'GROUP' and n.node_tree.name == lightgroup_blending_grp_name]
        # Create a Frame node
        frame = nodes.new(type='NodeFrame')
        frame.label = 'Light Groups'
        frame.name = 'PG_Lightgroups_Frame'
        frame.use_custom_color = True
        frame.color = (0.42,0.5,0.415)
        # Frame them
        for node in lg_nodes:
            node.parent = frame'''

    #////////////////////////////////////////////////////////////////////////////////////
        links.new(r_layers.outputs['Image'], switch_node.inputs['Off'])     
        links.new(denoise_node.outputs['Image'], switch_node.inputs['On'])
        
        glare_node = None
        for node in node_tree.nodes:
            if node.type == 'GLARE' and node.label == "KH-Post SIMPLE_STAR":
                glare_node = node
                break
        composite_node = None
        for node in node_tree.nodes:
            if node.type == 'COMPOSITE':
                composite_node = node
                break
        if glare_node and composite_node:
            if not glare_node.outputs["Image"].is_linked and not composite_node.inputs["Image"].is_linked :
                    links.new(switch_node.outputs['Image'], composite_node.inputs["Image"])
    

 #delete//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                    
def Delete_light_mix():
    light_groups = [lg for lg in bpy.context.scene.view_layers[0].lightgroups]
    for lg in light_groups:
        bpy.ops.scene.view_layer_remove_lightgroup()

    compositor_window = get_scene_compositor(bpy.context.scene)
    render_layers = compositor_window.nodes.get("Render Layers")
    if render_layers:
        Denoise_node = compositor_window.nodes.get("Switch")
        if Denoise_node:
            denoise_output_linked = False
            for link in compositor_window.links:
                if link.from_node == Denoise_node and link.from_socket == Denoise_node.outputs[0]:
                    denoise_output_linked = True
                    denoise_output_link = link
                    break
            if denoise_output_linked:                    
                render_to_composite = compositor_window.links.new(render_layers.outputs[0], denoise_output_link.to_socket)
                
    denoise_node = None
    for node in compositor_window.nodes:
        if node.label == "Denoise Light Mix":
            denoise_node = node
            break
    if denoise_node is not None:
        compositor_window.nodes.remove(denoise_node)

    Switch_node = None
    for node in compositor_window.nodes:
        if node.label == "Switch Light Mix":
            Switch_node = node
            break
    if Switch_node is not None:
        compositor_window.nodes.remove(Switch_node)
    bpy.ops.scene.view_layer_remove_unused_lightgroups()

def Delete_light_mix_GROUP():
    render_layer_node_name = "Render Layers"
    output_prefix = "Combined"
    compositor_window = get_scene_compositor(bpy.context.scene)
    if render_layer_node_name in compositor_window.nodes:
        render_layer_node = compositor_window.nodes[render_layer_node_name]
        for output in render_layer_node.outputs:
            if output.name.startswith(output_prefix):
                node_group = output.links[0].to_node if output.links else None
                if node_group and node_group.type == 'GROUP':
                    compositor_window.nodes.remove(node_group)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def append_node_group(group_name,retrocompatible=False):
    path = "blends/node_groups.blend/NodeTree/"
    # if retrocompatible and bpy.app.version < (3,4,0):
    #     path = "blends/node_groups_3.3.blend/NodeTree/"
    dir = os.path.join(light_mix_folder,path)
    dir = os.path.normpath(dir)
    grp = None
    grps = [g for g in bpy.data.node_groups if g.name == group_name]
    if grps:
        grp = grps[0]
    if not grp:
        bpy.ops.wm.append(filename=group_name, directory=dir)
        grp = [g for g in bpy.data.node_groups if g.name == group_name][0]
    return grp
     


class VIEW3D_OT_Add_LightGroup(bpy.types.Operator):
    bl_idname = "view3d.add_light_group"
    bl_label = "Add Light Mix"
    
    def execute(self, context):
        lightmix_Compositor()
        add_lightgroup()

        view_layer = context.view_layer      
        if not view_layer.lightgroups:
            self.report({'WARNING'}, "No Light Group found, create World First.")
            return {'CANCELLED'}
    
        add_lightmix_nodes(self, context)

        self.report({'INFO'}, f"Light Mix addition has been Add") 
        return {'FINISHED'}

# Update Light Mix ////////////////////////////////////////////////////////////////////////////////////////////////////////  
class VIEW3D_OT_Update_LightGroup(bpy.types.Operator):
    bl_idname = "view3d.update_light_group"
    bl_label = "Update Light Mix"
    
    def execute(self, context):
        Delete_light_mix()
        Delete_light_mix_GROUP()
        lightmix_Compositor()
        add_lightgroup()
        view_layer = context.view_layer      
        if not view_layer.lightgroups:
            self.report({'WARNING'}, "No Light Group found, create World First.")
            return {'CANCELLED'}

        add_lightmix_nodes(self, context)
        
        self.report({'INFO'}, f"Light Mix has been Updated")
        return {'FINISHED'}
    
# Reset Light Mix ////////////////////////////////////////////////////////////////////////////////////////////////////////  
class VIEW3D_OT_Reset_LightGroup(bpy.types.Operator):
    bl_idname = "view3d.reset_light_group"
    bl_label = "Reset Light Mix"
    
    def execute(self, context):
        Delete_light_mix()
        Delete_light_mix_GROUP()
        lightmix_Compositor()
        add_lightgroup()
        view_layer = context.view_layer      
        if not view_layer.lightgroups:
            self.report({'WARNING'}, "No Light Group found, create World First.")
            return {'CANCELLED'}
        
        add_lightmix_nodes(self, context)
        return {'FINISHED'}
    
# Remove Light Mix ////////////////////////////////////////////////////////////////////////////////////////////////////////  
class VIEW3D_OT_Remove_LightGroup(bpy.types.Operator):
    bl_idname = "view3d.remove_light_group"
    bl_label = "Remove Light Mix"
    
    def execute(self, context):
        Delete_light_mix()
        Delete_light_mix_GROUP()
        self.report({'INFO'}, f"Light Mix has been Deleted")
        return {'FINISHED'}
        

#Denoise Light Mix////////////////////////////////////////////////////////////////////////////////////////////
class VIEW3D_OT_mute_Denoise(bpy.types.Operator):
    bl_idname = "view3d.mute_denoise"
    bl_label = "Denoise(Fast)"

    def execute(self, context):
        compositor_window = get_scene_compositor(bpy.context.scene)
        denoise_node = None
        for node in compositor_window.nodes:
            if node.label == "Denoise Light Mix":
                denoise_node = node
                break
        if denoise_node is not None:
            denoise_node.mute = True

        if node.type == 'GLARE':
            node.mute = True
        return {'FINISHED'}
    
class VIEW3D_OT_mute_False_Denoise(bpy.types.Operator):
    bl_idname = "view3d.mute_false_denoise"
    bl_label = "Denoise(Low)"

    def execute(self, context):
        compositor_window = get_scene_compositor(bpy.context.scene)
        denoise_node = None
        for node in compositor_window.nodes:
            if node.label == "Denoise Light Mix":
                denoise_node = node
                break
        if denoise_node is not None:
            denoise_node.mute = False
        return {'FINISHED'}

        '''compositor_window = bpy.context.scene.node_tree
        for node in compositor_window.nodes:
            if node.type == 'GLARE':
                node.mute = False

            print("تم حذف النود بنجاح")'''
        

# Switch.check ////////////////////////////////////////////////////////////////////////////////////////////
class Switch_On_Operator(bpy.types.Operator):
    bl_idname = "render.switch_on"
    bl_label = "Switch ON"
    
    def execute(self, context):
        compositor_window = get_scene_compositor(bpy.context.scene)
        Switch = None
        for node in compositor_window.nodes:
            if node.label == "Switch Light Mix":
                Switch = node
                break
        if Switch is not None:
            set_switch_check(Switch, True)
        return {'FINISHED'}

class Switch_Off_Operator(bpy.types.Operator):
    bl_idname = "render.switch_off"
    bl_label = "Switch OFF"
    def execute(self, context):
        compositor_window = get_scene_compositor(bpy.context.scene)
        Switch = None
        for node in compositor_window.nodes:
            if node.label == "Switch Light Mix":
                Switch = node
                break
        if Switch is not None:
            set_switch_check(Switch, False)
        return {'FINISHED'}




# IMAGE_EDITOR Panel //////////////////////////////////////////////////////////////////////////////////////////   
# my_icons_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Blender Foundation", "Blender", "4.0", "scripts", "addons", "KH-Light Mix", "icons")
# preview_collection = bpy.utils.previews.new()
# preview_collection.load("17.png", os.path.join(my_icons_dir, "17.png"), 'IMAGE')  



addon_dir = os.path.dirname(__file__)
my_icons_dir = os.path.join(addon_dir, "icons")

#preview_collection = bpy.utils.previews.new()
#preview_collection.load("17.png", os.path.join(my_icons_dir, "17.png"), 'IMAGE')



class Image_Editor_Light_Mix_Panel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_image_editor_light_mix_panel"
    bl_label = "Light Mix"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = "UI"
    bl_category = "Light Mix" 

    @classmethod
    def poll(cls, context):
        if 'KH-Tools' in context.preferences.addons:
            KH = context.preferences.addons['KH-Tools'].preferences.Light_Mix == True
            return KH
        else:
            return True

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon="OUTLINER_OB_LIGHT")
        except KeyError:
            pass          

    def draw(self, context):
        scene   = context.scene
        compositor_window = get_scene_compositor(scene)
        if compositor_window and compositor_window.nodes is not None:
            nodes = compositor_window.nodes


        layout = self.layout
        render_engine = bpy.context.scene.render.engine
        if render_engine == 'CYCLES':
            # Check if compositor is set up (5.0+) or use_nodes (4.x)
            has_compositor = (bpy.app.version >= (5, 0, 0) and scene.compositing_node_group is not None) or \
                           (bpy.app.version < (5, 0, 0) and scene.use_nodes == True)
            
            if not has_compositor:
                box = layout.box()
                row = box.row(align=True)
                row.label(text="Light Mix Is Not Activated", icon='ERROR')
                row = box.row(align=True)
                row.label(text="Activate it first from the Render Settings", icon='ERROR')        
            else:
                render_layers = compositor_window.nodes.get("Render Layers")
                target_switch_label = "Switch Light Mix"
                switch_node = None
                for node in compositor_window.nodes:
                    if node.type == 'SWITCH' and node.label == target_switch_label:
                        if node.type == 'SWITCH' and node.label == target_switch_label:
                            switch_node = node
                            break
                if switch_node:
                    current_scene = bpy.context.scene
                    windows = bpy.context.window_manager.windows
                    compositing_window = None
                    for window in windows:
                        screen = window.screen
                        for area in screen.areas:
                            if area.type == 'NODE_EDITOR' and area.ui_type == 'CompositorNodeTree':
                                compositing_window = window

                    if not compositing_window:
                        box = layout.box()
                        row = box.row(align=True)
                        row .operator("object.compositor", icon='ERROR')
                    else :
                            box = layout.box()
                            row = box.row(align=True)
                            Switch = None
                            for node in compositor_window.nodes:
                                if node.label == "Switch Light Mix":
                                    Switch = node
                                    break
                            if Switch is not None:
                                if get_switch_check(Switch) == False :
                                    row.operator("render.switch_on", text="Light Mix", icon='CHECKBOX_DEHLT')  
                                else:
                                    row.operator("render.switch_off", text="Light Mix", icon='CHECKBOX_HLT') 
                                    
                                    target_switch_label = "Switch Light Mix"

                                    switch_node = None
                                    for node in compositor_window.nodes:
                                        if node.type == 'SWITCH' and node.label == target_switch_label:
                                            if node.type == 'SWITCH' and node.label == target_switch_label:
                                                switch_node = node
                                                break
                                    if switch_node:
                                        #box = layout.box()
                                        #row = box.row(align=True)
                                        nodes = compositor_window.nodes
                                        has_image_node = False

                                        for node in nodes:
                                            if node.type == 'IMAGE':
                                                has_image_node = True
                                                break

                                        if has_image_node:
                                            row.operator("view3d.reset_exr", text="Reset EXR" , icon='FILE_REFRESH')
                                        else:
                                            row.operator("view3d.reset_light_group", text="Reset" , icon='FILE_REFRESH')
                                    #row.operator("view3d.remove_light_group", text="Disable", icon='RESTRICT_RENDER_ON')
                                    scene = context.scene
                                    node_tree = compositor_window
                                    target_node_name = "Denoise"                   
                                    Denoise_node = node_tree.nodes.get(target_node_name)
                                    row = box.row(align=True)
                                    if Denoise_node is not None and Denoise_node.mute == True:
                                        row.operator("view3d.mute_false_denoise", text="Denoise" , icon='RESTRICT_VIEW_ON') 
                                    else:
                                        row.operator("view3d.mute_denoise", text="Denoise" , icon='RESTRICT_VIEW_OFF') 
                                        
                                    if hasattr(bpy.context.scene.render, "compositor_device"):
                                        row.prop(context.scene.render, "compositor_device", text="", toggle=True)

                                    
                                        
                                        
                                    compositor_window = get_scene_compositor(context.scene)
                                    if compositor_window:
                                        node_tree = compositor_window
                                        exposure_nodes = []
                                        render_layer_node_name = "Render Layers" if "Render Layers" in compositor_window.nodes else "Image"

                                        
                                        if render_layer_node_name in compositor_window.nodes:
                                            render_layer_node = compositor_window.nodes[render_layer_node_name]
                                            outputs = [output for output in render_layer_node.outputs if output.name.startswith("Combined_")]
                                            for i, output in enumerate(outputs):
                                                exposure_name = output.name.replace("Combined_", "")
                                                exposure_name1 = exposure_name.split(' /')[0]
                                                exposure_name2 = output.name.replace("Combined_", "").replace('C-', '').replace('/', '|').replace('_', '.')
                                                exposure_name3 =  exposure_name1.replace('M-', '').replace('_', '.')
                                                

                                                # حذف كلمة "Combined"
                                                Switch = None
                                                for node in compositor_window.nodes:
                                                    if node.label == "Switch Light Mix":
                                                        Switch = node
                                                        break
                                                exposure_node = None
                                                if Switch is not None:
                                                    if get_switch_check(Switch) == True :
                                                        exposure_node = next((node for node in node_tree.nodes if exposure_name in node.name ),None)
                                                
                                                if exposure_node:
                                                    #exposure_nodes.append(exposure_node)
                                                    layout = self.layout
                                                    box = layout.box()
                                                    row = box.row(align=True)
                                                    
                                                    if 'M-' in exposure_name:
                                                        row.label(text=exposure_name3, icon='MATERIAL')
                                                        #row.scale_x = 0.5
                                                        row.prop(exposure_node, "mute", text="", icon='SETTINGS')
                                                        #row.scale_y = 0.5
                                                    elif '1-' in exposure_name:
                                                        row.label(text=exposure_name2, icon='LIGHT_DATA')
                                                        #row.scale_x = 0.5
                                                        row.prop(exposure_node, "mute", text="", icon='SETTINGS')
                                                        #row.scale_y = 0.6
                                                    elif 'World' in exposure_name: 
                                                        row.label(text=exposure_name, icon='WORLD')
                                                        #row.scale_x = 0.5
                                                        row.prop(exposure_node, "mute", text="", icon='SETTINGS')
                                                        #row.scale_y = 0.6
                                                    else:
                                                        row.label(text=exposure_name2, icon='OUTLINER_COLLECTION')
                                                        
                                                        #row.label(text="", icon='OUTLINER_COLLECTION')
                                                        
                                                        row.prop(exposure_node, "mute", text="", icon='SETTINGS')
                                                        #row.scale_y = 0.5
                                                    if not exposure_node.mute:
                                                        # row = box.row(align=True)
                                                        row.prop(exposure_node.inputs[2], "default_value", text="")
                                                        row.scale_y = 0.9
                                                        row = box.row(align=True)
                                                        row.prop(exposure_node.inputs[4], "default_value", text="", slider=True)
                                                        row.scale_y = 0.9
                                                        row.scale_x = 0.5
                                                        row.prop(exposure_node.inputs[3], "default_value", text="")
                                                    box = layout.box()
            
                else :
                    #group_nodes = [node for node in bpy.context.scene.node_tree.nodes if node.type == 'GROUP' and node.label == 'World']
                    #if group_nodes:
                        #box = layout.box()
                        #row = box.row(align=True)
                        #row.operator("view3d.add_light_group", text="Activate Light Mix", icon='RESTRICT_RENDER_OFF')
                    box = layout.box()
                    row = box.row(align=True)
                    row.label(text="Light Mix Is Not Activated", icon='ERROR')
                    row = box.row(align=True)
                    row.label(text="Activate it first from the Render Settings", icon='ERROR')
        else:
            layout = self.layout
            box = layout.box()
            row = box.row(align=True)
            row.label(text="Switch the render engine to CYCLES.", icon='ERROR') 




# PROPERTIES render Panel ////////////////////////////////////////////////////////////////////////////////////////// 
#preview_collection1 = bpy.utils.previews.new()
#preview_collection1.load("17.png", os.path.join(my_icons_dir, "17.png"), 'IMAGE')              
class Light_Mix_Panel(bpy.types.Panel):
    bl_label = "Light Mix"
    bl_idname = "VIEW3D_PT_light_mix_panel"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "KH-Tools"
    bl_options = {'DEFAULT_CLOSED'}
    #bl_options     = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        if 'KH-Tools' in context.preferences.addons:
            KH = context.preferences.addons['KH-Tools'].preferences.Light_Mix == True
            return KH
        else:
            return True
        
    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon="OUTLINER_OB_LIGHT")
        except KeyError:
            pass
    def draw(self, context):
        scene   = context.scene
        layout = self.layout
        render_engine = bpy.context.scene.render.engine
        if render_engine == 'CYCLES':
            # Check if compositor is set up (5.0+) or use_nodes (4.x)
            has_compositor = (bpy.app.version >= (5, 0, 0) and scene.compositing_node_group is not None) or \
                           (bpy.app.version < (5, 0, 0) and scene.use_nodes == True)
            
            if not has_compositor:
                box = layout.box()
                row = box.row(align=True)
                row.operator("view3d.add_light_group", text="Add Light Mix" , icon='ADD')
                row = box.row(align=True)
                row.operator("view3d.open_exr_file", text="Open EXR File" , icon='ADD')
                compositor_window = get_scene_compositor(scene)
                if compositor_window:
                    nodes = compositor_window.nodes
                    for node in nodes:
                        if node.type == 'IMAGE':
                            row = box.row(align=True)
                            row.operator("view3d.exr_light_group", text="EXR Light Mix" , icon='ADD')

            else:
                target_switch_label = "Switch Light Mix"
                switch_node = None
                compositor_window = get_scene_compositor(scene)
                if not compositor_window:
                    return  # No compositor set up yet
                for node in compositor_window.nodes:
                    if node.type == 'SWITCH' and node.label == target_switch_label:
                        if node.type == 'SWITCH' and node.label == target_switch_label:
                            switch_node = node
                            break
                if switch_node:
                    box = layout.box()
                    row = box.row(align=True)
                    nodes = compositor_window.nodes
                    has_image_node = False

                    for node in nodes:
                        if node.type == 'IMAGE':
                            has_image_node = True
                            break

                    if has_image_node:
                        row.operator("view3d.remove_exr", text="Delete EXR" , icon='TRASH')
                    else:                
                        row.operator("view3d.update_light_group", text="Update" , icon='FILE_REFRESH')
                        row.operator("view3d.remove_light_group", text="Delete" , icon='TRASH')
                        row = box.row(align=True)
                        row.prop(scene, "render_exr_enabled", text="Export EXR" , icon="NODE_COMPOSITING") 
                        row.prop(scene, "light_mix_enabled", text="Auto (Slow)" , icon='OUTLINER_OB_LIGHT')

                    
                    compositor_window = get_scene_compositor(scene)
                    if compositor_window:
                        nodes = compositor_window.nodes
                        for node in nodes:
                            if node.type == 'IMAGE':
                                row = box.row(align=True)          
                else:
                    compositor_window = get_scene_compositor(scene)
                    if compositor_window:
                        box = layout.box()
                        row = box.row(align=True)
                        nodes = compositor_window.nodes
                        has_image_node = False

                        for node in nodes:
                            if node.type == 'IMAGE':
                                has_image_node = True
                                break
                        if has_image_node:
                            row.operator("view3d.exr_light_group", text="EXR Light Mix" , icon='QUIT')
                        else:
                            row.operator("view3d.add_light_group", text="Activate Light Mix" , icon='QUIT')
                
                compositor_window = get_scene_compositor(scene)
                if compositor_window:
                    render_layer_node_name = "Render Layers"
                    if render_layer_node_name in compositor_window.nodes:
                        render_layer_node = compositor_window.nodes[render_layer_node_name]
                        outputs = [output for output in render_layer_node.outputs if output.name.startswith("Combined")]
                        for i, output in enumerate(outputs):
                            if output.name in render_layer_node.outputs:
                                exposure_name = output.name.replace("Combined_", "")
                                exposure_name1 = output.name.split(' /')[0].replace("Combined_", "")# حذف كلمة "Combined"
                                exposure_name2 = output.name.replace("Combined_", "").replace('C-', '').replace('/', '|').replace('_', '.')
                                exposure_name3 =  exposure_name1.replace('M-', '').replace('_', '.')
                                
                                layout = self.layout
                                box = layout.box()
                                row = box.row(align=True)
                                if 'M-' in exposure_name:
                                    row.label(text=exposure_name3, icon='MATERIAL')                                           
                                    op = row.operator("object.light_mix_emission_selectb", text="", icon = 'RESTRICT_SELECT_OFF')
                                    op.exposure_name = exposure_name

                                elif '1-' in exposure_name:
                                    row.label(text=exposure_name2, icon='LIGHT_DATA')
                                elif 'World' in exposure_name:
                                    row.label(text=exposure_name, icon='WORLD')
                                else:
                                    row.label(text=exposure_name2, icon='OUTLINER_COLLECTION')
                                #row.scale_x = 0.8
                                
                                row.scale_y = 0.6
        
        else:
            layout = self.layout
            box = layout.box()
            row = box.row(align=True)
            row.label(text="Switch the render engine to CYCLES.", icon='ERROR')                  
                   
class light_mix_EmissionSelectb(bpy.types.Operator):
    bl_idname = "object.light_mix_emission_selectb"
    bl_label = ""
    bl_description = "Select by Material Name"
    exposure_name : bpy.props.StringProperty()
    def execute(self, context):
        exposure_name = self.exposure_name
        for obj in bpy.data.objects:
            if obj.lightgroup == exposure_name:
                bpy.ops.object.select_all(action='DESELECT')             
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                obj = bpy.context.active_object
                if hasattr(obj, 'lightgroup'):
                    light_group = obj.lightgroup.replace('M-', '').replace('_', '.').split(' /')[0].replace("Combined_", "")
                    if light_group in [slot.material.name for slot in obj.material_slots]:
                        obj.active_material_index = [slot.material.name for slot in obj.material_slots].index(light_group)
                break

        return {'FINISHED'}
    
import time, datetime   
active_camera_name = None
@persistent
def render_init1(scene):
    global active_camera_name
    active_camera_name = scene.camera.name
    print(f"Render init: Active camera is set to {active_camera_name}")

  
def save_original_settings():
    original_file_format = bpy.context.scene.render.image_settings.file_format
    original_color_depth = bpy.context.scene.render.image_settings.color_depth
    return original_file_format, original_color_depth

def restore_original_settings(original_file_format, original_color_depth):
    bpy.context.scene.render.image_settings.file_format = original_file_format
    bpy.context.scene.render.image_settings.color_depth = original_color_depth
    

def render_exr(scene):
    global active_camera_name
    if scene.render_exr_enabled:
        active_camera_name = bpy.context.scene.camera.name
        current_filepath = bpy.data.filepath
        directory, filename = os.path.split(current_filepath)
        if not directory:
            raise Exception("يرجى حفظ الملف أولاً لتحديد مسار الحفظ")
        original_file_format, original_color_depth = save_original_settings()
        try:
            render_result_image = bpy.data.images['Render Result']
            image_filepath = os.path.join(directory, "Render", f"{active_camera_name}.exr")
            bpy.context.scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
            bpy.context.scene.render.image_settings.color_depth = '16'
            render_result_image.save_render(image_filepath, scene=scene)
        finally:
            restore_original_settings(original_file_format, original_color_depth)
        
                    
@persistent
def render_exr_handler(dummy):
    render_exr(bpy.context.scene)       
        
 
# Register the classes//////////////////////////////////////////////////////////////////////////////////////////////
classes = (
    Image_Editor_Light_Mix_Panel,
    Light_Mix_Panel,
    VIEW3D_OT_Add_LightGroup,
    VIEW3D_OT_Update_LightGroup,
    VIEW3D_OT_Reset_LightGroup,
    VIEW3D_OT_Remove_LightGroup,
    CompositorOperator,
    VIEW3D_OT_mute_False_Denoise,
    VIEW3D_OT_mute_Denoise,

    Post_Production,
    Clear_Compositor_Operator,
    Rest_Composito_rOperator,
    Post_Production_Panel,
    Post_Productions_IMAGE_EDITOR_Panel,
    Delete_Compositor_Operator,
    Switch_On_Operator,
    Switch_Off_Operator,
    VIEW_3D_ALWAYS_Operator,
    VIEW_3D_DISABLED_Operator,

    open_exr_file,
    VIEW3D_OT_exrLightGroup,
    VIEW3D_OT_Remove_exr,
    reset_exr, 
    light_mix_EmissionSelectb,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    
    bpy.types.Scene.color_management_enabled = bpy.props.BoolProperty(name="Color Management", default=False) 

    bpy.types.Scene.light_mix_enabled = bpy.props.BoolProperty(
        name="Light_Mix",
        description="Enabled Light Mix",
        default=False,
    )  

    bpy.types.Scene.render_exr_enabled = bpy.props.BoolProperty(
        name="Export EXR",
        description="Export EXR",
        default=False,
    )
    
    def make_glare_update(idx):
        def update(self, context):
            from .Post_Production import get_compositor_tree
            tree = get_compositor_tree(context.scene)
            if tree:
                nodes = [n for n in tree.nodes if n.type == 'GLARE' and n.label.startswith("KH-Post")]
                nodes.sort(key=lambda n: n.location.x)
                if len(nodes) >= idx:
                    nodes[idx-1].mute = not getattr(context.scene, f"kh_post_glare{idx}_active")
        return update

    # Glare UI tabs properties (7 types)
    for i in range(1, 8):
        # Tab property
        setattr(bpy.types.Scene, f"kh_post_glare{i}_tab", bpy.props.EnumProperty(
            name=f"Glare Tab {i}",
            items=[
                ('MAIN', "Main", "General settings"),
                #('HIGHLIGHTS', "Highlights", "Threshold and Clamp settings"),
                #('ADJUST', "Adjust", "Color and Intensity settings"),
                ('GLARE', "Glare", "Type specific settings")
            ],
            default='MAIN'
        ))
        
        # Active/Enable property
        setattr(bpy.types.Scene, f"kh_post_glare{i}_active", bpy.props.BoolProperty(
            name="Active",
            description="Enable or Disable this glare effect",
            default=False,
            update=make_glare_update(i)
        ))

    bpy.app.handlers.render_post.append(render_exr_handler)
    bpy.app.handlers.depsgraph_update_pre.append(render_pre_Aoto_light_mix)
    bpy.app.handlers.render_init.append(render_init1)
    
    
    
    

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # التحقق من وجود الخصائص قبل حذفها لتجنب الأخطاء
    if hasattr(bpy.types.Scene, 'render_exr_enabled'):
        del bpy.types.Scene.render_exr_enabled
    if hasattr(bpy.types.Scene, 'light_mix_enabled'):
        del bpy.types.Scene.light_mix_enabled
    if hasattr(bpy.types.Scene, 'color_management_enabled'):
        del bpy.types.Scene.color_management_enabled

    # إزالة handlers بأمان
    try:
        bpy.app.handlers.render_post.remove(render_exr_handler)
    except ValueError:
        pass  # Handler already removed or not present

    try:
        bpy.app.handlers.depsgraph_update_pre.remove(render_pre_Aoto_light_mix)
    except ValueError:
        pass  # Handler already removed or not present

    try:
        bpy.app.handlers.render_init.remove(render_init1)
    except ValueError:
        pass  # Handler already removed or not present
    
    
    
   
if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()


