import pathlib

# In path_resolver.py, resolve mesh references in this order:

# 1. absolute file path
# 2. path relative to the URDF file
# 3. path relative to the selected mesh folder
# 4. package:// mapping
# 5. recursive filename search as a fallback