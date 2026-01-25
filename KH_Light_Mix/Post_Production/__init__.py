from sqlite3 import Row
import bpy
import bpy, os

# Helper function for Blender 5.0+ compositor compatibility
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

def set_glare_type(glare_node, glare_type_value):
    """Set glare type with Blender 5.0+ compatibility (options as inputs)"""
    if bpy.app.version >= (5, 0, 0):
        # In Blender 5.0, Input[1] is 'Glare Type' (Enum/String)
        # We try to set it by name first, if not browse inputs
        gt_input = None
        if 'Glare Type' in glare_node.inputs:
            gt_input = glare_node.inputs['Glare Type']
        elif len(glare_node.inputs) > 1:
            gt_input = glare_node.inputs[1]
            
        if gt_input:
            # Mapping common values to standard Blender 5.0 enum strings
            glare_type_map = {
                'BLOOM': 'Bloom', 'Bloom': 'Bloom',
                'GHOSTS': 'Ghosts', 'Ghosts': 'Ghosts',
                'STREAKS': 'Streaks', 'Streaks': 'Streaks',
                'FOG_GLOW': 'Fog Glow', 'Fog Glow': 'Fog Glow',
                'SIMPLE_STAR': 'Simple Star', 'Simple Star': 'Simple Star',
                'SUN_BEAMS': 'Sun Beams', 'Sun Beams': 'Sun Beams',
                'KERNEL': 'Kernel', 'Kernel': 'Kernel'
            }
            mapped_value = glare_type_map.get(glare_type_value, glare_type_value)
            gt_input.default_value = mapped_value
    else:
        # Blender 4.x: glare_type is a property
        glare_node.glare_type = glare_type_value

def set_glare_quality(glare_node, quality_value):
    """Set glare quality with Blender 5.0+ compatibility (options as inputs)"""
    if bpy.app.version >= (5, 0, 0):
        # Blender 5.0: quality is an input, enum values are 'High', 'Medium', 'Low'
        if 'Quality' in glare_node.inputs:
            # Convert old enum values to new ones
            quality_map = {
                'HIGH': 'High',
                'MEDIUM': 'Medium',
                'LOW': 'Low',
                'High': 'High',
                'Medium': 'Medium',
                'Low': 'Low'
            }
            mapped_value = quality_map.get(quality_value, quality_value)
            glare_node.inputs['Quality'].default_value = mapped_value
    else:
        # Blender 4.x: quality is a property
        if hasattr(glare_node, 'quality'):
            glare_node.quality = quality_value

def set_glare_mix(glare_node, mix_value):
    """Set glare mix with Blender 5.0+ compatibility (options as inputs)"""
    if bpy.app.version >= (5, 0, 0):
        # Blender 5.0: mix is an input
        if 'Mix' in glare_node.inputs:
            glare_node.inputs['Mix'].default_value = mix_value
    else:
        # Blender 4.x: mix is a property
        if hasattr(glare_node, 'mix'):
            glare_node.mix = mix_value

def set_glare_iterations(glare_node, iterations_value):
    """Set glare iterations with Blender 5.0+ compatibility (options as inputs)"""
    if bpy.app.version >= (5, 0, 0):
        # Blender 5.0: iterations is an input
        if 'Iterations' in glare_node.inputs:
            glare_node.inputs['Iterations'].default_value = iterations_value
    else:
        # Blender 4.x: iterations is a property
        if hasattr(glare_node, 'iterations'):
            glare_node.iterations = iterations_value

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

def get_glare_input(glare_node, input_name, input_index=None):
    """Get glare input by name or index, returns None if not found"""
    if input_name in glare_node.inputs:
        return glare_node.inputs[input_name]
    elif input_index is not None and len(glare_node.inputs) > input_index:
        return glare_node.inputs[input_index]
    return None

def add_nod(tree):
    nodes = tree.nodes
    links = tree.links
    
    # 1. Create/Get Group Node
    node_group_name = "KH-Post Group"
    if node_group_name not in bpy.data.node_groups:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        folder_path = os.path.join(script_dir, "asset")
        file_name = "KH-Post Group.blend"
        world_file_path = os.path.join(folder_path, file_name)
        with bpy.data.libraries.load(world_file_path, link=False) as (data_from, data_to):
            data_to.node_groups = [name for name in data_from.node_groups if name.startswith(node_group_name)]
            
    group_node = nodes.new('CompositorNodeGroup')
    group_node.node_tree = bpy.data.node_groups.get(node_group_name)
    group_node.label = "KH-Post Group"
    group_node.location = (800, 0)

    # 2. Setup IO Nodes
    r_layers = nodes.get('Render Layers') or nodes.new('CompositorNodeRLayers')
    composite = get_or_create_output_node(tree, nodes)
    
    # 3. Create ALL 7 Glare types in a chain
    glare_types = ['Bloom', 'Ghosts', 'Streaks', 'Fog Glow', 'Simple Star', 'Sun Beams', 'Kernel']
    previous_node = group_node
    
    # Connect Render Layers to Group
    links.new(r_layers.outputs['Image'], group_node.inputs[0])
    
    for i, g_type in enumerate(glare_types):
        g_node = nodes.new('CompositorNodeGlare')
        g_node.label = f"KH-Post {g_type.upper().replace(' ', '_')}"
        set_glare_type(g_node, g_type)
        set_glare_quality(g_node, 'HIGH')
        set_glare_mix(g_node, -0.8)
        g_node.mute = True
        g_node.location = (800 + (i+1)*250, 0)
        
        # Link in chain
        links.new(previous_node.outputs[0], g_node.inputs[0])
        previous_node = g_node

    # Link last node to composite and viewer
    if composite:
        composite.location = (previous_node.location.x + 300, 0)
        target_socket = composite.inputs[0] if bpy.app.version >= (5, 0, 0) else composite.inputs.get('Image')
        if target_socket:
            links.new(previous_node.outputs[0], target_socket)
            
    viewer = nodes.get("Viewer")
    if viewer:
        viewer.location = (previous_node.location.x + 300, -200)
        links.new(previous_node.outputs[0], viewer.inputs[0])


