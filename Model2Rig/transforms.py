import bpy
import numpy as np

from Model2Rig.robot_model import RobotModel

def compute_rest_transforms(robot: RobotModel):
    pass

# compute_rest_transforms(robot)

# * parsing xyz
# * parsing rpy
# * converting RPY to a matrix
# * converting URDF coordinates to Blender coordinates
# * composing parent and child transformations
# * transforming joint axes

# 12. Compute every link’s rest transform
# Traverse the hierarchy starting from the root link.