import bpy

from Model2Rig.robot_model import RobotModel

def validate_model(robot: RobotModel):
    pass

# validate_model(robot)

# In validation.py, check that:

# * the robot has at least one link
# * every parent link exists
# * every child link exists
# * no child has multiple parent joints
# * the hierarchy has no cycles
# * exactly one root link exists
# * every revolute or prismatic joint has a nonzero axis
# * every referenced mesh exists
# * lower limit does not exceed upper limit

# Do this before creating Blender objects.