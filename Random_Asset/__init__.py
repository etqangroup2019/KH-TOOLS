#this is a free addon, you can use, edit and share this addon as you please! If you have any suggestions for the code, please let me know
bl_info = {
    "name" : "CLICKR",
    "author" : "OliverJPost",
    "description" : "Place objects, with some randomization",
    "blender" : (2, 81, 0),
    "version" : (1, 2,),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}


import bpy
import random
from bpy_extras import view3d_utils
from mathutils import Vector
from mathutils import Matrix, Vector
import numpy as np
import os
import json
import subprocess
import tempfile

def get_selected_assets_from_browser(context):
    """
    Exhaustive detection of assets for Blender 4.0/5.0+.
    Uses new 'selected_assets' property and older fallbacks.
    """
    assets = []
    processed_names = set()

    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'ASSETS' or area.ui_type == 'ASSETS':
                
                # Check regions to find the one with the assets
                for region in area.regions:
                    if region.type not in {'WINDOW', 'UI'}:
                        continue
                        
                    try:
                        with context.temp_override(window=window, area=area, region=region):
                            targets = []
                            
                            # 1. Try NEW Blender 4.0+ 'selected_assets' (AssetRepresentation)
                            new_sel = getattr(context, "selected_assets", None)
                            if new_sel: targets.extend(list(new_sel))
                            
                            # 2. Try 'selected_asset_files' (FileSelectEntry)
                            old_sel = getattr(context, "selected_asset_files", None)
                            if old_sel: targets.extend(list(old_sel))
                            
                            # 3. Try 'selected_asset_handles'
                            handles = getattr(context, "selected_asset_handles", None)
                            if handles: targets.extend(list(handles))
                            
                            # 4. Fallback to active items
                            if not targets:
                                for active_attr in ["active_asset", "asset_handle", "active_asset_file", "asset_file_handle"]:
                                    active = getattr(context, active_attr, None)
                                    if active:
                                        targets.append(active)
                                        break

                            for asset in targets:
                                if not asset or (hasattr(asset, "name") and asset.name in processed_names):
                                    continue
                                
                                # A. Detect LOCAL
                                local_id = None
                                if hasattr(asset, "local_id") and asset.local_id:
                                    local_id = asset.local_id
                                elif hasattr(asset, "id_metadata") and asset.id_metadata:
                                    # AssetRepresentation has id_metadata
                                    local_id = getattr(asset.id_metadata, "id", None)
                                
                                if local_id:
                                    assets.append({
                                        'name': getattr(asset, "name", "Unknown"),
                                        'type': 'LOCAL',
                                        'object': local_id
                                    })
                                    processed_names.add(getattr(asset, "name", "Unknown"))
                                    continue

                                # B. Detect EXTERNAL
                                path = ""
                                # Check multiple path attributes
                                for attr in ["full_path", "filepath", "full_library_path"]:
                                    val = getattr(asset, attr, "")
                                    if val: path = val; break
                                
                                # Check metadata
                                if not path and hasattr(asset, "metadata"):
                                    path = getattr(asset.metadata, "filepath", "")
                                
                                if path and ".blend" in path.lower():
                                    blend_path = path.rsplit(".blend", 1)[0] + ".blend"
                                    assets.append({
                                        'name': getattr(asset, "name", "Unknown"),
                                        'type': 'EXTERNAL',
                                        'blend_path': blend_path
                                    })
                                    processed_names.add(getattr(asset, "name", "Unknown"))
                                    
                    except Exception as e:
                        # Silently continue to next region/area
                        continue
                
                if assets: return assets
    
    return assets

# Random rotation and scale operators moved from Asset_Manager
class random_R(bpy.types.Operator):
    """
    random rotation
    """
    bl_idname = "random.rotation"
    bl_label = "random rotation"

    def execute(self, context):
        scene = bpy.context.scene
        selected_objects = bpy.context.selected_objects
        if selected_objects:
            for obj in selected_objects:
                if obj.type == 'MESH':
                    # Get the strength/intensity from scene property
                    strength = scene.random_rotation_strength
                    # Apply strength to the rotation angle (0.0 = no rotation, 1.0 = full rotation)
                    max_rotation = 2 * 3.141592653589793  # Full 360 degrees in radians
                    rotation_angle = random.uniform(0, max_rotation * strength)
                    obj.rotation_euler[2] += rotation_angle

        return {'FINISHED'}
    
class Delete_random_R(bpy.types.Operator):
    """
    Delete random rotation
    """
    bl_idname = "delete_random.rotation"
    bl_label = "Delete random rotation"

    def execute(self, context):
        scene = bpy.context.scene
        selected_objects = bpy.context.selected_objects
        if selected_objects:
            for obj in selected_objects:
                if obj.type == 'MESH':
                    current_rotation = obj.rotation_euler
                    # ضبط الروتيشن لتكون z = 0
                    obj.rotation_euler = (current_rotation[0], current_rotation[1], 0)
        
        return {'FINISHED'}
    
