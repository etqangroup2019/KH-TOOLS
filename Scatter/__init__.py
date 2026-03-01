bl_info = {
    "name": "KH-Scatter",
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
import random
import math
from bpy.utils import register_class, unregister_class


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

def spawn_asset_for_scatter(context, asset_data, collection):
    """
    Append asset and move to collection
    """
    if asset_data['type'] == 'LOCAL':
        obj = asset_data['object']
        if obj.name not in collection.objects:
            collection.objects.link(obj)
            # Unlink from scene collection if it's there
            if obj.name in context.scene.collection.objects:
                context.scene.collection.objects.unlink(obj)
        if obj.type == 'MESH':
            obj.display_type = 'BOUNDS'
        return obj
    else:
        blend_path = asset_data['blend_path']
        obj_name = asset_data['name']
        
        try:
            # Check if already appended
            existing_obj = bpy.data.objects.get(obj_name)
            if existing_obj and not existing_obj.library:
                if existing_obj.name not in collection.objects:
                    collection.objects.link(existing_obj)
                if existing_obj.type == 'MESH':
                    existing_obj.display_type = 'BOUNDS'
                return existing_obj

            # Append from external file
            with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
                if obj_name in data_from.objects:
                    data_to.objects = [obj_name]
            
            for obj in data_to.objects:
                if obj is not None:
                    collection.objects.link(obj)
                    if obj.type == 'MESH':
                        obj.display_type = 'BOUNDS'
                    return obj
        except:
            pass
    return None

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

def KH_Scatter_collection():
    collections_names = ["KH-Scatter"]
    scene = bpy.context.scene
    existing_collections = [collection.name for collection in bpy.data.collections]
    for name in collections_names:
        if name not in existing_collections:
            new_collection = bpy.data.collections.new(name)
            scene.collection.children.link(new_collection)

def get_layer_collection(layer_collection, collection_name):
    """Recursively find a layer collection by name."""
    if layer_collection.name == collection_name:
        return layer_collection
    for child in layer_collection.children:
        found = get_layer_collection(child, collection_name)
        if found:
            return found
    return None


class kh_scatter_Operator1(bpy.types.Operator):
    bl_idname = "object.import_particle_settings1"
    bl_label = "Import Particle Settings"
    
    def execute(self, context):
        KH_Scatter_collection()
        source_file = os.path.join(os.path.dirname(__file__), "scatter.blend")
        particle_settings_name = "KH-Grass"

        with bpy.data.libraries.load(source_file, link=False) as (data_from, data_to):
            if particle_settings_name in data_from.particles:
                data_to.particles = [particle_settings_name] 
                
        if particle_settings_name in bpy.data.particles:
            if particle_settings_name not in bpy.data.collections:
                bpy.ops.wm.append(directory=source_file + "\\Collection\\", filename=particle_settings_name, link=False)
        
        if "KH-Grass" in bpy.data.collections and "KH-Scatter" in bpy.data.collections:
            kh_rock = bpy.data.collections["KH-Grass"]
            kh_scatter = bpy.data.collections["KH-Scatter"]
            
            if kh_rock.name in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.unlink(kh_rock)
            for collection in bpy.data.collections:
                if kh_rock.name in collection.children:
                    collection.children.unlink(kh_rock)
            kh_scatter.children.link(kh_rock)

            # Set objects to BOUNDS display type
            for obj in kh_rock.all_objects:
                if obj.type == 'MESH':
                    obj.display_type = 'BOUNDS'
            
        if particle_settings_name in bpy.data.particles:
            target_object = bpy.context.active_object 
            bpy.ops.object.particle_system_add()
            particle_system = target_object.particle_systems[-1]            
            particle_system.settings = bpy.data.particles[particle_settings_name]
            particle_system.name = "KH-Grass"
            # إنشاء نسخة منفصلة من إعدادات النظام الجزيئي
            particle_system.settings = particle_system.settings.copy()
            
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            
            bpy.context.view_layer.update()
            
            particle_system.settings.instance_collection = bpy.data.collections[particle_settings_name]

            particle_system.seed = random.randint(1, 1000)  
            
            # Set as active
            context.scene.selected_particle_system = len(target_object.particle_systems) - 1
            context.scene.selected_scatter_modifier = ""
            
        kh_rock_name = "KH-Grass"
        kh_scatter_name = "KH-Scatter"

        kh_rock = bpy.data.collections.get(kh_rock_name)
        kh_scatter = bpy.data.collections.get(kh_scatter_name)

        if kh_rock and kh_scatter:
            view_layer = bpy.context.view_layer
            if kh_rock.name in view_layer.layer_collection.children:
                view_layer.layer_collection.children[kh_rock.name].exclude = True
            if kh_scatter_name in view_layer.layer_collection.children:
                scatter_collection = view_layer.layer_collection.children[kh_scatter_name]
                for child_collection in scatter_collection.children:
                    if child_collection.collection.name == kh_rock_name:
                        child_collection.exclude = True

           
        ensure_scale_handler()
        return {'FINISHED'}
    

# --- Unified Scale Handler System ---
def KH_Universal_Scale_Handler(scene, depsgraph=None):
    """Unifies scale for all KH and Scatter collections on every frame update."""
    # This covers KH-Grass, KH-Leaves, Scatter_Asset, Scatter_P, etc.
    prefixes = ("KH-", "Scatter") 
    updated = False
    for coll in bpy.data.collections:
        if any(coll.name.startswith(p) for p in prefixes):
            for obj in coll.all_objects:
                if obj.type == 'MESH':
                    # If Z axis is changed by user, force X and Y to match
                    if abs(obj.scale.x - obj.scale.z) > 0.0001 or abs(obj.scale.y - obj.scale.z) > 0.0001:
                        obj.scale.x = obj.scale.z
                        obj.scale.y = obj.scale.z
                        updated = True
    # if updated: print("KH-Scatter: Scales Unified")

def ensure_scale_handler():
    """Ensures the universal scale handler is registered and active."""
    if KH_Universal_Scale_Handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(KH_Universal_Scale_Handler)
    # Force a refresh if possible
    try:
        if hasattr(bpy.context, "view_layer"):
            bpy.context.view_layer.update()
    except:
        pass

# Remove old prev_scale_z variables and individual handlers

            
class kh_KH_Grass1_Operator1(bpy.types.Operator):
    bl_idname = "object.import_kh_grass1"
    bl_label = "Import Particle Settings"
    
    def execute(self, context):
        KH_Scatter_collection()
        source_file = os.path.join(os.path.dirname(__file__), "scatter.blend")
        particle_settings_name = "KH-Grass1"

        with bpy.data.libraries.load(source_file, link=False) as (data_from, data_to):
            if particle_settings_name in data_from.particles:
                data_to.particles = [particle_settings_name] 
                
        if particle_settings_name in bpy.data.particles:
            if particle_settings_name not in bpy.data.collections:
                bpy.ops.wm.append(directory=source_file + "\\Collection\\", filename=particle_settings_name, link=False)
        
        if "KH-Grass1" in bpy.data.collections and "KH-Scatter" in bpy.data.collections:
            kh_rock = bpy.data.collections["KH-Grass1"]
            kh_scatter = bpy.data.collections["KH-Scatter"]
            
            if kh_rock.name in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.unlink(kh_rock)
            for collection in bpy.data.collections:
                if kh_rock.name in collection.children:
                    collection.children.unlink(kh_rock)
            kh_scatter.children.link(kh_rock)

            # Set objects to BOUNDS display type
            for obj in kh_rock.all_objects:
                if obj.type == 'MESH':
                    obj.display_type = 'BOUNDS'
                
        if particle_settings_name in bpy.data.particles:
            target_object = bpy.context.active_object 
            bpy.ops.object.particle_system_add()
            particle_system = target_object.particle_systems[-1]
            particle_system.settings = bpy.data.particles[particle_settings_name]
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            particle_system.name = "KH-Grass1"
            # إنشاء نسخة منفصلة من إعدادات النظام الجزيئي
            particle_system.settings = particle_system.settings.copy()
            bpy.context.view_layer.update()
            
            particle_system.settings.instance_collection = bpy.data.collections[particle_settings_name]

            particle_system.seed = random.randint(1, 1000)  
            
            # Set as active
            context.scene.selected_particle_system = len(target_object.particle_systems) - 1
            context.scene.selected_scatter_modifier = ""
                   
        kh_rock_name = "KH-Grass1"
        kh_scatter_name = "KH-Scatter"

        kh_rock = bpy.data.collections.get(kh_rock_name)
        kh_scatter = bpy.data.collections.get(kh_scatter_name)

        if kh_rock and kh_scatter:
            view_layer = bpy.context.view_layer
            if kh_rock.name in view_layer.layer_collection.children:
                view_layer.layer_collection.children[kh_rock.name].exclude = True
            if kh_scatter_name in view_layer.layer_collection.children:
                scatter_collection = view_layer.layer_collection.children[kh_scatter_name]
                for child_collection in scatter_collection.children:
                    if child_collection.collection.name == kh_rock_name:
                        child_collection.exclude = True
                        
        ensure_scale_handler()
        return {'FINISHED'}


class kh_KH_Grassl_Operator1(bpy.types.Operator):
    bl_idname = "object.import_kh_grassl"
    bl_label = "Import Particle Settings"
    
    def execute(self, context):
        KH_Scatter_collection()
        source_file = os.path.join(os.path.dirname(__file__), "scatter.blend")
        particle_settings_name = "KH-Grassl"

        with bpy.data.libraries.load(source_file, link=False) as (data_from, data_to):
            if particle_settings_name in data_from.particles:
                data_to.particles = [particle_settings_name] 
                
        if particle_settings_name in bpy.data.particles:
            if particle_settings_name not in bpy.data.collections:
                bpy.ops.wm.append(directory=source_file + "\\Collection\\", filename=particle_settings_name, link=False)
        
        if "KH-Grassl" in bpy.data.collections and "KH-Scatter" in bpy.data.collections:
            kh_rock = bpy.data.collections["KH-Grassl"]
            kh_scatter = bpy.data.collections["KH-Scatter"]
            
            if kh_rock.name in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.unlink(kh_rock)
            for collection in bpy.data.collections:
                if kh_rock.name in collection.children:
                    collection.children.unlink(kh_rock)
            kh_scatter.children.link(kh_rock)

            # Set objects to BOUNDS display type
            for obj in kh_rock.all_objects:
                if obj.type == 'MESH':
                    obj.display_type = 'BOUNDS'
                
        if particle_settings_name in bpy.data.particles:
            target_object = bpy.context.active_object 
            bpy.ops.object.particle_system_add()
            particle_system = target_object.particle_systems[-1]
            particle_system.settings = bpy.data.particles[particle_settings_name]
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            particle_system.name = "KH-Grassl"
            # إنشاء نسخة منفصلة من إعدادات النظام الجزيئي
            particle_system.settings = particle_system.settings.copy()
            bpy.context.view_layer.update()
            
            particle_system.settings.instance_collection = bpy.data.collections[particle_settings_name]

            particle_system.seed = random.randint(1, 1000)  
            
            # Set as active
            context.scene.selected_particle_system = len(target_object.particle_systems) - 1
            context.scene.selected_scatter_modifier = ""
                   
        kh_rock_name = "KH-Grassl"
        kh_scatter_name = "KH-Scatter"

        kh_rock = bpy.data.collections.get(kh_rock_name)
        kh_scatter = bpy.data.collections.get(kh_scatter_name)

        if kh_rock and kh_scatter:
            view_layer = bpy.context.view_layer
            if kh_rock.name in view_layer.layer_collection.children:
                view_layer.layer_collection.children[kh_rock.name].exclude = True
            if kh_scatter_name in view_layer.layer_collection.children:
                scatter_collection = view_layer.layer_collection.children[kh_scatter_name]
                for child_collection in scatter_collection.children:
                    if child_collection.collection.name == kh_rock_name:
                        child_collection.exclude = True
        ensure_scale_handler()
        return {'FINISHED'}
                        
# Replaced by Universal Handler
            
class kh_scatter_Operator2(bpy.types.Operator):
    bl_idname = "object.import_particle_settings2"
    bl_label = "Import Particle Settings"
    
    def execute(self, context):
        KH_Scatter_collection()
        source_file = os.path.join(os.path.dirname(__file__), "scatter.blend")
        particle_settings_name = "KH-Leaves"

        with bpy.data.libraries.load(source_file, link=False) as (data_from, data_to):
            if particle_settings_name in data_from.particles:
                data_to.particles = [particle_settings_name]
                
        if particle_settings_name in bpy.data.particles:
            if particle_settings_name not in bpy.data.collections:
                bpy.ops.wm.append(directory=source_file + "\\Collection\\", filename=particle_settings_name, link=False)
            
        if "KH-Leaves" in bpy.data.collections and "KH-Scatter" in bpy.data.collections:
            kh_rock = bpy.data.collections["KH-Leaves"]
            kh_scatter = bpy.data.collections["KH-Scatter"]
            
            if kh_rock.name in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.unlink(kh_rock)
            for collection in bpy.data.collections:
                if kh_rock.name in collection.children:
                    collection.children.unlink(kh_rock)
            kh_scatter.children.link(kh_rock)

            # Set objects to BOUNDS display type
            for obj in kh_rock.all_objects:
                if obj.type == 'MESH':
                    obj.display_type = 'BOUNDS'
                
        if particle_settings_name in bpy.data.particles:
            target_object = bpy.context.active_object 
            bpy.ops.object.particle_system_add()
            particle_system = target_object.particle_systems[-1]
            particle_system.settings = bpy.data.particles[particle_settings_name]

            bpy.ops.outliner.orphans_purge(do_recursive=True)
            particle_system.name = "KH-Leaves"
            # إنشاء نسخة منفصلة من إعدادات النظام الجزيئي
            particle_system.settings = particle_system.settings.copy()
            bpy.context.view_layer.update()
            
            particle_system.settings.instance_collection = bpy.data.collections[particle_settings_name]

            particle_system.seed = random.randint(1, 1000)  
            
            # Set as active
            context.scene.selected_particle_system = len(target_object.particle_systems) - 1
            context.scene.selected_scatter_modifier = ""
        
        kh_rock_name = "KH-Leaves"
        kh_scatter_name = "KH-Scatter"

        kh_rock = bpy.data.collections.get(kh_rock_name)
        kh_scatter = bpy.data.collections.get(kh_scatter_name)

        if kh_rock and kh_scatter:
            view_layer = bpy.context.view_layer
            if kh_rock.name in view_layer.layer_collection.children:
                view_layer.layer_collection.children[kh_rock.name].exclude = True
            if kh_scatter_name in view_layer.layer_collection.children:
                scatter_collection = view_layer.layer_collection.children[kh_scatter_name]
                for child_collection in scatter_collection.children:
                    if child_collection.collection.name == kh_rock_name:
                        child_collection.exclude = True
        ensure_scale_handler()
        return {'FINISHED'}
                    
class kh_scatter_Operator3(bpy.types.Operator):
    bl_idname = "object.import_particle_settings3"
    bl_label = "Import Particle Settings"
    
    def execute(self, context):
        KH_Scatter_collection()
        source_file = os.path.join(os.path.dirname(__file__), "scatter.blend")
        particle_settings_name = "KH-Ivy Wall"

        with bpy.data.libraries.load(source_file, link=False) as (data_from, data_to):
            if particle_settings_name in data_from.particles:
                data_to.particles = [particle_settings_name] 
                
        if particle_settings_name in bpy.data.particles:
            if particle_settings_name not in bpy.data.collections:
                bpy.ops.wm.append(directory=source_file + "\\Collection\\", filename=particle_settings_name, link=False)
        
        if "KH-Ivy Wall" in bpy.data.collections and "KH-Scatter" in bpy.data.collections:
            kh_rock = bpy.data.collections["KH-Ivy Wall"]
            kh_scatter = bpy.data.collections["KH-Scatter"]
            
            if kh_rock.name in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.unlink(kh_rock)
            for collection in bpy.data.collections:
                if kh_rock.name in collection.children:
                    collection.children.unlink(kh_rock)
            kh_scatter.children.link(kh_rock)

            # Set objects to BOUNDS display type
            for obj in kh_rock.all_objects:
                if obj.type == 'MESH':
                    obj.display_type = 'BOUNDS'
                 
        if particle_settings_name in bpy.data.particles:
            target_object = bpy.context.active_object 
            bpy.ops.object.particle_system_add()
            particle_system = target_object.particle_systems[-1]
            particle_system.settings = bpy.data.particles[particle_settings_name]
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            particle_system.name = "KH-Ivy Wall"
            particle_system.settings = particle_system.settings.copy()
            bpy.context.view_layer.update()
            
            particle_system.settings.instance_collection = bpy.data.collections[particle_settings_name]

            particle_system.seed = random.randint(1, 1000)  
            
            # Set as active
            context.scene.selected_particle_system = len(target_object.particle_systems) - 1
            context.scene.selected_scatter_modifier = ""
   
        kh_rock_name = "KH-Ivy Wall"
        kh_scatter_name = "KH-Scatter"

        kh_rock = bpy.data.collections.get(kh_rock_name)
        kh_scatter = bpy.data.collections.get(kh_scatter_name)

        if kh_rock and kh_scatter:
            view_layer = bpy.context.view_layer
            if kh_rock.name in view_layer.layer_collection.children:
                view_layer.layer_collection.children[kh_rock.name].exclude = True
            if kh_scatter_name in view_layer.layer_collection.children:
                scatter_collection = view_layer.layer_collection.children[kh_scatter_name]
                for child_collection in scatter_collection.children:
                    if child_collection.collection.name == kh_rock_name:
                        child_collection.exclude = True
        ensure_scale_handler()
        return {'FINISHED'}
                      
class kh_scatter_Operator4(bpy.types.Operator):
    bl_idname = "object.import_particle_settings4"
    bl_label = "Import Particle Settings"
    
    def execute(self, context):
        KH_Scatter_collection()
        source_file = os.path.join(os.path.dirname(__file__), "scatter.blend")
        particle_settings_name = "KH-ALL MIX"

        with bpy.data.libraries.load(source_file, link=False) as (data_from, data_to):
            if particle_settings_name in data_from.particles:
                data_to.particles = [particle_settings_name] 
                
        if particle_settings_name in bpy.data.particles:
            if particle_settings_name not in bpy.data.collections:
                bpy.ops.wm.append(directory=source_file + "\\Collection\\", filename=particle_settings_name, link=False)
         
        if "KH-ALL MIX" in bpy.data.collections and "KH-Scatter" in bpy.data.collections:
            kh_rock = bpy.data.collections["KH-ALL MIX"]
            kh_scatter = bpy.data.collections["KH-Scatter"]
            
            if kh_rock.name in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.unlink(kh_rock)
            for collection in bpy.data.collections:
                if kh_rock.name in collection.children:
                    collection.children.unlink(kh_rock)
            kh_scatter.children.link(kh_rock)

            # Set objects to BOUNDS display type
            for obj in kh_rock.all_objects:
                if obj.type == 'MESH':
                    obj.display_type = 'BOUNDS'
               
        if particle_settings_name in bpy.data.particles:
            target_object = bpy.context.active_object 
            bpy.ops.object.particle_system_add()
            particle_system = target_object.particle_systems[-1]
            particle_system.settings = bpy.data.particles[particle_settings_name]
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            particle_system.name = "KH-ALL MIX"
            particle_system.settings = particle_system.settings.copy()
            bpy.context.view_layer.update()
            
            particle_system.settings.instance_collection = bpy.data.collections[particle_settings_name]

            particle_system.seed = random.randint(1, 1000)  
            
            # Set as active
            context.scene.selected_particle_system = len(target_object.particle_systems) - 1
            context.scene.selected_scatter_modifier = ""
        
        kh_rock_name = "KH-ALL MIX"
        kh_scatter_name = "KH-Scatter"

        kh_rock = bpy.data.collections.get(kh_rock_name)
        kh_scatter = bpy.data.collections.get(kh_scatter_name)

        if kh_rock and kh_scatter:
            view_layer = bpy.context.view_layer
            if kh_rock.name in view_layer.layer_collection.children:
                view_layer.layer_collection.children[kh_rock.name].exclude = True
            if kh_scatter_name in view_layer.layer_collection.children:
                scatter_collection = view_layer.layer_collection.children[kh_scatter_name]
                for child_collection in scatter_collection.children:
                    if child_collection.collection.name == kh_rock_name:
                        child_collection.exclude = True
        ensure_scale_handler()
        return {'FINISHED'}
                    
class kh_scatter_Operator5(bpy.types.Operator):
    bl_idname = "object.import_particle_settings5"
    bl_label = "Import Particle Settings"
    
    def execute(self, context):
        KH_Scatter_collection()
        source_file = os.path.join(os.path.dirname(__file__), "scatter.blend")
        particle_settings_name = "KH-Rock"

        with bpy.data.libraries.load(source_file, link=False) as (data_from, data_to):
            if particle_settings_name in data_from.particles:
                data_to.particles = [particle_settings_name]
        
        if particle_settings_name in bpy.data.particles:
            if particle_settings_name not in bpy.data.collections:
                bpy.ops.wm.append(directory=source_file + "\\Collection\\", filename=particle_settings_name, link=False)
                
        if "KH-Rock" in bpy.data.collections and "KH-Scatter" in bpy.data.collections:
            kh_rock = bpy.data.collections["KH-Rock"]
            kh_scatter = bpy.data.collections["KH-Scatter"]
            
            if kh_rock.name in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.unlink(kh_rock)
            for collection in bpy.data.collections:
                if kh_rock.name in collection.children:
                    collection.children.unlink(kh_rock)
            kh_scatter.children.link(kh_rock)

            # Set objects to BOUNDS display type
            for obj in kh_rock.all_objects:
                if obj.type == 'MESH':
                    obj.display_type = 'BOUNDS'
            
              
        if particle_settings_name in bpy.data.particles:
            target_object = bpy.context.active_object 
            bpy.ops.object.particle_system_add()
            particle_system = target_object.particle_systems[-1]
            particle_system.settings = bpy.data.particles[particle_settings_name]
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            particle_system.name = "KH-Rock"
            particle_system.settings = particle_system.settings.copy()
            bpy.context.view_layer.update()
            
            particle_system.settings.instance_collection = bpy.data.collections[particle_settings_name]
            # kh_leaves = bpy.data.collections[particle_settings_name]
            # view_layer = bpy.context.view_layer
            # view_layer.layer_collection.children[kh_leaves.name].exclude = True

            particle_system.seed = random.randint(1, 1000)  

            # Set as active
            context.scene.selected_particle_system = len(target_object.particle_systems) - 1
            context.scene.selected_scatter_modifier = ""

        kh_rock_name = "KH-Rock"
        kh_scatter_name = "KH-Scatter"

        kh_rock = bpy.data.collections.get(kh_rock_name)
        kh_scatter = bpy.data.collections.get(kh_scatter_name)

        if kh_rock and kh_scatter:
            view_layer = bpy.context.view_layer
            if kh_rock.name in view_layer.layer_collection.children:
                view_layer.layer_collection.children[kh_rock.name].exclude = True
            if kh_scatter_name in view_layer.layer_collection.children:
                scatter_collection = view_layer.layer_collection.children[kh_scatter_name]
                for child_collection in scatter_collection.children:
                    if child_collection.collection.name == kh_rock_name:
                        child_collection.exclude = True
        ensure_scale_handler()
        return {'FINISHED'}

class kh_scatter_fur(bpy.types.Operator):
    bl_idname = "object.fur"
    bl_label = "Import Particle Settings"
    
    def execute(self, context):
        source_file = os.path.join(os.path.dirname(__file__), "scatter.blend")
        particle_settings_name = "KH-FUR"

        with bpy.data.libraries.load(source_file, link=False) as (data_from, data_to):
            if particle_settings_name in data_from.particles:
                data_to.particles = [particle_settings_name]  
        if particle_settings_name in bpy.data.particles:
            target_object = bpy.context.active_object 
            bpy.ops.object.particle_system_add()
            particle_system = target_object.particle_systems[-1]
            particle_system.settings = bpy.data.particles[particle_settings_name]
            bpy.ops.outliner.orphans_purge(do_recursive=True)
            particle_system.name = "KH-FUR"
            particle_system.settings = particle_system.settings.copy()
            bpy.context.view_layer.update()
            
            # Set as active
            context.scene.selected_particle_system = len(target_object.particle_systems) - 1
            context.scene.selected_scatter_modifier = ""
        
        # with bpy.data.libraries.load(source_file) as (data_from, data_to):
        #     data_to.collections = ["KH-Scatter1"]
        # for collection in data_to.collections:
        #     bpy.context.collection.children.link(collection)
        #     bpy.ops.outliner.orphans_purge(do_recursive=True)
        
        return {'FINISHED'}

class kh_scatter_asset_library(bpy.types.Operator):
    bl_idname = "object.kh_scatter_asset_library"
    bl_label = "Scatter Asset Library"
    bl_description = "Scatter selected assets from Asset Browser using Scatter on Surface modifier"
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "Please select a mesh object first")
            return {'CANCELLED'}
        
        # 1. Get selected assets
        assets = get_selected_assets_from_browser(context)
        if not assets:
            self.report({'WARNING'}, "No assets selected in the Asset Browser")
            return {'CANCELLED'}
        
        # 2. Create a new unique collection
        KH_Scatter_collection()
        coll_name = f"Scatter_{obj.name}"
        collection = bpy.data.collections.new(coll_name)
        
        # Link to KH-Scatter if it exists, otherwise to scene root
        kh_scatter_coll = bpy.data.collections.get("KH-Scatter")
        if kh_scatter_coll:
            kh_scatter_coll.children.link(collection)
        else:
            context.scene.collection.children.link(collection)
        # Exclude from View Layer (the checkbox in Outliner)
        context.view_layer.update()
        lc = get_layer_collection(context.view_layer.layer_collection, collection.name)
        if lc:
            lc.exclude = True
        
        # 3. Add assets to collection
        for asset_data in assets:
            spawn_asset_for_scatter(context, asset_data, collection)
        
        # 4. Add "Scatter on Surface" modifier
        mod_name = "Scatter on Surface"
        try:
            # We always add a new one to support multiple layers
            bpy.ops.object.modifier_add_node_group(
                asset_library_type='ESSENTIALS', 
                asset_library_identifier="", 
                relative_asset_identifier="nodes/geometry_nodes_essentials.blend/NodeTree/Scatter on Surface"
            )
            modifier = obj.modifiers[-1]
            # Rename it (Blender will auto-increment if name exists)
            modifier.name = mod_name
        except Exception as e:
            self.report({'ERROR'}, f"Could not add 'Scatter on Surface' modifier: {e}")
            return {'CANCELLED'}
        
        # 5. Set modifier inputs (Collection, Instance Type, and Randomize)
        # 5. Set modifier inputs (Hard Refresh Strategy)
        if modifier and modifier.type == 'NODES':
            context.view_layer.update()
            
            print(f"KH-Scatter: Performing Hard Refresh for '{modifier.name}'...")
            
            # 1. Capture the node group
            ng = modifier.node_group
            
            try: modifier["Socket_30"] = 0 # 
            except: pass

            try: modifier["Socket_31"] =10 # 
            except: pass

            # 2. Set the integer values (Safe IDProperties)
            try: modifier["Socket_6"] = 0 # Instance Type -> Collection
            except: pass
            
            try: modifier["Socket_39"] = True # Randomize
            except: pass

            try: modifier["Socket_17"] = True # Pick Instance
            except: pass

            try: modifier["Socket_35"][2] = 6.28319 
            except: pass

            try: modifier["Socket_41"] = 0.5
            except: pass
                    

            # 3. Find and Link Collection (Using robust type checking)
            try:
                # Specifically target Socket 7 as requested by user
                try: 
                    modifier["Socket_7"] = collection
                    print("KH-Scatter: Linked collection directly to Socket_7")
                except:
                    pass

                # Fallback to dynamic search
                items = ng.interface.items_tree if hasattr(ng.interface, "items_tree") else ng.inputs
                for input in items:
                    # Ignore outputs/panels
                    if hasattr(input, "item_type") and input.item_type != 'INPUT': continue
                    
                    # Check for collection socket
                    if "Collection" in input.name or input.type == 'COLLECTION':
                        # Only set if not already set or as a double check
                        modifier[input.identifier] = collection
                        print(f"KH-Scatter: Linked collection to {input.identifier}")
            except Exception as e:
                print(f"KH-Scatter: Collection link error: {e}")

            # 4. THE HARD REFRESH: Re-assign node_group to force UI rebuild
            try:
                modifier.node_group = ng
                context.view_layer.update()
                # Set as active modifier for settings
                context.scene.selected_scatter_modifier = modifier.name
                context.scene.selected_particle_system = -1
            except: pass

        return {'FINISHED'}
    
