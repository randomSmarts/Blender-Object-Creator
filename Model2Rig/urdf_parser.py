import xml.etree.ElementTree as ET
import bpy

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