class random_s(bpy.types.Operator):
    """
    random scale
    """
    bl_idname = "random.scale"
    bl_label = "random scale"

    def execute(self, context):
        scene = bpy.context.scene
        selected_obj = bpy.context.selected_objects
        if selected_obj is not None:
            for obj in selected_obj:
                if obj.type == 'MESH':
                    # Get the strength/intensity from scene property
                    strength = scene.random_scale_strength
                    # Apply strength to the scale variation (0.0 = no scaling, 1.0 = full scaling)
                    # Base scale variation of 0.1 (10%) multiplied by strength
                    scale_variation = 0.1 * strength

                    selected_objects_names = [obj.name for obj in context.selected_objects]
                    bpy.ops.object.randomize_transform(
                        random_seed=random.randint(0, 10000),
                        use_loc=False,
                        scale=(1.0 + scale_variation, 1.0 + scale_variation, 1.0 + scale_variation),
                        scale_even=True
                    )

        return {'FINISHED'}
    
class Delete_random_s(bpy.types.Operator):
    """
    Delete random scale
    """
    bl_idname = "delete_random.scale"
    bl_label = "Delete random scale"

    def execute(self, context):
        scale_factor = 1
        
        selected_obj = bpy.context.selected_objects
        if selected_obj is not None:
            for obj in selected_obj:
               if obj.type == 'MESH':
                    obj.scale = (scale_factor, scale_factor, scale_factor)
        
        return {'FINISHED'}

# Check functions for rotation and scale
def check_scale(object):
    if object.scale[0] != 1 or object.scale[1] != 1 or object.scale[2] != 1:
        return False
    return True

def check_Rotation(object):
    if object.rotation_euler[2] != 0:
        return False
    return True

# UI List for displaying ground surfaces
class CLICKR_UL_SURFACE_LIST(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Check if the object still exists
            obj_exists = item.object_name in bpy.data.objects
            if obj_exists:
                layout.label(text=item.name, icon='MESH_PLANE')
            else:
                layout.label(text=f"{item.name} (Missing)", icon='ERROR')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='MESH_PLANE')

class CLICKR_PT_PANEL(bpy.types.Panel):
    bl_idname = "CLICKR_PT_Panel"
    bl_label = "Random Asset"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "KH-Tools"
    #bl_parent_id   = "OBJECT_PT_kh_asset"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context: bpy.types.Context):
        try:
            self.layout.label(
                text="", icon='MOUSE_LMB')
        except KeyError:
            pass

    def draw(self, context):
        settings  = context.scene.CLICKR
        layout = self.layout

        # Random Rotation and Scale Tools
        box = layout.box()
        row = box.row()
        row.label(text="Random Tools:", icon='OUTLINER_DATA_POINTCLOUD')
        
        # Random Rotation
        row = box.row()
        row.operator("random.rotation", text="Random Rotation", icon='MOUSE_LMB')
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            if obj.type == 'MESH':
                if not check_Rotation(obj):
                    row.operator("delete_random.rotation", text="", icon='TRASH')
                    break
        # Add rotation strength slider
        row = box.row()
        row.prop(context.scene, "random_rotation_strength", text="Rotation Strength", slider=True)

        # Random Scale
        row = box.row()
        row.operator("random.scale", text="Random Scale", icon='MOUSE_LMB')
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            if obj.type == 'MESH':
                if not check_scale(obj):
                    row.operator("delete_random.scale", text="", icon='TRASH')
                    break
        # Add scale strength slider
        row = box.row()
        row.prop(context.scene, "random_scale_strength", text="Scale Strength", slider=True)
        

        # Ground Surfaces Section
        box = layout.box()
        row = box.row()
        row.label(text="Ground Surfaces:", icon='OUTLINER_OB_LIGHTPROBE')

        # Surface Mode Selection
        row = box.row()
        row.prop(settings, "surface_mode", expand=True)

        # Show surface list only in SPECIFIC mode
        if settings.surface_mode == 'SPECIFIC':
            # Surface List
            row = box.row()
            row.template_list("CLICKR_UL_SURFACE_LIST", "", settings, "surface_list",
                             settings, "surface_list_index", rows=3)

            # Add/Remove buttons
            col = row.column(align=True)
            col.operator("clickr.add_surface", text="", icon='ADD')
            col.operator("clickr.remove_surface", text="", icon='REMOVE')
        else:
            # Show info for ALL mode
            row = box.row()
            row.label(text="Will snap to all mesh objects in scene", icon='INFO')

        # Legacy single surface support (for backward compatibility)
        if settings.clickr_surface != 'None':
            row = box.row()
            row.label(text=f"Legacy Surface: {settings.clickr_surface}", icon='INFO')
            row = box.row()
            row.operator("clickr.surface", text="Select Ground Surface", icon='RESTRICT_SELECT_OFF')

        # Object Source Section
        box = layout.box()
        row = box.row()
        row.label(text="Object Source:", icon='OBJECT_DATA')
        
        row = box.row()
        row.prop(settings, "object_source", expand=True)
        
        # Show Asset Library info when Asset Library mode is selected
        if settings.object_source == 'ASSET_LIBRARY':
            row = box.row()
            row.label(text="Uses assets selected in Asset Browser", icon='INFO')
        else:
            row = box.row()
            row.label(text="Select objects in scene to place", icon='INFO')

        # Start Clicking button
        row = box.row()
        row.operator("clickr.modal", text="Start Clicking", icon='MOUSE_LMB')

        # Randomization Settings
        row = box.row()
        row.label(text="Randomize :", icon='STICKY_UVS_DISABLE')
        row = box.row()
        row.prop(settings, 'clickr_rotation', slider=True)
        row = box.row()
        row.prop(settings, 'clickr_askew', slider = True)
        row = box.row()
        row.prop(settings, 'clickr_scale')
        
        
        
        #box = layout.box()
        row = box.row()
        row.label(text="Options :", icon='OPTIONS')
        row = box.row()
        row.operator("clickr.origin", text="Move origins to bottom", icon='DOT')
        row = box.row()
        row.prop(settings, 'clickr_align')
        row = box.row()
        row.prop(settings, 'clickr_linked')
         
        
        