class kh_scatter_particle_asset_library(bpy.types.Operator):
    bl_idname = "object.kh_scatter_particle_asset_library"
    bl_label = "Scatter Asset Library (Particle)"
    bl_description = "Scatter selected assets from Asset Browser using Particle System (Grass base)"
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "Please select a mesh object first")
            return {'CANCELLED'}
        
        # 1. Get selected assets
        assets = get_selected_assets_from_browser(context)
        if not assets:
            self.report({'WARNING'}, "No assets selected in the Asset Browser")
            return {'CANCELLED'}
        
        # 2. Setup Base Particle Settings (Copy from KH-Grass)
        KH_Scatter_collection()
        source_file = os.path.join(os.path.dirname(__file__), "scatter.blend")
        particle_settings_name = "KH-Grass"

        with bpy.data.libraries.load(source_file, link=False) as (data_from, data_to):
            if particle_settings_name in data_from.particles:
                data_to.particles = [particle_settings_name] 
        
        # 3. Create a unique collection for assets
        coll_name = f"Scatter_P_{obj.name}"
        collection = bpy.data.collections.new(coll_name)
        
        # Link to KH-Scatter if it exists, otherwise to scene
        kh_scatter_coll = bpy.data.collections.get("KH-Scatter")
        if kh_scatter_coll:
            kh_scatter_coll.children.link(collection)
        else:
            context.scene.collection.children.link(collection)
            
        # Exclude from View Layer (the checkbox in Outliner)
        context.view_layer.update()
        lc = get_layer_collection(context.view_layer.layer_collection, collection.name)
        if lc:
            lc.exclude = True
        
        # 4. Add assets to collection
        for asset_data in assets:
            obj_inst = spawn_asset_for_scatter(context, asset_data, collection)
            if obj_inst:
                # Rotate 90 degrees on X to align Z-up model with Particle Y-up system
                obj_inst.rotation_euler[1] = math.pi / 2

        # 5. Add Particle System
        bpy.ops.object.particle_system_add()
        particle_system = obj.particle_systems[-1]
        
        if particle_settings_name in bpy.data.particles:
            particle_system.settings = bpy.data.particles[particle_settings_name]
            particle_system.settings = particle_system.settings.copy()
            
        particle_system.name = f"{coll_name}"
        if particle_system.settings:
            particle_system.settings.name = particle_system.name

        
        # 6. Set to use the new collection
        particle_system.settings.render_type = 'COLLECTION'
        particle_system.settings.instance_collection = collection
        particle_system.settings.use_collection_pick_random = True
        
        # Enable rotation and set to Global Z to keep objects upright
        particle_system.settings.use_rotations = True
        #particle_system.settings.rotation_mode = 'GLOB_Y'
        particle_system.settings.rotation_mode = 'VEL'
        particle_system.settings.phase_factor_random = 2.0 # Add some random rotation by default
        particle_system.settings.use_rotation_instance = True
        particle_system.seed = random.randint(1, 1000)  
        particle_system.settings.count = 10
        particle_system.settings.child_percent = 1
        particle_system.settings.rendered_child_count = 1

     
        
        # 7. Cleanup and Refresh
        bpy.ops.outliner.orphans_purge(do_recursive=True)
        bpy.context.view_layer.update()

        
        # Set as active
        context.scene.selected_particle_system = len(obj.particle_systems) - 1
        context.scene.selected_scatter_modifier = ""
        
        return {'FINISHED'}
    
