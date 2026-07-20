from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RobotVisual:
    mesh_path: Path
    origin_xyz: tuple[float, float, float]
    origin_rpy: tuple[float, float, float]
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)


@dataclass
class RobotLink:
    name: str
    visuals: RobotVisual | None


@dataclass
class RobotJoint:
    name: str
    joint_type: str
    parent_link: str
    child_link: str
    origin_xyz: tuple[float, float, float]
    origin_rpy: tuple[float, float, float]
    axis: tuple[float, float, float]
    lower_limit: float | None = None
    upper_limit: float | None = None
    effort: float | None = None
    velocity: float | None = None


@dataclass
class RobotModel:
    links: dict[str, RobotLink]
    joints: dict[str, RobotJoint]
    root_link: str
    name: str = "Unitree G1"