def add_to_collection(object_to_move):
    """
    checks if the CLICKR collection exists and moves the object to this collection
    """   
    
    #only run the code when the user has checked the checkbox
    if bpy.context.scene.CLICKR.clickr_collection == True:
        #name for the collection that will be created
        collection_name = 'CLICKR' 
        
        #try if it exists, otherwise create it
        try: 
            collection = bpy.data.collections[collection_name]
        except:
            collection = bpy.data.collections.new(name= collection_name )
            bpy.context.scene.collection.children.link(collection)
        
        #move object to new collection and unlink from old collection
        obj = object_to_move
        old_collections = []
        for collection in obj.users_collection:
            try:
                bpy.data.collections[collection.name].objects.unlink(obj)
            except:
                bpy.context.scene.collection.objects.unlink(obj)
        bpy.data.collections[collection_name].objects.link(obj)


def choose_object(self):
    """
    chooses a random object from the objects that were selected when the user pressed 'start clicking' and duplicates it
    Supports both scene selection and asset library modes
    """   
    settings = bpy.context.scene.CLICKR
    
    # Check if using Asset Library mode
    use_asset_library = (settings.object_source == 'ASSET_LIBRARY' and 
                         hasattr(self, 'asset_pool') and 
                         self.asset_pool and 
                         len(self.asset_pool) > 0)
    
    if use_asset_library:
        # Asset Library mode - spawn from asset pool
        asset_data = random.choice(self.asset_pool)
        
        bpy.ops.object.select_all(action='DESELECT')
        
        spawned_obj = spawn_asset_object(bpy.context, asset_data, linked=settings.clickr_linked)
        
        if spawned_obj:
            self.clickr_dupl = spawned_obj
            self.clickr_pick = spawned_obj  # For compatibility
            self.object = self.clickr_dupl
            add_to_collection(self.clickr_dupl)
        else:
            self.clickr_dupl = None
            self.object = None
    elif hasattr(self, 'obj_pool') and self.obj_pool and len(self.obj_pool) > 0:
        # Original selection mode
        #choose a random object from the pool of objects
        self.clickr_pick = random.choice(self.obj_pool)
        
        #deselect all and make the pick active
        bpy.ops.object.select_all(action='DESELECT')
        self.clickr_pick.select_set(state=True)
        bpy.context.view_layer.objects.active = self.clickr_pick
        
        #duplicate this object and make it clickr_dupl
        bpy.ops.object.duplicate(linked=bpy.context.scene.CLICKR.clickr_linked, mode='TRANSLATION')
        self.clickr_dupl = bpy.context.active_object

        # Object is created only when there's a valid surface, so it should be visible
        self.object = self.clickr_dupl

        #move to CLICKR collection
        add_to_collection(self.clickr_dupl)
    else:
        # No objects available
        self.clickr_dupl = None
        self.object = None

