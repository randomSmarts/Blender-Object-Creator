import xml.etree.ElementTree as ET
from pathlib import Path

from Model2Rig.robot_model import RobotModel, RobotLink, RobotJoint, RobotVisual


Vector3 = tuple[float, float, float]


def require_child(element: ET.Element, tag: str) -> ET.Element:
    child = element.find(tag)

    if child is None:
        raise ValueError(
            f"Missing required <{tag}> inside "
            f"<{element.tag} name='{element.get('name', 'unknown')}'>"
        )

    return child


def require_attr(element: ET.Element, name: str) -> str:
    value = element.get(name)

    if value is None:
        raise ValueError(f"Missing required attribute '{name}' on <{element.tag}>")

    return value


def parse_vector(value: str) -> Vector3:
    values = [float(component) for component in value.split()]

    if len(values) != 3:
        raise ValueError(f"Expected three values, received: {value}")

    return values[0], values[1], values[2]


def parse_urdf(urdf_path: str, mesh_root: str) -> RobotModel:
    if not urdf_path or not mesh_root:
        raise ValueError("Both urdf_path and mesh_root must be provided.")

    resolved_urdf_path = Path(urdf_path).resolve()
    resolved_mesh_root = Path(mesh_root).resolve()

    try:
        tree = ET.parse(resolved_urdf_path)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"URDF file not found: {resolved_urdf_path}") from error
    except ET.ParseError as error:
        raise ValueError(f"Invalid XML/URDF file: {resolved_urdf_path}") from error

    root = tree.getroot()

    if root.tag != "robot":
        raise ValueError(f"Expected root tag <robot>, found <{root.tag}>")

    robot = RobotModel(
        links={},
        joints={},
        root_link="",
        name=require_attr(root, "name"),
    )

    for link in root.findall("link"):
        name = require_attr(link, "name")

        visual = link.find("visual")

        if visual is None:
            continue

        origin = visual.find("origin")

        if origin is None:
            xyz = (0.0, 0.0, 0.0)
            rpy = (0.0, 0.0, 0.0)
        else:
            xyz = parse_vector(origin.get("xyz", "0 0 0"))
            rpy = parse_vector(origin.get("rpy", "0 0 0"))

        geometry = require_child(visual, "geometry")
        mesh = require_child(geometry, "mesh")

        mesh_filename = Path(require_attr(mesh, "filename"))

        resolved_mesh_path = (resolved_mesh_root / mesh_filename.name).resolve()

        scale = parse_vector(mesh.get("scale", "1 1 1"))

        robot_visual = RobotVisual(
            mesh_path=resolved_mesh_path,
            origin_xyz=xyz,
            origin_rpy=rpy,
            scale=scale,
        )

        robot.links[name] = RobotLink(
            name=name,
            visuals=robot_visual,
        )

    for joint in root.findall("joint"):
        name = require_attr(joint, "name")
        joint_type = require_attr(joint, "type")

        origin = joint.find("origin")

        if origin is None:
            xyz = (0.0, 0.0, 0.0)
            rpy = (0.0, 0.0, 0.0)
        else:
            xyz = parse_vector(origin.get("xyz", "0 0 0"))
            rpy = parse_vector(origin.get("rpy", "0 0 0"))

        parent = require_child(joint, "parent")
        child = require_child(joint, "child")

        parent_link = require_attr(parent, "link")
        child_link = require_attr(child, "link")

        axis_element = joint.find("axis")
        axis = (
            parse_vector(axis_element.get("xyz", "1 0 0"))
            if axis_element is not None
            else (1.0, 0.0, 0.0)
        )

        limit = joint.find("limit")

        lower = None
        upper = None
        effort = None
        velocity = None

        if limit is not None:
            lower_value = limit.get("lower")
            upper_value = limit.get("upper")
            effort_value = limit.get("effort")
            velocity_value = limit.get("velocity")

            lower = float(lower_value) if lower_value is not None else None
            upper = float(upper_value) if upper_value is not None else None
            effort = float(effort_value) if effort_value is not None else None
            velocity = float(velocity_value) if velocity_value is not None else None

        robot.joints[name] = RobotJoint(
            name=name,
            joint_type=joint_type,
            parent_link=parent_link,
            child_link=child_link,
            origin_xyz=xyz,
            origin_rpy=rpy,
            axis=axis,
            lower_limit=lower,
            upper_limit=upper,
            effort=effort,
            velocity=velocity,
        )

    child_links = {joint.child_link for joint in robot.joints.values()}

    root_candidates = set(robot.links) - child_links

    if len(root_candidates) != 1:
        raise ValueError(
            f"Expected exactly one root link, found: {sorted(root_candidates)}"
        )

    robot.root_link = root_candidates.pop()

    return robot
