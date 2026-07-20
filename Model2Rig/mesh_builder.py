# mesh_builder.py
 
from pathlib import Path

import bpy
from mathutils import Matrix

from .robot_model import RobotLink, RobotVisual
from .transforms import make_transform


def numpy_to_matrix(matrix) -> Matrix:
    return Matrix(matrix.tolist())


def import_stl(
    context: bpy.types.Context,
    mesh_path: Path,
) -> bpy.types.Object:
    if not mesh_path.exists():
        raise FileNotFoundError(f"Mesh not found: {mesh_path}")

    bpy.ops.object.select_all(action="DESELECT")

    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(
            filepath=str(mesh_path),
            forward_axis="X",
            up_axis="Z",
            global_scale=1.0,
        )
    else:
        bpy.ops.import_mesh.stl(
            filepath=str(mesh_path),
            axis_forward="X",
            axis_up="Z",
            global_scale=1.0,
        )

    selected_objects = context.selected_objects

    if selected_objects is None:
        raise RuntimeError("Blender has no selected-object context.")

    imported_objects = list(selected_objects)

    if len(imported_objects) != 1:
        raise RuntimeError(
            f"Expected one imported object from '{mesh_path}', "
            f"found {len(imported_objects)}."
        )

    return imported_objects[0]


def move_to_collection(
    obj: bpy.types.Object,
    collection: bpy.types.Collection,
) -> None:
    for old_collection in list(obj.users_collection):
        old_collection.objects.unlink(obj)

    collection.objects.link(obj)


def build_visual_mesh(
    context: bpy.types.Context,
    link: RobotLink,
    visual: RobotVisual,
    robot_collection: bpy.types.Collection,
    armature_object: bpy.types.Object,
    bone_name: str,
) -> bpy.types.Object:
    if link.rest_transform_urdf is None:
        raise ValueError(f"Link '{link.name}' has no rest transform.")

    mesh_object = import_stl(
        context=context,
        mesh_path=visual.mesh_path,
    )

    mesh_object.name = f"{link.name}_visual"
    move_to_collection(mesh_object, robot_collection)

    link_world = numpy_to_matrix(link.rest_transform_urdf)

    visual_local = numpy_to_matrix(
        make_transform(
            visual.origin_xyz,
            visual.origin_rpy,
        )
    )

    scale_matrix = Matrix.Diagonal(
        (
            visual.scale[0],
            visual.scale[1],
            visual.scale[2],
            1.0,
        )
    )

    mesh_object.matrix_world = link_world @ visual_local @ scale_matrix

    world_transform = mesh_object.matrix_world.copy()

    mesh_object.parent = armature_object
    mesh_object.parent_type = "BONE"
    mesh_object.parent_bone = bone_name

    mesh_object.matrix_world = world_transform

    return mesh_object
