# Done

from Model2Rig import panel, operators, properties

import bpy  # Blender Python API

from importlib import (
    reload,
)  # Blender won't see plugin changes unless I restart Blender or reload the scripts, this function allows the plugin to force-refresh its sub-modules

for module in (operators, panel, properties):
    reload(module)  # forces Python to reload the respective files

classes = (
    properties.RobotImporterProperties,
    panel.ROBOT_PT_import_panel,
    operators.ROBOT_OT_import_urdf,
    operators.ROBOT_OT_select_urdf,
    # TODO: add rest of classes needed
)


def register():
    unregister()

    for item in classes:
        bpy.utils.register_class(item)

    bpy.types.Scene.Model2Rig = bpy.props.PointerProperty(  # type: ignore bpy.types.Scene is dynamically modified at runtime
        type=properties.RobotImporterProperties
    )


def unregister():
    # Clean up the scene property first
    if hasattr(bpy.types.Scene, "Model2Rig"):
        del bpy.types.Scene.Model2Rig

    # Unregister classes in reverse order
    for item in reversed(classes):
        try:
            bpy.utils.unregister_class(item)
        except Exception:
            continue
