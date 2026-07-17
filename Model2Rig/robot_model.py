from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RobotVisual:
    mesh_path: Path | None
    origin_xyz: tuple[float, float, float]
    origin_rpy: tuple[float, float, float]
    scale: tuple[float, float, float]
    geometry_type: str = "mesh"


@dataclass
class RobotLink:
    name: str
    visuals: list[RobotVisual] = field(default_factory=list)


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


@dataclass
class RobotModel:
    name: str
    links: dict[str, RobotLink]
    joints: dict[str, RobotJoint]
    root_link: str | None = None