class KH_OT_ScatterToggleDisplay(bpy.types.Operator):
    bl_idname = "object.kh_scatter_toggle_display"
    bl_label = "Toggle Scatter Display"
    bl_description = "Toggle between Bounds and Textured display for scatter objects to improve performance"
    
    collection_name: bpy.props.StringProperty(default="")
    
    def execute(self, context):
        # Look for KH-Scatter or kh-scatter (case insensitive)
        main_coll = None
        target_name = self.collection_name.lower() if self.collection_name else "kh-scatter"
        
        for c in bpy.data.collections:
            if c.name.lower() == target_name:
                main_coll = c
                break
                
        if not main_coll:
            # Fallback for individual item toggle if collection_name was specified but not found
            if self.collection_name:
                main_coll = bpy.data.collections.get(self.collection_name)
        
        if not main_coll:
            self.report({'INFO'}, f"Scatter collection not found")
            return {'FINISHED'}
            
        objs = [o for o in main_coll.all_objects if o.type == 'MESH']
        if not objs:
            return {'FINISHED'}
            
        # Determine target state - if first is BOUNDS, switch to TEXTURED
        target_type = 'TEXTURED' if objs[0].display_type == 'BOUNDS' else 'BOUNDS'
            
        for o in objs:
            o.display_type = target_type
            o.show_bounds = False
            
        return {'FINISHED'}
    