#Add post_production
class Post_Production(bpy.types.Operator):
    bl_idname = "object.post_production"
    bl_label = "Post Production"

    def execute(self, context):
        scene = context.scene
        tree = create_compositor_tree(scene)
        
        # Check if already active
        target_node = None
        for node in tree.nodes:
            if node.label == "KH-Post Group":
                target_node = node
                break
        
        if target_node is None:
            add_nod(tree)

        # UI Setup
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].shading.use_compositor = 'ALWAYS'
                
        self.report({'INFO'}, 'Post Production is activated with 7 Glare types')
        return {'FINISHED'}

#ClearCompositor///////////////////////////////////////////////////////////////////////////////////////////////////
    
class Clear_Compositor_Operator(bpy.types.Operator):
    bl_idname = "render.clear_compositor"
    bl_label = "Clear Compositor"

    def execute(self, context):
        # Get a reference to the current Compositor tree
        tree = get_compositor_tree(bpy.context.scene)
        # Enable use nodes in Compositor
        bpy.context.scene.use_nodes = True
        # Check if RLayers and Composite nodes exist
        tree = get_compositor_tree(bpy.context.scene)
        nodes = tree.nodes
        if 'Render Layers' not in nodes:
            r_layers = nodes.new('CompositorNodeRLayers')
            r_layers.location = (-100, 0)
        
        else:
            r_layers = nodes['Render Layers']
        composite = get_or_create_output_node(tree, nodes)
        if composite:
            composite.location = (1400, 0)

        switch_name = "KH-Post Group"
        switch_node = None
        tree = get_compositor_tree(bpy.context.scene)
        for node in tree.nodes:
            if node.label == switch_name:
                switch_node = node
                break
        if switch_node:
            connected_node = None
            # Find what is connected to switch input
            image_socket_name = 'Image' if 'Image' in switch_node.inputs else switch_node.inputs[0].name
            for link in tree.links:
                if link.to_node == switch_node and link.to_socket.name == image_socket_name:
                    connected_node = link.from_node
                    break
            
            if connected_node:
                composite_node = get_or_create_output_node(tree, tree.nodes)
                if composite_node:
                    target_socket = composite_node.inputs[0] if bpy.app.version >= (5, 0, 0) else composite_node.inputs.get('Image')
                    if target_socket:
                        tree.links.new(target_socket, connected_node.outputs[0])

                # Check for Viewer node
                viewer_node = None
                for n in tree.nodes:
                    if n.type == 'VIEWER':
                        viewer_node = n
                        break
                if viewer_node:
                    tree.links.new(viewer_node.inputs[0], connected_node.outputs[0])

        
        switch_name = "KH-Post Group"
        switch_node = None
        tree = get_compositor_tree(bpy.context.scene)
        for node in tree.nodes:
            if node.label == switch_name:
                switch_node = node
                break

        if switch_node:
            connected_nodes = []
            for link in tree.links:
                if link.to_node == switch_node and link.to_socket.name == 'Image':
                    connected_node = link.from_node
                    connected_nodes.append(connected_node)
                    tree.links.remove(link)

        self.report({'INFO'}, 'Rest Post Production')
        
        # Get a reference to the current Compositor tree
        tree = get_compositor_tree(bpy.context.scene)
        #bpy.context.space_data.shading.use_compositor = 'DISABLED'
        bpy.context.scene.use_nodes = True

        '''target_label = "KH-Post"
        compositor_window = get_compositor_tree(bpy.context.scene)
        for node in compositor_window.nodes:
            if node.label.startswith(target_label):
                compositor_window.nodes.remove(node)'''
                  
        # Delete all existing nodes
        #for node in tree.nodes:
           # tree.nodes.remove(node)
        return {'FINISHED'} 
    

#rest///////////////////////////////////////////////////////////////////////////////
class Rest_Composito_rOperator(bpy.types.Operator):
    bl_idname = "render.rest_compositor"
    bl_label = "Rest Compositor"

    def execute(self, context):
        tree = get_compositor_tree(context.scene)
        if not tree: return {'FINISHED'}
        
        # 1. Delete all KH-Post nodes
        for node in list(tree.nodes):
            if node.label.startswith("KH-Post"):
                tree.nodes.remove(node)
        
        # 2. Re-activate with all 7 nodes
        add_nod(tree)
        
        context.scene.view_settings.use_curve_mapping = False
        self.report({'INFO'}, 'Post Production Reset with 7 Glare types')
        return {'FINISHED'}