def randomization(self):
    """
    applies randomization in scale and rotation on the currently selected object
    """
    
    #get a random positive or negative 
    if random.random() < 0.5: 
        pos_neg= 1 
    else:
        pos_neg= -1 

    
    #randomize scale
    scale_random= 1+random.randrange(10)/10*bpy.context.scene.CLICKR.clickr_scale*pos_neg
    bpy.ops.transform.resize(value=(scale_random, scale_random, scale_random))
    
    #randomize Z rotation
    rotation_random= bpy.context.scene.CLICKR.clickr_rotation/200 *random.randrange(10)*pos_neg
    bpy.ops.transform.rotate(value=rotation_random, orient_axis='Z')

    #randomize XY rotation
    askew_random= bpy.context.scene.CLICKR.clickr_askew/30 *random.randrange(10)*pos_neg
    bpy.ops.transform.rotate(value=askew_random, orient_axis='Y')
    bpy.ops.transform.rotate(value=askew_random, orient_axis='X')

    
def origin_to_bottom(ob, matrix=Matrix(), use_verts=False):
    """
    moves the origin of the object to the bottom of it's bounding box. This code was shared by the user batFINGER on Blender StackExchange in the post named "Set origin to bottom center of multiple objects"
    """
    me = ob.data
    mw = ob.matrix_world
    if use_verts:
        data = (v.co for v in me.vertices)
    else:
        data = (Vector(v) for v in ob.bound_box)


    coords = np.array([matrix @ v for v in data])
    z = coords.T[2]
    mins = np.take(coords, np.where(z == z.min())[0], axis=0)

    o = Vector(np.mean(mins, axis=0))
    o = matrix.inverted() @ o
    me.transform(Matrix.Translation(-o))

    mw.translation = mw @ o    