class kh_show_viewporh(bpy.types.Operator):
    bl_idname = "object.kh_show_viewporh"
    bl_label = "show_viewpor"
    
    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.modifiers:
                for mod in obj.modifiers:
                    if mod.type == 'PARTICLE_SYSTEM':
                        mod.show_viewport = False
                    elif mod.type == 'NODES' and (mod.name.startswith("Scatter") or mod.name.startswith("KH-")):
                        mod.show_viewport = False
        return {'FINISHED'}
    
class kh_show_viewpor(bpy.types.Operator):
    bl_idname = "object.kh_show_viewpor"
    bl_label = "show_viewpor"
    def execute(self, context):
        for obj in bpy.data.objects:
            if obj.modifiers:
                for mod in obj.modifiers:
                    if mod.type == 'PARTICLE_SYSTEM':
                        mod.show_viewport = True
                    elif mod.type == 'NODES' and (mod.name.startswith("Scatter") or mod.name.startswith("KH-")):
                        mod.show_viewport = True
        return {'FINISHED'}
    
    

class kh_scatter_Panel(bpy.types.Panel):
    bl_label = ""
    bl_idname = "KH_PT_ParticleSystemPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'KH-Tools'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        # استخدام الدالة المساعدة للبحث عن إعدادات الإضافة
        return get_addon_preferences(context, 'KH_Scatter') == True

    def draw_header(self, context: bpy.types.Context):
        layout = self.layout
        try:
            #self.layout.label(text="", icon="OUTLINER_OB_CURVES")
            layout.label(text="Scatter", icon="OUTLINER_OB_CURVES")
        except KeyError:
            pass
        objects = bpy.data.objects
        found = False  # علم لتحديد ما إذا تم العثور على كائن مناسب

