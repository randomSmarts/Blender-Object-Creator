import bpy

from Model2Rig.urdf_parser import parse_urdf
from Model2Rig.validation import validate_model
from Model2Rig.transforms import compute_rest_transforms
from Model2Rig.armature_builder import build_model_in_blender
from Model2Rig.robot_model import RobotModel


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
            robot: RobotModel = parse_urdf(
                urdf_path=properties.urdf_path,
                mesh_root=properties.mesh_root,
            )

            # TODO: validate_model(robot)
            compute_rest_transforms(
                robot
            )  # Passes it in by reference by default so modifies it in place

            resulting_armature = build_model_in_blender(  # I don't think I need the result of this?
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