#         888                                              
#         888                                              
#         888                                              
# .d8888b 888  8888b.  .d8888b  .d8888b   .d88b.  .d8888b  
#d88P"    888     "88b 88K      88K      d8P  Y8b 88K      
#888      888 .d888888 "Y8888b. "Y8888b. 88888888 "Y8888b. 
#Y88b.    888 888  888      X88      X88 Y8b.          X88 
# "Y8888P 888 "Y888888  88888P'  88888P'  "Y8888   88888P'
 
                         
class CLICKR_OP(bpy.types.Operator):
    """
    Modal for placing the objects
    """
    bl_idname = "clickr.modal"
    bl_label = "CLICKR modal"

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            """
            Moves the object to the raycasted snap position on a pre-selected object. This part of the code was shared by the user 'lemon' on Blender StackExchange in the post named "How to move object while tracking to mouse cursor with a modal operator?"
            """
            #Get the mouse position thanks to the event            
            self.mouse_pos = event.mouse_region_x, event.mouse_region_y

            #Contextual active object, 2D and 3D regions
            self.object = self.clickr_dupl
            region = bpy.context.region
            region3D = bpy.context.space_data.region_3d

            #The direction indicated by the mouse position from the current view
            self.view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, self.mouse_pos)
            #The view point of the user
            self.view_point = view3d_utils.region_2d_to_origin_3d(region, region3D, self.mouse_pos)
            #The 3D location in this direction - extend the ray far into the scene
            # Use a very large distance (10000 units) to ensure ray reaches all surfaces
            self.world_loc = self.view_point + (self.view_vector * 10000.0)

            # Initialize variables for finding closest surface hit
            closest_hit = None
            closest_distance = float('inf')
            closest_normal = Vector((0, 0, 1))

            # Get all valid surfaces to test based on selected mode
            settings = bpy.context.scene.CLICKR
            surfaces_to_test = []

            if settings.surface_mode == 'ALL':
                # ALL mode: Test against all mesh objects in the scene except the ones being placed
                obj_pool_names = [o.name for o in self.obj_pool]
                for obj in bpy.data.objects:
                    if (obj.type == 'MESH' and
                        obj.name not in obj_pool_names and
                        obj != self.clickr_dupl):  # Exclude the object being placed
                        surfaces_to_test.append(obj)
            else:
                # SPECIFIC mode: Use surfaces from the list
                # Add surfaces from the new list
                for surface_item in settings.surface_list:
                    if surface_item.object_name in bpy.data.objects:
                        surfaces_to_test.append(bpy.data.objects[surface_item.object_name])

                # Also test legacy single surface for backward compatibility
                if settings.clickr_surface != 'None' and settings.clickr_surface in bpy.data.objects:
                    legacy_surface = bpy.data.objects[settings.clickr_surface]
                    if legacy_surface not in surfaces_to_test:
                        surfaces_to_test.append(legacy_surface)

            # Test ray casting against all surfaces
            for plane in surfaces_to_test:
                if plane and plane.type == 'MESH':
                    try:
                        # Ensure the object has mesh data
                        if plane.data and len(plane.data.polygons) > 0:
                            world_mat_inv = plane.matrix_world.inverted()
                            # Calculates the ray direction in the target space
                            rc_origin = world_mat_inv @ self.view_point
                            rc_direction = world_mat_inv.to_3x3() @ self.view_vector
                            rc_direction = rc_direction.normalized()
                            
                            # Use a very long distance for ray casting (10000 units)
                            hit, loc, norm, index = plane.ray_cast(origin=rc_origin, direction=rc_direction, distance=10000.0)

                            if hit:
                                # Convert hit location back to world space
                                world_hit_loc = plane.matrix_world @ loc
                                # Calculate distance from view point to hit
                                distance = (world_hit_loc - self.view_point).length

                                # Keep track of closest hit
                                if distance < closest_distance:
                                    closest_distance = distance
                                    closest_hit = world_hit_loc
                                    if bpy.context.scene.CLICKR.clickr_align == True:
                                        norm.rotate(plane.matrix_world.to_euler('XYZ'))
                                        closest_normal = norm.normalized()
                    except RuntimeError as e:
                        # Skip objects that cause ray_cast errors
                        continue

            # Only create/update object if we have a valid surface hit
            if closest_hit:
                self.world_loc = closest_hit
                self.normal = closest_normal
                self.has_valid_surface = True

                # Create object if it doesn't exist yet
                if not hasattr(self, 'clickr_dupl') or self.clickr_dupl is None:
                    choose_object(self)
                    randomization(self)

                # Update object position and rotation
                if self.object:
                    self.object.location = self.world_loc
                    if bpy.context.scene.CLICKR.clickr_align == True:
                        z = Vector((0, 0, 1))
                        self.object.rotation_euler = z.rotation_difference(self.normal).to_euler()
            else:
                # No valid surface hit - no object should exist
                self.has_valid_surface = False
                # Delete the object if it exists
                if hasattr(self, 'clickr_dupl') and self.clickr_dupl is not None:
                    bpy.ops.object.select_all(action='DESELECT')
                    self.clickr_dupl.select_set(state=True)
                    bpy.context.view_layer.objects.active = self.clickr_dupl
                    bpy.ops.object.delete()
                    self.clickr_dupl = None
                    self.object = None
                
                
        elif event.type == 'LEFTMOUSE' and event.value == "RELEASE":
            """
            Places object only if there's a valid surface hit
            """
            # Only place object if we have a valid surface hit and object exists
            if (hasattr(self, 'has_valid_surface') and self.has_valid_surface and
                hasattr(self, 'clickr_dupl') and self.clickr_dupl is not None):
                # Create a new object for the next placement
                choose_object(self)
                randomization(self)
            else:
                # Show warning that placement requires surface contact
                self.report({'WARNING'}, "Cannot place object - no surface contact. Move cursor over a surface.")

        
        
        elif event.type in {'LEFT_ALT', 'RIGHT_ALT'} and event.value == 'PRESS':
            """
            When Alt is pressed, choose a new random object (same logic as RET)
            This allows quickly swapping the currently previewed model while placing objects.
            """
            settings = bpy.context.scene.CLICKR
            
            # Only act if there is a currently moving object
            if hasattr(self, 'clickr_dupl') and self.clickr_dupl is not None:
                # make sure only the CLICKR object is selected and active
                bpy.ops.object.select_all(action='DESELECT')
                self.clickr_dupl.select_set(state=True)
                context.view_layer.objects.active = self.clickr_dupl

                # delete the old object
                bpy.ops.object.delete()

                # Don't create new object immediately - wait for valid surface
                self.clickr_dupl = None
                self.object = None
                self.has_valid_surface = False

        elif event.type == 'RET' and event.value == "RELEASE":
            """
            Get a new random object, making sure its not the same as the last one. Chooses a new object, and deletes the one that was being moved. 
            """
            settings = bpy.context.scene.CLICKR
            
            if hasattr(self, 'clickr_dupl') and self.clickr_dupl is not None:
                #make sure only the CLICKR object is selected and active
                bpy.ops.object.select_all(action='DESELECT')
                self.clickr_dupl.select_set(state=True)
                context.view_layer.objects.active = self.clickr_dupl
                
                #delete the old object    
                bpy.ops.object.delete()     
                
                # Don't create new object immediately - wait for valid surface
                # The object will be created when mouse moves over a valid surface
                self.clickr_dupl = None
                self.object = None
                self.has_valid_surface = False
            # The object will be created when mouse moves over a valid surface
            self.clickr_dupl = None
            self.object = None
            self.has_valid_surface = False
            
            
        elif event.type in {'ESC'}:
            """
            Cancels the modal, deleting the object that was currently being placed
            """

            #delete the currently moving object if it exists
            if hasattr(self, 'clickr_dupl') and self.clickr_dupl is not None:
                bpy.ops.object.select_all(action='DESELECT')
                self.clickr_dupl.select_set(state=True)
                context.view_layer.objects.active = self.clickr_dupl
                bpy.ops.object.delete()
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            settings = bpy.context.scene.CLICKR
            
            # Check if using Asset Library mode
            if settings.object_source == 'ASSET_LIBRARY':
                # Use assets selected in the Asset Browser
                self.asset_pool = get_selected_assets_from_browser(context)
                
                if not self.asset_pool:
                    self.report({'WARNING'}, "No assets selected in the Asset Browser")
                    return {'CANCELLED'}
                
                self.obj_pool = []  # Empty for asset library mode
                
            elif bpy.context.selected_objects:
                # Selection mode - use selected objects
                self.asset_pool = []  # Empty for selection mode
                
                # Check if surfaces are available based on selected mode
                valid_surfaces = []

                if settings.surface_mode == 'ALL':
                    # ALL mode: Check if there are any mesh objects in the scene
                    for obj in bpy.data.objects:
                        if obj.type == 'MESH':
                            valid_surfaces.append(obj)

                    if not valid_surfaces:
                        self.report({'WARNING'}, "No mesh objects found in the scene for snapping.")
                        return {'CANCELLED'}
                else:
                    # SPECIFIC mode: Check surfaces from the list
                    # Check surfaces from the new list
                    for surface_item in settings.surface_list:
                        if surface_item.object_name in bpy.data.objects:
                            valid_surfaces.append(bpy.data.objects[surface_item.object_name])

                    # Check legacy single surface for backward compatibility
                    if settings.clickr_surface != 'None' and settings.clickr_surface in bpy.data.objects:
                        legacy_surface = bpy.data.objects[settings.clickr_surface]
                        if legacy_surface not in valid_surfaces:
                            valid_surfaces.append(legacy_surface)

                    # Ensure we have at least one valid surface in SPECIFIC mode
                    if not valid_surfaces:
                        self.report({'WARNING'}, "No valid ground surfaces found. Please add surfaces to the list or select a legacy surface.")
                        return {'CANCELLED'}

                # Create a list of objects that are selected when starting the modal
                self.obj_pool = []
                objs = bpy.context.selected_objects

                if settings.surface_mode == 'ALL':
                    # In ALL mode, all selected objects are considered objects to place
                    # We don't exclude any objects as surfaces since any mesh can be a surface
                    for obj in objs:
                        self.obj_pool.append(obj)

                    # Ensure we have objects to place
                    if not self.obj_pool:
                        self.report({'WARNING'}, "No objects selected. Please select objects to place.")
                        return {'CANCELLED'}

                else:
                    # SPECIFIC mode: exclude surface objects from placement objects
                    surface_names = [surf.name for surf in valid_surfaces]

                    for obj in objs:
                        if obj.name in surface_names:
                            # Check if user only selected surface objects
                            if len([o for o in objs if o.name not in surface_names]) == 0:
                                self.report({'WARNING'}, "You have only ground surfaces selected. Please select objects to place.")
                                return {'CANCELLED'}
                        else:
                            self.obj_pool.append(obj)

                    # Ensure we have objects to place
                    if not self.obj_pool:
                        self.report({'WARNING'}, "No objects to place. Please select objects in addition to ground surfaces.")
                        return {'CANCELLED'}
            else:
                self.report({'WARNING'}, "No objects selected and Asset Library mode not enabled")
                return {'CANCELLED'}
            
            # Check surfaces for Asset Library mode too
            if settings.object_source == 'ASSET_LIBRARY':
                valid_surfaces = []
                if settings.surface_mode == 'ALL':
                    for obj in bpy.data.objects:
                        if obj.type == 'MESH':
                            valid_surfaces.append(obj)
                    if not valid_surfaces:
                        self.report({'WARNING'}, "No mesh objects found in the scene for snapping.")
                        return {'CANCELLED'}
                else:
                    for surface_item in settings.surface_list:
                        if surface_item.object_name in bpy.data.objects:
                            valid_surfaces.append(bpy.data.objects[surface_item.object_name])
                    if settings.clickr_surface != 'None' and settings.clickr_surface in bpy.data.objects:
                        legacy_surface = bpy.data.objects[settings.clickr_surface]
                        if legacy_surface not in valid_surfaces:
                            valid_surfaces.append(legacy_surface)
                    if not valid_surfaces:
                        self.report({'WARNING'}, "No valid ground surfaces found. Please add surfaces to the list.")
                        return {'CANCELLED'}
            
            # Don't create object initially - wait for valid surface
            # choose_object(self)
            # randomization(self)

            #these variables are needed for the snapping. This part of the invoke code was shared by the user 'lemon' as referenced above
            self.mouse_pos = [0,0]
            self.loc = [0,0,0]
            self.object = None
            self.view_point = None
            self.view_vector = None
            self.world_loc = None
            self.loc_on_plane = None
            self.normal = None
            self.has_valid_surface = False  # Initialize surface validation flag
            self.clickr_dupl = None  # No object initially

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