#        for obj in objects:
#            if obj.type == 'MESH' and obj.modifiers:
#                for modifier in obj.modifiers:
#                    if modifier.type == 'PARTICLE_SYSTEM':
#                        if modifier.show_viewport == True:
#                            layout.operator("object.kh_show_viewporh", text="", icon="RESTRICT_VIEW_OFF")
#                        else:
#                            layout.operator("object.kh_show_viewpor", text="", icon="RESTRICT_VIEW_ON")
#                        
#                        found = True  # تم العثور على الكائن المناسب
#                        break  # كسر الحلقة الداخلية
#                if found:
#                    break  # كسر الحلقة الخارجية
                
        
        for obj in objects:
            if obj.type == 'MESH' and obj.modifiers:
                for modifier in obj.modifiers:
                    # Check if it's a KH/Scatter system (Particle or GN)
                    is_ps = (modifier.type == 'PARTICLE_SYSTEM')
                    is_gn = (modifier.type == 'NODES' and (modifier.name.startswith("Scatter") or modifier.name.startswith("KH-")))
                    
                    if (is_ps or is_gn) and modifier.show_viewport:
                        # If any system is currently visible
                        layout.operator("object.kh_show_viewporh", text="", icon="RESTRICT_VIEW_OFF")
                        found = True
                        break
                if found:
                    break

        if not found:
            # إذا لم يتم العثور على أي كائن يحتوي على نظام جسيمات ظاهر
            layout.operator("object.kh_show_viewpor", text="", icon="RESTRICT_VIEW_ON")

        # New Toggle Display Button
        main_coll = None
        for c in bpy.data.collections:
            if c.name.lower() == "kh-scatter":
                main_coll = c
                break
                
        if main_coll:
            first_mesh = next((o for o in main_coll.all_objects if o.type == 'MESH'), None)
            icon = "SHADING_BBOX" if first_mesh and first_mesh.display_type != 'BOUNDS' else "SHADING_TEXTURE"
            layout.operator("object.kh_scatter_toggle_display", text="", icon=icon).collection_name = main_coll.name

       

#    @classmethod
#    def poll(cls, context):
#        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        # Check if there are any particle systems or scatter modifiers on the active object
        has_scatter = False
        if obj and obj.type == 'MESH':
            if len(obj.particle_systems) > 0:
                has_scatter = True
            else:
                for mod in obj.modifiers:
                    if mod.type == 'NODES' and (mod.name.startswith("Scatter on Surface") or mod.name.startswith("KH-")):
                        has_scatter = True
                        break
        
        # Unified Viewport Display (Simplify) Settings - Show only if scatter items exist
        if has_scatter:
            box = layout.box()
            row = box.row()
            row.label(text="Viewport Display", icon="MEMORY")
            if context.scene.render.use_simplify == False:
                row.prop(context.scene.render, "use_simplify", text="") 
            else:
                row.prop(context.scene.render, "simplify_child_particles", text="")
                                                    
        if obj and obj.type == 'MESH':
            # 1. Show existing Scatter Layers (Particle Systems and GeoNodes)
            any_scatter = False
            selected_type = 'NONE' # 'PSYS' or 'MOD'
            
            # Draw Particle Systems
            for ps_idx, ps in enumerate(obj.particle_systems):
                any_scatter = True
                is_selected = (context.scene.selected_particle_system == ps_idx)
                if is_selected: selected_type = 'PSYS'
                
                box = layout.box()
                if is_selected:
                    box.alert = True # Highlight selected
                
                row = box.row(align=True)
                
                # Selection button
                select_icon = 'RESTRICT_SELECT_OFF' if is_selected else 'RESTRICT_SELECT_ON'
                row.operator("object.select_particle_system", text="", icon=select_icon).particle_system_index = ps_idx
                
                # Compact selector: Hide X, Copy, and Fake User, keep only the name and interactive users count
                if ps.settings:
                    row.prop(ps, "settings", text="", icon='PARTICLES')
                    if ps.settings.users > 1:
                        op = row.operator("object.kh_make_single_user", text=str(ps.settings.users))
                        op.object_name = obj.name
                        op.psys_index = ps_idx
                        op.modifier_name = ""
                else:
                    row.label(text="None", icon='PARTICLES')
                
                # Find associated modifier for visibility toggles
                for mod in obj.modifiers:
                    if mod.type == 'PARTICLE_SYSTEM' and mod.particle_system == ps:
                        # Toggle Display button
                        coll = ps.settings.instance_collection
                        if coll:
                            first_mesh = next((o for o in coll.all_objects if o.type == 'MESH'), None)
                            icon = "SHADING_BBOX" if first_mesh and first_mesh.display_type != 'BOUNDS' else "SHADING_TEXTURE"
                            row.operator("object.kh_scatter_toggle_display", text="", icon=icon).collection_name = coll.name
                            
                        row.prop(mod, "show_viewport", text="", icon="RESTRICT_VIEW_ON")
                        row.prop(mod, "show_render", text="", icon="RESTRICT_RENDER_ON")
                        break
                
                row.operator("object.particle_delete", text="", icon='TRASH').particle_system_index1 = ps_idx

            # Draw "Scatter on Surface" Geometry Nodes modifiers
            for mod in obj.modifiers:
                if mod.type == 'NODES' and (mod.name.startswith("Scatter on Surface") or mod.name.startswith("KH-")):
                    any_scatter = True
                    is_selected = (context.scene.selected_scatter_modifier == mod.name)
                    if is_selected: selected_type = 'MOD'
                    
                    box = layout.box()
                    if is_selected:
                        box.alert = True
                        
                    row = box.row(align=True)
                    
                    # Selection button
                    select_icon = 'RESTRICT_SELECT_OFF' if is_selected else 'RESTRICT_SELECT_ON'
                    row.operator("object.select_scatter_modifier", text="", icon=select_icon).modifier_name = mod.name
                    
                    # Compact selector: Hide X, Copy, and Fake User, keep only the name and interactive users count
                    if mod.node_group:
                        row.prop(mod, "node_group", text="", icon='GEOMETRY_NODES')
                        if mod.node_group.users > 1:
                            op = row.operator("object.kh_make_single_user", text=str(mod.node_group.users))
                            op.object_name = obj.name
                            op.modifier_name = mod.name
                            op.psys_index = -1
                    else:
                        row.label(text="None", icon='GEOMETRY_NODES')
                    
                    # Toggle Display button
                    coll = mod.get("Socket_7") or mod.get("Collection")
                    if coll and isinstance(coll, bpy.types.Collection):
                        first_mesh = next((o for o in coll.all_objects if o.type == 'MESH'), None)
                        icon = "SHADING_BBOX" if first_mesh and first_mesh.display_type != 'BOUNDS' else "SHADING_TEXTURE"
                        row.operator("object.kh_scatter_toggle_display", text="", icon=icon).collection_name = coll.name

                    row.prop(mod, "show_viewport", text="", icon="RESTRICT_VIEW_ON")
                    row.prop(mod, "show_render", text="", icon="RESTRICT_RENDER_ON")
                    
                    op = row.operator("object.particle_delete", text="", icon='TRASH')
                    op.modifier_name = mod.name

            if any_scatter:
                # Show Settings for selected layer
                if selected_type == 'PSYS':
                    selected_idx = context.scene.selected_particle_system
                    if 0 <= selected_idx < len(obj.particle_systems):
                        selected_ps = obj.particle_systems[selected_idx]
                        bottom_panel = layout.box()
                        bottom_panel.label(text=f"Settings: {selected_ps.name}", icon="SETTINGS")
                        bottom_panel.prop(selected_ps.settings, "count", text="Distribution")
                        bottom_panel.prop(selected_ps.settings, "hair_length", text="Scale")
                        bottom_panel.prop(selected_ps.settings, "size_random", text="S-Random")
                        bottom_panel.prop(selected_ps.settings, "phase_factor_random", text="R-Random")
                        bottom_panel.prop(selected_ps, "seed", text="Seed")
                        bottom_panel.prop(selected_ps.settings, "use_rotation_instance", text="Rotation")

                elif selected_type == 'MOD':
                    mod_name = context.scene.selected_scatter_modifier
                    mod = obj.modifiers.get(mod_name)
                    if mod and mod.type == 'NODES' and mod.node_group:
                        box = layout.box()
                        box.label(text=f"Scatter Settings: {mod.name}", icon="GEOMETRY_NODES")
                        
                        # Explicitly show specific sockets requested by user
                        try:
                            # Socket 4
                            row = box.row()
                            row.prop(mod, '["Socket_31"]', text="Amount")
                            #row.prop(mod, '["Socket_4"]', text="Density Max")
                            
                            # Socket 27
                            # row = box.row()
                            # row.prop(mod, '["Socket_27"]', text="Density Factor")

                            # Socket 35 (Rotation Z)
                            row = box.row()
                            row.prop(mod, '["Socket_35"]', index=2, text="Rotation Z")
                            
                            # Socket 41
                            row = box.row()
                            row.prop(mod, '["Socket_41"]', text="Scale Randomness")
                            
                            # Socket 45 (Seed)
                            row = box.row()
                            row.prop(mod, '["Socket_45"]', text="Seed")
                        except:
                            pass

                        ng = mod.node_group
                        # Update skip list to include all handled sockets
                        skip_inputs = {"Surface", "Selection", "Collection", 
                                       "Socket_4", "Socket_27", "Socket_35", "Socket_41", "Socket_45"}
                        
                        # Get items from interface (Blender 4.0+)
                        items = []
                        if hasattr(ng, "interface"):
                            items = getattr(ng.interface, "items_tree", getattr(ng.interface, "items", []))
                        
                        for item in items:
                            if hasattr(item, "item_type") and item.item_type != 'INPUT':
                                continue
                            
                            identifier = getattr(item, "identifier", "")
                            if not identifier or identifier in skip_inputs:
                                continue
                                
                            name = item.name
                            if item.type == 'MATERIAL':
                                continue
                                
                            row = box.row()
                            try:
                                row.prop(mod, f'["{identifier}"]', text=name)
                            except:
                                pass
            
            # Show creation buttons
            layout.label(text="Add New Scatter:", icon="ADD")
            grid = layout.grid_flow(columns=2, align=True)
            grid.operator("object.import_particle_settings1", text="Grass", icon="OUTLINER_OB_CURVES")
            grid.operator("object.import_kh_grass1", text="Grass 1", icon="OUTLINER_OB_CURVES")
            grid.operator("object.import_kh_grassl", text="Grass L", icon="OUTLINER_OB_CURVES")
            grid.operator("object.import_particle_settings2", text="Leaves", icon="OUTLINER_OB_CURVES")
            grid.operator("object.import_particle_settings3", text="Ivy Wall", icon="OUTLINER_OB_CURVES")
            grid.operator("object.import_particle_settings5", text="Rock", icon="OUTLINER_OB_POINTCLOUD")
            grid.operator("object.fur", text="FUR", icon="PARTICLES")
            #grid.operator("object.kh_scatter_asset_library", text="Asset", icon="ASSET_MANAGER")
            grid.operator("object.kh_scatter_particle_asset_library", text="From Asset", icon="ASSET_MANAGER")
        else:
            layout.label(text="Select your object first !", icon="QUESTION")
            
