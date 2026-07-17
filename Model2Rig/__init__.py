from bpy.ops import armature
import bpy  # Blender Python API
from bpy.utils import previews
import addon_utils

import os  # used to calculate exact file path to icons/ folder on hard drive, regardless of OS

from importlib import (
    reload,
)  # Blender won't see plugin changes unless I restart Blender or reload the scripts, this function allows the plugin to force-refresh its sub-modules


from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)  # Imports data types specific to Blenedr; bpy.props are visible to the UI, can be animated, and are auto. saved inside .blend project file

from bpy.utils import (
    previews,
)  # Import's Blender's custom image preview utility system; used to load custom PNG/JPG icons into Blender panels

from bpy.app.handlers import persistent

from Model2Rig import properties
from Model2Rig import robot_model

JOINT_NAMES = [
    "left_hip_pitch_joint",
    "left_hip_roll_joint",
    "left_hip_yaw_joint",
    "left_knee_joint",
    "left_ankle_pitch_joint",
    "left_ankle_roll_joint",
    "right_hip_pitch_joint",
    "right_hip_roll_joint",
    "right_hip_yaw_joint",
    "right_knee_joint",
    "right_ankle_pitch_joint",
    "right_ankle_roll_joint",
    "waist_yaw_joint",
    "waist_roll_joint",
    "waist_pitch_joint",
    "left_shoulder_pitch_joint",
    "left_shoulder_roll_joint",
    "left_shoulder_yaw_joint",
    "left_elbow_joint",
    "left_wrist_roll_joint",
    "left_wrist_pitch_joint",
    "left_wrist_yaw_joint",
    "right_shoulder_pitch_joint",
    "right_shoulder_roll_joint",
    "right_shoulder_yaw_joint",
    "right_elbow_joint",
    "right_wrist_roll_joint",
    "right_wrist_pitch_joint",
    "right_wrist_yaw_joint",
]

_previews = None

# Import and register all classes

def register():
    bpy.types.Scene.model2rig = bpy.props.PointerProperty(
        type=RobotImporterProperties
    )
    pass
    
def unregister():
    del bpy.types.Scene.model2rig
    pass