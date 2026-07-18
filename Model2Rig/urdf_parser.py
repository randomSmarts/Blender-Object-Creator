import xml.etree.ElementTree as ET
import bpy


def parse_urdf(urdf_path, mesh_root):
    pass


# robot = parse_urdf(
#     urdf_path=properties.urdf_path,
#     mesh_root=properties.mesh_root,
# )

# * load the XML using xml.etree.ElementTree
# * read the robot name
# * read every <link>
# * read every <visual>
# * read every <joint>
# * extract origins
# * extract mesh paths
# * extract joint axes
# * extract joint limits
# * identify the root link

# Support these joint types first:

# * fixed
# * revolute
# * continuous
# * prismatic
# * floating