#Delete_Compositor////////////////////////////////////////////////////////////////////////////////////////////
class Delete_Compositor_Operator(bpy.types.Operator):
    bl_idname = "render.delete_compositor"
    bl_label = "Delete Compositor"

    def execute(self, context):
        # Get a reference to the current Compositor tree
        tree = get_compositor_tree(bpy.context.scene)
        # Enable use nodes in Compositor
        bpy.context.scene.use_nodes = True
        # Check if RLayers and Composite nodes exist
        tree = get_compositor_tree(bpy.context.scene)
        nodes = tree.nodes
        if 'Render Layers' not in nodes:
            r_layers = nodes.new('CompositorNodeRLayers')
            r_layers.location = (-100, 0)
        
        else:
            r_layers = nodes['Render Layers']
        composite = get_or_create_output_node(tree, nodes)
        if composite:
            composite.location = (1400, 0)

        switch_name = "KH-Post Group"
        switch_node = None
        tree = get_compositor_tree(bpy.context.scene)
        for node in tree.nodes:
            if node.label == switch_name:
                switch_node = node
                break
        if switch_node:
            connected_node = None
            for link in tree.links:
                if link.to_node == switch_node and link.to_socket.name == 'Image':
                    connected_node = link.from_node
                    break
            if connected_node:
                composite_node = tree.nodes.get("Composite")
                if composite_node:
                    tree.links.new(composite_node.inputs['Image'], connected_node.outputs[0])

                Viewer = tree.nodes.get("Viewer")
                if Viewer:
                    tree.links.new(Viewer.inputs['Image'], connected_node.outputs[0])
               

        self.report({'INFO'}, 'Post Production deleted')
        
        # Get a reference to the current Compositor tree
        tree = get_compositor_tree(bpy.context.scene)
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                bpy.context.window.scene = bpy.data.scenes[0]
                area.spaces[0].shading.use_compositor = 'DISABLED' 
        #bpy.context.space_data.shading.use_compositor = 'DISABLED'
        bpy.context.scene.use_nodes = True

        target_label = "KH-Post"
        compositor_window = get_compositor_tree(bpy.context.scene)
        for node in compositor_window.nodes:
            if node.label.startswith(target_label):
                compositor_window.nodes.remove(node)

        bpy.context.scene.view_settings.use_curve_mapping = False
         
        # Delete all existing nodes
        #for node in tree.nodes:
           # tree.nodes.remove(node)
        return {'FINISHED'}
    
#Activate Compositing //////////////////////////////////////////////////////////////////////////////////////////
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
    
# Switch.check = True ////////////////////////////////////////////////////////////////////////////////////////////
class Switch_On_Operator(bpy.types.Operator):
    bl_idname = "render.switch_on"
    bl_label = "Switch ON"
    
    def execute(self, context):
        compositor_window = get_compositor_tree(bpy.context.scene)
        if not compositor_window or not compositor_window.nodes:
            return {'CANCELLED'}
        # ابحث عن النود بالاسم "Switch Light Mix"
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
        compositor_window = get_compositor_tree(bpy.context.scene)
        if not compositor_window or not compositor_window.nodes:
            return {'CANCELLED'}
        # ابحث عن النود بالاسم "Switch Light Mix"
        Switch = None
        for node in compositor_window.nodes:
            if node.label == "Switch Light Mix":
                Switch = node
                break
        if Switch is not None:
            set_switch_check(Switch, False) 
        return {'FINISHED'}
    
# VIEW_3D' 'ALWAYS' ////////////////////////////////////////////////////////////////////////////////////////////
class VIEW_3D_ALWAYS_Operator(bpy.types.Operator):
    bl_idname = "render.view_always"
    bl_label = "Show in view port"
    
    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                bpy.context.window.scene = bpy.data.scenes[0] 
                area.spaces[0].shading.use_compositor = 'ALWAYS'
                break
            return {'FINISHED'}

    
class VIEW_3D_DISABLED_Operator(bpy.types.Operator):
    bl_idname = "render.view_disabled"
    bl_label = "Show in viewport"
    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                bpy.context.window.scene = bpy.data.scenes[0] 
                area.spaces[0].shading.use_compositor = 'DISABLED'
                break
            return {'FINISHED'}
       
