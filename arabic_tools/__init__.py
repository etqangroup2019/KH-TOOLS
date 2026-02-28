
import bpy
from bpy.app.handlers import persistent

bl_info = {
    "name": "Arabic Auto-Reshaper",
    "author": "Antigravity",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "Automated",
    "description": "Automatically reshapes Arabic names for all objects in the scene (standalone).",
    "category": "Interface",
}

# --- Embedded Arabic Reshaper Logic ---

def is_arabic(char):
    return 0x0600 <= ord(char) <= 0x06FF

# Mapping for Arabic Presentation Forms-B (U+FE70 - U+FEFF)
ARABIC_FORMS = {
    0x0621: [0xFE80, 0, 0, 0], # Hamza
    0x0622: [0xFE81, 0xFE82, 0, 0], # Alef with Madda
    0x0623: [0xFE83, 0xFE84, 0, 0], # Alef with Hamza Above
    0x0624: [0xFE85, 0xFE86, 0, 0], # Waw with Hamza
    0x0625: [0xFE87, 0xFE88, 0, 0], # Alef with Hamza Below
    0x0626: [0xFE89, 0xFE8A, 0xFE8B, 0xFE8C], # Yeh with Hamza
    0x0627: [0xFE8D, 0xFE8E, 0, 0], # Alef
    0x0628: [0xFE8F, 0xFE90, 0xFE91, 0xFE92], # Beh
    0x0629: [0xFE93, 0xFE94, 0, 0], # Teh Marbuta
    0x062A: [0xFE95, 0xFE96, 0xFE97, 0xFE98], # Teh
    0x062B: [0xFE99, 0xFE9A, 0xFE9B, 0xFE9C], # Theh
    0x062C: [0xFE9D, 0xFE9E, 0xFE9F, 0xFEA0], # Jeem
    0x062D: [0xFEA1, 0xFEA2, 0xFEA3, 0xFEA4], # Hah
    0x062E: [0xFEA5, 0xFEA6, 0xFEA7, 0xFEA8], # Khah
    0x062F: [0xFEA9, 0xFEAA, 0, 0], # Dal
    0x0630: [0xFEAB, 0xFEAC, 0, 0], # Thal
    0x0631: [0xFEAD, 0xFEAE, 0, 0], # Reh
    0x0632: [0xFEAF, 0xFEB0, 0, 0], # Zain
    0x0633: [0xFEB1, 0xFEB2, 0xFEB3, 0xFEB4], # Seen
    0x0634: [0xFEB5, 0xFEB6, 0xFEB7, 0xFEB8], # Sheen
    0x0635: [0xFEB9, 0xFEBA, 0xFEBB, 0xFEBC], # Sad
    0x0636: [0xFEBD, 0xFEBE, 0xFEBF, 0xFEC0], # Dad
    0x0637: [0xFEC1, 0xFEC2, 0xFEC3, 0xFEC4], # Tah
    0x0638: [0xFEC5, 0xFEC6, 0xFEC7, 0xFEC8], # Zah
    0x0639: [0xFEC9, 0xFECA, 0xFECB, 0xFECC], # Ain
    0x063A: [0xFECD, 0xFECE, 0xFECF, 0xFED0], # Ghain
    0x0640: [0x0640, 0x0640, 0x0640, 0x0640], # Tatweel
    0x0641: [0xFED1, 0xFED2, 0xFED3, 0xFED4], # Feh
    0x0642: [0xFED5, 0xFED6, 0xFED7, 0xFED8], # Qaf
    0x0643: [0xFED9, 0xFEDA, 0xFEDB, 0xFEDC], # Kaf
    0x0644: [0xFEDD, 0xFEDE, 0xFEDF, 0xFEE0], # Lam
    0x0645: [0xFEE1, 0xFEE2, 0xFEE3, 0xFEE4], # Meem
    0x0646: [0xFEE5, 0xFEE6, 0xFEE7, 0xFEE8], # Noon
    0x0647: [0xFEE9, 0xFEEA, 0xFEEB, 0xFEEC], # Heh
    0x0648: [0xFEED, 0xFEEE, 0, 0], # Waw
    0x0649: [0xFEEF, 0xFEF0, 0xFBE8, 0xFBE9], # Alef Maksura
    0x064A: [0xFEF1, 0xFEF2, 0xFEF3, 0xFEF4], # Yeh
    0x067E: [0xFB56, 0xFB57, 0xFB58, 0xFB59], # Peh
    0x0686: [0xFB7A, 0xFB7B, 0xFB7C, 0xFB7D], # Tcheh
    0x0698: [0xFB8A, 0xFB8B, 0, 0], # Jeh
    0x06AF: [0xFB92, 0xFB93, 0xFB94, 0xFB95], # Gaf
    0x06CC: [0xFBFC, 0xFBFD, 0xFBFE, 0xFBFF], # Farsi Yeh
}

