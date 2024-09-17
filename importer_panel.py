import bpy

from bpy.types import Panel

class QueryProps(bpy.types.PropertyGroup):
    model_name: bpy.props.StringProperty(default="")
    model_type: bpy.props.StringProperty(default="tp")
    import_args: bpy.props.StringProperty(default="")

class OHI_PT_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Valorant agents importer operations"
    bl_category = "VAI"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.QueryProps

        row = layout.row()
        col = layout.column()

        rowsub = col.row(align=True)
        rowsub.prop(props, "model_name", text="Model Name")
        rowsub = col.row(align=True)
        rowsub.prop(props, "model_type", text="Model Type")
        rowsub = col.row(align=True)
        rowsub.prop(props, "import_args", text="Import Args")

        tips1 = "在使用前启用Rigify插件!"
        tips2 = "导入模型前删除所有物体!"
        tips3 = "下一步之前先Rigify生成!"
        tips4 = "修复Metarig Bones"

        col.label(text = tips1, icon = "ERROR")
        col.label(text = tips2, icon = "ERROR")

        col.separator()
        col.operator("object.setup_config", text = "Setup Config")
        col.operator("object.setup_source_model", text = "Setup Model")
        col.operator("object.setup_metarig", text = "Setup Metarig")

        col.separator()
        col.label(text = tips4, icon = "ERROR")
        col.operator("object.fix_fp_bone", text = "Fix FP Metarig")
        col.operator("object.fix_tp_bone", text = "Fix TP Metarig")

        col.separator()
        col.label(text = tips3, icon = "ERROR")
        #col.operator("object.copy_rigify_to_src", text = "Copy Rigify To Src")
        col.operator("object.setup_rigify", text = "Setup Rigify")