# Post Production PROPERTIES////////////////////////////////////////////////////////////////////
class Post_Production_Panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_post_product_panel"
    bl_label = "Post Production"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "KH-Tools"
    bl_options = {'DEFAULT_CLOSED'}

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
                text="", icon='SHADERFX')
        except KeyError:
            pass
        
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Import the helper function from parent module
        from .. import get_scene_compositor
        
        scene = bpy.context.scene
        # Check if compositor is set up (5.0+) or use_nodes (4.x)
        has_compositor = (bpy.app.version >= (5, 0, 0) and scene.compositing_node_group is not None) or \
                       (bpy.app.version < (5, 0, 0) and scene.use_nodes == True)
        
        if not has_compositor:
            layout = self.layout
            box = layout.box()
            row = box.row(align=True)           
            row.operator("object.post_production", text="Activate")
        else:
            compositor_window = get_scene_compositor(scene)
            if not compositor_window or not compositor_window.nodes:
                box = layout.box()
                row = box.row(align=True)
                row.operator("object.post_production", text="Activate", icon='QUIT')
                return
            
            Switch = None
            for node in compositor_window.nodes:
                if node.label == "Switch Light Mix":
                    Switch = node
                    break
            
            # Display Switch Light Mix toggle
            if Switch is not None:
                box = layout.box()
                row = box.row(align=True)
                if get_switch_check(Switch) == False:
                    row.operator("render.switch_on", text="Light Mix", icon='CHECKBOX_DEHLT')  
                else:
                    row.operator("render.switch_off", text="Light Mix", icon='CHECKBOX_HLT')
                    box = layout.box()
                    row = box.row(align=True)
                    row.operator("render.switch_off", text="Fixt Black Screen", icon='ERROR')
                    
                    # Display Light Mix list when Switch is enabled
                    if compositor_window:
                        node_tree = compositor_window
                        render_layer_node_name = "Render Layers" if "Render Layers" in compositor_window.nodes else "Image"
                        
                        if render_layer_node_name in compositor_window.nodes:
                            render_layer_node = compositor_window.nodes[render_layer_node_name]
                            outputs = [output for output in render_layer_node.outputs if output.name.startswith("Combined_")]
                            for i, output in enumerate(outputs):
                                exposure_name = output.name.replace("Combined_", "")
                                exposure_name1 = exposure_name.split(' /')[0]
                                exposure_name2 = output.name.replace("Combined_", "").replace('C-', '').replace('/', '|').replace('_', '.')
                                exposure_name3 = exposure_name1.replace('M-', '').replace('_', '.')
                                
                                exposure_node = None
                                if Switch is not None:
                                    if get_switch_check(Switch) == True:
                                        exposure_node = next((node for node in node_tree.nodes if exposure_name in node.name), None)
                                
                                if exposure_node:
                                    box = layout.box()
                                    row = box.row(align=True)
                                    
                                    if 'M-' in exposure_name:
                                        row.label(text=exposure_name3, icon='MATERIAL')
                                        row.prop(exposure_node, "mute", text="", icon='SETTINGS')
                                    elif '1-' in exposure_name:
                                        row.label(text=exposure_name2, icon='LIGHT_DATA')
                                        row.prop(exposure_node, "mute", text="", icon='SETTINGS')
                                    elif 'World' in exposure_name:
                                        row.label(text=exposure_name, icon='WORLD')
                                        row.prop(exposure_node, "mute", text="", icon='SETTINGS')
                                    else:
                                        row.label(text=exposure_name2, icon='OUTLINER_COLLECTION')
                                        row.prop(exposure_node, "mute", text="", icon='SETTINGS')
                                    
                                    if not exposure_node.mute:
                                        row.prop(exposure_node.inputs[2], "default_value", text="")
                                        row.scale_y = 0.9
                                        row = box.row(align=True)
                                        row.prop(exposure_node.inputs[4], "default_value", text="", slider=True)
                                        row.scale_y = 0.9
                                        row.scale_x = 0.5
                                        row.prop(exposure_node.inputs[3], "default_value", text="")
            
            target_node_name = "KH-Post Group"
            target_node = None
            # Use the same compositor_window from above, or get it if not set
            if 'compositor_window' not in locals() or compositor_window is None:
                compositor_window = get_compositor_tree(bpy.context.scene)
            if not compositor_window or not compositor_window.nodes:
                box = layout.box()
                row = box.row(align=True)
                row.operator("object.post_production", text="Activate", icon='QUIT')
                return
            
            for node1 in compositor_window.nodes:
                if node1.label == target_node_name:
                    target_node = node1
                    break
            
            if target_node is None:
                box = layout.box()
                row = box.row(align=True)
                row.operator("object.post_production", text="Activate", icon='QUIT')
            else:
                box = layout.box()
                row = box.row(align=True)
                scene = bpy.context.scene
                node_tree = compositor_window
                
                glare_node = None
                for node in node_tree.nodes:
                    if node.label == "KH-Post SIMPLE_STAR":
                        glare_node = node
                        break
                
                Group_node = None
                for node in node_tree.nodes:
                    if node.label == "KH-Post Group":
                        Group_node = node
                        break
                    
                glare1_node = None
                for node in node_tree.nodes:
                    if node.label == "KH-Post FOG_GLOW":
                        glare1_node = node
                        break
                    
                composite_node = None
                for node in node_tree.nodes:
                    if bpy.app.version >= (5, 0, 0):
                        # Blender 5.0+: Use GROUP_OUTPUT
                        if node.type == 'GROUP_OUTPUT':
                            composite_node = node
                            break
                    else:
                        # Blender 4.x: Use COMPOSITE
                        if node.type == 'COMPOSITE':
                            composite_node = node
                            break
                
                if glare_node and composite_node:
                    # Check if linked based on Blender version
                    is_composite_linked = False
                    if bpy.app.version >= (5, 0, 0):
                        # Blender 5.0+: NodeGroupOutput uses first input
                        if len(composite_node.inputs) > 0:
                            is_composite_linked = composite_node.inputs[0].is_linked
                    else:
                        # Blender 4.x: CompositorNodeComposite uses 'Image' input
                        if "Image" in composite_node.inputs:
                            is_composite_linked = composite_node.inputs["Image"].is_linked
                    
                    if glare_node.outputs["Image"].is_linked and is_composite_linked:
                        row.operator("render.clear_compositor", text="Disable", icon='RESTRICT_RENDER_ON')                            
                    else:
                        row.operator("object.post_production", text="Activate", icon='QUIT')
                
                box = layout.box()
                row = box.row(align=True)
                row.operator("render.rest_compositor", text="Rest", icon= 'FILE_REFRESH')
                row.operator("render.delete_compositor", text="Delete", icon= 'TRASH')

                if glare_node and composite_node:
                    # Check if linked based on Blender version
                    is_composite_linked = False
                    if bpy.app.version >= (5, 0, 0):
                        # Blender 5.0+: NodeGroupOutput uses first input
                        if len(composite_node.inputs) > 0:
                            is_composite_linked = composite_node.inputs[0].is_linked
                    else:
                        # Blender 4.x: CompositorNodeComposite uses 'Image' input
                        if "Image" in composite_node.inputs:
                            is_composite_linked = composite_node.inputs["Image"].is_linked
                    
                    if glare_node.outputs["Image"].is_linked and is_composite_linked:
                        comp_nodes = get_compositor_tree(context.scene)
                        if not comp_nodes:
                            return
                        
                        # Find Group_node if not already found
                        if Group_node is None:
                            for node in node_tree.nodes:
                                if node.label == "KH-Post Group":
                                    Group_node = node
                                    break

                        if Group_node is not None:
                            if bpy.context.scene.use_nodes:
                                box = layout.box()
                                
                                box.label(text="Color :", icon= 'COLOR')
                                box.prop(Group_node.inputs[1], "default_value", text="Tint")
                                box.prop(Group_node.inputs[2], "default_value", text="Saturation")
                                box.prop(scene.view_settings, "use_curve_mapping", text="Color balance", toggle=True)
                                if scene.view_settings.use_curve_mapping :
                                    box.prop(context.scene, "temperature_value", text="Temperature", slider=True)
                                    box.prop(scene.view_settings.curve_mapping,"white_level", index=0, text="Red")
                                    box.prop(scene.view_settings.curve_mapping,"white_level", index=1, text="Green")
                                    box.prop(scene.view_settings.curve_mapping,"white_level", index=2, text="Blue")

                                box.label(text="Brightness/Contrast", icon= 'BRUSHES_ALL')                               
                                box.prop(Group_node.inputs[3], "default_value", text="Exposure", slider=True) 
                                box.prop(Group_node.inputs[4], "default_value", text="Brightness")      
                                box.prop(Group_node.inputs[5], "default_value", text="Gamma")
                                
                                box = layout.box()
                                box.label(text="Shadow :", icon= 'SHADING_RENDERED')
                                box.prop(Group_node.inputs[6], "default_value", text="Brightness")
                                box.prop(Group_node.inputs[7], "default_value", text="Contrast") 
                                
                                box = layout.box()
                                box.label(text="Details :", icon= 'GRIP')
                                box.prop(Group_node.inputs[8], "default_value", text="Sharpens") 
                                box.prop(Group_node.inputs[9], "default_value", text="Details")
                                
                            
                            
                            
                            # Draw the checkbox to enable/disable mute
                        # Find all Glare nodes starting with KH-Post
                        kh_glares = [n for n in node_tree.nodes if n.type == 'GLARE' and n.label.startswith("KH-Post")]
                        # Sort them by location X to keep order (Bloom -> Kernel)
                        kh_glares.sort(key=lambda n: n.location.x)

                        for i, g_node in enumerate(kh_glares):
                            # Determine dynamic title
                            type_label = g_node.label.replace("KH-Post ", "").replace("_", " ").title()
                            
                            box = layout.box() 
                            header = box.row()
                            header.label(text=type_label, icon='LIGHT_SUN') 
                            
                            # Access dynamic active property
                            tab_idx = (i % 7) + 1
                            active_prop = f"kh_post_glare{tab_idx}_active"
                            header.prop(scene, active_prop, text="")
                            
                            if getattr(scene, active_prop):
                                # Access dynamic tab property
                                tab_prop = f"kh_post_glare{tab_idx}_tab"
                                
                                row = box.row(align=True)
                                if hasattr(scene, tab_prop):
                                    row.prop(scene, tab_prop, expand=True)
                                else:
                                    # Fallback if property not yet registered
                                    row.label(text="Tabs Loading...")
                                    continue
                                
                                current_tab = getattr(scene, tab_prop)
                                inner_box = box.box()
                                
                                if current_tab == 'MAIN':
                                    if bpy.app.version >= (5, 0, 0):
                                        if len(g_node.inputs) > 1:
                                            inner_box.prop(g_node.inputs[1], "default_value", text="Glare Type")
                                        if 'Quality' in g_node.inputs:
                                            inner_box.prop(g_node.inputs['Quality'], "default_value", text="Quality")
                                        if 'Mix' in g_node.inputs:
                                            inner_box.prop(g_node.inputs['Mix'], "default_value", text="Mix", slider=True)
                                    else:
                                        inner_box.prop(g_node, "glare_type")
                                        inner_box.prop(g_node, "quality")
                                        inner_box.prop(g_node, "mix", slider=True)
                                        
                                elif current_tab == 'HIGHLIGHTS':
                                    if bpy.app.version >= (5, 0, 0):
                                        threshold_input = get_glare_input(g_node, 'Threshold', 3)
                                        if threshold_input: inner_box.prop(threshold_input, "default_value", text="Threshold")
                                        smoothness_input = get_glare_input(g_node, 'Smoothness', 4)
                                        if smoothness_input: inner_box.prop(smoothness_input, "default_value", text="Smoothness", slider=True)
                                        clamp_input = get_glare_input(g_node, 'Clamp', 5)
                                        if clamp_input: inner_box.prop(clamp_input, "default_value", text="Clamp")
                                        maximum_input = get_glare_input(g_node, 'Maximum', 6)
                                        if maximum_input: inner_box.prop(maximum_input, "default_value", text="Maximum")
                                    else:
                                        inner_box.prop(g_node, "threshold")
                                        
                                elif current_tab == 'ADJUST':
                                    if bpy.app.version >= (5, 0, 0):
                                        strength_input = get_glare_input(g_node, 'Strength', 7)
                                        if strength_input: inner_box.prop(strength_input, "default_value", text="Strength", slider=True)
                                        saturation_input = get_glare_input(g_node, 'Saturation', 8)
                                        if saturation_input: inner_box.prop(saturation_input, "default_value", text="Saturation", slider=True)
                                        tint_input = get_glare_input(g_node, 'Tint', 9)
                                        if tint_input: inner_box.prop(tint_input, "default_value", text="Tint")
                                    else:
                                        inner_box.label(text="Adjust: Standard property in 5.0")

                                elif current_tab == 'GLARE':
                                    if bpy.app.version >= (5, 0, 0):
                                        g_mode = g_node.inputs[1].default_value if len(g_node.inputs) > 1 else "None"
                                        
                                        if g_mode in ['Bloom', 'Fog Glow', 'Sun Beams']:
                                            size_input = get_glare_input(g_node, 'Size', 15)
                                            if size_input: inner_box.prop(size_input, "default_value", text="Size", slider=True)
                                        
                                        if g_mode == 'Kernel':
                                            k_type = get_glare_input(g_node, 'Kernel Data Type', 20)
                                            if k_type: inner_box.prop(k_type, "default_value", text="Data Type")
                                            # k_val = get_glare_input(g_node, 'Kernel', 21)
                                            # if k_val: inner_box.prop(k_val, "default_value", text="Kernel")

                                        if g_mode in ['Ghosts', 'Streaks', 'Simple Star']:
                                            iter_input = get_glare_input(g_node, 'Iterations', 12)
                                            if iter_input: inner_box.prop(iter_input, "default_value", text="Iterations")
                                        
                                        if g_mode in ['Streaks', 'Simple Star']:
                                            fade_input = get_glare_input(g_node, 'Fade', 14)
                                            if fade_input: inner_box.prop(fade_input, "default_value", text="Fade", slider=True)
                                    
                                        if g_mode == 'Sun Beams':
                                            sun_pos = get_glare_input(g_node, 'Sun Position', 17)
                                            if sun_pos: inner_box.prop(sun_pos, "default_value", text="Sun Position")
                                            jitter = get_glare_input(g_node, 'Jitter', 18)
                                            if jitter: inner_box.prop(jitter, "default_value", text="Jitter", slider=True)

                                        if g_mode in ['Streaks', 'Ghosts']:
                                            cmod_input = get_glare_input(g_node, 'Color Modulation', 11)
                                            if cmod_input: inner_box.prop(cmod_input, "default_value", text="Color Modulation", slider=True)
                                            
                                        if g_mode == 'Streaks':
                                            streaks_in = get_glare_input(g_node, 'Streaks', 13)
                                            if streaks_in: inner_box.prop(streaks_in, "default_value", text="Streaks")
                                            angle_in = get_glare_input(g_node, 'Streaks Angle', 16)
                                            if angle_in: inner_box.prop(angle_in, "default_value", text="Streaks Angle")

                                        if g_mode == 'Simple Star':
                                            diag_input = get_glare_input(g_node, 'Diagonal', 19)
                                            if diag_input: inner_box.prop(diag_input, "default_value", text="Diagonal")
                                    else:
                                        if hasattr(g_node, 'size'): inner_box.prop(g_node, "size")
                                        if hasattr(g_node, 'iterations'): inner_box.prop(g_node, "iterations")
       