LAM_ALIF_MAP = {
    0x0622: [0xFEF5, 0xFEF6],
    0x0623: [0xFEF7, 0xFEF8],
    0x0625: [0xFEF9, 0xFEFA],
    0x0627: [0xFEFB, 0xFEFC],
}

NON_CONNECTORS = {0x0621, 0x0622, 0x0623, 0x0624, 0x0625, 0x0627, 0x062F, 0x0630, 0x0631, 0x0632, 0x0648, 0x0649, 0x0698}

def reshape(text):
    if not text: return text
    if not any(is_arabic(c) for c in text): return text

    processed = []
    i = 0
    while i < len(text):
        c = text[i]
        code = ord(c)
        if code == 0x0644 and i + 1 < len(text):
            next_code = ord(text[i+1])
            if next_code in LAM_ALIF_MAP:
                processed.append({'char': 'LAM_ALIF', 'code': next_code})
                i += 2
                continue
        processed.append({'char': c, 'code': code})
        i += 1
    
    output = []
    for idx, item in enumerate(processed):
        if item['char'] == 'LAM_ALIF':
            prev_connects = False
            if idx > 0:
                prev = processed[idx-1]
                if is_arabic(prev['char']) and prev['char'] != 'LAM_ALIF':
                    if prev['code'] not in NON_CONNECTORS:
                        prev_connects = True
            forms = LAM_ALIF_MAP[item['code']]
            output.append(chr(forms[1] if prev_connects else forms[0]))
            continue

        c = item['char']
        code = item['code']
        if not is_arabic(c):
            output.append(c)
            continue
            
        prev_connects = False
        next_connects = False
        
        if idx > 0:
            prev = processed[idx-1]
            if prev['char'] != 'LAM_ALIF' and is_arabic(prev['char']):
                if prev['code'] not in NON_CONNECTORS:
                    prev_connects = True

        if idx < len(processed) - 1:
            next_c = processed[idx+1]
            if next_c['char'] == 'LAM_ALIF':
                next_connects = True
            elif is_arabic(next_c['char']):
                if code not in NON_CONNECTORS:
                    next_connects = True

        form_idx = 0
        if prev_connects and next_connects:
            form_idx = 3 # Medial
        elif prev_connects:
            form_idx = 1 # Final
        elif next_connects:
            form_idx = 2 # Initial
        else:
            form_idx = 0 # Isolated

        if code in ARABIC_FORMS:
            forms = ARABIC_FORMS[code]
            output.append(chr(forms[form_idx] if form_idx < len(forms) and forms[form_idx] != 0 else forms[0]))
        else:
            output.append(c)

    # Simplified BiDi: Full Reversal
    # This ensures correct word order for RTL languages in LTR renderers.
    # Logic: "Word1 Word2" -> "2droW 1droW"
    # Rendered LTR: "Visual: 2droW ... 1droW"
    # RTL Reader reads from Right: "1droW" (Word1) -> "2droW" (Word2).
    
    return "".join(output)[::-1]

# --- Addon Logic ---

def is_reshaped(text):
    for c in text:
        if 0x0600 <= ord(c) <= 0x06FF:
            return False
    return True

