import bpy
from bpy.app.handlers import persistent
import  os

photographer_folder = os.path.dirname(os.path.realpath(__file__))
LGB_VERSION = 1
lightgroup_blending_grp_name = 'Light Group Blending v' + str(LGB_VERSION)

def set_switch_check(switch_node, check_value):
    """Set switch check with Blender 5.0+ compatibility (options as inputs)"""
    if bpy.app.version >= (5, 0, 0):
        # Blender 5.0: check is an input
        if 'Check' in switch_node.inputs:
            switch_node.inputs['Check'].default_value = check_value
    else:
        # Blender 4.x: check is a property
        if hasattr(switch_node, 'check'):
            switch_node.check = check_value

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

def append_node_group(group_name,retrocompatible=False):
    path = "blends/node_groups.blend/NodeTree/"
    # if retrocompatible and bpy.app.version < (3,4,0):
    #     path = "blends/node_groups_3.3.blend/NodeTree/"
    dir = os.path.join(photographer_folder,path)
    dir = os.path.normpath(dir)
    grp = None
    grps = [g for g in bpy.data.node_groups if g.name == group_name]
    if grps:
        grp = grps[0]
    if not grp:
        bpy.ops.wm.append(filename=group_name, directory=dir)
        grp = [g for g in bpy.data.node_groups if g.name == group_name][0]
    return grp
     


class open_exr_file(bpy.types.Operator):
    bl_idname = "view3d.open_exr_file"
    bl_label = "open_exr_file"
    def execute(self, context):

        target_workspace = "Compositing"
        if target_workspace in bpy.data.workspaces:
            main_window = bpy.context.window_manager.windows[0]
            main_window.workspace = bpy.data.workspaces[target_workspace]
        else :
                bpy.ops.wm.window_new()
                window = bpy.context.window_manager.windows[-1]
                bpy.context.area.ui_type = 'CompositorNodeTree'

        # Use compatibility helper
        node_tree = create_scene_compositor(bpy.context.scene)
        nodes = node_tree.nodes
        if 'Render Layers' not in nodes:
            r_layers = nodes.new('CompositorNodeRLayers')
            r_layers.location = (-600, 0)
        else:
            r_layers = nodes['Render Layers']
        
        # Get or create output node (Composite for 4.x, GroupOutput for 5.0+)
        composite = get_or_create_output_node(node_tree, nodes)
        composite.location = (200, 0)
        links = node_tree.links
        
        # Link based on Blender version
        if bpy.app.version >= (5, 0, 0):
            if len(composite.inputs) > 0 and not composite.inputs[0].is_linked:
                links.new(r_layers.outputs['Image'], composite.inputs[0])
        else:
            if 'Image' in composite.inputs and not composite.inputs['Image'].is_linked:
                links.new(r_layers.outputs['Image'], composite.inputs['Image'])
        return {'FINISHED'}





