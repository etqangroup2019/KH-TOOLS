import bpy
from .base_operator_class import kh_BaseBulkOperator
from .utilities import kh_id_type_to_type_name, kh_path_for_blender, kh_py_string_literal


class kh_OT_PreviewOperator(kh_BaseBulkOperator):
	"""Generate Previews for Selected Assets"""
	bl_idname = "asset.kh_bulk_preview_generate"
	bl_label = "Generate Previews"
	bl_options = {"REGISTER"}

	use_image_render: bpy.props.BoolProperty(
		name="Use Image Rendering (Objects)",
		description="Render a thumbnail image (object assets) and set it as a custom preview. Other types fall back to auto-generate.",
		default=False,
	)

	def invoke(self, context, event):
		return self.execute(context)

	def main(self, context):
		self.commands = {}

		for f in bpy.context.selected_assets:
			# Resolve which .blend to operate on
			if f.local_id is None:
				path_key = f.full_library_path
			else:
				current_path = bpy.data.filepath
				if current_path == "":
					continue
				path_key = current_path

			if path_key not in self.commands.keys():
				self.commands[path_key] = []

			id_type_plural = kh_id_type_to_type_name(f.id_type)
			asset_name = f.name

			if self.use_image_render and id_type_plural == 'objects':
				# Render an image for the object and load as custom preview
				cmd = (
					"import bpy, os, tempfile; "
					f"id_type='{kh_py_string_literal(id_type_plural)}'; "
					f"name='{kh_py_string_literal(asset_name)}'; "
					"db = getattr(bpy.data, id_type); obj = db.get(name); "
					"sc = bpy.context.scene; "
					"# Ensure camera\n"
					"cam = sc.camera\n"
					"if cam is None:\n    cd=bpy.data.cameras.new('KH_Prev_Camera'); cam=bpy.data.objects.new('KH_Prev_Camera', cd); sc.collection.objects.link(cam); sc.camera=cam\n"
					"# Ensure a sun light\n"
					"sun = bpy.data.lights.get('KH_Prev_Sun') or bpy.data.lights.new('KH_Prev_Sun','SUN'); "
					"sun_ob = bpy.data.objects.get('KH_Prev_Sun') or bpy.data.objects.new('KH_Prev_Sun', sun); "
					"('KH_Prev_Sun' not in [o.name for o in sc.objects]) and sc.collection.objects.link(sun_ob); "
					"# Link object into scene if needed\n"
					"obj and (obj.name not in [o.name for o in sc.objects]) and sc.collection.objects.link(obj); "
					"# Basic camera setup\n"
					"cam.location = (0.0, -3.0, 0.0); cam.rotation_euler = (1.570796, 0.0, 0.0); "
					"# Render settings with engine fallback\n"
					"eng_items = [e.identifier for e in sc.render.bl_rna.properties['engine'].enum_items]; "
					"engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in eng_items else ('BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in eng_items else 'CYCLES'); "
					"sc.render.engine = engine; sc.render.film_transparent = True; sc.render.resolution_x = 256; sc.render.resolution_y = 256; "
					"# Enforce PNG output\n"
					"sc.render.image_settings.file_format = 'PNG'; sc.render.use_file_extension = True; "
					"tmp = os.path.join(tempfile.gettempdir(), name); sc.render.filepath = tmp; "
					"obj and (getattr(obj,'asset_mark',None) and obj.asset_mark()); "
					"bpy.ops.render.render(write_still=True); "
					"# Load image as custom preview\n"
					"obj and (__import__('builtins').exec(\"\"\"\\nwith bpy.context.temp_override(id=obj):\\n    bpy.ops.ed.lib_id_load_custom_preview(filepath=tmp + '.png')\\n\"\"\")); "
				)
			else:
				# Fallback to automatic preview generation
				cmd = (
					"import bpy; "
					f"id_type='{kh_py_string_literal(id_type_plural)}'; "
					f"name='{kh_py_string_literal(asset_name)}'; "
					"db = getattr(bpy.data, id_type); obj = db.get(name); "
					"(obj and getattr(obj, 'asset_generate_preview', None)) and obj.asset_generate_preview(); "
				)

			self.commands[path_key].append(cmd)


def kh_MT_preview_menu_button(self, context):
	layout = self.layout
	row = layout.row(align=True)
	op = row.operator('asset.kh_bulk_preview_generate', text='Preview', icon='FILE_IMAGE')
	# Property will be shown in the dialog; keep default False


