bl_info = {
    "name": "Face Selector & Separator",
    "author": "Your Name",
    "version": (1, 3),
    "blender": (2, 80, 0),
    "location": "3D Viewport",
    "description": "Select face under mouse cursor, select linked faces, separate, set origin to geometry and exit to object mode with F key",
    "warning": "",
    "doc_url": "",
    "category": "Mesh",
}

import bpy
import bmesh
from bpy_extras import view3d_utils
from mathutils import Vector
import gpu
from gpu_extras.batch import batch_for_shader

class MESH_OT_select_face_under_mouse(bpy.types.Operator):
    """Select face under mouse cursor, select linked, separate, set origin to geometry and exit to object mode"""
    bl_idname = "mesh.select_face_under_mouse"
    bl_label = "Select Face Under Mouse and Separate"
    bl_options = {'REGISTER', 'UNDO'}
    
    def modal(self, context, event):
        if event.type == 'F' and event.value == 'PRESS':
            # Get the active object
            obj = context.active_object
            
            # Check if object exists and is a mesh
            if obj is None or obj.type != 'MESH':
                self.report({'WARNING'}, "Please select a mesh object")
                return {'CANCELLED'}
            
            # Get mouse coordinates
            mouse_x = event.mouse_region_x
            mouse_y = event.mouse_region_y
            
            # Switch to edit mode if not already
            if obj.mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
            
            # Ensure we're in face select mode
            bpy.ops.mesh.select_mode(type='FACE')
            
            # Deselect all faces first
            bpy.ops.mesh.select_all(action='DESELECT')
            
            # Get the region and region_3d
            region = context.region
            region_3d = context.space_data.region_3d
            
            # Convert mouse coordinates to 3D ray
            view_vector = view3d_utils.region_2d_to_vector_3d(region, region_3d, (mouse_x, mouse_y))
            ray_origin = view3d_utils.region_2d_to_origin_3d(region, region_3d, (mouse_x, mouse_y))
            
            # Get bmesh representation
            bm = bmesh.from_edit_mesh(obj.data)
            bm.faces.ensure_lookup_table()
            
            # Transform ray to object space
            ray_origin_local = obj.matrix_world.inverted() @ ray_origin
            view_vector_local = obj.matrix_world.inverted().to_3x3() @ view_vector
            
            # Find the closest face
            closest_face = None
            closest_face_index = -1
            closest_distance = float('inf')
            
            for face in bm.faces:
                # Calculate intersection with face
                result = self.ray_cast_face(ray_origin_local, view_vector_local, face)
                if result:
                    distance = (result - ray_origin_local).length
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_face = face
                        closest_face_index = face.index
            
            # Select the closest face if found
            if closest_face:
                closest_face.select = True
                # Update the mesh immediately
                bmesh.update_edit_mesh(obj.data)
                
                # Select all linked faces
                bpy.ops.mesh.select_linked()
                
                # Get updated bmesh to check selected faces
                bm_updated = bmesh.from_edit_mesh(obj.data)
                selected_faces = [f for f in bm_updated.faces if f.select]
                selected_count = len(selected_faces)
                
                if selected_faces:
                    # Store the original object name for reference
                    original_obj_name = obj.name
                    
                    # Separate the selected faces into a new object
                    bpy.ops.mesh.separate(type='SELECTED')
                    
                    # Exit to object mode
                    bpy.ops.object.mode_set(mode='OBJECT')
                    
                    # Get all selected objects (this will include the new separated object)
                    selected_objects = [o for o in context.selected_objects if o.type == 'MESH']
                    
                    # Set origin to geometry for all selected objects
                    for selected_obj in selected_objects:
                        # Make sure the object is selected and active
                        bpy.context.view_layer.objects.active = selected_obj
                        selected_obj.select_set(True)
                        
                        # Set origin to geometry
                        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                    
                    # Report success
                    if len(selected_objects) > 1:
                        self.report({'INFO'}, f"Selected face {closest_face_index} and {selected_count} linked faces, separated into new object and set origin to geometry for {len(selected_objects)} objects")
                    else:
                        self.report({'INFO'}, f"Selected face {closest_face_index} and {selected_count} linked faces, separated into new object and set origin to geometry")
                else:
                    self.report({'WARNING'}, "No faces were selected for separation")
            else:
                self.report({'WARNING'}, "No face found under mouse cursor")
            
            return {'FINISHED'}
        
        elif event.type in {'ESC'}:
            return {'CANCELLED'}
        
        return {'PASS_THROUGH'}
    
    def ray_cast_face(self, ray_origin, ray_direction, face):
        """Cast a ray against a face and return intersection point"""
        # Get face normal and center
        face_normal = face.normal
        face_center = face.calc_center_median()
        
        # Calculate intersection with face plane
        denom = face_normal.dot(ray_direction)
        if abs(denom) < 1e-6:  # Ray is parallel to face
            return None
        
        t = (face_center - ray_origin).dot(face_normal) / denom
        if t < 0:  # Intersection is behind ray origin
            return None
        
        intersection_point = ray_origin + t * ray_direction
        
        # Check if intersection point is inside the face
        if self.point_in_face(intersection_point, face):
            return intersection_point
        
        return None
    
    def point_in_face(self, point, face):
        """Check if a point is inside a face using barycentric coordinates"""
        # For triangular faces
        if len(face.verts) == 3:
            v0, v1, v2 = [v.co for v in face.verts]
            return self.point_in_triangle(point, v0, v1, v2)
        
        # For quad faces, split into two triangles
        elif len(face.verts) == 4:
            v0, v1, v2, v3 = [v.co for v in face.verts]
            return (self.point_in_triangle(point, v0, v1, v2) or 
                   self.point_in_triangle(point, v0, v2, v3))
        
        # For n-gons, use a more complex method
        else:
            # Project to 2D and use winding number
            return self.point_in_polygon(point, face)
    
    def point_in_triangle(self, point, v0, v1, v2):
        """Check if point is inside triangle using barycentric coordinates"""
        # Calculate vectors
        v0v1 = v1 - v0
        v0v2 = v2 - v0
        v0p = point - v0
        
        # Calculate dot products
        dot00 = v0v2.dot(v0v2)
        dot01 = v0v2.dot(v0v1)
        dot02 = v0v2.dot(v0p)
        dot11 = v0v1.dot(v0v1)
        dot12 = v0v1.dot(v0p)
        
        # Calculate barycentric coordinates
        inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * inv_denom
        v = (dot00 * dot12 - dot01 * dot02) * inv_denom
        
        # Check if point is in triangle
        return (u >= 0) and (v >= 0) and (u + v <= 1)
    
    def point_in_polygon(self, point, face):
        """Check if point is inside polygon face"""
        # Simple approach: check if point is on the same side of all edges
        face_normal = face.normal
        face_center = face.calc_center_median()
        
        # Project point onto face plane
        to_point = point - face_center
        projected_point = point - face_normal * to_point.dot(face_normal)
        
        # Check winding
        verts = [v.co for v in face.verts]
        n = len(verts)
        
        for i in range(n):
            v1 = verts[i]
            v2 = verts[(i + 1) % n]
            
            # Calculate cross product
            edge = v2 - v1
            to_projected = projected_point - v1
            cross = edge.cross(to_projected)
            
            # Check if on wrong side
            if cross.dot(face_normal) < 0:
                return False
        
        return True
    
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class MESH_OT_face_selector_toggle(bpy.types.Operator):
    """Toggle face selector mode"""
    bl_idname = "mesh.face_selector_toggle"
    bl_label = "Toggle Face Selector and Separator"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        # Start the modal operator
        bpy.ops.mesh.select_face_under_mouse('INVOKE_DEFAULT')
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MESH_OT_select_face_under_mouse)
    bpy.utils.register_class(MESH_OT_face_selector_toggle)
    
    # Add keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('mesh.face_selector_toggle', 'F', 'PRESS')

def unregister():
    bpy.utils.unregister_class(MESH_OT_select_face_under_mouse)
    bpy.utils.unregister_class(MESH_OT_face_selector_toggle)
    
    # Remove keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.get('3D View')
        if km:
            for kmi in km.keymap_items:
                if kmi.idname == 'mesh.face_selector_toggle':
                    km.keymap_items.remove(kmi)
                    break

if __name__ == "__main__":
    register()