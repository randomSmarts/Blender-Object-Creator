import bpy


# In mesh_builder.py, for each visual:

# 1. resolve its mesh path
# 2. import the STL
# 3. capture the newly created object
# 4. rename it
# 5. apply its local scale
# 6. apply the link transform
# 7. move it into the robot collection

# The final visual transform is:

# T_{\text{visual}}
# =
# T_{\text{link}}T_{\text{visual-origin}}