class CLICKR_SURFACE(bpy.types.Operator):
    """
    selects the surface objects will snap to
    """
    bl_idname = "clickr.surface"
    bl_label = "CLICKR Surface"
    bl_description = "Make the current active object your CLICKR ground surface"
    
    def execute(self, context):    
        try:
            bpy.context.scene.CLICKR.clickr_surface = bpy.context.active_object.name
        
        #return warning when no objects was selected
        except:
            self.report({'WARNING'}, "No object selected")
        return {'FINISHED'}
    
class CLICKR_ORIGIN(bpy.types.Operator):
    """
    moves origin of objects to the bottom of their bounding box
    """
    bl_idname = "clickr.origin"
    bl_label = "CLICKR Origin"
    bl_description = "Move origins to bottom of objects"

    def execute(self, context):
        try:
            for obj in bpy.context.selected_objects:
                origin_to_bottom(obj)
        #return warning when no objects were selected
        except:
            self.report({'WARNING'}, "No object selected")
        return {'FINISHED'}

class CLICKR_ADD_SURFACE(bpy.types.Operator):
    """
    Add the active object to the ground surfaces list
    """
    bl_idname = "clickr.add_surface"
    bl_label = "Add Surface"
    bl_description = "Add the active object to the ground surfaces list"

    def execute(self, context):
        if not context.active_object:
            self.report({'WARNING'}, "No active object selected")
            return {'CANCELLED'}

        obj = context.active_object
        settings = context.scene.CLICKR

        # Check if object is already in the list
        for surface in settings.surface_list:
            if surface.object_name == obj.name:
                self.report({'WARNING'}, f"Object '{obj.name}' is already in the surfaces list")
                return {'CANCELLED'}

        # Add new surface to the list
        new_surface = settings.surface_list.add()
        new_surface.name = obj.name
        new_surface.object_name = obj.name

        # Set the index to the newly added item
        settings.surface_list_index = len(settings.surface_list) - 1

        self.report({'INFO'}, f"Added '{obj.name}' to ground surfaces list")
        return {'FINISHED'}

