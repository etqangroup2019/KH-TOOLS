bl_info = {
    "name": "Asset Manager - Auto Catalogs",
    "author": "Cursor Assistant",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Asset Manager",
    "description": "Generate Asset Catalogs from folder structure and assign catalog IDs to Objects/Materials in .blend files",
    "warning": "",
    "doc_url": "",
    "category": "Asset",
}

import bpy
import os
import sys
import uuid
import shutil
import pathlib
import tempfile
import subprocess
import threading

# Global cancel event to allow cancel operator to signal running job
AM_CANCEL_EVENT = threading.Event()


class ASSETMANAGER_LibraryItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Library Name")
    path: bpy.props.StringProperty(name="Path")
    selected: bpy.props.BoolProperty(name="Selected", default=False)


class ASSETMANAGER_CatalogItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Catalog Name")
    path: bpy.props.StringProperty(name="Catalog Path")


class ASSETMANAGER_UL_libraries(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index=0):
        lib: ASSETMANAGER_LibraryItem = item
        row = layout.row(align=True)
        row.prop(lib, "selected", text="")
        split = row.split(factor=0.35)
        split.label(text=lib.name or "(Unnamed)")
        split.label(text=lib.path or "")
        if lib.path:
            btn = row.operator("wm.path_open", text="", icon='FILE_FOLDER')
            btn.filepath = lib.path


class ASSETMANAGER_OT_refresh_libraries(bpy.types.Operator):
    bl_idname = "asset_manager.refresh_libraries"
    bl_label = "Refresh Asset Libraries"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context: bpy.types.Context):
        wm = context.window_manager
        if hasattr(wm, "am_libraries"):
            wm.am_libraries.clear()
            for lib_name, lib_path in list_asset_library_paths():
                item = wm.am_libraries.add()
                item.name = lib_name
                item.path = lib_path
                item.selected = False
        return {'FINISHED'}


class ASSETMANAGER_OT_cancel(bpy.types.Operator):
    bl_idname = "asset_manager.cancel"
    bl_label = "Cancel Processing"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context: bpy.types.Context):
        AM_CANCEL_EVENT.set()
        return {'FINISHED'}


def normalize_posix_path(path: str) -> str:
    return pathlib.Path(path).as_posix()


def stable_uuid_for_catalog(root: str, rel_catalog_path: str) -> str:
    namespace = uuid.uuid5(uuid.NAMESPACE_URL, "blender-asset-catalogs")
    return str(uuid.uuid5(namespace, f"root={os.path.abspath(root)}|catalog={rel_catalog_path}"))


def list_asset_library_paths() -> list[tuple[str, str]]:
    libraries = []
    prefs = bpy.context.preferences
    if not prefs:
        return libraries
    filepaths = prefs.filepaths
    if not hasattr(filepaths, "asset_libraries"):
        return libraries
    for lib in filepaths.asset_libraries:
        try:
            lib_path = bpy.path.abspath(lib.path)
        except Exception:
            lib_path = lib.path
        if lib_path and os.path.isdir(lib_path):
            libraries.append((lib.name, os.path.abspath(lib_path)))
    return libraries


def build_catalog_mapping_for_library(library_root: str) -> dict[str, tuple[str, str, str]]:
    # Format: {rel_path: (uuid, catalog_name, parent_path)}
    mapping: dict[str, tuple[str, str, str]] = {}
    root_path = pathlib.Path(library_root)
    
    # First pass: collect ALL directories (including empty ones) to ensure hierarchy
    all_dirs = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        rel = pathlib.Path(dirpath).relative_to(root_path)
        if str(rel) == "." or str(rel) == "":
            continue
        parts = list(rel.parts)
        if any(p.startswith(".") for p in parts):
            continue
        
        # Include ALL directories to ensure complete hierarchy
        all_dirs.append((dirpath, rel))
    
    # Second pass: create catalogs for all directories
    for dirpath, rel in all_dirs:
        parts = list(rel.parts)
        rel_posix = normalize_posix_path(str(rel))
        simple_name = parts[-1]
        catalog_uuid = stable_uuid_for_catalog(library_root, rel_posix)
        
        # Create catalog name based on hierarchy level
        if len(parts) == 1:
            # Main catalog - simple name
            catalog_name = simple_name
        else:
            # Sub-catalog - use full path to show hierarchy
            catalog_name = rel_posix
        
        mapping[rel_posix] = (catalog_uuid, catalog_name, "")
    
    return mapping