class Post_Productions_IMAGE_EDITOR_Panel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_post_productions_image_editor"
    bl_label = "Post Production"
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
                text="", icon='SHADERFX')
        except KeyError:
            pass        

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Check if compositor is set up (5.0+) or use_nodes (4.x)
        has_compositor = (bpy.app.version >= (5, 0, 0) and scene.compositing_node_group is not None) or \
                       (bpy.app.version < (5, 0, 0) and scene.use_nodes == True)
        
        if not has_compositor:
            layout = self.layout
            box = layout.box()
            row = box.row(align=True)           
            row.operator("object.post_production", text="Activate")
        else:
            compositor_window = get_compositor_tree(bpy.context.scene)
            if not compositor_window:
                return
            render_layers = compositor_window.nodes.get("Render Layers")
            if render_layers :
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
                    target_node_name = "KH-Post Group"
                    compositor = get_compositor_tree(bpy.context.scene)
                    target_node = None
                    for node in compositor.nodes:
                        if node.label == target_node_name:
                            target_node = node
                            break
                    if target_node is None:
                        box = layout.box()
                        row = box.row(align=True)
                        row .operator("object.post_production", text="Activate", icon='QUIT')
                    else:
                        box = layout.box()
                        row = box.row(align=True)
                        scene = bpy.context.scene
                        node_tree = get_compositor_tree(scene)
                        if not node_tree:
                            return
                        
                        glare_node = None
                        for node in node_tree.nodes:
                            if node.label == "KH-Post SIMPLE_STAR":
                                glare_node = node
                                break
                        
                        Group_node = None
                        for node in node_tree.nodes:
                            if node.label == "KH-Post Group":
                                Group_node = node
                                break
                            
                        glare1_node = None
                        for node in node_tree.nodes:
                            if node.label == "KH-Post FOG_GLOW":
                                glare1_node = node
                                break
                            
                        # Get composite/output node based on Blender version
                        composite_node = None
                        if bpy.app.version >= (5, 0, 0):
                            # Blender 5.0+: Look for NodeGroupOutput
                            for node in node_tree.nodes:
                                if node.type == 'GROUP_OUTPUT':
                                    composite_node = node
                                    break
                        else:
                            # Blender 4.x: Look for CompositorNodeComposite
                            for node in node_tree.nodes:
                                if node.type == 'COMPOSITE':
                                    composite_node = node
                                    break
                        
                        if glare_node and composite_node:
                            # Check if linked based on Blender version
                            is_composite_linked = False
                            if bpy.app.version >= (5, 0, 0):
                                # Blender 5.0+: NodeGroupOutput uses first input
                                if len(composite_node.inputs) > 0:
                                    is_composite_linked = composite_node.inputs[0].is_linked
                            else:
                                # Blender 4.x: CompositorNodeComposite uses 'Image' input
                                if "Image" in composite_node.inputs:
                                    is_composite_linked = composite_node.inputs["Image"].is_linked
                            
                            if glare_node.outputs["Image"].is_linked and is_composite_linked:                               
                                row.operator("render.clear_compositor", text="Disable", icon='RESTRICT_RENDER_ON')
                            else:
                                row.operator("object.post_production", text="Activate", icon='QUIT')
                        row = box.row(align=True)
                        row.operator("render.rest_compositor", text="Rest", icon= 'FILE_REFRESH')
                        row.operator("render.delete_compositor", text="Delete", icon= 'TRASH')
                        
                        box = layout.box()
                        box.prop(scene, "color_management_enabled" , icon='IMAGE_DATA', toggle=False)
                        if scene.color_management_enabled:
                            box.prop(scene.view_settings, "view_transform")
                            box.prop(scene.view_settings, "look")
                            box.prop(scene.view_settings, "exposure")
                            box.prop(scene.view_settings, "gamma")
                                                 
                            

                        if glare_node and composite_node:
                            # Check if linked based on Blender version
                            is_composite_linked = False
                            if bpy.app.version >= (5, 0, 0):
                                # Blender 5.0+: NodeGroupOutput uses first input
                                if len(composite_node.inputs) > 0:
                                    is_composite_linked = composite_node.inputs[0].is_linked
                            else:
                                # Blender 4.x: CompositorNodeComposite uses 'Image' input
                                if "Image" in composite_node.inputs:
                                    is_composite_linked = composite_node.inputs["Image"].is_linked
                            
                            # Display options if nodes exist (regardless of linking)
                            if glare_node or glare1_node or Group_node:
                                comp_nodes = get_compositor_tree(context.scene)
                                if not comp_nodes:
                                    return
                                comp_nodes = comp_nodes.nodes
                                
                                # Find Group_node if not already found
                                if Group_node is None:
                                    for node in node_tree.nodes:
                                        if node.label == "KH-Post Group":
                                            Group_node = node
                                            break

                                if Group_node is not None:
                                    if bpy.context.scene.use_nodes:
                                        box = layout.box()
                                        
                                        box.label(text="Color :", icon= 'COLOR')
                                        box.prop(Group_node.inputs[1], "default_value", text="Tint")
                                        box.prop(Group_node.inputs[2], "default_value", text="Saturation")
                                        box.prop(scene.view_settings, "use_curve_mapping", text="Color balance", toggle=True)
                                        if scene.view_settings.use_curve_mapping :
                                            box.prop(context.scene, "temperature_value", text="Temperature", slider=True)
                                            box.prop(scene.view_settings.curve_mapping,"white_level", index=0, text="Red")
                                            box.prop(scene.view_settings.curve_mapping,"white_level", index=1, text="Green")
                                            box.prop(scene.view_settings.curve_mapping,"white_level", index=2, text="Blue")

                                        box.label(text="Brightness/Contrast", icon= 'BRUSHES_ALL')                               
                                        box.prop(Group_node.inputs[3], "default_value", text="Exposure", slider=True) 
                                        box.prop(Group_node.inputs[4], "default_value", text="Brightness")      
                                        box.prop(Group_node.inputs[5], "default_value", text="Gamma")
                                        
                                        box = layout.box()
                                        box.label(text="Shadow :", icon= 'SHADING_RENDERED')
                                        box.prop(Group_node.inputs[6], "default_value", text="Brightness")
                                        box.prop(Group_node.inputs[7], "default_value", text="Contrast") 
                                        
                                        box = layout.box()
                                        box.label(text="Details :", icon= 'GRIP')
                                        box.prop(Group_node.inputs[8], "default_value", text="Sharpens") 
                                        box.prop(Group_node.inputs[9], "default_value", text="Details") 
                                    
                                # Find all Glare nodes starting with KH-Post
                                kh_glares = [n for n in node_tree.nodes if n.type == 'GLARE' and n.label.startswith("KH-Post")]
                                # Sort them by location X to keep order (Bloom -> Kernel)
                                kh_glares.sort(key=lambda n: n.location.x)

                                for i, g_node in enumerate(kh_glares):
                                    # Determine dynamic title
                                    type_label = g_node.label.replace("KH-Post ", "").replace("_", " ").title()
                                    
                                    box = layout.box() 
                                    header = box.row()
                                    header.label(text=type_label, icon='LIGHT_SUN') 
                                    
                                    # Access dynamic active property
                                    tab_idx = (i % 7) + 1
                                    active_prop = f"kh_post_glare{tab_idx}_active"
                                    header.prop(scene, active_prop, text="")
                                    
                                    if getattr(scene, active_prop):
                                        # Access dynamic tab property
                                        tab_prop = f"kh_post_glare{tab_idx}_tab"
                                        
                                        row = box.row(align=True)
                                        if hasattr(scene, tab_prop):
                                            row.prop(scene, tab_prop, expand=True)
                                        else:
                                            row.label(text="Tabs Loading...")
                                            continue
                                        
                                        current_tab = getattr(scene, tab_prop)
                                        inner_box = box.box()
                                        
                                        if current_tab == 'MAIN':
                                            if bpy.app.version >= (5, 0, 0):
                                                gt_input = get_glare_input(g_node, 'Glare Type', 1)
                                                if gt_input:
                                                    inner_box.prop(gt_input, "default_value", text="Type")
                                                if 'Quality' in g_node.inputs:
                                                    inner_box.prop(g_node.inputs['Quality'], "default_value", text="Quality")
                                                if 'Mix' in g_node.inputs:
                                                    inner_box.prop(g_node.inputs['Mix'], "default_value", text="Mix", slider=True)
                                            else:
                                                inner_box.prop(g_node, "glare_type")
                                                inner_box.prop(g_node, "quality")
                                                inner_box.prop(g_node, "mix", slider=True)
                                                
                                        elif current_tab == 'HIGHLIGHTS':
                                            if bpy.app.version >= (5, 0, 0):
                                                threshold_input = get_glare_input(g_node, 'Threshold', 3)
                                                if threshold_input: inner_box.prop(threshold_input, "default_value", text="Threshold")
                                                smoothness_input = get_glare_input(g_node, 'Smoothness', 4)
                                                if smoothness_input: inner_box.prop(smoothness_input, "default_value", text="Smoothness", slider=True)
                                                clamp_input = get_glare_input(g_node, 'Clamp', 5)
                                                if clamp_input: inner_box.prop(clamp_input, "default_value", text="Clamp")
                                                maximum_input = get_glare_input(g_node, 'Maximum', 6)
                                                if maximum_input: inner_box.prop(maximum_input, "default_value", text="Maximum")
                                            else:
                                                inner_box.prop(g_node, "threshold")
                                                
                                        elif current_tab == 'ADJUST':
                                            if bpy.app.version >= (5, 0, 0):
                                                strength_input = get_glare_input(g_node, 'Strength', 7)
                                                if strength_input: inner_box.prop(strength_input, "default_value", text="Strength", slider=True)
                                                saturation_input = get_glare_input(g_node, 'Saturation', 8)
                                                if saturation_input: inner_box.prop(saturation_input, "default_value", text="Saturation", slider=True)
                                                tint_input = get_glare_input(g_node, 'Tint', 9)
                                                if tint_input: inner_box.prop(tint_input, "default_value", text="Tint")
                                            else:
                                                inner_box.label(text="Adjust: Standard property in 5.0")

                                        elif current_tab == 'GLARE':
                                            if bpy.app.version >= (5, 0, 0):
                                                g_mode = g_node.inputs[1].default_value if len(g_node.inputs) > 1 else "None"
                                                
                                                if g_mode in ['Bloom', 'Fog Glow', 'Sun Beams']:
                                                    size_input = get_glare_input(g_node, 'Size', 15)
                                                    if size_input: inner_box.prop(size_input, "default_value", text="Size", slider=True)
                                                
                                                if g_mode == 'Kernel':
                                                    k_type = get_glare_input(g_node, 'Kernel Data Type', 20)
                                                    if k_type: inner_box.prop(k_type, "default_value", text="Data Type")
                                                    # k_val = get_glare_input(g_node, 'Kernel', 21)
                                                    # if k_val: inner_box.prop(k_val, "default_value", text="Kernel")

                                                if g_mode in ['Ghosts', 'Streaks', 'Simple Star']:
                                                    iter_input = get_glare_input(g_node, 'Iterations', 12)
                                                    if iter_input: inner_box.prop(iter_input, "default_value", text="Iterations")
                                                
                                                if g_mode in ['Streaks', 'Simple Star']:
                                                    fade_input = get_glare_input(g_node, 'Fade', 14)
                                                    if fade_input: inner_box.prop(fade_input, "default_value", text="Fade", slider=True)
                                            
                                                if g_mode == 'Sun Beams':
                                                    sun_pos = get_glare_input(g_node, 'Sun Position', 17)
                                                    if sun_pos: inner_box.prop(sun_pos, "default_value", text="Sun Position")
                                                    jitter = get_glare_input(g_node, 'Jitter', 18)
                                                    if jitter: inner_box.prop(jitter, "default_value", text="Jitter", slider=True)
                                                    
                                                if g_mode in ['Streaks', 'Ghosts']:
                                                    cmod_input = get_glare_input(g_node, 'Color Modulation', 11)
                                                    if cmod_input: inner_box.prop(cmod_input, "default_value", text="Color Modulation", slider=True)
                                                    
                                                if g_mode == 'Streaks':
                                                    streaks_in = get_glare_input(g_node, 'Streaks', 13)
                                                    if streaks_in: inner_box.prop(streaks_in, "default_value", text="Streaks")
                                                    angle_in = get_glare_input(g_node, 'Streaks Angle', 16)
                                                    if angle_in: inner_box.prop(angle_in, "default_value", text="Streaks Angle")

                                                if g_mode == 'Simple Star':
                                                    diag_input = get_glare_input(g_node, 'Diagonal', 19)
                                                    if diag_input: inner_box.prop(diag_input, "default_value", text="Diagonal")
                                            else:
                                                if hasattr(g_node, 'size'): inner_box.prop(g_node, "size")
                                                if hasattr(g_node, 'iterations'): inner_box.prop(g_node, "iterations")

                                        