class CLICKR_REMOVE_SURFACE(bpy.types.Operator):
    """
    Remove the selected surface from the ground surfaces list
    """
    bl_idname = "clickr.remove_surface"
    bl_label = "Remove Surface"
    bl_description = "Remove the selected surface from the ground surfaces list"

    def execute(self, context):
        settings = context.scene.CLICKR

        if len(settings.surface_list) == 0:
            self.report({'WARNING'}, "No surfaces in the list to remove")
            return {'CANCELLED'}

        if settings.surface_list_index < 0 or settings.surface_list_index >= len(settings.surface_list):
            self.report({'WARNING'}, "Invalid surface selection")
            return {'CANCELLED'}

        # Get the name before removing
        surface_name = settings.surface_list[settings.surface_list_index].name

        # Remove the surface
        settings.surface_list.remove(settings.surface_list_index)

        # Adjust index if necessary
        if settings.surface_list_index >= len(settings.surface_list) and len(settings.surface_list) > 0:
            settings.surface_list_index = len(settings.surface_list) - 1
        elif len(settings.surface_list) == 0:
            settings.surface_list_index = 0

        self.report({'INFO'}, f"Removed '{surface_name}' from ground surfaces list")
        return {'FINISHED'}


def spawn_asset_object(context, asset_data, linked=True):
    """
    Spawn an object from asset data
    Returns the spawned object
    Note: For external assets, always append (not link) to allow full editing
    """
    if asset_data['type'] == 'LOCAL':
        # Duplicate local object
        obj = asset_data['object']
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.object.duplicate(linked=linked, mode='TRANSLATION')
        return context.active_object
    else:
        # Append from external file (always append, not link)
        blend_path = asset_data['blend_path']
        obj_name = asset_data['name']
        
        try:
            # Check if object already exists in bpy.data.objects (previously appended)
            existing_obj = None
            for obj in bpy.data.objects:
                # Check if it's the same base object (without .001, .002 suffix)
                base_name = obj.name.split('.')[0] if '.' in obj.name else obj.name
                if base_name == obj_name and not obj.library:
                    existing_obj = obj
                    break
            
            if existing_obj:
                # Object already appended - duplicate it
                bpy.ops.object.select_all(action='DESELECT')
                existing_obj.select_set(True)
                context.view_layer.objects.active = existing_obj
                bpy.ops.object.duplicate(linked=linked, mode='TRANSLATION')
                new_obj = context.active_object
                return new_obj
            else:
                # Append object from external file (link=False for append)
                with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
                    if obj_name in data_from.objects:
                        data_to.objects = [obj_name]
                
                # Link the appended object to the scene collection
                for obj in data_to.objects:
                    if obj is not None:
                        # Check if already linked to a collection
                        if obj.name not in context.collection.objects:
                            context.collection.objects.link(obj)
                        obj.select_set(True)
                        context.view_layer.objects.active = obj
                        return obj
        except Exception as e:
            pass
    
    return None

