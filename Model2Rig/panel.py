# DONE

import bpy


class ROBOT_PT_import_panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Robot"

    bl_label = "Robot Rig Importer"
    bl_idname = "ROBOT_PT_import_panel"

    bl_options = {"DEFAULT_CLOSED"}

    version = "1.0.0"
    icons = None

    def draw(self, context):  # context = info about what user is curr. doing
        if not self.layout:
            return

        layout = self.layout
        properties = context.scene.Model2Rig

        row = layout.row(align=True)  # all row items sit side by side
        row.prop(
            properties, "urdf_path"
        )  # When user inputs path, it gets saved to properties.urdf_path
        row.operator(
            "robot.select_urdf",
            text="",
            icon="FILE_FOLDER",  # robot.select_urdf refers to a idname in operators.py for a function: category.name_of_operator
        )  # Runs an operator function which lets the user select a urdf file --> updates properties.urdf_path

        row = layout.row(align=True)
        row.prop(
            properties, "mesh_root"
        )  # This and the following are defined in my properties.py
        row.operator("robot.select_meshes", text="", icon="FILE_FOLDER")

        layout.prop(properties, "global_scale")
        layout.prop(properties, "collapse_fixed_joints")
        layout.prop(properties, "create_joint_limits")

        layout.separator()

        import_button = layout.operator(
            "robot.import_urdf",
            text="Import URDF Robot",
            icon="ARMATURE_DATA",
        )

        import_button.enabled = bool(
            properties.urdf_path
        )  # separate from selecting the proper urdf file
