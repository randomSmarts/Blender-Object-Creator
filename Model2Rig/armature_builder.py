# armature_builder.py

import bpy
from mathutils import Matrix, Vector

from .mesh_builder import build_visual_mesh
from .robot_model import RobotModel


BONE_DISPLAY_LENGTH = 0.08


def numpy_to_matrix(matrix) -> Matrix:
    return Matrix(matrix.tolist())


def build_model_in_blender(
    context: bpy.types.Context,
    robot: RobotModel,
    global_scale: float,
    collapse_fixed_joints: bool,
    create_joint_limits: bool,
) -> bpy.types.Object:
    del collapse_fixed_joints
    del create_joint_limits

    collection = bpy.data.collections.new(f"{robot.name}_Collection")
    context.scene.collection.children.link(collection)

    armature_data = bpy.data.armatures.new(f"{robot.name}_Armature")

    armature_object = bpy.data.objects.new(
        f"{robot.name}_Armature",
        armature_data,
    )

    armature_object.show_in_front = True
    armature_data.display_type = "OCTAHEDRAL"

    collection.objects.link(armature_object)

    # Keep at 1 during transform debugging.
    armature_object.scale = (1.0, 1.0, 1.0)

    bpy.ops.object.select_all(action="DESELECT")
    armature_object.select_set(True)
    context.view_layer.objects.active = armature_object

    bpy.ops.object.mode_set(mode="EDIT")

    bones: dict[str, bpy.types.EditBone] = {}

    root_bone = armature_data.edit_bones.new(robot.root_link)
    root_bone.head = Vector((0.0, 0.0, 0.0))
    root_bone.tail = Vector((0.0, 0.0, BONE_DISPLAY_LENGTH))

    bones[robot.root_link] = root_bone

    for joint in robot.joints.values():
        if joint.rest_transform_urdf is None:
            raise ValueError(f"Joint '{joint.name}' has no transform.")

        if joint.axis_world_urdf is None:
            raise ValueError(f"Joint '{joint.name}' has no world axis.")

        transform = numpy_to_matrix(joint.rest_transform_urdf)

        position = transform.translation
        axis = Vector(joint.axis_world_urdf)

        if axis.length == 0.0:
            axis = Vector((0.0, 0.0, 1.0))
        else:
            axis.normalize()

        bone = armature_data.edit_bones.new(joint.name)
        bone.head = position
        bone.tail = position + axis * BONE_DISPLAY_LENGTH

        bones[joint.name] = bone

    child_link_to_joint = {joint.child_link: joint for joint in robot.joints.values()}

    for joint in robot.joints.values():
        bone = bones[joint.name]

        if joint.parent_link == robot.root_link:
            bone.parent = root_bone
        else:
            parent_joint = child_link_to_joint.get(joint.parent_link)

            if parent_joint is None:
                raise ValueError(
                    f"No joint controls parent link '{joint.parent_link}'."
                )

            bone.parent = bones[parent_joint.name]

        bone.use_connect = False

    bpy.ops.object.mode_set(mode="OBJECT")

    for link in robot.links.values():
        visual = link.visuals

        if visual is None:
            continue

        if link.name == robot.root_link:
            bone_name = robot.root_link
        else:
            controlling_joint = child_link_to_joint.get(link.name)

            if controlling_joint is None:
                raise ValueError(f"No joint controls link '{link.name}'.")

            bone_name = controlling_joint.name

        build_visual_mesh(
            context=context,
            link=link,
            visual=visual,
            robot_collection=collection,
            armature_object=armature_object,
            bone_name=bone_name,
        )

    # Apply global scaling after the pose is verified.
    if global_scale != 1.0:
        for obj in collection.objects:
            obj.scale *= global_scale

    return armature_object