# Property group for individual surface items
class CLICKR_SURFACE_ITEM(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Surface Name",
        description="Name of the ground surface object",
        default=""
    )
    object_name: bpy.props.StringProperty(
        name="Object Name",
        description="Internal object name reference",
        default=""
    )

class CLICKR_SETTINGS(bpy.types.PropertyGroup):
    # Keep the old single surface property for backward compatibility
    clickr_surface: bpy.props.StringProperty(
        name='clickr_surface',
        description="surface CLICKR places objects on",
        default= 'None',
        )

    # New collection property for multiple surfaces
    surface_list: bpy.props.CollectionProperty(
        type=CLICKR_SURFACE_ITEM,
        name="Ground Surfaces",
        description="List of ground surfaces for object placement"
    )

    surface_list_index: bpy.props.IntProperty(
        name="Surface List Index",
        description="Index of the selected surface in the list",
        default=0
    )

    # New property for surface mode selection
    surface_mode: bpy.props.EnumProperty(
        name="Surface Mode",
        description="Choose how surfaces are detected for snapping",
        items=[
            ('SPECIFIC', "Specific Surfaces", "Use only surfaces from the list", 'RESTRICT_SELECT_ON', 0),
            ('ALL', "All Surfaces", "Snap to all mesh objects in the scene", 'MESH_DATA', 1),
        ],
        default='ALL'
    )

    # Asset Library Source Mode
    object_source: bpy.props.EnumProperty(
        name="Object Source",
        description="Choose where to get objects from",
        items=[
            ('SELECTION', "Selection", "Use selected objects from scene", 'RESTRICT_SELECT_OFF', 0),
            ('ASSET_LIBRARY', "Asset Library", "Use objects from Asset Library", 'ASSET_MANAGER', 1),
        ],
        default='SELECTION'
    )


    clickr_linked: bpy.props.BoolProperty(
        name="Create instances",
        description="",
        default=True
        )
    clickr_collection: bpy.props.BoolProperty(
        name="Move to CLICKR collection",
        description="",
        default=False
        )
    clickr_align: bpy.props.BoolProperty(
        name="Align to surface",
        description="",
        default=False
        )
    clickr_rotation: bpy.props.IntProperty(
        name='Z Rotation',
        subtype="PERCENTAGE",
        default=30,
        min=0,
        max=100)
    clickr_scale: bpy.props.FloatProperty(
        name='Scale',
        step = 1,
        precision = 2,
        min=0.0,
        soft_max=1,
        max=10,
        default=0.25)

    clickr_askew: bpy.props.FloatProperty(
        name='Skewness',
        step = 1,
        precision = 2,
        min=0.0,
        soft_max=0.1,
        max=10)

    
classes = (
    CLICKR_UL_SURFACE_LIST,
    CLICKR_PT_PANEL,
    CLICKR_OP,
    CLICKR_SURFACE_ITEM,
    CLICKR_SETTINGS,
    CLICKR_SURFACE,
    CLICKR_ADD_SURFACE,
    CLICKR_REMOVE_SURFACE,
    CLICKR_ORIGIN,
    random_R,
    Delete_random_R,
    random_s,
    Delete_random_s,
    )

# Register
def register():
    for cls in classes:    
        bpy.utils.register_class(cls)
    bpy.types.Scene.CLICKR = bpy.props.PointerProperty(type=CLICKR_SETTINGS)
    
    # Random rotation and scale strength properties
    bpy.types.Scene.random_rotation_strength = bpy.props.FloatProperty(
        name="Rotation Strength",
        description="Control the intensity of random rotation (0.0 = no rotation, 1.0 = maximum rotation)",
        default=0.5,
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )
    bpy.types.Scene.random_scale_strength = bpy.props.FloatProperty(
        name="Scale Strength",
        description="Control the intensity of random scaling (0.0 = no scaling, 1.0 = maximum scaling)",
        default=0.5,
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )

# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    # التحقق من وجود الخاصية قبل حذفها لتجنب الأخطاء
    if hasattr(bpy.types.Scene, 'CLICKR'):
        del bpy.types.Scene.CLICKR
    
    # Clean up random rotation and scale strength properties
    if hasattr(bpy.types.Scene, 'random_rotation_strength'):
        del bpy.types.Scene.random_rotation_strength
    if hasattr(bpy.types.Scene, 'random_scale_strength'):
        del bpy.types.Scene.random_scale_strength

if __name__ == "__main__":
    register()
