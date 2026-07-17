import bpy

# Properties which will be attached to every scene
class RobotImporterProperties(bpy.types.PropertyGroup):
    urdf_path: bpy.props.StringProperty( # type: ignore
        name="URDF File",
        subtype="FILE_PATH",
    )

    mesh_root: bpy.props.StringProperty( # type: ignore
        name="Mesh Folder",
        subtype="DIR_PATH",
    )

    global_scale: bpy.props.FloatProperty( # type: ignore
        name="Global Scale",
        default=1.0,
        min=0.0001,
    )

    collapse_fixed_joints: bpy.props.BoolProperty( # type: ignore
        name="Collapse Fixed Joints",
        default=True,
    )

    create_joint_limits: bpy.props.BoolProperty( # type: ignore
        name="Create Joint Limits",
        default=True,
    )