import bpy
        
def Activate_Node_Wrangler():
    addon_name = "node_wrangler"
    if addon_name not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module=addon_name)

def clear_node():
    active_material = bpy.context.object.active_material
    if active_material is not None:
        for node in active_material.node_tree.nodes:
            active_material.node_tree.nodes.remove(node)
        output_node = active_material.node_tree.nodes.new('ShaderNodeOutputMaterial')
        output_node.location = (400, 0)
        bsdf_node = active_material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        bsdf_node.location = (0, 0)
        active_material.node_tree.links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
        for node in active_material.node_tree.nodes:
            node.select = False
        bsdf_node.select = True
        active_material.node_tree.nodes.active = bsdf_node

def kh_show_preview():
    material = bpy.context.object.active_material
    if material and material.use_nodes:
        node_tree = material.node_tree
        nodes = node_tree.nodes
        for node in nodes:
            if hasattr(node, 'show_preview'):
                node.show_preview = not node.show_preview



class ActivateNodeWranglerOperator(bpy.types.Operator):
    bl_idname = "script.activate_node_wrangler"
    bl_label = "Activate Node Wrangler"
    
    def execute(self, context):
        Activate_Node_Wrangler()
        clear_node()
        return {'FINISHED'}
    

class kh_show_previewOperator(bpy.types.Operator):
    bl_idname = "script.kh_show_previewr"
    bl_label = "Show Node Preview"
    
    def execute(self, context):
        kh_show_preview()
        return {'FINISHED'}
    
class kh_PreviewPanel1(bpy.types.Panel):
    bl_label = "Material preview"
    bl_idname = "OBJECT_PT_material_preview1"
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
            self.layout.operator("script.activate_node_wrangler", text="Import Maps")
            self.layout.operator("node.nw_add_textures_for_principled", text="Maps",icon= "FILE_REFRESH")

def kh_activate_node_wrangler(self, context):
    KH = context.preferences.addons['KH-Tools'].preferences.KH_Material == True
    if KH and context.active_object is not None and context.object.active_material is not None: 
        self.layout.operator("script.activate_node_wrangler", text="Clean",icon= "FILE_REFRESH")
        self.layout.operator("node.nw_add_textures_for_principled", text="Import Maps",icon= "IMPORT")

        #self.layout.operator("script.kh_show_previewr", text="Preview",icon= "MATERIAL")
                    


# def register():
#     bpy.utils.register_class(ActivateNodeWranglerOperator)   
#     bpy.utils.register_class(PreviewPanel1)
#     bpy.types.NODE_MT_editor_menus.append(kh_activate_node_wrangler)

# def unregister():
#     bpy.utils.unregister_class(ActivateNodeWranglerOperator)
#     bpy.utils.unregister_class(PreviewPanel1)
#     bpy.types.NODE_MT_editor_menus.remove(kh_activate_node_wrangler)

# if __name__ == "__main__":
#     register()
