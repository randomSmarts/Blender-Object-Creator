from dataclasses import dataclass
from pathlib import Path

import numpy as np


Vector3 = tuple[float, float, float]


@dataclass
class RobotVisual:
    mesh_path: Path
    origin_xyz: Vector3
    origin_rpy: Vector3
    scale: Vector3 = (1.0, 1.0, 1.0)


@dataclass
class RobotLink:
    name: str
    visuals: RobotVisual | None = None
    rest_transform_urdf: np.ndarray | None = None
    rest_transform_blender: np.ndarray | None = None


@dataclass
class RobotJoint:
    name: str
    joint_type: str
    parent_link: str
    child_link: str
    origin_xyz: Vector3
    origin_rpy: Vector3
    axis: Vector3

    lower_limit: float | None = None
    upper_limit: float | None = None
    effort: float | None = None
    velocity: float | None = None

    rest_transform_urdf: np.ndarray | None = None
    rest_transform_blender: np.ndarray | None = None

    axis_world_urdf: np.ndarray | None = None
    axis_world_blender: np.ndarray | None = None


@dataclass
class RobotModel:
    links: dict[str, RobotLink]
    joints: dict[str, RobotJoint]
    root_link: str
    name: str = "Unitree G1"