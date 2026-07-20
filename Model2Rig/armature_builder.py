import bpy
from mathutils import Matrix, Vector

from Model2Rig.mesh_builder import build_visual_mesh
from Model2Rig.robot_model import RobotModel


BONE_DISPLAY_LENGTH = 0.08


def numpy_to_matrix(matrix) -> Matrix:
    return Matrix(matrix.tolist())


def create_robot_collection(
    context: bpy.types.Context,
    name: str,
) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    context.scene.collection.children.link(collection)

    return collection


def build_model_in_blender(
    context: bpy.types.Context,
    robot: RobotModel,
    global_scale: float,
    collapse_fixed_joints: bool,
    create_joint_limits: bool,
) -> bpy.types.Object:
    # Reserved for later.
    del collapse_fixed_joints
    del create_joint_limits

    if robot.root_link not in robot.links:
        raise ValueError(
            f"Root link '{robot.root_link}' is missing."
        )

    robot_collection = create_robot_collection(
        context,
        f"{robot.name}_Collection",
    )

    # Parent object for scaling the entire imported robot.
    robot_root_object = bpy.data.objects.new(
        f"{robot.name}_Root",
        None,
    )

    robot_root_object.scale = (
        global_scale,
        global_scale,
        global_scale,
    )

    robot_collection.objects.link(robot_root_object)

    armature_data = bpy.data.armatures.new(
        f"{robot.name}_Armature"
    )

    armature_object = bpy.data.objects.new(
        f"{robot.name}_Armature",
        armature_data,
    )

    robot_collection.objects.link(armature_object)
    armature_object.parent = robot_root_object

    bpy.ops.object.select_all(action="DESELECT")
    armature_object.select_set(True)
    context.view_layer.objects.active = armature_object

    bpy.ops.object.mode_set(mode="EDIT")

    bones: dict[str, bpy.types.EditBone] = {}

    # The root link itself becomes the root bone.
    root_bone = armature_data.edit_bones.new(robot.root_link)
    root_bone.head = Vector((0.0, 0.0, 0.0))
    root_bone.tail = Vector((0.0, 0.0, BONE_DISPLAY_LENGTH))

    bones[robot.root_link] = root_bone

    # Create one bone per URDF joint.
    for joint in robot.joints.values():
        if joint.rest_transform_blender is None:
            raise ValueError(
                f"Joint '{joint.name}' has no rest transform."
            )

        if joint.axis_world_blender is None:
            raise ValueError(
                f"Joint '{joint.name}' has no Blender axis."
            )

        transform = numpy_to_matrix(
            joint.rest_transform_blender
        )

        joint_position = transform.translation
        joint_axis = Vector(joint.axis_world_blender)

        if joint_axis.length == 0.0:
            raise ValueError(
                f"Joint '{joint.name}' has a zero-length axis."
            )

        joint_axis.normalize()

        bone = armature_data.edit_bones.new(joint.name)

        bone.head = joint_position
        bone.tail = (
            joint_position
            + joint_axis * BONE_DISPLAY_LENGTH
        )

        bones[joint.name] = bone

    # Maps each child link to the joint controlling it.
    child_link_to_joint = {
        joint.child_link: joint
        for joint in robot.joints.values()
    }

    # Create the bone hierarchy.
    for joint in robot.joints.values():
        child_bone = bones[joint.name]

        if joint.parent_link == robot.root_link:
            parent_bone = root_bone
        else:
            parent_joint = child_link_to_joint.get(
                joint.parent_link
            )

            if parent_joint is None:
                raise ValueError(
                    f"Could not find the joint controlling "
                    f"parent link '{joint.parent_link}'."
                )

            parent_bone = bones[parent_joint.name]

        child_bone.parent = parent_bone
        child_bone.use_connect = False

    bpy.ops.object.mode_set(mode="OBJECT")

    # Import every link's visual mesh.
    for link in robot.links.values():
        if link.visuals is None:
            continue

        if link.name == robot.root_link:
            controlling_bone_name = robot.root_link
        else:
            controlling_joint = child_link_to_joint.get(
                link.name
            )

            if controlling_joint is None:
                raise ValueError(
                    f"No joint controls link '{link.name}'."
                )

            controlling_bone_name = controlling_joint.name

        build_visual_mesh(
            context=context,
            link=link,
            visual=link.visuals,
            robot_collection=robot_collection,
            armature_object=armature_object,
            bone_name=controlling_bone_name,
        )

    bpy.ops.object.select_all(action="DESELECT")
    armature_object.select_set(True)
    context.view_layer.objects.active = armature_object

    return armature_object

# Don't worry about collapse_fixed_joints and create_joint_limits, that is just placeholders for something else for now;
# Context and robot is the real useful stuff because context is the user's current scene and so can create the armature and put it in the current scene

# How it is called in operators.py: 
# armature = build_model_in_blender(
#     context=context,
#     robot=robot,
#     global_scale=properties.global_scale,
#     collapse_fixed_joints=properties.collapse_fixed_joints,
#     create_joint_limits=properties.create_joint_limits,
# )

# In armature_builder.py:
# 1. create armature data
# 2. create an armature object
# 3. link it to the robot collection
# 4. make it active
# 5. enter Edit Mode