def write_catalog_file(library_root: str, mapping: dict[str, tuple[str, str, str]]) -> str:
    cats_path = os.path.join(library_root, "blender_assets.cats.txt")
    if os.path.exists(cats_path):
        backup_path = cats_path + ".BAKUP"
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
        except Exception:
            pass
        shutil.move(cats_path, backup_path)

    lines = []
    lines.append("# This is an Asset Catalog Definition file for Blender.")
    lines.append("#")
    lines.append("# Empty lines and lines starting with # will be ignored.")
    lines.append("# The first non-ignored line should be the version indicator.")
    lines.append("# Other lines are of the format \"UUID:catalog/path/for/assets:simple catalog name\"")
    lines.append("")
    lines.append("VERSION 1")
    lines.append("")

    # Sort paths to ensure proper hierarchy display:
    # 1. Main catalogs (depth 1) first
    # 2. Sub-catalogs (depth > 1) in order
    # 3. Within each depth, sort alphabetically
    def sort_key(path):
        parts = path.split('/')
        return (len(parts), path.lower())
    
    sorted_paths = sorted(mapping.keys(), key=sort_key)
    
    for rel_path in sorted_paths:
        cat_uuid, catalog_name, parent_path = mapping[rel_path]
        # The catalog_name now contains the full path for sub-catalogs
        # This will create hierarchical structure in Blender
        lines.append(f"{cat_uuid}:{catalog_name}:{catalog_name}")

    with open(cats_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return cats_path


def create_temp_blender_script() -> str:
    script = r"""
import bpy
import sys
import os
import json

def assign_catalog_to_selected_types(catalog_uuid: str, catalog_name: str, apply_objects: bool, apply_materials: bool, apply_collections: bool, catalog_mapping: dict = None) -> int:
    changed = 0
    
    # Process Objects
    if apply_objects:
        seen_mesh_data = set()
        for obj in list(bpy.data.objects):
            try:
                if obj.type != 'MESH':
                    continue  # تجاهل أي نوع غير Mesh

                mesh_name = obj.data.name  # التحقق من اسم الـ Mesh Data
                if mesh_name in seen_mesh_data:
                    continue  # تجاهل المجسمات التي تستخدم نفس الـ Mesh Data
                seen_mesh_data.add(mesh_name)

                # Skip if already an asset
                if obj.asset_data is not None:
                    # Just update catalog if different
                    if obj.asset_data.catalog_id != catalog_uuid:
                        obj.asset_data.catalog_id = catalog_uuid
                        changed += 1
                    continue
                    
                # Make asset and assign catalog
                mark = getattr(obj, "asset_mark", None)
                if callable(mark):
                    mark()
                else:
                    bpy.ops.asset.mark()
                
                # توليد البريفيو
                if hasattr(obj, "asset_generate_preview"):
                    obj.asset_generate_preview()
                    time.sleep(0.05)


                if obj.asset_data:
                    obj.asset_data.catalog_id = catalog_uuid
                    changed += 1
                
                
            except Exception as e:
                print(f"Error processing object {obj.name}: {e}")
    
    # Process Materials
    if apply_materials:
        for mat in list(bpy.data.materials):
            try:
                # Skip if already an asset
                if mat.asset_data is not None:
                    # Just update catalog if different
                    if mat.asset_data.catalog_id != catalog_uuid:
                        mat.asset_data.catalog_id = catalog_uuid
                        changed += 1
                    continue
                    
                # Make asset and assign catalog
                mark = getattr(mat, "asset_mark", None)
                if callable(mark):
                    mark()
                else:
                    bpy.ops.asset.mark()
                
                # توليد البريفيو
                if hasattr(mat, "asset_generate_preview"):
                    mat.asset_generate_preview()
                    #time.sleep(0.05)
                    
                if mat.asset_data:
                    mat.asset_data.catalog_id = catalog_uuid
                    changed += 1
            except Exception as e:
                print(f"Error processing material {mat.name}: {e}")
    
    # Process Collections
    if apply_collections:
        for col in list(bpy.data.collections):
            try:
                # Skip if already an asset
                if col.asset_data is not None:
                    # Just update catalog if different
                    if col.asset_data.catalog_id != catalog_uuid:
                        col.asset_data.catalog_id = catalog_uuid
                        changed += 1
                    continue
                    
                # Make asset and assign catalog
                mark = getattr(col, "asset_mark", None)
                if callable(mark):
                    mark()
                else:
                    bpy.ops.asset.mark()
                
                # توليد البريفيو
                if hasattr(col, "asset_generate_preview"):
                    col.asset_generate_preview()
                    time.sleep(0.05)
                    
                if col.asset_data:
                    col.asset_data.catalog_id = catalog_uuid
                    changed += 1
            except Exception as e:
                print(f"Error processing collection {col.name}: {e}")
    
    return changed

def main():
    argv = sys.argv
    if "--" not in argv:
        return
    idx = argv.index("--")
    args = argv[idx+1:]
    if len(args) < 6:
        return
    blend_file = args[0]
    catalog_uuid = args[1]
    catalog_name = args[2]
    apply_objects = args[3].lower() == 'true'
    apply_materials = args[4].lower() == 'true'
    apply_collections = args[5].lower() == 'true'
    
    bpy.ops.wm.open_mainfile(filepath=blend_file)
    changed = assign_catalog_to_selected_types(catalog_uuid, catalog_name, apply_objects, apply_materials, apply_collections)
    bpy.ops.wm.save_mainfile()
    print(f"Assigned catalog {catalog_uuid} ({catalog_name}) to {changed} assets in {blend_file}")

if __name__ == "__main__":
    main()
"""
    fd, path = tempfile.mkstemp(prefix="am_blend_apply_", suffix=".py")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(script)
    return path


def assign_catalog_to_blend_in_subprocess(blender_binary: str, blend_file: str, catalog_uuid: str, catalog_name: str, apply_objects: bool = True, apply_materials: bool = True, apply_collections: bool = True) -> tuple[bool, str]:
    script_path = create_temp_blender_script()
    try:
        cmd = [
            blender_binary,
            "-b",
            "--factory-startup",
            "-noaudio",
            "--python", script_path,
            "--",
            blend_file,
            catalog_uuid,
            catalog_name,
            str(apply_objects).lower(),
            str(apply_materials).lower(),
            str(apply_collections).lower(),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        ok = proc.returncode == 0
        output = (proc.stdout or "") + (proc.stderr or "")
        return ok, output
    finally:
        try:
            os.remove(script_path)
        except Exception:
            pass


class ASSETMANAGER_OT_build_catalogs(bpy.types.Operator):
    bl_idname = "asset_manager.build_catalogs"
    bl_label = "Asset Manager: Build Catalogs and Assign"
    bl_options = {"REGISTER", "INTERNAL"}

    run_in_subprocess: bpy.props.BoolProperty(
        name="Run in Background",
        description="Open each .blend in a separate background Blender to avoid changing current file",
        default=True,
    )
    
    apply_to_objects: bpy.props.BoolProperty(
        name="Apply to Objects",
        description="Apply catalog assignment to objects (skip objects that are already assets)",
        default=True,
    )
    
    apply_to_materials: bpy.props.BoolProperty(
        name="Apply to Materials",
        description="Apply catalog assignment to materials (skip materials that are already assets)",
        default=True,
    )
    
    apply_to_collections: bpy.props.BoolProperty(
        name="Apply to Collections",
        description="Apply catalog assignment to collections (skip collections that are already assets)",
        default=True,
    )

    # Async state
    _thread = None
    _timer = None
    _errors = None
    _total_tasks = 0
    _completed_tasks = 0
    _current_file = ""

    def _worker(self, selected_roots: list[str], blender_binary: str, use_subprocess: bool):
        errors: list[str] = []
        total = 0
        # pre-scan
        try:
            for lib_root in selected_roots:
                mapping = build_catalog_mapping_for_library(lib_root)
                write_catalog_file(lib_root, mapping)
                for rel_path, (_cuid, _name, _parent) in mapping.items():
                    abs_dir = os.path.join(lib_root, rel_path.replace('/', os.sep))
                    try:
                        entries = os.listdir(abs_dir)
                    except Exception:
                        continue
                    for entry in entries:
                        if entry.lower().endswith('.blend'):
                            total += 1
        except Exception as ex:
            errors.append(f"Pre-scan failed: {ex}")
        self._total_tasks = max(total, 1)

        # process
        for lib_root in selected_roots:
            if AM_CANCEL_EVENT.is_set():
                break
            mapping = build_catalog_mapping_for_library(lib_root)
            try:
                write_catalog_file(lib_root, mapping)
            except Exception as ex:
                errors.append(f"Write catalog failed for {lib_root}: {ex}")
            for rel_path, (cat_uuid, simple_name, parent_path) in mapping.items():
                if AM_CANCEL_EVENT.is_set():
                    break
                abs_dir = os.path.join(lib_root, rel_path.replace('/', os.sep))
                try:
                    entries = os.listdir(abs_dir)
                except Exception:
                    continue
                for entry in entries:
                    if AM_CANCEL_EVENT.is_set():
                        break
                    if not entry.lower().endswith('.blend'):
                        continue
                    blend_path = os.path.join(abs_dir, entry)
                    self._current_file = blend_path
                    # Always prefer subprocess to avoid touching bpy from worker thread
                    ok, out = assign_catalog_to_blend_in_subprocess(
                        blender_binary, 
                        blend_path, 
                        cat_uuid, 
                        simple_name,
                        self.apply_to_objects,
                        self.apply_to_materials,
                        self.apply_to_collections
                    )
                    if not ok:
                        errors.append(f"Failed assigning catalog to {blend_path}: {out[-500:]}")
                    self._completed_tasks += 1
        self._errors = errors

    def invoke(self, context: bpy.types.Context, event):
        wm = context.window_manager
        # collect selected libraries
        selected_roots: list[str] = []
        if hasattr(wm, "am_libraries") and len(wm.am_libraries) > 0:
            for item in wm.am_libraries:
                if item.selected:
                    selected_roots.append(item.path)
        else:
            selected_roots = [p for _n, p in list_asset_library_paths()]
        if not selected_roots:
            self.report({'WARNING'}, "No Asset Libraries selected. Use Refresh and select at least one.")
            return {'CANCELLED'}

        AM_CANCEL_EVENT.clear()
        wm.am_is_running = True
        wm.am_progress_text = "Starting..."
        self._errors = []
        self._total_tasks = 1
        self._completed_tasks = 0
        self._current_file = ""

        blender_binary = bpy.app.binary_path
        self._thread = threading.Thread(target=self._worker, args=(selected_roots, blender_binary, self.run_in_subprocess), daemon=True)
        self._thread.start()

        wm.progress_begin(0, 1)
        self._timer = wm.event_timer_add(0.2, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context: bpy.types.Context, event):
        wm = context.window_manager
        if event.type == 'TIMER':
            total = max(self._total_tasks, 1)
            comp = min(self._completed_tasks, total)
            fraction = 0.0
            try:
                fraction = comp / float(total)
            except Exception:
                fraction = 0.0
            wm.progress_update(fraction)
            if self._current_file:
                wm.am_progress_text = f"Processing: {os.path.basename(self._current_file)} ({comp}/{total})"
            else:
                wm.am_progress_text = f"Scanning... ({comp}/{total})"

            if self._thread and not self._thread.is_alive():
                wm.progress_end()
                wm.am_is_running = False
                if self._timer:
                    wm.event_timer_remove(self._timer)
                    self._timer = None
                if self._errors:
                    wm.am_progress_text = f"Completed with errors: {len(self._errors)}"
                    self.report({'ERROR'}, f"Completed with errors: {len(self._errors)}. See console.")
                    for e in self._errors[:10]:
                        print(e)
                else:
                    wm.am_progress_text = "Completed successfully"
                    self.report({'INFO'}, "Asset catalogs created and assigned successfully.")
                return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        AM_CANCEL_EVENT.set()


class ASSETMANAGER_OT_create_catalog(bpy.types.Operator):
    bl_idname = "asset_manager.create_catalog"
    bl_label = "Create Catalog and Folders"
    bl_options = {"REGISTER", "INTERNAL"}

    catalog_name: bpy.props.StringProperty(
        name="Catalog Name",
        description="Name of the catalog to create",
        default=""
    )
    
    catalog_type: bpy.props.EnumProperty(
        name="Catalog Type",
        description="Type of catalog to create",
        items=[
            ('MAIN', "Main Catalog", "Create a main catalog"),
            ('SUB', "Sub Catalog", "Create a sub catalog"),
            ('BOTH', "Both", "Create both main and sub catalogs")
        ],
        default='MAIN'
    )
    
    parent_catalog: bpy.props.StringProperty(
        name="Parent Catalog",
        description="Parent catalog for sub catalogs",
        default=""
    )
    
    parent_catalog_items: bpy.props.CollectionProperty(
        type=ASSETMANAGER_CatalogItem
    )

    def invoke(self, context, event):
        wm = context.window_manager
        # Get selected library path
        selected_roots = []
        if hasattr(wm, "am_libraries") and len(wm.am_libraries) > 0:
            for item in wm.am_libraries:
                if item.selected:
                    selected_roots.append(item.path)
        
        if not selected_roots:
            self.report({'WARNING'}, "No Asset Libraries selected. Use Refresh and select at least one.")
            return {'CANCELLED'}
        
        # Use first selected library
        self.library_path = selected_roots[0]
        
        # Update parent catalog items
        self._update_parent_catalog_items()
        
        return context.window_manager.invoke_props_dialog(self, width=400)

    def _update_parent_catalog_items(self):
        """Update parent catalog items list from the library"""
        # Clear existing items
        self.parent_catalog_items.clear()
        
        try:
            # Read existing catalog file
            catalog_file_path = os.path.join(self.library_path, "blender_assets.cats.txt")
            if os.path.exists(catalog_file_path):
                with open(catalog_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Parse catalog entries
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            catalog_path = parts[1]
                            
                            # Create display name based on path structure
                            if '/' in catalog_path:
                                # Sub catalog: show as "parent-child"
                                path_parts = catalog_path.split('/')
                                parent_name = path_parts[0]
                                child_name = path_parts[-1]
                                display_name = f"{parent_name}-{child_name}"
                            else:
                                # Main catalog: show as is
                                display_name = catalog_path
                            
                            # Add to collection
                            item = self.parent_catalog_items.add()
                            item.name = display_name
                            item.path = catalog_path
            
            # If no catalogs found, add a default option
            if not self.parent_catalog_items:
                item = self.parent_catalog_items.add()
                item.name = "No catalogs available"
                item.path = ""
                
        except Exception as e:
            # If error reading catalogs, add error option
            item = self.parent_catalog_items.add()
            item.name = f"Error: {str(e)}"
            item.path = ""

    def draw(self, context):
        layout = self.layout
        
        # Catalog Name
        layout.prop(self, "catalog_name")
        
        # Catalog Type
        layout.prop(self, "catalog_type")
        
        # Parent Catalog - only show when type is SUB
        if self.catalog_type == 'SUB':
            # Update parent catalog items if empty
            if not self.parent_catalog_items:
                self._update_parent_catalog_items()
            
            # Create a row for parent catalog selection
            row = layout.row()
            row.label(text="Parent Catalog:")
            
            # Create a dropdown-like interface
            if self.parent_catalog_items:
                # Find the current selection index
                current_index = 0
                for i, item in enumerate(self.parent_catalog_items):
                    if item.path == self.parent_catalog:
                        current_index = i
                        break
                
                # Create a menu-like interface
                row = layout.row()
                row.prop_search(self, "parent_catalog", self, "parent_catalog_items", text="", icon='FOLDER_REDIRECT')
            else:
                row.label(text="No catalogs available")

    def execute(self, context):
        if not self.catalog_name.strip():
            self.report({'ERROR'}, "Catalog name cannot be empty")
            return {'CANCELLED'}
        
        try:
            if self.catalog_type == 'MAIN':
                self._create_main_catalog()
            elif self.catalog_type == 'SUB':
                self._create_sub_catalog()
            elif self.catalog_type == 'BOTH':
                self._create_main_catalog()
                self._create_sub_catalog()
            
            self.report({'INFO'}, f"Catalog '{self.catalog_name}' created successfully")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create catalog: {str(e)}")
            return {'CANCELLED'}

    def _create_main_catalog(self):
        """Create main catalog and folder"""
        catalog_path = os.path.join(self.library_path, self.catalog_name)
        
        # Create folder
        if not os.path.exists(catalog_path):
            os.makedirs(catalog_path)
        
        # Create catalog file if it doesn't exist
        catalog_file_path = os.path.join(self.library_path, "blender_assets.cats.txt")
        if not os.path.exists(catalog_file_path):
            self._create_catalog_file(catalog_file_path)
        
        # Add catalog entry
        self._add_catalog_entry(catalog_file_path, self.catalog_name, "")

    def _create_sub_catalog(self):
        """Create sub catalog and folder"""
        if not self.parent_catalog or self.parent_catalog == "":
            self.report({'ERROR'}, "Parent catalog is required for sub catalogs")
            return
        
        # Find the actual catalog path from the selected display name
        parent_catalog_path = ""
        for item in self.parent_catalog_items:
            if item.name == self.parent_catalog:
                parent_catalog_path = item.path
                break
        
        if not parent_catalog_path:
            self.report({'ERROR'}, f"Could not find path for parent catalog '{self.parent_catalog}'")
            return
        
        parent_path = os.path.join(self.library_path, parent_catalog_path)
        if not os.path.exists(parent_path):
            self.report({'ERROR'}, f"Parent catalog path '{parent_path}' does not exist")
            return
        
        sub_catalog_path = os.path.join(parent_path, self.catalog_name)
        
        # Create sub folder
        if not os.path.exists(sub_catalog_path):
            os.makedirs(sub_catalog_path)
        
        # Create or update catalog file
        catalog_file_path = os.path.join(self.library_path, "blender_assets.cats.txt")
        if not os.path.exists(catalog_file_path):
            self._create_catalog_file(catalog_file_path)
        
        # Add sub catalog entry
        self._add_catalog_entry(catalog_file_path, self.catalog_name, parent_catalog_path)

    def _create_catalog_file(self, catalog_file_path):
        """Create new catalog file with header"""
        header = """# This is an Asset Catalog Definition file for Blender.
#
# Empty lines and lines starting with # will be ignored.
# The first non-ignored line should be the version indicator.
# Other lines are of the format "UUID:catalog/path/for/assets:simple catalog name"

VERSION 1

"""
        with open(catalog_file_path, 'w', encoding='utf-8') as f:
            f.write(header)

    def _add_catalog_entry(self, catalog_file_path, catalog_name, parent_path):
        """Add catalog entry to the catalog file"""
        # Generate UUID for the catalog
        import uuid
        catalog_uuid = str(uuid.uuid4())
        
        # Create catalog entry in correct format: UUID:catalog/path:simple_name
        if parent_path:
            # Sub catalog: UUID:parent/catalog_name:simple_name
            entry = f"{catalog_uuid}:{parent_path}/{catalog_name}:{catalog_name}\n"
        else:
            # Main catalog: UUID:catalog_name:simple_name
            entry = f"{catalog_uuid}:{catalog_name}:{catalog_name}\n"
        
        # Append to catalog file
        with open(catalog_file_path, 'a', encoding='utf-8') as f:
            f.write(entry)


class ASSETMANAGER_OT_create_missing_folders(bpy.types.Operator):
    bl_idname = "asset_manager.create_missing_folders"
    bl_label = "Create Missing Folders"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        wm = context.window_manager
        # Collect selected libraries; if none selected, process all libraries
        selected_roots = []
        if hasattr(wm, "am_libraries") and len(wm.am_libraries) > 0:
            for item in wm.am_libraries:
                if item.selected:
                    selected_roots.append(item.path)
        if not selected_roots:
            selected_roots = [p for _n, p in list_asset_library_paths()]

        if not selected_roots:
            self.report({'WARNING'}, "No Asset Libraries available to process")
            return {'CANCELLED'}

        created_count = 0
        processed_catalogs = 0

        for lib_root in selected_roots:
            try:
                cats_path = os.path.join(lib_root, "blender_assets.cats.txt")
                if not os.path.exists(cats_path):
                    # No catalog file; skip this library
                    continue
                with open(cats_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f.readlines():
                        line = line.strip()
                        if not line or line.startswith('#') or line.startswith('VERSION'):
                            continue
                        parts = line.split(':')
                        if len(parts) < 2:
                            continue
                        catalog_path = parts[1].strip()
                        if not catalog_path:
                            continue
                        processed_catalogs += 1
                        rel_dir = catalog_path.replace("\\", "/").strip("/").replace('/', os.sep)
                        abs_dir = os.path.join(lib_root, rel_dir)
                        if not os.path.isdir(abs_dir):
                            try:
                                os.makedirs(abs_dir, exist_ok=True)
                                created_count += 1
                            except Exception:
                                pass
            except Exception as ex:
                # Continue with other libraries on error
                print(f"Create Missing Folders error for {lib_root}: {ex}")

        if created_count == 0:
            self.report({'INFO'}, "All folders already exist for current catalogs")
        else:
            self.report({'INFO'}, f"Created {created_count} missing folder(s)")
        return {'FINISHED'}


class kh_ASSET_PANEL(bpy.types.Panel):
    bl_label = "Asset Manager"
    bl_idname = "KH_ASSET_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KH-Tools"
    #bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id   = "OBJECT_PT_kh_asset_browser"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator("asset_manager.refresh_libraries", text="Refresh Libraries", icon='FILE_REFRESH')
        #row.prop(wm, "am_run_in_subprocess")

        col.template_list("ASSETMANAGER_UL_libraries", "", wm, "am_libraries", wm, "am_libraries_index", rows=5)

        if wm.am_is_running:
            col.operator("asset_manager.cancel", text="Cancel", icon='CANCEL')
            if wm.am_progress_text:
                col.label(text=wm.am_progress_text)
        else:
            # Asset Type Options
            # col.separator()
            # col.label(text="Apply to:", icon='ASSET_MANAGER')
            row = col.row(align=True)
            row.prop(wm, "am_apply_to_objects", text="Objects", toggle=True)
            row.prop(wm, "am_apply_to_materials", text="Materials", toggle=True)
            row.prop(wm, "am_apply_to_collections", text="Collections", toggle=True)
            
            col.separator()
            op = col.operator("asset_manager.build_catalogs", text="Make catalog & Assets", icon='ASSET_MANAGER')
            op.run_in_subprocess = wm.am_run_in_subprocess
            op.apply_to_objects = wm.am_apply_to_objects
            op.apply_to_materials = wm.am_apply_to_materials
            op.apply_to_collections = wm.am_apply_to_collections
            
            col.separator()
            col.label(text="Create New Catalogs:", icon='ADD')
            row = col.row(align=True)
            row.operator("asset_manager.create_catalog", text="Create Catalog", icon='FOLDER_REDIRECT')
            row.operator("asset_manager.create_missing_folders", text="Create Folders", icon='FILE_FOLDER')


classes = (
    ASSETMANAGER_LibraryItem,
    ASSETMANAGER_CatalogItem,
    ASSETMANAGER_UL_libraries,
    ASSETMANAGER_OT_refresh_libraries,
    ASSETMANAGER_OT_cancel,
    ASSETMANAGER_OT_build_catalogs,
    ASSETMANAGER_OT_create_catalog,
    ASSETMANAGER_OT_create_missing_folders,
    kh_ASSET_PANEL,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # UI/State properties
    bpy.types.WindowManager.am_run_in_subprocess = bpy.props.BoolProperty(
        name="Run in Background",
        description="Open each .blend in a separate background Blender to avoid changing current file",
        default=True,
    )
    bpy.types.WindowManager.am_libraries = bpy.props.CollectionProperty(type=ASSETMANAGER_LibraryItem)
    bpy.types.WindowManager.am_libraries_index = bpy.props.IntProperty(default=0)
    bpy.types.WindowManager.am_is_running = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.am_progress_text = bpy.props.StringProperty(default="")
    
    # Asset type options
    bpy.types.WindowManager.am_apply_to_objects = bpy.props.BoolProperty(
        name="Apply to Objects",
        description="Apply catalog assignment to objects (skip objects that are already assets)",
        default=False,
    )
    bpy.types.WindowManager.am_apply_to_materials = bpy.props.BoolProperty(
        name="Apply to Materials",
        description="Apply catalog assignment to materials (skip materials that are already assets)",
        default=False,
    )
    bpy.types.WindowManager.am_apply_to_collections = bpy.props.BoolProperty(
        name="Apply to Collections",
        description="Apply catalog assignment to collections (skip collections that are already assets)",
        default=False,
    )


def unregister():
    # Remove properties
    for prop in ("am_progress_text", "am_is_running", "am_libraries_index", "am_libraries", "am_run_in_subprocess", "am_apply_to_objects", "am_apply_to_materials", "am_apply_to_collections"):
        if hasattr(bpy.types.WindowManager, prop):
            try:
                delattr(bpy.types.WindowManager, prop)
            except Exception:
                pass

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass


if __name__ == "__main__":
    register()