class KH_OT_MakeSingleUser(bpy.types.Operator):
    bl_idname = "object.kh_make_single_user"
    bl_label = "Make Single User"
    bl_description = "Make this scatter unique (unlinks from other objects)"
    
    object_name: bpy.props.StringProperty()
    modifier_name: bpy.props.StringProperty(default="")
    psys_index: bpy.props.IntProperty(default=-1)
    
    def execute(self, context):
        obj = bpy.data.objects.get(self.object_name)
        if not obj: return {'CANCELLED'}
        
        if self.modifier_name:
            mod = obj.modifiers.get(self.modifier_name)
            if mod and mod.type == 'NODES' and mod.node_group:
                # Duplicate the node group
                mod.node_group = mod.node_group.copy()
                self.report({'INFO'}, "Scatter data is now unique")
        elif self.psys_index >= 0:
            if 0 <= self.psys_index < len(obj.particle_systems):
                ps = obj.particle_systems[self.psys_index]
                if ps.settings:
                    # Duplicate the particle settings
                    ps.settings = ps.settings.copy()
                    self.report({'INFO'}, "Particle data is now unique")
        
        return {'FINISHED'}

class KH_OT_NavigateToScatter(bpy.types.Operator):
    bl_idname = "object.kh_navigate_to_scatter"
    bl_label = "Navigate to Scatter"
    bl_description = "Select the object and highlight this scatter system"
    
    object_name: bpy.props.StringProperty()
    modifier_name: bpy.props.StringProperty(default="")
    psys_index: bpy.props.IntProperty(default=-1)
    
    def execute(self, context):
        target_obj = bpy.data.objects.get(self.object_name)
        if not target_obj:
            self.report({'WARNING'}, f"Object '{self.object_name}' not found")
            return {'CANCELLED'}
        
        # Deselect all, select and make active
        bpy.ops.object.select_all(action='DESELECT')
        target_obj.select_set(True)
        context.view_layer.objects.active = target_obj
        
        # Highlight the specific scatter system
        if self.modifier_name:
            context.scene.selected_scatter_modifier = self.modifier_name
            context.scene.selected_particle_system = -1
        elif self.psys_index >= 0:
            context.scene.selected_particle_system = self.psys_index
            context.scene.selected_scatter_modifier = ""
        
        return {'FINISHED'}

class KH_OT_ToggleScatterVisibility(bpy.types.Operator):
    bl_idname = "object.kh_toggle_scatter_visibility"
    bl_label = "Toggle Scatter Visibility"
    bl_description = "Toggle viewport or render visibility for this scatter"
    
    object_name: bpy.props.StringProperty()
    modifier_name: bpy.props.StringProperty(default="")
    psys_index: bpy.props.IntProperty(default=-1)
    toggle_type: bpy.props.StringProperty(default="VIEWPORT")  # VIEWPORT or RENDER
    
    def execute(self, context):
        target_obj = bpy.data.objects.get(self.object_name)
        if not target_obj:
            return {'CANCELLED'}
        
        if self.modifier_name:
            mod = target_obj.modifiers.get(self.modifier_name)
            if mod:
                if self.toggle_type == 'VIEWPORT':
                    mod.show_viewport = not mod.show_viewport
                else:
                    mod.show_render = not mod.show_render
        elif self.psys_index >= 0:
            # Find the particle system modifier
            if 0 <= self.psys_index < len(target_obj.particle_systems):
                psys = target_obj.particle_systems[self.psys_index]
                for mod in target_obj.modifiers:
                    if mod.type == 'PARTICLE_SYSTEM' and mod.particle_system == psys:
                        if self.toggle_type == 'VIEWPORT':
                            mod.show_viewport = not mod.show_viewport
                        else:
                            mod.show_render = not mod.show_render
                        break
        
        return {'FINISHED'}

class KH_OT_DeleteScatterFromProject(bpy.types.Operator):
    bl_idname = "object.kh_delete_scatter_from_project"
    bl_label = "Delete Scatter"
    bl_description = "Delete this scatter system"
    
    object_name: bpy.props.StringProperty()
    modifier_name: bpy.props.StringProperty(default="")
    psys_index: bpy.props.IntProperty(default=-1)
    
    def execute(self, context):
        target_obj = bpy.data.objects.get(self.object_name)
        if not target_obj:
            return {'CANCELLED'}
        
        # Temporarily make this the active object
        prev_active = context.view_layer.objects.active
        context.view_layer.objects.active = target_obj
        
        if self.modifier_name:
            # Use the existing delete operator logic
            bpy.ops.object.particle_delete(modifier_name=self.modifier_name)
        elif self.psys_index >= 0:
            bpy.ops.object.particle_delete(particle_system_index1=self.psys_index)
        
        # Restore active object
        if prev_active and prev_active.name in bpy.data.objects:
            context.view_layer.objects.active = prev_active
        
        return {'FINISHED'}