def _reshape_data_block(data_block):
    """Reshape the name of a single data block. Returns True if changed."""
    if data_block is None:
        return False
    if not is_reshaped(data_block.name):
        try:
            new_name = reshape(data_block.name)
            if new_name != data_block.name:
                data_block.name = new_name
                return True
        except:
            pass
    return False

def _reshape_collection(collection_attr):
    """Reshape all names in a bpy.data collection. Returns count of changed items."""
    count = 0
    try:
        for item in collection_attr:
            if _reshape_data_block(item):
                count += 1
    except:
        pass
    return count

@persistent
def auto_reshape_handler(scene):
    # Safe guard
    if not bpy.data: return
    
    # All data collections to reshape
    data_collections = [
        bpy.data.objects,        # Objects
        bpy.data.meshes,         # Mesh data
        bpy.data.collections,    # Collections
        bpy.data.materials,      # Materials
        bpy.data.cameras,        # Cameras
        bpy.data.lights,         # Lights
        bpy.data.curves,         # Curves
        bpy.data.armatures,      # Armatures
        bpy.data.lattices,       # Lattices
        bpy.data.speakers,       # Speakers
        bpy.data.images,         # Images
        bpy.data.textures,       # Textures
        bpy.data.node_groups,    # Node Groups
        bpy.data.worlds,         # Worlds
        bpy.data.scenes,         # Scenes
        bpy.data.texts,          # Texts
    ]
    
    # Grease Pencil (available in Blender 3.0+)
    if hasattr(bpy.data, 'grease_pencils'):
        data_collections.append(bpy.data.grease_pencils)
    
    # Grease Pencil v3 (available in Blender 4.0+)
    if hasattr(bpy.data, 'grease_pencils_v3'):
        data_collections.append(bpy.data.grease_pencils_v3)
    
    for collection in data_collections:
        _reshape_collection(collection)

class ARABIC_OT_fix_all(bpy.types.Operator):
    """Fix All Arabic Names Now"""
    bl_idname = "arabic.fix_all"
    bl_label = "Fix All Arabic Names"
    
    def execute(self, context):
        total = 0
        
        data_collections = [
            ("Objects", bpy.data.objects),
            ("Meshes", bpy.data.meshes),
            ("Collections", bpy.data.collections),
            ("Materials", bpy.data.materials),
            ("Cameras", bpy.data.cameras),
            ("Lights", bpy.data.lights),
            ("Curves", bpy.data.curves),
            ("Armatures", bpy.data.armatures),
            ("Lattices", bpy.data.lattices),
            ("Speakers", bpy.data.speakers),
            ("Images", bpy.data.images),
            ("Textures", bpy.data.textures),
            ("Node Groups", bpy.data.node_groups),
            ("Worlds", bpy.data.worlds),
            ("Scenes", bpy.data.scenes),
            ("Texts", bpy.data.texts),
        ]
        
        if hasattr(bpy.data, 'grease_pencils'):
            data_collections.append(("Grease Pencils", bpy.data.grease_pencils))
        
        if hasattr(bpy.data, 'grease_pencils_v3'):
            data_collections.append(("Grease Pencils v3", bpy.data.grease_pencils_v3))
        
        for name, collection in data_collections:
            total += _reshape_collection(collection)
        
        self.report({'INFO'}, f"Arabic Reshaper: Fixed {total} names")
        return {'FINISHED'}

class ARABIC_PT_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Arabic Tools"
    bl_idname = "ARABIC_PT_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Arabic"

    def draw(self, context):
        layout = self.layout
        layout.operator("arabic.fix_all", icon='FILE_REFRESH')
        layout.label(text="Auto-fix is Active")

def register():
    bpy.utils.register_class(ARABIC_OT_fix_all)
    #bpy.utils.register_class(ARABIC_PT_panel)
    
    if auto_reshape_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(auto_reshape_handler)

def unregister():
    bpy.utils.unregister_class(ARABIC_OT_fix_all)
    #bpy.utils.unregister_class(ARABIC_PT_panel)
    
    if auto_reshape_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(auto_reshape_handler)

if __name__ == "__main__":
    register()
