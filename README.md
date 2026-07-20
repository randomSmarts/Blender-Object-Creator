# Blender-Object-Creator

urdf_parser.py
    Reads definitions.
    “What links and joints exist?”

transforms.py
    Solves the rest-pose kinematic chain.
    “Where is every frame?”

armature_builder.py
    Creates Blender bones and their hierarchy.
    “What controls should the animator manipulate?”

mesh_builder.py
    Imports and attaches visible geometry.
    “What should move with each bone?”
