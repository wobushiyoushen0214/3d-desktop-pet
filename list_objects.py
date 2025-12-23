import bpy
import os

BLEND_FILE = os.path.abspath("logo_model_v13.blend")
try:
    bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
    print("Objects in v13:")
    for obj in bpy.data.objects:
        print(f" - {obj.name}")
except Exception as e:
    print(e)