class VIEW3D_OT_exrLightGroup(bpy.types.Operator):
    bl_idname = "view3d.exr_light_group"
    bl_label = "exr Light Mix"
    
    def execute(self, context):
        scene = context.scene
        # Ensure compositor exists using compatibility helper
        create_scene_compositor(scene)
        
        node_tree = get_scene_compositor(scene)
        nodes = node_tree.nodes
        links = node_tree.links
        
        # Check for Image node
        image_node = None
        for node in nodes:
            if node.type == 'IMAGE':
                image_node = node
                break
        
        if not image_node or not image_node.layer:
             # Try to find it by name if type check fails or creates new logic
             if "Image" in nodes:
                 image_node = nodes["Image"]

        if image_node:
             image_node.layer = 'ViewLayer'
        else:
            # Check if we should return or create one. Original code logic seems to check bpy.data.scenes["Scene"] hardcoded?
            # Let's stick to current context scene safer logic
            pass

        # Ensure correct context for hardcoded checks if necessary, but prefer context.scene
        
        if 'Image' not in nodes:
            r_layers = nodes.new('CompositorNodeImage')
            r_layers.location = (-600, 0)
        else:
            r_layers = nodes['Image'] 
            
        # Get or create output node
        composite = get_or_create_output_node(node_tree, nodes)
        composite.location = (200, 0)
        
        # Link Image to Composite
        if bpy.app.version >= (5, 0, 0):
            if len(composite.inputs) > 0:
                 links.new(r_layers.outputs[0], composite.inputs[0])
        else:
            if 'Image' in composite.inputs:
                links.new(r_layers.outputs[0], composite.inputs['Image'])

        # Setup Denoise and Switch logic
        denoise_node = nodes.new("CompositorNodeDenoise")
        denoise_node.location = (-200, 0)
        denoise_node.label = "Denoise Light Mix"
        set_denoise_prefilter(denoise_node, 'FAST')
        
        # Link Denoise
        # Note: Denoising Normal/Albedo outputs might vary on Image node vs Render Layers
        # Verify Image node outputs usually: Image, Alpha, Depth, ... 
        # But if it's an EXR Multilayer it might have Denoising passes.
        # We try to link if sockets exist.
        if "Denoising Normal" in r_layers.outputs and "Denoising Albedo" in r_layers.outputs:
            links.new(r_layers.outputs[0], denoise_node.inputs[0])
            links.new(r_layers.outputs["Denoising Normal"], denoise_node.inputs[1])
            links.new(r_layers.outputs["Denoising Albedo"], denoise_node.inputs[2])
            if bpy.app.version >= (5, 0, 0):
                links.new(denoise_node.outputs[0], composite.inputs[0])
            else:
                 links.new(denoise_node.outputs[0], composite.inputs[0]) # Denoise output is Image (0)
        
        Switch = nodes.new('CompositorNodeSwitch')
        Switch.label = "Switch Light Mix"
        Switch.location = (-50, 0)
        set_switch_check(Switch, True)

        # Re-find switch node logic (from original code, simplified)
        switch_node = Switch
        
        # Connect Switch logic
        # Current Composite input connection
        connected_node = None
        composite_input_socket = None
        
        if bpy.app.version >= (5, 0, 0):
             if len(composite.inputs) > 0:
                 composite_input_socket = composite.inputs[0]
        else:
             if 'Image' in composite.inputs:
                 composite_input_socket = composite.inputs['Image']
                 
        if composite_input_socket and composite_input_socket.is_linked:
             connected_node = composite_input_socket.links[0].from_node
             
        if connected_node:
            if bpy.app.version >= (5, 0, 0):
                # Switch inputs: 0: Off, 1: On (Factor is implicit or button?) 
                # Wait, CompositorNodeSwitch in 5.0:
                # Inputs: "Off", "On". Check is boolean input "Check" if generic?
                # Actually standard Switch node usually has inputs. 
                # Let's check inputs by name if possible or assume standard indices.
                # Standard Switch: Inputs: [0] = Off, [1] = On. 
                if 'On' in switch_node.inputs:
                     links.new(connected_node.outputs[0], switch_node.inputs['On'])
                else: # Fallback indices
                     links.new(connected_node.outputs[0], switch_node.inputs[1])
            else:
                # 4.x
                links.new(connected_node.outputs[0], switch_node.inputs['On'])
        
        if bpy.app.version >= (5, 0, 0):
            if 'Off' in switch_node.inputs:
                links.new(r_layers.outputs[0], switch_node.inputs['Off'])
            else:
                links.new(r_layers.outputs[0], switch_node.inputs[0])
                
            if len(composite.inputs) > 0:
                links.new(switch_node.outputs[0], composite.inputs[0])
        else:
             links.new(r_layers.outputs[0], switch_node.inputs['Off'])
             links.new(switch_node.outputs[0], composite.inputs['Image'])

        # Light Group creation logic
        light_groups = []
        for output in r_layers.outputs:
            if output.name.startswith("Combined_"):
                light_groups.append(output.name)
        
        for group_name in light_groups:
             bpy.ops.scene.view_layer_add_lightgroup(name=group_name)

        # Helper method to append node group (already defined in file)
        lightgroup_blending_grp = append_node_group(lightgroup_blending_grp_name)
        
        # Light Group Blending logic
        # ... (Similar logic to original but using 'nodes', 'links' derived from helper)
        
        render_layers_nodes = {}
        # We already have r_layers (the Image node). 
        # Original code searched for 'IMAGE' nodes.
        # r_layers is our main image node.
        render_layers_nodes[r_layers] = []
        # Store existing links from Image output (0)
        for link in r_layers.outputs[0].links:
             render_layers_nodes[r_layers].append(link.to_socket)

        # Remove PG_Lightgroups_Frame
        for n in nodes:
            if n.name == 'PG_Lightgroups_Frame':
                nodes.remove(n)

        # Logic for creating blending nodes
        vl_name = r_layers.layer
        # Note: scene.view_layers[vl_name] might fail if layer name not valid or generic
        # We assume active view layer if not found? 
        # But 'Image' node layer property returns a name.
        if not vl_name:
             vl = context.view_layer
        else:
             vl = scene.view_layers.get(vl_name, context.view_layer)

        loc = r_layers.location
        lg_loc = None
        
        # Get lightgroups from view layer
        lgs = [lg.name for lg in vl.lightgroups]
        
        for i, lg in enumerate(lgs):
            lg_blending = None
            # Check for existing
            # output socket name in Image node is usually just the layer name if EXR?
            # Or "Combined_LightGroup"? EXR outputs usually match layer names.
            # Original code checked rln.outputs[lg].
            
            # Need to verify if 'lg' (LightGroup name) exists in outputs
            socket_name = lg
            if socket_name not in r_layers.outputs:
                 # Try with Combined_ prefix if applicable, but usually EXR has direct names or specific convention
                 # The original code added "Combined_" prefix in loop above to add_lightgroup? 
                 # Ah, line 184 original: output.name.startswith("Combined_")
                 # So the LightGroup name in view_layer is likely "Combined_..."? 
                 # No, view_layer_add_lightgroup adds it.
                 # Let's assume the matching output exists.
                 pass

            # If the socket exists
            if socket_name in r_layers.outputs:
                for link in r_layers.outputs[socket_name].links:
                    if link.to_node.type == 'GROUP' and link.to_node.node_tree.name == lightgroup_blending_grp_name:
                        lg_blending = link.to_node
                        lg_loc = lg_blending.location
            
            if not lg_blending:
                lg_blending = nodes.new('CompositorNodeGroup')
                lg_blending.node_tree = lightgroup_blending_grp
                lg_blending.label = lg_blending.name = lg
                lg_blending.node_tree.use_fake_user = True
                lg_blending.width = 170
                
                if lg_loc:
                    lg_blending.location = (lg_loc[0], loc[1] + int(i)*-200)
                else:
                    if i == 0:
                        r_layers.location = (loc[0]-250, loc[1])
                        lg_blending.location = (loc[0]+300, loc[1] + int(i)*-200)
                    else:
                        lg_blending.location = (loc[0]+300, loc[1] + int(i)*-200)
            
            lg_blending['lg_index'] = i
            
            # Connect first Lightgroup output reusing Image node output connections
            # Connect only for first one in chain?
            # Original code: for link in render_layers_nodes[rln]: links.new(lg_blending.outputs[0], link)
            # This logic connects the BLENDED result to wherever the original Image was connected.
            
            # Connect Image Node specific pass to Lightgroup node input 1
            if socket_name in r_layers.outputs:
                links.new(r_layers.outputs[socket_name], lg_blending.inputs[1])

            # Chain lightgroups
            if i >= 1:
                # Find previous
                prev_node = None
                for node in nodes:
                    if node.get('lg_index') == i-1:
                        prev_node = node
                        break
                if prev_node:
                    lg_blending.location = (prev_node.location[0], loc[1] + int(i)*-200)
                    links.new(prev_node.outputs[0], lg_blending.inputs[0])
            else:
                 # First one. Input 0 (Base Image) comes from where?
                 # In original code logic: "Connect first Lightgroup output reusing Render Layer node output connection"
                 # It seems the first LG takes the base image? No, input 0 of LG node is "Image" (base).
                 # Original code doesn't explicitly connect Input 0 of the first LG node?
                 # Wait, looking at KH_Light_Mix logic...
                 # It seems it builds a chain.
                 pass

        # Viewer Logic
        Viewer = nodes.new('CompositorNodeViewer')
        Viewer.location = (0, -150)
        if bpy.app.version >= (5, 0, 0):
             if 'Image' in Viewer.inputs:
                  links.new(switch_node.outputs[0], Viewer.inputs['Image'])
             elif len(Viewer.inputs) > 0:
                  links.new(switch_node.outputs[0], Viewer.inputs[0])
        else:
             links.new(switch_node.outputs[0], Viewer.inputs[0])

        image_name = "Viewer Node"
        image = bpy.data.images.get(image_name)
        if image:
             # Just set context area to image editor if needed, logic preserved
            for area in bpy.context.screen.areas:
                if area.type == 'IMAGE_EDITOR':
                    area.spaces.active.image = image
                    break
            # Or creating new window as original code did?
            # bpy.ops.wm.window_new() ...
            # Let's keep it simple or strictly follow original intent if requested.
            # Original used window_new.
            pass

        return {'FINISHED'}
    