class kh_scatter_Project_Panel(bpy.types.Panel):
    bl_label = ""
    bl_idname = "KH_PT_Scatter_Project_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'KH-Tools'
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "KH_PT_ParticleSystemPanel"
    
    @classmethod
    def poll(cls, context):
        return get_addon_preferences(context, 'KH_Scatter') == True
    
    def draw_header(self, context: bpy.types.Context):
        self.layout.label(text="Project Scatter", icon="WORLD")
    
    def draw(self, context):
        layout = self.layout
        
        found_any = False
        
        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue
            
            # --- GeoNodes Scatter modifiers ---
            for mod in obj.modifiers:
                if mod.type == 'NODES' and (mod.name.startswith("Scatter on Surface") or mod.name.startswith("KH-")):
                    found_any = True
                    is_current = (context.object == obj and context.scene.selected_scatter_modifier == mod.name)
                    
                    box = layout.box()
                    if is_current:
                        box.alert = True
                    
                    # Header row: object name
                    row = box.row(align=True)
                    
                    # Navigate button
                    nav_icon = 'RESTRICT_SELECT_OFF' if is_current else 'RESTRICT_SELECT_ON'
                    op_nav = row.operator("object.kh_navigate_to_scatter", text="", icon=nav_icon)
                    op_nav.object_name = obj.name
                    op_nav.modifier_name = mod.name
                    op_nav.psys_index = -1
                    
                    # Editable object name
                    row.prop(obj, "name", text="", icon="GEOMETRY_NODES")
                    
                    # Display toggle (bounds/textured)
                    coll = mod.get("Socket_7") or mod.get("Collection")
                    if coll and isinstance(coll, bpy.types.Collection):
                        first_mesh = next((o for o in coll.all_objects if o.type == 'MESH'), None)
                        disp_icon = "SHADING_BBOX" if first_mesh and first_mesh.display_type != 'BOUNDS' else "SHADING_TEXTURE"
                        row.operator("object.kh_scatter_toggle_display", text="", icon=disp_icon).collection_name = coll.name
                    
                    # Viewport visibility
                    vp_icon = 'RESTRICT_VIEW_OFF' if mod.show_viewport else 'RESTRICT_VIEW_ON'
                    op_vp = row.operator("object.kh_toggle_scatter_visibility", text="", icon=vp_icon)
                    op_vp.object_name = obj.name
                    op_vp.modifier_name = mod.name
                    op_vp.toggle_type = 'VIEWPORT'
                    
                    # Render visibility
                    rn_icon = 'RESTRICT_RENDER_OFF' if mod.show_render else 'RESTRICT_RENDER_ON'
                    op_rn = row.operator("object.kh_toggle_scatter_visibility", text="", icon=rn_icon)
                    op_rn.object_name = obj.name
                    op_rn.modifier_name = mod.name
                    op_rn.toggle_type = 'RENDER'
                    
                    # Delete
                    op_del = row.operator("object.kh_delete_scatter_from_project", text="", icon='TRASH')
                    op_del.object_name = obj.name
                    op_del.modifier_name = mod.name
            
            # --- Particle Systems ---
            for ps_idx, ps in enumerate(obj.particle_systems):
                found_any = True
                is_current = (context.object == obj and context.scene.selected_particle_system == ps_idx)
                
                box = layout.box()
                if is_current:
                    box.alert = True
                
                row = box.row(align=True)
                
                # Navigate button
                nav_icon = 'RESTRICT_SELECT_OFF' if is_current else 'RESTRICT_SELECT_ON'
                op_nav = row.operator("object.kh_navigate_to_scatter", text="", icon=nav_icon)
                op_nav.object_name = obj.name
                op_nav.modifier_name = ""
                op_nav.psys_index = ps_idx
                
                # Editable object name
                row.prop(obj, "name", text="", icon="PARTICLES")
                
                # Display toggle (bounds/textured)
                coll = ps.settings.instance_collection if ps.settings else None
                if coll:
                    first_mesh = next((o for o in coll.all_objects if o.type == 'MESH'), None)
                    disp_icon = "SHADING_BBOX" if first_mesh and first_mesh.display_type != 'BOUNDS' else "SHADING_TEXTURE"
                    row.operator("object.kh_scatter_toggle_display", text="", icon=disp_icon).collection_name = coll.name
                
                # Find modifier for viewport/render visibility
                ps_mod = None
                for mod in obj.modifiers:
                    if mod.type == 'PARTICLE_SYSTEM' and mod.particle_system == ps:
                        ps_mod = mod
                        break
                
                if ps_mod:
                    # Viewport visibility
                    vp_icon = 'RESTRICT_VIEW_OFF' if ps_mod.show_viewport else 'RESTRICT_VIEW_ON'
                    op_vp = row.operator("object.kh_toggle_scatter_visibility", text="", icon=vp_icon)
                    op_vp.object_name = obj.name
                    op_vp.psys_index = ps_idx
                    op_vp.toggle_type = 'VIEWPORT'
                    
                    # Render visibility
                    rn_icon = 'RESTRICT_RENDER_OFF' if ps_mod.show_render else 'RESTRICT_RENDER_ON'
                    op_rn = row.operator("object.kh_toggle_scatter_visibility", text="", icon=rn_icon)
                    op_rn.object_name = obj.name
                    op_rn.psys_index = ps_idx
                    op_rn.toggle_type = 'RENDER'
                
                # Delete
                op_del = row.operator("object.kh_delete_scatter_from_project", text="", icon='TRASH')
                op_del.object_name = obj.name
                op_del.psys_index = ps_idx
        
        if not found_any:
            layout.label(text="No scatter systems in project", icon="INFO")


class kh_scatter_Asset_LIST_Panel(bpy.types.Panel):
    bl_label = ""
    bl_idname = "KH_PT_Particle_asset_list_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'KH-Tools'
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id   = "KH_PT_ParticleSystemPanel"
    
    @classmethod
    def poll(cls, context):
        # استخدام الدالة المساعدة للبحث عن إعدادات الإضافة
        return get_addon_preferences(context, 'KH_Scatter') == True

    def draw_header(self, context: bpy.types.Context):
        try:
            layout = self.layout
            layout.label(text="Asset LIST", icon="ASSET_MANAGER")

        except KeyError:
            pass

    def draw(self, context):                 
        layout = self.layout
        obj = context.object
        if not obj or obj.type != 'MESH':
            return

        # 1. Handle Particle Systems
        if obj.particle_systems:
            for ps in obj.particle_systems:
                # Only show for the selected one or if it's a KH/Scatter system
                if ps.settings.render_type == 'COLLECTION' and ps.settings.instance_collection:
                    box = layout.box()
                    box.label(text=f"PS: {ps.name}", icon='PARTICLES')
                    
                    if ps.settings.use_collection_count:
                        for particle_weight in ps.settings.instance_weights:
                            row = box.row(align=True)
                            name = particle_weight.name.split(':')[0]
                            
                            # Select in scene button
                            target_obj = bpy.data.objects.get(particle_weight.name)
                            if not target_obj:
                                clean_name = particle_weight.name.split(':')[0]
                                target_obj = bpy.data.objects.get(clean_name)
                            
                            if not target_obj and ps.settings.instance_collection:
                                for o in ps.settings.instance_collection.objects:
                                    if o.name.startswith(name):
                                        target_obj = o
                                        break
                            
                            if target_obj:
                                # Determine icon based on solo state
                                soloed_name = context.scene.get("kh_soloed_asset", "")
                                if soloed_name:
                                    sel_icon = 'HIDE_OFF' if (soloed_name == target_obj.name) else 'RESTRICT_SELECT_ON'
                                else:
                                    sel_icon = 'RESTRICT_SELECT_OFF'
                                op_sel = row.operator("object.kh_select_asset_in_scene", text="", icon=sel_icon)
                                op_sel.object_name = target_obj.name
                                if ps.settings.instance_collection:
                                    op_sel.collection_name = ps.settings.instance_collection.name
                            
                            row.prop(particle_weight, "count", text=name)
                            
                            if target_obj:
                                row.prop(target_obj, "scale", index=2, text="Scale")
                    else:
                        # Fallback: show all objects in collection if weight not used
                        coll = ps.settings.instance_collection
                        for sub_obj in coll.objects:
                            row = box.row(align=True)
                            soloed_name = context.scene.get("kh_soloed_asset", "")
                            if soloed_name:
                                sel_icon = 'HIDE_OFF' if (soloed_name == sub_obj.name) else 'RESTRICT_SELECT_ON'
                            else:
                                sel_icon = 'RESTRICT_SELECT_OFF'
                            op_sel = row.operator("object.kh_select_asset_in_scene", text="", icon=sel_icon)
                            op_sel.object_name = sub_obj.name
                            op_sel.collection_name = coll.name
                            row.label(text=sub_obj.name)
                            row.prop(sub_obj, "scale", index=2, text="Scale")

        # 2. Handle Geometry Nodes (Scatter on Surface)
        for mod in obj.modifiers:
            if mod.type == 'NODES' and mod.node_group:
                # Check if it's a scatter modifier
                if mod.name.startswith(("Scatter", "KH-")):
                    # Try to find the collection input
                    coll = None
                    # Method 1: Check known socket names/identifiers
                    if "Socket_7" in mod and isinstance(mod["Socket_7"], bpy.types.Collection):
                        coll = mod["Socket_7"]
                    else:
                        # Method 2: Search interface for Collection type
                        for input in mod.node_group.interface.items_tree:
                            if input.item_type == 'INPUT' and input.type == 'COLLECTION':
                                try:
                                    potential_coll = mod[input.identifier]
                                    if isinstance(potential_coll, bpy.types.Collection):
                                        coll = potential_coll
                                        break
                                except: pass
                    
                    if coll:
                        box = layout.box()
                        box.label(text=f"Mod: {mod.name} ({coll.name})", icon='GEOMETRY_NODES')
                        for sub_obj in coll.objects:
                            row = box.row(align=True)
                            soloed_name = context.scene.get("kh_soloed_asset", "")
                            if soloed_name:
                                sel_icon = 'HIDE_OFF' if (soloed_name == sub_obj.name) else 'RESTRICT_SELECT_ON'
                            else:
                                sel_icon = 'RESTRICT_SELECT_OFF'
                            op_sel = row.operator("object.kh_select_asset_in_scene", text="", icon=sel_icon)
                            op_sel.object_name = sub_obj.name
                            op_sel.collection_name = coll.name
                            row.label(text=sub_obj.name)
                            # Control Z scale which handlers will then unify to X and Y
                            row.prop(sub_obj, "scale", index=2, text="Scale")

