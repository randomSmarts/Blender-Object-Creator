import numpy as np

from Model2Rig.robot_model import RobotJoint, RobotModel


Vector3 = tuple[float, float, float]
Matrix4 = np.ndarray


# URDF:
#   +X forward, +Y left, +Z up
#
# Blender:
#   +X right, +Y forward, +Z up
#
# Therefore:
#   x_blender = -y_urdf
#   y_blender =  x_urdf
#   z_blender =  z_urdf
URDF_TO_BLENDER = np.array(
    [
        [0.0, -1.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0],
    ]
)


def rpy_to_rotation_matrix(rpy: Vector3) -> np.ndarray:
    """Convert URDF fixed-axis roll, pitch, yaw into a 3x3 rotation matrix."""
    roll, pitch, yaw = rpy

    cr, sr = np.cos(roll), np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)

    rotation_x = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, cr, -sr],
            [0.0, sr, cr],
        ]
    )

    rotation_y = np.array(
        [
            [cp, 0.0, sp],
            [0.0, 1.0, 0.0],
            [-sp, 0.0, cp],
        ]
    )

    rotation_z = np.array(
        [
            [cy, -sy, 0.0],
            [sy, cy, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )

    # The rightmost rotation acts first.
    return rotation_z @ rotation_y @ rotation_x


def make_transform(xyz: Vector3, rpy: Vector3) -> Matrix4:
    """Create a homogeneous 4x4 transform from translation and URDF RPY."""
    transform = np.eye(4)

    transform[:3, :3] = rpy_to_rotation_matrix(rpy)
    transform[:3, 3] = np.asarray(xyz, dtype=float)

    return transform


def build_joint_children(
    robot: RobotModel,
) -> dict[str, list[RobotJoint]]:
    """Map each parent link name to the joints leaving that link."""
    children: dict[str, list[RobotJoint]] = {}

    for joint in robot.joints.values():
        children.setdefault(joint.parent_link, []).append(joint)

    return children


def urdf_transform_to_blender(transform: Matrix4) -> Matrix4:
    """Express a full URDF transform in Blender's coordinate system."""
    conversion = np.eye(4)
    conversion[:3, :3] = URDF_TO_BLENDER

    # C^-1 = C^T because C is an orthonormal rotation matrix.
    return conversion @ transform @ conversion.T


def urdf_direction_to_blender(direction: Vector3) -> np.ndarray:
    """Convert a direction vector, such as a joint axis, into Blender space."""
    return URDF_TO_BLENDER @ np.asarray(direction, dtype=float)


def compute_rest_transforms(robot: RobotModel) -> None:
    """
    Compute zero-position world transforms for all links and joints.

    This mutates the passed RobotModel.
    """
    if robot.root_link is None:
        raise ValueError("Robot root link has not been computed.")

    if robot.root_link not in robot.links:
        raise ValueError(f"Root link '{robot.root_link}' is missing from robot.links.")

    children = build_joint_children(robot)

    root_link = robot.links[robot.root_link]

    root_link.rest_transform_urdf = np.eye(4)
    root_link.rest_transform_blender = np.eye(4)

    visited_links: set[str] = set()

    def visit(parent_link_name: str) -> None:
        if parent_link_name in visited_links:
            raise ValueError(f"Cycle detected at link '{parent_link_name}'.")

        visited_links.add(parent_link_name)

        parent_link = robot.links[parent_link_name]
        parent_world = parent_link.rest_transform_urdf

        for joint in children.get(parent_link_name, []):
            if joint.child_link not in robot.links:
                raise ValueError(
                    f"Joint '{joint.name}' references missing child link "
                    f"'{joint.child_link}'."
                )

            # Transform from the parent-link frame to the joint/child frame.
            joint_local = make_transform(
                joint.origin_xyz,
                joint.origin_rpy,
            )

            # World -> child = world -> parent followed by parent -> child.
            joint_world = parent_world @ joint_local

            joint.rest_transform_urdf = joint_world
            joint.rest_transform_blender = urdf_transform_to_blender(joint_world)

            # Joint axis is defined in the joint's local frame.
            axis_local = np.asarray(joint.axis, dtype=float)

            axis_length = np.linalg.norm(axis_local)
            if axis_length == 0.0:
                raise ValueError(f"Joint '{joint.name}' has a zero-length axis.")

            axis_local = axis_local / axis_length

            joint.axis_world_urdf = joint_world[:3, :3] @ axis_local

            joint.axis_world_blender = URDF_TO_BLENDER @ joint.axis_world_urdf

            child_link = robot.links[joint.child_link]

            # At joint position q = 0, the child-link frame coincides with
            # the joint frame in URDF.
            child_link.rest_transform_urdf = joint_world
            child_link.rest_transform_blender = joint.rest_transform_blender

            visit(joint.child_link)

        visited_links.remove(parent_link_name)

    visit(robot.root_link)
