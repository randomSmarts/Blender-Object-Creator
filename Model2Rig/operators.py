import bpy


class ROBOT_OT_select_urdf(bpy.types.Operator):
    bl_idname = "robot.select_urdf"
    bl_label = "Select URDF"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")  # type: ignore

    filter_glob: bpy.props.StringProperty(  # type: ignore
        default="*.urdf;*.xml",
        options={"HIDDEN"},
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        context.scene.robot_importer.urdf_path = self.filepath
        return {"FINISHED"}


class ROBOT_OT_select_meshes(bpy.types.Operator):
    bl_idname = "robot.select_meshes"
    bl_label = "Select mesh folder"

    filepath: bpy.props.StringProperty(subtype="DIR_PATH")  # type: ignore

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        context.scene.Model2Rig.mesh_root = self.filepath
        return {"FINISHED"}


class ROBOT_OT_import_urdf(bpy.types.Operator):
    bl_idname = "robot.import_urdf"
    bl_label = "Import Robot"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        properties = context.scene.Model2Rig

        try:
            robot = parse_urdf(
                urdf_path=properties.urdf_path,
                mesh_root=properties.mesh_root,
            )

            validate_robot(robot)
            compute_rest_transforms(robot)

            armature = build_robot_in_blender(
                context=context,
                robot=robot,
                global_scale=properties.global_scale,
                collapse_fixed_joints=properties.collapse_fixed_joints,
                create_joint_limits=properties.create_joint_limits,
            )

        except Exception as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        self.report({"INFO"}, f"Imported robot: {robot.name}")
        return {"FINISHED"}