# Replaced by Universal Handler

class KH_OT_SelectAssetInScene(bpy.types.Operator):
    bl_idname = "object.kh_select_asset_in_scene"
    bl_label = "Solo Asset Type on Surface"
    bl_description = "Show only this asset type on the surface to identify it. Click again to show all"
    
    object_name: bpy.props.StringProperty()
    collection_name: bpy.props.StringProperty(default="")
    
    def execute(self, context):
        target_obj = bpy.data.objects.get(self.object_name)
        if not target_obj:
            self.report({'WARNING'}, f"Object '{self.object_name}' not found")
            return {'CANCELLED'}
        
        coll = bpy.data.collections.get(self.collection_name) if self.collection_name else None
        if not coll:
            self.report({'WARNING'}, "Collection not found")
            return {'CANCELLED'}
        
        # Check if this object is already soloed (all others are hidden)
        other_objects = [o for o in coll.objects if o != target_obj]
        all_others_hidden = all(o.hide_render for o in other_objects) if other_objects else False
        target_is_soloed = all_others_hidden and not target_obj.hide_render and len(other_objects) > 0
        
        if target_is_soloed:
            # UN-SOLO: Restore all objects visibility
            for o in coll.objects:
                o.hide_render = False
                o.hide_viewport = False
            # Store the un-soloed state
            context.scene["kh_soloed_asset"] = ""
            self.report({'INFO'}, f"Showing all types")
        else:
            # SOLO: Hide all others, show only the target
            for o in coll.objects:
                if o == target_obj:
                    o.hide_render = False
                    o.hide_viewport = False
                else:
                    o.hide_render = True
                    o.hide_viewport = True
            # Store which object is soloed
            context.scene["kh_soloed_asset"] = self.object_name
            self.report({'INFO'}, f"Soloed: {self.object_name}")
        
        # Force viewport update
        context.view_layer.update()
        
        return {'FINISHED'}


class ParticleSystemSelectOperator(bpy.types.Operator):
    bl_idname = "object.select_particle_system"
    bl_label = "Select Particle System"

    particle_system_index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.selected_particle_system = self.particle_system_index
        context.scene.selected_scatter_modifier = ""
        return {'FINISHED'}  

class ModifierSelectOperator(bpy.types.Operator):
    bl_idname = "object.select_scatter_modifier"
    bl_label = "Select Scatter Modifier"

    modifier_name: bpy.props.StringProperty()

    def execute(self, context):
        context.scene.selected_scatter_modifier = self.modifier_name
        # Set particle system index to -1 to indicate a modifier is selected
        context.scene.selected_particle_system = -1
        return {'FINISHED'}

class ParticleDeleteOperator(bpy.types.Operator):
    bl_idname = "object.particle_delete"
    bl_label = "Delete Particle System"
    particle_system_index1: bpy.props.IntProperty()
    modifier_name: bpy.props.StringProperty(default="")

    def _is_collection_used_elsewhere(self, coll, current_obj, current_mod_name="", current_psys_index=-1):
        """Check if the collection is used by any other modifier or particle system on ANY object."""
        for other_obj in bpy.data.objects:
            if other_obj.type != 'MESH':
                continue
            
            # Check GeoNodes modifiers
            for mod in other_obj.modifiers:
                if mod.type == 'NODES':
                    # Skip the modifier we are about to delete
                    if other_obj == current_obj and mod.name == current_mod_name:
                        continue
                    try:
                        mod_coll = mod.get("Socket_7") or mod.get("Collection")
                        if mod_coll and isinstance(mod_coll, bpy.types.Collection) and mod_coll == coll:
                            return True
                    except:
                        pass
            
            # Check particle systems
            for ps_idx, ps in enumerate(other_obj.particle_systems):
                # Skip the particle system we are about to delete
                if other_obj == current_obj and ps_idx == current_psys_index:
                    continue
                if ps.settings and ps.settings.instance_collection == coll:
                    return True
        
        return False

    def execute(self, context):
        obj = context.object
        if not obj:
            return {'CANCELLED'}
            
        # If modifier_name is provided (for GeoNodes)
        if self.modifier_name:
            mod = obj.modifiers.get(self.modifier_name)
            if mod:
                # Find collection associated with this modifier
                coll = None
                if mod.type == 'NODES':
                    try:
                        # Common identifiers for collection inputs in GeoNodes
                        coll = mod.get("Socket_7") or mod.get("Collection")
                    except:
                        pass
                
                # Only delete collection if it's NOT used by other modifiers/particle systems
                if coll and isinstance(coll, bpy.types.Collection):
                    if coll.name.startswith(("KH-", "Scatter_")):
                        if not self._is_collection_used_elsewhere(coll, obj, current_mod_name=self.modifier_name):
                            # Safe to delete - no other users
                            for o in list(coll.objects):
                                bpy.data.objects.remove(o, do_unlink=True)
                            bpy.data.collections.remove(coll)
                        else:
                            print(f"KH-Scatter: Collection '{coll.name}' is shared with other surfaces, keeping it.")

                obj.modifiers.remove(mod)
                bpy.ops.outliner.orphans_purge(do_recursive=True)
                return {'FINISHED'}

        # Fallback to particle system removal
        if obj.particle_systems:
            particle_system_index1 = self.particle_system_index1
            if 0 <= particle_system_index1 < len(obj.particle_systems):
                psys = obj.particle_systems[particle_system_index1]
                
                # Find associated collection
                coll = psys.settings.instance_collection
                if coll and coll.name.startswith(("KH-", "Scatter_")):
                    if not self._is_collection_used_elsewhere(coll, obj, current_psys_index=particle_system_index1):
                        # Safe to delete - no other users
                        for o in list(coll.objects):
                            bpy.data.objects.remove(o, do_unlink=True)
                        bpy.data.collections.remove(coll)
                    else:
                        print(f"KH-Scatter: Collection '{coll.name}' is shared with other surfaces, keeping it.")

                # Find associated modifier
                for mod in list(obj.modifiers):
                    if mod.type == 'PARTICLE_SYSTEM' and mod.particle_system == psys:
                        obj.modifiers.remove(mod)
                        break
                        
                bpy.ops.outliner.orphans_purge(do_recursive=True)
                
        return {'FINISHED'}        



classes = ( kh_scatter_Panel,
            kh_scatter_Project_Panel,
            kh_scatter_Asset_LIST_Panel,
            kh_scatter_Operator1,
            kh_KH_Grass1_Operator1,
            kh_KH_Grassl_Operator1,
            kh_scatter_Operator2,
            kh_scatter_Operator3,
            kh_scatter_Operator4,
            kh_scatter_Operator5,
            ParticleDeleteOperator,
            ParticleSystemSelectOperator,
            ModifierSelectOperator,
            kh_show_viewporh,
            kh_show_viewpor,
            KH_OT_ScatterToggleDisplay,
            kh_scatter_fur,
            kh_scatter_asset_library,
            kh_scatter_particle_asset_library,
            KH_OT_SelectAssetInScene,
            KH_OT_NavigateToScatter,
            KH_OT_ToggleScatterVisibility,
            KH_OT_DeleteScatterFromProject,
            KH_OT_MakeSingleUser,
                )

def register():
    for i in classes:
        register_class(i)
    bpy.types.Scene.selected_particle_system = bpy.props.IntProperty(default=0)
    bpy.types.Scene.selected_scatter_modifier = bpy.props.StringProperty(default="")
    
    # Register the universal asset scale handler
    ensure_scale_handler()

def unregister():
    for i in classes:
        unregister_class(i)
    if hasattr(bpy.types.Scene, 'selected_particle_system'):
        del bpy.types.Scene.selected_particle_system
    if hasattr(bpy.types.Scene, 'selected_scatter_modifier'):
        del bpy.types.Scene.selected_scatter_modifier



if __name__ == "__main__":
    try:
        register()
    except:
        pass
    unregister() 


