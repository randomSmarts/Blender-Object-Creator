from pathlib import Path

import bpy
from mathutils import Matrix

from .robot_model import RobotLink, RobotVisual
from .transforms import (
    make_transform,
    urdf_transform_to_blender,
)


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
        bpy.ops.wm.stl_import(filepath=str(mesh_path))
    else:
        bpy.ops.import_mesh.stl(filepath=str(mesh_path))

    selected_objects = context.selected_objects

    if selected_objects is None:
        raise RuntimeError("Blender context has no selected objects.")

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
    for current_collection in list(obj.users_collection):
        current_collection.objects.unlink(obj)

    collection.objects.link(obj)


def build_visual_mesh(
    context: bpy.types.Context,
    link: RobotLink,
    visual: RobotVisual,
    robot_collection: bpy.types.Collection,
    armature_object: bpy.types.Object,
    bone_name: str,
) -> bpy.types.Object:
    if link.rest_transform_blender is None:
        raise ValueError(f"Link '{link.name}' has no Blender rest transform.")

    mesh_object = import_stl(
        context=context,
        mesh_path=visual.mesh_path,
    )

    mesh_object.name = f"{link.name}_visual"

    move_to_collection(mesh_object, robot_collection)

    visual_local_urdf = make_transform(
        visual.origin_xyz,
        visual.origin_rpy,
    )

    visual_local_blender = urdf_transform_to_blender(visual_local_urdf)

    link_world = numpy_to_matrix(link.rest_transform_blender)

    visual_local = numpy_to_matrix(visual_local_blender)

    scale_matrix = Matrix.Diagonal(
        (
            visual.scale[0],
            visual.scale[1],
            visual.scale[2],
            1.0,
        )
    )

    # World -> visual = World -> link @ Link -> visual
    visual_world = link_world @ visual_local @ scale_matrix

    mesh_object.matrix_world = visual_world

    # Rigidly attach the link mesh to its controlling bone.
    preserved_world_transform = mesh_object.matrix_world.copy()

    mesh_object.parent = armature_object
    mesh_object.parent_type = "BONE"
    mesh_object.parent_bone = bone_name

    mesh_object.matrix_world = preserved_world_transform

    return mesh_object


# In mesh_builder.py, for each visual:

# 1. resolve its mesh path
# 2. import the STL
# 3. capture the newly created object
# 4. rename it
# 5. apply its local scale
# 6. apply the link transform
# 7. move it into the robot collection

# The final visual transform is:

# T_{\text{visual}}
# =
# T_{\text{link}}T_{\text{visual-origin}}