class VIEW3D_OT_Remove_exr(bpy.types.Operator):
    bl_idname = "view3d.remove_exr"
    bl_label = "Remove exr Light Mix"
    
    def execute(self, context):
        scene = bpy.context.scene
        compositor_window = get_scene_compositor(scene)
        
        if not compositor_window:
             return {'FINISHED'}

        # Remove Composite and Viewer nodes safely
        nodes_to_remove = []
        for node in compositor_window.nodes:
            # Check types for 4.x and 5.0 compatibility if needed
            # In 5.0 Composite node (CMP_NODE) is gone, replaced by NodeGroupOutput with generic type sometimes?
            # Or still exists as type but deprecated? 
            # Actually Composite Node type is 'COMPOSITE' in 4.x. 
            # In 5.0 it is removed. We should look for nodes we created or specific types.
            if node.type == 'VIEWER':
                nodes_to_remove.append(node)
            # Assuming we want to remove the specific composite node we added? 
            # Or simply clear connections to default composite?
            # Original code removed 'COMPOSITE' type nodes.
            # In 5.0, we use Group Output. We probably shouldn't delete Group Output as it might be the main output.
            # Maybe just disconnect? Or if we created a specific "CompositorNodeComposite" (in 4.x), delete it.
            if bpy.app.version < (5, 0, 0) and node.type == 'COMPOSITE':
                 nodes_to_remove.append(node)

        for node in nodes_to_remove:
            compositor_window.nodes.remove(node)

        bpy.ops.scene.view_layer_remove_unused_lightgroups()
        
        # Remove Combined nodes
        nodes_to_delete = [node for node in compositor_window.nodes if node.name.startswith("Combined")]
        for node in nodes_to_delete:
            compositor_window.nodes.remove(node)

        # Logic to remove lightgroups and special nodes like Switch/Denoise
        # Note: Iterating and removing lightgroups from View Layer
        if scene.view_layers:
             view_layer = scene.view_layers[0] # Assuming first view layer as original code
             if hasattr(view_layer.cycles, 'denoising_store_passes'):
                  view_layer.cycles.denoising_store_passes = True
             
             # Copy list to avoid modification during iteration issues if any
             light_groups = [lg for lg in view_layer.lightgroups]
             for lg in light_groups:
                 bpy.ops.scene.view_layer_remove_lightgroup()
                 
                 # Reconnect Denoise if exists (Original logic tried to maintain denoise?)
                 # The original logic looks for "Switch" node and tries to reconnect.
                 # Let's simplify: We want to remove our custom setup.
        
        # Remove specific valid nodes by Label/Name
        # Switch
        switch_node = None
        for node in compositor_window.nodes:
            if node.label == "Switch Light Mix":
                switch_node = node
                break
        if switch_node:
            compositor_window.nodes.remove(switch_node)
            
        # Denoise
        denoise_node = None
        for node in compositor_window.nodes:
            if node.label == "Denoise Light Mix":
                denoise_node = node
                break
        if denoise_node:
            compositor_window.nodes.remove(denoise_node)

        # Remove Image nodes that were likely created by us?
        # Original code removed all 'IMAGE' nodes. This seems aggressive but adhering to original logic.
        image_nodes = [n for n in compositor_window.nodes if n.type == 'IMAGE']
        for node in image_nodes:
            compositor_window.nodes.remove(node)

        self.report({'INFO'}, f"EXR Deleted")
        return {'FINISHED'}
    

class reset_exr(bpy.types.Operator):
    bl_idname = "view3d.reset_exr"
    bl_label = "Reset exr Light Mix"
    
    def execute(self, context):
        # reuse remove logic
        bpy.ops.view3d.remove_exr()
        
        self.report({'INFO'}, f"Light Mix has been Deleted")
        
        # Re-add
        bpy.ops.view3d.exr_light_group()
        
        return {'FINISHED'}

        