def update_temperature_value(self, context):
    # تحديث قيمة index=0 وindex=1 وindex=2 عند تغيير درجة الحرارة
    temperature_value = context.scene.temperature_value
    white_level = context.scene.view_settings.curve_mapping.white_level

    # حساب التناسب بناءً على الشروط المطلوبة
    if temperature_value == 6500:
        context.scene.view_settings.curve_mapping.white_level[0] = 1
        context.scene.view_settings.curve_mapping.white_level[1] = 1
        context.scene.view_settings.curve_mapping.white_level[2] = 1
        
    elif temperature_value > 6500:
        proportion = (temperature_value - 6500) / 3600
        context.scene.view_settings.curve_mapping.white_level[0] = 1 + proportion
        context.scene.view_settings.curve_mapping.white_level[1] = 1
        context.scene.view_settings.curve_mapping.white_level[2] = 1 - proportion
        
    elif temperature_value < 6500:
        proportion = (temperature_value - 6500)/ 6200
        context.scene.view_settings.curve_mapping.white_level[0] = 1 + proportion
        context.scene.view_settings.curve_mapping.white_level[1] = 1
        context.scene.view_settings.curve_mapping.white_level[2] = 1 - proportion

# إضافة خاصية درجة الحرارة إلى السيناريو
bpy.types.Scene.temperature_value = bpy.props.FloatProperty(
    name="Temperature",
    description="Adjust Temperature",
    default=6500,
    min=1800,
    max=9999,
    update=update_temperature_value
)

           

