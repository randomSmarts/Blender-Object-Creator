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

import numpy as np

from .robot_model import RobotJoint, RobotModel, Vector3


URDF_TO_BLENDER = np.array(
    [
        [0.0, -1.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0],
    ]
)


def rpy_to_rotation_matrix(rpy: Vector3) -> np.ndarray:
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

    return rotation_z @ rotation_y @ rotation_x


def make_transform(xyz: Vector3, rpy: Vector3) -> np.ndarray:
    transform = np.eye(4)

    transform[:3, :3] = rpy_to_rotation_matrix(rpy)
    transform[:3, 3] = np.asarray(xyz, dtype=float)

    return transform


def urdf_transform_to_blender(transform: np.ndarray) -> np.ndarray:
    conversion = np.eye(4)
    conversion[:3, :3] = URDF_TO_BLENDER

    return conversion @ transform @ conversion.T


def build_joint_children(
    robot: RobotModel,
) -> dict[str, list[RobotJoint]]:
    children: dict[str, list[RobotJoint]] = {}

    for joint in robot.joints.values():
        children.setdefault(joint.parent_link, []).append(joint)

    return children


def compute_rest_transforms(robot: RobotModel) -> None:
    if robot.root_link not in robot.links:
        raise ValueError(f"Root link '{robot.root_link}' is missing from the model.")

    children = build_joint_children(robot)

    root = robot.links[robot.root_link]
    root.rest_transform_urdf = np.eye(4)
    root.rest_transform_blender = np.eye(4)

    visited: set[str] = set()

    def visit(parent_link_name: str) -> None:
        if parent_link_name in visited:
            raise ValueError(f"Cycle detected at link '{parent_link_name}'.")

        visited.add(parent_link_name)

        parent_link = robot.links[parent_link_name]
        parent_world = parent_link.rest_transform_urdf

        if parent_world is None:
            raise ValueError(f"Link '{parent_link_name}' has no rest transform.")

        for joint in children.get(parent_link_name, []):
            if joint.child_link not in robot.links:
                raise ValueError(
                    f"Joint '{joint.name}' references missing link "
                    f"'{joint.child_link}'."
                )

            joint_local = make_transform(
                joint.origin_xyz,
                joint.origin_rpy,
            )

            joint_world = parent_world @ joint_local

            joint.rest_transform_urdf = joint_world
            joint.rest_transform_blender = urdf_transform_to_blender(joint_world)

            axis_local = np.asarray(joint.axis, dtype=float)
            axis_length = np.linalg.norm(axis_local)

            if axis_length == 0.0:
                raise ValueError(f"Joint '{joint.name}' has a zero-length axis.")

            axis_local /= axis_length

            joint.axis_world_urdf = joint_world[:3, :3] @ axis_local

            joint.axis_world_blender = URDF_TO_BLENDER @ joint.axis_world_urdf

            child_link = robot.links[joint.child_link]

            # At q = 0, the joint and child-link frames coincide.
            child_link.rest_transform_urdf = joint_world
            child_link.rest_transform_blender = joint.rest_transform_blender

            visit(joint.child_link)

        visited.remove(parent_link_name)

    visit(robot.root_link)
