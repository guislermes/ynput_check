"""
node_002_blender — bpy mind map (learn what Blender's Python API does)

Run inside Blender: Scripting workspace > Text Editor > Run Script
  or Blender Python Console. `bpy` is NOT available in a normal OS Python.

Docs: https://docs.blender.org/api/current/
Mental model:
  bpy.data   -> all data-blocks in the .blend (source of truth)
  bpy.context -> what the user/UI currently sees/selects (read-only view)
  bpy.ops    -> operators (buttons/menus/hotkeys as callable tools)
"""

# ---------------------------------------------------------------------------
# MIND MAP (API surface)
# ---------------------------------------------------------------------------
#
# bpy
# ├── data          # BlendData — scenes, objects, meshes, materials, ...
# │   ├── scenes / objects / meshes / materials / images / collections
# │   └── filepath  # current .blend path ("" if unsaved)
# ├── context       # Context — active/selected state (READ-ONLY attrs)
# │   ├── scene / view_layer / window / area
# │   ├── object / active_object
# │   └── selected_objects / selected_editable_objects
# ├── ops           # Operators — mesh.*, object.*, wm.*, render.*, ...
# └── types         # Class definitions (Object, Scene, Mesh, ...)
#
# Rule of thumb:
#   UI tools / selection-aware  -> context + ops
#   Automation / by name        -> data
#

# ---------------------------------------------------------------------------
# SNIPPETS — common use (paste into Blender)
# ---------------------------------------------------------------------------

def snippet_data_vs_context():
    import bpy

    # Data: address anything in the file by name/index
    scene = bpy.data.scenes["Scene"]
    cube = bpy.data.objects.get("Cube")

    # Context: whatever is active/selected right now
    active = bpy.context.active_object
    selected = list(bpy.context.selected_objects)
    current_scene = bpy.context.scene

    return scene, cube, active, selected, current_scene


def snippet_create_and_link_object():
    import bpy

    mesh = bpy.data.meshes.new("MyMesh")
    obj = bpy.data.objects.new("MyObject", mesh)

    # New objects exist in data but are invisible until linked to a collection
    bpy.context.collection.objects.link(obj)
    obj.location = (0.0, 0.0, 1.0)
    return obj


def snippet_operators():
    import bpy

    # Operators mirror UI actions (tooltip on buttons shows Python: bpy.ops...)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def snippet_temp_override():
    """Run an operator as if another object were active/selected."""
    import bpy

    obj = bpy.data.objects.get("Cube")
    if obj is None:
        return

    with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def snippet_frame_and_render_settings():
    import bpy

    scene = bpy.context.scene
    scene.frame_start = 1001
    scene.frame_end = 1100
    scene.render.fps = 24
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = "//renders/shot_"  # // = relative to .blend


def snippet_custom_properties():
    """Pipeline-friendly: store metadata on IDs (objects, scenes, ...)."""
    import bpy

    obj = bpy.context.active_object
    if obj is None:
        return
    obj["ayon_folder_path"] = "/assets/hero"
    obj["kitsu_task_id"] = "abc-123"
    # Read back: obj.get("ayon_folder_path")


# ---------------------------------------------------------------------------
# CHEAT — print a tiny inventory of the open file
# ---------------------------------------------------------------------------

def inventory():
    import bpy

    print("filepath:", bpy.data.filepath or "<unsaved>")
    print("scenes:", [s.name for s in bpy.data.scenes])
    print("objects:", [o.name for o in bpy.data.objects])
    print("active:", getattr(bpy.context.active_object, "name", None))


if __name__ == "__main__":
    # Only meaningful when executed inside Blender
    try:
        inventory()
    except ImportError:
        print("Open this file inside Blender — bpy is not in system Python.")
